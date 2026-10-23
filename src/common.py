import hashlib,json,os,shutil,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def objhash(x):return hashlib.sha256(canonical(x)).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def write(path,x):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    s=json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n'
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(s);os.replace(tmp,path)
def checkpoint(phase,**kw):
    path=ROOT/'STATE.json'
    if path.exists():shutil.copy2(path,ROOT/'STATE.previous.json')
    write(path,dict(phase=phase,time=now(),**kw))
def append(path,x):
    with Path(path).open('a') as f:f.write(json.dumps(x,ensure_ascii=False,allow_nan=False)+'\n')
def core_entries(root):
    root=Path(root)
    prefixes=['core','src','adapters','configs','gop_intake','schemas','tests']
    return [{'path':str(p.relative_to(root)),'sha256':sha(p)} for p in sorted(root.rglob('*')) if p.is_file() and p.relative_to(root).parts[0] in prefixes and '__pycache__' not in p.parts and p.suffix not in ('.pyc',) and p.name!='FREEZE.json']
def core_hash(entries):return objhash(entries)
