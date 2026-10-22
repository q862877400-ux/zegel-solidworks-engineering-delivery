"""门禁：代码里「官方没有 X」的断言，必须在**官方页**里核过 —— 断言与官方页相反即拦。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（与 check_member_names.py / check_interface_member_ownership.py 同为门禁）
# 文件:   scripts/check_official_md_claims.py —— 本文件自身
# 定位:   ★ 2026-10-03（接手轮）★ 由**一次真实误判**立起来的一道门禁。
#
#   ★★★ **为什么需要它（真因，★ 不是假想）**：
#     `scripts/sw_curve_and_split.py::insert_split_line_project` 原先逐字写着
#       「⚠ ★ 调用前要有**可选的分割工具**（草图 / 曲线 / 面）—— ★ 官方**没给 mark 表**，
#         ★ 故本模块**不假定 mark**」
#     并把它当返回值吐出来。★★ **而官方那一页的 `## Remarks` 里就有 mark 表**：
#       > The sketch to project must be selected using IModelDocExtension::SelectByID2
#       > with a mark value of **4**.
#       > The faces to split must be … with mark values of **1**.
#     ⇒ ★★ **后果很实**：真机失败被**归因成了"能力不成"**（台账里挂了 3 轮"待重查 mark 表"），
#       ★ 而**真正的原因是我没照官方 Remarks 选**。
#     ⇒ 于是立这条：★ **"官方没有 X"是可核对的断言** —— ★ 而它**必须真的核对过**。
#
#   ★★ 判据（★ 精确到"哪个成员、哪一页"）：
#     ```
#     ① 在 scripts/*.py 与 mcp-server/*.py 里找「否定词 + <token>」的断言
#        （当前 token 集 = {"mark"}；★ 它是本轮实证的缺陷类别）
#     ② 沿该行**向上**找最近的、**能解析到官方页**的成员名
#        （解析 = C:\swapi\types\**\<name>.md 存在 **且** 其 front-matter 的 `member:` == <name>）
#     ③ 解析不到 ⇒ **跳过并在输出里计数**（★ 不静默、也不猜）
#     ④ 解析到了 ⇒ 读那一页；★ 若页里**出现了该 token** ⇒ **违规**
#     ```
#     ⇒ ★ 第 ② 步的 `member:` 等值判据是**防假阳性的关键**：
#       ★ 只按文件名存在就认，会把 `Path` / `Name` 这种通用词也认成成员。
#
#   ★ **为什么这道门禁自己可信**：★ 它**在门禁运行时读官方源**（不是读我们自己的转述），
#     ⇒ ★ 官方页一改，门禁的判据跟着改（★ 与 check_member_names.py 同一个形态）。
#   ⚠ ★ **限度（如实写）**：★ token 集目前只有 `mark` —— ★ 它**不是**"所有官方断言"的通用校验器；
#     ★ 扩 token 只需往 `CLAIM_TOKENS` 里加，★ 而**判据不动**。
#   ⚠ 官方源不在本机 ⇒ `[SKIP]` 并**如实说明这是静默通过**（★ 与 check_member_names.py 同口径）。
# 官方依据: `C:\swapi\types\*\*.md` 的 YAML front-matter（`member:` 字段）+ 正文（`## Re
#           marks`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SWAPI = Path(r"C:\swapi")
TYPES = SWAPI / "types"

#: ★ 被校验的"断言 token"（★ 目前只有本轮实证的那一个；★ 加词只加这里）
CLAIM_TOKENS = ("mark",)

#: ★ 「否定词（+可选动词）+ token」= 一条"官方没有 X"的断言
_NEG = r"(?:未|没|没有|不曾|无|缺)"
_VERB = r"(?:给|提供|出|有)?"
CLAIM_RE = re.compile(
    r"%s\s*%s\s*\**\s*(%s)\b" % (_NEG, _VERB, "|".join(CLAIM_TOKENS)), re.I)

#: ★ 候选成员名的形态（防把散文里的词当成员）
MEMBER_RE = re.compile(r"\b(I?[A-Z][A-Za-z0-9_]{2,})\b")

#: ★ 只扫这两处（能力层与工具层 —— 断言都写在这）
SCAN_DIRS = ("scripts", "mcp-server")

#: ★ 本文件自己（判据里就含这些词，必然自命中）
SELF = Path(__file__).name

#: ★★ **不能当"没给 mark"断言的主语**的成员 —— ★ 它们**签名里本来就有 `Mark`**，
#:   ★ 对它们说"官方没给 mark"是**自相矛盾**（实测：解析会把 `SelectByID2` 认成主语）。
SUBJECT_EXCLUDE = {
    "SelectByID2", "SelectByID", "SelectByRay", "IModelDocExtension",
    "ISelectionMgr", "IModelDoc2", "IFeatureManager", "SelectionManager",
}

#: ★★ **"这条断言已被我撤回"的标记** —— ★ 出现在同一行就**不当活断言算**。
#:   ★ 为什么必须有：★ 本仓的规矩是**把错的那句留在原地、旁边写清它是错的**
#:   （★ 见 `sw_curve_and_split.py` 的更正段），★ 而那种**引述**不该被当成新违规。
#:   ⚠ 限度如实写明：★ 它**是一个可被滥用的排除**（★ 写上"更正"就能躲）——
#:   ★ 故门禁把跳过的条数**打印出来**，★ 让人看得见有多少条走了这条路。
QUOTED_MARKERS = ("更正", "此前", "原先", "曾经", "是错的", "是假的", "错了", "已被证伪", "撤销")


def _is_retracted(lines: list[str], lineno: int) -> bool:
    """★ 该行是不是「**已被我撤回的引述**」。

    ★ 判据：**本行或紧邻上方 2 行**里出现撤回标记 —— ★ 因为撤回的写法通常是
      「★★ 此前这里是 X」+ 下一行引述 X ⇒ ★ 引述那一行自己**不带**标记。
    """
    lo = max(0, lineno - 3)
    for i in range(lo, lineno):
        if i < len(lines) and any(mk in lines[i] for mk in QUOTED_MARKERS):
            return True
    return False

#: ★ 向上找主语的窗口（★ 越窄越不易误认；★ 窗口内主语不唯一就**跳过**）
WINDOW = 25

#: ★★ **已人工核对过的豁免** —— ★ 门禁"向上找主语"会在这两处**认错主语**：
#:   `scripts/sw_surface_ref_ops.py` 里那句"旋转曲面…没给 mark"，★ **真主语是
#:   `InsertRevolvedRefSurface`**（★ 它只出现在**下方**的"官方依据"块里 ⇒ 向上找不到），
#:   而门禁越过去认成了 `InsertProtrusionSwept3`。
#:   ⇒ ★★ **我逐字核过** `C:\swapi\types\{IFeatureManager,IModelDoc2}\InsertRevolvedRefSurface.md`：
#:     ★ 它的 `## Remarks` **确实一处 mark 都没有** ⇒ ★ **那句断言是对的**，★ 是门禁错、不是代码错。
#:   ⚠ 豁免**按 (文件, 被认错的主语, token)** 给 ⇒ ★ 只挡这一处，★ 不挡住该文件里别的断言。
ALLOWED = {
    ("scripts/sw_surface_ref_ops.py", "InsertProtrusionSwept3", "mark"):
        "主语认错：真主语是 InsertRevolvedRefSurface（官方页 Remarks 确实无 mark，已逐字核过）",
}


def _member_pages() -> dict[str, Path] | None:
    """★ 成员名 ⇒ 官方页路径（★ 以 front-matter 的 `member:` 为准，不靠文件名猜）。"""
    if not TYPES.is_dir():
        return None
    pages: dict[str, Path] = {}
    for page in TYPES.rglob("*.md"):
        try:
            head = page.read_text(encoding="utf-8", errors="replace")[:600]
        except OSError:
            continue
        m = re.search(r"^member:\s*(\S+)\s*$", head, re.M)
        if m:
            pages.setdefault(m.group(1), page)
    return pages


def _claims_in(path: Path):
    """★ 回报 ``[(lineno, token, claim_text)]``。"""
    out = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return out
    for i, line in enumerate(text.splitlines(), start=1):
        for m in CLAIM_RE.finditer(line):
            out.append((i, m.group(1).lower(), line.strip()[:160]))
    return out


def _resolve_upward(lines: list[str], lineno: int, pages: dict[str, Path]):
    """★ 从 ``lineno`` 往上找**唯一**的、能解析到官方页的**主语**成员名。

    ★ 三条纪律（★ 都是为了**别把假阳性当违规**）：
      ① 窗口 ``WINDOW`` 行；② 落在 ``SUBJECT_EXCLUDE`` 里的不作主语；
      ③ ★ **窗口内主语不唯一 ⇒ 返回 `("__ambiguous__", None)`**（★ 跳过并计数，不猜）。
    """
    lo = max(0, lineno - 1 - WINDOW)
    for i in range(lineno - 1, lo - 1, -1):
        if i >= len(lines):
            continue
        found = sorted({t for t in MEMBER_RE.findall(lines[i])
                        if t in pages and t not in SUBJECT_EXCLUDE})
        if not found:
            continue
        if len(found) > 1:
            return "__ambiguous__", i + 1
        return found[0], i + 1
    return None, None


def scan() -> tuple[list, int, int, int, int]:
    """★ 返回 ``(violations, claims_total, unresolved, quoted, exempted)``。"""
    pages = _member_pages() or {}
    violations, total, unresolved, quoted, exempted = [], 0, 0, 0, 0
    for d in SCAN_DIRS:
        root = REPO / d
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.py")):
            if path.name == SELF:
                continue
            claims = _claims_in(path)
            if not claims:
                continue
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            for lineno, token, text in claims:
                total += 1
                #: ★ 「我已撤回这条」的引述 ⇒ 不算活断言
                if _is_retracted(lines, lineno):
                    quoted += 1
                    continue
                member, mline = _resolve_upward(lines, lineno, pages)
                if member is None or member == "__ambiguous__":
                    unresolved += 1
                    continue
                #: ★ 已人工核对过的豁免（★ 带理由，★ 见文件头 ALLOWED）
                if (f"{d}/{path.name}", member, token) in ALLOWED:
                    exempted += 1
                    continue
                page = pages[member]
                body = page.read_text(encoding="utf-8", errors="replace")
                if re.search(r"\b%s\b" % re.escape(token), body, re.I):
                    snippet = ""
                    for ln in body.splitlines():
                        if re.search(r"\b%s\b" % re.escape(token), ln, re.I):
                            snippet = ln.strip()[:200]
                            break
                    violations.append({
                        "file": f"{d}/{path.name}", "line": lineno,
                        "member": member, "member_line": mline, "token": token,
                        "claim": text, "page": str(page), "page_says": snippet,
                    })
    return violations, total, unresolved, quoted, exempted


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if not TYPES.is_dir():
        print("[SKIP] 官方源 C:\\swapi 不在本机，无法校验（这是静默通过，不算通过）")
        return 0
    pages = _member_pages() or {}
    violations, total, unresolved, quoted, exempted = scan()
    print("官方断言门禁 · 官方成员页 %d 份 · 扫描目录 %s"
          % (len(pages), " / ".join(SCAN_DIRS)))
    print("  断言 %d 条（token 集 %s）· 引述已撤回 %d 条 · 主语不唯一/解析不到而**跳过** %d 条"
          " · 已核对豁免 %d 条 · 违规 %d 条"
          % (total, ",".join(CLAIM_TOKENS), quoted, unresolved, exempted, len(violations)))
    if not violations:
        return 0
    print("\n★ 以下断言与**官方页内容相反**（页里出现了被说成「没有」的东西）：")
    for v in violations:
        print("  %s:%d  成员 %s（第 %d 行处解析到）· token `%s`"
              % (v["file"], v["line"], v["member"], v["member_line"], v["token"]))
        print("      我方断言：%s" % v["claim"])
        print("      官方页（%s）里有：%s" % (v["page"], v["page_says"]))
    print("\n⇒ 修法：**照官方页改断言**（或删掉那句），★ 不要把「官方没写」当结论。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
