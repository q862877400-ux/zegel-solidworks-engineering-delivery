"""SolidWorks Simulation COM 调用的**签名契约**测试（不连接 SolidWorks）。

不验证任何运行结果，只验证**调用形态**：参数个数与类型顺序是否与官方签名一致。
铁律 2 下唯一被认可的替代验证方式。

官方签名依据（全部来自纯元数据反射，未实例化任何 COM 对象）：
    D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt
    D:\\AI\\SW\\_raw\\reflect\\enum_cosworks.txt
    由 D:\\AI\\SW\\tools\\reflect-interop.ps1 生成。

与本仓库既有测试一致：**不依赖 pytest**，纯 assert，可直接
``python tests\\test_sw_simulation_signature_contract.py`` 运行。
"""
from __future__ import annotations

import importlib.util
import io
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "sw_simulation.py"

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（AGENTS.md 铁律 1 认可的第三类来源）
# 文件:   tests/test_drawing_signature_contract.py（同一批次产出的姊妹测试）
# 定位:   加载被测模块并把 COM 依赖替换为本地桩。**不连接 SolidWorks**，
#         桩的行为须复刻 scripts/sw_connect.py::get_com_member 的真实语义
#         （可调用则调用，属性则取值），否则断言测不到实参。
# ⚠ 本测试为静态签名契约测试，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   下方「官方签名表」逐项照抄反射清单的 Signature 行，一个参数都不多不少。
#         测试用它们断言实参个数与类型，故错一个名字都跑不过。
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
#: ICWLoadsAndRestraintsManager.AddRestraint(Int32, Object, Object, Int32&)
ADD_RESTRAINT_PARAMS = ("RestraintType", "Entities", "<未查证>", "ErrorCode")

#: ICWLoadsAndRestraintsManager.AddForce(Int32, Object, Object, Int32&)
ADD_FORCE_PARAMS = ("ForceType", "Entities", "<未查证>", "ErrorCode")

#: ICWStudyManager.CreateNewStudy3(String, Int32, Int32, Int32&)
CREATE_NEW_STUDY3_PARAMS = ("Name", "StudyType", "MeshType", "ErrorCode")

#: ICWStudyManager.CreateNewStudy2(String, Int32, Int32&)
CREATE_NEW_STUDY2_PARAMS = ("Name", "StudyType", "ErrorCode")

#: ICWStudyManager.CreateNewStudy(String, Int32, Int32, Int32&)
#: ⚠ 是 **4 参**，与 CreateNewStudy3 同形。本测试初稿误写为 3 参且没断言它，
#:   是被 D:\AI\SW\tools\audit_call_arity.py 的自动 arity 比对抓出来的 ——
#:   「测试自证自洽」挡不住「常量本身就抄错了」。
CREATE_NEW_STUDY_PARAMS = ("Name", "StudyType", "MeshType", "ErrorCode")

#: ICWStudy.CreateMesh(Int32, Double, Double) —— 挂在 ICWStudy，不在 ICWStudy.Mesh
CREATE_MESH_PARAMS = ("<未查证>", "<未查证>", "<未查证>")

#: ICWLoadsAndRestraintsManager.GetLoadsAndRestraints(Int32, Int32&)
GET_LOADS_AND_RESTRAINTS_PARAMS = ("Index", "ErrorCode")




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

def _faithful_get_com_member(obj, name, *args, **kwargs):
    """复刻 scripts/sw_connect.py::get_com_member 的行为。

    真实实现要同时应对「迟到绑定下同一成员可能是属性也可能是方法」
    （见 AGENTS.md §六 事实 4）。纯 getattr 的桩会把方法对象原样返回而不调用，
    导致被测代码拿到函数而不是返回值——故这里必须可调用则调用。
    """
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


