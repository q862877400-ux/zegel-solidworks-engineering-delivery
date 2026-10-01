"""给 `capabilities.yaml` 的 29 条加 `source` 标记（**按硬证据，不编造**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（清单收敛：补 A2 的「能力级出处」）
# 文件:   C:\\swprojects\\sw-skill-fork\\capabilities.yaml
#         依据：`D:\\AI\\SW\\AGENTS.md §一 A2`（两层 provenance）与 §四.3（来源标注制）
# 定位:   2026-10-01（轮 58）把 A2 的**能力级出处**落地。
#         ⚠ **此前状态**：schema **没有** `source`/`origin` 字段 ⇒
#           29 条里**无法区分**「并入来的」与「本项目自研的」（例：`requirements_planning`
#           的 backend 是 `local-agent`，显然是自研，却**没有地方这么说**）。
#
#   **证据来源（两级，从弱到强）**：
#     ① `tools/propose_capability_sources.py` 的**关键词提案**（只打印、不写文件）
#        ⇒ `upstream=11 / mixed=7 / original=3 / undetermined=8`
#     ② **我逐条按能力语义点名候选模块，再用硬证据 `git cat-file -e origin/main:<path>` 判定**
#        —— 这是**事实 49** 的方法，**比关键词硬**。
#        ⚠ 8 条 `undetermined` 我**全部**用 ② 复核过（见 `SOURCE_EVIDENCE` 注释）。
#
#   **⚠ 为什么必须写「undetermined」而不是硬填**：
#     `THIRD-PARTY-NOTICES.md` 自己写着「把**未并入**的东西写成**已并入**，是**归属造假**，
#     比遗漏更严重」⇒ 宁可留 `undetermined`，不猜。
#
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 先证明 JSON 往返逐字节相同；按**事实 61**跑完看 `git diff --stat`（应只有预期行变化）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")
CAP = REPO / "capabilities.yaml"

#: ★ **8 条 `undetermined` 的人工确证结果**（每条都写**依据**，不写「我确认」）
#: ⚠ 判据一律是硬证据 `git cat-file -e origin/main:<path>`（事实 49）。
RESOLVED = {
    "solidworks_addin_host": ("upstream", "scripts/sw_addin_host.py + dotnet/CadStudio.SolidWorks.AddinHost/SwAddin.cs 都在 origin/main"),
    "custom_properties_and_bom": ("upstream", "scripts/sw_document_data.py 在 origin/main（自定义属性读写的实现）"),
    "headless_open_format_writing": ("upstream", "scripts/cad_studio.py 在 origin/main（无头格式写出）"),
    "autocad_basic_drafting": ("upstream", "scripts/cad_studio.py 在 origin/main（AutoCAD 二维路径）"),
    "requirements_planning": ("upstream", "apps/desktop/cad_workbench/engineering_orchestrator.py 在 origin/main"),
    "parameter_updates": ("upstream", "scripts/sw_document_data.py 含 `model.Parameter(dimension_name)` 且在 origin/main"),
    # ⚠ 这一条**没有**在 origin/main 里找到明确实现 ⇒ **如实留 undetermined**
    "configurations_and_design_tables": ("undetermined",
                                         "在 origin/main 与工作树里**都没找到**明确的配置/设计表实现模块；"
                                         "`capabilities.yaml` 的 evidence 只指向 `tests/test_cad_reliability.py`"
                                         "（宽泛集成测试，**推不出**实现）⇒ **按铁律 5 不猜**"),
}
#: ⚠ 第 8 条 `undetermined` 名单里的 `pack_and_go` 已由 ① 的工具给出 upstream（命中 8 个上游模块）


def is_upstream(rel: str) -> bool:
    return subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", "origin/main:%s" % rel],
                          check=False, capture_output=True, text=True).returncode == 0


def main() -> int:
    RAW = CAP.read_text(encoding="utf-8")
    d = json.loads(RAW)
    assert json.dumps(d, ensure_ascii=False, indent=2) + "\n" == RAW, "⚠ 往返不是逐字节相同 ⇒ 停下"
    print("  ✓ 往返逐字节相同（%d 字节）" % len(RAW))

    caps = d["capabilities"] if isinstance(d.get("capabilities"), list) else list(d["capabilities"].values())

    # ① 先跑提案工具，拿下它的分类（**不重造**）
    proc = subprocess.run([sys.executable, str(REPO / "tools" / "propose_capability_sources.py")],
                          check=False, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=str(REPO))
    proposed = {}
    for m in re.finditer(r"^\s{2}(\w[\w_]*)\s+→ \*\*(\w+)\*\*", proc.stdout or "", re.M):
        proposed[m.group(1)] = m.group(2)
    print("  ✓ 提案工具给出 %d 条分类" % len(proposed))

    changed, dist = 0, {}
    for cap in caps:
        cid = cap.get("id")
        # ② 人工确证优先（比关键词硬）
        if cid in RESOLVED:
            kind, why = RESOLVED[cid]
            cap["source"] = kind
            cap["source_evidence"] = why
        elif cid in proposed:
            cap["source"] = proposed[cid]
            cap["source_evidence"] = ("`tools/propose_capability_sources.py` 的关键词提案"
                                      "（命中模块的上游/新增归属已由该工具用 "
                                      "`git cat-file -e origin/main:<path>` 判定）")
        else:
            cap["source"] = "undetermined"
            cap["source_evidence"] = "提案工具与人工确证**都没给出**归属 ⇒ 按铁律 5 留 undetermined"
        dist[cap["source"]] = dist.get(cap["source"], 0) + 1
        changed += 1

    CAP.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    after = json.loads(CAP.read_text(encoding="utf-8"))
    a = after["capabilities"] if isinstance(after.get("capabilities"), list) else list(after["capabilities"].values())
    print()
    print("  ── 落盘核对 ──")
    print("    加了 source 的条数: %d / %d" % (sum(1 for c in a if "source" in c), len(a)))
    print("    分布: %s" % ", ".join("%s=%d" % kv for kv in sorted(dist.items())))
    print("    每条都带 source_evidence: %s"
          % all(c.get("source_evidence") for c in a))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
