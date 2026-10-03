"""★ **任务 3 · 扫全仓"用了官方废弃成员"** —— ★ 判据用「所有接口都废弃」的**安全名字**（★ 事实 511）。

★★ 为什么要有这一版（★ 上一版报了 **870 处、头几名全假阳性**）：
  ★ 第一版 `tools/scan_obsolete_usage.py` **按成员名**直接对废弃名单 ⇒
    ★★ `FeatureCut4`（★ 本仓**事实 1** 说它才是"切除的正确入口"）· `Name`（★ 24 个接口里只有 2 个废弃）·
    `GetBodies2` · `CreateLine` · `GetEdges` —— **全被误报** ✓
  ⇒ ★★★ **根因**：★ 官方 API 是「**接口 × 成员**」二维表，★ 而 `get_com_member(x, "GetBodies2")` 里
    **`x` 属于哪个接口静态看不出来** ⇒ ★ **按名字判必须有取舍**。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
★★★ 判据（★ **本文件在跑之前写死，跑完不改**）
  ★ **纳入**：★ 成员名落在「**在所有接口上都废弃**」那一桶里（★ 实测量约 **1163** 个）
      ⇒ ★ 按名字判**对这种名字不含歧义**（★ 事实 511 定的边界）。
  ★ **覆盖两种调用形态**（★ 上一版只覆盖 ①，★ 漏了 `sw_part.fillet` 那种）：
      ① `get_com_member(x, "M", …)` / `call_com_member` / `set_com_member`
      ② ★★ **点调用** `obj.Member(…)` / `obj.Member = …`
  ★ **三种排除**（★ 每条都必须过，★ 否则又是 870 处）：
      E1 ★ **注释里的不算** —— ★ 用 `scripts/check_env_pitfalls.py::strip_comments_and_strings`
           （★ 事实 61 定则④：写了好用的工具函数，就要在**所有**同类场合用它）
      E2 ★★ **"兜底/回退分支"单列不算缺陷** —— ★ 若**同文件里已出现该成员的后继调用**
           （★ bunny 的 `PATTERNS.md` 档② 就是这个形态）⇒ ★ 标 `fallback_branch`
      E3 ★ **纯字符串登记表不算** —— ★ 行内只有字符串字面量、没有调用形态的（★ 如 `METHODS = {...}`）⇒ 标 `registry`
  ★ **三个自检**（★ 事实 506/510：判据要自证在跑、要先标定）：
      S1 ★ **覆盖面自报**：★ 扫了几个文件 · 抽了几个调用点 · 命中几条
      S2 ★★ **假阳性自检**：★ 拿**已知反例**试 —— ★ `FeatureCut4` / `Name` / `GetBodies2` /
           `CreateLine` / `GetEdges` **必须 0 命中**（★ 它们有多接口，★ 落在歧义桶里）
      S3 ★ **抽 5 条回原文**：★ 每条给附近两行原文，★ 供人工复核
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
★ 只读。产出 `output/obsolete-dotcall-scan.json`。
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"D:\AI\SW")
IDX = REPO / "specs" / "202-user-coverage-gaps" / "recon" / "official-obsolete-index.json"
MEM = REPO / "specs" / "202-user-coverage-gaps" / "recon" / "official-members-index.json"
OUT = REPO / "output" / "obsolete-dotcall-scan.json"

#: ★★ 已知反例（★ S2 用它自检）—— 它们**必须 0 命中**
NEGATIVES = ["FeatureCut4", "Name", "GetBodies2", "CreateLine", "GetEdges",
             "CreateCircleByRadius", "GetType"]

CALL_FORMS = [
    ("get_com_member", re.compile(r'\b(?:get|call|set)_com_member\s*\(\s*[^,]+,\s*"([A-Za-z_]\w*)"')),
    ("dot_call", re.compile(r"\.([A-Z][A-Za-z0-9_]{2,})\s*\(")),
    ("dot_assign", re.compile(r"\.([A-Z][A-Za-z0-9_]{2,})\s*=(?!=)")),
]


def main() -> int:
    started = time.time()
    sys.path.insert(0, str(REPO / "scripts"))
    sys.path.insert(0, str(REPO))
    from check_env_pitfalls import strip_comments_and_strings          # noqa: E402

    obs = json.loads(IDX.read_text(encoding="utf-8", errors="replace"))["entries"]
    mem = json.loads(MEM.read_text(encoding="utf-8", errors="replace"))

    #: ★★★ 算「在所有接口上都废弃」的安全桶（★ 事实 511 的边界）
    per_iface = mem.get("per_interface") or {}
    by_name: dict = defaultdict(list)
    for iface, members in per_iface.items():
        for m in members:
            by_name[m["member"]].append(bool(m.get("obsolete")))
    safe = {n for n, flags in by_name.items() if flags and all(flags)}
    ambiguous = {n for n, flags in by_name.items() if any(flags) and not all(flags)}
    successor = {}
    for e in obs:
        if e["member"] in safe and e.get("successor"):
            successor.setdefault(e["member"], e["successor"])

    #: ★ S2 自检：反例必须在歧义桶或不在桶里（★ 不许进安全桶）
    s2 = {n: ("★ 安全桶" if n in safe else ("歧义桶" if n in ambiguous else "不在废弃名单"))
          for n in NEGATIVES}
    s2_bad = [n for n, v in s2.items() if v == "★ 安全桶"]

    files = (sorted((REPO / "scripts").glob("*.py"))
             + sorted((REPO / "mcp-server").glob("*.py"))
             + sorted((REPO / "tools").glob("*.py")))

    #: ★★★★ 2026-10-03（接手轮）**修一个假阴性**：
    #:   ★ 第一版 E1 用了 `check_env_pitfalls.strip_comments_and_strings` ——
    #:     ★★ **它把字符串字面量也剥掉** ⇒ ★★★ 于是 `get_com_member(x, "SystemValue")`
    #:     里的**成员名也没了** ⇒ ★ **全部 ① 形态的命中被漏掉**，★ 只剩点调用被抓到。
    #:   ★ 实测证据：`IDimension.SystemValue` 是废弃的（★ 且只在 1 个接口上 ⇒ 属安全桶），
    #:     而 `scripts/sw_document_data.py:221` 的 `get_com_member(dimension, "SystemValue")`
    #:     **没出现在结果里**。
    #:   ⇒ ★ 本版改用 **tokenize 只丢 COMMENT**（★ 保留 STRING）——
    #:     ★ 与事实 61 定则④同精神：**工具函数用错场合就等于没有**。
    def strip_comments_only(src: str) -> str:
        import io as _io
        import tokenize as _tk

        out, last = [], (1, 0)
        try:
            for tok in _tk.generate_tokens(_io.StringIO(src).readline):
                if tok.type == _tk.COMMENT:
                    continue
                out.append(tok)
        except Exception:                                                 # noqa: BLE001
            return src
        #: ★ 按 token 类型重建：★ 直接拼 token 的原始文本（★ 保留字符串字面量）
        try:
            res = _tk.untokenize(out)
            return res if isinstance(res, str) else res.decode("utf-8", "replace")
        except Exception:                                                 # noqa: BLE001
            lines = []
            for line in src.splitlines():
                #: ★ 退化路径：★ 只砍掉"看起来在字符串外面"的 `#`
                q = None
                for i, c in enumerate(line):
                    if q:
                        if c == q and line[i - 1] != "\\":
                            q = None
                    elif c in "\"'":
                        q = c
                    elif c == "#":
                        line = line[:i]
                        break
                lines.append(line)
            return "\n".join(lines)

    #: ★★★ 2026-10-03（接手轮）**新增"跨库存疑"档**（★ 由 OCP 的 `bounds.Get()` 暴露）：
    #:   ★ 病灶：★ `scripts/advanced_geometry_ocp.py` 与 `headless_occt_service.py` 里的
    #:     `xmin, ymin, zmin, xmax, ymax, zmax = **bounds.Get()**` 是 **OCP/OpenCASCADE** 的调用
    #:     （★ `Bnd_Box.Get()` 正是回 6 元组），★ 而本扫描器**按名字**把它算成了
    #:     SolidWorks 的 `ICustomPropertyManager.Get` ⇒ ★★ **跨库假阳性** ✓
    #:   ★★★ 根因与**事实 511**同源：★ **点调用（`obj.M()`）的宿主是运行时的，静态判不出来**。
    #:   ⇒ ★ 判据：★ **点调用** 且 **同文件里没有任何 SolidWorks 标志**（`sw_`/`SldWorks`/
    #:     `get_com_member`/`IModelDoc`/`SolidWorks`…）⇒ ★★ **降级为「跨库存疑」，不计入真命中** ✓
    #:   ⚠ 限度（★ 如实记）：★ 这是**启发式**（★ 同文件可能恰好没有那些词），
    #:     所以它**只降级、不删除** —— 存疑条目**仍会单独列出**供人看 ✓
    SW_MARKERS = ("get_com_member", "call_com_member", "set_com_member", "SldWorks",
                  "SolidWorks", "IModelDoc", "sw_app", "sldworks")
    SUSPECT_LIB = ("ocp", "occ", "opencascade", "pythonocc", "cadquery")

    def _is_crosslib_suspect(f: Path, raw: str) -> bool:
        low = str(f).lower()
        if any(k in low for k in SUSPECT_LIB):
            return True
        head = raw[:4000]
        return not any(m in head for m in SW_MARKERS)

    rows, scanned, calls = [], 0, 0
    for f in files:
        if f.name.startswith("_"):
            continue
        scanned += 1
        try:
            raw = f.read_text(encoding="utf-8", errors="replace")
        except Exception:                                                 # noqa: BLE001
            continue
        #: ★ E1 —— 只剥**注释**（★ 保留字符串字面量，★ 否则成员名一起没了）
        code = strip_comments_only(raw)
        lines = raw.splitlines()
        code_lines = code.splitlines()
        #: ★ E2 依据：本文件里出现过的官方**后继**名字集合
        succ_here = set()
        for _m, pat in CALL_FORMS:
            for g in pat.findall(code):
                succ_here.add(g)
        for i, cl in enumerate(code_lines):
            s = cl.strip()
            for how, pat in CALL_FORMS:
                for name in pat.findall(cl):
                    if name not in safe:
                        continue
                    calls += 1
                    succ = successor.get(name, "")
                    succ_short = succ.split("::")[-1] if succ else ""
                    #: ★ E2：后继在本文件里出现过 ⇒ 这是兜底/回退分支
                    fallback = bool(succ_short) and succ_short in succ_here
                    #: ★ E3：该行只有字符串/登记，没有真正的调用括号
                    registry = (how != "dot_call" and "(" not in s.replace("#", "")) or \
                               bool(re.match(r'^\s*["\']', s))
                    rows.append({
                        "file": str(f.relative_to(REPO)), "line": i + 1, "member": name,
                        "how": how, "successor": succ, "fallback_branch": fallback,
                        "registry_like": registry,
                        #: ★★★ 2026-10-03（接手轮）**加"生产 vs 探针/证据"这一维**：
                        #:   ★ 实测 `GetActiveSketch2` 的 17 处里 **只有 3 处在 `scripts/`**，
                        #:   ★ 其余 14 处都在 `tools/`（★ 探针与历史证据脚本）。
                        #:   ★★ **探针是**历史证据**，改了会破坏"证据不可变"**
                        #:   （★ 我在 `gate-cand/GATE-FINAL.md` 的 **C12 证据不可变**里也写了这条）
                        #:   ⇒ ★ **只改 `scripts/`（生产）**，★ `tools/` 的**只报不动** ✓
                        "scope": ("★ 生产（scripts/）" if str(f.relative_to(REPO)).startswith("scripts")
                                  else "★ 探针/证据（tools/，★ 只报不动）"
                                  if str(f.relative_to(REPO)).startswith("tools")
                                  else "★ 其它"),
                        #: ★★★ 「跨库存疑」：★ **点调用** 且 **同文件没有 SolidWorks 标志**
                        #:   ⇒ ★ 降级（★ 见上面 `_is_crosslib_suspect` 的说明）
                        "crosslib": bool(how != "get_com_member" and _is_crosslib_suspect(f, raw)),
                        "ctx": lines[i].strip()[:160] if i < len(lines) else "",
                    })
    #: ★ 分类
    for r in rows:
        r["class"] = ("★ 兜底分支（不算缺陷）" if r["fallback_branch"]
                      else "★ 疑似登记表（要人看）" if r["registry_like"]
                      else "★ 跨库存疑（点调用 + 无 SolidWorks 标志）" if r.get("crosslib")
                      else "★★ 待修（真命中）")
    real = [r for r in rows if r["class"] == "★★ 待修（真命中）"]
    crosslib = [r for r in rows if r["class"] == "★ 跨库存疑（点调用 + 无 SolidWorks 标志）"]
    agg = Counter(r["member"] for r in real)

    R = {
        "at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "★_判据": "成员名 ∈「所有接口都废弃」的安全桶；覆盖 get_com_member/dot_call/dot_assign；"
                  "排除 E1 注释 · E2 兜底分支 · E3 登记表",
        "规模": {"官方废弃成员": len(obs),
                 "★_安全桶（所有接口都废弃）": len(safe),
                 "★_歧义桶（部分接口废弃）": len(ambiguous),
                 "扫的文件": scanned,
                 "★_抽到的调用点": calls},
        "自检 S2 反例": s2,
        "★_S2 通过": not s2_bad,
        "命中": {"真命中": len(real), "兜底分支": sum(1 for r in rows if r["fallback_branch"]),
                 "疑似登记表": sum(1 for r in rows if r["registry_like"] and not r["fallback_branch"])},
        "★_按成员": agg.most_common(30),
        "行": real,
        "全部行": rows,
    }
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")

    print("★ 官方废弃成员 **%d** ⇒ ★★ **安全桶 %d**（★ 所有接口都废弃）· 歧义桶 %d"
          % (len(obs), len(safe), len(ambiguous)))
    print("★ 扫了 **%d** 个文件 · 抽到 **%d** 个调用点" % (scanned, calls))
    print()
    print("★ 自检 S2（★ 已知反例**必须不进安全桶**）：%s" % ("★ 通过 ✓" if not s2_bad else "★★ 失败：%s" % s2_bad))
    for n, v in s2.items():
        print("     %-24s %s" % (n, v))
    print()
    print("★★★ 分类：")
    print("   ★★ 真命中（待修）      **%d**" % len(real))
    #: ★★★ 新增档：★ 跨库存疑（★ 由 OCP 的 `bounds.Get()` 暴露 —— 与事实 511 同源）
    print("   ★ 跨库存疑（★ 点调用 + 无 SolidWorks 标志）**%d**  ← ★ 降级，不计入真命中"
          % len(crosslib))
    #: ★★★ 生产 / 探针 分开报（★ 探针是**历史证据**，★ 改了会破坏"证据不可变" —— GATE-FINAL C12）
    print("        ★ 其中**生产（scripts/）**  **%d**  ← ★★ **只有这批该改**"
          % len([r for r in real if str(r.get("scope", "")).startswith("★ 生产")]))
    print("        ★ 其中探针/证据（tools/）**%d**  ← ★ **只报不动**"
          % len([r for r in real if str(r.get("scope", "")).startswith("★ 探针")]))
    print("   ★ 兜底分支（不算缺陷）  **%d**" % R["命中"]["兜底分支"])
    print("   ★ 疑似登记表（要人看）  **%d**" % R["命中"]["疑似登记表"])
    print()
    print("★ 真命中的成员分布（前 16）：")
    for m, n in agg.most_common(16):
        print("   %-34s %-3d ⇒ 后继 %s" % (m[:33], n, successor.get(m, "（官方没写）")[:36]))
    print()
    print("★ 抽 5 条回原文（★ S3）：")
    for r in real[:5]:
        print("   %s:%d  [%s]  %s" % (r["file"], r["line"], r["member"], r["ctx"][:88]))
    print()
    print("★ 产出:", OUT, "（%.1f s）" % (time.time() - started))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
