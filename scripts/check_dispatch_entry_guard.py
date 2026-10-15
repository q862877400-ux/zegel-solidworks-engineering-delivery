"""★ 门禁：**分发口**（把「成员名」当参数转发给 COM 包装器的函数）必须逐个表态。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁）
# 文件:   scripts/check_dispatch_entry_guard.py
# 定位:   把 spec 228 记下的那条通用教训变成常设守卫（2026-10-09 · spec 229）：
#         **「加新分发口时必须问一句：它进审计白名单了吗」** —— 一个存在但没人审的
#         入口 = 没有守卫（事实 40）。
# 官方依据: 无（纯 AST + 本仓既有登记表）。by-ref 语义依据见 spec 228 §三。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
#
# ## 靶子：**审计的可见性边界**
# `audit_byref_args.py`（by-ref 占位审计）只审「**成员名写在调用点**」的调用 ——
# 它的 `WRAPPERS = {_safe_member, get_com_member, safe_get_com_member, call_com_member}`
# 要求**第二实参是字符串字面量**。⇒ 凡是把成员名**当变量**传进去的调用点，
# 静态审计**一律看不见**。spec 228 只修了其中**一个**入口（`call_assembly_doc`）。
#
# ★ 本轮（spec 229）先**量**清这条边界到底有多宽（真树实测）：
# ```
#   COM 包装器调用点总数 1310
#     · 字面量（审计可见）        1219
#     · 非字面量（审计不可见）      91   ← 7 %
#         ├ 形参转发（真「分发口」） 37   ← 本门禁判它
#         ├ 局部变量               52
#         └ 计算式                  2
# ```
# ⇒ ★ 37 个分发口**逐个表态**是本门禁的判据；52 + 2 那两个桶**只计数、不判罪**
#   （把它们一次判完需要逐个人工定性，会变成半成品 —— 先可见化 + 冻结下界）。
#
# ## ★★★ spec 233：上面那组读数**是虚增的**（口径缺陷，已修）
# `ast.walk(fn)` 会**下钻到嵌套 `def`** ⇒ 嵌套函数里的同一个调用点被**外层与内层各计一次**。
# 真树实测虚增：`visible` **+34** · `非字面量` **+6**（其中 3 处被同时计进 `param` 与 `local`，
# 3 处被计两次 `local`）。修正后（按调用点去重 + 按**最内层包围 `def`** 归属）：
# ```
#   COM 包装器调用点总数 1266   （1310 → 1270 → ★ spec 240：1266）
#     · 字面量（审计可见）        1183   （1219 → 1185 → ★ spec 240：1183）
#     · 非字面量（审计不可见）      85   （91 → 85）
#         ├ 形参转发（真「分发口」） 37   （不变）
#         ├ 局部变量               46   （52 → 46）
#         └ 计算式                  2   （不变）
# ```
# ★★ **spec 240 的 -4**：`sw_weldment.py` 删掉无调用方的共用骨架 `_create_from_definition`
#   （它含 4 个 `get_com_member(..., "<字面量>")` 调用点：`FeatureManager` / `CreateDefinition` /
#   `CreateFeature` / `GetErrorCode`）⇒ 可见调用点 1187 → **1183**。
#   ★ 这是**正当减少**（删了代码，不是探测器漏了）；★ 替代的内容断言 =
#   `tests/test_mate_official_entry.py`（按名字定位 `create_profile_center_mate`，
#   断言它不走 `CreateDefinition`、且逐字调 `call_assembly_doc(…, "CreateMateData"/"CreateMate")`）。
#   ★★ 注意：新加的 2 个 `call_assembly_doc(...)` **不计入本计数** —— `call_assembly_doc`
#   **不在** `audit_call_arity.WRAPPERS`（`{_safe_member, get_com_member, safe_get_com_member,
#   call_com_member}`）里 ⇒ 它由**另一条**门禁 `check_assembly_doc_call_shape.py`（spec 228）管。
# ★ `sum(buckets) == nonliteral` 现在是**门禁内的一条硬断言**（口径自洽）——
#   它自己就是这条缺陷的判据：虚增时 `91 != 85` 即红。
#
# ## 契约（**由人写死**，门禁只负责「按你写的查」）
# 每个分发口的 `def` **正上方**（跳过空行，取第一行非空行 —— 确定性关联，
# 不用行窗口启发式，见 225 的教训）必须有一行：
# ```
# #: dispatch-guard: <code> [detail]
# ```
# `code` 是**封闭词表**，且**每一条都由门禁自证**（不是声明即通过）：
#
# | code | 自证条件 |
# |---|---|
# | `covered <gate-id>` | `<gate-id>` 必须是 `docs/gate-classification.json` 里**已登记**的门禁（承重性：登记表改名即红）|
# | `covered-wrappers`  | 该 `def` 名**就在** `audit_call_arity.WRAPPERS` 里（口径从那里 import，不重写）|
# | `exempt generated-api` | 文件名匹配 `sw_api_*.py`（生成模块）|
# | `exempt internal-helper` | `def` 名以 `_` 开头（模块私有）|
# | `exempt module-local` | 该 `def` 名**全仓只此一处**，且它**所有调用点都在本文件内** |
#
# ★ `exempt *` 的语义是**「已知盲区，登记在案」**，**不是**「已验证安全」——
#   门禁只保证「盲区被枚举且不会被悄悄扩大」，**不保证**这些入口的 by-ref 是对的。
#
# ## 只增不减（下界冻结）
# 分发口数、不可见调用点数、可见字面量数都只允许**增**：
# 减少 = 探测器漏了（不是「问题解决了」）⇒ 判 FAIL，先查清再改常量。
#
# ## 假绿守卫
# ★ 「检查过的 `def` == 0」**判失败**（事实 46：`检查过 0 个` 不许 PASS）。
#
# ## 便携性
# 纯 AST + 两个仓内文件，**不需要反射转储** ⇒ 没有 SKIP 路径。
# 合成树开关：`DSH_DISPATCH_ROOT`（扫描根）· `DSH_DISPATCH_CLASSIFICATION`（登记表路径）·
# `DSH_DISPATCH_BASELINE_MIN`（下界，仅测试用）。
from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

#: ★ 扫描根可被覆盖 ⇒ 负例能在**合成树**上端到端跑。
ROOT = Path(os.environ.get("DSH_DISPATCH_ROOT") or Path(__file__).resolve().parents[1])
#: 门禁分类登记表路径（`covered <gate-id>` 的承重性依据）。
CLASSIFICATION = Path(os.environ.get("DSH_DISPATCH_CLASSIFICATION")
                      or ROOT / "docs" / "gate-classification.json")
#: 声明（确定性关联：`def` 上方第一行非空行）。两种头：`covered <gate-id>` / `exempt <code>`。
DECL = re.compile(r"^#:\s*dispatch-guard:\s*(?P<head>[A-Za-z_-]+)(?:\s+(?P<rest>\S.*?))?\s*$")
#: 封闭词表（`covered` 带参数；`covered-wrappers` 与四个 `exempt` 子码不带）。
CODES = {"covered", "covered-wrappers", "generated-api", "internal-helper", "module-local"}
#: `exempt <sub>` 的合法子码。
EXEMPT_CODES = {"generated-api", "internal-helper", "module-local"}
#: 明细打印上限。
DETAIL_LIMIT = 30
#: ★ 下界（真树实测 · 2026-10-09 · spec 229；★ **spec 233 按去重口径订正**）—— 只增不减。
BASELINE_ENTRIES = 37
BASELINE_INVISIBLE = 85          # spec 233：91 → 85（原先把嵌套 `def` 的调用点计了两次）
BASELINE_VISIBLE = 1174          # spec 233：1219 → 1185（同上，虚增 34）
#:                               ★ spec 240：1185 → **1183** —— `sw_weldment._create_from_definition`
#:                               整体删除（无调用方 + 官方不支持该路径）⇒ 少 4 个字面量调用点。
#:                               ★ 替代的内容断言见 `tests/test_mate_official_entry.py`。
#:                               ★★ spec 256：1183 → **1180** —— **`IView::Name` 换路由**：
#:                               `sw_drawing_query.py:194` / `:264` 与 `sw_drawing_view.py:436` 三处
#:                               **兜底调用被去掉**（★ 官方 `IView/Name.md` 已标 Obsolete），
#:                               `sw_review.py:637` 是**同位置换名**（`Name` → `GetName2`，★ 净 0）⇒ **净少 3**。
#:                               ★★ **为什么是正当减少**：★ 那 3 处是**调废弃成员**，★ 删它们是**目的**不是副作用。
#:                               ★ 替代的内容断言见 `tests/test_iview_name_routing_done.py`
#:                               （★ AST 按名字断言「对 `view`/`av` 调 `Name` 的处数 == 0」+
#:                                 ★ 「`sw_review.py` 用的是官方后继 `GetName2`」）。
#:                               ★★★ 2026-10-10：1180 → **1174** —— **`configure_force` 修一处真 bug**：
#:                               `sw_simulation_loadprops.configure_force` 里 **6 处**把
#:                               `get_com_member(force, "<可写属性>", 值)` **当 setter 用** ✗ ——
#:                               ★★ `get_com_member` 的语义是「**取或调**」（★ 有实参 ⇒ **一定调用**）；
#:                               而 `NormalForceOrTorqueValue` / `PhaseAngle` / `PhaseAngleUnit` /
#:                               `EquationLinearUnit` / `EquationAngularUnit` /
#:                               `EquationCoordinateSystemType` / `IncludeNonUniformDistribution2`
#:                               是**可写属性**（★ 不是方法）⇒ ★ **抛 `TypeError`** ⇒ **属性从来没设上** ✓
#:                               ★★★ **真机后果**：★ 求解弹窗报「★ **未定义载荷或规定的位移**」
#:                               +「固定-刚性零件上的载荷将不处于活动状态」⇒ **求解被前置检查拦住** ✓
#:                               ★★ **为什么是正当减少**：★ 那 6 处**本就是误用**（把 getter 当 setter）——
#:                               ★ 改成 `set_com_member` 是**修 bug 的目的**，★ 不是副作用 ✓
#:                               ★ 替代的内容断言见 `tests/test_simulation_force_property_write.py`
#:                               （★ AST 断言：★ 「`get_com_member(<可写属性>, …)` **带实参**的处数 == 0」+
#:                                 ★ 「那三个属性走 `set_com_member`」+ ★ 「`applied` 里记了
#:                                 `NormalForceOrTorqueValue`」+ ★ 真机证据断言求解成功）✓
#: ★★ 下界（真树实测 · 2026-10-09 · spec 230「解析面」）—— 只增不减。
#: `resolved` = **调用点全部可静态解析出字面量成员名**的分发口数；
#: `sites` = 这些可解析的调用点数（= 将来能继承 `audit_byref_args` 判据的规模）。
BASELINE_RESOLVED = 18
BASELINE_RESOLVED_SITES = 327


def _baseline():
    """⇒ `(entries, invisible, visible, resolved, sites)`。

    `DSH_DISPATCH_BASELINE_MIN` 可整体覆盖（仅测试用）—— ★ **3 个值 = 旧口径**
    （后两项取 0，合成树判据不受影响）；**5 个值 = 含解析面下界**。
    """
    spec = os.environ.get("DSH_DISPATCH_BASELINE_MIN", "")
    if spec.strip():
        parts = [int(x) for x in spec.split(",")]
        if len(parts) == 3:
            return (*parts, 0, 0)
        if len(parts) == 5:
            return tuple(parts)
    return (BASELINE_ENTRIES, BASELINE_INVISIBLE, BASELINE_VISIBLE,
            BASELINE_RESOLVED, BASELINE_RESOLVED_SITES)


def wrapper_names() -> set[str]:
    """⇒ COM 包装器名集合（★ 口径**从 `audit_call_arity` import，不重写**）。"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from audit_call_arity import WRAPPERS  # noqa: PLC0415

    return set(WRAPPERS)


