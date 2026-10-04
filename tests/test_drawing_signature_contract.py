"""工程图 COM 调用的**签名契约**测试（不连接 SolidWorks）。

本文件不验证任何运行结果，只验证**调用形态**：参数个数与参数类型顺序
是否与官方 API 签名一致。这是 AGENTS.md 铁律 2 认可的唯一替代验证方式
（静态签名比对），因此断言针对「实参个数 / 类型 / 取值来源」，
而不是「模型是否真的建出来了」。

与本仓库既有测试一致：**不依赖 pytest**，纯 assert，可直接
``python tests\\test_drawing_signature_contract.py`` 运行。

官方签名依据：
- ``C:\\swapi\\types\\IDrawingDoc\\CreateDetailViewAt4.md``
- ``C:\\swapi\\types\\IModelDocExtension\\InsertBomTable4.md``
- ``C:\\swapi\\enums\\swDetViewStyle_e.md``
- ``C:\\swapi\\enums\\swDetCircleShowType_e.md``
- ``C:\\swapi\\enums\\swBomType_e.md``
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名 + 枚举定义（非开源项目，无第三方许可）
# 文件:   C:\swapi\types\IDrawingDoc\CreateDetailViewAt4.md
#         C:\swapi\types\IModelDocExtension\InsertBomTable4.md
#         C:\swapi\enums\swDetViewStyle_e.md
#         C:\swapi\enums\swDetCircleShowType_e.md
#         C:\swapi\enums\swBomType_e.md
# 定位:   本文件断言的两个官方参数表 —— DETAIL_VIEW_AT4_PARAMS（12 项）与
#         INSERT_BOM_TABLE4_PARAMS（9 项），逐字照抄官方签名，不增删不改写。
#         枚举期望值同理，取自上述三份 enum md 的「Enumeration Members」表。
# 被测对象: subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py
#           的 add_detail_view 与 insert_bom_table（其自身来源块见该文件）。
# 查证:   python "$env:USERPROFILE\.agents\skills\mech-design\tools\sw_know.py" \
#           member IDrawingDoc CreateDetailViewAt4
#         python "$env:USERPROFILE\.agents\skills\mech-design\tools\sw_know.py" \
#           member IModelDocExtension InsertBomTable4
# ⚠ 本文件为静态签名契约测试，未在本机实测（见 AGENTS.md 铁律 2）
# ⚠ 断言针对「调用形态」而非「建模结果」——铁律 2 下唯一被认可的替代验证。
# ────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = (
    REPO_ROOT
    / "subskills"
    / "solidworks-engineering-drawing"
    / "scripts"
    / "drawing_workflow.py"
)


def _faithful_get_com_member(obj, name, *args, **kwargs):
    """复刻 scripts/sw_connect.py::get_com_member 的行为。

    必须**可调用则调用**、属性则取值。只做 getattr 的桩会把方法对象原样返回
    而不调用，被测代码拿不到返回值，契约断言全部失效。
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


