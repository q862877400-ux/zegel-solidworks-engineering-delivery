"""本任务新增/扩展模块的签名契约测试（不连接 SolidWorks）。

覆盖 sw_render_material / sketch_relations / sw_weldment(新增部分) 三块。
前两块此前只有 arity 审计、没有专门的契约测试；焊件扩写同样。
本文件把三块拉到与其余模块（sw_simulation 13/13、sw_surface 14/14）同一标准。

不验证任何运行结果，只验证**调用形态**：参数个数与类型顺序是否与官方签名一致。
铁律 2 下唯一被认可的替代验证方式。

官方签名依据（全部来自纯元数据反射，未实例化任何 COM 对象）：
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt
    D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt
由 D:\\AI\\SW\\tools\\reflect-interop.ps1 对官方 interop DLL 生成。

与本仓库既有测试一致：**不依赖 pytest**，纯 assert。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_extended_modules_contract.py —— 本文件自身
# 定位:   sw_render_material / sketch_relations / sw_weldment 三块的签名契约。
#         断言依据全部是下方两张「官方签名表」，它们照抄反射清单的
#         Signature 行，一个参数都不多不少。
# 被测对象: scripts/sw_render_material.py
#           scripts/sketch_relations.py
#           scripts/sw_weldment.py（仅本任务新增的 5 个函数）
# 覆盖:   全文件 —— 本文件是自包含的测试单元，各测试函数已就地标明对应的
#         官方成员；下方 def 之后不再逐个贴块。
# ⚠ 本文件为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import dataclasses
import importlib.util
import io
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
# 定位:   本文件断言所依据的官方成员与参数个数，逐项照抄。
#   IModelDocExtension : RenderMaterial CreateRenderMaterial(String)          → 1
#                       Boolean       AddRenderMaterial(RenderMaterial, Int32&) → 2
#                       Void          UpdateRenderMaterialsInSceneGraph(Bool) → 1
#                       Int32         GetRenderMaterialsCount()                → 0
#                       Object        GetRenderMaterials()                     → 0
#                       Boolean       DeleteRenderMaterial(Int32, Boolean)     → 2
#   IRenderMaterial    : Ambient / Diffuse / Specular / Roughness /
#                       Transparency / Emission                              → 各 1（属性）
#   ISketchManager     : SketchSegment CreateSpline(Object)                   → 1
#                       SketchSegment CreateSpline2(Object, Boolean)          → 2
#   ISketchSpline      : Object GetPoints() / Int32 GetPointCount() /
#                       Boolean DeletePoint(SketchPoint) / Int32 GetCurveDegree() →
#                       AddTangencyControl(Double,Double,Double)              → 3
#   IHoleStandardsData : Boolean GetHoleStandards(Object&, Object&)            → 2
#                       Boolean GetFastenerTypes(String, Object&, Object&)     → 3
#                       Boolean GetFastenerTableTypes(String, Int32, Object&) → 3
#                       Boolean GetFastenerTable(String, Int32, Int32, Object&) → 4
#   IMassProperty2     : Object GetOverrideOptions()                          → 0
# ⚑ 注意: 上表里 GetSplinePointCount 实际名为 GetPointCount；成员名以
#   反射清单为准，本文件不按印象拼写。
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
OFFICIAL_ARITY = {
    "CreateRenderMaterial": 1,
    "AddRenderMaterial": 2,
    "UpdateRenderMaterialsInSceneGraph": 1,
    "GetRenderMaterialsCount": 0,
    "GetRenderMaterials": 0,
    "DeleteRenderMaterial": 2,
    "GetOverrideOptions": 0,
    "CreateSpline": 1,
    "CreateSpline2": 2,
    "GetPoints": 0,
    "GetPointCount": 0,
    "DeletePoint": 1,
    "GetCurveDegree": 0,
    "GetCurveType": 0,
    "IsRationalCurve": 0,
    "IsStyleSpline": 0,
    "AddTangencyControl": 3,
    "AddCurvatureControl": 3,
    "GetHoleStandards": 2,
    "GetFastenerTypes": 3,
    "GetFastenerTableTypes": 3,
    "GetFastenerTable": 4,
    "SetOverrideOptions": 3,
}

#: IRenderMaterial 上确认为 Double 的属性全集（反射确认只有这 7 个）
CONFIRMED_RENDER_DOUBLES = (
    "Ambient", "Brightness", "Diffuse", "Emission",
    "Roughness", "Specular", "Transparency",
)

#: 曾经被我凭印象写成 Shininess —— 官方**不存在**该成员
HALLUCINATED_MEMBERS = ("Shininess", "MassProperties", "COSMOSWORKS")


def _faithful_get_com_member(obj, name, *args, **kwargs):
    """复刻 scripts/sw_connect.py::get_com_member 的行为。

    必须**可调用则调用**、属性则取值 —— 只做 getattr 的桩会把方法对象
    原样返回而不调用，被测代码拿到的就不是返回值，断言全部失效
    （本文件初版就栽在这里，8 个用例一起红）。
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


