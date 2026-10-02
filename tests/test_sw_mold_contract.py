"""模具域签名契约测试 —— 断言每个 COM 调用与**官方反射**逐参数对齐。

本文件的存在意义有一半是**针对来源的**：来源 `Eduardof0nt` 对模具域的两个方法
**两个名字都是错的**（`InsertPartingLines` / `InsertShutOffSurfaces`，官方真名见下）。
所以这里的每条断言都照 `iface_sldworks.txt` 抄，**不照来源抄**。

官方签名（真源 `D:\\AI\\SW\\_raw\\topo-sldworks\\iface_sldworks.txt`）：
    Feature InsertMoldPartingLine(Boolean)
    Feature InsertMoldPartingSurface(Int32, Boolean, Boolean, Double, Double, Int32, Double, Boolean)
    Feature InsertMoldShutOffSurface()
    Feature InsertMoldCoreCavitySolids(Double, Double, Boolean, Double)
    Int32   MoldDraftAnalysis(Double, Int32, Object, Int32)
    Void    MoldUndercutDetect(Int32, Int32, Boolean, Double, Double, Double)

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（契约测试）+ SolidWorks 官方 API 签名（纯元数据反射）
# 文件:   tests/test_sw_mold_contract.py
# 定位:   AGENTS.md 铁律 4「签名三源互证」与验收 A5 的落地：把官方 arity 与参数类型
#         写成断言，来源的名字一旦被误搬进来就会红。
# 官方签名依据: 见上（逐条核过 iface_sldworks.txt）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 纯静态桩测试，**不连真机**（真机验证属 capabilities.yaml 的 evidence，本文件不管）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "sw_mold.py"

#: 官方 arity（照反射逐条抄；改这些数等于改契约）
PARTING_LINE_PARAMS = ("DraftAnalysis",)                                        # 1
PARTING_SURFACE_PARAMS = ("type", "flip", "trim", "dist", "angle", "opt",
                          "tol", "alt")                                         # 8
SHUT_OFF_PARAMS = ()                                                            # 0
CORE_CAVITY_PARAMS = ("scale", "thickness", "flip", "offset")                   # 4
DRAFT_ANALYSIS_PARAMS = ("angle", "type", "colors", "opt")                      # 4
UNDERCUT_PARAMS = ("dir", "opt", "hidden", "a", "b", "c")                       # 6


class _Recorder:
    """记录 COM 调用：``.calls`` 收 (成员名, 实参元组)。"""

    def set(self, name, ret=None):
        def _fn(*args):
            self.calls.append((name, args))
            return ret
        setattr(self, name, _fn)
        return self

    def __init__(self, **ret_values):
        self.calls = []
        for k, v in ret_values.items():
            self.set(k, v)


class _Feat:
    def __init__(self, name):
        self.Name = name


def _load_module():
    """加载被测模块，并把 sw_connect 换成忠实桩。"""
    connect = types.ModuleType("sw_connect")

    def _get(obj, name, *args, **kwargs):
        member = getattr(obj, name)
        if callable(member) and args:
            return member(*args)
        if callable(member) and not args:
            # 属性也可能被可调用对象伪装；本模块的成员都是方法，故无参即调用
            return member()
        return member

    connect.get_com_member = _get
    connect.call_com_member = _get
    connect.set_com_member = lambda obj, name, value: (setattr(obj, name, value), value)[1]
    sys.modules.setdefault("sw_connect", connect)

    spec = importlib.util.spec_from_file_location("sw_mold_contract", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_mold_contract"] = module
    spec.loader.exec_module(module)
    return module


class _Model:
    """最小模型桩：只有 FeatureManager。"""

    def __init__(self, fm, **props):
        self.FeatureManager = fm
        for k, v in props.items():
            setattr(self, k, v)


# ── ① 来源名字必须**不存在**于本模块（防误搬）────────────────────────
def test_source_wrong_names_are_not_used():
    """来源写的 `InsertPartingLines` / `InsertShutOffSurfaces` 不得出现在本模块。

    这是本文件的**反自证锚点**：若有人照来源抄，这条会红。
    """
    src = MODULE_PATH.read_text(encoding="utf-8")
    # docstring 里会提到这两个错名（作为更正说明），故只在**代码行**里查
    code_lines = [l for l in src.splitlines()
                  if not l.strip().startswith("#") and '"""' not in l]
    code = "\n".join(code_lines)
    # 允许出现在字符串字面量里的更正说明；不允许作为 get_com_member 的成员名
    assert '"InsertPartingLines"' not in code, "不得把来源的错名当成成员名使用"
    assert '"InsertShutOffSurfaces"' not in code, "不得把来源的错名当成成员名使用"


# ── ② 每个函数的官方 arity 与位置 ────────────────────────────────
def test_insert_parting_line_passes_one_boolean():
    m = _load_module()
    fm = _Recorder().set("InsertMoldPartingLine", _Feat("PartingLine1"))
    m.insert_parting_line(_Model(fm), draft_analysis=True)
    name, args = fm.calls[0]
    assert name == "InsertMoldPartingLine"
    assert len(args) == len(PARTING_LINE_PARAMS) == 1
    assert args[0] is True