def _load_workflow():
    """静态导入 drawing_workflow，桩掉 COM 依赖（不启动 SolidWorks）。"""
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    sys.modules.setdefault(
        "scripts.sw_preflight",
        types.ModuleType("scripts.sw_preflight"),
    )
    sys.modules["scripts.sw_preflight"].import_com_dependencies = (
        lambda: (None, None, None)
    )
    connect = types.ModuleType("scripts.sw_connect")
    connect.create_empty_dispatch_variant = lambda *a, **k: None
    connect.get_com_member = _faithful_get_com_member
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    connect.set_com_member = _faithful_get_com_member
    connect.call_com_member = _faithful_get_com_member
    sys.modules.setdefault("scripts.sw_connect", connect)

    spec = importlib.util.spec_from_file_location("drawing_workflow_contract", WORKFLOW_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["drawing_workflow_contract"] = module
    spec.loader.exec_module(module)
    # 无条件覆盖模块自己的引用，避免被其它测试先 import 时换成真 COM 调用
    module.get_com_member = _faithful_get_com_member
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    module.set_com_member = _faithful_get_com_member
    module.call_com_member = _faithful_get_com_member
    return module


class _Recorder:
    """记录 COM 调用的对象，取代真实 SolidWorks 文档。"""

    def __init__(self):
        self.calls = []
        self.accessed = []

    def __getattr__(self, name):
        self.accessed.append(name)

        def _call(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return f"<{name}-result>"

        return _call


# ── 官方签名参数表（照抄 C:\swapi，不改写）────────────────────────────────

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（非开源项目，无第三方许可）
# 文件:   C:\swapi\types\IDrawingDoc\CreateDetailViewAt4.md
#         C:\swapi\types\IModelDocExtension\InsertBomTable4.md
# 定位:   下方两张「官方签名参数表」的参数名与顺序，逐项照抄官方 Signature 行：
#           IDrawingDoc.CreateDetailViewAt4          → 12 项
#           IModelDocExtension.InsertBomTable4       → 9 项
#         测试用它们做长度与顺序断言，故一个名字都不能错。
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
#: IDrawingDoc.CreateDetailViewAt4 —— 12 个参数
DETAIL_VIEW_AT4_PARAMS = (
    "X", "Y", "Z", "Style", "Scale1", "Scale2",
    "LabelIn", "Showtype", "FullOutline", "JaggedOutline",
    "NoOutline", "ShapeIntensity",
)

#: IModelDocExtension.InsertBomTable4 —— 9 个参数
INSERT_BOM_TABLE4_PARAMS = (
    "TemplateName", "X", "Y", "BomType", "ConfigurationName",
    "Hidden", "IndentedNumberingType", "DetailedCutList", "DissolvePartLevelRows",
)


# ── CreateDetailViewAt4 ───────────────────────────────────────────────────

def test_add_detail_view_passes_twelve_arguments():
    """官方 CreateDetailViewAt4 是 12 参；7 参会直接失败。"""
    workflow = _load_workflow()
    drawing_model = _Recorder()

    workflow.add_detail_view(drawing_model, 0.1, 0.2)

    assert len(drawing_model.calls) == 1
    name, args, _ = drawing_model.calls[0]
    assert name == "CreateDetailViewAt4"
    assert len(args) == len(DETAIL_VIEW_AT4_PARAMS) == 12


def test_add_detail_view_argument_types_follow_official_order():
    """参数类型顺序须与官方签名逐位对应。"""
    workflow = _load_workflow()
    drawing_model = _Recorder()

    workflow.add_detail_view(drawing_model, 0.1, 0.2, scale=3.0)

    _, args, _ = drawing_model.calls[0]
    x, y, z, style, scale1, scale2, label, show_type = args[:8]
    full, jagged, no_outline, intensity = args[8:12]

    assert (x, y, z) == (0.1, 0.2, 0.0)                    # Double
    assert isinstance(style, int)                          # Int
    assert isinstance(scale1, float) and scale1 == 3.0     # Double Scale1
    assert isinstance(scale2, float) and scale2 == 1.0     # Double Scale2
    assert isinstance(label, str)                          # String LabelIn
    assert isinstance(show_type, int)                      # Int Showtype
    assert isinstance(full, bool)                          # Boolean
    assert isinstance(jagged, bool)                        # Boolean
    assert isinstance(no_outline, bool)                    # Boolean
    assert isinstance(intensity, int)                      # Int


def test_detail_view_enums_match_official_values():
    """枚举取值必须来自 C:\\swapi，不许猜。"""
    workflow = _load_workflow()

    assert workflow.DET_VIEW_STYLES == {
        "standard": 0, "broken": 1, "leader": 2, "noleader": 3, "connected": 4,
    }
    assert workflow.DET_CIRCLE_SHOW_TYPES == {
        "profile": 0, "circle": 1, "dont_show": 2,
    }


# ── InsertBomTable4 ───────────────────────────────────────────────────────

def test_insert_bom_table_routes_through_extension():
    """InsertBomTable4 不在 IDrawingDoc 上，必须经 model.Extension 调用。"""
    workflow = _load_workflow()
    extension = _Recorder()

    class _DocWithExtension(_Recorder):
        Extension = extension

    drawing_model = _DocWithExtension()

    workflow.insert_bom_table(drawing_model, "bom-standard.sldbomtbt", 10, 20)

    # 不得在文档对象上直接取 InsertBomTable4
    assert "InsertBomTable4" not in drawing_model.accessed
    assert len(extension.calls) == 1
    name, args, _ = extension.calls[0]
    assert name == "InsertBomTable4"
    assert len(args) == len(INSERT_BOM_TABLE4_PARAMS) == 9


def test_insert_bom_table_argument_types_follow_official_order():
    workflow = _load_workflow()
    extension = _Recorder()
    drawing_model = types.SimpleNamespace(Extension=extension)

    workflow.insert_bom_table(
        drawing_model,
        "bom.sldbomtbt",
        10,
        20,
        bom_type=workflow.BOM_TYPES["indented"],
        config_name="Cfg-A",
    )

    _, args, _ = extension.calls[0]
    template, x, y, bom_type, config, hidden, numbering, cut_list, dissolve = args

    assert template == "bom.sldbomtbt"                  # String TemplateName
    assert isinstance(x, int) and x == 10               # Int X
    assert isinstance(y, int) and y == 20               # Int Y
    assert isinstance(bom_type, int) and bom_type == 3  # Int BomType
    assert config == "Cfg-A"                            # String ConfigurationName
    assert hidden is False                              # Boolean
    assert isinstance(numbering, int)                   # Int
    assert cut_list is False                            # Boolean
    assert dissolve is False                            # Boolean


def test_bom_type_enum_is_not_intuitive():
    """swBomType_e：1=仅零件、2=仅顶层 —— 与「1=顶层」的说法相反。"""
    workflow = _load_workflow()

    assert workflow.BOM_TYPES == {
        "parts_only": 1, "top_level_only": 2, "indented": 3, "flattened": 4,
    }


def test_insert_bom_table_default_config_is_not_empty():
    """官方 Remarks：空配置名不会回落到 Default，必须显式指定。"""
    workflow = _load_workflow()
    extension = _Recorder()
    drawing_model = types.SimpleNamespace(Extension=extension)

    workflow.insert_bom_table(drawing_model, "bom.sldbomtbt", 0, 0)

    _, args, _ = extension.calls[0]
    assert args[4] == "Default"


def test_insert_bom_table_raises_when_extension_missing():
    workflow = _load_workflow()
    drawing_model = _Recorder()  # 无 Extension -> _safe_member 返回 None

    try:
        workflow.insert_bom_table(drawing_model, "bom.sldbomtbt", 0, 0)
    except AttributeError:
        return
    raise AssertionError("缺少 Extension 时应当抛 AttributeError")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
# 定位:   本节断言所依据的表注解 / 剖视 / 注释视图 / FeatureManager 剖视成员，
#         参数个数逐条照抄反射清单：
#   IDrawingDoc        : InsertTableAnnotation(Double,Double,Int32,Int32,Int32) → 5
#                        InsertTableAnnotation2(Boolean,Double,Double,Int32,String,
#                                            Int32,Int32)                      → 7
#   ITableAnnotation   : Text(Int32,Int32) / RowCount() / ColumnCount() /
#                        RowHidden(Int32,Boolean) / ColumnHidden(Int32,Boolean) /
#                        DeleteRow(Int32) / DeleteColumn(Int32)
#   5 个具体表族        : GeneralTable() / HoleTable() / BendTable() /
#                        WeldmentCutListFeature() / RevisionTableFeature()
#                        GetColumnCustomProperty(Int32) / SetColumnCustomProperty(Int32,String)
#                        Sort(Int32, Boolean)
#   IRevisionTableAnnotation : AddRevision(String) → 1 / DeleteRevision(Int32,Boolean) → 2
#   IAnnotationView    : 全部 0 参属性
#   IModelViewManager  : CreateSectionViewData() → 0 / CreateSectionView(SectionViewData) → 1 /
#                        GetSectionViewData(String) → 1 / RemoveSectionView() → 0
# ⚑ 本节同时是「防复发」锚点: 这批族的代码先后用过 dict+循环、变量名分发、
#   get_com_member(嵌套调用(), "X") 三种写法, 静态审计都归因不到,
#   导致「明明写了代码」却长期显示未触及。测试须锁死「显式成员名」这一形状。
# 覆盖:   后续同级定义
# ⚠ 本节为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────


def _load_drawing_workflow():
    """加载工程图模块，并替换它自己的 get_com_member（不受 import 顺序影响）。"""
    for mod, attrs in (
        ("sw_connect", {"get_com_member": _faithful_get_com_member,
                        "save_document": lambda *a, **k: None}),
        ("sw_document_data", {"set_custom_properties": lambda *a, **k: None}),
        ("sw_part", {"_ensure_sketch_selected": lambda *a, **k: None}),
        ("sw_preflight", {"import_com_dependencies": lambda: (None, None, None)}),
    ):
        module = types.ModuleType(mod)
        for key, value in attrs.items():
            setattr(module, key, value)
        sys.modules.setdefault(mod, module)
    target = (REPO_ROOT / "subskills" / "solidworks-engineering-drawing"
              / "scripts" / "drawing_workflow.py")
    spec = importlib.util.spec_from_file_location("drawing_workflow_tables", target)
    module = importlib.util.module_from_spec(spec)
    sys.modules["drawing_workflow_tables"] = module
    spec.loader.exec_module(module)
    module.get_com_member = _faithful_get_com_member
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    module.set_com_member = _faithful_get_com_member
    module.call_com_member = _faithful_get_com_member
    return module


class _Rec:
    """记录 (成员名, 实参) 的假 COM 对象。

    ``results`` 可指定某些成员的返回值（不记录调用），用于模拟
    「取对象」这类 getter —— 生产代码常对返回值做 int()/索引转换，
    一律返回字符串会让断言崩在转换上，而不是崩在真正要验的地方。
    """

    def __init__(self, **attrs):
        self.calls = []
        self.results = {}
        for key, value in attrs.items():
            setattr(self, key, value)

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            # results 里配了就返回配置值，否则返回 0 —— 0 能安全地被
            # int() 转换、也不会掩盖「这个成员到底被调了没有」这个断言。
            return self.results.get(name, 0)
        return _call


def test_insert_table_annotation_uses_five_arguments():
    dw = _load_drawing_workflow()
    doc = _Rec()
    dw.insert_table_annotation(doc, 0.1, 0.2, 5, 3, 4)
    assert doc.calls == [("InsertTableAnnotation", (0.1, 0.2, 5, 3, 4))]


def test_insert_table_annotation_uses_seven_arguments_with_template():
    dw = _load_drawing_workflow()
    doc = _Rec()
    dw.insert_table_annotation(doc, 0.1, 0.2, 5, 3, 4, template="t.sldtab")
    name, args = doc.calls[0]
    assert name == "InsertTableAnnotation2" and len(args) == 7


def test_table_text_reads_two_indices():
    dw = _load_drawing_workflow()
    table = _Rec()
    table.results["Text"] = "CELL-2-3"
    assert dw.read_table_text(table, 2, 3) == "CELL-2-3"
    assert table.calls[0] == ("Text", (2, 3))


def test_each_table_kind_uses_its_own_official_getter():
    """5 个表族各取各的底层表对象 —— 名字须与反射一致，不能靠一个分发字典。"""
    dw = _load_drawing_workflow()
    for getter, member in (
        (dw.get_general_table, "GeneralTable"),
        (dw.get_hole_table, "HoleTable"),
        (dw.get_bend_table, "BendTable"),
        (dw.get_weldment_cutlist_table, "WeldmentCutListFeature"),
        (dw.get_revision_table_feature, "RevisionTableFeature"),
    ):
        table = _Rec()
        getter(table)
        assert table.calls[0] == (member, ())


def test_custom_property_column_arity():
    dw = _load_drawing_workflow()
    table = _Rec()
    dw.get_table_custom_property_column(table, 2)
    assert table.calls[0] == ("GetColumnCustomProperty", (2,))
    table2 = _Rec()
    dw.set_table_custom_property_column(table2, 2, "Material")
    assert table2.calls[0] == ("SetColumnCustomProperty", (2, "Material"))


def test_add_revision_is_single_string_argument():
    dw = _load_drawing_workflow()
    table = _Rec()
    table.results["AddRevision"] = 5          # 官方返回 Int32 行号
    assert dw.add_revision(table, "C") == 5
    assert table.calls[0] == ("AddRevision", ("C",))


def test_section_style_sets_only_explicit_properties():
    """剖视样式：只设显式给值的，成员名必须是字面量（可被静态审计归因）。"""
    dw = _load_drawing_workflow()
    data = _Rec()
    applied = dw.set_section_style(
        data, show_section_cap=True, zonal_section=True, sectioned_zones=3)
    assert [name for name, _ in data.calls] == [
        "ShowSectionCap", "ZonalSection", "SectionedZones"]
    assert set(applied) == {"ShowSectionCap", "ZonalSection", "SectionedZones"}


def test_section_style_with_no_arguments_sets_nothing():
    dw = _load_drawing_workflow()
    data = _Rec()
    assert dw.set_section_style(data) == {} and data.calls == []


def test_annotation_view_evidence_uses_zero_argument_properties():
    dw = _load_drawing_workflow()
    view = _Rec()
    view.results.update({"IsShown": True, "AnnotationCount": 3, "Always2D": False,
                         "FlatPatternView": False, "UnassignedView": False,
                         "AngleMadeWithViewHorizontal": 30.0})
    evidence = dw.get_annotation_view_evidence(view)
    assert evidence["is_shown"] is True and evidence["annotation_count"] == 3
    assert evidence["angle_deg"] == 30.0
    for name, args in view.calls:
        assert args == (), f"{name} 反射确认是 0 参属性"


def test_feature_manager_section_helpers_use_official_arity():
    """IModelViewManager 的 4 个剖视相关成员，参数个数须与反射一致。"""
    dw = _load_drawing_workflow()
    for build, expected in (
        (lambda m: dw.create_section_view_data(m), ("CreateSectionViewData", ())),
        (lambda m: dw.create_feature_manager_section_view(m, "SD"),
         ("CreateSectionView", ("SD",))),
        (lambda m: dw.get_feature_manager_section_data(m, "A-A"),
         ("GetSectionViewData", ("A-A",))),
        (lambda m: dw.remove_feature_manager_section_view(m), ("RemoveSectionView", ())),
    ):
        manager = _Rec()
        manager.results.update({"CreateSectionViewData": "SDATA",
                                "CreateSectionView": 1, "GetSectionViewData": "SDATA",
                                "RemoveSectionView": 1})
        model = _Rec()
        #: ★ 2026-10-04（接手轮）：原名 `GetModelViewManager` **官方没有** ——
        #: 官方 `IModelDoc2.ModelViewManager`（`kind: property`，`{get;}`）⇒ 无 `Get` 前缀。
        model.results["ModelViewManager"] = manager
        build(model)
        assert manager.calls[-1] == expected


def test_model_view_manager_ui_members_are_listed_not_hidden():
    """刻意不封装的 UI 成员必须列在名单里 —— 不假装它们不存在。"""
    dw = _load_drawing_workflow()
    listed = set(dw.MODEL_VIEW_MANAGER_UI_MEMBERS)
    assert "CreateFeatureMgrControl" in listed
    assert "GetFeatureMgrViewHWnd" in listed
    for member in ("CreateSectionViewData", "CreateSectionView",
                   "GetSectionViewData", "RemoveSectionView"):
        assert member not in listed


# ── 直接运行 ──────────────────────────────────────────────────────────────

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
    print(f"\n{len(tests) - len(failures)}/{len(tests)} 通过")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_main())
