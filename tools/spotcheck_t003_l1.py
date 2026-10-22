"""★ T003 抽查：把 `recon/bunny-L1-signature-transcribe.md` 的断言逐条拿**官方原文**核。

（★ 处置 SPEC `202-user-coverage-gaps` 的 **T003**）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `specs/202-user-coverage-gaps/recon/bunny-L1-signature-transcribe.md`（★ 被抽
# 查的侦察稿）·
#         `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`（★ 它的源）·
#         `C:\swapi\types\**`（★ 官方原文）
# 定位:   ★ SPEC 的 **T003** 逐字：「逐条**拿官方原文抽查**侦察结论 —— 宪法 §III
#   「**专挑最容易编造处**」；`docs/` 下留抽查记录」✓
# ★★ **为什么挑 L1**：★ 那是**纯抄录签名**那份 —— ★ **实参个数与成员名是最容易被编造的**
# 、
#     而**同时最好核**（★ 官方页一查就知道）✓
#   ★★★ **两条独立判据（★ 都要）**：
#     ★ ① **成员在不在** —— ★ 那个名字在 `C:\swapi\types\**` 里有没有一页；
#     ★ ② **形参个数对不对** —— ★ 官方签名里几个形参 vs ★ 侦察稿说的实参个数 ✓
#     ★★ 另核 **③ 行号** —— ★ 侦察稿指的行号在源文件里是不是那一行（★ 防止"行号编造"）✓
#   ★★★★ **只报不动**：★ 不改仓 · ★ 只写 `output/` ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
SWAPI = Path(r"C:\swapi\types")
SRC = REPO / "subskills" / "solidworks-engineering-drawing" / "scripts" / "drawing_workflow.py"
OUT = REPO / "output" / "t003-spotcheck-l1.json"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: ★ 侦察稿的断言（★ 逐条从 `bunny-L1-signature-transcribe.md` 抄来）
#:   字段：成员名 · 声称的**实参个数** · 声称的**调用行** · 出现在哪个函数
CLAIMS = [
    {"fn": "add_section_view", "member": "CreateSectionViewAt5", "args": 7, "line": 998},
    {"fn": "add_detail_view", "member": "CreateDetailViewAt4", "args": 12, "line": 1061},
    {"fn": "auto_insert_center_marks", "member": "AutoInsertCenterMarks2", "args": 10,
     "line": 1927},
    #: ★ 3.2 表里那 7 个不带实参个数的成员（★ 只核"在不在"）
    {"fn": "auto_insert_center_marks", "member": "GetCurrentSheet", "args": None, "line": 1890},
    {"fn": "auto_insert_center_marks", "member": "GetViews", "args": None, "line": 1891},
    {"fn": "auto_insert_center_marks", "member": "GetPathName", "args": None, "line": 1893},
    {"fn": "auto_insert_center_marks", "member": "ActivateView", "args": None, "line": 1925},
    {"fn": "auto_insert_center_marks", "member": "ForceRebuild3", "args": None, "line": 1943},
    {"fn": "auto_insert_center_marks", "member": "GraphicsRedraw2", "args": None, "line": 1944},
    #: ★ §3.4 附注里那四个（★ 辅助函数体里的）
    {"fn": "_view_center_marks", "member": "GetFirstCenterMark2", "args": None, "line": 1635},
    {"fn": "_view_center_marks", "member": "GetFirstCenterMark", "args": None, "line": 1637},
    {"fn": "_view_center_marks", "member": "GetNext", "args": None, "line": 1646},
    {"fn": "_view_center_marks", "member": "GetCenterMarks", "args": None, "line": 1650},
]

#: ★ 定义行的断言（★ 行号 + 是否逐字）
DEFS = [
    {"fn": "add_section_view", "line": 996, "text": "def add_section_view(drawing_model, x, y):"},
    {"fn": "add_detail_view", "line": 1020, "text": "def add_detail_view("},
    {"fn": "auto_insert_center_marks", "line": 1878,
     "text": "def auto_insert_center_marks(drawing_model, requirements) -> dict:"},
]

SIG = re.compile(r"\*\*Signature\*\*:\s*`([^`]+)`")


def official_signature(member: str) -> dict:
    """★ 去 `C:\\swapi\\types\\**` 找那个成员，★ 回它的签名与形参数。"""
    hits = []
    for f in SWAPI.rglob(member + ".md"):
        t = f.read_text(encoding="utf-8", errors="replace")
        g = SIG.search(t)
        hits.append({"iface": f.parent.name, "sig": g.group(1) if g else None})
    if not hits:
        return {"found": False}
    #: ★ 形参数：★ 从签名的括号里数顶层逗号 + 1（★ 空括号 = 0）
    out = []
    for h in hits:
        n = None
        if h["sig"] and "(" in h["sig"] and h["sig"].rstrip().endswith(")"):
            inner = h["sig"][h["sig"].index("(") + 1:h["sig"].rindex(")")].strip()
            n = 0 if not inner else inner.count(",") + 1
        out.append({**h, "params": n})
    return {"found": True, "hits": out}


def main() -> int:
    src_lines = (SRC.read_text(encoding="utf-8", errors="replace").splitlines()
                 if SRC.is_file() else [])
    R = {"★_目的": "T003 抽查 · recon/bunny-L1-signature-transcribe.md",
         "★_源文件": str(SRC), "★_源文件行数": len(src_lines),
         "★_判据": "① 成员在 C:/swapi/types 里有没有页 ② 官方形参数 vs 声称的实参数 ③ 行号对不对",
         "members": [], "defs": []}

    print("=" * 78)
    print("★ 判据 ① + ②：成员在不在 · 形参数对不对")
    for c in CLAIMS:
        o = official_signature(c["member"])
        row = {"member": c["member"], "fn": c["fn"], "声称实参": c["args"],
               "行": c["line"], "官方找到": o["found"]}
        if o["found"]:
            row["官方命中"] = [{"interface": h["iface"], "params": h["params"],
                             "sig": (h["sig"] or "")[:150]} for h in o["hits"]]
            #: ★ 判据：★ 只要**有一个**接口的形参数与声称相等 ⇒ 就算对得上
            row["形参数相符"] = any(h["params"] == c["args"] for h in o["hits"]) \
                if c["args"] is not None else None
        R["members"].append(row)
        flag = "✓" if o["found"] else "✗"
        extra = ""
        if o["found"] and c["args"] is not None:
            ps = [h["params"] for h in o["hits"]]
            extra = " · 官方形参数=%s · 相符=%s" % (ps, row["形参数相符"])
        print("  %s %-24s 声称实参=%-4s%s" % (flag, c["member"], c["args"], extra))

    print("=" * 78)
    print("★ 判据 ③：行号对不对（★ 直接读源文件那一行）")
    for d in DEFS:
        got = src_lines[d["line"] - 1].strip() if 0 < d["line"] <= len(src_lines) else None
        ok = (got == d["text"].strip()) if got is not None else None
        R["defs"].append({"fn": d["fn"], "line": d["line"], "声称": d["text"],
                          "实读": got, "相符": ok})
        print("  %s L%-5d 声称=%s" % ("✓" if ok else "✗", d["line"], d["text"][:70]))
        if not ok:
            print("           实读=%s" % str(got)[:80])

    #: ★ 调用行的实参个数（★ 从源文件逐字数括号里的顶层逗号）—— ★ 独立复核判据②
    print("=" * 78)
    print("★ 判据 ②'：★ 直接从源文件数那个调用的实参个数")
    for c in CLAIMS:
        if c["args"] is None:
            continue
        lo = max(0, c["line"] - 1)
        chunk = "\n".join(src_lines[lo:lo + 20])
        i = chunk.find(c["member"])
        n = None
        if i >= 0:
            j = chunk.find("(", i)
            if j >= 0:
                depth, comm, k = 1, 0, j + 1
                while k < len(chunk) and depth > 0:
                    ch = chunk[k]
                    if ch in "([{":
                        depth += 1
                    elif ch in ")]}":
                        depth -= 1
                        if depth == 0:
                            break
                    elif ch == "," and depth == 1:
                        comm += 1
                    k += 1
                body = chunk[j + 1:k].strip()
                n = 0 if not body else comm + 1
        for row in R["members"]:
            if row["member"] == c["member"]:
                row["源文件数出的实参"] = n
                row["源文件与声称相符"] = (n == c["args"]) if n is not None else None
        print("  %-24s 声称=%-4s 源文件数出=%s" % (c["member"], c["args"], n))

    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    m_found = sum(1 for r in R["members"] if r["官方找到"])
    m_arity = [r for r in R["members"] if r.get("形参数相符") is not None]
    d_ok = sum(1 for r in R["defs"] if r["相符"])
    print("=" * 78)
    print("★ 汇总：★ 成员 %d/%d 在官方源找到 · ★ 形参数相符 %d/%d · ★ 定义行号相符 %d/%d"
          % (m_found, len(R["members"]),
             sum(1 for r in m_arity if r["形参数相符"]), len(m_arity), d_ok, len(R["defs"])))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
