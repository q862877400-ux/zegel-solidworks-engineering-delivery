"""T003 抽查（第二份）：核 `recon/bunny-L2-official-member-calls.md` 的 143 个成员名。

（处置 SPEC `202-user-coverage-gaps` 的 T003；第一份见 `tools/spotcheck_t003_l1.py`）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `specs/202-user-coverage-gaps/recon/bunny-L2-official-member-calls.md` ·
#         `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py` · `C:\swapi\types\**`
# 定位:   ★ SPEC 的 **T003** 逐字：「逐条**拿官方原文抽查**侦察结论 —— 宪法 §III
#   「**专挑最容易编造处**」」✓
#   ★★ **L2 比 L1 厚得多**：★ 它自称「函数总数 **83** / 调用了至少一个官方成员的 **67** /
#     全文去重后的官方成员名共 **143** 个」⇒ ★★ **⇒ 那 143 个名字是最容易编造的一类断言**、
#     而**同时最好核**（★ 官方页一查就知道在不在）✓
#   ★★★ **两条判据**：
#     ★ ① **143 个名字逐个**去 `C:\swapi\types\**` 查有没有一页 —— 报**没找到**的那些；
#     ★ ② **顺带核它 §五 那条**代码断言**：★ 「`Any` 未导入」——
#       ★ 那是**可直接读源码验的**（★ SPEC 的"专挑最容易编造处"里，**代码断言也是**）✓
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
L2 = REPO / "specs" / "202-user-coverage-gaps" / "recon" / "bunny-L2-official-member-calls.md"
SRC = (REPO / "subskills" / "solidworks-engineering-drawing" / "scripts"
       / "drawing_workflow.py")
OUT = REPO / "output" / "t003-spotcheck-l2.json"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: ★ 官方成员名的形状：★ 大驼峰、不以 `_` 开头、★ 长度 ≥ 3
NAME_RE = re.compile(r"^[A-Z][A-Za-z0-9]{2,}$")


def claimed_names(text: str) -> list:
    """★ 从那张对照表的**最后一列**里抽成员名。

    ★ 行形如：`| 30 | `insert_dimensions` | 1079 | `ActivateView`、`Extension`、… |`
    ⇒ ★ 取**第 4 列**（★ 用 `|` 切、★ 索引 4）、★ 再抽反引号里的标识符 ✓
    """
    names, rows = {}, 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 4:
            continue
        if not re.match(r"^\d+$", cells[0]):          #: ★ 只要数据行（# 列是数字）
            continue
        rows += 1
        for m in re.finditer(r"`([^`]+)`", cells[3]):
            n = m.group(1).strip()
            #: ★ 去掉行内标记（※ 属性 / ◇ 动态派发 / ＋DISPID …）
            n = re.sub(r"[※◇].*$", "", n).strip()
            if NAME_RE.match(n):
                names.setdefault(n, []).append(cells[1].strip("`"))
    return rows, names


def main() -> int:
    text = L2.read_text(encoding="utf-8", errors="replace")
    rows, names = claimed_names(text)
    R = {"★_目的": "T003 抽查 · recon/bunny-L2-official-member-calls.md",
         "★_声称": "函数总数 83 / 有成员的 67 / 去重成员名 143",
         "★_解析到的数据行": rows, "★_解析到的成员名数": len(names),
         "★_判据": "① 每个成员名在 C:/swapi/types 里有没有页 ② 顺带核它的代码断言",
         "成员": {}, "没找到": [], "代码断言": {}}

    print("★ 对照表数据行 %d 行 · ★ 解析到**去重成员名 %d 个**（★ L2 自称 143）"
          % (rows, len(names)))
    print("=" * 78)
    print("★ 判据①：逐个去 C:/swapi/types 查有没有一页")
    for n in sorted(names):
        #: ★ 官方页名 = 成员名 + `.md`（★ 大小写敏感；★ 先在 types/ 下递归找）
        found = any(SWAPI.rglob(n + ".md"))
        R["成员"][n] = {"找到": found, "出现于函数": sorted(set(names[n]))[:6]}
        if not found:
            R["没找到"].append(n)
    ok = len(names) - len(R["没找到"])
    print("   ★ 找到 **%d / %d** ⇒ 没找到 **%d** 个" % (ok, len(names), len(R["没找到"])))
    if R["没找到"]:
        print("   ★★ 没找到（★ 编造嫌疑 / ★ 或名字属于**枚举/常量**不是成员）：")
        for n in R["没找到"]:
            print("      %-34s ← 出现在 %s" % (n, R["成员"][n]["出现于函数"][:3]))

    print("=" * 78)
    print("★ 判据②：核它 §五 那条**代码断言**（★ 「Any 未导入」）")
    src = SRC.read_text(encoding="utf-8", errors="replace")
    head = "\n".join(src.splitlines()[:60])
    has_any_import = bool(re.search(r"^\s*from typing import .*\bAny\b", src, re.M))
    has_future = "from __future__ import annotations" in src
    uses_any = bool(re.search(r"\bdict\[str,\s*Any\]", src))
    R["代码断言"] = {"用到 dict[str, Any]": uses_any,
                 "有 from typing import Any": has_any_import,
                 "有 from __future__ import annotations": has_future,
                 "文件顶部 60 行的 import": [l.strip() for l in head.splitlines()
                                        if l.strip().startswith(("import ", "from "))][:8]}
    print("   ★ 用到 `dict[str, Any]`：%s" % uses_any)
    print("   ★ 有 `from typing import Any`：**%s**" % has_any_import)
    print("   ★ 有 `from __future__ import annotations`：%s" % has_future)
    print("   ★ 顶部 import：%s" % R["代码断言"]["文件顶部 60 行的 import"])
    R["代码断言"]["L2 的说法成立"] = bool(uses_any and not has_any_import)

    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("=" * 78)
    print("★ 汇总：★ 成员名 %d/%d 在官方源找到 · ★「Any 未导入」这条断言 %s"
          % (ok, len(names),
             "成立" if R["代码断言"]["L2 的说法成立"] else "**不成立**"))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
