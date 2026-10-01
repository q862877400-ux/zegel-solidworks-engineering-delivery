import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\THIRD-PARTY-NOTICES.md")
t = P.read_text(encoding="utf-8")

OLD = "| 2026-10-01 | 初版。如实区分「已包含」（上游 + microsoft/UFO）与「已评估未并入」（四家）。四家的许可与版权已逐份读真实 `LICENSE` 文件核到，不采信 README 徽章。 |"
NEW = OLD + "\n" + (
    "| 2026-10-01（轮 131）| **复核 + 加机器检查**。"
    "① 复核结论：`capabilities.yaml` 里 `level: source_verified` 的条目**仍为 0** ⇒ "
    "第二节那句「尚未有来源派生的能力条目」**依然成立**；"
    "带 `provenance` 字段的条目**只有 `mold_tools` 一条**（`Eduardof0nt/Solidworks-MCP-Server`，MIT，"
    "**只取思路、没抄代码**，见 §一.3）。"
    "② 复核 §一.4 的依赖清单：`pyproject.toml` 与 `requirements*.txt` 对得上"
    "（`numpy` 在 `requirements-mesh.txt` / `requirements-occt.txt` 里，不是写错）。"
    "③ **新增机器检查** `tests/test_notice_consistency.py`（5 条）："
    "**能力条目里出现的每个外部 owner 都必须在 NOTICE 里有登记**、"
    "`provenance` 四字段齐、repo 写 `owner/repo` 全名、Apache-2.0 义务点名到位、"
    "**登记历史必须不止一条** —— 也就是本节这条规则本身。 |"
)

if "轮 131" not in t:
    assert OLD in t, "登记历史锚点不符"
    P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("  ok 已补登记历史（轮 131）")
else:
    print("  已有轮 131 条目")
print("  现在 %d 行" % len(P.read_text(encoding='utf-8').splitlines()))