def _load_module():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
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
    connect.get_com_member = _faithful_get_com_member
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    connect.set_com_member = _faithful_get_com_member
    connect.call_com_member = _faithful_get_com_member
    # ⚑ 2026-10-01 真机实测后新增的两个 helper，桩必须一并提供 ——
    #   否则被测模块在 `from sw_connect import out_i4, ...` 处直接 ImportError（本轮撞了）。
    #   `out_i4` 是 `Int32&` 出参的**唯一**可用形态（真机裁决五种形态，见 sw_connect.out_i4）。
    connect.out_i4 = lambda value=0: ("<out_i4>", int(value))
    connect.create_empty_dispatch_variant = lambda: "<empty_dispatch>"
    # `_selected_dispatch_array` 用 safe_get_com_member 逐下标取选区实体（取不到即停）。
    connect.safe_get_com_member = lambda obj, name, *a, **k: None
    # 写成员的唯一可行形态是属性赋值（真机 `probe_setter_forms.py`）——
    # 桩里记下来，契约测试才能断言「用的是赋值而不是 set_/put_ 方法名」。
    def _set_com_member(obj, name, value):
        setattr(obj, name, value)
        return value
    connect.set_com_member = _set_com_member
    sys.modules.setdefault("sw_connect", connect)

    spec = importlib.util.spec_from_file_location("sw_simulation_contract", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_simulation_contract"] = module
    spec.loader.exec_module(module)
    return module


class _Recorder:
    """记录 COM 调用的对象，取代真实 Simulation 对象。

    通过 ``_method(name, ret)`` 装一个会记录实参的可调用属性，
    模拟「COM 方法被 get_com_member 调用」的情形。
    """

    def __init__(self, **attrs):
        self.calls = []
        for key, value in attrs.items():
            setattr(self, key, value)

    def _method(self, name, result):
        def _call(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return result
        return _call

    def __getattr__(self, name):
        # 未预置的成员一律当作「返回自身的方法」，避免 getattr 拿到 None。
        def _call(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return self
        return _call


class _Lrm(_Recorder):
    """模拟 ICWStudyManager -> ICWStudy -> LoadsAndRestraintsManager 三层。"""

    def __init__(self, entries):
        self.calls = []
        self._entries = entries
        self.Count = len(entries)

    def GetLoadsAndRestraints(self, index, err):
        self.calls.append(("GetLoadsAndRestraints", (index, err), {}))
        return self._entries[index]

    def AddRestraint(self, *args):
        self.calls.append(("AddRestraint", args, {}))
        return _CallResult()

    def AddForce(self, *args):
        self.calls.append(("AddForce", args, {}))
        return _CallResult()

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return _call_result

        return _call


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试桩）
# 文件:   tests/test_sw_simulation_signature_contract.py —— 本文件自身
# 定位:   `_CallResult` 的零参/带参区分哨兵。
# 起因:   sw_simulation.py::apply_normal_force 补上了官方要求的编辑事务
#         `ForceBeginEdit()` / `ForceEndEdit()`（反射确认**零参**），
#         而本文件的 `_CallResult.__getattr__` 原先返回
#         `_setter(value)` —— 强制要求一个值，零参调用直接 TypeError。
#         故引入哨兵：不给值时记为「方法调用」，给值时记为「属性写入」。
# ⚠ 本哨兵只服务于测试桩，**不代表任何官方签名**。
# ⚠ 本桩为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
#: 传给 _CallResult.__getattr__ 返回函数的哨兵：表示「这次是零参方法调用」
_MISSING = object()


class _CallResult:
    """被返回的载荷对象：setattr 与「调用式写入」都记录到 ``sets`` / ``calls``。

    生产代码用 ``get_com_member(force, "NormalForceOrTorqueValue", 25.0)``
    写值；在真实 COM 里这会命中 setter。纯 Python 对象没有 setter 语义，
    故这里让 ``__getattr__`` 返回一个记录写入的函数，二者效果等价。

    ⚑ ``value`` 改成**可选**：sw_simulation.py 的 apply_normal_force 补上了
    官方要求的编辑事务 ``ForceBeginEdit()`` / ``ForceEndEdit()``，两者
    **反射确认是零参**。原先 ``_setter(value)`` 强制要求一个值 ⇒
    零参调用直接 TypeError。现在零参记进 ``calls``（当方法），
    带值记进 ``sets``（当属性）。
    """

    def __init__(self):
        object.__setattr__(self, "sets", {})
        object.__setattr__(self, "calls", [])

    def __setattr__(self, name, value):
        self.sets[name] = value

    def __getattr__(self, name):
        def _setter(value=_MISSING):
            if value is _MISSING:
                self.calls.append(name)      # 零参 → 方法调用
                return None
            self.sets[name] = value          # 带值 → 属性写入
            return value
        return _setter


def _make_app(studies=(), lrm=None):
    """构造 sw_app -> CosmosWorks -> ActiveDoc -> StudyManager 的假对象链。"""
    manager = _Recorder()
    manager.StudyCount = len(studies)
    manager.ActiveStudy = 0
    study_list = list(studies)
    manager.CreateNewStudy3 = lambda *a: _CallResult()
    manager.CreateNewStudy2 = lambda *a: _CallResult()
    manager.CreateNewStudy = lambda *a: _CallResult()

    def get_study(index):
        return study_list[index]

    manager.GetStudy = get_study

    document = _Recorder(StudyManager=manager)
    cosmos = _Recorder(ActiveDoc=document, VersionNumber="2024.0")
    addin = _Recorder(CosmosWorks=cosmos)
    return _Recorder(GetAddInObject=lambda *a: addin), manager


def _make_study(lrm):
    study = _Recorder(LoadsAndRestraintsManager=lrm, Name="Static-1")
    return study


# ── 入口链 ───────────────────────────────────────────────────────────

def test_entry_chain_uses_camel_case_cosmosworks():
    """官方 getter 是 get_CosmosWorks → COM 属性名 ``CosmosWorks``，不是全大写。"""
    sim = _load_module()
    app, _ = _make_app()

    assert sim.get_cosmosworks(app) is not None
    # 取到的应是 CosmosWorks 层的对象，其 VersionNumber 可回读
    assert sim.get_cosmosworks(app).VersionNumber == "2024.0"


def test_get_addin_object_progid_is_sldworks_simulation():
    sim = _load_module()
    assert sim.SIMULATION_ADDIN_PROGID == "SldWorks.Simulation"


# ── 研究创建 ─────────────────────────────────────────────────────────

def test_create_study_uses_four_argument_entry_first():
    """CreateNewStudy3 是 4 参，命中时不应再降级。"""
    sim = _load_module()
    app, _ = _make_app()

    study, entry, _ = sim.create_static_study(app, "Static-1")
    assert entry == "CreateNewStudy3"
    assert study is not None


def test_create_study_degrades_with_correct_arity():
    """降级入口的参数个数必须与官方一致：3/2 为 3 参，CreateNewStudy 为 3 参。"""
    sim = _load_module()
    app, manager = _make_app()
    manager.CreateNewStudy3 = lambda *a: None          # 强制降级
    seen = {}
    manager.CreateNewStudy2 = lambda *a: (seen.update(v2=a), _CallResult())[1]

    study, entry, _ = sim.create_static_study(app, "Static-1")
    assert entry == "CreateNewStudy2"
    assert len(seen["v2"]) == len(CREATE_NEW_STUDY2_PARAMS) == 3
    assert isinstance(seen["v2"][0], str)
    assert isinstance(seen["v2"][1], int)
    # ⚑ 2026-10-01 真机裁决：第 3 参是 `Int32&` 出参，不是一个裸 int ——
    #   静态反射只说得清「有几个参数」，说不清「出参怎么传」；实测必须包 byref VARIANT。
    #   原断言写的是 `isinstance(seen["v2"][2], int)`，那是**照反射推断**的，
    #   真机跑会抛 `类型不匹配`（本轮实测：传裸 0 必失败）。
    assert _is_byref_i4(seen["v2"][2]), "出参必须包成 byref VARIANT（真机裁决）"


def test_create_study_third_fallback_uses_four_arguments():
    """CreateNewStudy 官方是 4 参（与 3 同形），不是 3 参。

    这条断言是本测试的「反自证」锚点：常量抄错时它必须红。
    """
    sim = _load_module()
    app, manager = _make_app()
    manager.CreateNewStudy3 = lambda *a: None
    manager.CreateNewStudy2 = lambda *a: None
    seen = {}
    manager.CreateNewStudy = lambda *a: (seen.update(v1=a), _CallResult())[1]

    study, entry, _ = sim.create_static_study(app, "Static-1")
    assert entry == "CreateNewStudy"
    assert len(seen["v1"]) == len(CREATE_NEW_STUDY_PARAMS) == 4


def test_create_study_raises_when_all_entries_fail():
    sim = _load_module()
    app, manager = _make_app()
    manager.CreateNewStudy3 = lambda *a: None
    manager.CreateNewStudy2 = lambda *a: None
    manager.CreateNewStudy = lambda *a: None

    try:
        sim.create_static_study(app, "Static-1")
    except RuntimeError:
        return
    raise AssertionError("三个入口都失败时应当抛 RuntimeError")


# ── 载荷与夹具 ───────────────────────────────────────────────────────

def _is_byref_i4(value) -> bool:
    """判断实参是不是 `Int32&` 出参的正确形态。

    ⚑ 必须有这个谓词，因为**单独跑与全量跑的桩不一样**：
    单独跑时 `sw_connect` 是测试装的字面量桩（`("<out_i4>", 0)`），
    全量跑时别的测试已导入真实模块，`_load_module` 里的 `setdefault` 不生效，
    `out_i4()` 返回**真的** `win32com.client.VARIANT(16387, 0)`。
    断言写死任一种都会「单独绿、全量红」—— 故只查语义。

    `VT_BYREF|VT_I4` = 0x4003 = 16387。
    ⚠ pywin32 的 VARIANT **不暴露 `.vt` 属性**（实测 `getattr(v, "vt", None)` 是 None），
      故只能看 repr：它形如 `win32com.client.VARIANT(16387, 0)`。
    """
    if value == ("<out_i4>", 0):            # 桩形态
        return True
    return repr(value).startswith("win32com.client.VARIANT(16387")


def _is_empty_dispatch(value) -> bool:
    """判断实参是不是空 Dispatch 参数的正确形态（`VT_DISPATCH` = 9）。"""
    if value == "<empty_dispatch>":        # 桩形态
        return True
    return repr(value).startswith("win32com.client.VARIANT(9")


def test_add_restraint_passes_four_arguments():
    sim = _load_module()
    lrm = _Lrm([])
    study = _make_study(lrm)

    sim.apply_fixed_restraint(study)
    name, args, _ = lrm.calls[0]
    assert name == "AddRestraint"
    assert len(args) == len(ADD_RESTRAINT_PARAMS) == 4
    assert isinstance(args[0], int)          # Int32 RestraintType
    assert args[1] is None                   # Object Entities（选区已在模型上选好，此处留空）
    # ⚑ 2026-10-01 真机裁决：第 3 参（Object，语义未查证）传裸 None 会抛
    #   `类型不匹配 (arg 3)`，必须传空 Dispatch；而第 2 参传裸 None 是**可以**的
    #   （实测 `None, empty_dispatch()` 通过、`empty_dispatch(), None` 失败）。
    assert _is_empty_dispatch(args[2]), "第 3 参（Object）必须包成空 Dispatch"
    assert _is_byref_i4(args[3]), "第 4 参（Int32& Err）必须包成 byref VARIANT"


def test_add_force_passes_four_arguments_and_sets_magnitude_after():
    """官方 AddForce 只有 4 参；力的大小是**事后**在返回对象上回填的。"""
    sim = _load_module()
    lrm = _Lrm([])
    study = _make_study(lrm)
    result = _CallResult()
    lrm.AddForce = lambda *a: (lrm.calls.append(("AddForce", a, {})), result)[1]

    sim.apply_normal_force(study, 25.0)
    name, args, _ = lrm.calls[0]
    assert name == "AddForce"
    assert len(args) == len(ADD_FORCE_PARAMS) == 4
    assert result.sets["NormalForceOrTorqueValue"] == 25.0
    assert result.sets["Unit"] == 0
    assert result.sets["ForceType"] == 1


def test_add_force_rejects_zero_magnitude():
    sim = _load_module()
    lrm = _Lrm([])
    study = _make_study(lrm)
    try:
        sim.apply_normal_force(study, 0.0)
    except ValueError:
        return
    raise AssertionError("力的大小为 0 时应当抛 ValueError")


# ── 网格与求解 ───────────────────────────────────────────────────────

def test_create_mesh_is_called_on_study_with_three_arguments():
    """``CreateMesh`` 挂在 ICWStudy 上、3 参；不是 ``study.Mesh`` 的方法。

    ⚠ 2026-10-01 更正：第 1 参是 **``NUnits``**（``swsUnit_e``），不是网格类型；
    后两参是 **``DElementSize`` / ``DTolerance``**（毫米）。真参数名取自官方
    VB6 类型库 CHM 的 ``CosmosWorksLib~CWStudy~CreateMesh`` 页 —— 反射只给类型不给名，
    这是本案里唯一的参数名来源。真机证据见 ``scripts/sw_simulation.py`` 的来源块。
    """
    sim = _load_module()
    study = _Recorder()
    study.CreateMesh = study._method("CreateMesh", 0)

    sim.create_mesh(study, units=sim.SWSU_SI, element_size=4.9339, tolerance=0.2467)
    assert study.calls[0][0] == "CreateMesh"
    assert len(study.calls[0][1]) == len(CREATE_MESH_PARAMS) == 3
    # 位置顺序必须与官方签名一致：NUnits 在**第 1 位**
    units, element_size, tolerance = study.calls[0][1]
    assert units == sim.SWSU_SI
    assert element_size == 4.9339
    assert tolerance == 0.2467


def test_run_analysis_is_called_with_zero_arguments():
    """官方 RunAnalysis() 是零参 —— 传任何实参都是错的。"""
    sim = _load_module()
    study = _Recorder()
    study.RunAnalysis = study._method("RunAnalysis", 7)

    assert sim.run_analysis(study) == 7
    assert ("RunAnalysis", (), {}) in study.calls


# ── 枚举取值 ─────────────────────────────────────────────────────────

def test_enum_values_match_reflected_official_values():
    sim = _load_module()

    assert sim.SWS_RESTRAINT_TYPES == {
        "fixed": 0, "immovable": 1, "symmetric": 2, "roller": 3, "hinge": 4,
        "reference_geometry": 5, "flat_face": 6, "cylindrical_faces": 7,
        "spherical_surface": 8, "cyclic_symmetry": 9,
    }
    assert sim.SWS_FORCE_TYPES == {"force_or_moment": 0, "normal": 1, "torque": 2}
    assert sim.SWS_FORCE_UNITS == {"n_or_nm": 0, "lb_or_lbin": 1, "kgf_or_kgfcm": 2}
    assert sim.SWS_MESH_TYPES == {
        "solid": 0, "mid_surface": 1, "surfaces": 2, "mixed": 3, "beam": 4,
    }
    assert sim.SWS_ANALYSIS_STUDY_TYPES["static"] == 0
    assert sim.SWS_ANALYSIS_STUDY_TYPES["topology_static"] == 13
    # 保留值 10/11/12 未收录
    assert 10 not in sim.SWS_ANALYSIS_STUDY_TYPES.values()
    assert 11 not in sim.SWS_ANALYSIS_STUDY_TYPES.values()
    assert 12 not in sim.SWS_ANALYSIS_STUDY_TYPES.values()


# ── 证据回读 ─────────────────────────────────────────────────────────

def test_evidence_uses_two_argument_get_loads_and_restraints():
    """GetLoadsAndRestraints 是双参（末位 by-ref），计数属性在管理器上叫 Count。"""
    sim = _load_module()
    entries = [_Recorder(Name="Fixed-1", Type=1, State=0, EntityCount=2)]
    lrm = _Lrm(entries)
    study = _make_study(lrm)
    study.AnalysisType = 0
    study.MeshType = 0
    study.ConfigurationName = "Default"
    app, _ = _make_app(studies=[study])

    evidence = sim.collect_study_evidence(app)
    assert evidence["study_count"] == 1
    assert len(lrm.calls) == 1
    name, args, _ = lrm.calls[0]
    assert name == "GetLoadsAndRestraints"
    assert len(args) == len(GET_LOADS_AND_RESTRAINTS_PARAMS) == 2
    assert evidence["studies"][0]["loads_and_restraints"][0]["name"] == "Fixed-1"
    assert evidence["cosmos_version"] == "2024.0"


# ── 直接运行 ─────────────────────────────────────────────────────────

def _enable_utf8_stdout() -> None:
    """Windows 控制台默认 GBK，中文测试名会糊；强制 UTF-8 输出。"""
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


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
    _enable_utf8_stdout()
    raise SystemExit(_main())