def registered_gates() -> set[str]:
    """⇒ `docs/gate-classification.json` 里已登记的门禁文件名集合；读不到 ⇒ 空集。"""
    try:
        data = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    out = set()
    for item in data.get("classification") or []:
        name = item.get("gate")
        if isinstance(name, str) and name.strip():
            out.add(name.strip())
    return out


def iter_sources(root: Path | None = None):
    """⇒ `root/scripts/**/*.py` 里能解析的文件 `(path, src, tree, lines)`（默认 `ROOT`）。

    ★ `root` 可显式传入 ⇒ 别的门禁（spec 231）能在**自己的**扫描根上复用同一套取点。
    """
    root = root or ROOT
    for path in sorted(root.glob("scripts/**/*.py")):
        try:
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        yield path, src, tree, src.splitlines()


def _params(fn: ast.FunctionDef) -> list[str]:
    a = fn.args
    out = [x.arg for x in list(a.posonlyargs) + list(a.args) + list(a.kwonlyargs)]
    if a.vararg:
        out.append(a.vararg.arg)
    if a.kwarg:
        out.append(a.kwarg.arg)
    return out


def scan(root: Path | None = None):
    """⇒ `(entries, visible, nonliteral, buckets)`。

    `entries` = 分发口清单 `[(path, fn, 成员名形参下标, 形参名, 调用行)]`（每 `def` 最多一条）。
    `buckets` = 不可见调用点分类计数 `{param, local, computed}`。
    ★ `root` 可显式传入（spec 231 复用同一套取点），默认 `ROOT`。
    """
    wrappers = wrapper_names()
    files = {}
    for path, src, tree, lines in iter_sources(root):
        files[path] = (src, tree, lines)

    #: 全仓同名 `def` 计数（`exempt module-local` 自证用）。
    def_files: dict[str, set[Path]] = {}
    #: 全仓同名函数调用点所在文件（`exempt module-local` 自证用）。
    call_files: dict[str, set[Path]] = {}
    for path, (_src, tree, _lines) in files.items():
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                def_files.setdefault(node.name, set()).add(path)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                call_files.setdefault(node.func.id, set()).add(path)

    entries = []
    visible = 0
    nonliteral = 0
    buckets = {"param": 0, "local": 0, "computed": 0}

    #: ★★★ 调用点 → **最内层包围 `def`**（spec 233）。
    #: 为什么必须：`ast.walk(fn)` 会**下钻到嵌套 `def`** ⇒ 嵌套函数里的同一个调用点
    #: 会被**外层 `def` 与内层 `def` 各计一次** ⇒ `visible` / `nonliteral` / `buckets`
    #: 全部**虚增**（真树实测：`visible` +34 · `不可见` +6 · `local` +6）。
    #: `ast.walk` 先外后内 ⇒ 后写者即最内层。
    innermost: dict[int, object] = {}
    for _p, (_s, _t, _l) in files.items():
        for _fn in ast.walk(_t):
            if isinstance(_fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for _sub in ast.walk(_fn):
                    if isinstance(_sub, ast.Call):
                        innermost[id(_sub)] = _fn

    for path, (src, tree, lines) in files.items():
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            params = _params(fn)
            local_literals = set()
            for st in ast.walk(fn):
                if isinstance(st, ast.Assign) and isinstance(st.value, ast.Constant) \
                        and isinstance(st.value.value, str):
                    for tg in st.targets:
                        if isinstance(tg, ast.Name):
                            local_literals.add(tg.id)
            first_entry = None
            for sub in ast.walk(fn):
                if not (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)
                        and sub.func.id in wrappers and len(sub.args) >= 2):
                    continue
                if innermost.get(id(sub)) is not fn:
                    continue                      # ★ 属于更内层的 `def` ⇒ 由它计一次
                arg = sub.args[1]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    visible += 1
                    continue
                nonliteral += 1
                if isinstance(arg, ast.Name):
                    if arg.id in params:
                        buckets["param"] += 1
                        if first_entry is None or sub.lineno < first_entry[4]:
                            first_entry = (path, fn, params.index(arg.id), arg.id, sub.lineno)
                    elif arg.id in local_literals:
                        buckets["local"] += 1
                    else:
                        buckets["local"] += 1
                else:
                    buckets["computed"] += 1
            if first_entry is not None:
                entries.append(first_entry)

    entries.sort(key=lambda e: (e[0].as_posix(), e[1].lineno))
    return entries, visible, nonliteral, buckets, def_files, call_files, files


