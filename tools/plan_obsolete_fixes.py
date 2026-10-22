"""★ T1a 第一步：把**每一条废弃调用**与它**后继的官方签名**逐个对照 ⇒ 分清"纯改名"与"要改参数"。

★★ 为什么必须先做这一步（★ 不能直接批量替换）：
  ★ bunny 的 `PATTERNS.md` 实测：★ 废弃成员的**后继有 8 种改法** ——
    ★ 同型同名 · 删兜底分支 · 首位换后继 · ★★ **后继形参变了** · ★ **属性→方法** ·
    ★★ **换宿主接口** · 链尾 `CreateFeature` · ★★★ **by-ref 出参新增**。
  ⇒ ★★ **"号+1"只是形态之一，★ 而参数量可能完全变了**（★ 例：`FeatureFillet` 8 → `FeatureFillet3` 15）。
★★ 判据（★ 写死在跑之前）：
  · **纯改名**：★ 后继的**形参个数 == 我们调用的实参个数**（★ 且没有新增 by-ref/out）
  · **要改参数**：★ 个数不等 ⇒ ★★ **必须人工/真机逐条定**，★ 不许自动替换
★ 只读官方文档 + 我们的源码。产出 `output/obsolete-fix-plan.json`。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/plan_obsolete_fixes.py
# 定位:   T1a 第一步：把**每一条废弃调用**与它**后继的官方签名**逐个对照 ⇒ 分清"纯改名
#           "与"要改参数"。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(Path(__file__).resolve().parents[1])
SWAPI = Path(r"C:\swapi\types")
SCAN = REPO / "output" / "obsolete-dotcall-scan.json"
OUT = REPO / "output" / "obsolete-fix-plan.json"


def official_params(member: str) -> dict:
    """★ 取官方签名与形参个数（★ 三源里的 `C:\\swapi\\types\\<接口>\\<成员>.md`）。"""
    hits = list(SWAPI.rglob(member + ".md"))
    if not hits:
        return {"found": False}
    t = hits[0].read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\*\*Signature\*\*:\s*`(.*?)`", t)
    sig = m.group(1) if m else ""
    params = re.findall(r"System\.[A-Za-z0-9_.\[\]]+", sig)
    names = re.findall(r"ByVal\s+(\w+)", t) or re.findall(r"\*\*(\w+)\*\*:", t)
    byref = bool(re.search(r"\bbyref\b|\bByRef\b|\bout\b", t, re.I))
    #: ★★★ 2026-10-03（接手轮）**新加「方法↔属性」的识别** —— ★ 这是**本仓最大的一类**：
    #: ★ `GetActiveSketch2`（★ 方法）→ `ActiveSketch`（★ **属性**，`Sketch ActiveSketch 
    #: {get;}`）；
    #:   ★ `SystemValue`（★ **属性**）→ `GetSystemValue3`（★ 方法）。
    #: ★★ 判据：★ 官方签名里出现 **`{get;}` / `{set;}` / `{ get; set; }`** ⇒ **是属性** 
    #: ✓
    #:   ★ 为什么必须单独成类：★ 属性**没有形参** ⇒ ★ 用"参数个数"去判会得到 0，
    #: 而**调用形态完全不同**（★ 属性是**取值**、方法是**调用**）⇒ ★ 混在一起会给出错的
    #: 改法。
    is_property = bool(re.search(r"\{\s*(get|set)\s*;", sig, re.I))
    return {"found": True, "signature": sig, "n_params": len(params),
            "params": names[:20], "has_byref_or_out": byref, "is_property": is_property,
            "page": str(hits[0])}


def arg_count(text: str, member: str) -> int:
    """★ 数出那一次调用的实参个数（★ 括号配对，★ 不按第一个 `)` 截 —— 事实 58 的教训）。

    ★★ 2026-10-03 修：★ 第一版**只传进来一行** ⇒ ★ 而本仓的调用**大量跨多行**
      （★ 例 `return asm_model.AddComponent4(` 后面才是参数）⇒ ★★ **数到 0**
      ⇒ ★ 那是**我的测量错**，★ 不是代码的错（★ 与事实 51 同族：分析范围要和代码的组织单元匹配）。
    ⇒ ★ 现在传**调用点附近的多行窗口**进来。
    """
    i = text.find(member + "(")
    if i < 0:
        return -1
    j = i + len(member) + 1
    depth, n, seen = 1, 0, False
    while j < len(text) and depth:
        c = text[j]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                break
        elif c == "," and depth == 1:
            n += 1
        elif not c.isspace() and depth == 1:
            seen = True
        j += 1
    return (n + 1) if seen else 0


def main() -> int:
    scan = json.loads(SCAN.read_text(encoding="utf-8", errors="replace"))
    rows = scan["行"]
    plan = []
    for r in rows:
        succ = (r.get("successor") or "").split("::")[-1]
        #: ★ 多级后继：★ `FeatureFillet` → `FeatureFillet2` → `FeatureFillet3`（★ 本仓事
        #: 实）
        chain, cur = [succ], succ
        for _ in range(3):
            info = official_params(cur)
            m2 = re.search(r"Superseded by\s*\[\[[^:]+::([^\]]+)\]\]",
                           (Path(info["page"]).read_text(encoding="utf-8", errors="replace")
                            if info.get("found") else ""))
            if m2 and m2.group(1) != cur:
                cur = m2.group(1)
                chain.append(cur)
            else:
                break
        final = chain[-1]
        finfo = official_params(final)
        cur_info = official_params(r["member"])
        src = (REPO / r["file"]).read_text(encoding="utf-8", errors="replace").splitlines()
        #: ★★ 用**调用点附近的多行窗口**（★ 本仓调用大量跨行 ⇒ 只看单行会数成 0）
        i0 = max(0, r["line"] - 1)
        window = "\n".join(src[i0:i0 + 14])
        n_ours = arg_count(window, r["member"])
        n_succ = finfo.get("n_params", -1)
        #: ★★★ byref 过滤（★ bunny `PATTERNS.md` 结论 3 + 本仓事实 47）：
        #:   ★ 后继多出 by-ref / out ⇒ ★ **换过去会撞 pywin32 迟到绑定的不可调用**
        #:   ⇒ ★★ **判为"不可换，保留现状并记档"**。
        byref_block = bool(finfo.get("has_byref_or_out"))
        #: ★★★ 「方法 ↔ 属性」这一类（★ 本仓最大的一类）—— ★★ 单列，★ 因为**调用形态完全
        #: 不同**：
        #: · ★ **方法 → 属性**：★ `obj.GetActiveSketch2()` ⇒ `obj.ActiveSketch`（★ 去掉
        #: 括号）
        #: · ★ **属性 → 方法**：★ `obj.SystemValue` ⇒ `obj.GetSystemValue3(...)`（★ 要加
        #: 括号与实参）
        #:   ★ 用"参数个数"判它会得到 0 vs 0（★ 属性没有形参）⇒ ★ **会误判成"纯改名"** ✓
        succ_is_prop = bool(finfo.get("is_property"))
        ours_is_call = "(" in (window.split(r["member"], 1)[-1][:2] if r["member"] in window else "")
        if byref_block:
            kind = "★★★ 不可换（后继含 by-ref，★ 事实 47 会失败）"
        elif succ_is_prop and not ours_is_call:
            kind = "★★ 属性 → 属性（★ 只改名，★ 注意取值写法）"
        elif succ_is_prop and ours_is_call:
            kind = "★★★ 方法 → 属性（★ 要去掉括号；★ 调用形态变了）"
        elif (not succ_is_prop) and (not ours_is_call) and n_succ >= 1:
            kind = "★★★ 属性 → 方法（★ 要加括号与实参；★ 如 SystemValue → GetSystemValue3）"
        elif n_ours == n_succ and n_ours >= 0:
            kind = "★ 纯改名（个数相同）"
        elif n_succ >= 0:
            kind = "★★ 要改参数"
        else:
            kind = "★ 后继页查不到"
        plan.append({
            "member": r["member"], "file": r["file"], "line": r["line"],
            "chain": chain, "final": final,
            "ours_args": n_ours,
            "ours_official_params": cur_info.get("n_params"),
            "final_params": n_succ,
            "final_has_byref": finfo.get("has_byref_or_out"),
            "kind": kind,
            "ctx": window.strip()[:150],
        })
    by_kind: dict = {}
    for p in plan:
        by_kind.setdefault(p["kind"], []).append(p)
    OUT.write_text(json.dumps({"at": __import__("time").strftime("%Y-%m-%d %H:%M:%S"),
                               "plan": plan, "by_kind": {k: len(v) for k, v in by_kind.items()}},
                              ensure_ascii=False, indent=1), encoding="utf-8")

    print("★ %d 条命中 ⇒ 逐个核后继签名：" % len(plan))
    print()
    print("%-24s %-22s %-6s %-8s %-8s %s" % ("成员", "★ 后继链", "我们", "后继", "byref?", "判定"))
    print("-" * 116)
    for p in plan:
        print("%-24s %-22s %-6s %-8s %-8s %s"
              % (p["member"][:23], " → ".join(p["chain"])[:21], p["ours_args"],
                 p["final_params"], p["final_has_byref"], p["kind"]))
    print()
    for k, v in by_kind.items():
        print("★ %-22s **%d** 条" % (k, len(v)))
    print()
    print("★ 产出:", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
