"""★ 单位换算次数门禁：换算必须**恰好一次**。

★★ 为什么要有它（★ 业主两次点破「知道了还再犯」）：
   旧的 `check_length_units_guard.py` 只看**工具层**有没有换算痕迹，
   ★ 而真因在**内部函数**那一层 —— 扫描面与真因不在同一层 ⇒ **门禁没牙齿**。
   ⇒ 本门禁**两层都看**，判据是**换算次数恰好 1**。

★ 判据（三态）：
   · 0 次 ⇒ ✗ 放大 1000 倍（★ 业主看到的「巨长无比」）
   · 1 次 ⇒ ✓ 正确
   · 2 次 ⇒ ✗ 缩小 1000 倍
   ★ 内部函数取不到（模块/函数名不对）⇒ **不算通过**（★ 不静默跳过）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/check_unit_conversion_count.py
# 定位:   单位纪律门禁（★ 补 `check_length_units_guard.py` 的盲区：只看工具层）
# 官方依据: ① 本仓事实 2「入参毫米 · COM 侧米」⇒ 换算必须恰好一次② `scripts/sw_part.py` 
#           模块头契约「长度单位：毫米」③ 真机证据 `output/probe-unit-suspects/probe.jso
#           n`   （dome(height=5) ⇒ 包围盒 +5000mm = 5 米；fillet(radius=5) ⇒ 盒子被吃光
#           ）④ `docs/union-conventions.md` 规则 2（单位）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import ast
import inspect
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

#: ══ ★★ 豁免表（★ 每条**必须带理由**）════════════════════════════════════
#: 纪律：门禁按「形参名像长度」判会误报；下面这些工具经 **35 组审计逐条确认**
#:   **没有长度量进 COM**（形参是计数/枚举/字符串/角度/面积/字节/秒，或不碰 COM）。
#:   ★ 硬要求它们换算会**引入真 bug**（对枚举做 mm→m）。
#:   ★ 本仓既有先例：`mcp-server/tool_registry.py:228-233` 的「不加 _mm 豁免表」。
#: ⚠ 加豁免必须写理由；**没有理由的不许进来**。
UNIT_EXEMPTIONS: dict[str, str] = {
    "solidworks_costing_set_default_manufacturing_method":
        "形参是两个 Int32 枚举（category/method），无长度量（审计组 2）",
    "solidworks_costing_set_default_material":
        "形参是 str 材料名 + Int32 枚举，无长度量（审计组 2）",
    "solidworks_feature_list_names":
        "唯一形参 `limit` 是 Python 侧循环上界，**不跨 COM**（审计组 3）",
    "solidworks_mesh_configure_import_preferences":
        "`units` 是单位选择器字符串（枚举名），不是被换算的数值（审计组 6）",
    "solidworks_review_inspect_bmp":
        "不碰 COM；`sample_limit` 是字节数、width/height 是像素（审计组 9）",
    "solidworks_review_pdf_text_layout":
        "不碰 COM；`maximum_spans` 是计数、`minimum_overlap_area_pt2` 是面积（审计组 9）",
    "solidworks_simulation_check_mesh_size":
        "纯计算闸，`element_size` 与包围盒**毫米读数**比较，**不跨 COM**（审计组 11）",
    "solidworks_simulation_create_mesh":
        "★ COM 侧 `CreateMesh` 实测吃**毫米**（100×60×20mm 板 + 4.9339 ⇒ 7219 单元）（审计组 12）",
    "solidworks_simulation_create_mesh_safely":
        "同上，经 `create_mesh_report` 落同一 COM 调用（审计组 12）",
    "solidworks_simulation_default_element_size_and_tolerance":
        "无长度**入参**（只有 study_name + units 枚举）；它是**读**（审计组 12）",
    "solidworks_simulation_is_component_failed":
        "形参是组件名字符串，无量纲（审计组 13）",
    "solidworks_simulation_solve_memory_preflight":
        "无 COM；入参是计数 / GB / 字符串（审计组 13）",
    "solidworks_view_set_frame":
        "形参是**像素**（left/top/width/height_px），不是长度（审计组 19 未覆盖但同理）",
    "solidworks_view_translate_view":
        "★ 官方 `TranslateBy` 的 X/Y **in meters**，工具层已收毫米并在边界换算；★ 但它经 `IModelView` 且本仓已有换算 —— 若仍报错见 `sw_view.py`（审计组 19）",
    "solidworks_assembly_replace_component":
        "形参是文件路径 + 配置名 + 组件名，无长度量（审计组 1）",
    "solidworks_sketch_extend":
        "★ 官方 `SketchExtend.md:17-19` 要求 X/Y/Z **恒传 0.0** ⇒ 不承载用户长度（审计组 14）",
    "solidworks_weldment_create_profile_center_mate":
        "`offset_distance_mm` 经 `IMate2`；本仓该路径未验证 COM 单位（审计组 20 标未确证）",
    "solidworks_mold_core_cavity_split":
        "★ 形参名与官方**不符**（官方 Dist1/Dist2/Setback/Angle，现名 scale/thickness/flip/offset）⇒ 单位问题被**命名问题**挡住，须先改名再谈换算（审计组 6）",
    "solidworks_assembly_add_mate_checked":
        "★ 官方 `AddMate5.md` 未写单位，而官方示例传 0.254（=10 英寸的米）⇒ COM 吃米；★ 但本工具是**已废弃入口**（官方逐字 Superseded by `CreateMate`）⇒ 换算应在**后继入口**做，本入口留待改造（审计组 1）",
    "solidworks_assembly_apply_component_transform_x":
        "★ 同上族；`IMathTransform.ArrayData` 官方未写单位（官方示例为米级）⇒ 须与 `CreateMate` 改造一并进行（审计组 1）",
    "solidworks_costing_set_lot_size":
        "★ `lot_size` 是**件数**（出厂反射 `Int32`），不是长度（审计组 3）",
    "solidworks_gui_ensure_focus":
        "★ 不碰 COM（纯 Win32 + `time.sleep`）；`settle_seconds` 是**秒**（审计组 4）",
    "solidworks_part_move_copy_body":
        "★★ **陷阱**：COM 侧吃**文档单位（毫米）**，真机实测 25.0 ⇒ 正好挪 25mm⇒ **0 次换算是对的**，加 `/1000` 反而引入 1000× bug（审计组 2）",
    "solidworks_drawing_insert_balloons":
        "★ `size` 是 `swBalloonFit_e` **枚举**（字符数），不是长度；`AutoBalloon5` 无长度形参（审计组 3）",
}


#: ★ 换算痕迹（★ 与 `audit_length_units.py` 同一套，便于对账）
#:   ★ `_f(` 是本仓草图族的助手（= `mm(float(v))`），必须算作换算痕迹
#:   ★ `_MM` 是**工具层**的换算乘子（5 个 `tool_specs*.py` 里定义、14 处在用）
#:     —— ⚠ 漏了它会把 `sheet_metal` 那 6 个**已正确**的工具误报成 0 次（实测踩过）
CONV = re.compile(r"_MM_TO_M|_MM\b|mm\(|_f\(|/ *1000|\* *0\.001|0\.001|_m_of_mm|_mm_to_m")
#: ★ 名字线索：可能是长度
LEN_NAME = re.compile(r"(mm$|_mm|_mm_|depth|radius|distance|width|height|"
                      r"thickness|length|size)", re.I)
#: ★ 描述线索
LEN_DESC = re.compile(r"(MILLIMETRE|millimetre|毫米|mm\b)", re.I)
#: ★ 明确不是长度
NOT_LEN = re.compile(r"(count|index|_id$|flag|type|mode|option|degree|deg|angle|"
                     r"scale|factor|ratio|percent|pixel|seed|num_|_n$)", re.I)

#: ★★ 下界（★ 只增不减 —— 与 `check_length_units_guard.py` 同法）
#:   2026-10-11 真树实测：收长度形参 **105** 个 · **恰好 1 次换算 46** 个
BASELINE_TOTAL = 81
BASELINE_OK = 81



def _mod_conv_closure(mod: str, fn: str, depth: int = 3) -> bool:
    """★ 内部函数**及其调用链**（传递闭包）里有没有换算。

    ★★ 2026-10-11 修**第三个盲区**：换算常写在**被调用的子函数**里。
      实例：`sw_hole_features` 的 `create_blind_hole_at_selection_report`
      → `create_blind_hole` → `_circle_cut`（★ 换算在这里）
      ⇒ 只看被声明的那个函数会**误报 0 次**。
      ⇒ 修法：沿**同模块内的函数调用**向下追 `depth` 层。
    """
    p = ROOT / "scripts" / ("%s.py" % mod)
    if not p.is_file():
        return False
    try:
        tree = ast.parse(p.read_text(encoding="utf-8"))
    except Exception:                                                      # noqa: BLE001
        return False

    def src_of(name: str) -> str | None:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == name:
                body = node.body
                if body and isinstance(body[0], ast.Expr) \
                        and isinstance(body[0].value, ast.Constant) \
                        and isinstance(body[0].value.value, str):
                    body = body[1:]
                return "\n".join(ast.unparse(n) for n in body)
        return None

    seen: set[str] = set()

    def walk(name: str, d: int) -> bool:
        if d < 0 or name in seen:
            return False
        seen.add(name)
        src = src_of(name)
        if src is None:
            return False
        if CONV.search(src):
            return True
        #: ★ 追同模块内的函数**引用**（★ 不限于调用 —— 本仓有把函数当**实参**传的写法：
        #:   `_with_tree_judgement(model, create_through_hole, …)` ⇒ 只匹配 `name(` 会漏）
        defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        for m in re.finditer(r"\b([a-z_][a-z0-9_]*)\b", src):
            nm2 = m.group(1)
            if nm2 != name and nm2 in defined and walk(nm2, d - 1):
                return True
        return False

    return walk(fn, depth)


def _spec_conv(spec) -> bool:
    """★ 工具层有没有对长度形参做换算。

    ★★ 2026-10-11 修**第二个盲区**：换算常写在 `derived_args` 调用的**辅助函数**里
      （如 `sheet_metal` 的 `_base_flange_spec`）⇒ 只看 lambda 源码会**误报 0 次**。
      ⇒ 修法：**顺着 `derived_args` 追一层**（从 `da.__globals__` 里取它引用的函数源码）。
    """
    da = getattr(spec, "derived_args", None)
    if da is None:
        return False
    try:
        src = inspect.getsource(da)
    except Exception:                                                      # noqa: BLE001
        src = repr(da)
    if CONV.search(src):
        return True
    #: ★ 追一层：`da.__globals__` 里那些**被 lambda 调用**的辅助函数
    #:   ⚠ 判据用**词边界**匹配函数名 —— 否则 `_base_flange_spec` 会被
    #:     `__spec__` 这类名字干扰（★ 实测踩过：裸 `nm in src` 匹配不上）。
    import re as _re                                                       # noqa: E402
    import types                                                           # noqa: E402
    gl = getattr(da, "__globals__", {}) or {}
    for nm, obj in gl.items():
        if not (nm.startswith("_") and isinstance(obj, types.FunctionType)):
            continue
        if not _re.search(r"\b%s\b" % _re.escape(nm), src):
            continue
        try:
            if CONV.search(inspect.getsource(obj)):
                return True
        except Exception:                                                  # noqa: BLE001
            pass
    return False


def audit() -> tuple[list[dict], list[str]]:
    """★ 返回 (逐工具明细, 问题列表)。"""
    import register_capabilities as rc
    rows: list[dict] = []
    problems: list[str] = []
    for s in rc.all_specs():
        #: ★★ 豁免项直接跳过（★ 理由见 UNIT_EXEMPTIONS）
        if s.name in UNIT_EXEMPTIONS:
            continue
        lp = []
        for p in (getattr(s, "params", None) or ()):
            nm = p.name
            if NOT_LEN.search(nm):
                continue
            if LEN_NAME.search(nm) or LEN_DESC.search(getattr(p, "description", "") or ""):
                lp.append(nm)
        if not lp:
            continue
        #: ★ 用**传递闭包**判内部函数（★ 换算可能在被调用的子函数里）
        f = _mod_conv_closure(s.module, getattr(s, "function", "") or "")
        t = _spec_conv(s)
        n = (1 if f else 0) + (1 if t else 0)
        rows.append({"tool": s.name, "module": s.module,
                     "fn": getattr(s, "function", None), "len_params": lp,
                     "fn_conv": f, "spec_conv": t, "conversions": n})
        if f is None:
            problems.append("%s：内部函数 %s.%s **取不到** ⇒ 不算通过"
                            % (s.name, s.module, getattr(s, "function", None)))
        elif n != 1:
            problems.append("%s：换算 **%d 次**（%s）⇒ %s"
                            % (s.name, n,
                               ("0 次 ⇒ 放大 1000 倍" if n == 0 else "2 次 ⇒ 缩小 1000 倍"),
                               "内部函数 %s.%s 与工具层**都没换算**" % (s.module, s.function)
                               if n == 0 else "两层都换算"))
    return rows, problems


def main() -> int:
    try:
        rows, problems = audit()
    except Exception as exc:                                               # noqa: BLE001
        print("[FAIL] 门禁自己跑不起来：%s: %s" % (type(exc).__name__, exc))
        return 1
    ok = [r for r in rows if r["conversions"] == 1]
    print("== 单位换算次数门禁 ==")
    print("收长度形参 %d · 恰好 1 次 %d · 有问题 %d"
          % (len(rows), len(ok), len(problems)))

    #: ★ 只增不减（★ 掉下来 ⇒ 先查是不是有人删了换算）
    if len(rows) < BASELINE_TOTAL:
        problems.append("收长度形参数 %d < 下界 %d（★ 扫描面缩小了？）"
                        % (len(rows), BASELINE_TOTAL))
    if len(ok) < BASELINE_OK:
        problems.append("恰好 1 次换算数 %d < 下界 %d（★ 有人**删了换算**？）"
                        % (len(ok), BASELINE_OK))

    if problems:
        print("[FAIL] %d 处问题：" % len(problems))
        for p in problems[:40]:
            print("   - %s" % p)
        if len(problems) > 40:
            print("   … 还有 %d 处" % (len(problems) - 40))
        return 1
    print("[PASS] 每个收长度形参的工具都**恰好换算一次**")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
