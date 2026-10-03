#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""COM 调用 arity 自动比对（不猜宿主接口，只判「有没有这种形状的成员」）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务的工具层，非第三方移植）
# 文件:   scripts/audit_call_arity.py —— 本文件自身
# 定位:   AGENTS.md 铁律 2「静态签名比对」在**规模**上的自动化。
#         工程图子技能里所有 COM 访问都走 _safe_member(obj, "Name", *args)
#         包装，好处是单个成员缺席不会整体崩，**坏处是签名错了也不会报错、
#         只会静默无效果**。手工逐个比对 140 个调用点不现实，故自动化。
#         与 scripts/check_provenance.py 配套：那一个管「出处可追溯」，
#         这一个管「调用形状对不对」。
# 签名源: 由 D:\\AI\\SW\\tools\\reflect-interop.ps1 对官方 interop DLL 做
#         纯元数据反射生成的 iface_*.txt（读官方程序集，非实测）。
# 许可:   本仓库 MIT。纯 AST + 文本解析，无第三方代码引入。
# ⚠ 本工具为静态比对，未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）
# ⚑ 定位: 5 处存疑、1 处查不到 —— 见 docs/signature-audit.md 批次 5。
#   其中「查不到」的 GetSheet 是真实缺陷（成员根本不存在，静默回落），
#   而 InsertModelAnnotations3/4 属 *args 解包导致的**假阳性**，
#   故本工具选择跳过 Starred 实参：宁可漏报也不误报。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务的工具层，非第三方移植）
# 文件:   scripts/audit_call_arity.py —— 本文件自身
# 定位:   AGENTS.md 铁律 2「静态签名比对」在**规模**上的自动化。
#         与 scripts/check_provenance.py 配套：那一个管「出处可追溯」，
#         这一个管「调用形状对不对」。详见模块 docstring。
# 签名源: D:\AI\SW\tools\reflect-interop.ps1 对官方 interop DLL 做纯元数据
#         反射生成的 iface_*.txt（读官方程序集，不是实测）。
# 许可:   本仓库 MIT。纯 ast + 文本解析，无第三方代码引入。
# 覆盖:   全文件 —— 内聚型工具模块，逐个私有函数贴来源块无意义。
# ⚠ 本工具为静态比对，未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
import ast
import sys
from collections import defaultdict
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

#: 被审计的成员包装函数名（与本仓库实际用法保持一致）
#: ⚑⚑ 2026-10-01（轮 145）：原集合是 `{"_safe_member", "get_com_member", "get_com_member"}`
#:   ——★ **第三项是重复的**（显然是 `safe_get_com_member` 写错了）
#:   ⇒ **`safe_get_com_member` 的调用点一直被漏计**（与 `check_member_names.py` 同一个根因：
#:      "有几个取成员的同义词"没有单一真源）。
#:   ⚑ 本轮再加 `call_com_member`（轮 145 为"故意要调"的站点新起的名字）。
#:   ⇒ 这三种**都是**"取/调 COM 成员"的调用点，都要算。
WRAPPERS = {"_safe_member", "get_com_member", "safe_get_com_member", "call_com_member"}

IFACE_HEAD = __import__("re").compile(r"^##\s+(\w+)\s*$")
IFACE_SIG = __import__("re").compile(r"^\s+(\S+)\s+(\w+)\((.*)\)\s*$")


