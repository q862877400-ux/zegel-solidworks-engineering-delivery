import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"D:\AI\SW\_mk090.py")
t = p.read_text(encoding="utf-8")
DQ = '"'
#: ★ 事实 48：内层裸双引号统一换成「」——只换这两处中文引号包裹
t = t.replace(DQ + "收尾行还在不在" + DQ, "「收尾行还在不在」")
t = t.replace(DQ + "收尾报的窗口数是不是 0" + DQ, "「收尾报的窗口数是不是 0」")
p.write_text(t, encoding="utf-8")
try:
    ast.parse(t)
    print("  修完语法 OK")
except SyntaxError as e:
    print("  L%s: %s" % (e.lineno, (e.text or "").strip()[:80]))
