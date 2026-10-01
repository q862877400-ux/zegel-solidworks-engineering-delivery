import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── ① 更正 backend_catalog（长文本从独立文件搬，事实 48 定则①）──────────────
CORRECTION = Path(r"D:\AI\SW\_correction188.txt").read_text(encoding="utf-8")
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
bc = d["backend_catalog"]["solidworks-com-pywin32"]
hit = 0
for i, s in enumerate(bc["limitations"]):
    if "ISafeArrayUtility" in s and "轮 188" not in s:
        bc["limitations"][i] = s + " " + CORRECTION
        hit += 1
print("  ok backend_catalog 更正 %d 处" % hit)
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ── ② 事实 128（用文件正文拼，避免多行字面量）────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
body = Path(r"D:\AI\SW\_fact128.txt").read_text(encoding="utf-8")
FACT = "| 128 | " + body.strip().replace("\n", " ") + " |"
if "| 128 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 128")
else:
    print("  已有 128")
