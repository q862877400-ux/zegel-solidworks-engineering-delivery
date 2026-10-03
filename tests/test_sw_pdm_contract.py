"""sw_pdm 的官方签名契约测试（不连接 SolidWorks）。

本文件最该被测的不是那几个封装函数，而是**范围判断**：
模块声称「只覆盖 Document31 / Configuration18 / Table6 三个最新世代，
因为它们是旧世代的超集」——这句话对不对，必须能对回反射清单逐个验证。
若哪天有人加一个成员到旧世代却没有加到新世代，这个测试会红。

签名来源（AGENTS.md §四.1③：对官方 interop 程序集的纯元数据反射）
    D:\\AI\\SW\\_raw\\reflect\\iface_swdocumentmgr.txt

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_pdm_contract.py —— 本文件自身
# 定位:   域 14 PDM 的世代超集契约与「by-ref 不封装」纪律锁。
# 被测对象: scripts/sw_pdm.py
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
MODULE_PATH = REPO_ROOT / "scripts" / "sw_pdm.py"
REFLECTION = Path(r"D:\AI\SW\_raw\reflect\iface_swdocumentmgr.txt")

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（swdocumentmgr interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_swdocumentmgr.txt
# 定位:   本模块封装的三个「最新世代」。这些是反射清单里成员数最多的
#         同名接口的最新一代。**不含** by-ref 出参。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
REFLECTED_ARITY = {
    # ISwDMDocument31
    "CloseDoc": 0,
    "AddCustomProperty": 3,
    "AddInvisibleCustomProperty": 3,
    "DeleteCustomProperty": 1,
    "DeleteInvisibleCustomProperty": 1,
    "GetAllExternalReferences": 1,
    # ISwDMTable6
    "AddRevisionRow": 1,
    "DeleteRow": 1,
    "DeleteColumn": 1,
    "GetBOMStartNumber": 0,
    "GetBOMNumberIncrement": 0,
    "GetBOMTableType": 0,
}

BY_REF_ONLY_MEMBERS = (
    # 官方有这些成员，但末位全是 by-ref 出参 → 本模块刻意不封装
    "GetAllCustomPropertyNamesAndValues",
    "AddColumnLeft", "AddColumnRight", "AddRowHead", "AddRowTail",
    "GetCellText",
)




def _faithful_write(obj, name, value, *args, **kwargs):
    """★ 写属性的"忠实替身"：**就是 `setattr`**。

    ★★ 2026-10-03（轮 470）新增：本仓把 98 处「写 COM 属性」从
    `get_com_member(obj, 名, 值)` 改成了 `set_com_member(obj, 名, 值)`
    （★ 前者有实参就**调用**属性 ⇒ `TypeError: 'bool' object is not callable`
    ⇒ 而外面 `return True` ⇒ 失败报成成功）。
    ⇒ ★ 故本文件的契约装置也得认得这个新名字 ✓
    """
    setattr(obj, name, value)
    return value

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
    #: ★★★ 2026-10-03（轮 470）假模块的**其余名字一律转发给真模块**。
    #:   原先只手装了一两个名字，而被测模块顶层还 import 了别的
    #:   ⇒ 报 `cannot import name … from 'sw_connect' (**unknown location**)`
    #:   （★ "unknown location" 正因为假模块**没有 __file__** ⇒ 指不到真因）。
    #:   ★ 故加 PEP 562 的模块级 `__getattr__` 兜底 ✓
    import sw_connect as _real_connect

    def _connect_attr(name):  # noqa: ANN001
        return getattr(_real_connect, name)

    connect.__getattr__ = _connect_attr
    connect.set_com_member = _faithful_write
    connect.get_com_member = _faithful
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    connect.set_com_member = _faithful
    connect.call_com_member = _faithful
    sys.modules.setdefault("sw_connect", connect)
    spec = importlib.util.spec_from_file_location("sw_pdm", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_pdm"] = module
    spec.loader.exec_module(module)
    module.set_com_member = _faithful_write
    module.get_com_member = _faithful
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    module.set_com_member = _faithful
    module.call_com_member = _faithful
    return module


def _record(m, sink, result="OBJ"):
    m.get_com_member = lambda o, n, *a, **k: sink.append((n, a)) or result
    m.set_com_member = lambda o, n, v, **k: sink.append((n, (v,))) or result
    m.call_com_member = lambda o, n, *a, **k: sink.append((n, a)) or result


def _members(interface: str) -> set[str]:
    """从反射清单里取某个接口段的成员名（去参数与返回类型）。"""
    if not REFLECTION.is_file():
        return set()
    text = REFLECTION.read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"(?ms)^## {re.escape(interface)}\r?\n(.*?)(?=\r?\n## |\z)",
                      text)
    if not match:
        return set()
    out = set()
    for raw in match.group(1).splitlines():
        if not raw.strip():
            continue
        name = raw.strip().split("(")[0].split()[-1]
        if name:
            out.add(name)
    return out


# ── 世代超集（整个模块范围判断的依据）────────────────────────────────

def test_generations_are_the_newest_available():
    m = _load()
    assert m.PDM_DOCUMENT_GENERATION == 31
    assert m.PDM_CONFIGURATION_GENERATION == 18
    assert m.PDM_TABLE_GENERATION == 6


def test_newest_document_generation_is_a_superset_of_older_ones():
    """Document31 ⊇ Document30 ⊇ Document20 —— 逐成员比对，不抽查。"""
    if not REFLECTION.is_file():
        print("  (跳过：PDM 反射清单不在本机)")
        return
    newest = _members("ISwDMDocument31")
    assert newest, "反射清单里取不到 ISwDMDocument31"
    for older in ("ISwDMDocument30", "ISwDMDocument20", "ISwDMDocument12"):
        subset = _members(older)
        if not subset:
            continue
        missing = subset - newest
        assert not missing, (
            f"{older} 有而 {newest.replace('31', '31')} 没有的成员: "
            f"{sorted(missing)}\n=> 世代超集判断不成立，模块范围需重算")


def test_every_wrapped_member_exists_in_the_covered_generations():
    """本模块封装的每个成员，必须真在它声称的世代里。"""
    if not REFLECTION.is_file():
        print("  (跳过：PDM 反射清单不在本机)")
        return
    m = _load()
    available = (_members("ISwDMDocument31") | _members("ISwDMTable6"))
    for name in list(m.DOCUMENT_ARITY) + list(m.TABLE_ARITY):
        assert name in available, f"{name} 不在所封装的世代里 —— 可能编造"


# ── 「by-ref 就不封装」纪律 ─────────────────────────────────────────



def test_source_explains_the_by_ref_decision():
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "by-ref" in source
    assert "不臆造" in source or "宁可没有" in source


# ── 签名表对账 ───────────────────────────────────────────────────────

def test_arity_tables_match_reflection_expectation():
    m = _load()
    for member, count in REFLECTED_ARITY.items():
        got = m.DOCUMENT_ARITY.get(member, m.TABLE_ARITY.get(member))
        assert got == count, f"{member} 期望 {count}，登记表是 {got}"


def test_add_custom_property_passes_three_arguments():
    m = _load()
    seen = []
    _record(m, seen)
    m.add_custom_property(object(), "PartNo", 7, "PN-001")
    assert seen == [("AddCustomProperty", ("PartNo", 7, "PN-001"))]




def test_configuration_manager_is_property():
    m = _load()
    seen = []
    _record(m, seen)
    m.get_configuration_manager(object())
    assert seen == [("ConfigurationManager", ())]


def test_table_name_is_property():
    m = _load()
    seen = []
    _record(m, seen, result="BOM")
    assert m.read_table_name(object()) == "BOM"
    assert seen == [("Name", ())]


def test_bom_start_number_uses_numeric_result():
    m = _load()
    seen = []
    _record(m, seen, result=1001)
    assert m.get_bom_start_number(object()) == 1001
    assert seen == [("GetBOMStartNumber", ())]


# ── None 目标 ────────────────────────────────────────────────────────



def test_guard_rejects_wrong_arity():
    m = _load()
    try:
        m._checked(m.DOCUMENT_ARITY, object(), "AddCustomProperty", "a", "b")
    except ValueError as exc:
        assert "AddCustomProperty" in str(exc)
        return
    raise AssertionError("错 arity 未被拦")


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
