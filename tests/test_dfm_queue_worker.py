"""DFM worker 任务回归。"""
from __future__ import annotations

from pathlib import Path

from cad_workbench.queue_worker import process_job, read_job, run_dfm_review_job, write_job


def test_worker_runs_dfm_review_from_ui_configuration(tmp_path: Path) -> None:
    """@brief 没有模型文件时，UI 配置草案也必须形成可追溯待复核报告。"""
    queue_dir = tmp_path / "queue"
    queue_dir.mkdir()
    output_dir = tmp_path / "output"
    job_path = queue_dir / "dfm-job.json"
    job = {
        "schemaVersion": "2.0",
        "id": "dfm-job",
        "runId": "run-dfm",
        "kind": "dfm_review",
        "title": "DFM 复核",
        "detail": "配置草案",
        "status": "queued",
        "progress": 0,
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
        "projectId": "p",
        "conversationId": "c",
        "inputs": [],
        "stage": "intake",
        "capabilitySnapshot": {},
        "assumptions": [],
        "requiredArtifacts": ["dfm_report"],
        "verificationEvidence": [],
        "cwd": str(tmp_path),
        "uiConfig": {
            "outputDir": str(output_dir),
            "process": "CNC",
            "geometry": {"length": 120, "width": 70, "height": 8, "wallThickness": 3},
            "manufacturing": {"process": "CNC", "material": "Al6061", "unit": "mm"},
        },
    }
    write_job(job_path, job)

    result = process_job(job_path, handlers={"dfm_review": run_dfm_review_job})
    saved = read_job(job_path)

    #: ★★★ 2026-10-10 **业主架构指令**（★ 只继承工具 · 方法移出）：
    #:   业主原话：「★ **我想让你继承上游的是工具，只是单纯的工具。**
    #:     ★ **而像齿轮这种东西，在我认知里属于方法 —— 方法错了，工具再多也没有用。**
    #:     ★ **你要从你继承的东西里面把方法筛选出来，把工具留下来，方法全部都删掉。**」✓
    #:   ★★ `dfm_review`（★ DFM 规则库）是**方法** ⇒ 已移出
    #:     ★ `archive/inherited-methods/scripts/dfm_review.py`（★ **只搬不删**）✓
    #:   ★★★ **⇒ 本判据改为断言**队列工具**如实报 `removed`**（★ 不抛异常）——
    #:     ★ 判据**还在**（★ 它守的是「队列工具遇到已移出的方法时行为正确」）✓
    assert result is not None
    assert result["status"] == "removed", result
    assert "archive/inherited-methods" in result["dfmEvidence"]["message"], result
    assert saved["dfmEvidence"]["status"] == "removed", saved["dfmEvidence"]
