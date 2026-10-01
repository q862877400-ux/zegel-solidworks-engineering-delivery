import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_server_wiring.py")
t = P.read_text(encoding="utf-8")

OLD_DOC = '''    """九批合计 37 条 —— 数字变了就说明有人加了批次（本测试要跟着更新）。

    ⚠ 历史：批次 1–4 合计 **20** 条；轮 90 新增 `tool_specs_batch5.py`（**5** 条）
    ⇒ 25。**本测试是"钉死数量"的守卫，加批次必须同时改这里**（这是它的设计意图：
    让"悄悄多注册了工具"这件事**可见**）。
    """'''
NEW_DOC = '''    """**十批**合计 **41** 条 —— 数字变了就说明有人加了批次（本测试要跟着更新）。

    ⚠ 历史：批次 1–4 合计 **20** 条；轮 90 新增 `tool_specs_batch5.py`（**5** 条）⇒ 25；
    轮 93/96/97/98 陆续加到 **37**；**轮 128 新增 `tool_specs_batch10.py`（4 条）⇒ 41** ——
    那 4 条是轮 123~127 **查证并真机跑过**的高层入口（`bbox` + 孔标准/紧固件链路）。
    **本测试是"钉死数量"的守卫，加批次必须同时改这里**（这是它的设计意图：
    让"悄悄多注册了工具"这件事**可见**）。
    """'''
if OLD_DOC in t:
    t = t.replace(OLD_DOC, NEW_DOC, 1)
    print("  ok docstring 已更新")
else:
    print("  ⚠ docstring 锚点不符")

import re
# 断言本体：把字面量 37 改成 41（只改这一处，谨慎）
m = re.search(r"assert len\(([^)]*)\) == 37", t)
if m:
    t = t[:m.start()] + ("assert len(%s) == 41" % m.group(1)) + t[m.end():]
    print("  ok 断言 37 -> 41")
else:
    # 可能写成别的形状，找找
    for i, l in enumerate(t.splitlines(), 1):
        if "37" in l:
            print("    L%-4d %s" % (i, l.strip()[:96]))
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")
