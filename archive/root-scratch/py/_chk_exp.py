import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
srv = (R / "mcp-server" / "server.py").read_text(encoding="utf-8", errors="ignore")
disp = set(re.findall(r'"(\w+)":\s*[A-Za-z_]\w*\.(\w+)\s*,', srv))
disp_fns = {f for _, f in disp}
print("server.py 分发表：%d 条，落到 %d 个不同函数名" % (len(disp), len(disp_fns)))
for n in ("collect_model_summary", "collect_mate_feature_summary", "iter_feature_tree",
          "iter_features_recursive", "iter_features"):
    print("  %-32s 已暴露=%s" % (n, "是" if n in disp_fns else "**否**"))