def _import_map(files):
    """⇒ `{文件: {本文件里的裸名: 模块 stem}}`（`from <stem> import <name>`）。"""
    out: dict[Path, dict[str, str]] = {}
    for path, (_src, tree, _lines) in files.items():
        m: dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                stem = node.module.split(".")[-1]
                for al in node.names:
                    m[al.asname or al.name] = stem
            elif isinstance(node, ast.Import):
                for al in node.names:
                    m[al.asname or al.name.split(".")[-1]] = al.name.split(".")[-1]
        out[path] = m
    return out


def _entry_sites(entry, files, imap):
    """⇒ 该分发口的调用点 `[(文件, 调用节点)]`。

    ★★ **按文件作用域/限定名**，不用裸名 —— 裸名会把同名 `def` 的调用点**合并**
    （`_checked` 在 9 个模块重名 ⇒ 各被算成 94 个，分类被假命中污染）。
    三种形态：同文件裸名 · 别的文件 `from <该模块> import <名>` 后裸名 · `模块.名`。
    """
    path, fn = entry[0], entry[1]
    stem = path.stem
    out = []
    for p, (_src, tree, _lines) in files.items():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            if isinstance(f, ast.Name) and f.id == fn.name:
                if p == path or imap.get(p, {}).get(fn.name) == stem:
                    out.append((p, node))
            elif (isinstance(f, ast.Attribute) and f.attr == fn.name
                  and isinstance(f.value, ast.Name) and f.value.id == stem and p != path):
                out.append((p, node))
    return out