class _StubModule(types.ModuleType):
    """任意属性都返回一个可调用的假函数。

    被测模块之间会互相 import（sw_hole_features → sw_part → …），
    逐个列举桩成员很脆（本文件已因此两次栽在 `_select_com_object`、
    `extrude_cut` 上），故改为「问什么给什么」。
    """

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return lambda *a, **k: None


def _load(name: str):
    """加载被测模块，并把它的 get_com_member 换成忠实的桩。

    ⚠ 隔离要点: 不能只靠 ``sys.modules.setdefault`` 装桩 —— 全量 pytest 下
    别的测试可能**已经**导入了真实的 scripts.sw_connect，那时 setdefault
    不会替换，本文件就会用真实 get_com_member 去调真 COM，
    表现为「单独跑全绿、全量跑挂 1 个」（本文件初版就是这样）。
    可靠做法是拿到模块对象后**直接替换它自己持有的引用** ——
    模块里的 `get_com_member` 是它自己的全局名，与谁先被 import 无关。
    """
    for mod, attrs in (
        ("sw_connect", {"get_com_member": _faithful_get_com_member,
                        "save_document": lambda *a, **k: None,
                        # ⚑ 2026-10-01 真机实测新增的两个 helper，桩必须一并提供 ——
                        #   被测模块会 `from sw_connect import out_i4, ...`，缺了就 ImportError。
                        "out_i4": lambda value=0: ("<out_i4>", int(value)),
                        "create_empty_dispatch_variant": lambda: "<empty_dispatch>",
                        "safe_get_com_member": lambda obj, name, *a, **k: None,
                        "set_com_member": lambda obj, name, value: (setattr(obj, name, value), value)[1]}),
        ("sw_document_data", {"set_custom_properties": lambda *a, **k: None}),
        ("sw_preflight", {"import_com_dependencies": lambda: (None, None, None)}),
    ):
        module = _StubModule(mod)
        for key, value in attrs.items():
            setattr(module, key, value)
        sys.modules.setdefault(mod, module)
    sys.modules.setdefault("sw_part", _StubModule("sw_part"))
    if str(REPO_ROOT / "scripts") not in sys.path:
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import importlib
    module = importlib.import_module(name)
    # 关键：无条件覆盖模块自己的引用，不受 import 顺序影响
    module.get_com_member = _faithful_get_com_member
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    module.set_com_member = _faithful_get_com_member
    module.call_com_member = _faithful_get_com_member
    return module


def _enable_utf8_stdout() -> None:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


# ── 枚举表完整性 ─────────────────────────────────────────────────────

def test_constraint_enum_only_contains_members_from_official_enum():
    """草图约束类型表只能出现 swConstraintType_e 里真实存在的项。"""
    m = _load("sketch_relations")
    # 反向确认：本项目查证过程中 swSketchRelation_e 三路确认不存在，
    # 真正的枚举是 swConstraintType_e。表里的键必须是可读的名字而非那个错名。
    assert "swSketchRelation" not in " ".join(m.SKETCH_CONSTRAINT_TYPES)
    for key in ("coincident", "perpendicular", "tangent", "midpoint", "horizontal"):
        assert key in m.SKETCH_CONSTRAINT_TYPES


def test_slot_and_entity_enums_match_official_counts():
    """槽与关系实体的枚举是全量照录，项数必须与官方一致。"""
    m = _load("sketch_relations")
    assert len(m.SKETCH_SLOT_CREATION_TYPES) == 3   # center_line / arc / 3pointarc
    assert len(m.SKETCH_SLOT_LENGTH_TYPES) == 2     # CenterCenter / FullLength
    assert len(m.SKETCH_RELATION_ENTITY_TYPES) == 6  # line/arc/ellipse/hatch/cylinder/dimension


