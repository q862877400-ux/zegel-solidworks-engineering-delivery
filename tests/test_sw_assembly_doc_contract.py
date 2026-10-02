"""sw_assembly_doc 的官方签名契约测试（不连接 SolidWorks）。

⚑ 本文件最重要的一条是 ``test_every_referenced_member_is_in_the_registry`` ——
它专门抓「凭印象写 API」。本模块初稿引用了 5 个**在 IAssemblyDoc 上不存在**
的成员（SuppressMate2 / MoveComponent / DissolveAll / HideComponent2 /
GetPathName / GetSuppressions），全靠这条抓出来。官方真实名字是：

    SuppressMate2  → SetComponentSuppression(String)
    MoveComponent  → TranslateComponent()        零参
    DissolveAll    → DissolveSubAssembly()       零参
    HideComponent2 → HideComponent() / ShowComponent()  零参
    GetPathName    → 不在 IAssemblyDoc（路径在 IModelDoc2）
    GetSuppressions→ 不在 IAssemblyDoc

签名来源：AGENTS.md §四.1③ —— 对官方 interop 程序集的纯元数据反射
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt → IAssemblyDoc 段

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_assembly_doc_contract.py —— 本文件自身
# 定位:   域 8 装配的登记表完整性契约 + 「不许凭印象写成员名」纪律锁。
# 被测对象: scripts/sw_assembly_doc.py
# 覆盖:   全文件 —— 本文件是自包含测试单元，各测试函数已就地标明核对对象。
# ⚠ 本文件为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import io
import re
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "sw_assembly_doc.py"
REFLECTION = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt")

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IAssemblyDoc 段
# 定位:   独立复算的期望规模（由本测试**自己逐行解析**）。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
EXPECTED = {
    "raw_members": 211,
    "internal_dispatch": 25,
    # ⚑ property_count 是**反射里的行数**；一个属性通常有 get_X 与 set_X
    #    **两行**，所以唯一属性名比行数少。本表两个数都记下来。
    "property_lines": 13,
    "property_names": 8,
    "method_count": 173,
    "distinct_capabilities": 133,
}

#: 本模块曾凭想象写、且**在 IAssemblyDoc 上不存在**的成员 —— 不得复活
HALLUCINATED = ("SuppressMate2", "MoveComponent", "DissolveAll",
                "HideComponent2", "GetPathName", "GetSuppressions",
                "GetLightweightComponentCount")


def _faithful(obj, name, *args, **kwargs):
    if obj is None:
        return None
    attr = getattr(obj, name, None)
    if attr is None:
        return None
    if callable(attr):
        try:
            return attr(*args, **kwargs)
        except TypeError:
            return attr()
    return attr


def _load():
    connect = types.ModuleType("sw_connect")
    connect.get_com_member = _faithful
    connect.call_com_member = _faithful
    sys.modules.setdefault("sw_connect", connect)
    spec = importlib.util.spec_from_file_location("sw_assembly_doc", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_assembly_doc"] = module
    spec.loader.exec_module(module)
    module.get_com_member = _faithful
    module.call_com_member = _faithful
    return module


def _parse_iface():
    """逐行解析 IAssemblyDoc 段（正则切段会提前截断，见 sw_view 的教训）。"""
    if not REFLECTION.is_file():
        return None
    current, out = None, []
    for raw in REFLECTION.read_text(encoding="utf-8",
                                   errors="replace").splitlines():
        if raw.startswith("## "):
            if current == "IAssemblyDoc":
                break
            current = raw[3:].strip()
            if current == "IAssemblyDoc":
                out = []
        elif current == "IAssemblyDoc" and raw.strip():
            out.append(raw.strip())
    return out


def _referenced_members():
    """本模块源码里通过 call_assembly_doc 引用的成员名。"""
    source = MODULE_PATH.read_text(encoding="utf-8")
    return set(re.findall(r'call_assembly_doc\(\s*doc,\s*"(\w+)"', source))


# ── ⚑ 核心：显式封装引用的成员必须都在登记表里 ──────────────────────

def test_every_referenced_member_is_in_the_registry():
    """专抓「凭印象写 API」——本模块初稿有 6 个这样的成员，全靠这条抓出。"""
    m = _load()
    known = set(m.ASSEMBLY_DOC_ARITY) | set(m.ASSEMBLY_DOC_PROPERTIES)
    missing = sorted(_referenced_members() - known)
    assert not missing, (
        f"源码引用了登记表里没有的成员: {missing}\n"
        f"⚠ 这类成员名多半是凭印象写的 —— 回反射清单核实后再改。")


def test_hallucinated_members_never_appear():
    """曾凭想象写、官方不存在的成员名，不得出现在源码里。"""
    source = MODULE_PATH.read_text(encoding="utf-8")
    for member in HALLUCINATED:
        # 允许出现在「⚑ 初稿写错了」的注释里做记录，但不得出现在实际调用里
        for hit in re.findall(rf'call_assembly_doc\(\s*doc,\s*"{member}"',
                             source):
            assert False, f"{member} 是凭印象写的，官方 IAssemblyDoc 上不存在"
        assert f'"{member}"' not in re.sub(r"^\s*#.*$", "", source,
                                           flags=re.M), (
            f"{member} 不该出现在实际代码里")


# ── 登记表完整性 ─────────────────────────────────────────────────────

def test_registry_size_matches_reflection():
    m = _load()
    assert len(m.ASSEMBLY_DOC_ARITY) == EXPECTED["distinct_capabilities"]
    # 属性：登记表存的是**唯一名**，反射里 get_X/set_X 是两行 ⇒ 名字数更少
    assert len(m.ASSEMBLY_DOC_PROPERTIES) == EXPECTED["property_names"]


def test_property_lines_exceed_unique_names_because_of_get_set_pairs():
    """把「反射行数」与「唯一属性名」的区别固化成断言，避免后人拿错数。

    ⚑ 本测试初版把两者混为一谈（写成 ``len(names) == property_lines``，
       即 8 == 13）—— 恰好又是一次「两个数含义不同却当成同一个」。
    """
    if _parse_iface() is None:
        print("  (跳过：反射清单不在本机)")
        return
    block = _parse_iface()
    sig = re.compile(r"^\S+\s+(get_|set_)(\w+)\s*\(")
    names, line_count = set(), 0
    for line in block:
        hit = sig.match(line)
        if hit:
            line_count += 1
            names.add(hit.group(2))
    assert line_count == EXPECTED["property_lines"], (
        f"get_/set_ 行数应为 {EXPECTED['property_lines']}，实际 {line_count}")
    assert len(names) == EXPECTED["property_names"], (
        f"唯一属性名应为 {EXPECTED['property_names']}，实际 {len(names)}")
    m = _load()
    assert len(m.ASSEMBLY_DOC_PROPERTIES) == len(names)
def test_composition_of_assembly_doc_is_as_documented():
    if _parse_iface() is None:
        print("  (跳过：反射清单不在本机)")
        return
    block = _parse_iface()
    sig = re.compile(r"^(\S+)\s+(\w+)\s*\((.*)\)$")
    internal = props = methods = 0
    for line in block:
        hit = sig.match(line)
        if not hit:
            continue
        _, name, _args = hit.groups()
        if re.match(r"^I[A-Z]", name):
            internal += 1
        elif name.startswith(("get_", "set_")):
            props += 1
        else:
            methods += 1
    assert len(block) == EXPECTED["raw_members"]
    assert internal == EXPECTED["internal_dispatch"]
    assert props == EXPECTED["property_lines"]
    assert methods == EXPECTED["method_count"]


def test_every_registered_name_exists_in_reflection():
    if _parse_iface() is None:
        print("  (跳过：反射清单不在本机)")
        return
    block = _parse_iface()
    m = _load()
    for name in m.ASSEMBLY_DOC_ARITY:
        assert any(f"{name}(" in line for line in block), (
            f"{name} 不在 IAssemblyDoc 段里 —— 可能编造")


def test_no_internal_dispatch_or_property_leakage():
    m = _load()
    for name in m.ASSEMBLY_DOC_ARITY:
        assert not re.match(r"^I[A-Z][a-z]", name), f"{name} 是 COM 内部分发口"
    overlap = set(m.ASSEMBLY_DOC_PROPERTIES) & set(m.ASSEMBLY_DOC_ARITY)
    assert not overlap, f"既是属性又登记成方法: {sorted(overlap)}"


def test_numbered_variants_folded_and_declared():
    m = _load()
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "编号变体" in source and "明确声明的取舍" in source


# ── 通用访问器 ───────────────────────────────────────────────────────

def test_call_rejects_unknown_member_loudly():
    m = _load()
    try:
        m.call_assembly_doc(object(), "NotARealMember")
    except KeyError as exc:
        assert "NotARealMember" in str(exc)
        return
    raise AssertionError("未登记的成员名被放行了")


def test_call_rejects_wrong_arity_before_com():
    m = _load()
    zero = next(n for n, a in m.ASSEMBLY_DOC_ARITY.items() if a == 0)
    try:
        m.call_assembly_doc(object(), zero, 1)
    except ValueError as exc:
        assert zero in str(exc)
        return
    raise AssertionError("错 arity 未被拦")


def test_add_mate_requires_fifteen_arguments():
    """AddMate5 是 15 参（不含末尾 by-ref 错误码）。"""
    m = _load()
    try:
        m.add_mate(object(), 1, 2, 3)
    except ValueError as exc:
        assert "15" in str(exc)
        return
    raise AssertionError("AddMate5 未校验实参个数")






def test_evidence_passes_configuration_to_component_count():
    """官方 GetComponentCount 是 **1 参**，不是零参。"""
    m = _load()
    seen = []
    m.get_com_member = lambda o, n, *a, **k: (seen.append((n, a)) or 3)
    m.call_com_member = lambda o, n, *a, **k: (seen.append((n, a)) or 3)
    m.collect_assembly_doc_evidence(object(), "Default")
    assert ("GetComponentCount", ("Default",)) in seen




# ── 直接运行 ─────────────────────────────────────────────────────────

def _main():
    failures = []
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
        except Exception as exc:  # noqa: BLE001
            failures.append((test.__name__, exc))
            print(f"  FAIL  {test.__name__}: {exc}")
    print(f"\n{len(tests) - len(failures)}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    raise SystemExit(_main())