def _bind(fn, call):
    """⇒ `{形参名: 实参节点}`（位置 + 关键字；vararg 收在 `"*<名>"`）。"""
    a = fn.args
    pos = [x.arg for x in list(a.posonlyargs) + list(a.args)]
    env: dict[str, object] = {}
    rest = []
    for i, arg in enumerate(call.args):
        if isinstance(arg, ast.Starred):
            rest.append(arg)
            continue
        if i < len(pos):
            env[pos[i]] = arg
        else:
            rest.append(arg)
    for k in call.keywords:
        if k.arg is None:
            rest.append(k.value)
        else:
            env[k.arg] = k.value
    if a.vararg:
        env["*" + a.vararg.arg] = rest
    return env


def inner_wrapper_call(fn, pname):
    """⇒ 该 `def` 里**把成员名形参 `pname` 当第 2 实参**转发的那次 COM 包装调用（或 `None`）。

    ★ 取 `ast.walk` 顺序里**第一个**命中（与 `resolution()` 原先的内联循环同序）。
    ★ spec 231 复用本函数 ⇒ 「哪个调用算转发」只有**一处**定义。
    """
    for sub in ast.walk(fn):
        if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)
                and sub.func.id in wrapper_names() and len(sub.args) >= 2
                and isinstance(sub.args[1], ast.Name) and sub.args[1].id == pname):
            return sub
    return None


