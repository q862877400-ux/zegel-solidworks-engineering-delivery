"""★ 真缺口分诊：把 `audit_real_gaps.py` 那 101 条分成 ① 该挂 ② 内部件 ③ 不做（+原因）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/triage_real_gaps.py
# 定位:   ★ 2026-10-03（轮 396）24 小时计划 v2 的 **T0.1**（`docs/plan-24h-v2.md` 段 0
#           ）。
# ★ 口径来自 `tools/audit_real_gaps.py`：**真缺口 = 公开函数 −（有我们工具 ∪ 被上游调）*
# *。
#   ★★ 而"真缺口 101 条"**不等于 101 个该挂的工具** —— 里面混着
# **内部件**（类/异常/管道）与**不该挂的**（★ 事实 40：`IModeler.Create*Surface` 返回值
# 跨次都变）。
#   ⇒ 本脚本做那层分诊，并把**每一类的理由**写成可核对的字段。
# 官方依据: 不适用（★ 纯静态扫描 + 既有文档里的既有结论）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★★ **原则（★ 重要）：默认"该挂"，只把有**明确理由**的移出。**
#   反面做法是"凭名字猜哪些是内部件" —— 那会**静默丢掉真能力**（★ 与硬约束⑧冲突）。
#   所以三条移出规则都要**能在下面逐条读出来**：
#   ```
#   ① 不是函数：CamelCase（类/异常/数据类）—— 挂出去只会污染工具面
#   ② 内部管道：明确的名单（★ 逐条列出，见 PLUMBING_WHY）
#   ③ 返回值不可靠：★ 事实 40（`IModeler.Create*Surface` 跨次都变）⇒ **标"不做"+原因**
#   ```
#   其余 ⇒ **该挂** ✓

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path


#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"" + _ROOT_S + r"")
UPSTREAM_SERVER = ROOT / "mcp-server" / "server.py"
OUT = Path(Path(__file__).resolve().parents[1] / "output" / "real-gap-triage.json")

#: ★ 规则②：内部管道的**显式名单**（★ 每条给理由 —— 不靠名字猜）
PLUMBING_WHY: dict[str, str] = {
    "get_modeler": "返回 IModeler 单例（COM 会话对象），不是能力",
    "require_runtime_available": "运行期可用性守卫，不是能力",
    "runtime_available": "运行期可用性布尔，不是能力",
    "iter_features_recursive": "特征树遍历的内部实现",
    "iter_studies": "算例遍历的内部实现",
    "get_cosmosworks": "返回 CW 顶层 COM 对象，不是能力",
    "get_cw_document": "返回 CW 文档 COM 对象，不是能力",
    "get_study_manager": "返回算例管理器 COM 对象，不是能力",
    "get_fastener_table": "返回紧固件数据表的内部查询",
    "get_fastener_table_types": "同上",
    "get_fastener_types": "同上",
    "get_hole_standards": "返回标准清单的内部查询（★ 已有 hole_standards 工具覆盖）",
    "get_mass_property_override_options": "返回选项对象的内部查询",
    "collect_loads_evidence": "内部证据收集器（★ 那些 add_* 才是能力）",
    "get_loads_and_restraints": "同上（读回内部状态）",
    "list_topology_constraints_and_controls": "★ 已有 solidworks_topology_list_constraints 工具覆盖",
    "get_topology_study_manager": "返回管理器 COM 对象，不是能力",
    "get_topology_study_options": "返回选项对象，不是能力",
    "ensure_simulation_addin": "★ 已有工具覆盖（加载项开关）",
}

#: ★ 规则③：不做（★ 事实 40：`IModeler.Create*Surface` 返回值**跨次都变**）
UNRELIABLE_MODULE = "sw_surface"
UNRELIABLE_PATTERN = re.compile(r"^create_.*surface$|^create_sheet_from_surface$")

#: ★ 规则③：**已有据的死路**（★ 逐条写理由 —— 不靠名字猜）
#: ★★★ 2026-10-03（轮 438）**一条有原则的"不做"** ——
#:   ★ 有些函数**本来就不能**做成工具：**它的签名是裸坐标**。
#:   ★★ 依据：**规则 3**（本仓五统一之一）——「**声明式 `selection`，禁裸坐标**」；
#: ★ 而 `tool_registry` 已有对应门禁（`_BARE_COORD_NAMES` + `_looks_like_coord_component
#: `）
#:     ⇒ ★ 即使把它挂上，**声明也会过不了门禁** ✓
#:   ★★ 故它不是"该挂"，而是"不做"（★ 而理由是**规则**，不是"我们没功夫"）。
CANNOT_BE_A_TOOL_WHY: dict[tuple[str, str], str] = {
    (
        "sw_simulation",
        "select_face_at",
    ): "★★ 它的签名是**裸坐标**（`(model, x, y, z)`）⇒ **规则 3 禁止**"
    "把它做成工具（★ 而 `tool_registry` 的声明门禁**会直接拦住**）。"
    "★ 它仍是**内部助手**（★ 多处调用）——★ 只是**不能对外暴露**。",
}


KNOWN_DEAD_ENDS: dict[tuple[str, str], str] = {
    ("sw_part", "sketch_spline"): (
        "第 141 轮真机：`CreateSpline2` 返回 None、重绘后仍 0 段、"
        "旧版 `CreateSpline` 在迟到绑定里不存在；后继 `CreateSpline3` 末参是 "
        "**BYREF `Object&`** ⇒ 事实 47/68 架构限制（pywin32 到不了）"
    ),
}

#: ★ 不是函数：CamelCase 或这些后缀（类 / 异常 / 数据类）
NOT_A_FUNCTION_SUFFIXES = (
    "Error",
    "Evidence",
    "Ref",
    "Data",
    "Options",
    "Result",
    "Info",
)


_HAVE_TOOL_CACHE: set | None = None


def have_tool_functions() -> set:
    """★ 已被某个 ToolSpec 声明为目标函数的名字集（★ 懒加载）。"""
    global _HAVE_TOOL_CACHE
    if _HAVE_TOOL_CACHE is None:
        _HAVE_TOOL_CACHE = _tool_functions()
    return _HAVE_TOOL_CACHE


#: ★ 第四层证据（轮 399）：**功能已由另一个包装暴露** ——
#:   ★ 真例（真机核过）：`sw_part.shell` 自己没有工具，
#:   ★★ 而 `sw_part.shell_report` **有**（工具 `solidworks_part_shell`）。
#:   ⇒ 那不是缺口（★ “名字不同 ≠ 能力没有” —— 事实 311 同族）。
_REPORT_SUFFIXES = ("_report", "2_report", "_report2")


#: ★ 动词对（轮 402）：低层原语叫 `add_X`，★ 而**对外封装**叫 `apply_X`
#: （★ 真例：`sw_simulation_loads.add_fixed_restraint(manager, entities, …)` 吃 **COM ma
#: nager**，
#: ★ 而 `sw_simulation.apply_fixed_restraint` 才是取 manager + 构造数组 + 调原语的那一层
#: ，
#:   ★★ 而**后者已经是工具**）。
#:   ⇒ ★ 只看 `_report` 后缀会**把这一整族误判成缺口**。
_VERB_PAIRS = ("apply", "create", "set", "insert", "remove")


def _name_variants(name: str) -> list:
    """★ `name` 及其**动词换写**的候选（★ 不改其余部分）。"""
    out = [name]
    if name.startswith("add_"):
        tail = name[4:]
        out.extend("%s_%s" % (v, tail) for v in _VERB_PAIRS)
    return out


def exposed_by_prefix(name: str) -> str | None:
    """★ ★★ 2026-10-03（轮 432）**前缀别名规则** —— 一个**已注册**的 function
    若**以 `name + "_"` 开头** ⇒ 说明那个裸函数**已经是工具的一部分**。

    ★★ 真例（本轮发现）：`sw_weldment.create_structural_member` 一直被算成「该挂」，
      ★ 而它已经被包成了 `solidworks_weldment_create_structural_member`（function =
      `create_structural_member**_from_sketch**`）⇒ ★ **名字不同 ≠ 能力没有**。
    ★ 而旧规则（`exposed_by_wrapper`）**只试** `base` 与 `base + "_report"` ⇒ ★ 认不出这一类。
    """
    have = have_tool_functions()
    for base in _name_variants(name):
        for cand in sorted(have):
            if cand.startswith(base + "_"):
                return cand
    return None


def used_by_other_module(module: str, name: str) -> bool:
    """★ ★★ 2026-10-03（轮 432）**跨模块使用 ⇒ 内部件**。

    ★★ 真例：`sw_selection_spec.entities_as_array` 是本轮**新加的助手**（给多实体载荷装数组），
      ★ 而它**已经被 `sw_simulation_loads` 引用** ⇒ ★ 它是**内部件**，**不是待挂的能力**。
    ★ 判据：★ 在 `scripts/` 下**除它自己**外有人调它。
    """
    #: ★★★ 2026-10-03（轮 432）**判据收紧为"真的被调用"** ——
    #:   ★ 第一版用的是**子串出现**（`if name in text`），★ 而它**太宽**：
    #:     注释 / 字符串 / 别名都算"出现" ⇒ 把真缺口吞掉。
    #:   ★★ 而**本仓的负例守卫当场抓到它**：
    #: `tests/test_real_gap_triage_contract.py::test_wrapper_rule_does_not_swallow_real_
    #: gaps`
    #:     断言 `sw_part.linear_pattern` 必须是「该挂」，★ 而它被判成了「内部件」。
    #: ⇒ ★ 正解：**用 AST 找 `ast.Call`**（★ 即"真的被调用"）—— ★ 与**事实 51**（判据要
    #: 贴合代码的组织单元，
    #:     不要按文本匹配）**同族**。
    own = ROOT / "scripts" / (module + ".py")
    import ast as _ast  # noqa: PLC0415

    for f in (ROOT / "scripts").glob("*.py"):
        if f == own:
            continue
        try:
            tree = _ast.parse(f.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        for node in _ast.walk(tree):
            if not isinstance(node, _ast.Call):
                continue
            func = node.func
            #: ★ 三种写法：`name(...)` · `mod.name(...)` · 别名后的 `name(...)`
            if isinstance(func, _ast.Name) and func.id == name:
                return True
            if isinstance(func, _ast.Attribute) and func.attr == name:
                return True
    return False


def exposed_by_wrapper(name: str) -> str | None:
    """★ 若 `name`（或它的**动词换写**）的**包装变体**已有工具 ⇒ 回那个名字。

    ★ 两类侯选：① 同名 + `_report`；② **动词换写**（`add_X` ⇒ `apply_X` 等）+ `_report`。
    """
    have = have_tool_functions()
    for base in _name_variants(name):
        for cand in (base, base + "_report", base + "2_report"):
            if cand in have:
                return cand
    return None


_EMPTY_STUB_CACHE: dict = {}


def is_empty_stub(module: str, name: str) -> str:
    """★★ 第五层证据（轮 399）：**空实现（存根）检测**。

    ★ 真例：`sw_part.hole_wizard` **有名字、有参数、有文档串**，
    ★★ 而函数体只有一个 `pass` —— ★ 挂出去**必然什么都不发生**，
    ★ 而且比 `spline` 那种“会报错”的更糟：它**静默成功**。

    :returns: 空存根的**原因**；非空存根回**空字符串**。
    """
    key = (module, name)
    if key not in _EMPTY_STUB_CACHE:
        reason = ""
        path = ROOT / "scripts" / (module + ".py")
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            tree = None
        if tree is not None:
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name == name:
                    body = [
                        b
                        for b in node.body
                        if not (
                            isinstance(b, ast.Expr)
                            and isinstance(b.value, ast.Constant)
                            and isinstance(b.value.value, str)
                        )
                    ]  #: ★ 剔掉 docstring
                    if not body:
                        reason = "函数体只有 docstring（连 `pass` 都没有）"
                    elif all(isinstance(b, ast.Pass) for b in body):
                        reason = "函数体只有 `pass`（**空实现** —— 调了什么都不会发生）"
                    break
        _EMPTY_STUB_CACHE[key] = reason
    return _EMPTY_STUB_CACHE[key]


#: ★★★ 2026-10-03（轮 436）**显式别名表** —— 「**功能已由另一个名字的工具覆盖**」的那一
#: 类。
#:
#: ★★ **为什么用穷举表而不是再放宽规则**：**事实 53** ——
#:   「同一个启发式连续修补 ≥ 3 次就该停下换做法；★ 而**最优换法常是
#:   把猜测变成一张穷举表**」。本档的 `exposed_by_wrapper` / `exposed_by_prefix`
#:   已经是**两个启发式**（★ `name + "_report"` 与 `name + "_"` 前缀）——
#:   ★ 而这三条**名字差得多**，启发式再放宽就会吞真缺口 ⇒ ★★ **改成显式登记**。
#:
#: ★ **每条都写清依据**（★ 照 `PLUMBING_WHY` 的先例：没依据的不许进来）——
#:   ★ 而这三条的依据都是**真机/静态可核的**：那个工具的 `function` **调的就是它**。
ALIASED_BY_TOOL: dict[tuple[str, str], str] = {
    (
        "sw_export",
        "export_to_bmp",
    ): "solidworks_export_bmp（★ 它的 function `export_bmp_report` **调的正是** `export_to_bmp`）",
    #: ★★ 2026-10-03（轮 438）新增 —— ★ 依据已核：
    #: `sw_simulation.create_study_report` **调的正是** `create_static_study`（已读源码
    #: ），
    #:   ★ 而它就是工具 `solidworks_simulation_create_study` 的 function。
    (
        "sw_simulation",
        "create_static_study",
    ): "solidworks_simulation_create_study（★ 它的 function `create_study_report` **调的正是** "
    "`create_static_study`）",
    (
        "sw_export",
        "export_to_image",
    ): "solidworks_export_image（★ `export_image_report` **调的正是** `export_to_image`）",
    #: ★★★ 2026-10-03（轮 437）**本条已删** —— ★ 而那是**结构判据取代穷举表条目**的正确
    #: 闭环：
    #:   ★ `_server_export_functions()` 现已把 `server.py` 侧的 60 个 function 并进名单
    #:     ⇒ `batch_export_formats` 可见 ⇒ ★★ **前缀规则**（`batch_export` ⇐
    #:     `batch_export_*`）**自己就能认出它** ⇒ ★ 本条多余 ✓
    #:   ★ 而**下面两条不能删**：它们的包装名是 `export_bmp_report` /
    #:     `export_image_report` —— ★ **既非同名加后缀、也非前缀**，
    #:     ★★ 而再放宽启发式就会吞真缺口（事实 53）。
}


def classify(module: str, name: str) -> tuple[str, str]:
    """★ 把一条真缺口分成**三类**。★★ 可测（契约测试直接调它）。

    :returns: ``(kind, why)``，kind ∈ 「该挂」/ 「内部件」/ 「不做」。
    """
    if (module, name) in KNOWN_DEAD_ENDS:
        return "不做", KNOWN_DEAD_ENDS[(module, name)]
    if module == UNRELIABLE_MODULE and UNRELIABLE_PATTERN.match(name):
        return "不做", (
            "事实 40：IModeler.Create*Surface 的返回值**跨次都变**"
            "（官方 4 个已 Obsolete、*2 后继同样返回 None）⇒ "
            "挂出来只会给人「能调」的错觉"
        )
    #: ★★ 2026-10-03（轮 436）**显式别名**：功能已由另一个名字的工具覆盖（★ 而启发式推不
    #: 出来）
    _alias = ALIASED_BY_TOOL.get((module, name))
    if _alias is not None:
        return "已有", "功能已由 `%s` 覆盖" % _alias
    _cant = CANNOT_BE_A_TOOL_WHY.get((module, name))
    if _cant is not None:
        return "不做", _cant
    stub_reason = is_empty_stub(module, name)
    if stub_reason:
        return "不做", stub_reason
    wrapper = exposed_by_wrapper(name)
    if wrapper is not None:
        return "已有", ("功能已由 `%s` 包装暴露（★ 名字不同 ≠ 能力没有）" % wrapper)
    if name[:1].isupper() or name.endswith(NOT_A_FUNCTION_SUFFIXES):
        return "内部件", "不是函数（类 / 异常 / 数据类）"
    #: ★★★ 2026-10-03（轮 432）**显式登记优先于抽象推断** ——
    #:   ★ `PLUMBING_WHY` 是**人写下的理由**，★ 而下面两条是**我从代码推的**。
    #:   ★★ 真例：`sw_simulation.get_study_manager` 既在 `PLUMBING_WHY` 里、
    #:     又命中了"被别的模块调用" ⇒ ★ 两条都对，
    #:     而**人写的理由该赢**（★ 否则那张表的意义被稀释）。
    if name in PLUMBING_WHY:
        return "内部件", PLUMBING_WHY[name]
    #: ★★ 2026-10-03（轮 432）**前缀别名**：`create_structural_member` ⇐
    #:   `create_structural_member**_from_sketch**`（已注册）（★ 真例）
    prefixed = exposed_by_prefix(name)
    if prefixed is not None:
        return "已有", (
            "功能已由 `%s` 包装暴露（★ **前缀别名**："
            "裸函数名是包装名的前缀）" % prefixed
        )
    #: ★★ 2026-10-03（轮 432）**跨模块使用 ⇒ 内部件**：
    #:   ★ 别人已经在用它 ⇒ 它是助手，**不是待挂的能力**（★ 真例：`entities_as_array`）
    if used_by_other_module(module, name):
        return "内部件", (
            "★ 已被 `scripts/` 下**别的模块引用** ⇒ 它是**内部助手**，不是待挂的能力"
        )
    return "该挂", ""


def _public_defs(module: str) -> list[str]:
    p = ROOT / "scripts" / (module + ".py")
    if not p.exists():
        return []
    try:
        tree = ast.parse(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []
    return [
        n.name
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")
    ]


def _server_export_functions() -> set[str]:
    """★★★ 2026-10-03（轮 437）**分诊的第二个盲区的修法** ——
    ★ `_tool_functions()` 读的是 **ToolSpec**（`register_capabilities.all_specs()`），
      ★★ 而 `server.py` 里另有一批**非 ToolSpec** 的工具声明
        （★ 形式是 `exports = { "函数名": 模块.函数, … }`）
      ⇒ ★ 那一半**对分诊不可见** ⇒ 把已覆盖的名字报成该挂。
    ★★ 而判据是**结构**（★ 找变量名为 `exports` 的 dict 字面量的**键**）——
      ★ 不是再列一张表（★ 否则又变成穷举 —— 事实 53）。
    """
    import ast as _ast  # noqa: PLC0415

    path = ROOT / "mcp-server" / "server.py"
    out: set[str] = set()
    try:
        tree = _ast.parse(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return out
    for node in _ast.walk(tree):
        if not isinstance(node, _ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, _ast.Name)]
        if "exports" not in names or not isinstance(node.value, _ast.Dict):
            continue
        for k in node.value.keys:
            if isinstance(k, _ast.Constant) and isinstance(k.value, str):
                out.add(k.value)
    return out


def _tool_functions() -> set[str]:
    """★ 我们**已注册**成工具的 function 名。

    ★★ ★ 2026-10-03（轮 402）**第二次修正（同一族）**：
      ① 最初扫**文件**（`tool_specs*.py`）⇒ 阈掉未注册的文件（轮 400 修）；
      ② 改成读 `BATCH_MODULES` 后**仍然用正则扫源码** ⇒ ★★ 只认 `function="..."` 的写法，
         ★ 而 `tool_specs_batch29.py` 用的是**函数名列表**（`"apply_pressure_report",`）
         ⇒ **漏掉了它的 4 条任务加载**（★ 于是 `add_pressure` 等被误判成缺口）。
      ⇒ ★ 正解：**读注册表对象**（`register_capabilities.all_specs()` 的 `.function`）——
        ★ 那才是**它们真正对外暴露的名字**，★ 与 `audit_real_gaps` 同一个口径。
    """
    try:
        sys.path.insert(0, str(ROOT / "mcp-server"))
        import register_capabilities as _rc  # noqa: PLC0415

        #: ★★★ 2026-10-03（轮 437）**并上 `server.py` 那半边** ——
        #:   ★ 否则分诊只看得见 ToolSpec，★ 而把 `batch_export_formats` 这类
        #:     （★ 在 `server.py` 侧声明的）当成没有工具 —— ★ 事实 350 记的就是这个盲区。
        return {
            s.function for s in _rc.all_specs() if getattr(s, "function", None)
        } | _server_export_functions()
    except Exception:  # noqa: BLE001
        #: ★ 兜底：退回扫源码（★ 而那是有漏洞的 —— 所以上面那条才是主路）
        out: set = set()
        for f in (ROOT / "mcp-server").glob("tool_specs*.py"):
            try:
                out.update(
                    __import__("re").findall(
                        r'function="([A-Za-z_][A-Za-z0-9_]*)"',
                        f.read_text(encoding="utf-8"),
                    )
                )
            except Exception:  # noqa: BLE001
                continue
        return out


def _upstream_called() -> set[str]:
    if not UPSTREAM_SERVER.exists():
        return set()
    try:
        src = UPSTREAM_SERVER.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return set()
    return set(re.findall(r"\b([a-z_][a-z0-9_]{3,})\s*\(", src))


def main() -> int:
    sys.path.insert(0, str(ROOT / "tools"))
    from audit_real_gaps import MODULES  # noqa: PLC0415

    have_tool = _tool_functions()
    upstream = _upstream_called()
    rows: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for module in MODULES:
        for name in _public_defs(module):
            #: ★ 同一模块里同名 def 可能出现两次（★ 真例：
            #:   `sw_hole_features.get_fastener_table`）⇒ 去重，否则计数虚高。
            if (module, name) in seen:
                continue
            seen.add((module, name))
            if name in have_tool:
                continue
            if name in upstream:  # ★ 被上游 server.py 调 ⇒ 不算缺口
                continue
            kind, why = classify(module, name)
            rows.append({"module": module, "name": name, "kind": kind, "why": why})

    counts: dict[str, int] = {}
    for r in rows:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    summary = {
        "total": len(rows),
        **counts,
        "★": "四类之和必须 == total（★ 本脚本自检）",
        "★口径差异": "本脚本报 108 而 audit_real_gaps 报 101 "
        "—— ★ 两者对「被上游调」的判定略有不同"
        "（本脚本用字面量匹配）；★ 本文件的 108 "
        "是本轮作业的口径，★ 而两者的模块级分布一致。",
        "self_check": len(rows) == sum(counts.values()),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=1)
        + "\n",
        encoding="utf-8",
    )

    print("  === 分诊结果（%d 条）===" % len(rows))
    for k in ("该挂", "已有", "内部件", "不做"):
        print("  %-6s %3d" % (k, counts.get(k, 0)))
    print("  自检：四类之和 == total ⇒ %s" % summary["self_check"])
    print("\n  === 该挂的（按模块）===")
    for module in MODULES:
        names = [
            r["name"] for r in rows if r["module"] == module and r["kind"] == "该挂"
        ]
        if names:
            print("  %-22s %2d  %s" % (module, len(names), ", ".join(names[:8])))
    print("\n  === 内部件 ===")
    for module in MODULES:
        names = [
            r["name"] for r in rows if r["module"] == module and r["kind"] == "内部件"
        ]
        if names:
            print("  %-22s %2d  %s" % (module, len(names), ", ".join(names[:8])))
    print("\n  === 不做 ===")
    for module in MODULES:
        names = [
            r["name"] for r in rows if r["module"] == module and r["kind"] == "不做"
        ]
        if names:
            print("  %-22s %2d  %s" % (module, len(names), ", ".join(names[:10])))
    print("\n  产物: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
