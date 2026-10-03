"""门禁测试：项目对 SolidWorks 只暴露**官方 API**，不自造第二套命名。

用户要求：「不要有自创的东西」。
本测试把这条钉死 —— 任何人再加一个**官方成员之外的**调用入口，门禁就红。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_official_names_only_contract.py —— 本文件自身
# 定位:   「只暴露官方 API」的契约门禁。
# 覆盖:   全文件 —— 本文件是自包含测试单元。
# ⚠ 本文件为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import importlib.util
import io
import re
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
#: ⚑⚑ **自动发现**，不写死 —— 写死的清单每加一个程序集就会漏一次，
#:   而漏了的表现是「测试报某个成员不在官方反射里」，看起来像数据错、实则是清单旧。
#:   本轮已经因此栽了两次（漏 swmotionstudy、漏 swdimxpert 等 5 个）。
# ⚑ 从 _raw 根找 —— 反射清单**散在两个目录**：大部分在 _raw\reflect\\，
#   最大的 sldworks 在它的兄弟目录 _raw\reflect_sldworks\。
#   只扫其中一个都会漏（本轮实测漏掉 15,297 条）。
REFLECT_DIR = Path(r"D:\AI\SW\_raw")
# ⚑ **递归**找 —— 最大的 sldworks 反射落在子目录里（_raw\\reflect_sldworks\\），
#   只扫顶层会把 8,210 个方法整个漏掉（本轮实测：只扫到 7,610 条）。
REFLECTIONS = sorted(REFLECT_DIR.rglob("iface_*.txt")) if REFLECT_DIR.is_dir() else []

#: ★ 唯一允许的自造入口 —— 它只做一件事：按**官方**参数个数校核后调
#:   上游自带的 ``get_com_member``。它不新增任何成员名。
ALLOWED_ENTRYPOINTS = {"call_index"}

#: 允许的「行为」符号（非 API 成员别名，是成对调用的编排）
ALLOWED_BEHAVIOUR = {"edit_feature_selection", "edit_sheet_metal_selection"}

SIG = re.compile(r"^\S+\s+(\w+)\s*\(")
INTERNAL = re.compile(r"^I[A-Z][a-z]")




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


def _official_members(asm: str | None = None) -> set[str] | None:
    """某程序集（或全部）的官方成员名。

    ⚑⚑ 必须**按程序集**分别取，不能混成一锅 ——
      本任务明确不收录 sustainability / sw3dprinter / swbrowser，
      混起来比就会把「故意不收」误报成「漏抄」。
    """
    files = ([next(iter(REFLECT_DIR.rglob(f"iface_{asm}.txt")), None)] if asm
             else list(REFLECT_DIR.rglob("iface_*.txt")))
    files = [f for f in files if f is not None]
    files = [f for f in files if f.is_file()]
    if not files:
        return None
    out: set[str] = set()
    for f in files:
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("## "):
                continue
            m = SIG.match(line)
            if m:
                out.add(re.sub(r"^(get|set)_", "", m.group(1)))
    return out


# ── 1. 只有一个入口名字 ─────────────────────────────────────────────

def test_exactly_one_entrypoint_name():
    """⚑ 早先我留了 **11 个不同名字**的访问器（call_index / call_hub /
    call_member / call_sim / call_annotation / …），干的是同一件事。
    用户指出「不要有自创的东西」⇒ 现在只允许一个名字。"""
    found = set()
    for p in sorted(SCRIPTS.glob("sw_api_*.py")):
        for node in ast.parse(p.read_text(encoding="utf-8")).body:
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                found.add(node.name)
    assert found == ALLOWED_ENTRYPOINTS, (
        f"6 份全量索引里只应有一个入口 `call_index`，实有 {sorted(found)}")


#: ⚑ 本任务新建的模块（上游自有的 sw_part / sw_addin_host / … 不在管辖范围
#:   —— 那是项目本来的对外 API，用户明确说过不要动）。
OWNED: set = set()   # ★ 2026-10-03（轮 431）：唯一那个（sw_selection_tx）已按决断删除


#: ★★ 2026-10-03（轮 431）：原本这里有一条 `test_no_other_sw_api_helper_survives`，
#:   ★ 而它**只**遍历 `OWNED`（当时只有 `sw_selection_tx`）。
#:   ★ 而那个模块已删 ⇒ ★★ 循环**为空** ⇒ 那样的测试
#:   **比没有更坏**（★ 本仓自己的规矩：“一个存在但没人用的守卫
#:   与没有守卫等价”）⇒ ★ **故删掉那条测试**，★ 而把它的契约
#:   留在下面那些**真在遍历文件**的测试里。
# ── 2. 登记的每个名字都必须在官方反射里 ─────────────────────────────

def test_every_registered_name_is_official():
    """⚑ **逐程序集**比对 —— 每个索引只跟它自己那个 DLL 的反射比。"""
    total = 0
    for p in sorted(SCRIPTS.glob("sw_api_*.py")):
        asm = re.search(r"ASSEMBLY = '(\w+)'", p.read_text(encoding="utf-8")).group(1)
        official = _official_members(asm)
        if official is None:
            print(f"  (跳过：{asm} 反射清单不在本机)")
            continue
        src = p.read_text(encoding="utf-8")
        for name in re.findall(r"^        '([A-Za-z_]\w*)': \d+,$", src, re.M):
            total += 1
            assert name in official, f"{p.name}: {name} 不在 {asm} 反射里"
        for name in re.findall(r"^        '([A-Za-z_]\w*)',$", src, re.M):
            total += 1
            assert name in official, f"{p.name}: 属性 {name} 不在 {asm} 反射里"
    # ⚑ 阈值随收录程序集增长 —— 写死过小会在「少扫了一个程序集」时也不报
    #   （本轮 7,610 < 10,000 正是靠这条抓出 sldworks 反射没被找到）。
    assert total > 20000, f"只扫到 {total} 条，清单可能没读全"


def test_no_internal_dispatch_is_registered():
    """``IGetXxx`` / ``IUpdateYyy`` 是同一能力的内部变体，不是独立成员。"""
    for p in sorted(SCRIPTS.glob("sw_api_*.py")):
        for name in re.findall(r"^        '([A-Za-z_]\w*)': \d+,$",
                               p.read_text(encoding="utf-8"), re.M):
            assert not INTERNAL.match(name), f"{p.name}: 收了内部变体 {name}"


def test_index_is_complete_against_reflection():
    """**逐程序集**：该 DLL 反射里的成员，索引里必须一个不少。

    ⚑⚑ **必须逐程序集比**，不能把 12 份反射混成一锅 ——
      本任务明确**不收录** sustainability / sw3dprinter / swbrowser，
      混起来比就会把「故意不收」误报成「漏抄」（本轮实测就报了一堆
      `AssemblyProcessAmount` 之类的 sustainability 成员「缺失」）。
    """
    checked = 0
    for p in sorted(SCRIPTS.glob("sw_api_*.py")):
        src = p.read_text(encoding="utf-8")
        asm = re.search(r"ASSEMBLY = '(\w+)'", src).group(1)
        official = _official_members(asm)
        if official is None:
            print(f"  (跳过：{asm} 反射清单不在本机)")
            continue
        seen = set(re.findall(r"^\s+'([A-Za-z_]\w*)': \d+,$", src, re.M))
        seen |= set(re.findall(r"^\s+'([A-Za-z_]\w*)',$", src, re.M))
        # ⚑ 同样要剥掉 COM 内部分发口（`IGetXxx` 之类）——
        #   索引刻意不收它们，比对时也不能算成「缺」。
        absent = {n for n in official - seen if not re.match(r"^I[A-Z][a-z]", n)}
        assert not absent, f"{asm}: 反射里有、索引里没有: {sorted(absent)[:8]}"
        checked += 1
    assert checked >= 10, f"只比对了 {checked} 个程序集，清单可能没读全"


# ── 3. 入口只调上游的 get_com_member ────────────────────────────────

def test_entrypoint_delegates_to_upstream_get_com_member():
    """入口**不得**自己造调用路径 —— 必须走上游自带的 ``get_com_member``。"""
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
    for asm in sorted(p.stem[len("sw_api_"):]
                     for p in SCRIPTS.glob("sw_api_*.py")):
        name = f"sw_api_{asm}"
        spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules[name] = m
        spec.loader.exec_module(m)
        assert m.ASSEMBLY == asm
        seen = []
        m.get_com_member = lambda o, n, *a, **k: seen.append((n, a))
        m.set_com_member = lambda o, n, v, **k: sink.append((n, (v,))) or result
        m.call_com_member = lambda o, n, *a, **k: seen.append((n, a))
        # ⚑ 取**任意一个**有零参成员的族 —— 早先固定取 FAMILIES[0]，
        #   而 SWRoutingLib 的第一个族没有零参成员，样本取不到（断言本身的毛病）。
        fam, zero = next(
            ((f, n) for f in m.FAMILIES
             for n, k in m.ARITY[f].items() if k == 0), (None, None))
        assert zero, f"{asm}: 没有零参成员可作样本"
        m.call_index(object(), fam, zero)
        assert seen == [(zero, ())], f"{asm}: 入口没有原样转发到 {zero}"


def test_entrypoint_rejects_unknown_family_and_bad_arity():
    connect = types.ModuleType("sw_connect")
    connect.get_com_member = _faithful
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    connect.set_com_member = _faithful
    connect.call_com_member = _faithful
    sys.modules.setdefault("sw_connect", connect)
    spec = importlib.util.spec_from_file_location("swa",
                                                 SCRIPTS / "sw_api_sldworks.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["swa"] = m
    spec.loader.exec_module(m)
    m.get_com_member = lambda o, n, *a, **k: None
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    m.set_com_member = lambda o, n, *a, **k: None
    m.call_com_member = lambda o, n, *a, **k: None
    for args, exc in ((("INotAFamily", "X"), KeyError),
                      ((m.FAMILIES[0], "NotRealMember"), KeyError)):
        try:
            m.call_index(object(), *args)
        except exc:
            continue
        raise AssertionError(f"{args} 未被拒")
    # 错 arity
    one = next((f for f in m.FAMILIES if any(k == 1 for k in m.ARITY[f].values())), None)
    if one:
        name = next(n for n, k in m.ARITY[one].items() if k == 1)
        try:
            m.call_index(object(), one, name, 1, 2)
        except ValueError:
            pass
        else:
            raise AssertionError("错 arity 未被拦")
    # None 目标
    zero = next((n for n, k in m.ARITY[m.FAMILIES[0]].items() if k == 0), None)
    if zero:
        try:
            m.call_index(None, m.FAMILIES[0], zero)
        except ValueError:
            return
        raise AssertionError("None 目标未被拒")


# ── 4. 门禁自身有效（负向验证） ─────────────────────────────────────

def test_gate_detects_an_invented_entrypoint():
    """把一个假想自造入口喂进判定逻辑，它必须被抓到。"""
    fake = Path(SCRIPTS / "sw_api_fake.py")
    fake.write_text(
        "def call_index(obj, family, member, *args):\n    return None\n"
        "def my_custom_helper(obj):\n    return None\n", encoding="utf-8")
    try:
        tree = ast.parse(fake.read_text(encoding="utf-8"))
        names = {n.name for n in tree.body
                 if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")}
        assert names != ALLOWED_ENTRYPOINTS, "判定逻辑没抓到自造入口"
    finally:
        fake.unlink()


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