def forward_slots(fn, inner):
    """⇒ `[(槽位, 固定表达式节点)]`；槽位 = 形参名 / `"*"+vararg 名` / `None`（固定实参）。

    * 形参槽 ⇒ 第二项 `None`（值由**调用方实参**填）。
    * 固定实参（字面量 / 表达式）⇒ 第二项带回节点（值由**本 `def`** 决定）。
    ★★ 只认**一级转发**：出现 `*局部变量`（如 `sw_simulation_loads._check` 的 `*tail`）
      ⇒ 返回 `None`（二级数据流，超出边界，判 `unresolved`）。
    ★ 本函数是 `_one_level_forward` 的**实现**，也是 spec 231 组 COM 实参的**唯一**口径来源。
    """
    a = fn.args
    known = {x.arg for x in list(a.posonlyargs) + list(a.args) + list(a.kwonlyargs)}
    if a.vararg:
        known.add(a.vararg.arg)
    slots = []
    for x in inner.args[2:]:
        if isinstance(x, ast.Starred) and isinstance(x.value, ast.Name):
            if not (a.vararg and x.value.id == a.vararg.arg):
                return None
            slots.append(("*" + x.value.id, None))
        elif isinstance(x, ast.Name):
            if x.id not in known:
                return None
            slots.append((x.id, None))
        else:
            slots.append((None, x))
    return slots


