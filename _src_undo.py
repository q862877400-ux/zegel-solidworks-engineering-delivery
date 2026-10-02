import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_session.py")
t = p.read_text(encoding="utf-8")

SRC = """
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_session.py —— 追加 undo_report
# 定位:   objective② 的四家缺口 `undo`（★ 事实 311 三层证据判定的真缺）；官方
#   IModelDoc2.EditUndo2(int Steps)（★ 1 参、回 void）⇒ 判据只能是特征树退回（规则 6）。
# 官方依据: C:\\swapi\\types\\IModelDoc2\\EditUndo2.md（★ void EditUndo2(int Steps)）
#   · EditUndo（★ Obsolete）· SketchUndo()（★ 零参）· 反射 arity 1
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────
"""

KEY = "#: ★ 本模块新增入口所需的两个依赖（★ 就地 import，★ 避免动首部结构）"
if "覆盖:   后续同级定义" in t:
    print("  已有覆盖声明")
elif KEY in t:
    t = t.replace(KEY, SRC.strip() + "\n" + KEY, 1)
    p.write_text(t, encoding="utf-8")
    print("  已补来源块 + 覆盖声明")
else:
    print("  **未找到插入锚点**")
try:
    compile(p.read_text(encoding="utf-8"), str(p), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **错 L%s**: %s" % (e.lineno, str(e.msg)[:80]))
