"""无 CAD 软件开放格式写入回归。"""
import json
import sys
from pathlib import Path

import ezdxf

from cad_workbench.cad_core_contracts import NeutralCadDocument, NeutralFeature, write_json_contract
from scripts import headless_cad_writer
from scripts.dxf_preview_scene import dxf_to_preview_scene
from scripts.headless_cad_writer import export_headless

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "subskills" / "autocad-automation" / "scripts"))
from acad_headless import inspect_dxf  # noqa: E402


def test_headless_writer_exports_stl_obj_dxf_and_preview_manifest(tmp_path: Path):
    document = NeutralCadDocument(
        documentId="headless_plate",
        title="无头安装板",
        features=[
            NeutralFeature(id="base", type="box", parameters={"length": 120, "width": 70, "height": 8}),
        ],
    )
    input_path = write_json_contract(tmp_path / "headless_plate.cadstudio.json", document)

    result = export_headless(input_path, tmp_path / "out", ["cadstudio", "stl", "obj", "dxf", "svg", "pdf", "png"])

    assert result["status"] == "pass"
    artifacts = {Path(item["path"]).suffix.lower(): Path(item["path"]) for item in result["artifacts"]}
    assert artifacts[".json"].name == "headless_plate.preview.json"
    cadstudio_artifact = next(Path(item["path"]) for item in result["artifacts"] if item["kind"] == "cadstudio")
    assert cadstudio_artifact.name == "headless_plate.cadstudio.json"
    stl_text = artifacts[".stl"].read_text(encoding="utf-8")
    assert stl_text.startswith("solid")
    assert "facet normal" in stl_text
    assert artifacts[".stl"].stat().st_size > 100
    assert "\nf " in artifacts[".obj"].read_text(encoding="utf-8")
    document_dxf = ezdxf.readfile(artifacts[".dxf"])
    assert len(list(document_dxf.modelspace())) >= 4
    assert "<svg" in artifacts[".svg"].read_text(encoding="utf-8")[:500]
    assert artifacts[".pdf"].read_bytes().startswith(b"%PDF")
    assert artifacts[".png"].read_bytes().startswith(b"\x89PNG")
    assert Path(result["previewManifest"]).is_file()
    manifest = json.loads(Path(result["previewManifest"]).read_text(encoding="utf-8"))
    assert "headless_plate.png" in manifest["fallbackImage"]
    assert manifest["previewArtifact"].endswith(".scene.json")
    assert manifest["entities"]
    assert {layer["name"] for layer in manifest["layers"]} >= {"OUTLINE", "TEXT"}
    scene_artifact = next(Path(item["path"]) for item in result["artifacts"] if item["kind"] == "preview_scene")
    assert scene_artifact.is_file()


def test_headless_dxf_contains_manufacturing_layers_dimensions_frame_and_preview_scene(tmp_path: Path):
    """@brief 验证无头二维写入满足可制造图纸的结构证据底线。"""
    document = NeutralCadDocument(
        documentId="gbt_plate",
        title="安装板",
        features=[
            NeutralFeature(id="base", type="box", parameters={"length": 120, "width": 70, "height": 8}),
            NeutralFeature(id="hole-a", type="hole", operation="subtract", parameters={"x": -35, "y": 20, "diameter": 10}),
            NeutralFeature(id="hole-b", type="hole", operation="subtract", parameters={"x": 35, "y": -20, "diameter": 10}),
        ],
        metadata={
            "drawing": {
                "includeFrame": True,
                "sheet": "A3",
                "orientation": "landscape",
                "drawingNumber": "CS-PLATE-001",
                "material": "Q235B",
                "scale": "1:1",
                "designer": "CAD Studio",
                "reviewer": "待人工复核",
            }
        },
    )
    input_path = write_json_contract(tmp_path / "gbt_plate.cadstudio.json", document)

    result = export_headless(input_path, tmp_path / "out", ["cadstudio", "dxf", "svg", "pdf", "png"])

    assert result["status"] == "pass"
    dxf_path = next(Path(item["path"]) for item in result["artifacts"] if item["kind"] == "dxf")
    report = inspect_dxf(dxf_path)
    assert report["evaluation"]["status"] == "pass"
    assert report["trueDimensionEntityCount"] >= 4
    assert report["engineeringChecks"] == {
        "layerGroups": {
            "outline": True,
            "center": True,
            "hidden": False,
            "dimension": True,
            "text": True,
            "frame": True,
        },
        "hasTrueDimensions": True,
        "hasFrameCandidate": True,
        "hasTitleBlockEvidence": True,
        "hasHoleCenters": True,
    }
    assert len(report["holeEvidence"]) == 2
    scene = dxf_to_preview_scene(dxf_path)
    assert scene["kind"] == "dxf-scene"
    assert scene["units"] == "mm"
    assert {layer["name"] for layer in scene["layers"]} >= {"OUTLINE", "HOLES", "CENTER", "DIMENSION", "FRAME", "TITLE"}
    assert sum(entity["kind"] == "dimension" for entity in scene["entities"]) >= 4
    manifest = json.loads(Path(result["previewManifest"]).read_text(encoding="utf-8"))
    assert manifest["sha256"]
    assert manifest["bounds"] == scene["bounds"]
    assert len(manifest["entities"]) == len(scene["entities"])


