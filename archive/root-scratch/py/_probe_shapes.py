import json, io, sys
d = json.load(open(r"D:\AI\SW\tools\union-sources.json", encoding="utf-8"))
out = io.StringIO()
out.write("### schema_version=%s union_size=%s\n" % (d.get("schema_version"), d.get("union_size")))
out.write("### sources len=%d\n" % len(d["sources"]))
for s in d["sources"]:
    out.write("\n--- SOURCE keys=%s\n" % sorted(s.keys()))
out.write("\n### union_operations len=%d\n" % len(d["union_operations"]))
open(r"D:\AI\SW\_probe_shapes.txt","w",encoding="utf-8").write(out.getvalue())
print("ok")