def _one_level_forward(fn, inner) -> bool:
    """内部包装调用的第 2 位起，**每个实参槽**是否都是「形参 / `*形参` / 固定表达式」。

    ★ 出现 `*局部变量`（如 `sw_simulation_loads._check` 的 `*tail`）⇒ **不是一级转发**
    （二级数据流，超出本切片边界）⇒ 该入口判 `unresolved`。
    """
    return forward_slots(fn, inner) is not None


def resolution(entries, files):
    """⇒ `(classes, resolved_sites)`。

    `classes[(path, fn.lineno)] = ("resolved"|"partial"|"unresolved"|"no-callers", 调用点数)`
    `resolved_sites` = **可静态解析出字面量成员名**的调用点总数 ——
    ★ 这就是「将来能继承 `audit_byref_args` 判据」的规模。
    ★ 本函数**只分类、不判罪**：成员名的 arity/by-ref 约定必须**由人写死**
    （见 spec 227 的教训：门禁不得自动挑选约定）。
    """
    imap = _import_map(files)
    classes: dict[tuple, tuple] = {}
    resolved_sites = 0
    for entry in entries:
        path, fn = entry[0], entry[1]
        sites = _entry_sites(entry, files, imap)
        if not sites:
            classes[(path, fn.lineno)] = ("no-callers", 0)
            continue
        inner = inner_wrapper_call(fn, entry[3])
        if inner is None or not _one_level_forward(fn, inner):
            classes[(path, fn.lineno)] = ("unresolved", len(sites))
            continue
        ok = 0
        for _p, call in sites:
            env = _bind(fn, call)
            m = env.get(entry[3])
            if isinstance(m, ast.Constant) and isinstance(m.value, str):
                ok += 1
        resolved_sites += ok
        cls = "resolved" if ok == len(sites) else ("partial" if ok else "unresolved")
        classes[(path, fn.lineno)] = (cls, len(sites))
    return classes, resolved_sites


def declaration_above(lines: list[str], def_lineno: int):
    """⇒ `(code, arg)` 或 `None`（未表态）。

    ★ **确定性**：只跳过空行，第一行非空行必须是声明（与 227/228 同一关联方式）。
    `exempt <sub>` ⇒ `code=<sub>`；`covered <gate-id>` ⇒ `code="covered"`、`arg=<gate-id>`；
    其余 ⇒ `code=<head>`。格式不合法（`exempt` 后不是单一子码）⇒ `("", 原文)`。
    """
    i = def_lineno - 2
    while i >= 0 and not lines[i].strip():
        i -= 1
    if i < 0:
        return None
    m = DECL.match(lines[i].strip())
    if not m:
        return None
    head = m.group("head")
    rest = (m.group("rest") or "").strip()
    if head == "exempt":
        parts = rest.split()
        if len(parts) != 1:
            return "", rest or "(缺子码)"
        return parts[0], ""
    if head == "covered":
        return "covered", rest
    return head, rest