def test_headless_writer_does_not_fake_mesh_when_occt_is_unavailable(tmp_path: Path, monkeypatch):
    document = NeutralCadDocument(
        documentId="plate_with_holes",
        features=[
            NeutralFeature(id="base", type="box", parameters={"length": 120, "width": 70, "height": 8}),
            NeutralFeature(id="hole-a", type="hole", operation="subtract", parameters={"x": -30, "y": 0, "diameter": 12}),
            NeutralFeature(id="hole-b", type="hole", operation="subtract", parameters={"x": 30, "y": 0, "diameter": 12}),
        ],
    )
    input_path = write_json_contract(tmp_path / "plate_with_holes.cadstudio.json", document)
    original_find_spec = headless_cad_writer.importlib.util.find_spec
    monkeypatch.setattr(
        headless_cad_writer.importlib.util,
        "find_spec",
        lambda name: None if name == "OCP" else original_find_spec(name),
    )

    result = export_headless(input_path, tmp_path / "out", ["cadstudio", "stl", "obj", "dxf", "png"])

    assert result["status"] == "pilot"
    assert result["missingFormats"] == ["obj", "stl"]
    kinds = {item["kind"] for item in result["artifacts"]}
    assert {"cadstudio", "dxf", "png", "preview_manifest"} <= kinds
    assert "stl" not in kinds
    assert "obj" not in kinds
    assert any("部分几何" in item for item in result["limitations"])


def test_headless_writer_blocks_unknown_formats_without_fake_files(tmp_path: Path):
    document = NeutralCadDocument(documentId="future_sat", features=[NeutralFeature(id="base", type="box")])
    input_path = write_json_contract(tmp_path / "future_sat.cadstudio.json", document)

    result = export_headless(input_path, tmp_path / "out", ["sat"])

    assert result["status"] == "blocked"
    assert not result["artifacts"]
    assert "sat" in result["limitations"][0]


def test_headless_writer_rejects_invalid_neutral_document(tmp_path: Path):
    input_path = tmp_path / "invalid.cadstudio.json"
    input_path.write_text('{"features": []}', encoding="utf-8")

    result = export_headless(input_path, tmp_path / "out", ["dxf"])

    assert result["status"] == "failed"
    assert result["stage"] == "preflight"
    assert result["error_code"] == "invalid_neutral_document"
    assert result["missingFormats"] == ["dxf"]


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   `tests/test_headless_cad_writer.py` → 本轮新增的两个用例
# 定位:   补 `capabilities.yaml` 的 `autocad_headless_preview` 里 **limitations 点名**
#         而**既有测试没覆盖**的两条承诺：
#         · 「**不能读取或写入 DWG**」—— 既有测试只覆盖了通用未知格式 `sat`；
#         · 「**只读**」—— 输入端不该被写操作反噬。
# ⚠ 依据 `AGENTS.md §一 A5`（行为要与承诺对齐）与 §一 A4（`verified` 要有运行证据）：
#   验收要**逐条覆盖承诺**，不是"测过一个未知格式就算"。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────
def test_headless_writer_refuses_dwg_and_does_not_fake_a_file(tmp_path: Path):
    """★★ **limitations 点名的那条**：**不能读取或写入 DWG**。

    ⚠ `capabilities.yaml` 的 `autocad_headless_preview.limitations` 原文：
      「…**不能读取或写入 DWG**，不能替代 AutoCAD 原生 DWG/PDF 复核」。
      而既有测试只覆盖了 `sat`（通用"未知格式"）—— **没测点名承诺的 `dwg`**。
    ★ 验收要**逐条覆盖承诺**，不是"测过一个未知格式就算"。

    ⚠ 判据比"返回 blocked"更强：**磁盘上不许出现任何 dwg 文件** ——
      一个"假装写了 DWG"的产物会让下游以为拿到了 DWG ⇒ 那是**诚信**问题（不只是格式问题）。
    """
    from cad_workbench.cad_core_contracts import NeutralCadDocument, NeutralFeature, write_json_contract
    from scripts.headless_cad_writer import export_headless

    document = NeutralCadDocument(
        documentId="dwg_probe",
        title="拒绝 DWG 探针",
        features=[NeutralFeature(id="base", type="box", parameters={"length": 10, "width": 10, "height": 10})],
    )
    input_path = write_json_contract(tmp_path / "dwg_probe.cadstudio.json", document)
    out_dir = tmp_path / "out"

    result = export_headless(input_path, out_dir, ["dwg"])

    assert result["status"] == "blocked", "申请 dwg 必须返回 blocked，实际 %r" % result["status"]
    assert not result["artifacts"], "blocked 时不许有任何产物，实际 %r" % result["artifacts"]
    assert "dwg" in str(result.get("limitations") or ""), "limitations 必须点名 dwg"
    stray = list(out_dir.rglob("*.dwg")) if out_dir.exists() else []
    assert not stray, "**磁盘上出现了 dwg 文件**：%r —— 那是「假装写了 DWG」" % stray


def test_headless_writer_does_not_modify_the_input_document(tmp_path: Path):
    """★ **只读**承诺：写产物不得改动输入的中性文档。

    ⚠ limitations 原文「**只读 DXF**；…」—— 输入端不该被写操作反噬。
    """
    import hashlib

    from cad_workbench.cad_core_contracts import NeutralCadDocument, NeutralFeature, write_json_contract
    from scripts.headless_cad_writer import export_headless

    document = NeutralCadDocument(
        documentId="readonly_probe",
        features=[NeutralFeature(id="base", type="box", parameters={"length": 20, "width": 20, "height": 5})],
    )
    input_path = write_json_contract(tmp_path / "ro.cadstudio.json", document)
    before = hashlib.sha256(input_path.read_bytes()).hexdigest()
    before_mtime = input_path.stat().st_mtime

    export_headless(input_path, tmp_path / "out", ["png", "svg", "pdf"])

    assert hashlib.sha256(input_path.read_bytes()).hexdigest() == before, "输入文档被改动了"
    assert input_path.stat().st_mtime == before_mtime, "输入文档 mtime 变了"
