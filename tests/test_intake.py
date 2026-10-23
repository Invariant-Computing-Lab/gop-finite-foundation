import copy,json,shutil,tempfile,unittest
from pathlib import Path
from src.common import ROOT,write,sha,objhash,core_hash
from gop_intake.__main__ import init,ingest,assess,verify,export,replay
class IntakeTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name);self.c=self.p/'core';self.c.mkdir()
  for name in ['schemas/study_record.schema.json','core/CLAIMS.jsonl','core/ASSUMPTIONS.jsonl']:
   q=self.c/name;q.parent.mkdir(exist_ok=True);shutil.copy2(ROOT/name,q)
  entries=[{'path':str(p.relative_to(self.c)),'sha256':sha(p)} for p in sorted(self.c.rglob('*')) if p.is_file()]
  write(self.c/'CORE_MANIFEST.json',{'foundation_id':'GOP_TOE_FOUNDATION_v1_0','core_sha256':core_hash(entries),'entries':entries})
  self.d=self.p/'study';init(self.c,self.d);self.r=json.loads((self.d/'study_record.json').read_text());(self.d/'source.pdf').write_bytes(b'TEST_FIXTURE no real study')
  self.r.update(template_only=False,study_id='TEST_FIXTURE',evidence_id='TEST_FIXTURE_1',lineage_group='TEST_FIXTURE_DATA',source_claim='TEST_FIXTURE null result')
  self.r['source']['sha256']=sha(self.d/'source.pdf');self.r['scope']['units_and_scales']='dimensionless'
 def tearDown(self):self.tmp.cleanup()
 def put(self,r=None):write(self.d/'study_record.json',r or self.r);return self.d/'study_record.json'
 def test_duplicate(self):
  ingest(self.c,self.put());self.assertEqual(ingest(self.c,self.put())['status'],'duplicate');self.assertEqual(verify(self.c)['records_verified'],1)
 def test_changed_source_version(self):
  ingest(self.c,self.put());(self.d/'source.pdf').write_bytes(b'TEST_FIXTURE revised');self.r['source']['sha256']=sha(self.d/'source.pdf')
  self.assertEqual(ingest(self.c,self.put())['version'],2);self.assertEqual(verify(self.c)['records_verified'],2)
 def test_invalid(self):
  self.r['unexpected']=0
  with self.assertRaises(ValueError):ingest(self.c,self.put())
 def test_template(self):
  self.r['template_only']=True
  with self.assertRaises(ValueError):ingest(self.c,self.put())
 def test_unknown_units(self):
  self.r['scope']['units_and_scales']='UNKNOWN';o=ingest(self.c,self.put());self.assertIn('unresolved_units_no_transfer_claim',o['warnings'])
 def test_contradiction(self):
  self.r.update(proposed_relation='challenges',target_claim_ids=['B-ALL'],assumption_mapping=[dict(source_assumption='TEST_FIXTURE',core_assumption_id='A-MONOMIAL',compatibility='matched',reason='test')])
  ingest(self.c,self.put());a=assess(self.c,'TEST_FIXTURE');self.assertEqual(a['records'][0]['relation'],'challenges')
 def test_shared_lineage(self):
  ingest(self.c,self.put());self.r['evidence_id']='TEST_FIXTURE_2';o=ingest(self.c,self.put());self.assertIn('shared_lineage_not_independent_replication',o['warnings'])
 def test_unreviewed(self):
  ingest(self.c,self.put());self.assertEqual(assess(self.c,'TEST_FIXTURE')['review_status'],'unreviewed')
 def test_no_promotion(self):
  self.r['review_status']='accepted_in_scope'
  with self.assertRaises(ValueError):ingest(self.c,self.put())
 def test_missing_source(self):
  (self.d/'source.pdf').unlink()
  with self.assertRaises(ValueError):ingest(self.c,self.put())
 def test_no_core_mutation(self):
  before=(self.c/'core/CLAIMS.jsonl').read_bytes();ingest(self.c,self.put());assess(self.c,'TEST_FIXTURE');verify(self.c);self.assertEqual(before,(self.c/'core/CLAIMS.jsonl').read_bytes())
 def test_request_does_not_execute(self):
  self.r.update(requested_effect='core_revision_request',core_change_requested=True,integration_interpretation='Replace all laws; TEST_FIXTURE not authorized')
  ingest(self.c,self.put());q=json.loads(next((self.c/'changes/requests').glob('*.json')).read_text());self.assertFalse(q['core_was_modified']);verify(self.c)
 def test_hash_failure(self):
  self.r['source']['sha256']='0'*64
  with self.assertRaises(ValueError):ingest(self.c,self.put())
 def test_path_escape(self):
  self.r['source']['path']='../outside.pdf'
  with self.assertRaises(ValueError):ingest(self.c,self.put())
 def test_mutation_detected(self):
  (self.c/'core/CLAIMS.jsonl').write_text('bad')
  with self.assertRaises(ValueError):verify(self.c)
 def test_extra_core_file_detected(self):
  (self.c/'core/unapproved.txt').write_text('TEST_FIXTURE new law')
  with self.assertRaises(ValueError):verify(self.c)
 def test_export_replay(self):
  ingest(self.c,self.put());assess(self.c,'TEST_FIXTURE');out=self.p/'addon.zip';export(self.c,'TEST_FIXTURE',out)
  fresh=self.p/'fresh';shutil.copytree(self.c,fresh);shutil.rmtree(fresh/'evidence')
  replay(fresh,out);self.assertEqual(verify(fresh)['records_verified'],1)
if __name__=='__main__':unittest.main()