def verify(code: str, arg: str, path: Path, fn, def_files, call_files, gates):
    """⇒ 违规说明字符串，或 `None`（自证通过）。"""
    if code == "":
        return "声明格式不合法（`exempt` 后必须恰好一个子码）：`%s`" % arg
    if code not in CODES:
        return "未知 code `%s`（封闭词表：covered / covered-wrappers / exempt {%s}）" % (
            code, "|".join(sorted(EXEMPT_CODES)))
    if code == "covered":
        if not arg:
            return "`covered` 缺 `<gate-id>`"
        if not gates:
            return None  #: 登记表读不到 ⇒ 不做承重性判罪（缺数据源 ≠ 检查失败）
        if arg not in gates:
            return "`covered %s` 的门禁**未**在 `docs/gate-classification.json` 登记（承重性）" % arg
        return None
    if code == "covered-wrappers":
        if fn.name not in wrapper_names():
            return "`covered-wrappers` 但 `%s` **不在** `audit_call_arity.WRAPPERS` 里" % fn.name
        return None
    if code == "generated-api":
        if not path.name.startswith("sw_api_"):
            return "`exempt generated-api` 但文件名 `%s` 不匹配 `sw_api_*.py`" % path.name
        return None
    if code == "internal-helper":
        if not fn.name.startswith("_"):
            return "`exempt internal-helper` 但 `%s` 不以 `_` 开头" % fn.name
        return None
    if code == "module-local":
        others = {p for p in def_files.get(fn.name, set()) if p != path}
        if others:
            return ("`exempt module-local` 但 `%s` 在别的文件里也有定义：%s"
                    % (fn.name, ", ".join(sorted(p.as_posix() for p in others))[:120]))
        out = {p for p in call_files.get(fn.name, set()) if p != path}
        if out:
            return ("`exempt module-local` 但 `%s` 被**别的文件**调用：%s"
                    % (fn.name, ", ".join(sorted(p.as_posix() for p in out))[:120]))
        return None
    return None


def bucket_consistency(buckets: dict, nonliteral: int) -> str | None:
    """⇒ 口径不自洽时的说明；自洽则 `None`（spec 233）。

    ★ 为什么单独成函数：**断言本身也要有能红的判据**。
    `tests/test_dispatch_call_site_dedup.py` 直接喂**历史缺陷的那组数**
    （桶和 91 · 不可见 85）⇒ 必须返回非 `None`。
    """
    total = sum(buckets.values())
    if total != nonliteral:
        return ("桶之和 %d != 不可见调用点 %d（口径不自洽：查重复计数）"
                % (total, nonliteral))
    return None


