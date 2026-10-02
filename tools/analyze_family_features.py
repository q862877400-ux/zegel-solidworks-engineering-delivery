"""抽「接口族的结构特征」，用来回答一件事：

  **「我们认定值得做并做了的族」与「还没做的族」在结构上有什么可判别的差异？**

## 为什么这么做（2026-10-01 轮 212）
用户给的方法是对的：**别靠感觉判「该不该做」，先从已经确定的正例里反推判据。**
- 正例集 = `docs/family-coverage.json` 里 `used > 0` 的族（**我们做过并且在用**）
- 待判集 = 同一台账里 `used == 0` 的族（其中 **51 个候选池**：零调用 + 有官方分类 + 属"建模型动作"类）
- 特征源 = `C:\\swapi\\types\\<接口>\\*.md` 的 **front-matter**（每个成员文件带 `kind:`）

⚠ 本脚本**只读**：读 `C:\\swapi`（只读源）与台账 JSON，写一个分析产物到 `D:\\AI\\SW\\output\\`。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（分析工具，非第三方移植；本文件在**工作区仓库**）
# 文件:   D:\\AI\\SW\\tools\\analyze_family_features.py
# 定位:   为「51 个候选族逐个过一遍」提供**可机器判定的特征**，取代凭感觉。
# 官方依据: `C:\\swapi\\types\\<接口>\\*.md` 的 front-matter（`kind: method|property`）
# 许可:   本仓库 MIT（工作区产物）。⚠ 输入源 `C:\\swapi` 的派生数据不入闭源分发。
# ⚠ 本工具只做**静态统计**，不连 SolidWorks。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8")

SWAPI = Path(r"C:\swapi\types")
EXAMPLES = Path(r"C:\swapi\examples")
LEDGER = Path(r"" + _ROOT_S + r"\docs\family-coverage.json")
OUT = Path(r"D:\AI\SW\output\family-features.json")

#: 接口名里的「动作词」—— 我们做过的族里这类接口多是"干活的动作"
ACTION_WORDS = re.compile(
    r"Create|Add|Insert|Set|Modify|Delete|Remove|Export|Import|Run|Build|Make|Save|Load|Select",
    re.I,
)


def _front(text: str, key: str) -> str:
    m = re.search(r"(?m)^%s:\s*(.+)$" % key, text[:800])
    return m.group(1).strip() if m else ""


def interface_features(iface: str) -> dict:
    """一个接口族的结构特征（全部来自 front-matter，**不猜**）。"""
    d = SWAPI / iface
    feat = {
        "iface": iface,
        "exists": d.is_dir(),
        "methods": 0, "properties": 0, "other": 0, "obsolete": 0,
        "members": 0, "has_example": False, "action_word": bool(ACTION_WORDS.search(iface)),
    }
    if not d.is_dir():
        return feat
    for p in d.glob("*.md"):
        if p.name == "_overview.md":
            continue
        feat["members"] += 1
        txt = p.read_text(encoding="utf-8", errors="replace")
        kind = _front(txt, "kind").lower()
        if kind == "method":
            feat["methods"] += 1
        elif kind == "property":
            feat["properties"] += 1
        else:
            feat["other"] += 1
        if "Obsolete" in txt[:600]:
            feat["obsolete"] += 1
    return feat


def main() -> int:
    rows = json.loads(LEDGER.read_text(encoding="utf-8"))
    ex_names = ""
    if EXAMPLES.is_dir():
        ex_names = "\n".join(p.stem for p in EXAMPLES.glob("*.md"))

    out = []
    for r in rows:
        iface = r["family"]
        f = interface_features(iface) if f"{iface}" and (SWAPI / iface).is_dir() else {
            "iface": iface, "exists": False, "methods": 0, "properties": 0,
            "other": 0, "obsolete": 0, "members": 0, "has_example": False,
            "action_word": bool(ACTION_WORDS.search(iface)),
        }
        f["iface"] = iface
        f["domain"] = r.get("domain", "")
        f["official_category"] = r.get("official_category", "")
        f["used"] = r.get("used") or 0
        f["hit"] = r.get("hit") or 0
        f["ledger_members"] = r.get("members") or 0
        #: 官方示例提到该接口名（粗匹配，够用）
        f["in_examples"] = bool(ex_names) and (iface in ex_names)
        out.append(f)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    done = [f for f in out if f["used"] > 0]
    todo = [f for f in out if f["used"] == 0 and f["ledger_members"] > 0]
    def stat(arr, label):
        n = len(arr)
        if not n:
            print("  %-24s (空)" % label); return
        with_m = sum(1 for f in arr if f["methods"] > 0)
        only_p = sum(1 for f in arr if f["methods"] == 0 and f["properties"] > 0)
        ex = sum(1 for f in arr if f["in_examples"])
        aw = sum(1 for f in arr if f["action_word"])
        print("  %-24s %4d 族 · **有方法的 %3d(%.0f%%)** · 只有属性的 %3d(%.0f%%) · 官方示例提到 %3d(%.0f%%) · 名含动作词 %3d(%.0f%%)"
              % (label, n, with_m, 100.0*with_m/n, only_p, 100.0*only_p/n, ex, 100.0*ex/n, aw, 100.0*aw/n))
    print("  ── 特征对比（正例 vs 未做）──")
    stat(done, "★ 做过的（used>0）")
    stat(todo, "  有成员但没做过")
    print()
    print("  产物:", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
