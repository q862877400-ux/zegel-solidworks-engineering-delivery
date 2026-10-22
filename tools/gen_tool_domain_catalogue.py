"""★ 生成"工具域目录"（供 AGENTS.md 引用 + 独立索引文档）—— ★ 判据全从 `all_specs()` 重推。

★ 为什么需要它（2026-10-04 · 业主提问「433 个工具怎么让 agent 知道有哪些」）：
  · 行业口径（MCP 官方 client-best-practices / Anthropic / Claude Code 文档）一致认为：
    **不要把工具定义全塞进上下文**，而是 **① 在系统提示里写"类别目录"** +
    **② 让工具定义按需发现**（search_tools / defer）。
  · 本仓现状：宿主**不支持** defer ⇒ 433 个 schema 每轮常驻；而 AGENTS.md 又受
    **65536 字节**预算限制（该预算**已经**逼我们把 known-facts 拆出去）
    ⇒ ★ **唯一能进 AGENTS.md 的形态就是"域目录"**（每域一行），全文进 `docs/mcp-tools.md`。
★ 本脚本负责**把这两样都生成出来**，并把**字节成本**如实打出来（★ 免得凭感觉说"装得下"）。

★ 用法：
    python tools/gen_tool_domain_catalogue.py                 # 打印统计 + 写两个文件
    python tools/gen_tool_domain_catalogue.py --check         # 只比对是否最新（门禁用）
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/gen_tool_domain_catalogue.py
# 定位:   生成"工具域目录"（供 AGENTS.md 引用 + 独立索引文档）—— ★ 判据全从 `all_specs
#           ()` 重推。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import argparse
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

AGENTS_LIMIT = 65536
OUT_DOMAIN = ROOT / "docs" / "tool-domains.md"          #: ★ 域目录（AGENTS.md 里引用它）
OUT_FULL = ROOT / "docs" / "mcp-tools.md"               #: ★ 全量索引（433 行）


def _specs():
    import register_capabilities as rc
    return rc.all_specs()


def _domain_line(module: str, specs: list) -> str:
    """★ 每域一行：域名 · 工具数 · 干什么 · 常用注入键。"""
    #: 域名去掉 sw_ 前缀，更短
    name = module[3:] if module.startswith("sw_") else module
    #: 一句话：取该域**最多 3 个**工具 title 的共同线索 —— ★ 不做花哨 NLP，直接给代表性能力
    titles = []
    for s in specs[:3]:
        t = (getattr(s, "title", "") or getattr(s, "name", "")).strip()
        if t and t not in titles:
            titles.append(t)
    inj = sorted({getattr(s, "inject", "") for s in specs if getattr(s, "inject", "")})
    keys = (" ★注入键: " + " / ".join(inj)) if inj else ""
    return "| `%s` | %d | %s%s |" % (name, len(specs), " · ".join(titles)[:110], keys)


def build() -> tuple[str, str, dict]:
    specs = _specs()
    g: dict = defaultdict(list)
    for s in specs:
        g[getattr(s, "module", "?")].append(s)
    ordered = sorted(g.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    dom = ["# 工具域目录（★ 由 `tools/gen_tool_domain_catalogue.py` 生成，**不要手改**）", "",
           "> **为什么有这个文件**：工具数已达 **%d** 个，**不可能**列进 `AGENTS.md`" % len(specs),
           "> （该文件受 **65536 字节**指令预算限制，本仓已因此把 known-facts 拆到 `docs/`）。",
           "> ★ 行业口径（MCP 官方 *client best practices* / Anthropic *advanced tool use*）是：",
           "> **系统提示里只写「类别」，工具定义按需发现** ⇒ 本文件就是那份「类别目录」 ✓",
           "> ★ 全量索引（每个工具一行）见 [`mcp-tools.md`](mcp-tools.md)。", "",
           "| 域（`scripts/sw_*.py`） | 工具数 | 代表性能力 |", "|---|---:|---|"]
    dom += [_domain_line(m, v) for m, v in ordered]
    dom += ["", "**合计 %d 个工具 · %d 个域**" % (len(specs), len(ordered)), ""]

    full = ["# MCP 工具全量索引（★ 由 `tools/gen_tool_domain_catalogue.py` 生成，**不要手改**）", "",
            "> ★ 按**域**分组；每条给：工具名 · 参数 · 注入键 · 一句话。",
            "> ★ 用途：人/agent **按需查**（★ 不是每轮都读 —— 那正是本文件要避免的事）。", ""]
    for m, v in ordered:
        full.append("## `%s`（%d 个）" % (m, len(v)))
        full.append("")
        full.append("| 工具 | 参数 | 注入键 | 说明（首句） |")
        full.append("|---|---|---|---|")
        for s in sorted(v, key=lambda x: x.name):
            ps = ", ".join(p.name for p in (getattr(s, "params", None) or []))
            doc = (getattr(s, "doc", "") or "").strip().split("。")[0][:80]
            full.append("| `%s` | %s | `%s` | %s |" % (
                s.name, ps or "—", getattr(s, "inject", "") or "—", doc))
        full.append("")
    stats = {"tools": len(specs), "domains": len(ordered),
             "domain_doc_bytes": len("\n".join(dom).encode("utf-8")),
             "full_doc_bytes": len("\n".join(full).encode("utf-8")),
             "agents_limit": AGENTS_LIMIT}
    return "\n".join(dom) + "\n", "\n".join(full) + "\n", stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只比对是否最新（门禁用）")
    a = ap.parse_args()
    dom, full, st = build()
    print("★ 工具 **%d** 个 · 域 **%d** 个" % (st["tools"], st["domains"]))
    print("★ 域目录（`docs/tool-domains.md`）: **%d 字节** ⇒ 占 AGENTS.md 预算的 **%.1f%%**"
          % (st["domain_doc_bytes"], 100.0 * st["domain_doc_bytes"] / st["agents_limit"]))
    print("★ 全量索引（`docs/mcp-tools.md`）: **%d 字节（%.1f KB）**" % (
        st["full_doc_bytes"], st["full_doc_bytes"] / 1024))
    if a.check:
        stale = [p.name for p, want in ((OUT_DOMAIN, dom), (OUT_FULL, full))
               if (not p.is_file()) or p.read_text(encoding="utf-8") != want]
        if stale:
            print("★ [FAIL] 生成物不新鲜: %r ⇒ 跑 `python tools/gen_tool_domain_catalogue.py`" % stale)
            return 1
        print("★ [PASS] 两个生成物都是最新的")
        return 0
    OUT_DOMAIN.write_text(dom, encoding="utf-8")
    OUT_FULL.write_text(full, encoding="utf-8")
    print("★ 已写: %s" % OUT_DOMAIN)
    print("★ 已写: %s" % OUT_FULL)
    (ROOT / "output" / "tool-catalogue-stats.json").write_text(
        json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
