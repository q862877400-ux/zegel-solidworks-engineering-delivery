"""★ 复核 T-B：从实现文件里用 ast 抽 COM 调用的实参个数，与官方 arity 表机器比。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（复核工具）。规格 `specs/202-user-coverage-gaps` 的 task-3（T-C 独立复核）。
# 文件:   specs/202-user-coverage-gaps/recon/check_drawing_signatures.py
# 定位:   ★ 2026-10-03 task-3 的交付之一：**拿官方原文逐条比**，不是"读一遍觉得对"。
#   ① 官方 arity 逐字抄在 `recon/api-arity-drawing.md`；本脚本把同一张表**硬编码**进来
#      （防"表改了脚本没改"的静默漂移）——两者不一致时以 `C:\swapi\types\<接口>\<成员>.md` 为准。
#   ② 用 `ast` 抽三类调用：
#      · `get_com_member(obj, "成员", a1, a2, ...)` / `call_com_member` / `safe_get_com_member`
#        ⇒ COM 实参个数 = len(args) - 2（args[0]=obj、args[1]=成员名）
#      · `set_com_member(obj, "成员", value)` ⇒ COM 实参个数 = **0**
#        （★ `scripts/sw_connect.py:581` 的签名是 `set_com_member(obj, attr_name, value)`
#         ——它**不是**"取或调"，第三参是**值**不是 COM 实参 ⇒ 不按可变实参算）
#      · `obj.成员(a1, a2, ...)` ⇒ COM 实参个数 = len(args)
#   ③ 与官方 arity 比：**少传**（会 `类型不匹配` / `DISP_E_PARAMNOTOPTIONAL`）与**多传**都报。
#   ④ ★ **零实参那是已知的两用语义**：`get_com_member(obj, "Name")` 是"取或调"（事实 84/144），
#      ⇒ 对官方 arity > 0 的**方法**，零实参调用**单列**为一类（ZERO），
#      不混进"少传"里 —— 否则会把 471 个既有调用点全报成问题。
#   ⑤ ★ **无实参的调用不计入"13 成员到齐"** —— "取一次"不等于"按签名建出来"。
# 官方依据: `C:\swapi\types\IDrawingDoc\*.md` / `IView\*.md` / `ISheet\*.md` /
#   `IModelDoc2\*.md` / `IModelDocExtension\*.md` 的 `**Signature**:` 行（逐字，见 api-arity-drawing.md）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from pathlib import Path

#: 官方 arity：成员名 -> (参数个数, 参数名序列, 接口, 是否 Obsolete, 后继)
OFFICIAL: dict[str, tuple[int, str, str, bool, str]] = {
    "CreateDrawViewFromModelView3": (5, "ModelName, ViewName, LocX, LocY, LocZ", "IDrawingDoc", False, ""),
    "CreateSectionViewAt5": (7, "X, Y, Z, SectionLabel, Options, ExcludedComponents, SectionDepth", "IDrawingDoc", False, ""),
    "CreateDetailViewAt4": (12, "X, Y, Z, Style, Scale1, Scale2, LabelIn, Showtype, FullOutline, JaggedOutline, NoOutline, ShapeIntensity", "IDrawingDoc", False, ""),
    "InsertBreak": (4, "Orientation, Position1, Position2, Style", "IView", True, "InsertBreak2 -> InsertBreak3"),
    "CreateAuxiliaryViewAt2": (7, "X, Y, Z, NotAligned, Label, Showarrow, Flip", "IDrawingDoc", False, ""),
    "SetupSheet5": (11, "Name, PaperSize, TemplateIn, Scale1, Scale2, FirstAngle, TemplateName, Width, Height, PropertyViewName, RemoveModifiedNotes", "IDrawingDoc", True, "SetupSheet6"),
    "InsertSurfaceFinishSymbol3": (14, "SymType, LeaderType, LocX, LocY, LocZ, LaySymbol, ArrowType, MachAllowance, OtherVals, ProdMethod, SampleLen, MaxRoughness, MinRoughness, RoughnessSpacing", "IModelDocExtension", False, ""),
    "InsertDatumTag2": (0, "", "IModelDoc2", False, ""),
    "InsertNote": (1, "Text", "IModelDoc2", False, ""),
    "AutoBalloon5": (1, "BalloonOptions", "IDrawingDoc", False, ""),
    "InsertHoleTable2": (6, "UseAnchorPoint, X, Y, AnchorType, StartValue, TableTemplate", "IView", True, "InsertHoleTable3"),
    "InsertRevisionTable2": (7, "UseAnchorPoint, X, Y, AnchorType, TableTemplate, Shape, AutoUpdateZoomCells", "ISheet", False, ""),
    "InsertCenterMark3": (3, "Style, Propagate, Slot", "IDrawingDoc", False, ""),
}

#: 官方后继/辅助入口的 arity（"用后继版"时按这张表比 —— 铁律 4）
SUCCESSORS: dict[str, int] = {
    "InsertBreak2": 5,
    "InsertBreak3": 6,
    "SetupSheet6": 17,
    "InsertHoleTable3": 9,
    "CreateAutoBalloonOptions": 0,
    "InsertNewNote3": 9,
}

KNOWN = {**{k: v[0] for k, v in OFFICIAL.items()}, **SUCCESSORS}

#: 可变实参的 helper：`helper(obj, "成员", *com_args)` ⇒ COM 实参 = len(args) - 2
VARARG_HELPERS = {"get_com_member", "call_com_member", "safe_get_com_member"}
#: `set_com_member(obj, "成员", value)` ⇒ 第三参是**值**，不是 COM 实参
SET_HELPERS = {"set_com_member"}


def _call_name(node: ast.Call) -> str:
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return ""


def scan(path: Path) -> list[tuple[int, str, int, str]]:
    """回 [(行号, 成员, COM 实参个数, 调用形态)]。形态 = 'helper' | 'setter' | 'attribute'。"""
    src = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    out: list[tuple[int, str, int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        if name in VARARG_HELPERS and len(node.args) >= 2:
            a1 = node.args[1]
            if isinstance(a1, ast.Constant) and isinstance(a1.value, str):
                out.append((node.lineno, a1.value, len(node.args) - 2, "helper"))
        elif name in SET_HELPERS and len(node.args) >= 2:
            a1 = node.args[1]
            if isinstance(a1, ast.Constant) and isinstance(a1.value, str):
                out.append((node.lineno, a1.value, 0, "setter"))
        elif isinstance(node.func, ast.Attribute) and node.func.attr in KNOWN:
            out.append((node.lineno, node.func.attr, len(node.args), "attribute"))
    return out


def report(path: Path) -> int:
    rows = scan(path)
    hits = [r for r in rows if r[1] in KNOWN]
    bad = 0
    real: set[str] = set()
    print("=== %s：共 %d 个调用点，其中 %d 个在这 13 成员/后继表内" % (path, len(rows), len(hits)))
    for lineno, member, nargs, form in sorted(hits):
        exp = KNOWN[member]
        if nargs == exp:
            tag, note = "OK  ", ""
            real.add(member)
        elif nargs == 0 and exp > 0 and form == "helper":
            tag = "ZERO"
            note = "零实参 = '取或调' 语义（事实 84/144）⇒ 单列；★ 不算建出来"
        else:
            tag, note = "MISMATCH", ("少传" if nargs < exp else "多传")
            bad += 1
        print("  [%-8s] %s:%d  %s（COM 实参 %d / 官方 %d）形态=%s %s"
              % (tag, path.name, lineno, member, nargs, exp, form, note))
    missing = [m for m in OFFICIAL if m not in real]
    print("  ★ 按官方 arity 真调用到的：%d / 13" % len(real))
    print("  ★ 未按官方 arity 调用到的：%s" % (", ".join(missing) if missing else "（无）"))
    return bad


def main(argv: list[str]) -> int:
    targets = [Path(a) for a in argv[1:]]
    if not targets:
        print("用法: python check_drawing_signatures.py <实现文件.py> [...]")
        return 2
    bad = 0
    for path in targets:
        if not path.is_file():
            print("[MISS] %s 不存在（★ 实现未落盘）" % path)
            bad += 1
            continue
        bad += report(path)
    print("")
    print("结论：%s" % ("★ 有 MISMATCH/MISS，见上" if bad else "★ 本表内无 arity 不一致"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
