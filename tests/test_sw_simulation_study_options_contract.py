"""sw_simulation_study_options 的登记表契约测试（不连接 SolidWorks）。

本模块最该被测的不是那几个显式包装函数，而是**登记表本身**：
它声称「这 9 个族共有 242 个可设项」，这句话对不对，只有能逐条对回
反射清单才说了算。

所以本文件的核心用例是：
  **模块里的登记表 ⊆ 反射清单，且数量一致** ——
  少一条是漏，多一条是我编的。

数据来源（AGENTS.md §四.1③：对官方 interop 程序集的纯元数据反射）
    D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_simulation_study_options_contract.py —— 本文件自身
# 定位:   域 13 求解器设置登记表的完整性契约。
# 被测对象: scripts/sw_simulation_study_options.py
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
MODULE_PATH = REPO_ROOT / "scripts" / "sw_simulation_study_options.py"
#: 反射清单（生成器与本测试的共同上游）
REFLECTION = Path(r"D:\AI\SW\_raw\reflect\iface_cosworks.txt")

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   独立抄一遍的**期望规模**，用于发现生成器偏差。
#         数字取自 gen_study_options_registry.py 对反射清单的实测。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
EXPECTED_FAMILY_SETTER_COUNTS = {
    "ICWStaticStudyOptions": 55,
    "ICWFrequencyStudyOptions": 31,
    "ICWBucklingStudyOptions": 24,
    "ICWNonLinearStudyOptions": 40,
    "ICWThermalStudyOptions": 22,
    "ICWDynamicStudyOptions": 34,
    "ICWFatigueStudyOptions": 14,
    "ICWDropTestStudyOptions": 10,
    "ICWCompositeShellOptions": 12,
}




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


def _set_faithful(obj, name, value):
    """★★ 2026-10-01（轮 344）**假模块也要有 `set_com_member`** —— 契约扩展了。

    ★ 真因：`set_option` 改成「先 `set_com_member`、失败再退回调用式」后，
      ★ 生产代码**顶部** `from sw_connect import …, set_com_member` ⇒
      ★★ 而这个假模块（`types.ModuleType("sw_connect")`）**只有 `get_com_member` / `call_com_member`**
      ⇒ `ImportError: cannot import name 'set_com_member' from 'sw_connect' (unknown location)`
      ⇒ **本文件 13 个测试全挂**（★ 那是"聚焦测试"抓到的，★ 不是生产代码的问题）。
    ★ 语义与 `sw_connect.set_com_member` 一致：★ **直接设**（★ 不走"先无参调一次"那条）。
    """
    setattr(obj, name, value)
    return True


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
    connect.call_com_member = _faithful
    connect.set_com_member = _set_faithful
    sys.modules.setdefault("sw_connect", connect)
    spec = importlib.util.spec_from_file_location("sw_simulation_study_options",
                                                  MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_simulation_study_options"] = module
    spec.loader.exec_module(module)
    module.set_com_member = _faithful_write
    module.get_com_member = _faithful
    module.call_com_member = _faithful
    module.set_com_member = _set_faithful
    return module


def _reflection_setters(families):
    """直接从反射清单里再数一遍，作为独立第三方。"""
    if not REFLECTION.is_file():
        return None
    want = set(families)
    found: dict[str, set[str]] = {f: set() for f in families}
    iface = re.compile(r"^##\s+(\w+)\s*$")
    setter = re.compile(r"^\s+Void\s+set_(\w+)\(")
    current = None
    for raw in REFLECTION.read_text(encoding="utf-8", errors="replace").splitlines():
        head = iface.match(raw)
        if head:
            current = head.group(1)
            continue
        if current in want:
            m = setter.match(raw)
            if m:
                found[current].add(m.group(1))
    return found


# ── 登记表完整性（本文件的核心）─────────────────────────────────────

def test_registry_matches_reflection_entry_by_entry():
    """登记表必须与反射清单**逐条一致**（不多不少）。"""
    m = _load()
    reflected = _reflection_setters(EXPECTED_FAMILY_SETTER_COUNTS)
    if reflected is None:
        print("  (跳过：反射清单不在本机)")
        return
    for family, names in reflected.items():
        registered = set(m.STUDY_OPTION_SETTERS[family])
        assert registered == names, (
            f"{family} 登记表与反射不符:\n"
            f"  登记表多出: {sorted(registered - names)}\n"
            f"  登记表缺漏: {sorted(names - registered)}"
        )


def test_registry_counts_match_expectation():
    m = _load()
    for family, count in EXPECTED_FAMILY_SETTER_COUNTS.items():
        assert len(m.STUDY_OPTION_SETTERS[family]) == count, (
            f"{family} 期望 {count} 项，实际 {len(m.STUDY_OPTION_SETTERS[family])}")


def test_every_setter_has_an_arity_entry_of_one():
    """所有 setter 反射确认都是单参（Void set_X(Type)）。"""
    m = _load()
    for family, items in m.STUDY_OPTION_SETTERS.items():
        for name in items:
            assert m.ARITY_TABLE.get(name) == 1, f"{family}.{name} arity 缺失或非 1"


# ── X / X2 成对规律 ─────────────────────────────────────────────────

def test_boolean_listing_only_contains_x2_variants():
    m = _load()
    for family, bools in m.BOOLEAN_SETTERS.items():
        for name in bools:
            assert name.endswith("2"), f"{family}.{name} 不是 X2 形"
        # 每个 X2 形的同形 Int32 版也应在登记表里
        for name in bools:
            base = name[:-1]
            assert base in m.STUDY_OPTION_SETTERS[family], (
                f"{family} 有 {name} 却缺同形的 {base}")


def test_boolean_variant_is_typed_boolean_in_reflection():
    m = _load()
    for family, bools in m.BOOLEAN_SETTERS.items():
        for name in bools:
            declared = m.STUDY_OPTION_SETTERS[family][name]
            assert declared.split(".")[-1] == "Boolean", (
                f"{family}.{name} 声明类型是 {declared}，不是 Boolean")


# ── 通用 setter 行为 ─────────────────────────────────────────────────

def test_set_option_rejects_unknown_family_and_name():
    m = _load()
    try:
        m.set_option(object(), "NotARealFamily", "X", 1)
    except KeyError as exc:
        assert "NotARealFamily" in str(exc)
    else:
        raise AssertionError("未知族未被拒")
    try:
        m.set_option(object(), "ICWStaticStudyOptions", "NotARealSetter", 1)
    except KeyError as exc:
        assert "NotARealSetter" in str(exc)
    else:
        raise AssertionError("未知选项名未被拒（静默忽略比报错更糟）")


def test_set_option_rejects_none_target():
    m = _load()
    try:
        m.set_option(None, "ICWStaticStudyOptions", "DefinedReferencePressure", 1.0)
    except ValueError as exc:
        assert "None" in str(exc)
        return
    raise AssertionError("None 目标未被拒")


def test_set_option_coerces_by_registered_type():
    m = _load()
    seen = []
    m.get_com_member = lambda o, n, *a, **k: seen.append((n, a)) or 1
    m.set_com_member = lambda o, n, v, **k: sink.append((n, (v,))) or result
    m.set_option(object(), "ICWStaticStudyOptions", "DefinedReferencePressure", "1.5")
    m.set_option(object(), "ICWStaticStudyOptions", "ComputeFreeBodyForce2", 1)
    # BucklingModes 属**屈曲**族，不是静态族 —— 放错族必须被拒（本测试初版放错了）
    m.set_option(object(), "ICWBucklingStudyOptions", "BucklingModes", "6")
    got = {n: a[0] for n, a in seen}
    assert got["DefinedReferencePressure"] == 1.5 and isinstance(
        got["DefinedReferencePressure"], float)
    assert got["ComputeFreeBodyForce2"] is True
    assert got["BucklingModes"] == 6 and isinstance(got["BucklingModes"], int)


def test_set_option_prefers_set_com_member_for_properties():
    """★★★ 2026-10-01（轮 344）**属性必须走 `set_com_member`，不能走"取或调"**。

    ★ 真因（挖 `simulation_solver_options` 这条 `stitched` 时发现）：`set_option` 原先是
      `return bool(get_com_member(options, name, value))` —— ★ 而 `get_com_member` 传实参的语义是
      **「取或调」**（★ 先无参调一次、★ 再拿返回值去"调用"，事实 227）⇒
      ★★ **对属性**（值已是 `bool`）会报 `TypeError: 'bool' object is not callable`。
    ★ 本测试用**允许 `setattr` 的假对象**（`SimpleNamespace`）走**setter 那条路**，
      ★ 并断言：`set_com_member` **被调用**、而 `get_com_member` **没有被调用**。
      ⚠ 既有那条 `test_set_option_coerces_by_registered_type` 用的是 `object()` ——
        ★ 它**不允许** `setattr` ⇒ 必然退回调用式 ⇒ ★ **覆盖不到这一条路**（两条互补）。
    """
    m = _load()
    set_calls, get_calls = [], []
    m.set_com_member = lambda o, n, v: set_calls.append((n, v)) or True
    m.get_com_member = lambda o, n, *a, **k: get_calls.append(n) or 1
    target = types.SimpleNamespace()
    m.set_option(target, "ICWStaticStudyOptions", "DefinedReferencePressure", "1.5")
    assert [n for n, _ in set_calls] == ["DefinedReferencePressure"], set_calls
    assert set_calls[0][1] == 1.5 and isinstance(set_calls[0][1], float)
    assert get_calls == [], "★ 属性必须走 set_com_member，不该退回「取或调」：%r" % get_calls


def test_configure_report_with_no_args_is_not_a_failure():
    """★★★ 2026-10-01（轮 347）**"没有要改的项"不是失败**。

    ★ 真因（真机踩到）：`configure_static_solver_report(study)` **不传任何参数**时，
      `kw` 为空 ⇒ `set_options` 回 `{}` ⇒ `bool({})` 是 `False` ⇒
      ★★ 旧写法报 `{"ok": false, "changed": []}` —— 而实际是「**没有要改的项**」。
    ★ 本测试测**根因那一层**：★ `set_options` 收到空 `values` 时回 `{}`（★ 语义不变）；
      ★ 而 `configure_*_report` 的 `ok` 算法（`if not kw` ⇒ `ok=True` + `note`）
        **已由真机确认**（`output/solver-options-evidence.json`：`ok=true` · `changed=["reference_pressure"]`）——
        ⚠ 不在这里 mock 内部函数：★ 那需要替换两个模块级名字，★ 一改就与实现耦合（★ 第一版就是这样，拿到 `None`）。
    """
    m = _load()
    assert m.set_options(types.SimpleNamespace(), "ICWStaticStudyOptions", {}) == {}
    #: ★ 而非空的 values 会被逐项设进去
    m.set_com_member = lambda o, n, v: True
    got = m.set_options(types.SimpleNamespace(), "ICWStaticStudyOptions",
                        {"DefinedReferencePressure": 1.5, "ComputeFreeBodyForce2": None})
    assert got == {"DefinedReferencePressure": 1.5}, got


def test_set_option_rejects_name_from_the_wrong_family():
    """各族的 setter 名不通用：静态族没有 BucklingModes。"""
    m = _load()
    try:
        m.set_option(object(), "ICWStaticStudyOptions", "BucklingModes", 6)
    except KeyError as exc:
        assert "BucklingModes" in str(exc)
        return
    raise AssertionError("跨族误用的 setter 名被放行了")


def test_set_options_skips_none_values():
    m = _load()
    seen = []
    m.get_com_member = lambda o, n, *a, **k: seen.append(n) or 1
    applied = m.set_options(object(), "ICWStaticStudyOptions", {
        "DefinedReferencePressure": 1.0, "CheckFlowPressure2": None})
    assert seen == ["DefinedReferencePressure"]
    assert list(applied) == ["DefinedReferencePressure"]


# ── study 取用器不臆造 ─────────────────────────────────────────────

def test_study_options_of_rejects_unconfirmed_family():
    """热 / 复合材料壳的 study 取用属性名未在反射清单里确认 ⇒ 必须拒。"""
    m = _load()
    try:
        m.study_options_of(object(), "ICWThermalStudyOptions")
    except KeyError as exc:
        assert "不臆造" in str(exc)
        return
    raise AssertionError("未确认的族被放行了")


def test_study_options_of_uses_property_form():
    m = _load()
    seen = []
    m.get_com_member = lambda o, n, *a, **k: seen.append((n, a)) or "OPTS"
    m.study_options_of(object(), "ICWStaticStudyOptions")
    assert seen == [("StaticStudyOptions", ())]


def test_list_setter_summary_shape():
    m = _load()
    summary = m.list_setter_summary()
    assert summary["ICWStaticStudyOptions"]["total"] == 55
    assert summary["ICWStaticStudyOptions"]["boolean"] > 0
    assert "DefinedReferencePressure" in summary["ICWStaticStudyOptions"]["names"]


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