def test_insert_parting_surface_passes_eight_args_in_official_order():
    m = _load_module()
    fm = _Recorder().set("InsertMoldPartingSurface", _Feat("PartingSurface1"))
    m.insert_parting_surface(_Model(fm), surface_type=2, flip=True, use_trim=True,
                             distance=1.5, angle=30.0, option=1,
                             tolerance=0.01, alternate=True)
    name, args = fm.calls[0]
    assert name == "InsertMoldPartingSurface"
    assert len(args) == len(PARTING_SURFACE_PARAMS) == 8
    # 位置严格照官方：Int32, Boolean, Boolean, Double, Double, Int32, Double, Boolean
    assert args[0] == 2 and isinstance(args[0], int)
    assert args[1] is True and args[2] is True
    assert args[3] == 1.5 and args[4] == 30.0
    assert args[5] == 1 and isinstance(args[5], int)
    assert args[6] == 0.01
    assert args[7] is True


def test_insert_shut_off_surface_takes_no_args():
    m = _load_module()
    fm = _Recorder().set("InsertMoldShutOffSurface", _Feat("ShutOff1"))
    m.insert_shut_off_surface(_Model(fm))
    name, args = fm.calls[0]
    assert name == "InsertMoldShutOffSurface"
    assert len(args) == len(SHUT_OFF_PARAMS) == 0


def test_insert_core_cavity_solids_passes_four_args():
    m = _load_module()
    fm = _Recorder().set("InsertMoldCoreCavitySolids", _Feat("CoreCavity1"))
    m.insert_core_cavity_solids(_Model(fm), scale=1.02, thickness=25.0,
                                flip=True, offset=0.5)
    name, args = fm.calls[0]
    assert name == "InsertMoldCoreCavitySolids"
    assert len(args) == len(CORE_CAVITY_PARAMS) == 4
    assert args[0] == 1.02 and args[1] == 25.0 and args[2] is True and args[3] == 0.5


def test_mold_draft_analysis_takes_four_args_from_the_model_document():
    """4 参从 **`IModelDoc2`** 取（**不是** `IFeatureManager`），且官方返回 **`Void`**。

    ⚠⚠⚠ **2026-10-01（轮 178）本条被改写过，因为原断言钉着**两条错的语义****：
    ```
    ① **对象错**：原实现 `fm = get_com_member(model, "FeatureManager")` 再取
       `MoldDraftAnalysis` —— 真机实测 `IFeatureManager.MoldDraftAnalysis`
       ⇒ **AttributeError: <unknown>.MoldDraftAnalysis**。
       ★ 官方两源一致：它在 **`IModelDoc2`** 上
         · 反射 `Void MoldDraftAnalysis(Double, Int32, Object, Int32)`（IModelDoc2 段）
         · `C:/swapi/types/IModelDoc2/MoldDraftAnalysis.md`
    ② **返回类型写反**：原断言 `got == 7`（"原样返回 Int32 返回码"）——
       ⚠ 官方是 **`Void`** ⇒ **根本没有返回码** ⇒ "不得自行判定成败"那句**无从谈起**。
    ```
    ★ 这两条是 `scripts/check_member_owner_interface.py` **静态抓出**（轮 177）并**真机核对**过的
    （反射 / 真机否定 / 真机肯定，三条独立证据）。
    """
    m = _load_module()
    fm = _Recorder().set("MoldDraftAnalysis", None)     #: ★ 放错地方的那个：**必须不被调用**
    calls: list = []
    model = _Model(fm)
    #: ⚠⚠⚠ **必须设成"可调用的属性"**（轮 178 我第一版设成了 `_Recorder` **实例** ⇒ 不可调用
    #: ⇒ `get_com_member(model, "MoldDraftAnalysis", *args)` 调用失败、**静默返回成员本身**
    #: ⇒ 我当时据此得出了「**从不调用**」的**错误结论**。
    #: ★ `get_com_member` 的语义是「**取或调**」：**有实参 ⇒ 一定调用**（见它的 docstring）。）
    model.MoldDraftAnalysis = lambda *a: (calls.append(a), None)[1]
    got = m.mold_draft_analysis(model, draft_angle_deg=3.0)
    assert not fm.calls, "★ 不许再从 IFeatureManager 取（真机 AttributeError）"
    assert calls, "★ 必须真的**调用** `model.MoldDraftAnalysis`（有实参 ⇒ 一定调用）"
    args = calls[0]
    assert len(args) == len(DRAFT_ANALYSIS_PARAMS) == 4
    assert args[0] == 3.0
    #: ★ 官方是 `Void` ⇒ **没有返回码**。
    #: ⚠ 真机实测（轮 178）：pywin32 对 `Void` 调用往往回 **`True`** ⇒ 本函数**原样返回**它。
    #: ⇒ 断言「**不是**被当成成败的整数返回码」——`True`/`None` 都可接受，**数字不行**。
    assert got is None or got is True, (
        "官方 `Void` ⇒ 只可能是 None 或 COM 的通用回执 True；"
        "若回整数，说明又被当成了「返回码」（那是**错的**语义）——实际 %r" % (got,))


