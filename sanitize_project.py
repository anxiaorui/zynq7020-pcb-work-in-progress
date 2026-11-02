import pathlib,sqlite3,hashlib,json,collections
root=pathlib.Path('/workspace/scratch/9bf93cee6dc0')
src=root/'pcb_task/working/zynq7020_MAIN_ROUTING_2322.eprj2'
dst=root/'github_upload/safety_review/zynq7020_PAUSED_UPLOAD_CREDENTIAL_CLEARED.eprj2'
assert not dst.exists()
expected='d4e60e5161dee90b5498ea1263977b7f2ff639dc5fa05c885e59723d4b996630'
assert hashlib.sha256(src.read_bytes()).hexdigest()==expected
s=sqlite3.connect(src.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
d=sqlite3.connect(dst); s.backup(d)
d.execute('pragma secure_delete=ON'); d.execute("update users set password=NULL"); d.commit(); d.execute('vacuum');d.close()
d=sqlite3.connect(dst.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
def q(v):return '"'+v.replace('"','""')+'"'
def digest(rows):
 def canon(v):
  if isinstance(v,bytes):return {'bytes_hex':v.hex()}
  return v
 records=[json.dumps([canon(v) for v in row],ensure_ascii=False,separators=(',',':')) for row in rows]
 return hashlib.sha256('\n'.join(sorted(records)).encode()).hexdigest(),len(records)
ss=s.execute('select type,name,tbl_name,sql from sqlite_master order by type,name').fetchall()
ds=d.execute('select type,name,tbl_name,sql from sqlite_master order by type,name').fetchall()
assert ss==ds
report={'status':'DATABASE_SANITIZATION_VERIFIED_NATIVE_OPEN_PENDING','source_sha256':expected,'upload_candidate_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'upload_candidate_size':dst.stat().st_size,'change':'Only users.password set NULL in independent copy; secure_delete then VACUUM. Original unmodified. Password values never selected, printed or logged.','schema_exact':True,'quick_check':d.execute('pragma quick_check').fetchone()[0],'nonempty_password_rows':d.execute('select count(*) from users where password is not null and length(password)>0').fetchone()[0],'tables':{}}
for (table,) in s.execute("select name from sqlite_master where type='table' order by name").fetchall():
 cols=[r[1] for r in s.execute('pragma table_info('+q(table)+')') if not(table=='users' and r[1]=='password')]
 sql='select '+','.join(map(q,cols))+' from '+q(table)
 a=digest(s.execute(sql));b=digest(d.execute(sql));assert a==b,table
 report['tables'][table]={'rows':a[1],'noncredential_records_sha256':a[0],'exact':True,'excluded_columns':['password'] if table=='users' else []}
assert hashlib.sha256(src.read_bytes()).hexdigest()==expected
(root/'github_upload/safety_review/SANITIZATION_DATABASE_CHECK.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='tables'},indent=2))
print('All',len(report['tables']),'tables exact except explicitly excluded password column.')
