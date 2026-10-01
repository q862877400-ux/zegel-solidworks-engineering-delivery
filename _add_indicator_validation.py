import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── ① 给 sw_gtol 加上「只允许那 5 个」的常量与校验 ──────────────────
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_gtol.py")
t = P.read_text(encoding="utf-8")

CONST = '''

#: ★★★ **官方限制**（轮 166 读 `C:/swapi/types/IGtolFrame/AddIndicator.md` 的 Remarks 读出）：
#: `IGtolFrame.AddIndicator` 的 `TolType` **只能是这 5 个** `swGtolGeomCharSymbol_e` 成员：
#: ```
#:   swGcsANG(20) · swGcsPARALLEL(22) · swGcsPERP(21) · swGcsCIRCRUNOUT(25) · swGcsSYMMETRY(13)
#: ```
#: ⚠⚠ 而 `GTOL_GEOM_SYMBOL` 里另外 14 个（`flatness` / `position` / `straightness` …）
#: **都不在这个清单里** ⇒ 传它们 `AddIndicator` **必然返回 `False`**。
#: ★ 这是本会话**第三次**「取值/形态不对」被读成「做不到」（前两次：事实 104 的 `CreateChamfer`、
#: 事实 105 的 `AddFrame` 顺序）⇒ 所以**在这里加一道明确的校验**，让错值**当场说清楚**。
INDICATOR_ALLOWED_TOL_TYPES = {
    20: "angularity", 22: "parallelism", 21: "perpendicularity",
    25: "circular_runout", 13: "symmetry",
}
'''
if "INDICATOR_ALLOWED_TOL_TYPES" not in t:
    #: 插在 `FIRST_FRAME` 定义之后（拿已有的锚）
    anchor = "FIRST_FRAME"
    i = t.find(anchor)
    j = t.find("\n\n", i)
    t = t[:j] + "\n" + CONST + t[j:]
    print("  ok 常量已加")
P.write_text(t, encoding="utf-8")
ast.parse(t)

# ── ② add_gtol_indicator 里加校验 ──────────────────────────────────
t = P.read_text(encoding="utf-8")
OLD = "    ensure_gtol_frame(gtol, frame)          # ⚑ 轮 120 加：先保证帧存在"
NEW = ('    #: ★★★ 轮 166 加的校验：`AddIndicator` 的 `TolType` **只能是那 5 个**\n'
       '    #: ⇒ 传别的**必然 False**（而过去会被读成"到不了"）。\n'
       '    if int(tol_type) not in INDICATOR_ALLOWED_TOL_TYPES:\n'
       '        raise ValueError(\n'
       '            "IGtolFrame.AddIndicator 的 TolType=%r **不在官方允许清单里** —— "\n'
       '            "官方 Remarks 明写只能是这 5 个：%s。\\n"\n'
       '            "⚠ 传别的（如 flatness / position / straightness）**必然返回 False**，"\n'
       '            "那不是"功能不行"，是**取值不对**。"\n'
       '            % (tol_type, INDICATOR_ALLOWED_TOL_TYPES)\n'
       '        )\n'
       '    ensure_gtol_frame(gtol, frame)          # ⚑ 轮 120 加：先保证帧存在')
if OLD in t:
    t = t.replace(OLD, NEW, 1)
    P.write_text(t, encoding="utf-8")
    ast.parse(t)
    print("  ok 校验已加进 add_gtol_indicator")
else:
    print("  ⚠ 锚点不符，跳过校验插入")
