"""Append-only local intake. Import is not scientific endorsement. No core-write operation."""
import argparse,copy,hashlib,json,os,re,shutil,tempfile,zipfile
from pathlib import Path
from src.common import canonical,objhash,sha,write,core_hash,core_entries

def validate(value,schema,path='$'):
    typ=schema.get('type'); types={'object':dict,'array':list,'string':str,'number':(int,float),'integer':int,'boolean':bool,'null':type(None)}
    if typ:
        options=typ if isinstance(typ,list) else [typ]
        if not any(isinstance(value,types[t]) and not (t in ('number','integer') and isinstance(value,bool)) for t in options):raise ValueError(path+': type')
    if 'const' in schema and value!=schema['const']:raise ValueError(path+': const')
    if 'enum' in schema and value not in schema['enum']:raise ValueError(path+': enum')
    if isinstance(value,str):
        if len(value)<schema.get('minLength',0):raise ValueError(path+': empty')
        if 'pattern' in schema and not re.search(schema['pattern'],value):raise ValueError(path+': pattern')
    if isinstance(value,(int,float)) and not isinstance(value,bool):
        if value<schema.get('minimum',float('-inf')):raise ValueError(path+': minimum')
    if isinstance(value,dict):
        if set(schema.get('required',[]))-value.keys():raise ValueError(path+': missing required')
        props=schema.get('properties',{})
        if schema.get('additionalProperties') is False and value.keys()-props.keys():raise ValueError(path+': additional properties')
        for k,v in value.items():
            if k in props:validate(v,props[k],path+'.'+k)
    if isinstance(value,list):
        if len(value)<schema.get('minItems',0):raise ValueError(path+': too few')
        if schema.get('uniqueItems') and len({objhash(v) for v in value})!=len(value):raise ValueError(path+': duplicates')
        for i,v in enumerate(value):validate(v,schema.get('items',{}),f'{path}[{i}]')
    for clause in schema.get('allOf',[]):
        try:validate(value,clause['if'],path)
        except ValueError:continue
        validate(value,clause['then'],path)

def safe(base,relative):
    p=Path(relative)
    if p.is_absolute() or '..' in p.parts:raise ValueError('source path must stay inside supplied study directory')
    out=(Path(base)/p).resolve()
    if not out.is_relative_to(Path(base).resolve()):raise ValueError('source symlink escape')
    return out

def manifest(core):
    p=Path(core)/'CORE_MANIFEST.json';m=json.loads(p.read_text());entries=m['entries']
    if core_hash(entries)!=m['core_sha256']:raise ValueError('manifest hash mismatch')
    if core_entries(core)!=entries:raise ValueError('core file set or content changed')
    if 'freeze_sha256' in m and sha(Path(core)/'configs/FREEZE.json')!=m['freeze_sha256']:raise ValueError('freeze record changed')
    for e in entries:
        if sha(safe(core,e['path']))!=e['sha256']:raise ValueError('core mutation: '+e['path'])
    return m

def registry(core):
    p=Path(core)/'evidence/registry.jsonl'
    return [json.loads(l) for l in p.read_text().splitlines() if l] if p.exists() else []

def init(core,directory):
    m=manifest(core);out=Path(directory);out.mkdir(parents=True,exist_ok=True)
    if (out/'study_record.json').exists():raise ValueError('draft already exists')
    rec={'schema_version':'1.0','template_only':True,'study_id':'ENTER_ID','evidence_id':'ENTER_EVIDENCE_ID','foundation_id':m['foundation_id'],'core_sha256':m['core_sha256'],
         'primary_program':'UNASSIGNED','source':{'path':'source.pdf','sha256':'REPLACE_WITH_REAL_SHA256','locator':'REPLACE','access_level':'report_only'},
         'evidence_type':'context','source_claim':'REPLACE with source-derived claim','integration_interpretation':'UNMAPPED; review required',
         'target_claim_ids':[],'proposed_relation':'unmapped','assumption_mapping':[],
         'scope':{'system_or_population':'UNKNOWN','independent_unit':'UNKNOWN','information_access':'UNKNOWN','units_and_scales':'UNKNOWN','intervention_status':'unknown'},
         'lineage_group':'REPLACE','reproduction_status':'not_attempted','review_status':'unreviewed','requested_effect':'unmapped','core_change_requested':False,'limitations':[]}
    write(out/'study_record.json',rec);return {'status':'draft_unreviewed','path':str(out/'study_record.json')}

