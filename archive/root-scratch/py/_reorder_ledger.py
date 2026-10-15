import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\obsolete-member-candidates.md")
text = P.read_text(encoding="utf-8")

# 按二级标题切块（保留标题行）
parts = re.split(r"(?m)^(?=## )", text)
head = parts[0]
blocks = {}
order_in = []
for b in parts[1:]:
    title = b.splitlines()[0].strip()
    blocks[title] = b
    order_in.append(title)

#: 期望顺序（按编号）
WANT = [
    "## 一、怎么产生的",
    "## 〇、⚑ 已处置（2026-10-01 轮 111）",
    "## 〇之二、⚑ 另两条真候选：**查清了，决定「不换」**（2026-10-01 轮 112）",
    "## 二、★ 已核实**为真**（我们确实在调官方已废弃的入口）",
    "## 三、已核实**为假阳性** —— 同名但**不同接口**",
    "## 四、已逐条核完（原「未逐条核」的 20 条 —— 2026-10-01 轮 113）",
    "## 四之二、台账总账（全部处置完毕）",
    "## 四之三、⚠ 那 7 条真候选：查清后继形状后 —— **全部不换**（2026-10-01 轮 114）",
    "## 四之四、**台账总账（全部处置完毕）**",
    "## 五、⚠⚠ 为什么**不能**做成门禁",
    "## 六、未查证",
]
missing = [w for w in WANT if w not in blocks]
extra = [t for t in order_in if t not in WANT]
print("  块数 %d · 缺 %s · 多 %s" % (len(blocks), missing, extra))
if missing or extra:
    print("  **不重排**（有未识别的块，避免丢内容）")
    raise SystemExit(1)

new = head + "".join(blocks[w] for w in WANT)
assert len(new) == len(text), "长度变了 ⇒ 有内容丢失 (%d vs %d)" % (len(new), len(text))
assert sorted(new) == sorted(text), "字符集合变了 ⇒ 有内容丢失"
P.write_text(new, encoding="utf-8")
print("  ok 已按编号重排；长度不变（%d 字节），字符集合一致" % len(new))
