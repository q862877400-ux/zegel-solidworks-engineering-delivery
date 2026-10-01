"""追加 `autocad_headless_preview` 的承诺覆盖测试（独立文件便于安全追加）。"""
from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path(r"C:\swprojects\sw-skill-fork\tests\test_headless_cad_writer.py")

BLOCK = '''

def test_headless_writer_refuses_dwg_and_does_not_fake_a_file(tmp_path: Path):
    """★★ **limitations 点名的那条**：**不能读取或写入 DWG**。

    ⚠ `capabilities.yaml` 的 `autocad_headless_preview.limitations` 原文：
      「…**不能读取或写入 DWG**，不能替代 AutoCAD 原生 DWG/PDF 复核」。
      而既有测试只覆盖了 `sat`（通用"未知格式"）—— **没测点名承诺的 `dwg`**。
    ★ 验收要**逐条覆盖承诺**，不是"测过一个未知格式就算"。

    ⚠ 判据比"返回 blocked"更强：**磁盘上不许出现任何 dwg 文件** ——
      一个"假装写了 DWG"的产物会让下游以为拿到了 DWG ⇒ 那是**诚信**问题（不只是格式问题）。
    """
    from apps.desktop.cad_workbench.cad_core_contracts import NeutralCadDocument, NeutralFeature, write_json_contract
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

    from apps.desktop.cad_workbench.cad_core_contracts import NeutralCadDocument, NeutralFeature, write_json_contract
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
'''

text = TARGET.read_text(encoding="utf-8")
if "test_headless_writer_refuses_dwg" in text:
    print("  已追加过")
else:
    TARGET.write_text(text + BLOCK, encoding="utf-8")
    print("  OK 已追加（%d -> %d 行）" % (len(text.splitlines()),
                                        len((text + BLOCK).splitlines())))
sys.stdout.reconfigure(encoding="utf-8")
