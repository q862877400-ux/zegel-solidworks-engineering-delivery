"""★ 真机：工程图 13 项（视图族 5 + 标注族 8）—— 每格先回读前置，再调用。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）· 规格 `specs/202-user-coverage-gaps`（T-D · C 类工程图
# 13 项）
# 文件:   tools/prove_drawing_batch.py
# 定位:   ★ 2026-10-03 ★ 为 `docs/user-feature-coverage.md` §八 的**工程图 13 项缺口**
#   写真机探针骨架。★★ **本文件只写真机步骤，不替调用方下结论**：
#     · 每格 = 一个 `case_*`；★ **先回读前置**（选区计数 / 枚举取值 / 模板是否找到），
#       前置不成立就**如实标注 `preconditions_held=False`** —— ★ 那一格**不能**当
#       「能力不成」的证据（★ 本仓事实 484 的教训：前置没满足被误读成"做不到"）。
#     · 判据**不只有特征树增量**：视图族数**视图数**、标注族数**注解数**（★ 规则 6）。
#
# ============  ================================  ======================================
# ==
#   格            官方成员（★ 接口）                  判据（★ 官方回读成员）
# ============  ================================  ======================================
# ==
#   V1  投影视图   CreateDrawViewFromModelView3 (IDrawingDoc) 视图数 +1 · 返回值非 None
# V2  剖面视图   CreateSectionViewAt5 (IDrawingDoc)         视图数 +1（★ 前置＝先选剖面
# 线）
#   V3  局部视图   CreateDetailViewAt4 (IDrawingDoc)          视图数 +1
# V4  断裂视图   **InsertBreak3** (IView)                   GetBreakLineCount +1 · IsBro
# ken
# V5  辅助视图   CreateAuxiliaryViewAt2 (IDrawingDoc)       视图数 +1（★ 前置＝选视图里
# 一条边）
# A1  图纸格式   **SetupSheet6** (IDrawingDoc)              SetupSheet6 回真 · 回读图纸
# 读数变了
#   A2  表面粗糙度 InsertSurfaceFinishSymbol3 (IModelDocExtension)  GetSFSymbolCount +1
#   A3  基准符号   InsertDatumTag2 (IModelDoc2)               GetDatumTagCount +1
#   A4  注释文字   InsertNote (IModelDoc2)                    GetNoteCount +1
# A5  气泡序号   AutoBalloon5 (IDrawingDoc)                 GetNoteCount +1（★ 前置＝有
# BOM 表）
#   A6  孔表       **InsertHoleTable3** (IView)               GetTableAnnotationCount +1
# A7  修订表     InsertRevisionTable2 (ISheet)              非 None · `ISheet.RevisionTa
# ble` 非 None
#   A8  中心符号线 InsertCenterMark3 (IDrawingDoc)            GetCenterMarkCount2 +1
# ============  ================================  ======================================
# ==
#
#   ★★★ **三条废弃链（★ 铁律 4「看后继」，官方页逐字）** —— 台账原先给的是**废弃入口**：
#     · `IView.InsertBreak`     → `Obsolete. Superseded by [[IView::InsertBreak2]]`
#       而 `InsertBreak2` 也废弃 → `Superseded by [[IView::InsertBreak3]]`
#       ⇒ ★ 本探针用 **`InsertBreak3`（6 参、未废弃）** ✓
#     · `IDrawingDoc.SetupSheet5` → `Obsolete. Superseded by [[IDrawingDoc::SetupSheet6]]`
#       ⇒ ★ 用 **`SetupSheet6`（17 参）** ✓
#     · `IView.InsertHoleTable2`  → `Obsolete. Superseded by [[IView::InsertHoleTable3]]`
#       ⇒ ★ 用 **`InsertHoleTable3`（9 参）** ✓
#     ★ 其余 10 项官方页**没有** Obsolete 行（★ 逐页核过，见下「官方依据」）。
#
#   ★★ **每格的"前置"都是从官方页 / 官方例子里读出来的**（★ 不是猜的；逐条写在各 case 的
#     docstring 与 `note` 里）。★ 最关键的几条：
# · `CreateDrawViewFromModelView3`：`ModelName` 必须是**含 `.sldprt`/`.sldasm` 的完整路
# 径**
# （官方 Remarks 逐字：Include the **.sldprt** or **.sldasm** extension in the pathname
# ）；
#       `ViewName` 要**与模型视图名完全一致**，★ 标准视图名**带星号**（官方逐字：the names of
# the standard views begin with an asterisk … for example, "*Front"）；Loc* 单位官方写明
#  **meters**。
# · `CreateSectionViewAt5`：**先选剖面线**（官方 Remarks 逐字：Before calling this metho
# d,
#       select the section line or lines to use as a section line.）★ 官方例子
#       `Create_Section_View_at_Specified_Location_Example_VB` 给的**调用序**是：
#       `ActivateView` → `SelectByID2(视图名,"DRAWINGVIEW")` → `ClearSelection2` →
#       `CreateLine2(...)`（★ 剖面线就是**在活动视图里画的一条草图线**）→ 才调建剖面视图。
#     · `CreateDetailViewAt4`：官方页**没有 Remarks**；★ 官方例子
#       `Create_Detail_Circle_and_Detail_View_Example_VB` 的调用序是
#       `ActivateView` → `SketchManager.CreateCircle(...)`（★ 局部圆＝草图圆）→ 才调。
#     · `InsertBreak3`：官方例子 `Insert_Jagged_Cut_Break_Example_VB` 的调用序是
#       `ActivateView` → `SelectByID2(视图名,"DRAWINGVIEW")` →
#       `SelectionManager.GetSelectedObject6(1,-1)` 取到 `IView` → 再调；
#       ★ 官方 Remarks：Position1/Position2 **相对视图原点**，方向决定它们是 X 还是 Y 值。
#     · `CreateAuxiliaryViewAt2`：官方摘要逐字 "Creates an auxiliary view based on a
#       **selected edge in a drawing view**"（★ 该页**无 Remarks**）⇒ 前置＝视图里选中一条边。
# · `InsertSurfaceFinishSymbol3`：官方 Remarks 逐字 "uses the location parameters … only
#  if
#       the surface finish symbol has a leader **leaderType != swNO_LEADER**"。
# · `InsertDatumTag2`：官方摘要逐字 "at a **selected location**"；★ 且本仓**已有真机反例
# **
#       （`output/drawing-datum-tag-evidence.json`：**不先选**时它回 `None`、计数 0→0）
#       ⇒ ★ 本探针把「选 / 不选」当**两个格子**（★ 单变量对照）。
# · `InsertNote`：官方 Remarks 逐字 "The leader attachment points for the new note come
# from
# the selections made before calling this method"；**没有选中时**：无引线、自由放置、在
# 原点。
# · `AutoBalloon5` + `CreateAutoBalloonOptions`：官方 **4 步调用序**（选视图/图纸 → 建 o
# ptions
# → 设属性 → 调 AutoBalloon5）；★ 前置是**图里有 BOM 表**（官方例子 precondition 逐字）
# 。
# · `InsertHoleTable3`：官方 Remarks **明写 mark 表**：基准原点**顶点 mark 1** · 孔**边
# 与面 mark 2**
#       · 基准原点 X 向参考 mark 4 · Y 向参考 mark 8；Template 是 `.sldholtbt`。
# · `InsertRevisionTable2`：官方 Returns 逐字 "[[Revision table]] **or null if a revisio
# n
#       table already exists**" ⇒ ★ 本探针把「插第二次」当**期望为 null** 的一格。
# · `InsertCenterMark3`：官方页**没有写前置**（Remarks 只说 `IView::AutoInsertCenterMark
# s`）
#       ⇒ ★ 本探针用「选 / 不选」两格**如实测**，★ 不假装知道前置。
#
#   官方依据（三源之① —— `C:\swapi\`；★ 逐页核过）:
# · types: `IDrawingDoc\{CreateDrawViewFromModelView3,CreateSectionViewAt5,CreateDetailV
# iewAt4,
#       CreateAuxiliaryViewAt2,SetupSheet6,SetupSheet5,AutoBalloon5,CreateAutoBalloonOptions,
#       InsertCenterMark3,ActivateView}.md` ·
# `IModelDocExtension\InsertSurfaceFinishSymbol3.md` · `IModelDoc2\{InsertDatumTag2,Inse
# rtNote}.md` ·
# `IView\{InsertBreak,InsertBreak2,InsertBreak3,InsertHoleTable2,InsertHoleTable3,GetOut
# line,
# GetBomTable,GetBreakLineCount,IsBroken}.md` · `ISheet\{InsertRevisionTable2,RevisionTa
# ble}.md`
#     · enums（★ 本探针**在运行期读这些页**取值，不把枚举写死 —— 见 `_enum`）:
# `swDwgTemplates_e` · `swDwgPaperSizes_e` · `swBreakLineOrientation_e` · `swBreakLineSt
# yle_e` ·
# `swDetViewStyle_e` · `swDetCircleShowType_e` · `swCreateSectionViewAtOptions_e`（**bit
# mask**）·
#       `swSFSymType_e` · `swLeaderStyle_e` · `swSFLaySym_e` · `swArrowStyle_e` ·
# `swBOMConfigurationAnchorType_e` · `swRevisionTableSymbolShape_e` · `swCenterMarkStyle
# _e` ·
# `swBalloonLayoutType_e` · `swBalloonStyle_e` · `swBalloonFit_e` · `swBalloonTextConten
# t_e` ·
#       `swBalloonItemNumbersOrder_e` · `swEditBalloonOption_e`
#     · examples（★ **调用序**只有例子给得出）: `Insert_Model_Annotations_Example_VB` ·
#       `Create_Section_View_at_Specified_Location_Example_VB` ·
# `Create_Detail_Circle_and_Detail_View_Example_VB` · `Insert_Jagged_Cut_Break_Example_V
# B` ·
#       `Add_Autoballoon_to_Face_Example_VB` · `Insert_Hole_Table_Example_VB` ·
#       `Create_Drawing_Sheet_Zones_Example_VB` · `Get_Annotations_Array_Example_VB` ·
#       `Insert_a_Note_Example_VB`
# 许可:   本仓库 MIT。★ **无第三方代码引入**（不外抄任何项目文本；官方例子只用来核**调用
# 序**）。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 怎么跑（★ 真机一律走弹窗护栏；★ 本轮**不由本文件的作者执行**）：
#     python tools/sw_guard.py --timeout 1800 -- python tools/prove_drawing_batch.py
#   ★ 只跑某几格（★ 卡住时省时间）：把**标签子串**当参数传进去，例如
#     python tools/sw_guard.py --timeout 900 -- python tools/prove_drawing_batch.py V4 A7
# ★ 产物：`output/drawing-batch-evidence.json`；★ 临时零件 `output/_probe_drawing_part.S
# LDPRT`。
# ★ 收尾：★ 每格自己关掉自己开的文档（`CloseDoc`）· ★ `CommandInProgress` 复位 ·
#   ★ **不保存任何已有文件**（★ 只在 `output/` 下新建临时零件）。

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import scripts.sw_drawing_query as DQ  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402

#: ★ 官方 `SelectByID2` 按点选时用的 z —— ★ 逐字抄自官方例子
#:   `Insert_Hole_Table_Example_VB` 的 `SelectByID2("", "VERTEX", …, **-500.0075**, …)`
#:   （★ 工程图里按点选用的就是这个量级的 z；★ 不是我们编的数）。
PICK_Z_M = -500.0075

#: ★ 视图落位（**米** —— 官方对 `CreateDrawViewFromModelView3` 的 Loc* 逐字写着 "in mete
#: rs"）。
VIEW_LOC_M = (0.14, 0.12)

#: ★ 官方对 `CreateSectionViewAt5` / `CreateDetailViewAt4` / `CreateAuxiliaryViewAt2` 的
#: 位置参数
#:   **只说 "position"**、没写单位；★ 而官方例子里那些数（0.223 / 0.65）与**米**一致
#:   ⇒ ★ 本探针按**米**传，并把这条**假设**记进返回值（★ 铁律 5：查不到就说清楚假设）。
SHEET_POS_UNIT_ASSUMPTION = (
    "★ 官方只写 position、未给单位；官方例子的量级与**米**一致 ⇒ 本探针按米传"
)

#: ★ `SectionDepth` = "Distance from the selected section line"（官方逐字），**单位与默
#: 认值官方都没给**
#:   ⇒ ★ 本探针传 0.05 米并**如实标注这是假设**。
SECTION_DEPTH_M = 0.05

#: ★ 枚举页根（★ 取值在**运行期**从这些官方页读，不写死 —— 见 `_enum`）。
SWAPI_ENUMS = Path(r"C:\swapi\enums")

OUT_JSON = R / "output" / "drawing-batch-evidence.json"
PART_PATH = R / "output" / "_probe_drawing_part.SLDPRT"

_ENUM_CACHE: dict[tuple[str, str], tuple[int | None, str | None]] = {}


# ── 小助手 ───────────────────────────────────────────────────────────
def _get(o, name, *a):
    """★ 本仓统一的 COM 取/调（`sw_connect.get_com_member`）。"""
    return C.get_com_member(o, name, *a)


def _close(sw, doc):
    """★ 关掉**自己开的**文档（★ 不保存）。"""
    try:
        t = str(_get(doc, "GetTitle") or "")
        if t:
            _get(sw, "CloseDoc", t)
    except Exception:  # noqa: BLE001
        pass


def _enum(enum_name: str, member: str):
    """★ **在官方枚举页里现场取枚举值** ⇒ `(value|None, 来源或原因)`。

    ★★ 为什么不在代码里写死：★ 枚举值属于**官方数据**，写死一份就会与出厂值漂移；
      ★ 而本仓又多处栽在「凭记忆写枚举」上 ⇒ 这里**每次读官方页**，★ 读不到就**回 None 并说明**。
    ★ 解析规则（★ 只认页里那张 `| Member | Value |` 表）：
      · Value 列形如 `12` / `4 or 0x4; 说明…` / `0x1 or 1` ⇒ ★ **先试 `0x…`，再试十进制**。
    """
    key = (enum_name, member)
    if key in _ENUM_CACHE:
        return _ENUM_CACHE[key]
    page = SWAPI_ENUMS / ("%s.md" % enum_name)
    val: int | None = None
    note: str | None = None
    if not page.is_file():
        note = "★ 官方枚举页不在本机：%s" % page
    else:
        try:
            text = page.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            text, note = "", "★ 读官方枚举页失败：%s" % str(exc)[:120]
        if text:
            for line in text.splitlines():
                if not line.startswith("|"):
                    continue
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) < 2 or cells[0] != member:
                    continue
                raw = cells[1]
                m = re.match(r"^0x([0-9a-fA-F]+)", raw) or re.match(r"^(-?\d+)", raw)
                if m:
                    val = (
                        int(m.group(1), 16)
                        if raw.lower().startswith("0x")
                        else int(m.group(1))
                    )
                    note = str(page)
                else:
                    note = "★ %s 的 Value 列不是数字（%r）⇒ 不解析、不猜" % (
                        member,
                        raw[:60],
                    )
                break
            else:
                note = "★ 官方枚举页 %s 里没有成员 %s ⇒ 不猜" % (page.name, member)
    _ENUM_CACHE[key] = (val, note)
    return val, note


def _ev(row: dict, enum_name: str, member: str, label: str = ""):
    """★ 取枚举值；取不到就**记进 row 并回 None**（★ 调用方据此跳过该格，不硬凑）。"""
    val, note = _enum(enum_name, member)
    if val is None:
        row.setdefault("enum_missing", []).append(
            "%s.%s%s ⇒ %s"
            % (enum_name, member, ("（%s）" % label) if label else "", note or "")
        )
    return val


def _sel_counts(doc, marks=(0, 1, 2, 4, 8)) -> dict:
    """★ 回读**按标记分组**的选区计数 —— ★ 事实 8：`SelectByID2` 的返回值不可信。

    ★★ 这是本探针的**核心纪律**：★ 每次调用前先看这张表 ⇒ 前置没成立就**不把失败读成"
    能力不成"（★ 事实 484 的教训；`prove_split_line_minimal_matrix.py` 同法）。
    """
    out = {}
    for m in marks:
        try:
            out[str(m)] = int(
                _get(_get(doc, "SelectionManager"), "GetSelectedObjectCount2", m)
            )
        except Exception:  # noqa: BLE001
            out[str(m)] = -1
    return out


def _clear(doc):
    """★ 清空选区（`IModelDoc2.ClearSelection2(True)`）—— ★ 每格开头都做，★ 免得上格残留。"""
    try:
        _get(doc, "ClearSelection2", True)
    except Exception:  # noqa: BLE001
        pass


def _vname(view) -> str:
    """★ 视图名（`GetName2`，★ 退回 `Name` —— 与 `sw_drawing_query` 同口径）。"""
    for attr in ("GetName2", "Name"):
        try:
            v = _get(view, attr)
            if v:
                return str(v)
        except Exception:  # noqa: BLE001
            continue
    return ""


def _chain(doc):
    """★ 视图链 `GetFirstView()` → `GetNextView()`（★ **含**"图纸本身"那个伪视图）。"""
    out: list = []
    try:
        v = _get(doc, "GetFirstView")
    except Exception as exc:  # noqa: BLE001
        return [], "%s: %s" % (type(exc).__name__, str(exc)[:120])
    n = 0
    while v is not None and n < 500:  #: ★ 上限防死循环
        n += 1
        out.append(v)
        try:
            v = _get(v, "GetNextView")
        except Exception:  # noqa: BLE001
            break
    return out, None


def _real_views(doc):
    """★ **真视图**（★ 排除"图纸本身"那个伪视图）。

    ★★ 不自己判那个陷阱：★ 先向 `scripts/sw_drawing_query.list_views`（**已真机验证过**
      "空图纸上 `GetFirstView()` 回的是图纸本身、`Type == 1`"的那一处）取**名单**，再按名对上对象。
    """
    try:
        names = [str((r or {}).get("name") or "") for r in (DQ.list_views(doc) or [])]
    except Exception as exc:  # noqa: BLE001
        return [], "取视图清单失败：%s: %s" % (type(exc).__name__, str(exc)[:120])
    chain, err = _chain(doc)
    if err:
        return [], err
    return [v for v in chain if _vname(v) in names], None


def _view_count(doc):
    """★ **视图数**（判据之一 —— ★ 不用特征树增量）。"""
    try:
        return len(DQ.list_views(doc) or [])
    except Exception:  # noqa: BLE001
        return None


#: ★ 各族的**官方回读成员**（★ 全部零参；★ 判据不许只看特征树）
_COUNTERS = (
    ("anno", "GetAnnotationCount"),  #: 视图里的注解总数
    ("sf", "GetSFSymbolCount"),  #: 表面粗糙度符号
    ("datum", "GetDatumTagCount"),  #: 基准符号
    ("note", "GetNoteCount"),  #: 注释（★ 气泡也是 note）
    ("center", "GetCenterMarkCount2"),  #: 中心符号线
    ("table", "GetTableAnnotationCount"),  #: 表格（孔表 / 修订表 / BOM）
    ("datum_origin", "GetDatumOriginCount"),  #: 基准原点
)
#: ★★ **带 `out` 参数的计数成员** —— ★ 与上面那张**零参表不能混**：
#:   官方签名逐字 `System.int GetBreakLineCount( out System.int Size )` ⇒
#:   ★ **必须传 by-ref 包装**（本仓 `sw_connect.out_i4()`；与 known-facts 47 同族）；
#:   ★ 零参调用会 `类型不匹配`，而被 `except` 吃成 `None` ⇒ **判据静默降级**，
#:     表面上只看到"量不到"，看不出是**调用形态错**。
#: ★ 2026-10-03：space-bunny 的 L5 档实测发现此处原先把 `GetBreakLineCount` 放进了上面那
#: 张零参表
#:     （于是**两条路径都错**）；Lead 核官方页确认后分到这里。
#: ★ 格式：`(键, 带 out 的成员, 零参交叉核成员)` —— ★ **兼用零参 `GetBreakLines()` 数组
#: 长度做交叉核**，
#:     两条独立读数一致才算稳（单条读数不可靠时不许当判据）。
_OUT_COUNTERS = (("breakline", "GetBreakLineCount", "GetBreakLines"),)


def _anno_state(doc) -> dict:
    """★ 注解读数：**真视图**与**整条视图链**各算一份（★ 判据取"任一份涨了"）。

    ⚠ 为什么要两份：★ 有些注解挂在**图纸**上而不挂在某个视图里 ⇒ 只数真视图会漏；
      ★ 而整条链又把"图纸本身"算了进来 ⇒ ★ 两份都报出来，★ 让人看得见是哪一份涨的。
    """
    real, _err = _real_views(doc)
    chain, _e2 = _chain(doc)
    state: dict = {}
    for label, views in (("real", real), ("all", chain)):
        rows = []
        for v in views:
            row = {"name": _vname(v)}
            for key, member in _COUNTERS:
                try:
                    row[key] = int(_get(v, member) or 0)
                except Exception:  # noqa: BLE001
                    row[key] = None
            # ★ 带 `out` 参数的成员走**另一条**通道（★ 零参调它会 `类型不匹配` ⇒ 见 `_OU
            # T_COUNTERS`）
            for key, member, member2 in _OUT_COUNTERS:
                row[key] = _out_count_of(v, member)
                row[key + "_crosscheck"] = _list_len_of(v, member2)
            rows.append(row)
        totals = {}
        for key, _m in _COUNTERS:
            vals = [r[key] for r in rows if isinstance(r.get(key), int)]
            totals[key] = sum(vals) if vals else None
        for key, _m, _m2 in _OUT_COUNTERS:
            vals = [r[key] for r in rows if isinstance(r.get(key), int)]
            totals[key] = sum(vals) if vals else None
            vals2 = [
                r[key + "_crosscheck"]
                for r in rows
                if isinstance(r.get(key + "_crosscheck"), int)
            ]
            totals[key + "_crosscheck"] = sum(vals2) if vals2 else None
        state[label] = {"count": len(rows), "totals": totals, "per_view": rows}
    return state


def _delta(before, after, key, bucket="all"):
    """★ 增量（★ 任一份量不到就回 None ⇒ 判据降级，不猜）。"""
    try:
        b = before[bucket]["totals"].get(key)
        a = after[bucket]["totals"].get(key)
    except Exception:  # noqa: BLE001
        return None
    if b is None or a is None:
        return None
    return int(a) - int(b)


def _outline(view):
    """★ 视图包围盒（★ 官方 `IView.GetOutline`：**4 个 double，单位米**，`[xmin,ymin,xmax,ymax]`）。"""
    try:
        raw = _get(view, "GetOutline")
        vals = [float(x) for x in raw]
    except Exception:  # noqa: BLE001
        return None
    return vals if len(vals) >= 4 else None


def _inside_points(bbox):
    """★ 由视图包围盒推出**一组**候选拾取点（★ 都在视图内，从中心往外）。

    ★ 为什么给一串：★ 工程图里"按点选"要求点**落在**目标实体上，★ 落空就是选不中
      ⇒ ★ 逐个试并**回读计数**，★ 把"哪个点选上了"写进读数（★ 不猜）。
    """
    xmin, ymin, xmax, ymax = bbox[:4]
    xm, ym = (xmin + xmax) / 2.0, (ymin + ymax) / 2.0
    w, h = (xmax - xmin), (ymax - ymin)
    return [
        (xm, ym),  #: 中心（★ 带孔的视图 ⇒ 一般落在孔边/面上）
        (xmin + 0.05 * w, ym),
        (xmax - 0.05 * w, ym),
        (xm, ymin + 0.05 * h),
        (xm, ymax - 0.05 * h),
        (xmin + 0.02 * w, ymin + 0.02 * h),
        (xmax - 0.02 * w, ymax - 0.02 * h),
        (xmin + 0.02 * w, ymax - 0.02 * h),
        (xmax - 0.02 * w, ymin + 0.02 * h),
    ]


def _pick(doc, kind, x, y, mark=0, append=False):
    """★ 按点选（`IModelDocExtension.SelectByID2`，★ 9 参、第 7 个是 `Mark`）。

    ★ 官方例子（`Insert_Hole_Table_Example_VB`）在**工程图**里就是这么按点选的：
      `SelectByID2("", "VERTEX", x, y, -500.0075, True, 1, Nothing, 0)`。
    ★ 判据 = **回读计数涨了**（★ 事实 8：返回值不可信）。
    """
    try:
        _get(
            _get(doc, "Extension"),
            "SelectByID2",
            "",
            str(kind),
            float(x),
            float(y),
            float(PICK_Z_M),
            bool(append),
            int(mark),
            C.create_empty_dispatch_variant(),
            0,
        )
    except Exception as exc:  # noqa: BLE001
        return False, "%s: %s" % (type(exc).__name__, str(exc)[:120])
    return True, None


def _pick_any(doc, kind, points, mark=0, append=False, marks=(0, 1, 2, 4, 8)):
    """★ 在候选点上**逐个试**按点选，直到**回读计数**涨了 ⇒ `(命中的点 | None, 计数, 错误)`。"""
    before = _sel_counts(doc, marks)
    errs = []
    for x, y in points:
        ok, err = _pick(doc, kind, x, y, mark=mark, append=append)
        if err:
            errs.append(err)
        after = _sel_counts(doc, marks)
        if sum(v for v in after.values() if v > 0) > sum(
            v for v in before.values() if v > 0
        ):
            return (round(x, 6), round(y, 6)), after, (errs or None)
    return None, _sel_counts(doc, marks), (errs or None)


def _activate_view(doc, name) -> bool:
    """★ 激活视图（`IDrawingDoc.ActivateView(string)`；★ 官方 Remarks：激活**图纸**会回 false）。"""
    try:
        return bool(_get(doc, "ActivateView", str(name)))
    except Exception:  # noqa: BLE001
        return False


def _select_view(doc, name, mark=0):
    """★ 按名选中视图（官方例子在工程图里用的就是 `SelectByID2(名字,"DRAWINGVIEW",…)`）。

    ★ 回 `(ok, 计数)`；★ `ok` 以**回读计数**为准（★ 事实 8）。
    """
    try:
        _get(
            _get(doc, "Extension"),
            "SelectByID2",
            str(name),
            "DRAWINGVIEW",
            0.0,
            0.0,
            0.0,
            False,
            int(mark),
            C.create_empty_dispatch_variant(),
            0,
        )
    except Exception as exc:  # noqa: BLE001
        return False, {"err": "%s: %s" % (type(exc).__name__, str(exc)[:120])}
    return True, _sel_counts(doc)


def _find_files(patterns, roots):
    """★ 在若干根目录下按扩展名找文件（★ 用到才找，★ 找不到就如实回空）。"""
    hits = []
    for root in roots:
        try:
            base = Path(root)
            if not base.is_dir():
                continue
            for pat in patterns:
                hits.extend(sorted(str(p) for p in base.rglob(pat)))
        except OSError:
            continue
    return hits


#: ★ 表格/图纸格式模板的**官方规则**（逐字）：表格模板在 `install_dir\lang\<language>`
#:   —— 孔表是 `.sldholtbt`（`InsertHoleTable3` 的 Remarks）· 修订表是 `.sldrevtbt`
#: （`InsertRevisionTable2` 的 Remarks）· 图纸格式是 `.slddrt`（SetupSheet6 的 Remarks +
#:  官方例子）。
TEMPLATE_ROOTS = (
    r"C:\ProgramData\SOLIDWORKS",
    r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang",
    r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang",
    r"C:\ProgramData\SolidWorks",
)


def _hole_table_template():
    """★ 孔表模板（★ 优先官方 Remarks 举的那个名字）。"""
    hits = _find_files(("standard hole table--letters.sldholtbt",), TEMPLATE_ROOTS)
    return (hits or _find_files(("*.sldholtbt",), TEMPLATE_ROOTS) or [None])[0]


def _revision_table_template():
    """★ 修订表模板（★ 优先官方 Remarks 举的那个名字）。"""
    hits = _find_files(("standard revision block.sldrevtbt",), TEMPLATE_ROOTS)
    return (hits or _find_files(("*.sldrevtbt",), TEMPLATE_ROOTS) or [None])[0]


def _sheet_format_template():
    """★ 图纸格式模板 `.slddrt`（★ 优先横向 A 幅）。"""
    hits = _find_files(("a - landscape.slddrt",), TEMPLATE_ROOTS)
    return (hits or _find_files(("*.slddrt",), TEMPLATE_ROOTS) or [None])[0]


def _new_drawing(sw, row: dict):
    """★ 新建工程图文档（★ 模板找不到就把**原因**写进 row，不硬失败）。"""
    try:
        return C.new_document(sw, "drawing")
    except Exception as exc:  # noqa: BLE001
        row["drawing_template_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        cand = _find_files(
            ("*.drwdot",), (r"C:\ProgramData\SOLIDWORKS", r"C:\ProgramData\SolidWorks")
        )
        if not cand:
            return None
        row["drawing_template_fallback"] = cand[0]
        try:
            return C.new_document(sw, "drawing", template_path=cand[0])
        except Exception as exc2:  # noqa: BLE001
            row["drawing_template_err2"] = "%s: %s" % (
                type(exc2).__name__,
                str(exc2)[:160],
            )
            return None


def _build_part(sw, row: dict):
    """★ 建一个**带孔**的板并**存盘**（★ 存盘是硬要求 —— 见下）。

    ★★ 为什么必须存盘：官方 `CreateDrawViewFromModelView3` 的 Remarks 逐字要求
      `ModelName` 是**完整路径**且**含 `.sldprt`/`.sldasm` 扩展名**。
    ★ 板上打一个孔：★ 好让"孔表 / 中心符号线 / 辅助视图"有**圆边**可用。
    """
    doc = C.new_document(sw, "part")
    try:
        P.start_sketch(doc, plane_name="Front Plane")
        _get(
            _get(doc, "SketchManager"),
            "CreateCornerRectangle",
            -0.04,
            -0.03,
            0.0,
            0.04,
            0.03,
            0.0,
        )
        P.end_sketch(doc)
        names = [
            n
            for n in (P.feature_names(doc) or [])
            if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
        ]
        if not names:
            row["extrude_err"] = "找不到草图特征名（feature_names 没回草图）"
            return None
        P.extrude_boss(doc, names[-1], 0.01)
        row["extrude_sketch"] = names[-1]
    except Exception as exc:  # noqa: BLE001
        row["extrude_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        return None
    try:
        from scripts import sw_hole_features as HF

        rep = HF.create_hole_wizard_at_selection_report(doc, "+z", "M8")
        row["hole"] = {k: rep.get(k) for k in ("ok", "selection_mark") if k in rep}
    except Exception as exc:  # noqa: BLE001
        #: ★ 孔不成**不阻断**：★ 只是"孔表/中心符号线"那两格的前置会更弱 ⇒ 如实记下来
        row["hole_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    try:
        row["saved"] = bool(C.save_document(doc, str(PART_PATH)))
    except Exception as exc:  # noqa: BLE001
        row["save_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        row["saved"] = False
    return doc if row.get("saved") else None


def _resolve_model_view_name(part_doc, info: dict | None = None):
    """★ **问模型自己**要一个合法视图名（★ 不硬编码 —— 名字会被 UI 本地化）。

    ★★ 依据（2026-10-03 真机发现，事实 494）：官方 `CreateDrawViewFromModelView3` 的 Remarks 要求
      `ViewName` "**exactly match**" 模型视图名，而它给的例子 `"*Front"` 是**英文界面**的取值
      ⇒ ★ 本机是**中文界面** ⇒ 名字是 `*前视` / `*正视于` … ⇒ **用 `*Front` 必回 `None` 且无任何报错**。
    ★ 正解：用 **`IModelDoc2.GetModelViewNames()`**（零参、**未废弃**）拿真实名单。
      ⚠ 同族的 `GetModelViewCount()` 官方标 **Obsolete** ⇒ **不用它**（用名单长度代替）。
    """
    try:
        names = [
            str(x) for x in (C.get_com_member(part_doc, "GetModelViewNames") or [])
        ]
    except Exception as exc:  # noqa: BLE001
        names = []
        if info is not None:
            info["view_names_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    if info is not None:
        info["model_view_names"] = names
    return names[0] if names else None


def _drawing_with_view(sw, part_doc, row: dict, view_name=None):
    """★ 建工程图 + 插一个模型视图 ⇒ `(drawing, 视图名 | None, 信息)`。

    ★ 前置（官方 Remarks）：`ViewName` 必须与**模型视图名完全一致**，★ 标准视图名**带星号**。
    ★★ `view_name=None` ⇒ **向模型要名字**（★ 不硬编码 —— 见 `_resolve_model_view_name` 的本地化坑）。
    """
    info: dict = {}
    if part_doc is None:
        return None, None, {"err": "★ 前置未成立：零件文档不在（没建成/没存盘）"}
    if view_name is None:
        view_name = _resolve_model_view_name(part_doc, info)
    info["view_name_used"] = view_name
    if not view_name:
        return (
            None,
            None,
            {"err": "★ 前置未成立：问不到模型视图名（GetModelViewNames 回空）", **info},
        )
    doc = _new_drawing(sw, row)
    if doc is None:
        return None, None, {"err": "新建工程图失败（★ 见 row 里的模板原因）", **info}
    info["views_before"] = _view_count(doc)
    try:
        ret = _get(
            doc,
            "CreateDrawViewFromModelView3",
            str(PART_PATH),
            str(view_name),
            float(VIEW_LOC_M[0]),
            float(VIEW_LOC_M[1]),
            0.0,
        )
        info["ret_is_none"] = ret is None
    except Exception as exc:  # noqa: BLE001
        info["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
    info["views_after"] = _view_count(doc)
    views, _err = _real_views(doc)
    info["view_names"] = [_vname(v) for v in views]
    return doc, (info["view_names"][0] if info["view_names"] else None), info


# ── 视图族 ───────────────────────────────────────────────────────────
def case_v1_draw_view_from_model_view(sw):
    """★ V1 投影视图：`IDrawingDoc.CreateDrawViewFromModelView3(ModelName, ViewName, LocX, LocY, LocZ)`。

    ★ 前置（官方 Remarks 逐字）：① `ModelName` = **完整路径 + `.sldprt`**；
      ② `ViewName` 与模型视图名**完全一致**，标准视图名**带星号**
        —— ★★ **不要照抄官方举例的 `"*Front"`**：那是**英文界面**的取值；
        ★ 本机中文界面是 `*前视` / `*正视于` ⇒ ★ 本格**向模型要名字**（`GetModelViewNames`，
        事实 494 真机 6/7 建成）；
      ③ Loc* 单位是**米**。
    ★ 判据：**视图数 +1** 且**返回值非 None**。
    """
    row = {
        "tag": "★ V1 投影视图（CreateDrawViewFromModelView3）",
        "ok": False,
        "preconditions": {"model_saved_with_extension": None, "view_name": None},
    }
    part = None
    doc = None
    try:
        part = _build_part(sw, row)
        row["preconditions"]["model_saved_with_extension"] = bool(
            part is not None
            and str(PART_PATH).lower().endswith(".sldprt")
            and PART_PATH.is_file()
        )
        if part is None:
            row["note"] = "★ 前置未成立：零件没建/没存盘 ⇒ 本格不作判据"
            return row
        # ★★ 问模型要合法视图名（★ 不硬编码 —— 名字会被 UI 本地化，事实 494）
        vname = _resolve_model_view_name(part, row)
        row["preconditions"]["view_name"] = vname
        if not vname:
            row["note"] = "★ 前置未成立：问不到模型视图名 ⇒ 本格不作判据"
            return row
        doc = _new_drawing(sw, row)
        if doc is None:
            row["note"] = "★ 前置未成立：新建工程图失败 ⇒ 本格不作判据"
            return row
        before = _view_count(doc)
        ret = _get(
            doc,
            "CreateDrawViewFromModelView3",
            str(PART_PATH),
            str(vname),
            float(VIEW_LOC_M[0]),
            float(VIEW_LOC_M[1]),
            0.0,
        )
        after = _view_count(doc)
        row.update(
            {
                "views_before": before,
                "views_after": after,
                "ret_is_none": ret is None,
                "view_names": [_vname(v) for v in _real_views(doc)[0]],
                "loc_m": list(VIEW_LOC_M),
                "unit": "★ 官方 Remarks 逐字：LocX/LocY/LocZ 单位 **meters**",
            }
        )
        row["ok"] = bool(
            ret is not None
            and before is not None
            and after is not None
            and after == before + 1
        )
        row["verified_by"] = "view_count_delta + return_not_none"
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if part is not None:
            _close(sw, part)
        if doc is not None:
            _close(sw, doc)
    return row


def _prep_section_line(doc, view_name, row: dict, explicit_pick=False):
    """★ 预备剖面线（★ 照官方例子的**调用序**）⇒ 回 `(命中点 | None, 计数, 错误)`。

    官方例子 `Create_Section_View_at_Specified_Location_Example_VB` 的顺序：
      ① `ActivateView(视图名)` ② `SelectByID2(视图名,"DRAWINGVIEW")` ③ `ClearSelection2`
      ④ `CreateLine2(x1,y1,0,x2,y2,0)` —— ★ **剖面线就是活动视图里画的一条草图线**
    ⚠ 例子在 `CreateLine2` 之后**没有**再显式选那条线（★ 隐含它被留下选中）⇒ ★ 本探针
      **先回读计数**；★ 若为 0，`explicit_pick=True` 时再试**按点选**（★ 见调用处的标注）。
    """
    views, _err = _real_views(doc)
    view = None
    for v in views:
        if _vname(v) == view_name:
            view = v
            break
    row["activated"] = _activate_view(doc, view_name)
    _ok, counts = _select_view(doc, view_name, mark=0)
    row["sel_view_counts"] = counts
    _clear(doc)
    if view is None:
        return None, _sel_counts(doc), "★ 取不到视图对象 ⇒ 无法取包围盒"
    bbox = _outline(view)
    row["view_outline_m"] = [round(v, 6) for v in bbox] if bbox else None
    if not bbox:
        return None, _sel_counts(doc), "★ IView.GetOutline 没回 4 个数"
    xmin, ymin, xmax, ymax = bbox[:4]
    y_mid = (ymin + ymax) / 2.0
    p1 = (xmin + 0.1 * (xmax - xmin), y_mid)
    p2 = (xmax - 0.1 * (xmax - xmin), y_mid)
    try:
        _get(
            _get(doc, "SketchManager"),
            "CreateLine2",
            float(p1[0]),
            float(p1[1]),
            0.0,
            float(p2[0]),
            float(p2[1]),
            0.0,
        )
        row["line_drawn"] = [
            round(p1[0], 6),
            round(p1[1], 6),
            round(p2[0], 6),
            round(p2[1], 6),
        ]
    except Exception as exc:  # noqa: BLE001
        return (
            None,
            _sel_counts(doc),
            "CreateLine2 失败：%s: %s" % (type(exc).__name__, str(exc)[:140]),
        )
    counts = _sel_counts(doc)
    if explicit_pick and sum(v for v in counts.values() if v > 0) == 0:
        #: ★★ 对照格：按点选那条草图线。⚠ 类型串 `SKETCHSEGMENT` 本探针**没在官方页里核
        #: 过**
        #:   ⇒ ★ 它**只是对照**：不成也不构成"剖面线选不上"的结论（★ 铁律 5）。
        hit, counts2, errs = _pick_any(
            doc, "SKETCHSEGMENT", [(xmin + 0.5 * (xmax - xmin), y_mid)], mark=0
        )
        row["explicit_pick"] = {
            "hit": hit,
            "counts": counts2,
            "errs": errs,
            "note": "★ 类型串 `SKETCHSEGMENT` 未在官方页核过 ⇒ 仅作对照格",
        }
        counts = counts2
    return None, counts, None


def case_v2_section_view(sw, excluded="empty_dispatch"):
    """★ V2 剖面视图：`IDrawingDoc.CreateSectionViewAt5(X,Y,Z,SectionLabel,Options,ExcludedComponents,SectionDepth)`。

    ★ 前置（官方 Remarks 逐字）：**先选剖面线**（"select the section line or lines …"）。
    ★ `Options` 是 `swCreateSectionViewAtOptions_e`（官方说它是 **bitmask**）⇒ ★ 本格传 **0**
      （★ bitmask 的 0 就是"一位都不置"，★ 不是猜的取值）。
    ★ `ExcludedComponents` 官方类型是 `System.object`、At3 的官方例子传的是一个**数组**
      ⇒ ★ 本探针把它当**单变量**试两种形态（空 Dispatch / 空数组）。
    ★ 判据：**视图数 +1**（★ 前置成立才算）。
    """
    row = {
        "tag": "★ V2 剖面视图（CreateSectionViewAt5 · excluded=%s）" % excluded,
        "ok": False,
    }
    part = None
    doc = None
    try:
        part = _build_part(sw, row)
        if part is None:
            row["note"] = "★ 前置未成立：零件没建成 ⇒ 本格不作判据"
            return row
        doc, view_name, info = _drawing_with_view(sw, part, row)
        row["parent_view"] = info
        if doc is None or not view_name:
            row["note"] = "★ 前置未成立：父视图没建成 ⇒ 本格不作判据（★ 见 case V1）"
            return row
        _hit, counts, perr = _prep_section_line(doc, view_name, row)
        row["sel_by_mark_before_call"] = counts
        if perr:
            row["err"] = perr
        row["preconditions_held"] = bool(sum(v for v in counts.values() if v > 0) > 0)
        excluded_arg = (
            [] if excluded == "empty_array" else C.create_empty_dispatch_variant()
        )
        row["excluded_components_form"] = excluded
        before = _view_count(doc)
        try:
            ret = _get(
                doc,
                "CreateSectionViewAt5",
                float(VIEW_LOC_M[0]),
                float(VIEW_LOC_M[1]),
                0.0,
                "A",
                0,
                excluded_arg,
                float(SECTION_DEPTH_M),
            )
            row["ret_is_none"] = ret is None
        except Exception as exc:  # noqa: BLE001
            row["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        after = _view_count(doc)
        row.update(
            {
                "views_before": before,
                "views_after": after,
                "view_names": [_vname(v) for v in _real_views(doc)[0]],
                "section_depth_m": SECTION_DEPTH_M,
                "unit": SHEET_POS_UNIT_ASSUMPTION,
                "options": "0（★ swCreateSectionViewAtOptions_e 官方说是 bitmask ⇒ 0 = 一位都不置）",
            }
        )
        row["view_delta"] = (
            None if (before is None or after is None) else after - before
        )
        row["ok"] = bool(row["preconditions_held"] and row["view_delta"] == 1)
        if not row["preconditions_held"]:
            row["note"] = (
                "★ 前置未成立（调用前选区为空）⇒ 本格**不能**当"
                "「剖面视图不成」的证据；★ 先解决「剖面线怎么被选中」"
            )
        row["verified_by"] = "view_count_delta（★ 前置成立才算）"
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if part is not None:
            _close(sw, part)
        if doc is not None:
            _close(sw, doc)
    return row


def case_v3_detail_view(sw):
    """★ V3 局部视图：`IDrawingDoc.CreateDetailViewAt4(…)`（★ 官方 **12 参**）。

    ★ 前置：官方页**没有 Remarks**；★ 官方例子 `Create_Detail_Circle_and_Detail_View_Example_VB`
      的调用序是 `ActivateView` → `SketchManager.CreateCircle(...)`（★ **局部圆＝草图圆**）→ 才调。
    ★ 判据：**视图数 +1**。
    """
    row = {"tag": "★ V3 局部视图（CreateDetailViewAt4）", "ok": False}
    part = None
    doc = None
    try:
        style = _ev(row, "swDetViewStyle_e", "swDetViewSTANDARD", "Style")
        showtype = _ev(row, "swDetCircleShowType_e", "swDetCircleCIRCLE", "Showtype")
        if style is None or showtype is None:
            row["note"] = (
                "★ 前置未成立：官方枚举取值没读到（★ 见 enum_missing）⇒ 不猜、不调"
            )
            return row
        part = _build_part(sw, row)
        if part is None:
            row["note"] = "★ 前置未成立：零件没建成 ⇒ 本格不作判据"
            return row
        doc, view_name, info = _drawing_with_view(sw, part, row)
        row["parent_view"] = info
        if doc is None or not view_name:
            row["note"] = "★ 前置未成立：父视图没建成 ⇒ 本格不作判据"
            return row
        views, _e = _real_views(doc)
        view = next((v for v in views if _vname(v) == view_name), None)
        bbox = _outline(view) if view is not None else None
        row["view_outline_m"] = [round(v, 6) for v in bbox] if bbox else None
        row["activated"] = _activate_view(doc, view_name)
        _clear(doc)
        if not bbox:
            row["note"] = "★ 前置未成立：取不到视图包围盒 ⇒ 画不出局部圆"
            return row
        xmin, ymin, xmax, ymax = bbox[:4]
        cx, cy = (xmin + xmax) / 2.0, (ymin + ymax) / 2.0
        r = 0.2 * min(xmax - xmin, ymax - ymin)
        try:
            _get(
                _get(doc, "SketchManager"),
                "CreateCircle",
                float(cx),
                float(cy),
                0.0,
                float(cx + r),
                float(cy),
                0.0,
            )
            row["detail_circle"] = {
                "center": [round(cx, 6), round(cy, 6)],
                "r_m": round(r, 6),
            }
        except Exception as exc:  # noqa: BLE001
            row["err"] = "CreateCircle 失败：%s: %s" % (
                type(exc).__name__,
                str(exc)[:160],
            )
            return row
        before = _view_count(doc)
        loc_x = xmax + 0.03
        try:
            ret = _get(
                doc,
                "CreateDetailViewAt4",
                float(loc_x),
                float(cy),
                0.0,
                int(style),
                1.0,
                1.0,
                "A",
                int(showtype),
                True,
                True,
                False,
                5,
            )
            row["ret_is_none"] = ret is None
        except Exception as exc:  # noqa: BLE001
            row["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        after = _view_count(doc)
        row.update(
            {
                "views_before": before,
                "views_after": after,
                "view_names": [_vname(v) for v in _real_views(doc)[0]],
                "style": style,
                "showtype": showtype,
                "shape_intensity": 5,
                "unit": SHEET_POS_UNIT_ASSUMPTION,
                "scale": [1, 1],
                "label": "A",
            }
        )
        row["view_delta"] = (
            None if (before is None or after is None) else after - before
        )
        row["ok"] = bool(row["view_delta"] == 1)
        row["verified_by"] = "view_count_delta"
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if part is not None:
            _close(sw, part)
        if doc is not None:
            _close(sw, doc)
    return row


def case_v4_break_view(sw):
    """★ V4 断裂视图：**`IView.InsertBreak3(Orientation, Position1, Position2, Style, ShapeIntensity, BreakSketchBlocks)`**。

    ★★★ 为什么不是 `InsertBreak`：官方页头顶逐字 `Obsolete. Superseded by [[IView::InsertBreak2]]`；
      而 `InsertBreak2` 也废弃（`Superseded by [[IView::InsertBreak3]]`）⇒ ★ 用 **3**（★ 铁律 4）。
    ★ 前置（★ 官方例子 `Insert_Jagged_Cut_Break_Example_VB` 的调用序）：`ActivateView` →
      `SelectByID2(视图名,"DRAWINGVIEW")` → `SelectionManager.GetSelectedObject6(1,-1)` 取出 `IView`。
    ★ 官方 Remarks：Position1/Position2 **相对视图原点**；**Horizontal 时是 Y 值**、
      **Vertical 时是 X 值**（★ 例子用 `Orientation = 2` = `swBreakLineVertical`）。
    ★ 判据：该视图 `GetBreakLineCount(out_i4())` **+1** 且 `IsBroken` 为真（★ 副作用：视图数**不该变**）。
    ★★ 注意：官方签名是 `GetBreakLineCount( out System.int Size )` **带 out 参数**
    ⇒ ★ **必须传 `out_i4()`**；★ 零参调它会 `类型不匹配` 而被 `except` 吃成 `None`（静默降级）。
    ★ 另用零参 `GetBreakLines()` 的数组长度做**交叉核**（两条独立读数）。
    """
    row = {"tag": "★ V4 断裂视图（InsertBreak3）", "ok": False}
    part = None
    doc = None
    try:
        orientation = _ev(
            row, "swBreakLineOrientation_e", "swBreakLineVertical", "Orientation"
        )
        style = _ev(row, "swBreakLineStyle_e", "swBreakLine_Jagged", "Style")
        if orientation is None or style is None:
            row["note"] = "★ 前置未成立：官方枚举取值没读到 ⇒ 不猜、不调"
            return row
        part = _build_part(sw, row)
        if part is None:
            row["note"] = "★ 前置未成立：零件没建成 ⇒ 本格不作判据"
            return row
        doc, view_name, info = _drawing_with_view(sw, part, row)
        row["parent_view"] = info
        if doc is None or not view_name:
            row["note"] = "★ 前置未成立：父视图没建成 ⇒ 本格不作判据"
            return row
        row["activated"] = _activate_view(doc, view_name)
        _ok, counts = _select_view(doc, view_name, mark=0)
        row["sel_by_mark_before_call"] = counts
        view = None
        try:
            view = _get(_get(doc, "SelectionManager"), "GetSelectedObject6", 1, -1)
        except Exception as exc:  # noqa: BLE001
            row["err"] = "GetSelectedObject6 失败：%s: %s" % (
                type(exc).__name__,
                str(exc)[:140],
            )
        row["view_from_selection"] = view is not None
        row["preconditions_held"] = bool(view is not None)
        if view is None:
            row["note"] = (
                "★ 前置未成立：按名选中视图后 `GetSelectedObject6(1,-1)` 取不到 IView"
                " ⇒ 本格不作判据（★ 例子给的正是这条调用序）"
            )
            return row
        bbox = _outline(view)
        row["view_outline_m"] = [round(v, 6) for v in bbox] if bbox else None
        dx = 0.25 * (bbox[2] - bbox[0]) if bbox else 0.01
        before_bl = _out_count_of(view, "GetBreakLineCount")
        before_bl2 = _list_len_of(view, "GetBreakLines")
        before_is_broken = _bool_of(view, "IsBroken")
        before_views = _view_count(doc)
        try:
            ret = _get(
                view,
                "InsertBreak3",
                int(orientation),
                float(-dx),
                float(dx),
                int(style),
                2,
                True,
            )
            row["ret_is_none"] = ret is None
        except Exception as exc:  # noqa: BLE001
            row["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        after_bl = _out_count_of(view, "GetBreakLineCount")
        after_bl2 = _list_len_of(view, "GetBreakLines")
        row.update(
            {
                "orientation": orientation,
                "style": style,
                "shape_intensity": 2,
                "break_sketch_blocks": True,
                "positions_relative_to_view_origin": [-dx, dx],
                "breaklines": [before_bl, after_bl],
                "breaklines_crosscheck": [before_bl2, after_bl2],
                "is_broken": [before_is_broken, _bool_of(view, "IsBroken")],
                "views_before": before_views,
                "views_after": _view_count(doc),
                "note_positions": (
                    "★ 官方 Remarks：Position1/2 **相对视图原点**；"
                    "Vertical ⇒ 它们是 **X 值**（★ 例子里就是这个形态）"
                ),
            }
        )
        gained = (
            None if (before_bl is None or after_bl is None) else after_bl - before_bl
        )
        gained2 = (
            None
            if (before_bl2 is None or after_bl2 is None)
            else after_bl2 - before_bl2
        )
        row["breakline_delta"] = gained
        row["breakline_delta_crosscheck"] = gained2
        # ★ 判据：**主读数**（带 out 的 `GetBreakLineCount`）增量 ≥1；
        # ★ 交叉核（零参 `GetBreakLines()` 长度）**只作对照**，量不到不判失败（★ 不猜）
        # 。
        row["ok"] = bool(row["preconditions_held"] and (gained or 0) >= 1)
        row["verified_by"] = (
            "GetBreakLineCount_delta（★ 传 out_i4，官方带 out 参数）"
            " + 交叉核 GetBreakLines() 数组长度 + IsBroken"
        )
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if part is not None:
            _close(sw, part)
        if doc is not None:
            _close(sw, doc)
    return row


#: 墓碑（2026-10-03 接手轮）：这里原有一个 `_count_of(obj, member)` ——
#:   它从没被调用过（`tests/test_no_uncalled_helpers.py` 点名），
#:   而它的活儿已由下面的 `_out_count_of`（带 out 参数的那种）与 `_list_len_of` 分担
#:   ⇒ 删掉；留墓碑而不是静默消失，免得下一个人以为「本来就没有」。
def _out_count_of(obj, member):
    """★ 读**带 `out` 参数**的计数成员；读不到回 `None`（★ 判据降级，不猜 0）。

    ★ 官方形态逐字：`System.int GetBreakLineCount( out System.int Size )`
    ⇒ ★ **必须传 `sw_connect.out_i4()` 的 by-ref 包装**（与 known-facts 47 同族）。
    ★ 零参调它会 `类型不匹配`，`except` 一吃就成 `None` ⇒ **静默降级**（这是 2026-10-03 踩到的坑）。
    """
    try:
        return int(_get(obj, member, C.out_i4(0)) or 0)
    except Exception:  # noqa: BLE001
        return None


def _list_len_of(obj, member):
    """★ 读一个**零参返回数组**的成员并取长度；读不到回 `None`。

    ★ 用途：给带 `out` 参数的计数成员做**交叉核** —— 两条**独立**读数一致才算稳。
    """
    try:
        v = _get(obj, member)
        return len(v) if v is not None else None
    except Exception:  # noqa: BLE001
        return None


def _bool_of(obj, member):
    """★ 读一个零参布尔成员；读不到回 `None`。"""
    try:
        v = _get(obj, member)
        return None if v is None else bool(v)
    except Exception:  # noqa: BLE001
        return None


def case_v5_auxiliary_view(sw):
    """★ V5 辅助视图：`IDrawingDoc.CreateAuxiliaryViewAt2(X,Y,Z,NotAligned,Label,Showarrow,Flip)`。

    ★ 前置（官方摘要逐字）："Creates an auxiliary view based on a **selected edge in a drawing
      view**" —— ★ 该页**没有 Remarks** ⇒ ★ 本格把"视图里选一条边"当**显式前置**，
      ★ 用 `IView.GetOutline` 推候选点**逐个试按点选**，★ 回读计数决定前置是否成立。
    ★ 判据：**视图数 +1**（★ 前置成立才算）。
    """
    row = {"tag": "★ V5 辅助视图（CreateAuxiliaryViewAt2）", "ok": False}
    part = None
    doc = None
    try:
        part = _build_part(sw, row)
        if part is None:
            row["note"] = "★ 前置未成立：零件没建成 ⇒ 本格不作判据"
            return row
        doc, view_name, info = _drawing_with_view(sw, part, row)
        row["parent_view"] = info
        if doc is None or not view_name:
            row["note"] = "★ 前置未成立：父视图没建成 ⇒ 本格不作判据"
            return row
        row["activated"] = _activate_view(doc, view_name)
        _clear(doc)
        views, _e = _real_views(doc)
        view = next((v for v in views if _vname(v) == view_name), None)
        bbox = _outline(view) if view is not None else None
        row["view_outline_m"] = [round(v, 6) for v in bbox] if bbox else None
        if not bbox:
            row["note"] = "★ 前置未成立：取不到视图包围盒 ⇒ 无法推候选拾取点"
            return row
        hit, counts, errs = _pick_any(doc, "EDGE", _inside_points(bbox), mark=0)
        row.update(
            {"edge_pick": hit, "sel_by_mark_before_call": counts, "pick_errs": errs}
        )
        row["preconditions_held"] = bool(hit is not None)
        if hit is None:
            row["note"] = (
                "★ 前置未成立：候选点都没选到**视图里的边** ⇒ 本格**不能**当"
                "「辅助视图不成」的证据；★ 要解决的是「怎么在视图里选中一条边」"
            )
            return row
        before = _view_count(doc)
        loc_x = bbox[2] + 0.03
        try:
            ret = _get(
                doc,
                "CreateAuxiliaryViewAt2",
                float(loc_x),
                float((bbox[1] + bbox[3]) / 2.0),
                0.0,
                False,
                "A",
                True,
                False,
            )
            row["ret_is_none"] = ret is None
        except Exception as exc:  # noqa: BLE001
            row["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        after = _view_count(doc)
        row.update(
            {
                "views_before": before,
                "views_after": after,
                "view_names": [_vname(v) for v in _real_views(doc)[0]],
                "unit": SHEET_POS_UNIT_ASSUMPTION,
                "not_aligned": False,
                "label": "A",
                "show_arrow": True,
                "flip": False,
            }
        )
        row["view_delta"] = (
            None if (before is None or after is None) else after - before
        )
        row["ok"] = bool(row["preconditions_held"] and row["view_delta"] == 1)
        row["verified_by"] = "view_count_delta（★ 前置成立才算）"
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if part is not None:
            _close(sw, part)
        if doc is not None:
            _close(sw, doc)
    return row


# ── 标注族 ───────────────────────────────────────────────────────────
def case_a1_setup_sheet(sw):
    """★ A1 图纸格式/模板：**`IDrawingDoc.SetupSheet6(…)`**（★ 官方 **17 参**、未废弃）。

    ★★★ 为什么不是 `SetupSheet5`：官方页逐字 `Obsolete. Superseded by [[IDrawingDoc::SetupSheet6]]`。
    ★ 官方 Remarks 两条：① 调完要 `IModelDoc2::ForceRebuild3`；
      ② **把 `TemplateName` 指到另一个文件 ⇒ SOLIDWORKS 会更新图纸格式**。
    ★★ 本格**只暴露** 17 参里的前 11 个（Name…RemoveModifiedNotes）；
      后 6 个是**分区（zone）**参数（LeftMargin/RightMargin/TopMargin/BottomMargin/Row/Col），
      ★ 官方对那 4 个 margin **没给单位**，★ 而官方例子里 `0.5` 与同一次调用的米制宽高
      （`0.2794`）**不自洽** ⇒ ★ 本格传 `0.0 / 0 / 0`（＝不分区的中性值）并**如实标注**。
    ★ 判据：`SetupSheet6` **回真** 且 **回读图纸读数真的变了**（★ 规则 6：不静默成功）。
    """
    row = {
        "tag": "★ A1 图纸格式（SetupSheet6）",
        "ok": False,
        "zone_params": "★ 传 0.0/0/0：官方那 4 个 margin **未给单位**，"
        "且例子里的 0.5 与米制宽高 0.2794 不自洽 ⇒ 不猜（铁律 5）",
    }
    doc = None
    try:
        paper = _ev(row, "swDwgPaperSizes_e", "swDwgPapersUserDefined", "PaperSize")
        tmpl_in = _ev(row, "swDwgTemplates_e", "swDwgTemplateCustom", "TemplateIn")
        if paper is None or tmpl_in is None:
            row["note"] = "★ 前置未成立：官方枚举取值没读到 ⇒ 不猜、不调"
            return row
        sheet_format = _sheet_format_template()
        row["sheet_format_template"] = sheet_format
        if not sheet_format:
            row["note"] = (
                "★ 前置未成立：找不到 `.slddrt` 模板（★ 官方 Remarks 说模板在 "
                "install_dir\\lang\\<language>）⇒ 本格不作判据"
            )
            return row
        doc = _new_drawing(sw, row)
        if doc is None:
            row["note"] = "★ 前置未成立：新建工程图失败 ⇒ 本格不作判据"
            return row
        try:
            sheet_name = DQ.current_sheet_name(doc)
        except Exception as exc:  # noqa: BLE001
            row["err"] = "读当前图纸名失败：%s: %s" % (
                type(exc).__name__,
                str(exc)[:140],
            )
            return row
        before = DQ.current_sheet_info(doc)
        ret = _get(
            doc,
            "SetupSheet6",
            str(sheet_name),
            int(paper),
            int(tmpl_in),
            1.0,
            2.0,
            True,
            str(sheet_format),
            0.2794,
            0.2159,
            "",
            False,
            0.0,
            0.0,
            0.0,
            0.0,
            0,
            0,
        )
        #: ★ 官方 Remarks 逐字：After calling this method, call IModelDoc2::ForceRebuild
        #: 3
        try:
            _get(doc, "ForceRebuild3", True)
            row["force_rebuild"] = True
        except Exception as exc:  # noqa: BLE001
            row["force_rebuild"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        after = DQ.current_sheet_info(doc)
        changed = {
            k: [before.get(k), after.get(k)]
            for k in sorted(set(before) | set(after))
            if before.get(k) != after.get(k)
        }
        row.update(
            {
                "setup_returned": None if ret is None else bool(ret),
                "sheet_name": sheet_name,
                "sheet_format_template_name": str(sheet_format),
                "asked_scale": [1.0, 2.0],
                "paper_size_code": paper,
                "template_in": tmpl_in,
                "sheet_before": before,
                "sheet_after": after,
                "readback_changed": changed,
            }
        )
        row["ok"] = bool(ret) and bool(changed)
        row["verified_by"] = (
            "SetupSheet6_returns_true + current_sheet_info_readback_changed"
        )
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            _close(sw, doc)
    return row


def case_a2_surface_finish(sw, leader="straight"):
    """★ A2 表面粗糙度：`IModelDocExtension.InsertSurfaceFinishSymbol3(…)`（★ 官方 **14 参**）。

    ★ 官方摘要逐字："Creates a surface-finish symbol **based on the last selection**"。
    ★★ 官方 Remarks 逐字："uses the location parameters for this method **only if** the surface
      finish symbol has a leader **leaderType != swNO_LEADER**"
      ⇒ ★ 本探针把它当**单变量**：`straight`（`swSTRAIGHT = 1`，带引线）vs `none`（`swNO_LEADER = 0`）。
    ★ 官方例子 `Get_Annotations_Array_Example_VB` 里那一次调用的**实参序**逐字是：
      `swSFBasic, swSTRAIGHT, 0.01, 0.01, 0.01, swSFCircular, swDOT_ARROWHEAD, "", "", "", "", "", "", ""`
      ⇒ ★ 本格照它传：7 个字符串参数**全空串**（★ 例子就是空串，★ 不是我们编的）。
    ★ 判据：`GetSFSymbolCount` **+1**（★ 视图链求和）。
    """
    row = {
        "tag": "★ A2 表面粗糙度（InsertSurfaceFinishSymbol3 · leader=%s）" % leader,
        "ok": False,
    }
    part = None
    doc = None
    try:
        sym = _ev(row, "swSFSymType_e", "swSFBasic", "SymType")
        lay = _ev(row, "swSFLaySym_e", "swSFCircular", "LaySymbol")
        arrow = _ev(row, "swArrowStyle_e", "swDOT_ARROWHEAD", "ArrowType")
        lead = _ev(
            row,
            "swLeaderStyle_e",
            "swSTRAIGHT" if leader == "straight" else "swNO_LEADER",
            "LeaderType",
        )
        if None in (sym, lay, arrow, lead):
            row["note"] = "★ 前置未成立：官方枚举取值没读到 ⇒ 不猜、不调"
            return row
        part = _build_part(sw, row)
        if part is None:
            row["note"] = "★ 前置未成立：零件没建成 ⇒ 本格不作判据"
            return row
        doc, view_name, info = _drawing_with_view(sw, part, row)
        row["parent_view"] = info
        if doc is None or not view_name:
            row["note"] = "★ 前置未成立：父视图没建成 ⇒ 本格不作判据"
            return row
        _activate_view(doc, view_name)
        _clear(doc)  #: ★ 不选任何东西（★ 单变量）
        row["sel_by_mark_before_call"] = _sel_counts(doc)
        before = _anno_state(doc)
        loc = {"straight": (0.01, 0.01, 0.01), "none": (0.0, 0.0, 0.0)}[leader]
        try:
            ret = _get(
                _get(doc, "Extension"),
                "InsertSurfaceFinishSymbol3",
                int(sym),
                int(lead),
                float(loc[0]),
                float(loc[1]),
                float(loc[2]),
                int(lay),
                int(arrow),
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            )
            row["ret_is_none"] = ret is None
        except Exception as exc:  # noqa: BLE001
            row["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        after = _anno_state(doc)
        row.update(
            {
                "before": before,
                "after": after,
                "sym_type": sym,
                "leader_type": lead,
                "lay_symbol": lay,
                "arrow_type": arrow,
                "loc_m": list(loc),
                "strings": "★ 7 个字符串参数全空串（★ 照官方例子逐字）",
            }
        )
        row["sf_delta"] = _delta(before, after, "sf")
        row["ok"] = bool((row["sf_delta"] or 0) >= 1)
        row["verified_by"] = "GetSFSymbolCount_delta"
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if part is not None:
            _close(sw, part)
        if doc is not None:
            _close(sw, doc)
    return row


def case_a3_datum_tag(sw, select_edge=False):
    """★ A3 基准符号：`IModelDoc2.InsertDatumTag2()`（★ 官方**零参**）。

    ★ 官方摘要逐字："Inserts a datum tag symbol at a **selected location**"。
    ★★ 单变量：`select_edge=False` 是**对照格** —— ★ 本仓已有真机反例
      （`output/drawing-datum-tag-evidence.json`：不先选时**回 `None`、计数 0→0**）
      ⇒ ★ 本格就是来**复现并确认**那条前置的，★ **不把它当成"能力不成"**。
    ★ 判据：`GetDatumTagCount` **+1**。
    """
    row = {
        "tag": "★ A3 基准符号（InsertDatumTag2 · select_edge=%s）" % select_edge,
        "ok": False,
    }
    part = None
    doc = None
    try:
        part = _build_part(sw, row)
        if part is None:
            row["note"] = "★ 前置未成立：零件没建成 ⇒ 本格不作判据"
            return row
        doc, view_name, info = _drawing_with_view(sw, part, row)
        row["parent_view"] = info
        if doc is None or not view_name:
            row["note"] = "★ 前置未成立：父视图没建成 ⇒ 本格不作判据"
            return row
        _activate_view(doc, view_name)
        _clear(doc)
        hit = None
        if select_edge:
            views, _e = _real_views(doc)
            view = next((v for v in views if _vname(v) == view_name), None)
            bbox = _outline(view) if view is not None else None
            row["view_outline_m"] = [round(v, 6) for v in bbox] if bbox else None
            if bbox:
                hit, _c, errs = _pick_any(doc, "EDGE", _inside_points(bbox), mark=0)
                row["edge_pick"] = hit
                row["pick_errs"] = errs
        counts = _sel_counts(doc)
        row["sel_by_mark_before_call"] = counts
        row["preconditions_held"] = bool(sum(v for v in counts.values() if v > 0) > 0)
        before = _anno_state(doc)
        try:
            tag = _get(doc, "InsertDatumTag2")
            row["ret_is_none"] = tag is None
        except Exception as exc:  # noqa: BLE001
            row["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        after = _anno_state(doc)
        row.update({"before": before, "after": after, "edge_pick": hit})
        row["datum_delta"] = _delta(before, after, "datum")
        row["ok"] = bool((row["datum_delta"] or 0) >= 1)
        if not row["preconditions_held"]:
            row["note"] = (
                "★ 前置未成立（调用前选区为空）⇒ 本格是对照格："
                "★ 它**只说明「没选中时不建」**，★ 不能当「基准符号不成」的证据"
            )
        row["verified_by"] = "GetDatumTagCount_delta"
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if part is not None:
            _close(sw, part)
        if doc is not None:
            _close(sw, doc)
    return row


def case_a4_note(sw, text="PROBE-NOTE", select_edge=False):
    """★ A4 注释文字：`IModelDoc2.InsertNote(Text)`（★ 官方 **1 参**）。

    ★ 官方 Remarks 逐字："The leader attachment points for the new note come from the selections
      made before calling this method. … If there are no selections, the note: does not have a
      leader · is free standing · **is at the origin of the model or drawing**"。
    ★ 单变量：`select_edge=False`（不选 ⇒ 按 Remarks 它是**无引线、自由放置、在原点**）
      vs `True`（★ 照官方例子 `Insert_a_Note_Example_VB`：先选一条 `EDGE` 再插）。
    ★ 判据：`GetNoteCount` **+1**。
    """
    row = {
        "tag": "★ A4 注释（InsertNote · select_edge=%s · text=%r）"
        % (select_edge, text),
        "ok": False,
    }
    part = None
    doc = None
    try:
        part = _build_part(sw, row)
        if part is None:
            row["note"] = "★ 前置未成立：零件没建成 ⇒ 本格不作判据"
            return row
        doc, view_name, info = _drawing_with_view(sw, part, row)
        row["parent_view"] = info
        if doc is None or not view_name:
            row["note"] = "★ 前置未成立：父视图没建成 ⇒ 本格不作判据"
            return row
        _activate_view(doc, view_name)
        _clear(doc)
        hit = None
        if select_edge:
            views, _e = _real_views(doc)
            view = next((v for v in views if _vname(v) == view_name), None)
            bbox = _outline(view) if view is not None else None
            if bbox:
                hit, _c, errs = _pick_any(doc, "EDGE", _inside_points(bbox), mark=0)
                row["pick_errs"] = errs
        row["edge_pick"] = hit
        row["sel_by_mark_before_call"] = _sel_counts(doc)
        before = _anno_state(doc)
        try:
            n = _get(doc, "InsertNote", str(text))
            row["ret_is_none"] = n is None
        except Exception as exc:  # noqa: BLE001
            row["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        after = _anno_state(doc)
        row.update({"before": before, "after": after})
        row["note_delta"] = _delta(before, after, "note")
        row["ok"] = bool((row["note_delta"] or 0) >= 1)
        row["verified_by"] = "GetNoteCount_delta"
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if part is not None:
            _close(sw, part)
        if doc is not None:
            _close(sw, doc)
    return row


def case_a5_auto_balloon(sw):
    """★ A5 气泡序号：`IDrawingDoc.AutoBalloon5(AutoBalloonOptions)`（★ 官方 **1 参**）。

    ★★ 官方 `AutoBalloon5` / `CreateAutoBalloonOptions` 的 Remarks 给的是**四步调用序**：
      ① 选中一个或多个**视图或图纸** ② 调 `CreateAutoBalloonOptions()` 建 options
      ③ 设 options 的属性 ④ 把 options 传给 `AutoBalloon5`。
    ★ 官方例子的 **precondition 逐字**是 "Open a drawing with a **bill of materials (BOM) table**"
      ⇒ ★ 本格**先回读有没有 BOM 表**（`IView.GetBomTable()`），★ 没有就**如实标注前置未成立**
      （★ 那不算"气泡不成"）。
    ★ 判据：`GetNoteCount` **+1**（★ 气泡就是 note —— 官方 `AutoBalloon5` 的 Returns 是 "Array of INotes"）。
    """
    row = {"tag": "★ A5 气泡序号（AutoBalloon5）", "ok": False}
    part = None
    doc = None
    try:
        part = _build_part(sw, row)
        if part is None:
            row["note"] = "★ 前置未成立：零件没建成 ⇒ 本格不作判据"
            return row
        doc, view_name, info = _drawing_with_view(sw, part, row)
        row["parent_view"] = info
        if doc is None or not view_name:
            row["note"] = "★ 前置未成立：父视图没建成 ⇒ 本格不作判据"
            return row
        row["activated"] = _activate_view(doc, view_name)
        _ok, counts = _select_view(doc, view_name, mark=0)
        row["sel_by_mark_before_call"] = counts
        views, _e = _real_views(doc)
        view = next((v for v in views if _vname(v) == view_name), None)
        bom = None
        try:
            bom = _get(view, "GetBomTable") if view is not None else None
        except Exception as exc:  # noqa: BLE001
            row["bom_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
        row["bom_table_present"] = bom is not None
        row["preconditions_held"] = bool(bom is not None)
        before = _anno_state(doc)
        try:
            opts = _get(doc, "CreateAutoBalloonOptions")
            row["options_is_none"] = opts is None
            #: ★ 属性名与取值**逐字取自官方例子** `Add_Autoballoon_to_Face_Example_VB`；
            #:   ★ 枚举值现场读官方页；★ 读不到就**跳过该属性**并记下来（★ 不猜）。
            prop_specs = (
                ("Layout", "swBalloonLayoutType_e", "swDetailingBalloonLayout_Square"),
                ("ReverseDirection", None, False),
                ("IgnoreMultiple", None, True),
                ("InsertMagneticLine", None, True),
                ("LeaderAttachmentToFaces", None, True),
                ("Style", "swBalloonStyle_e", "swBS_Circular"),
                ("Size", "swBalloonFit_e", "swBF_5Chars"),
                (
                    "UpperTextContent",
                    "swBalloonTextContent_e",
                    "swBalloonTextItemNumber",
                ),
                ("Layername", None, "-None-"),
                ("ItemNumberStart", None, 1),
                ("ItemNumberIncrement", None, 1),
                (
                    "ItemOrder",
                    "swBalloonItemNumbersOrder_e",
                    "swBalloonItemNumbers_DoNotChangeItemNumbers",
                ),
                ("EditBalloons", None, True),
                (
                    "EditBalloonOption",
                    "swEditBalloonOption_e",
                    "swEditBalloonOption_Resequence",
                ),
            )
            set_ok, set_err = [], []
            for prop, enum_name, value in prop_specs:
                if opts is None:
                    break
                want = value
                if enum_name:
                    want = _ev(row, enum_name, str(value), prop)
                    if want is None:
                        continue
                try:
                    C.set_com_member(opts, prop, want)
                    set_ok.append(prop)
                except Exception as exc:  # noqa: BLE001
                    set_err.append(
                        "%s ⇒ %s: %s" % (prop, type(exc).__name__, str(exc)[:90])
                    )
            row["options_set_ok"] = set_ok
            row["options_set_err"] = set_err
            ret = _get(doc, "AutoBalloon5", opts) if opts is not None else None
            row["ret_none"] = ret is None
            try:
                row["returned_count"] = len(list(ret)) if ret is not None else 0
            except TypeError:
                row["returned_count"] = None
        except Exception as exc:  # noqa: BLE001
            row["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        after = _anno_state(doc)
        row.update({"before": before, "after": after})
        row["note_delta"] = _delta(before, after, "note")
        row["ok"] = bool(row["preconditions_held"] and (row["note_delta"] or 0) >= 1)
        if not row["preconditions_held"]:
            row["note"] = (
                "★ 前置未成立：这张图**没有 BOM 表**（官方例子的 precondition 就是这个）"
                " ⇒ 本格**不能**当「气泡不成」的证据"
            )
        row["verified_by"] = "GetNoteCount_delta（★ 前置成立才算）"
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if part is not None:
            _close(sw, part)
        if doc is not None:
            _close(sw, doc)
    return row


def case_a6_hole_table(sw):
    """★ A6 孔表：**`IView.InsertHoleTable3(…)`**（★ 官方 **9 参**、未废弃）。

    ★★★ 为什么不是 `InsertHoleTable2`：官方页逐字 `Obsolete. Superseded by [[IView::InsertHoleTable3]]`。
    ★★ 官方 Remarks 的 **mark 表（逐字）**：基准原点**顶点 mark 1** · 孔**边与面 mark 2** ·
      基准原点 X 向参考 mark 4 · Y 向参考 mark 8；★ `Template` 用 `.sldholtbt`
      （例：`install_dir\\lang\\English\\standard hole table--letters.sldholtbt`，配 `StartValue` = A..Z）。
    ★ 单变量：本格**只**选"顶点 mark 1 + 面 mark 2"（**最小前置** —— 官方对 X/Y 向参考用的是
      mark 4/8，★ 本格先不选它们，看最小前置够不够）。
    ★ 官方例子的实参序逐字：`(False, x, y, 1, "A", <模板>, 1, 1, Nothing)`
      ⇒ ★ `ManualTags` 传**空 Dispatch**（★ 事实 12；★ 例子里是 `Nothing`）。
    ★ 判据：`GetTableAnnotationCount` **+1**（★ 前置成立才算）。
    """
    row = {
        "tag": "★ A6 孔表（InsertHoleTable3）",
        "ok": False,
        "official_marks": "顶点=1 · 孔边与面=2 · 原点 X 向参考=4 · Y 向参考=8（官方 Remarks 逐字）",
    }
    part = None
    doc = None
    try:
        anchor = _ev(
            row,
            "swBOMConfigurationAnchorType_e",
            "swBOMConfigurationAnchor_TopLeft",
            "AnchorType",
        )
        if anchor is None:
            row["note"] = "★ 前置未成立：官方枚举取值没读到 ⇒ 不猜、不调"
            return row
        template = _hole_table_template()
        row["template"] = template
        if not template:
            row["note"] = (
                "★ 前置未成立：找不到 `.sldholtbt` 模板（★ 官方 Remarks 说模板在 "
                "install_dir\\lang\\<language>）⇒ 本格不作判据"
            )
            return row
        part = _build_part(sw, row)
        if part is None:
            row["note"] = "★ 前置未成立：零件没建成 ⇒ 本格不作判据"
            return row
        doc, view_name, info = _drawing_with_view(sw, part, row)
        row["parent_view"] = info
        if doc is None or not view_name:
            row["note"] = "★ 前置未成立：父视图没建成 ⇒ 本格不作判据"
            return row
        _activate_view(doc, view_name)
        _clear(doc)
        views, _e = _real_views(doc)
        view = next((v for v in views if _vname(v) == view_name), None)
        bbox = _outline(view) if view is not None else None
        row["view_outline_m"] = [round(v, 6) for v in bbox] if bbox else None
        if not bbox:
            row["note"] = "★ 前置未成立：取不到视图包围盒 ⇒ 无法推候选拾取点"
            return row
        pts = _inside_points(bbox)
        v_hit, _c1, e1 = _pick_any(doc, "VERTEX", pts, mark=1)
        f_hit, counts, e2 = _pick_any(doc, "FACE", pts, mark=2, append=True)
        row.update(
            {
                "vertex_pick": v_hit,
                "face_pick": f_hit,
                "sel_by_mark_before_call": counts,
                "pick_errs": {"vertex": e1, "face": e2},
            }
        )
        row["preconditions_held"] = bool(
            v_hit is not None
            and f_hit is not None
            and counts.get("1", 0) >= 1
            and counts.get("2", 0) >= 1
        )
        if not row["preconditions_held"]:
            row["note"] = (
                "★ 前置未成立（官方 mark 表要求的 1/2 没同时选上）⇒ 本格**不能**当"
                "「孔表不成」的证据；★ 下一步是解决「怎么在视图里按 mark 选到"
                "基准原点顶点与孔面」"
            )
            return row
        before = _anno_state(doc)
        try:
            tbl = _get(
                view,
                "InsertHoleTable3",
                False,
                0.07,
                0.175,
                int(anchor),
                "A",
                str(template),
                1,
                1,
                C.create_empty_dispatch_variant(),
            )
            row["ret_is_none"] = tbl is None
        except Exception as exc:  # noqa: BLE001
            row["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        after = _anno_state(doc)
        row.update(
            {
                "before": before,
                "after": after,
                "anchor_type": anchor,
                "start_value": "A",
                "tag_order": 1,
                "tag_type": 1,
                "manual_tags": "★ 传空 Dispatch（★ 事实 12；★ 官方例子里是 Nothing）",
            }
        )
        row["table_delta"] = _delta(before, after, "table")
        row["ok"] = bool(row["preconditions_held"] and (row["table_delta"] or 0) >= 1)
        row["verified_by"] = "GetTableAnnotationCount_delta（★ 前置成立才算）"
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if part is not None:
            _close(sw, part)
        if doc is not None:
            _close(sw, doc)
    return row


def case_a7_revision_table(sw, second=False):
    """★ A7 修订表：`ISheet.InsertRevisionTable2(UseAnchorPoint, X, Y, AnchorType, TableTemplate, Shape, AutoUpdateZoomCells)`（★ **7 参**）。

    ★ 官方 Remarks 逐字：模板默认在 `install_dir\\lang\\<language>`、扩展名 **`.sldrevtbt`**，
      且**模板与表必须同型**（例：`…\\lang\\English\\standard revision block.sldrevtbt`）。
    ★★ 官方 **Returns** 逐字："Revision table … **or null if a revision table already exists**"
      ⇒ ★ 本探针把「**插第二次**」当**期望为 `null`** 的一格（`second=True`）—— ★ 那是**契约检查**，不是碰运气。
    ★ 判据：① 第一次：非 `None` **且** `ISheet.RevisionTable` 回读非 `None`；
      ② 第二次：**必须回 `None`**（★ 官方就是这么写的）。
    """
    row = {
        "tag": "★ A7 修订表（InsertRevisionTable2 · second=%s）" % second,
        "ok": False,
    }
    doc = None
    try:
        anchor = _ev(
            row,
            "swBOMConfigurationAnchorType_e",
            "swBOMConfigurationAnchor_TopLeft",
            "AnchorType",
        )
        shape = _ev(
            row, "swRevisionTableSymbolShape_e", "swRevisionTable_CircleSymbol", "Shape"
        )
        if anchor is None or shape is None:
            row["note"] = "★ 前置未成立：官方枚举取值没读到 ⇒ 不猜、不调"
            return row
        template = _revision_table_template()
        row["template"] = template
        if not template:
            row["note"] = (
                "★ 前置未成立：找不到 `.sldrevtbt` 模板（★ 官方 Remarks 说模板在 "
                "install_dir\\lang\\<language>）⇒ 本格不作判据"
            )
            return row
        doc = _new_drawing(sw, row)
        if doc is None:
            row["note"] = "★ 前置未成立：新建工程图失败 ⇒ 本格不作判据"
            return row
        sheet = _get(doc, "GetCurrentSheet")
        row["sheet_is_none"] = sheet is None
        if sheet is None:
            row["note"] = "★ 前置未成立：取不到当前图纸（ISheet）"
            return row
        before = _anno_state(doc)
        #: ★ 官方例子的实参序逐字：`(True, 0#, 0#, swBOMConfigurationAnchor_TopLeft, <模
        #: 板>, swRevisionTable_CircleSymbol, True)`
        try:
            ret1 = _get(
                sheet,
                "InsertRevisionTable2",
                True,
                0.0,
                0.0,
                int(anchor),
                str(template),
                int(shape),
                True,
            )
            row["first_ret_is_none"] = ret1 is None
        except Exception as exc:  # noqa: BLE001
            row["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        try:
            row["revision_table_property_is_none"] = (
                _get(sheet, "RevisionTable") is None
            )
        except Exception as exc:  # noqa: BLE001
            row["revision_table_property_err"] = "%s: %s" % (
                type(exc).__name__,
                str(exc)[:140],
            )
        after = _anno_state(doc)
        row.update(
            {
                "before": before,
                "after": after,
                "anchor_type": anchor,
                "shape": shape,
                "use_anchor_point": True,
                "auto_update_zoom_cells": True,
            }
        )
        row["table_delta"] = _delta(before, after, "table")
        if not second:
            row["ok"] = bool(
                not row.get("first_ret_is_none", True)
                and row.get("revision_table_property_is_none") is False
            )
            row["verified_by"] = "return_not_none + ISheet.RevisionTable_readback"
            return row
        #: ★ 第二格：★ 官方 Returns 明说"已经有了就回 null" ⇒ 这里**期望回 None**
        try:
            ret2 = _get(
                sheet,
                "InsertRevisionTable2",
                True,
                0.0,
                0.0,
                int(anchor),
                str(template),
                int(shape),
                True,
            )
            row["second_ret_is_none"] = ret2 is None
        except Exception as exc:  # noqa: BLE001
            row["second_call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        row["ok"] = bool(row.get("second_ret_is_none") is True)
        row["verified_by"] = (
            "★ 官方 Returns 逐字：已有修订表时回 null ⇒ 本格期望 second_ret_is_none"
        )
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            _close(sw, doc)
    return row


def case_a8_center_mark(sw, select_edge=False):
    """★ A8 中心符号线：`IDrawingDoc.InsertCenterMark3(Style, Propagate, Slot)`（★ 官方 **3 参**）。

    ⚠ ★★ **官方那一页没有写调用前置**（Remarks 只说"要自动插多个请用
      `IView::AutoInsertCenterMarks`"）⇒ ★ 本探针**不假装知道**，
      ★ 用「不选 / 先在视图里选一条圆边」**两格如实测**（★ 铁律 5：查不到就说查不到）。
    ★ 判据：`GetCenterMarkCount2` **+1**。
    """
    row = {
        "tag": "★ A8 中心符号线（InsertCenterMark3 · select_edge=%s）" % select_edge,
        "ok": False,
    }
    part = None
    doc = None
    try:
        style = _ev(row, "swCenterMarkStyle_e", "swCenterMark_Single", "Style")
        if style is None:
            row["note"] = "★ 前置未成立：官方枚举取值没读到 ⇒ 不猜、不调"
            return row
        part = _build_part(sw, row)
        if part is None:
            row["note"] = "★ 前置未成立：零件没建成 ⇒ 本格不作判据"
            return row
        doc, view_name, info = _drawing_with_view(sw, part, row)
        row["parent_view"] = info
        if doc is None or not view_name:
            row["note"] = "★ 前置未成立：父视图没建成 ⇒ 本格不作判据"
            return row
        _activate_view(doc, view_name)
        _clear(doc)
        hit = None
        if select_edge:
            views, _e = _real_views(doc)
            view = next((v for v in views if _vname(v) == view_name), None)
            bbox = _outline(view) if view is not None else None
            row["view_outline_m"] = [round(v, 6) for v in bbox] if bbox else None
            if bbox:
                hit, _c, errs = _pick_any(doc, "EDGE", _inside_points(bbox), mark=0)
                row["pick_errs"] = errs
        row["edge_pick"] = hit
        row["sel_by_mark_before_call"] = _sel_counts(doc)
        row["preconditions_held"] = bool(
            sum(v for v in row["sel_by_mark_before_call"].values() if v > 0) > 0
        )
        before = _anno_state(doc)
        try:
            cm = _get(doc, "InsertCenterMark3", int(style), True, False)
            row["ret_is_none"] = cm is None
        except Exception as exc:  # noqa: BLE001
            row["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        after = _anno_state(doc)
        row.update(
            {
                "before": before,
                "after": after,
                "style": style,
                "propagate": True,
                "slot": False,
                "official_precondition": "★ 官方页**未写**前置（Remarks 只指向 AutoInsertCenterMarks）"
                " ⇒ 本格是**如实测**，不是复核已知前置",
            }
        )
        row["center_delta"] = _delta(before, after, "center")
        row["ok"] = bool((row["center_delta"] or 0) >= 1)
        row["verified_by"] = "GetCenterMarkCount2_delta"
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if part is not None:
            _close(sw, part)
        if doc is not None:
            _close(sw, doc)
    return row


#: ★ 格子表：`(标签, 说明, 可调用)` —— ★ 标签用于命令行筛选（★ 卡住时只跑某几格）。
CASES = (
    ("V1", "投影视图", case_v1_draw_view_from_model_view),
    (
        "V2a",
        "剖面视图（ExcludedComponents=空 Dispatch）",
        lambda sw: case_v2_section_view(sw),
    ),
    (
        "V2b",
        "剖面视图（ExcludedComponents=空数组）",
        lambda sw: case_v2_section_view(sw, excluded="empty_array"),
    ),
    ("V3", "局部视图", case_v3_detail_view),
    ("V4", "断裂视图（InsertBreak3）", case_v4_break_view),
    ("V5", "辅助视图", case_v5_auxiliary_view),
    ("A1", "图纸格式（SetupSheet6）", case_a1_setup_sheet),
    (
        "A2a",
        "表面粗糙度（带引线）",
        lambda sw: case_a2_surface_finish(sw, leader="straight"),
    ),
    (
        "A2b",
        "表面粗糙度（swNO_LEADER）",
        lambda sw: case_a2_surface_finish(sw, leader="none"),
    ),
    (
        "A3a",
        "基准符号（不选，对照格）",
        lambda sw: case_a3_datum_tag(sw, select_edge=False),
    ),
    (
        "A3b",
        "基准符号（先选视图里一条边）",
        lambda sw: case_a3_datum_tag(sw, select_edge=True),
    ),
    (
        "A4a",
        "注释（不选 ⇒ 官方说自由放置）",
        lambda sw: case_a4_note(sw, select_edge=False),
    ),
    ("A4b", "注释（先选一条边）", lambda sw: case_a4_note(sw, select_edge=True)),
    ("A5", "气泡序号（AutoBalloon5）", case_a5_auto_balloon),
    ("A6", "孔表（InsertHoleTable3）", case_a6_hole_table),
    ("A7a", "修订表（第一次）", lambda sw: case_a7_revision_table(sw, second=False)),
    (
        "A7b",
        "修订表（第二次 ⇒ 官方说要回 null）",
        lambda sw: case_a7_revision_table(sw, second=True),
    ),
    (
        "A8a",
        "中心符号线（不选，对照格）",
        lambda sw: case_a8_center_mark(sw, select_edge=False),
    ),
    (
        "A8b",
        "中心符号线（先选一条边）",
        lambda sw: case_a8_center_mark(sw, select_edge=True),
    ),
)


def _selected(filters, label):
    """★ 命令行筛选（★ 不传筛选就跑全部）。"""
    if not filters:
        return True
    return any(f.lower() in label.lower() for f in filters)


def main() -> int:
    """★ 跑全部（或筛选后的）格子 ⇒ 写 `output/drawing-batch-evidence.json` 并打印判读。"""
    filters = [a for a in sys.argv[1:] if not a.startswith("-")]
    sw, _meta = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "工程图 13 项（视图族 5 + 标注族 8）—— ★ 每格先回读前置再调用；"
        "★ 前置不成立时 ok=False 且 note 写明'不能当能力不成的证据'",
        "spec": "specs/202-user-coverage-gaps",
        "filters": filters,
        "part_path": str(PART_PATH),
        "pick_z_m": PICK_Z_M,
        "cases": [],
    }
    try:
        #: ★ 铁律 2：未抑制的模态框会把会话挂死 ⇒ 跑之前先置位（★ 收尾必复位）
        try:
            sw.CommandInProgress = True
            ev["command_in_progress"] = True
        except Exception as exc:  # noqa: BLE001
            ev["command_in_progress"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        for label, desc, fn in CASES:
            if not _selected(filters, label):
                continue
            t0 = time.time()
            try:
                case = fn(sw)
            except Exception as exc:  # noqa: BLE001
                #: ★ 不许吞异常：★ 异常本身进 dict（★ 任务硬要求）
                case = {
                    "tag": label,
                    "ok": False,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:240]),
                }
            case["label"] = label
            case["desc"] = desc
            case["seconds"] = round(time.time() - t0, 2)
            ev["cases"].append(case)
            print(
                "  %-5s %-34s ok=%-6s pre=%-6s %ss"
                % (
                    label,
                    desc,
                    case.get("ok"),
                    case.get("preconditions_held"),
                    case.get("seconds"),
                )
            )
            for k in (
                "view_delta",
                "breakline_delta",
                "sf_delta",
                "datum_delta",
                "note_delta",
                "table_delta",
                "center_delta",
                "sel_by_mark_before_call",
                "preconditions_held",
                "enum_missing",
                "err",
                "call_err",
                "note",
            ):
                if k in case:
                    print("        %-22s %s" % (k, str(case[k])[:180]))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["preconditions_held_count"] = sum(
        1 for c in ev["cases"] if c.get("preconditions_held")
    )
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  判读：成 %d / %d（★ 前置成立的 %d 格）"
        % (ev["passed"], ev["total"], ev["preconditions_held_count"])
    )
    print(
        "  ⚠ ★ `ok=False` 且 `preconditions_held=False` 的格子**不能**当「能力不成」的证据。"
    )
    print("  产物：%s" % OUT_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