# ── sw_render_material ────────────────────────────────────────────────

def test_render_material_spec_has_no_hallucinated_property():
    """本模块曾凭印象写 Shininess；反射确认不存在，镜面锐度是 Roughness。"""
    m = _load("sw_render_material")
    fields = {f.name for f in dataclasses.fields(m.RenderMaterialSpec)}
    assert "shininess" not in fields
    assert "roughness" in fields
    for member in HALLUCINATED_MEMBERS:
        assert member not in fields


def test_render_material_presets_only_use_confirmed_doubles():
    """预设表里的每个键都必须是反射确认存在的 7 个 Double 属性之一。

    比较**忽略大小写**：官方成员名是 Ambient/Diffuse/…（首字母大写），
    而预设表用小写键（ambient/diffuse/…）。命名大小写不同不是缺陷，
    但键名本身必须在官方属性集合内。
    """
    m = _load("sw_render_material")
    allowed = {name.casefold() for name in CONFIRMED_RENDER_DOUBLES}
    for preset, values in m.RENDER_MATERIAL_PRESETS.items():
        for key in values:
            assert key.casefold() in allowed, f"{preset}.{key} 不是官方属性"
    assert len(m.RENDER_MATERIAL_PRESETS) == 3


def test_create_render_material_sets_exactly_seven_properties():
    """建材质对象时只设那 7 个已确认属性，多一个少一个都要能看出来。

    ★★ 2026-10-01（轮 319）**这个 mock 的形态本身错过一次**：它原本让
    `_Mat.__getattr__` 返回一个**可调用**（`def _set(value)`），也就是假设
    `Ambient` 这类成员是**方法**、`get_com_member(mat, "Ambient", 值)` 会走到
    `mat.Ambient(值)`。而真机证明 `IRenderMaterial.Ambient` 是**属性** ——
    取回来的是 `float`，再去"调用"它 ⇒ `TypeError: 'float' object is not callable`
    （事实 227 的「取或调」）。⇒ 实现已改为 `set_com_member`（属性赋值），
    本 mock 随之改为记录 **`__setattr__`**。
    """
    m = _load("sw_render_material")
    recorded: list[tuple[str, tuple]] = []

    class _Ext:
        def CreateRenderMaterial(self, name):
            recorded.append(("CreateRenderMaterial", (name,)))

            class _Mat:
                def __setattr__(self, attr, value):
                    #: ★ 属性赋值（★ 真机验证的唯一可行形态 —— 见 sw_connect.set_com_member）
                    recorded.append((attr, (value,)))
            return _Mat()

    class _Model:
        Extension = _Ext()

    m.create_render_material(_Model(), "x", m.RenderMaterialSpec(file_name=r"C:\fake\a.p2m"))
    props = [name for name, _ in recorded if name != "CreateRenderMaterial"]
    #: ★★★★ 2026-10-02（轮 373）**契约变更**：`file_name` 成了**必需项** ——
    #:   真机四轮收窄查明「不绑 `.p2m` 的外观不会被收录」（known-facts 287→290）⇒
    #:   实现现在**先设 `FileName`**，所以这张属性表**多这一项、且在最前**。
    assert props == ["FileName", "Ambient", "Diffuse", "Specular", "Roughness",
                     "Transparency", "Emission"]


def test_render_material_spec_rejects_empty_file_name():
    """★★ **负例**（★ 事实 62）：没有 `.p2m` 的外观**必须被拒**，而不是静默建一个不会被收录的。

    ★ 依据：真机实测 —— `FileName` 为空时 `AddDisplayStateSpecificRenderMaterial` **照样回 true**、
      `GetLinkedDisplayStates` **也显示已链接**，★ 而 `GetMaterialIds` 回 `None`、
      `GetRenderMaterialsCount2` 恒 **0** ⇒ ★★ 一个「看起来成功、实际不算数」的外观
      （known-facts 事实 287→290）。
    """
    m = _load("sw_render_material")
    try:
        m.RenderMaterialSpec().validate()
    except ValueError as exc:
        assert "file_name" in str(exc), exc
        return
    raise AssertionError("★ 空 file_name 必须被 validate() 拒掉（否则会静默建出不算数的外观）")


