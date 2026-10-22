"""交付物版本比较与可审计重新生成计划。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/delivery_compare.py
# 定位:   交付物版本比较与可审计重新生成计划。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

#: ★ 2026-10-22（仓库统一化）：`_sha256` 原在本文件与 `sw_delivery.py` 各有一份（逐字相
#: 同）
#:   ⇒ 收敛到单一实现 `scripts/sw_file_digest.py` ✓
try:
    from .sw_file_digest import sha256_file as _sha256
except ImportError:
    from sw_file_digest import sha256_file as _sha256


def snapshot_files(paths: Iterable[str | Path]) -> dict[str, dict[str, Any]]:
    """@brief 生成文件版本快照；目录和不存在路径不会伪装成交付物。"""
    snapshot: dict[str, dict[str, Any]] = {}
    for raw_path in paths:
        path = Path(raw_path).expanduser().resolve()
        key = str(path)
        if not path.is_file():
            snapshot[key] = {"path": key, "exists": False}
            continue
        stat = path.stat()
        snapshot[key] = {
            "path": key,
            "exists": True,
            "name": path.name,
            "extension": path.suffix.lower(),
            "size_bytes": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
            "sha256": _sha256(path),
        }
    return snapshot


def compare_snapshots(
    previous: dict[str, dict[str, Any]],
    current: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """@brief 比较两轮交付文件并返回 added/removed/changed/unchanged。"""
    rows = []
    for path in sorted(set(previous) | set(current)):
        before = previous.get(path, {"path": path, "exists": False})
        after = current.get(path, {"path": path, "exists": False})
        if not before.get("exists") and after.get("exists"):
            status = "added"
        elif before.get("exists") and not after.get("exists"):
            status = "removed"
        elif before.get("sha256") != after.get("sha256"):
            status = "changed"
        else:
            status = "unchanged"
        rows.append({"path": path, "status": status, "before": before, "after": after})
    counts = {
        status: sum(row["status"] == status for row in rows)
        for status in ("added", "removed", "changed", "unchanged")
    }
    return {"schemaVersion": "1.0", "counts": counts, "items": rows}


def build_regeneration_request(
    *,
    project_id: str,
    source_job_id: str,
    failed_stage: str,
    capabilities: list[str],
    assumptions: list[str] | None = None,
    changed_inputs: list[str] | None = None,
) -> dict[str, Any]:
    """@brief 创建不覆盖旧产物的局部重新生成请求。"""
    if not project_id.strip() or not source_job_id.strip() or not failed_stage.strip():
        raise ValueError("project_id、source_job_id、failed_stage 不能为空")
    return {
        "schemaVersion": "1.0",
        "type": "regeneration_request",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "projectId": project_id,
        "sourceJobId": source_job_id,
        "failedStage": failed_stage,
        "capabilitySnapshot": sorted(
            set(str(item) for item in capabilities if str(item).strip())
        ),
        "assumptions": list(assumptions or []),
        "changedInputs": list(changed_inputs or []),
        "policy": {
            "preservePreviousArtifacts": True,
            "overwrite": False,
            "requireReview": True,
            "scope": "failed_stage_and_downstream",
        },
    }