def ingest(core,path):
    core=Path(core);m=manifest(core);path=Path(path);r=json.loads(path.read_text())
    validate(r,json.loads((core/'schemas/study_record.schema.json').read_text()))
    if r['foundation_id']!=m['foundation_id'] or r['core_sha256']!=m['core_sha256']:raise ValueError('incompatible foundation')
    for k in ('study_id','evidence_id'):
        if not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',r[k]) or r[k] in ('.','..'):raise ValueError('unsafe ID')
    if r['review_status']!='unreviewed':raise ValueError('imports must begin unreviewed; source review is not foundation endorsement')
    if r['core_change_requested'] and r['requested_effect']!='core_revision_request':raise ValueError('core change only as request, never execution')
    if not r['target_claim_ids'] and r['proposed_relation']!='unmapped' and not r['integration_interpretation'].strip():raise ValueError('unmapped reason required')
    claims={json.loads(l)['id'] for l in (core/'core/CLAIMS.jsonl').read_text().splitlines() if l}
    if set(r['target_claim_ids'])-claims:raise ValueError('unknown claim ID')
    ass={json.loads(l)['id'] for l in (core/'core/ASSUMPTIONS.jsonl').read_text().splitlines() if l}
    if any(x['core_assumption_id'] is not None and x['core_assumption_id'] not in ass for x in r['assumption_mapping']):raise ValueError('unknown assumption ID')
    source=safe(path.parent,r['source']['path'])
    if not source.is_file() or sha(source)!=r['source']['sha256']:raise ValueError('missing source or hash mismatch')
    rr=copy.deepcopy(r);rr['source']['path']='source'+source.suffix
    digest=objhash(rr);reg=registry(core)
    for entry in reg:
        if entry['record_sha256']==digest:return {'status':'duplicate','version':entry['version'],'record_path':entry['record_path']}
    prior=[e for e in reg if e['evidence_id']==r['evidence_id']]
    if prior and any(e['study_id']!=r['study_id'] for e in prior):raise ValueError('evidence identity belongs to another study')
    version=max([e['version'] for e in prior]+[0])+1
    directory=core/'evidence/records'/r['evidence_id']/f'v{version}'
    if directory.exists():raise ValueError('orphan version directory; inspect before retry')
    directory.mkdir(parents=True);shutil.copy2(source,directory/rr['source']['path']);write(directory/'record.json',rr)
    warnings=[]
    if 'UNKNOWN' in r['scope']['units_and_scales'].upper():warnings.append('unresolved_units_no_transfer_claim')
    if any(x['compatibility'] in ('unknown','mismatched') for x in r['assumption_mapping']):warnings.append('assumption_bridge_unresolved')
    if any(e['lineage_group']==r['lineage_group'] for e in reg):warnings.append('shared_lineage_not_independent_replication')
    entry={'study_id':r['study_id'],'evidence_id':r['evidence_id'],'version':version,'record_sha256':digest,
        'record_path':str((directory/'record.json').relative_to(core)),'source_sha256':r['source']['sha256'],'lineage_group':r['lineage_group'],
        'review_status':'unreviewed','proposed_relation':r['proposed_relation'],'warnings':warnings}
    reg.append(entry);p=core/'evidence/registry.jsonl';p.parent.mkdir(exist_ok=True)
    tmp=p.with_suffix('.tmp');tmp.write_text(''.join(json.dumps(e)+'\n' for e in reg));os.replace(tmp,p)
    if r['core_change_requested']:
        request=core/'changes/requests'/f'{r["evidence_id"]}_v{version}.json'
        write(request,{'status':'PROPOSED_NOT_AUTHORIZED','core_sha256':m['core_sha256'],'evidence_id':r['evidence_id'],
            'proposed_change':r['integration_interpretation'],'affected_claims':r['target_claim_ids'],
            'required_before_new_core':['exact equation diff','complexity cost','regression tests','independent validation plan','explicit authorization'],
            'core_was_modified':False})
    manifest(core);return {'status':'imported_unreviewed',**entry}

