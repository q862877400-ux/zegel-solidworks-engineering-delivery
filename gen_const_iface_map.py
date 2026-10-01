r"""@brief 从**官方文本**生成 `swFeatureNameID_e 常量 → FeatureData 接口` 映射。

## 为什么需要它（第 29 轮的否定结果逼出来的）
第 29 轮证明「成员交集为空」这个判据**抓不到「整体用错接口」**（已知事实 42）。
**⇒ 要抓那一类，必须有 `CONST → 接口` 映射表。**
而**手写**那张表 = 新的错误来源 ⇒ 本脚本**从官方文本生成**它。

## 官方链路（两侧都是官方文本，描述同一件事）
```
① C:\swapi\types\IFeatureManager\CreateDefinition.md 的 Parameters 段：
     "- swFmSMGusset (**sheet metal gusset**)"          ← 常量的官方描述
② C:\swapi\types\<接口>\_overview.md 的 Description 段：
     "Allows access to a **sheet metal gusset** feature."  ← 接口的官方描述
     category: Feature Interfaces/Sheet Metal
```
**⇒ 判据：把常量描述的括注与接口 Description 做**规范化子串匹配**。**

## ⚠ 本脚本的自我约束
* **多命中不猜** —— 记成「歧义」，交给人看（宁可不说，不可说错）。
* **零命中不编** —— 记成「未映射」。
* **不写进任何文件** —— 只**打印**，由人决定是否采纳。
  （理由：自动写映射表 = 让一个未复核的推断成为后续检查的依据。）

# ── 来源 ──
# 仓库:   SolidWorks 官方 API 文档（`C:\swapi\`，结构化 markdown）
# 文件:   `types\IFeatureManager\CreateDefinition.md`（常量 + 括注描述）
#         `types\<接口>\_overview.md`（Description + category）
# 定位:   已知事实 42 的**后续**：那张必需的 `CONST → 接口` 映射表，
#         用官方文本生成而不是手写。
# 官方签名依据: `System.object CreateDefinition( System.int Type )`
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 纯静态（读官方 markdown），**不连 SolidWorks**。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SWAPI = Path(r"C:\swapi")
CD_DOC = SWAPI / "types" / "IFeatureManager" / "CreateDefinition.md"
TYPES = SWAPI / "types"

#: `- swFmXxx (描述文字)` —— CreateDefinition.md 里的常量行
CONST_RE = re.compile(r"^\s*-\s*(swFm\w+)\s*\(([^)]*)\)\s*$", re.M)


def norm(s: str) -> str:
    """规范化：小写、去标点、压缩空白、去冠词 —— 只用于**比对**。"""
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\b(a|an|the|of|to|for|and|or)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def load_constants(path: Path) -> dict:
    """``{常量名: 官方括注描述}``。"""
    if not path.is_file():
        return {}
    return {m.group(1): m.group(2).strip()
            for m in CONST_RE.finditer(path.read_text(encoding="utf-8"))}


def load_iface_descriptions(types_dir: Path) -> dict:
    """``{接口名: (Description 文本, category)}``。"""
    out = {}
    if not types_dir.is_dir():
        return out
    for d in types_dir.iterdir():
        if not d.is_dir() or not d.name.startswith("I"):
            continue
        f = d / "_overview.md"
        if not f.is_file():
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"##\s*Description\s*\n+(.+?)(?=\n##|\Z)", t, re.S)
        desc = " ".join(m.group(1).split()) if m else ""
        c = re.search(r"^category:\s*(.+)$", t, re.M)
        out[d.name] = (desc, c.group(1).strip() if c else "")
    return out


def main(argv=None) -> int:
    consts = load_constants(CD_DOC)
    if not consts:
        print("[SKIP] 官方 `CreateDefinition.md` 不在或格式变了 —— 缺数据源不算违规")
        return 0
    ifaces = load_iface_descriptions(TYPES)
    print("官方常量（CreateDefinition 的 Parameters 段）：**%d** 个" % len(consts))
    print("官方接口（有 Description 的）：%d 个" % len(ifaces))

    mapped, ambiguous, unmatched = [], [], []
    for cname, cdesc in sorted(consts.items()):
        key = norm(cdesc)
        if not key:
            unmatched.append((cname, cdesc, "描述为空"))
            continue
        hits = [(iname, d, cat) for iname, (d, cat) in ifaces.items()
                if key and key in norm(d)]
        if len(hits) == 1:
            mapped.append((cname, cdesc, hits[0][0], hits[0][2]))
        elif len(hits) > 1:
            ambiguous.append((cname, cdesc, [h[0] for h in hits]))
        else:
            unmatched.append((cname, cdesc, "接口 Description 里找不到该措辞"))

    print()
    print("── ✅ 唯一命中的映射：**%d** 个 ──" % len(mapped))
    for c, cd, i, cat in mapped:
        print("   %-28s → %-34s  [%s]" % (c, i, cat))
    print()
    print("── ⚠ 歧义（多命中，**不猜**）：%d 个 ──" % len(ambiguous))
    for c, cd, names in ambiguous[:8]:
        print("   %-28s (%s) → %r" % (c, cd[:32], names[:4]))
    print()
    print("── ✗ 未映射：%d 个 ──" % len(unmatched))
    for c, cd, why in unmatched[:16]:
        print("   %-28s (%s)  %s" % (c, cd[:34], why))
    print()
    print("=" * 70)
    print("⚠ **本脚本只打印，不写任何文件** —— 自动写映射表会让未复核的推断")
    print("   成为后续检查的依据。采纳与否由人定。")
    print("⚠ 判据是**官方文本的规范化子串匹配**，不是语义理解：")
    print("   措辞不同就漏（记入「未映射」），**多命中一律记歧义**（宁可不说，不可说错）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
