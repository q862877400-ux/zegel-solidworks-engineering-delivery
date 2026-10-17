"""★ 规格 205 / SC-001 的**达标证据**：一份可复核的报告（工具数 · 门禁 · 各批 · 提交）。

★ 判据全部**从盘上重推**（★ 不引用我自己的叙述）：
  · 工具数 ⇒ `register_capabilities.all_specs()`
  · 各批 ⇒ `mcp-server/tool_specs_batch*.py` 里 `ToolSpec(` 的个数
  · 门禁 ⇒ 直接跑 `check_param_binding` / `check_union_conventions`，**读退出码**
  · 提交 ⇒ `git log` 里带"规格 205"的提交
  · 能力侧 ⇒ `capabilities.yaml` 的 level 分布（★ SC-008：工具数 ≠ 能力指标）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（验收证据生成器）
# 文件:   `mcp-server/register_capabilities.py`（工具清单）· `mcp-server/tool_specs_batch*.py`（各批）·
#         `capabilities.yaml`（能力等级）· `scripts/check_param_binding.py` / `check_union_conventions.py`
# 定位:   规格 `specs/205-tool-ramp/` 的 **SC-001**（工具数 ≥400）与 **SC-008**（能力侧真实性）验收 ✓
# 官方依据: 无（本仓自建工具）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import register_capabilities as rc                                # noqa: E402

out: dict = {}
specs = rc.all_specs()
out["tool_count"] = len(specs)
out["sc001_target"] = 400
out["sc001_met"] = len(specs) >= 400

#: ★ 各批工具数（★ 只数文件里**真正的 ToolSpec(**，数名字也一起给）
batches = {}
for f in sorted((ROOT / "mcp-server").glob("tool_specs_batch*.py")):
    t = f.read_text(encoding="utf-8", errors="replace")
    n = len(re.findall(r"(?m)^\s*ToolSpec\(", t))
    names = re.findall(r'name="(solidworks_[^"]+)"', t)
    batches[f.name] = {"declared": n, "names": len(names)}
out["batches"] = batches
out["batches_total"] = sum(v["declared"] for v in batches.values())
out["tools_by_module"] = dict(Counter(getattr(s, "module", "") for s in specs).most_common())
out["resolver_keys"] = sorted(rc.RESOLVERS.keys())

#: ★ 门禁（★ 读退出码，不看输出文字）
gates = {}
for name, cmd in (("check_param_binding", [sys.executable, "scripts/check_param_binding.py"]),
                  ("check_union_conventions", [sys.executable, "scripts/check_union_conventions.py"])):
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600)
    gates[name] = {"exit": r.returncode, "tail": (r.stdout or "")[-200:]}
out["gates"] = gates

#: ★ 提交（★ 带"规格 205"的那些）
r = subprocess.run(["git", "log", "--oneline", "-60"], cwd=str(ROOT), capture_output=True,
                   text=True, encoding="utf-8", errors="replace", timeout=120)
out["commits_spec205"] = [ln for ln in (r.stdout or "").splitlines() if "205" in ln or "工具 3" in ln
                          or "工具数" in ln][:20]

#: ★ SC-008：能力侧（★ 支线的告诫：工具数是代码组织方式的函数，不是能力指标）
caps = json.loads((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))["capabilities"]
out["capabilities"] = {"total": len(caps),
                       "by_level": dict(Counter(c.get("level") for c in caps))}

(ROOT / "output" / "goal-evidence.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("★ 工具数 %d（目标 %d）⇒ SC-001 %s" % (out["tool_count"], out["sc001_target"],
                                            "**达成** ✓" if out["sc001_met"] else "未达成"))
print("★ 各批声明合计 %d · 批次文件 %d 个" % (out["batches_total"], len(batches)))
print("★ 门禁:", {k: v["exit"] for k, v in gates.items()})
print("★ 能力:", out["capabilities"])
print("★ 落盘 output/goal-evidence.json")
