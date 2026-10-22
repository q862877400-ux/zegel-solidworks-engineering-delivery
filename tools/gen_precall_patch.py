"""★ **生成器原型**：把 bunny 的 `precall-cand-*.py` 自动翻成"该给哪条 spec 挂什么"的**补丁计划**。

★ 业主问：「能不能给每个批次的种类搞一个生成器，直接用代码生成代码？」
★ ★★★ **本脚本就是那个回答的第一步** —— ★ 它证明「mark/前置」那一类的**输入是结构化的**：
  · **输入**（★ 全是机器可读的）：
      ① `specs/202-user-coverage-gaps/recon/precall-cand/precall-cand-*.py`
         —— ★ 形态统一：每条工具一个 `_pre_<name>(params)` + 一段共用帮手 + 每条自带官方依据；
      ② 仓内那条 spec 的现状（`mcp-server/tool_specs_batch*.py`）；
  · **处理**：★ 把 `_pre_<x>` ↔ 工具名 ↔ 它要的参数**对上**；
  · **输出**：★ **一份补丁计划（JSON）**，★ 每条说清「哪条 spec · 加什么 `pre_call` · 加什么
    `param_alias` · 要不要加参数」。
★ ★★★ **它刻意只出计划、不改任何文件** —— ★ 因为本仓有两条硬纪律：
  · **事实 61**：批量改文件的脚本**必须先证明只做加法**（`git diff --stat` 见 `deletions` 就是事故）；
  · **M3**：★ **集成与真机验证由 Lead 做** ⇒ ★ 生成器**只到"计划"为止**，★ 落笔由人。
★ 只读；★ 产出 `output/precall-patch-plan.json`。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/gen_precall_patch.py
# 定位:   生成器原型**：把 bunny 的 `precall-cand-*.py` 自动翻成"该给哪条 spec 挂什么"
#           的**补丁计划**。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(Path(__file__).resolve().parents[1])
CAND = REPO / "specs" / "202-user-coverage-gaps" / "recon" / "precall-cand"
OUT = REPO / "output" / "precall-patch-plan.json"


def _specs_by_tool() -> dict:
    """★ 仓内每条工具现在长什么样（★ 只读源码文本，不 import —— 免得拉 COM）。"""
    out = {}
    for f in sorted((REPO / "mcp-server").glob("tool_specs_batch*.py")):
        t = f.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r'name="(solidworks_[a-z0-9_]+)"', t):
            out.setdefault(m.group(1), {"file": f.name, "has_pre_call": False,
                                        "has_param_alias": False, "params": []})
        #: ★ 粗略取该文件里的 spec 块（★ 够用于"有没有 pre_call / param_alias"这两个布尔）
        for blk in re.split(r"ToolSpec\(", t)[1:]:
            nm = re.search(r'name="(solidworks_[a-z0-9_]+)"', blk)
            if not nm:
                continue
            e = out[nm.group(1)]
            e["has_pre_call"] = "pre_call=" in blk
            e["has_param_alias"] = "param_alias=" in blk
            e["params"] = re.findall(r'Param\(\s*"([a-z0-9_]+)"', blk)
    return out


def _cand_pre_calls() -> dict:
    """★ 从 bunny 的候选里抽 `_pre_<x>(params)`（★ 用 AST，★ 不执行它的代码）。"""
    out = {}
    for f in sorted(CAND.glob("precall-cand-*.py")):
        if f.name.startswith("__"):
            continue
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError as exc:
            out[f.name] = {"parse_error": str(exc)[:120]}
            continue
        fns = [n.name for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name.startswith("_pre_")]
        helpers = [n.name for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name.startswith("_")
                   and not n.name.startswith("_pre_")]
        #: ★ 从候选的**文字**里找它认领了哪几条工具（★ 候选里通常点名）
        txt = f.read_text(encoding="utf-8", errors="replace")
        claimed = sorted(set(re.findall(r"(?:solidworks_)?(part_[a-z0-9_]+|mold_[a-z0-9_]+)",
                                        txt)))[:24]
        out[f.name] = {"pre_calls": fns, "helpers": helpers, "claimed_names": claimed}
    return out


def main() -> int:
    started = time.time()
    specs = _specs_by_tool()
    cands = _cand_pre_calls()
    plan = []
    for cname, info in cands.items():
        for fn in info.get("pre_calls", []):
            #: ★ `_pre_part_sweep` ⇒ `part_sweep` ⇒ `solidworks_part_sweep`
            short = fn[len("_pre_"):]
            tool = "solidworks_" + short
            cur = specs.get(tool)
            plan.append({
                "candidate": cname,
                "pre_call_fn": fn,
                "tool": tool,
                "tool_registered": cur is not None,
                "spec_file": (cur or {}).get("file"),
                "already_has_pre_call": (cur or {}).get("has_pre_call"),
                "already_has_param_alias": (cur or {}).get("has_param_alias"),
                "current_params": (cur or {}).get("params", []),
                "action": ("★ 已挂（跳过）" if (cur or {}).get("has_pre_call")
                           else ("★ 要挂：" + fn) if cur else "★ 工具没注册 —— 核对名字"),
                "note": "★ 生成器**只出计划**；★ 落笔前须 Lead 复核 + 真机验证（M3）",
            })
    OUT.write_text(json.dumps({"at": time.strftime("%Y-%m-%d %H:%M:%S"),
                               "generator": "tools/gen_precall_patch.py",
                               "inputs": {"specs_scanned": len(specs),
                                          "candidates": list(cands)},
                               "candidate_detail": cands,
                               "plan": plan},
                              ensure_ascii=False, indent=1), encoding="utf-8")

    print("★ 输入：仓内 **%d** 条工具 · bunny 候选 **%d** 份" % (len(specs), len(cands)))
    for cn, info in cands.items():
        if "parse_error" in info:
            print("   %-22s ★ 解析失败: %s" % (cn, info["parse_error"]))
            continue
        print("   %-22s pre_call **%d** 个 · 帮手 %d 个 ⇒ %s"
              % (cn, len(info["pre_calls"]), len(info["helpers"]), ", ".join(info["pre_calls"])))
    print()
    print("%-26s %-22s %-22s %-8s %s" % ("候选里的 pre_call", "对上的工具", "那条 spec 在哪", "已挂?", "动作"))
    print("-" * 122)
    for r in plan:
        print("%-26s %-22s %-22s %-8s %s"
              % (r["pre_call_fn"][:25], r["tool"].replace("solidworks_", "")[:21],
                 str(r["spec_file"])[:21], str(r["already_has_pre_call"]), r["action"][:44]))
    print()
    print("★ 计划写到:", OUT, "（%.1f s）" % (time.time() - started))
    print("★★ 注意：★ 本生成器**不改任何文件** —— ★ 它只回答「该给谁挂什么」，★ 落笔与真机验证由 Lead 做。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
