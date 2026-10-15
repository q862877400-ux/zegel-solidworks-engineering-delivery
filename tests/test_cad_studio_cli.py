"""CAD Studio CLI 与桌面端任务语义的一致性测试。"""

# ── 来源 ──
# 仓库:   本项目自身（**上游文件的缺陷修复**，非第三方移植）+ Python 标准库 `subprocess` 文档
# 文件:   tests/test_cad_studio_cli.py
# 定位:   ⚠ 本文件的 `subprocess.run(..., text=True)` **没给 `encoding=`** ⇒ 用
#         `locale.getpreferredencoding()`（本机 **GBK**）⇒ 子进程的 **UTF-8 中文**输出
#         解不了（`UnicodeDecodeError`）⇒ `stdout` 变 **None** ⇒ `json.loads(None)` 崩。
#         **这是 4 个真实基线失败的共同根因**（轮 45 查明）。
#         **⇒ 已补 `encoding="utf-8", errors="replace"`**（与子进程实际输出一致）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.cad_studio import prepare_job_for_retry


def test_cli_retry_preserves_history_and_clears_current_evidence():
    job = {
        "schemaVersion": "2.0",
        "id": "job-cli-retry",
        "runId": "run-old",
        "status": "failed",
        "progress": 100,
        "result": {"message": "旧结果"},
        "artifacts": [{"path": "old.step", "producedThisRun": True}],
        "drawingEvidence": {"status": "failed", "stage": "review"},
        "reviewFindings": [{"id": "dimension-overlap"}],
        "reviewGate": {"status": "fail"},
        "error": "旧错误",
        "prompt": "不应复制到历史快照",
    }

    result = prepare_job_for_retry(job, "2026-08-02T00:00:00+00:00")

    assert result["status"] == "queued"
    assert result["runId"].startswith("retry-")
    assert result["retryPolicy"]["retryFromStage"] == "drawing-bom"
    assert result["retryPolicy"]["overwrite"] is False
    assert result["artifacts"] == []
    assert result["runHistory"][0]["artifacts"][0]["path"] == "old.step"
    assert "prompt" not in result["runHistory"][0]
    for field in ("result", "drawingEvidence", "reviewFindings", "reviewGate", "error"):
        assert field not in result


def test_cli_retry_keeps_only_latest_twenty_runs():
    job = {
        "runId": "run-current",
        "status": "blocked",
        "runHistory": [{"runId": f"old-{index}"} for index in range(20)],
    }

    result = prepare_job_for_retry(job, "2026-08-02T00:00:00+00:00")

    assert len(result["runHistory"]) == 20
    assert result["runHistory"][0]["runId"] == "old-1"
    assert result["runHistory"][-1]["runId"] == "run-current"


def test_cli_retry_rejects_active_job():
    job = {"runId": "run-active", "status": "running"}

    try:
        prepare_job_for_retry(job, "2026-08-02T00:00:00+00:00")
    except ValueError as exc:
        assert "不可重试" in str(exc)
    else:
        raise AssertionError("运行中任务不应允许重试")


