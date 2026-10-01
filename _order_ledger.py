import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\obsolete-member-candidates.md")
t = P.read_text(encoding="utf-8")
parts = re.split(r"(?m)^(?=## )", t)
head, blocks = parts[0], parts[1:]
titles = [b.splitlines()[0].strip() for b in blocks]
WANT = [
    "## 一、怎么产生的",
    "## 〇、⚑ 已处置（2026-10-01 轮 111）",
    "## 〇之二、⚑ 另两条真候选：**查清了，决定「不换」**（2026-10-01 轮 112）",
    "## 二、★ 已核实**为真**（我们确实在调官方已废弃的入口）",
    "## 三、已核实**为假阳性** —— 同名但**不同接口**",
    "## 四、已逐条核完（原「未逐条核」的 20 条 —— 2026-10-01 轮 113）",
    "## 四之三、⚠ 那 7 条真候选：查清后继形状后 —— **全部不换**（2026-10-01 轮 114）",
    "## 四之二、**台账总账（全部处置完毕）**",
    "## 五、⚠⚠ 为什么**不能**做成门禁",
    "## 六、未查证",
]
by = {b.splitlines()[0].strip(): b for b in blocks}
missing = [w for w in WANT if w not in by]
extra = [x for x in titles if x not in WANT]
print("  缺 %s · 多 %s" % (missing, extra))
if missing or extra:
    raise SystemExit(1)
new = head + "".join(by[w] for w in WANT)
assert len(new) == len(t), "长度变了 ⇒ 丢内容"
P.write_text(new, encoding="utf-8")
print("  ok 顺序已修正")
for m in re.finditer(r"(?m)^## .*$", new):
    print("    %s" % m.group(0)[:70])