def assess(core,study):
    m=manifest(core);entries=[e for e in registry(core) if e['study_id']==study]
    if not entries:raise ValueError('unknown study')
    p=Path(core)/'evidence/assessments'/study;p.mkdir(parents=True,exist_ok=True)
    a={'study_id':study,'core_sha256':m['core_sha256'],'review_status':'unreviewed','assessment':'proposed relations preserved; substantive scientific judgment not automated',
       'records':[{'evidence_id':e['evidence_id'],'version':e['version'],'relation':e['proposed_relation'],'warnings':e['warnings']} for e in entries],
       'independent_lineage_count':len({e['lineage_group'] for e in entries}),'evidence_count_is_not_support':True}
    out=p/f'{objhash(a)}.json'
    if not out.exists():write(out,a)
    return a

def verify(core):
    m=manifest(core);reg=registry(core)
    for e in reg:
        p=safe(core,e['record_path']);r=json.loads(p.read_text());validate(r,json.loads((Path(core)/'schemas/study_record.schema.json').read_text()))
        if objhash(r)!=e['record_sha256'] or sha(safe(p.parent,r['source']['path']))!=e['source_sha256']:raise ValueError('evidence corruption')
    return {'core_sha256':m['core_sha256'],'unchanged_core':True,'records_verified':len(reg),'scientific_validation':False}

def export(core,study,out):
    v=verify(core);entries=[e for e in registry(core) if e['study_id']==study]
    if not entries:raise ValueError('unknown study')
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for e in entries:
            p=safe(core,e['record_path']);r=json.loads(p.read_text());s=safe(p.parent,r['source']['path'])
            z.write(p,e['record_path']);z.write(s,str(s.relative_to(core)))
        for p in (Path(core)/'evidence/assessments'/study).glob('*.json'):z.write(p,str(p.relative_to(core)))
        for e in entries:
            p=Path(core)/'changes/requests'/f'{e["evidence_id"]}_v{e["version"]}.json'
            if p.exists():z.write(p,str(p.relative_to(core)))
        z.writestr('compatibility.json',json.dumps(v));z.writestr('records.json',json.dumps(entries))
    return {'path':str(out),'records':len(entries),'unchanged_core':True}

def replay(core,bundle):
    m=manifest(core)
    with tempfile.TemporaryDirectory() as d,zipfile.ZipFile(bundle) as z:
        for name in z.namelist():safe(d,name)
        z.extractall(d)
        c=json.loads((Path(d)/'compatibility.json').read_text())
        if c['core_sha256']!=m['core_sha256']:raise ValueError('addon core mismatch')
        reg=json.loads((Path(d)/'records.json').read_text());out=[]
        for e in reg:out.append(ingest(core,safe(d,e['record_path'])))
        # Assessments are recomputed as unreviewed; requests reconstructed; no automatic acceptance.
        for study in {e['study_id'] for e in reg}:assess(core,study)
        return {'replayed':out,'verification':verify(core)}

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['init','ingest','assess','verify','export','replay']);p.add_argument('--core',required=True)
    p.add_argument('--study-dir');p.add_argument('--record');p.add_argument('--study-id');p.add_argument('--out');p.add_argument('--bundle');a=p.parse_args()
    commands={'init':lambda:init(a.core,a.study_dir),'ingest':lambda:ingest(a.core,a.record),'assess':lambda:assess(a.core,a.study_id),
        'verify':lambda:verify(a.core),'export':lambda:export(a.core,a.study_id,a.out),'replay':lambda:replay(a.core,a.bundle)}
    try:print(json.dumps(commands[a.command](),indent=2))
    except (ValueError,FileNotFoundError,KeyError,TypeError) as e:p.exit(2,str(e)+'\n')
if __name__=='__main__':main()