def main() -> int:
    entries, visible, nonliteral, buckets, def_files, call_files, files = scan()
    gates = registered_gates()
    min_entries, min_invisible, min_visible, min_resolved, min_sites = _baseline()
    classes, resolved_sites = resolution(entries, files)
    dist: dict[str, int] = {}
    for _cls, _n in classes.values():
        dist[_cls] = dist.get(_cls, 0) + 1

    print("== 分发口（成员名以**形参**转发给 COM 包装器）的守卫覆盖 ==")
    print("扫描 `%s/scripts/**/*.py` · 已登记门禁 %d 个"
          % (ROOT.as_posix(), len(gates)))
    print("调用点：可见（字面量）%d · 不可见 %d（形参转发 %d / 局部变量 %d / 计算式 %d）"
          % (visible, nonliteral, buckets["param"], buckets["local"], buckets["computed"]))
    print("★ 解析面（按文件作用域索引调用点）："
          + " · ".join("%s %d" % (k, dist.get(k, 0))
                       for k in ("resolved", "partial", "unresolved", "no-callers"))
          + " · 可解析调用点 %d" % resolved_sites)

    violations: list[dict] = []

    #: ★★★ 口径自洽（spec 233）：三个桶之和**必须**等于不可见调用点数。
    #: 虚增（嵌套 `def` 二次命中）时 `91 != 85` ⇒ 这条断言自己就红了 ——
    #: ★ 它正是那条缺陷的判据（「修宽口径本身必须有能红的判据」）。
    bad = bucket_consistency(buckets, nonliteral)
    if bad:
        violations.append({"kind": "bucket-mismatch", "file": "-", "line": 0,
                           "detail": bad})

    declared = 0
    for path, fn, _idx, pname, lineno in entries:
        lines = files[path][2]
        decl = declaration_above(lines, fn.lineno)
        rel = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
        if decl is None:
            violations.append({"kind": "undeclared", "file": rel, "line": fn.lineno,
                               "member": fn.name,
                               "detail": "`def` 正上方缺 `#: dispatch-guard: <code> …`"
                                         "（形参 `%s` 被转发给 COM 包装器）" % pname})
            continue
        code, arg = decl
        declared += 1
        bad = verify(code, arg, path, fn, def_files, call_files, gates)
        if bad:
            violations.append({"kind": "invalid-claim", "file": rel, "line": fn.lineno,
                               "member": fn.name, "detail": bad})

    #: ★ 只增不减（下界冻结）：减少 = 探测器漏了。
    if len(entries) < min_entries:
        violations.append({"kind": "baseline-shrunk", "file": "-", "line": 0,
                           "detail": "分发口 %d < 下界 %d（只增不减：先查探测器）"
                                     % (len(entries), min_entries)})
    if nonliteral < min_invisible:
        violations.append({"kind": "baseline-shrunk", "file": "-", "line": 0,
                           "detail": "不可见调用点 %d < 下界 %d（只增不减）"
                                     % (nonliteral, min_invisible)})
    if visible < min_visible:
        violations.append({"kind": "baseline-shrunk", "file": "-", "line": 0,
                           "detail": "可见调用点 %d < 下界 %d（只增不减）"
                                     % (visible, min_visible)})
    #: ★★ 解析面下界（spec 230）：减少 = **解析器漏了**（不是「问题解决了」）。
    if dist.get("resolved", 0) < min_resolved:
        violations.append({"kind": "baseline-shrunk", "file": "-", "line": 0,
                           "detail": "可解析分发口 %d < 下界 %d（只增不减：先查解析器）"
                                     % (dist.get("resolved", 0), min_resolved)})
    if resolved_sites < min_sites:
        violations.append({"kind": "baseline-shrunk", "file": "-", "line": 0,
                           "detail": "可解析调用点 %d < 下界 %d（只增不减：先查解析器）"
                                     % (resolved_sites, min_sites)})

    #: ★ 假绿守卫（事实 46）。
    if not entries:
        violations.append({"kind": "zero-checked", "file": "-", "line": 0,
                           "detail": "检查过的分发口 == 0"})
    #: ★ 解析器失效 ⇒ 假绿：只在**下界非 0**（真树口径）时才判 ——
    #:   合成树（下界 0）里「一个都解析不出」是**合法**的（可能压根没有调用点）。
    if min_sites > 0 and resolved_sites == 0:
        violations.append({"kind": "zero-checked", "file": "-", "line": 0,
                           "detail": "可解析调用点 == 0（解析器失效 ⇒ 不许 PASS）"})

    if violations:
        print("[FAIL] 违规 %d 处：" % len(violations))
        for v in violations[:DETAIL_LIMIT]:
            print("  [%s] %s:%s %s —— %s"
                  % (v["kind"], v["file"], v.get("line", "-"), v.get("member", ""), v["detail"]))
        if len(violations) > DETAIL_LIMIT:
            print("  …另有 %d 处" % (len(violations) - DETAIL_LIMIT))
    ok = not violations
    print("[PASS]" if ok else "[FAIL]")
    print("分发口 %d · 已表态 %d · 违规 %d · 可见 %d · 不可见 %d · 可解析 %d/%d · [%s] · exit %d"
          % (len(entries), declared, len(violations), visible, nonliteral,
             dist.get("resolved", 0), len(entries),
             "PASS" if ok else "FAIL", 0 if ok else 1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