def test_add_render_material_passes_two_arguments():
    """官方 AddRenderMaterial(RenderMaterial, Int32&) 是 2 参。"""
    m = _load("sw_render_material")
    calls: list[tuple[str, tuple]] = []

    class _Ext:
        def AddRenderMaterial(self, mat, count):
            calls.append(("AddRenderMaterial", (mat, count)))
            return True

        def UpdateRenderMaterialsInSceneGraph(self, flag):
            calls.append(("UpdateRenderMaterialsInSceneGraph", (flag,)))

    class _Model:
        Extension = _Ext()

    m.add_render_material(_Model(), "MAT")
    # ⚑ 2026-10-01 真机裁决：第 2 参是 `Int32&` 出参，**不能传裸 0**（必抛类型不匹配），
    #   须包成 byref VARIANT —— 即 sw_connect.out_i4()。原断言写 ("MAT", 0) 是照反射推断的。
    #   ⚠ 只查语义不查字面量：单独跑时 sw_connect 是字面量桩，全量跑时是真模块，
    #   写死任一种都会「单独绿、全量红」。`VT_BYREF|VT_I4` = 16387；
    #   pywin32 的 VARIANT 不暴露 `.vt`（实测是 None），只能看 repr。
    count_arg = calls[0][1][1]
    assert count_arg == ("<out_i4>", 0) or repr(count_arg).startswith("win32com.client.VARIANT(16387"), \
        "Int32& 出参必须是 byref VARIANT（真机裁决）"
    assert calls[1] == ("UpdateRenderMaterialsInSceneGraph", (True,))


def test_mass_property_override_uses_real_member_name():
    """IModelDocExtension.MassProperties 不存在；真实是 GetMassProperties(Double)。"""
    src = (REPO_ROOT / "scripts" / "sw_export.py").read_text(encoding="utf-8")
    assert '"GetMassProperties"' in src
    # 不应再出现凭印象写的成员名
    assert '"MassProperties"' not in src


# ── sketch_relations ─────────────────────────────────────────────────

def test_add_relation_passes_two_arguments():
    """官方 AddRelation(Object Entities, Int32 Type) 是 2 参，且**实体要包成 SAFEARRAY**。

    ⚠⚠⚠ **2026-10-01（轮 161）这条断言被改了，理由要说清**：
    它原来传的是字符串 `"ENTS"` 并断言**原样透传**（`("AddRelation", ("ENTS", 1))`）——
    那是因为它用的是**假对象**，假对象看不见「实参要包 `VARIANT`」这件事。
    ★ 真机实测（`tools/probe_add_relation_forms.py`）：
    ```
      list[0:2]  / tuple(0,1)                      ⇒ com_error 0x80010105 且 GetRelationsCount 不变
      VARIANT(VT_ARRAY | VT_DISPATCH, [实体…])      ⇒ 无错、GetRelationsCount **3 → 4**
    ```
    ⇒ `sketch_relations` 现在把实体序列包成 SAFEARRAY 再传 ⇒ **断言随之改成"包过"**。
    ★ 与已知事实 99/101 **同族**：**假对象测试只能测「逻辑」，测不出「实参形态」**。
    """
    m = _load("sketch_relations")
    calls: list[tuple[str, tuple]] = []

    class _Mgr:
        def AddRelation(self, entities, kind):
            calls.append(("AddRelation", (entities, kind)))
            return "REL"

    class _Sketch:
        RelationManager = _Mgr()

    m.add_relation(_Sketch(), ["E1", "E2"], m.SKETCH_CONSTRAINT_TYPES["coincident"])
    assert len(calls) == 1 and calls[0][0] == "AddRelation", calls
    ents, kind = calls[0][1]
    assert kind == 1, "关系类型要原样透传"
    #: ★ 实体**必须**是包过的 SAFEARRAY（`VARIANT`），不是裸 list
    assert hasattr(ents, "varianttype"), (
        "实体没包成 VARIANT ⇒ 真机会报 com_error 0x80010105（「服务器出现意外情况」）")
    assert list(ents.value) == ["E1", "E2"], ents.value


def test_spline_tangency_passes_three_doubles():
    """官方 AddTangencyControl(Double, Double, Double) 是 3 参。"""
    m = _load("sketch_relations")
    calls: list[tuple[str, tuple]] = []

    class _Spline:
        def AddTangencyControl(self, x, y, z):
            calls.append(("AddTangencyControl", (x, y, z)))
            return "H"

    m.add_spline_tangency(_Spline(), 1, 2, 3)
    assert calls == [("AddTangencyControl", (1.0, 2.0, 3.0))]


