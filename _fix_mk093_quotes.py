import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"D:\AI\SW\_mk093.py")
t = p.read_text(encoding="utf-8")
DQ = '"'
#: ★ 事实 48：内层裸双引号统一换成「」
t = t.replace(DQ + "我不知道" + DQ, "「我不知道」")
t = t.replace(DQ + "它有错" + DQ, "「它有错」")
t = t.replace(DQ + "看起来合理" + DQ, "「看起来合理」")
t = t.replace(DQ + "判据不够严" + DQ, "「判据不够严」")
t = t.replace(DQ + "知道" + DQ, "「知道」")
t = t.replace(DQ + "不知道" + DQ, "「不知道」")
t = t.replace("**不是" + DQ + "判据不够严" + DQ + "**", "**不是「判据不够严」**")
p.write_text(t, encoding="utf-8")
try:
    ast.parse(t)
    print("  修完语法 OK")
except SyntaxError as e:
    print("  L%s: %s" % (e.lineno, (e.text or "").strip()[:90]))