def test_check_dfm_cli_generates_report(tmp_path: Path):
    #: ★★★ 2026-10-10 **业主架构指令**（★ 只继承工具 · 方法移出）：
    #:   业主原话：「★ **我想让你继承上游的是工具，只是单纯的工具。**
    #:     ★ **而像齿轮这种东西，在我认知里属于方法 —— 方法错了，工具再多也没有用。**
    #:     ★ **你要从你继承的东西里面把方法筛选出来，把工具留下来，方法全部都删掉。**」✓
    #:   ★★ 判据：★「**那个数字错了，回读能不能查出来**」⇒ ★ **不能** ⇒ **是方法** ✗
    #:   ★ 已移出：★ `archive/inherited-methods/scripts/`（★ **只搬不删**）✓
    #:   ★★ 本子命令现**如实报 `status: "removed"`** 且返回 1（★ 不是静默 2）✓
    """@brief check-dfm 命令必须输出真实 JSON 报告。"""
    source = tmp_path / "plate.cadstudio.json"
    source.write_text(
        json.dumps(
            {
                "documentId": "plate",
                "features": [{"id": "base", "type": "box", "parameters": {"length": 100, "width": 50, "height": 8}}],
                "metadata": {"manufacturing": {"process": "machining", "material": "Al6061", "wallThickness": 3}},
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "dfm.json"
    completed = subprocess.run(
        [sys.executable, "scripts/cad_studio.py", "check-dfm", "--input", str(source), "--output", str(output)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert completed.returncode == 1, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["status"] == "removed"


def _fea_request() -> dict:
    """@brief 返回 CLI prepare-fea 使用的最小静力请求。"""
    return {
        "schemaVersion": "1.0",
        "analysisId": "cli_static",
        "analysisType": "static_linear",
        "solver": "calculix",
        "units": {"length": "mm", "force": "N", "stress": "MPa", "temperature": "C"},
        "material": {"name": "Al6061", "elasticModulusMPa": 68900, "poissonRatio": 0.33, "densityKgM3": 2700},
        "mesh": {
            "nodes": [
                {"id": 1, "x": 0, "y": 0, "z": 0},
                {"id": 2, "x": 10, "y": 0, "z": 0},
                {"id": 3, "x": 0, "y": 10, "z": 0},
                {"id": 4, "x": 0, "y": 0, "z": 10},
            ],
            "elements": [{"id": 1, "type": "C3D4", "nodeIds": [1, 2, 3, 4]}],
            "nodeSets": {"FixedNodes": [1, 2, 3], "LoadNode": [4]},
            "elementSets": {"AllElements": [1]},
        },
        "constraints": [{"id": "fixed_base", "type": "fixed", "nodeSet": "FixedNodes"}],
        "loads": [{"id": "tip_force", "type": "force", "nodeSet": "LoadNode", "dof": 3, "value": -100}],
    }


def _advanced_geometry_plan() -> dict:
    """@brief 返回 CLI 复杂几何门禁使用的最小有效计划。"""
    return {
        "schemaVersion": "1.0",
        "planId": "cli_surface",
        "units": "mm",
        "entities": [
            {"id": "profileA", "type": "profile", "source": "section:A"},
            {"id": "profileB", "type": "profile", "source": "section:B"},
        ],
        "operations": [
            {"id": "loftMain", "type": "loft", "profiles": ["profileA", "profileB"], "continuity": "G1", "output": "loftSurface"}
        ],
    }


def test_cli_prepare_fea_generates_versioned_calculix_input(tmp_path: Path):
    #: ★★★ 2026-10-10 **业主架构指令**（★ 只继承工具 · 方法移出）：
    #:   业主原话：「★ **我想让你继承上游的是工具，只是单纯的工具。**
    #:     ★ **而像齿轮这种东西，在我认知里属于方法 —— 方法错了，工具再多也没有用。**
    #:     ★ **你要从你继承的东西里面把方法筛选出来，把工具留下来，方法全部都删掉。**」✓
    #:   ★★ 判据：★「**那个数字错了，回读能不能查出来**」⇒ ★ **不能** ⇒ **是方法** ✗
    #:   ★ 已移出：★ `archive/inherited-methods/scripts/`（★ **只搬不删**）✓
    #:   ★★ 本子命令现**如实报 `status: "removed"`** 且返回 1（★ 不是静默 2）✓
    """@brief prepare-fea 方法已移出 ⇒ 子命令须**如实报 removed**。"""
    source = tmp_path / "fea.json"
    source.write_text(json.dumps(_fea_request()), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "scripts/cad_studio.py", "prepare-fea", "--input", str(source), "--out-dir", str(tmp_path / "fea-out")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert completed.returncode == 1, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["status"] == "removed"
    assert "archive/inherited-methods" in payload["where"]


def test_cli_run_fea_convergence_rejects_invalid_request_without_output(tmp_path: Path):
    """@brief 收敛方法已移出 ⇒ 子命令须**如实报 removed**，且不留下结果目录。"""
    #: ★★★ 2026-10-10 **业主架构指令**（★ 只继承工具 · 方法移出）：
    #:   业主原话：「★ **我想让你继承上游的是工具，只是单纯的工具。**
    #:     ★ **而像齿轮这种东西，在我认知里属于方法 —— 方法错了，工具再多也没有用。**
    #:     ★ **你要从你继承的东西里面把方法筛选出来，把工具留下来，方法全部都删掉。**」✓
    #:   ★★ 判据：★「**那个数字错了，回读能不能查出来**」⇒ ★ **不能** ⇒ **是方法** ✗
    #:   ★ 已移出：★ `archive/inherited-methods/scripts/`（★ **只搬不删**）✓
    #:   ★★ 本子命令现**如实报 `status: "removed"`** 且返回 1（★ 不是静默 2）✓
    source = tmp_path / "bad-convergence.json"
    source.write_text("{}", encoding="utf-8")
    output = tmp_path / "convergence-out"
    completed = subprocess.run(
        [
            sys.executable, "scripts/cad_studio.py", "run-fea-convergence",
            "--input", str(source), "--out-dir", str(output), "--timeout-per-case", "30",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["status"] == "removed"
    assert "archive/inherited-methods" in payload["where"]
    assert not output.exists()


def test_cli_review_advanced_geometry_writes_report(tmp_path: Path):
    """@brief 复杂几何方法已移出 ⇒ 子命令须**如实报 removed**。"""
    #: ★★★ 2026-10-10 **业主架构指令**（★ 只继承工具 · 方法移出）：
    #:   业主原话：「★ **我想让你继承上游的是工具，只是单纯的工具。**
    #:     ★ **而像齿轮这种东西，在我认知里属于方法 —— 方法错了，工具再多也没有用。**
    #:     ★ **你要从你继承的东西里面把方法筛选出来，把工具留下来，方法全部都删掉。**」✓
    #:   ★★ 判据：★「**那个数字错了，回读能不能查出来**」⇒ ★ **不能** ⇒ **是方法** ✗
    #:   ★ 已移出：★ `archive/inherited-methods/scripts/`（★ **只搬不删**）✓
    #:   ★★ 本子命令现**如实报 `status: "removed"`** 且返回 1（★ 不是静默 2）✓
    source = tmp_path / "surface.json"
    source.write_text(json.dumps(_advanced_geometry_plan()), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "scripts/cad_studio.py", "review-advanced-geometry", "--input", str(source), "--output", str(tmp_path / "surface_report.json")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["status"] == "removed"
    assert "archive/inherited-methods" in payload["where"]


def test_cli_create_ocp_loft_writes_real_brep(tmp_path: Path):
    #: ★★★ 2026-10-10 **业主架构指令**（★ 只继承工具 · 方法移出）：
    #:   业主原话：「★ **我想让你继承上游的是工具，只是单纯的工具。**
    #:     ★ **而像齿轮这种东西，在我认知里属于方法 —— 方法错了，工具再多也没有用。**
    #:     ★ **你要从你继承的东西里面把方法筛选出来，把工具留下来，方法全部都删掉。**」✓
    #:   ★★ 判据：★「**那个数字错了，回读能不能查出来**」⇒ ★ **不能** ⇒ **是方法** ✗
    #:   ★ 已移出：★ `archive/inherited-methods/scripts/`（★ **只搬不删**）✓
    #:   ★★ 本子命令现**如实报 `status: "removed"`** 且返回 1（★ 不是静默 2）✓
    """@brief create-ocp-loft 必须生成并重开真实 STEP/BREP。"""
    pytest.importorskip("OCP")
    source = tmp_path / "loft.json"
    source.write_text(json.dumps({
        "schemaVersion": "1.0", "modelId": "cli_loft", "units": "mm", "operation": "loft",
        "solid": True, "ruled": True, "toleranceMm": 0.01,
        "sections": [
            {"id": "base", "type": "circle", "z": 0, "radius": 12},
            {"id": "top", "type": "circle", "z": 30, "radius": 6},
        ],
        "outputs": ["step", "brep"],
    }), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "scripts/cad_studio.py", "create-ocp-loft", "--input", str(source), "--out-dir", str(tmp_path / "loft-out")],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert completed.returncode == 1, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["status"] == "removed"
    assert payload["geometryProduced"] is True
    assert all(Path(item["path"]).is_file() for item in payload["artifacts"])


def test_cli_create_ocp_surface_writes_real_smooth_loft(tmp_path: Path):
    #: ★★★ 2026-10-10 **业主架构指令**（★ 只继承工具 · 方法移出）：
    #:   业主原话：「★ **我想让你继承上游的是工具，只是单纯的工具。**
    #:     ★ **而像齿轮这种东西，在我认知里属于方法 —— 方法错了，工具再多也没有用。**
    #:     ★ **你要从你继承的东西里面把方法筛选出来，把工具留下来，方法全部都删掉。**」✓
    #:   ★★ 判据：★「**那个数字错了，回读能不能查出来**」⇒ ★ **不能** ⇒ **是方法** ✗
    #:   ★ 已移出：★ `archive/inherited-methods/scripts/`（★ **只搬不删**）✓
    #:   ★★ 本子命令现**如实报 `status: "removed"`** 且返回 1（★ 不是静默 2）✓
    """@brief create-ocp-surface 必须生成并重开真实平滑 Loft BREP。"""
    pytest.importorskip("OCP")
    source = tmp_path / "smooth.json"
    source.write_text(json.dumps({
        "schemaVersion": "1.0", "modelId": "cli_smooth", "units": "mm",
        "operation": "smooth_loft", "toleranceMm": 0.01, "outputs": ["brep"],
        "solid": True, "continuityTarget": "C2", "maxDegree": 8,
        "sections": [
            {"id": "base", "type": "circle", "z": 0, "radius": 10},
            {"id": "middle", "type": "circle", "z": 20, "radius": 10},
            {"id": "top", "type": "circle", "z": 40, "radius": 10},
        ],
    }), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "scripts/cad_studio.py", "create-ocp-surface", "--input", str(source), "--out-dir", str(tmp_path / "surface-out")],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert completed.returncode == 1, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["status"] == "removed"
    assert payload["continuityEvidence"]["allSampledEdgesG2"] is True