def load_signatures(paths):
    """解析反射清单 → {成员名: {参数个数: [接口.签名, ...]}}

    ``get_`` / ``set_`` 前缀会被剥掉：反射里属性呈现为 ``get_X``，
    而调用侧写的是 ``X``。
    """
    table: dict[str, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
    for path in paths:
        current = None
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        for raw in text.splitlines():
            head = IFACE_HEAD.match(raw)
            if head:
                current = head.group(1)
                continue
            sig = IFACE_SIG.match(raw)
            if not (sig and current):
                continue
            ret, name, params = sig.groups()
            if name.startswith(("get_", "set_")):
                name = name[4:]
            # ⚑⚑ arity 口径 = **调用方要传的实参个数**。
            #
            # 旧规则「排除**所有** by-ref 出参」对 `Object&` 成立、**对 `Int32&` 不成立**：
            # 反射里 `Void GetErrorMessages(Object&, Object&, Object&)` 确实是 0 参
            # （三个全是纯 [out]），但 2026-10-01 真机实测（SW 2026 SP4.1）证明
            # **标量出参 `Int32&` 必须由调用方传入**：
            #
            #     CreateNewStudy3(name, 13, 0)                ✗ DISP_E_PARAMNOTOPTIONAL
            #                                                 （「非选择性的参数」= 该参必需）
            #     CreateNewStudy3(name, 13, 0, VARIANT(VT_BYREF|VT_I4, 0))  ✓
            #
            # 实测脚本：`D:\AI\SW\probe_outparam_convention.py`（五种形态逐一试）
            # 与 `probe_disparray_forms.py`（六种形态逐一试）。
            # 结论已固化进 `scripts/sw_connect.py::out_i4()` 的 docstring。
            #
            # ⇒ 规则按**类型**分（可证伪、不是启发式）：
            #     `Int32&` / `Int16&` / `Double&` / `Boolean&` 等**标量出参** ⇒ 调用方要传，**计入**
            #     `Object&` / `Variant&` 等**数组出参**（纯 [out] 容器） ⇒ 调用方不传，**排除**
            #
            # ⚠ 这条修正的由来：本轮新增 `sw_mold.py` 后跑审计，`sw_topology` /
            #   `sw_simulation` 报 18 处「存疑」，逐条查全是「带 `Int32&` 的成员」。
            #   旧规则把它们算成 0 参，而代码传了 byref VARIANT ⇒ 数量对不上。
            #   **是工具的口径错，不是代码错。**
            _params = [p.strip() for p in params.split(",") if p.strip()]

            # ⚑⚑ **2026-10-01（轮 123）：特例全部去掉 —— arity 就是反射里的参数个数。**
            #   真机实验 `tools/probe_outparam_object_byref.py` 对
            #   `IHoleStandardsData.GetHoleStandards(Object& Standards, Object& Types)`：
            #     A 不传出参 ⇒ com_error -2147352561「**非选择性的参数**」（= `DISP_E_PARAMNOTOPTIONAL`）
            #     D `VARIANT(VT_BYREF|VT_VARIANT, None)` ×2 ⇒ **返回 True** ✓
            #   ⇒ ★ **`Object&` 出参是必填的** ⇒ 官方 arity = **2**。
            #   ⇒ 旧规则「`Object&` / `Variant&` / `Dispatch&` 一律排除」**是错的**。
            #   ★ 按**铁律 4**：arity 以**出厂反射的参数个数**为准，不做任何类型特例。
            #   ⚠ 边界：只证了 `GetHoleStandards` 一个成员；但"以反射为准"这条**不需要外推**，
            #     它本身就是本仓库的口径。
            count = len(_params)
            table[name][count].append(f"{current}.{name}({params.strip()}) -> {ret}")
    return table


def call_sites(path):
    """用 AST 精确取包装调用点：(行号, 包装函数名, 成员名, 实参数 or None)。

    ``None`` 表示含 ``*args`` 解包 —— 真实元数运行期才定，静态不可判定。
    """
    src = Path(path).read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
        if name not in WRAPPERS or len(node.args) < 2:
            continue
        member_node = node.args[1]
        if not (isinstance(member_node, ast.Constant) and isinstance(member_node.value, str)):
            continue
        if any(isinstance(a, ast.Starred) for a in node.args[2:]):
            rows.append((node.lineno, name, member_node.value, None))
        else:
            rows.append((node.lineno, name, member_node.value, len(node.args) - 2))
    return sorted(rows)


def direct_call_sites(path, table):
    """捕获**直调**形式 ``obj.Member(a, b, c)``，补上包装式审计的盲区。

    只看包装函数（_safe_member / get_com_member）会漏掉 sw_part.py 这类
    直接写 ``model.FeatureManager.FeatureExtrusion3(...)`` 的代码 ——
    而那恰恰是参数最容易写错的地方。

    假阳性控制：只统计**名字确实存在于官方签名表里**的成员。任何普通 Python
    方法调用（append / split / update…）名字不在表里，直接被过滤掉。
    """
    src = Path(path).read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    known = set(table)
    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if not isinstance(fn, ast.Attribute):
            continue
        member = fn.attr
        if member.startswith("_") or member not in known:
            continue
        if node.args and any(isinstance(a, ast.Starred) for a in node.args):
            rows.append((node.lineno, "direct", member, None))
        else:
            rows.append((node.lineno, "direct", member, len(node.args)))
    return sorted(rows)



# ⚑⚑ **2026-10-01（轮 130）：`comtypes` 早绑定的调用点，本工具判不了 —— 单独归类，不算「存疑」。**
#
# ## 为什么本工具的 arity 规则管不到它们
# 本工具的 arity 口径（见上）是在 **pywin32 迟到绑定**上**真机量出来**的
# （`tools/probe_outparam_object_byref.py`，已知事实 68）。
# 而 `comtypes` 的**早绑定**代理对 `[out]` 参数的处理**不同**：
# 它会**自己分配** [out] 数组/VARIANT ⇒ 调用方**只传入参就是对的**。
# ⇒ 拿 pywin32 的规矩去判 comtypes 的调用点，是**类别错误**，不是"代码有问题"。
#
# ## 为什么要写成**显式表**而不是启发式
# ⚠ 与 `check_interface_member_ownership.MANUAL_MAP` 同一理由：
# **没有依据的不许自动进来**；每一条都要写清"为什么它属于这一类"，
# 而且**在输出里单独列出来**（不是静默吞掉）。
#
# ## 表的结构
# `(文件名后缀, 行号)` → 理由
#
# ★★★★★★ 2026-10-04（轮 116）**⚠ 这张表按**行号**登记 ⇒ 它会**漂**** ——
#   ★ **真机读数**：★ `tests/test_arity_comtypes_classification.py` 报
#     「★ 应当恰好 **2** 条 comtypes，★ 实际 **0**」⇒
#   ★★ **真因**：★ 我在轮 87 与 115 改过 `sw_delivery.py`（★ 加注释 · ★ 换成员 · ★ 修 fake）⇒
#     ★★★ **⇒ 那两条的行号从 `635` / `884` 漂到 `671` / `965`** ⇒ **登记失配** ✓
#   ★★★★ **⇒ 已按新行号更正**；★ **而这个"按行号"的脆弱性是本表固有的** ——
#     ★ 它与「钉死数量」「mock 落后」是**同一族**：★ **改了实现、★ 配套的定位就失配**、
#     ★★ **而它**不会自己报错**（★ 只在跑那条测试时才现形）✓
#   ★★★★★ **⇒ 下次改这个文件时，★ 记得同步这两行**；★ 更稳的做法是改成**按成员名**登记
#     （★ 那要改 `audit` 的接口 —— ★ **本轮不动**、★ 如实留给后人）✓
COMTYPES_CALL_SITES: dict[tuple[str, int], str] = {
    ("sw_delivery.py", 671):
        "`package.IGetDocumentNames(document_count)` —— 走 **comtypes 早绑定**"
        "（`_comtypes_document_names()`，由 `comtypes.client.GetModule` 得到）。"
        "注释写明：「comtypes 会自动分配 [out] 数组，只需传入 Count」。"
        "官方 arity = 2（`Int32&` + `Object&`）⇒ 在 **pywin32** 上要传 2，"
        "在 **comtypes** 上只传入参即正确。**不是缺陷。**",
    ("sw_delivery.py", 965):
        "`sw.OpenDoc6(path, type, options, empty)` —— 同样是 **comtypes 早绑定**"
        "（`sw` 由 `comtypes` 创建）。官方 arity = 6（含两个 `[out] long`）⇒ "
        "comtypes 代理自行分配出参。**不是缺陷。**"
        "⚠ 另：本仓库另有纪律「不经 pywin32 的 OpenDoc6 打开零件」，本条只在 Pack and Go 路径使用。",
}

def audit(target, signature_paths):
    """返回 (通过, 存疑, 查不到, 动态) 四组，供 CLI 与测试共用。

    同时覆盖两种调用形态：包装式（_safe_member/get_com_member）与直调式（obj.Member）。
    """
    table = load_signatures(signature_paths)
    sites = [(n, f, m, a) for n, f, m, a in call_sites(target) if f in WRAPPERS]
    sites += direct_call_sites(target, table)
    sites.sort()
    ok, doubt, missing, dynamic, comtypes = [], [], [], [], []
    stem = _stem(target)
    for lineno, fn, member, argc in sites:
        # ⚑ 轮 130：先看是不是**已知的 comtypes 早绑定站点** —— 那类本工具判不了
        reason = COMTYPES_CALL_SITES.get((stem, lineno))
        if reason is not None:
            comtypes.append((lineno, member, argc, reason))
            continue
        if argc is None:
            dynamic.append((lineno, member, fn))
        elif member not in table:
            missing.append((lineno, member, argc, fn))
        elif argc in table[member]:
            ok.append((lineno, member, argc))
        else:
            doubt.append((lineno, member, argc, sorted(table[member].items())))
    return ok, doubt, missing, dynamic, comtypes


def _stem(path) -> str:
    """取文件名（用于 `COMTYPES_CALL_SITES` 的键）。"""
    from pathlib import Path as _P
    return _P(str(path)).name


def main() -> int:
    # ⚑ 2026-10-01 加：`--all` 一次审 `scripts/` + `tools/`。
    #   起因：`tools/` 里有 3 个文件 / 35 处 COM 调用**不在本工具的覆盖内**，
    #   而我新写的一个工具因此带着 `GetStudy` 的 arity 错进了仓库。
    #   **⇒ COM 调用分散在两处，门禁必须两处都覆盖。**
    if "--all" in sys.argv:
        import glob as _glob
        _root = Path.cwd()
        targets = (sorted(_glob.glob(str(_root / "scripts" / "*.py")))
                   + sorted(_glob.glob(str(_root / "tools" / "*.py"))))
        sigs = [a for a in sys.argv[1:] if a != "--all"]
        if not sigs:
            print("用法: python scripts/audit_call_arity.py --all <iface_*.txt> [...]")
            raise SystemExit(2)
        bad_total = 0
        for _t in targets:
            _ok, _doubt, _missing, _dyn, _com = audit(_t, sigs)
            # ⚠ `ok` 是**列表**不是计数（第一版写成 `%d` ⇒ TypeError）
            if _doubt or _missing:
                print("%s\n  pass=%d doubt=%d missing=%d"
                      % (_t, len(_ok), len(_doubt), len(_missing)))
                for row in (_doubt + _missing)[:6]:
                    print("    %s" % (row,))
                bad_total += len(_doubt) + len(_missing)
        print()
        print("全量（scripts/ + tools/）: 有问题 %d 处" % bad_total)
        raise SystemExit(0 if bad_total == 0 else 1)

    if len(sys.argv) < 3:
        print("用法: python scripts/audit_call_arity.py <目标.py> <iface_*.txt> [...]")
        print(__doc__)
        return 2
    target, sigs = sys.argv[1], sys.argv[2:]
    ok, doubt, missing, dynamic, comtypes = audit(target, sigs)

    print(f"目标: {target}")
    print(f"签名源: {', '.join(Path(p).name for p in sigs)}")
    print(f"调用点: {len(ok) + len(doubt) + len(missing) + len(dynamic)} 个\n")
    print(f"  通过     {len(ok)}")
    # ⚑ 轮 130：`comtypes` 早绑定站点**单独报**（本工具的 arity 规则是在 pywin32 上量的）
    print(f"  comtypes {len(comtypes)}   ← **本工具判不了**（早绑定自行分配 [out]）")
    print(f"  存疑     {len(doubt)}   ← 同名成员存在但 arity 全对不上")
    print(f"  查不到   {len(missing)}   ← 全程序集无此成员名")
    print(f"  动态     {len(dynamic)}   ← 含 *args 解包，静态不可判定\n")

    if comtypes:
        print("── comtypes 明细（**不是缺陷**，是有依据的单独归类）──")
        for lineno, member, argc, reason in comtypes:
            print(f"  {target}:{lineno}  {member}() 实参 {argc} —— {reason[:110]}")
        print()
    if doubt:
        print("── 存疑明细 ──")
        for lineno, member, argc, variants in doubt:
            print(f"  {target}:{lineno}  {member}() 实参 {argc}")
            for arity, sigs_ in variants:
                print(f"        官方 arity={arity}  例: {sigs_[0][:96]}")
        print()
    if missing:
        print("── 查不到明细 ──")
        for lineno, member, argc, fn in missing:
            print(f"  {target}:{lineno}  {member}() 实参 {argc}  经 {fn}()")
        print()
    if dynamic:
        print("── 动态实参（需人工核对）──")
        for lineno, member, fn in dynamic:
            print(f"  {target}:{lineno}  {member}(*args)  经 {fn}()")
        print()
    return 1 if (doubt or missing) else 0


if __name__ == "__main__":
    raise SystemExit(main())