def test_hole_standards_wrappers_match_official_arity():
    """4 个查询方法的实参个数必须与官方签名逐个对齐。"""
    m = _load("sw_hole_features")
    calls: list[tuple[str, tuple]] = []

    class _Std:
        def __getattr__(self, name):
            def _call(*args):
                calls.append((name, args))
                return True
            return _call

    std = _Std()
    m.get_hole_standards(std, "A", "B")
    m.get_fastener_types(std, "T", "A", "B")
    m.get_fastener_table_types(std, "T", 1, "C")
    m.get_fastener_table(std, "T", 1, 2, "D")
    got = [(n, len(a)) for n, a in calls]
    assert got == [
        ("GetHoleStandards", OFFICIAL_ARITY["GetHoleStandards"]),
        ("GetFastenerTypes", OFFICIAL_ARITY["GetFastenerTypes"]),
        ("GetFastenerTableTypes", OFFICIAL_ARITY["GetFastenerTableTypes"]),
        ("GetFastenerTable", OFFICIAL_ARITY["GetFastenerTable"]),
    ]


def test_tap_configure_sets_expected_properties():
    """直螺纹设 7 个属性、锥螺纹设 5 个，且都是字面量名字（可被工具归因）。

    ⚠ 记录器必须是**两个独立对象**：初稿按「属性名是否属于锥螺纹」分流，
    结果锥螺纹的 CustomSizing / ThreadClass / ThreadClassOverride
    被记进了直螺纹的列表，断言看着像产品有 bug —— 其实分流规则本身错了。
    """
    m = _load("sw_hole_features")

    def _recorder():
        seen: list[str] = []

        class _El:
            def __getattr__(self, name):
                def _set(value):
                    seen.append(name)
                return _set
        return seen, _El()

    straight, straight_el = _recorder()
    m.configure_straight_tap(straight_el, custom_sizing=1, end_shape=2, equation=3,
                             thread_class=4, thread_class_override=True,
                             drill_point_angle=118.0,
                             drill_point_angle_override=True)
    assert straight == ["CustomSizing", "EndShape", "Equation", "ThreadClass",
                        "ThreadClassOverride", "DrillPointAngle",
                        "DrillPointAngleOverride"]

    tapered, tapered_el = _recorder()
    m.configure_tapered_tap(tapered_el, custom_sizing=1, thread_class=2,
                            thread_class_override=True,
                            end_condition_override=True, use_standard_depth=True)
    assert tapered == ["CustomSizing", "ThreadClass", "ThreadClassOverride",
                      "EndConditionOverride", "UseStandardDepth"]


# ── sw_weldment 新增部分 ─────────────────────────────────────────────

def test_weldment_fm_constants_match_reflected_values():
    """三个 fm 常量取自 swconst 反射，数值不得凭印象。"""
    m = _load("sw_weldment")
    assert m.SW_FM_PROFILE_FEATURE == 65
    assert m.SW_FM_WELD_MEMBER_FEAT == 72
    assert m.SW_FM_MATE_PROFILE_CENTER == 101


def test_weldment_has_no_create_weld_member():
    """被审计器抓出并删除的错误实现不得复活：
    IStructureSystemMemberFeatureData 只有 get_MemberProfile()，没有 setter。"""
    m = _load("sw_weldment")
    assert not hasattr(m, "create_weld_member")


def test_create_profile_center_mate_uses_fm_101_and_five_properties():
    """官方 IProfileCenterMateFeatureData 全部是属性，共 5 个。"""
    m = _load("sw_weldment")
    used: list[int] = []
    props: list[str] = []

    class _Mgr:
        def CreateDefinition(self, kind):
            used.append(kind)

            class _Data:
                def __getattr__(self, name):
                    def _set(value):
                        props.append(name)
                    return _set
            return _Data()

        def CreateFeature(self, data):
            return "FEAT"

    class _Model:
        FeatureManager = _Mgr()

    m.create_profile_center_mate(_Model(), "ENTS", mate_alignment=1,
                                 offset_distance=0.5, flip_dimension=True,
                                 lock_rotation=False)
    assert used == [m.SW_FM_MATE_PROFILE_CENTER]
    assert props == ["EntitiesToMate", "MateAlignment", "OffsetDistance",
                     "FlipDimension", "LockRotation"]


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
    _enable_utf8_stdout()
    raise SystemExit(_main())
