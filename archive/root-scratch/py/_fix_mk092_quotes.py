import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"D:\AI\SW\_mk092.py")
t = p.read_text(encoding="utf-8")
#: ★ 事实 48：内层裸双引号统一换成「」
t = t.replace('不是"取法"问题', "不是「取法」问题")
t = t.replace('"全 None"**不是"空件没有分型"**', "「全 None」**不是「空件没有分型」**")
t = t.replace('**不是"空件没有分型"**', "**不是「空件没有分型」**")
t = t.replace('**"两者表象相同，别混"**', "**「两者表象相同，别混」**")
t = t.replace('而是**读错了对象**', "而是**读错了对象**")
t = t.replace('**是的"取法"**', "**是「取法」**")
t = t.replace('不是"取法"', "不是「取法」")
t = t.replace('**这是"假对象测试看不见真契约"的第 4 次**', "**这是「假对象测试看不见真契约」的第 4 次**")
t = t.replace('**"没有"与"读错"**', "**「没有」与「读错」**")
t = t.replace('把"全 None"当成"空件没有"', "把「全 None」当成「空件没有」")
t = t.replace('分辨"没有"与"读错"', "分辨「没有」与「读错」")
t = t.replace('**不是"空件没有分型"**', "**不是「空件没有分型」**")
t = t.replace('不是"取法"问题', "不是「取法」问题")
t = t.replace('"取法"', "「取法」")
t = t.replace('不是"取法"', "不是「取法」")
p.write_text(t, encoding="utf-8")
try:
    ast.parse(t)
    print("  修完语法 OK")
except SyntaxError as e:
    print("  L%s: %s" % (e.lineno, (e.text or "").strip()[:90]))
