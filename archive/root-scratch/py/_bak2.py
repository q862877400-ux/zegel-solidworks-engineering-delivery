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
    # 忠实还原 scripts/sw_connect.py 的 get_com_member 行为（对纯 Python 对象
    # 等价于 getattr），否则 _safe_member 恒为 None，契约断言就测不到东西。
    connect.get_com_member = lambda obj, name, *a, **k: getattr(obj, name)
    sys.modules.setdefault("scripts.sw_connect", connect)

    spec = importlib.util.spec_from_file_location("drawing_workflow_contract", WORKFLOW_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
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