def test_mold_undercut_detect_passes_six_args_and_returns_none():
    """@brief 6 参**按官方参数名与顺序**透传。

    ⚠⚠ **2026-10-01（轮 167）改名，理由**：官方 md 的参数名是
    `ColUndercut / ColBase / BCoordInput / Dx / Dy / Dz`，而旧代码用
    `direction / option / include_hidden / a / b / c` ——
    ★ **旧名把第 3 参（`BCoordInput`，bool）当成了 `include_hidden`** ⇒
    传 `False` 等于「**不启用坐标输入**」⇒ 退回「用模型已定义方向」⇒
    在**未定义方向**的零件上**弹模态框并卡住会话**（轮 167 的根因）。
    """
    m = _load_module()
    fm = _Recorder().set("MoldUndercutDetect", None)
    got = m.mold_undercut_detect(_Model(fm), col_undercut=1, col_base=2,
                                 b_coord_input=True, dx=1.0, dy=2.0, dz=3.0)
    name, args = fm.calls[0]
    assert name == "MoldUndercutDetect"
    assert len(args) == len(UNDERCUT_PARAMS) == 6
    assert args[0] == 1 and args[1] == 2 and args[2] is True
    assert (args[3], args[4], args[5]) == (1.0, 2.0, 3.0)
    assert got is None, "官方是 Void ⇒ 不得假装能拿到检测结果"


def test_mold_undercut_detect_rejects_zero_direction():
    """@brief ★★★ **零向量方向必须当场拒**（否则会弹模态框卡住会话）。

    依据：官方 md 说 `BCoordInput=True` 时 `Dx/Dy/Dz` 是**拉拔方向**；
    零向量等于「没给方向」⇒ SolidWorks 退回「用模型已定义方向」那条路
    ⇒ 在未定义方向的零件上**弹「此拔模方向尚未定义。」**（轮 167 实测）。
    """
    import pytest
    m = _load_module()
    fm = _Recorder().set("MoldUndercutDetect", None)
    with pytest.raises(ValueError):
        m.mold_undercut_detect(_Model(fm), b_coord_input=True, dx=0.0, dy=0.0, dz=0.0)
    assert not fm.calls, "零向量时**不许**发出调用（要在发之前拒）"


# ── ③ 失败路径不静默 ────────────────────────────────────────────
def test_none_return_raises_with_actionable_message():
    m = _load_module()
    fm = _Recorder().set("InsertMoldPartingLine", None)
    try:
        m.insert_parting_line(_Model(fm))
    except RuntimeError as exc:
        assert "拔模方向参考" in str(exc), "错误信息要指向最可能的原因"
    else:
        raise AssertionError("返回 None 时必须抛 RuntimeError，不得静默")


def test_evidence_returns_none_for_missing_members():
    """证据采集是**读取入口**，缺成员返回 None 而不抛异常。"""
    m = _load_module()
    fm = _Recorder().set("GetPartingLinesCount", 2)

    class _M:
        FeatureManager = fm
    got = m.mold_evidence(_M())
    assert got["counts"]["parting_lines"] == 2
    assert got["counts"]["core_surfaces"] is None
    assert got["parting_type"] is None

def test_mold_evidence_does_not_fake_counts_when_members_are_absent():
    """@brief ★★★ `mold_evidence` 在成员**缺席**时必须返回 `None`，**不许假装读到 0**。

    ⚠⚠⚠ **2026-10-01（轮 172）真机查出的盲区**：本文件的假对象**恰好有**那些成员
    （`GetPartingLinesCount` …），所以 17 处契约测试**全绿**；而**真机上这些成员
    **根本不在 `IFeatureManager` / `IModelDoc2` 上****（在 `I*FeatureData` 上，★ 事实 36 那一族）
    ⇒ `mold_evidence()` 在真机上**永远全 None**。
    ★ 本测试用**没有那些成员**的假对象，钉住「**读到就是读到、读不到就是 `None`**」——
    也就是**不许把"没读到"粉饰成 0**。
    """
    m = _load_module()

    class _BareFM:
        """★ 一个**故意没有**模具成员的 FeatureManager（真机就是这个样子）。"""

    class _BareModel:
        FeatureManager = _BareFM()

        def GetTitle(self):      #: 让任何通用访问都不至于炸
            return "bare"

    got = m.mold_evidence(_BareModel())
    assert isinstance(got, dict), got
    counts = got.get("counts") or {}
    assert set(counts) == {"parting_lines", "parting_surfaces",
                           "cavity_surfaces", "core_surfaces"}, counts
    for k, v in counts.items():
        assert v is None, "★ 成员缺席时必须 None，**不许**变成 0（%s=%r）" % (k, v)
    assert got.get("parting_type") is None
    assert got.get("core_cavity_split") is None
