import json, io
d = json.load(open(r"D:\AI\SW\tools\union-sources.json", encoding="utf-8"))
out = io.StringIO()
for s in d["sources"]:
    out.write("="*70 + "\n")
    out.write("repo=%s\nlicense=%s\ntool_count=%s\noperation_count=%s\ndeclared_verified=%s\n"
              % (s.get("repo"), s.get("license"), s.get("tool_count"),
                 s.get("operation_count"), s.get("declared_verified")))
    out.write("note=%s\n" % s.get("note"))
    out.write("domains type=%s\n" % type(s.get("domains")))
    dm = s.get("domains")
    if isinstance(dm, dict):
        for k, v in dm.items():
            out.write("  domain %r -> %s\n" % (k, v if not isinstance(v, list) else ("list[%d] %s" % (len(v), v))))
    else:
        out.write("  domains=%s\n" % (dm,))
    out.write("operations len=%s\n" % (len(s.get("operations") or [])))
    out.write("tools len=%s\n" % (len(s.get("tools") or [])))
open(r"D:\AI\SW\_probe_sources.txt","w",encoding="utf-8").write(out.getvalue())
print("ok")
