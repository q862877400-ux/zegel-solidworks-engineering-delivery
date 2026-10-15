import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_in_context_reference_smoke.py")
t = P.read_text(encoding="utf-8")

#: 把「选边」从 `start_sketch` **之前**挪到**之后**
OLD_HEAD = '''        #: ⚠⚠ **`SketchUseEdge3` 用的是当前选择集** ⇒ 必须先**真的选中一条外部边**，'''
i = t.index(OLD_HEAD)
j = t.index('        chk("★★ 先**选中一条外部边**（`SketchUseEdge3` 的前置条件）", sel_ok,')
j = t.index("\n", j) + 1
SEL_BLOCK = t[i:j]
t = t[:i] + t[j:]

#: 插到 `sk = ...ActiveSketch...` 之后
ANCHOR = '''        sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")'''
assert ANCHOR in t, "锚点不符"
NEW_SEL = '''
        #: ⚠⚠⚠ **顺序很重要**（轮 162 查出）：`sw_part.start_sketch` 内部会
        #: `ClearSelection2(True)` ⇒ **它会把我刚选的那条边清掉**。
        #: ⇒ 正确顺序是：**先开草图 → 再选边 → 再投影**（第一版把选边放在开草图**之前**，
        #:   于是 `SketchUseEdge3` 拿到的是**空选择集** ⇒ 返回 ok 而**草图里 0 个实体**）。
''' + SEL_BLOCK.replace("        #: ⚠⚠ **`SketchUseEdge3` 用的是当前选择集** ⇒ 必须先**真的选中一条外部边**，",
                       "        #: `SketchUseEdge3` 用的是**当前选择集** ⇒ 此刻选它才作数。")
t = t.replace(ANCHOR, ANCHOR + "\n" + NEW_SEL, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已把选边挪到 start_sketch 之后")
