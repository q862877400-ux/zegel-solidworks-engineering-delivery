"""真机验证 `collect_topology_numbers` 的「**无结果**」分支（T-007 形态②）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）+ `specs/001-topology-result-readout`
# 文件:   `scripts/sw_topology.py` 的 `collect_topology_numbers`（被测对象）
# 定位:   做 T-007 验收里「**真机调用两次（有结果 / 无结果）**」的**后者** ——
#         **这个分支不需要求解**（≈0 秒），所以能便宜地真机验。
#         「有结果」那一次由 003 的闭环负责（`output/topology-evidence.json`）。
# 官方签名依据: 反射 `D:\AI\SW\_raw\reflect\iface_cosworks.txt`（`## ICWStudy` / `## ICWResults`）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ **铁律 2**：`CommandInProgress = True` 抑制弹窗；每步有界；收尾恢复。
# ⚠ 不求解、不弹窗、不写模型（只建一个研究再读它）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import win32com.client as win32  # noqa: E402
import pythoncom  # noqa: E402

from sw_topology import (  # noqa: E402
    collect_topology_numbers,
    create_topology_study,
    get_cw_document,
)

T0 = time.time()


def log(msg: str) -> None:
    print("  [%6.2fs] %s" % (time.time() - T0, msg))


def main() -> int:
    pythoncom.CoInitialize()
    sw = win32.GetActiveObject("SldWorks.Application")
    log("已连上 SolidWorks；revision = %s" % sw.RevisionNumber)

    doc = sw.ActiveDoc
    if doc is None:
        log("✗ 没有活动文档 ⇒ 停下（不自己建，避免污染用户文档）")
        return 2
    log("活动文档 = %s" % doc.GetTitle)

    sw.CommandInProgress = True          # ⚠ 铁律 2：抑制模态弹窗
    try:
        cw_doc = get_cw_document(sw)
        log("CWModelDoc = %s" % ("取到" if cw_doc is not None else "**None**"))
        if cw_doc is None:
            return 3

        # ── 建一个**新的**拓扑研究，**不求解** ──────────────────────
        name = "MCP_无结果探针_%d" % int(time.time())
        study = create_topology_study(sw, name, mesh_type=0)
        log("建研究 '%s' ⇒ %s" % (name, "取到" if study is not None else "**None**"))
        if study is None:
            return 4

        # ── 核心：未求解时应报 no_results，**不是**抛异常、**不是**空 dict ──
        got = collect_topology_numbers(study)
        log("collect_topology_numbers ⇒ status=%r" % got.get("status"))
        print()
        print("  ── 返回体 ──")
        for k, v in got.items():
            print("    %-18s %s" % (k, str(v)[:150]))
        print()

        ok = (got.get("status") == "no_results"
              and isinstance(got.get("reason"), str) and got["reason"]
              and isinstance(got.get("source_members"), dict))
        print("  ⇒ T-007 形态②（无结果）：**%s**" % ("✅ 通过" if ok else "✗ 不通过"))
        return 0 if ok else 1
    except Exception as exc:  # noqa: BLE001
        log("✗ 异常: %s: %s" % (type(exc).__name__, str(exc)[:200]))
        return 5
    finally:
        sw.CommandInProgress = False     # ⚠ 收尾必做
        log("已恢复 CommandInProgress = False")
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    raise SystemExit(main())
