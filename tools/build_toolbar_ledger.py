"""★ 台账核实：把 `docs/toolbar-ledger.json` 里每个 api 名对**官方离线源**逐条核，并生成 Markdown 台账。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/build_toolbar_ledger.py
# 定位:   ★ 2026-10-03（轮 464）★ 用户要求「把这几轮截图问过的**列出台账**，按 spec 的纪律全部攻关」。
#   ★★ 台账数据在 `docs/toolbar-ledger.json`（★ 人工读图得来 = 需求原文）。
#   ★★★ **本脚本的职责不是重复那份数据，而是核实它** —— 因为表里 `api` 一列是**凭记忆写的**，
#     而**铁律 5**（查不到就说查不到）与**铁律 4**（签名三源互证）都要求它**逐条对官方源核过**。
#   ★ 三源（★ 本机可离线查的两套 + 一套结构化）：
#     ```
#     ① C:\swapi\types\<接口>\<成员>.md      ← ★ 结构化 markdown，查**精确成员名**（本脚本主用）
#     ② C:\swapi\enums\*.md                  ← 枚举值
#     ③ D:\AI\SW\AI Solidworks\官方文档\      ← CHM 解包，查语义与示例（本脚本只做存在性抽查）
#     ```
#   ⇒ ★ 输出：每条标 `api_verified`（★ 在①里找到的接口/成员）/ `api_missing`（★ 查不到 ⇒ 按铁律 5 记「查不到」）
#     并生成 `docs/toolbar-ledger.md`（★ 人看的台账）✓
# 官方依据: 本机 `C:\swapi\`（结构化官方源）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每个 api 名必须在 `C:\swapi\` 里**至少一处**命中（接口目录名或成员文件名）。

from __future__ import annotations

import ast
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
SWAPI = Path(r"C:\swapi")
LEDGER = R / "docs" / "toolbar-ledger.json"
OUT_MD = R / "docs" / "toolbar-ledger.md"
OUT_JSON = R / "docs" / "toolbar-ledger-verified.json"
CAPABILITIES = R / "capabilities.yaml"
#: ★ 模块级缓存（★ 供 promoted_by_capability 的默认参数）
VERIFIED_IDS: set = set()


def promoted_by_capability(item: dict, verified_ids: set | None = None) -> bool:
    """⇒ 这条台账条目是否该因 `capabilities.yaml` 而判「已能」。

    ★★★ 2026-10-03（轮 549）★ **为什么做成模块级函数**：★ 它**原先是 `tier()` 里内联的一段**，
      而 `tier()` 是 `main()` 里的**嵌套函数**、读的是外层变量 `_VERIFIED` ⇒
      ★ **抽出来单测就 `NameError`**（★ 那是**测试抓到的**，不是我自己想到的）⚠
      ⇒ ★ 故改成**自洽的模块级函数**：★ 依赖**显式传入或自己加载**，★ 不靠闭包 ✓
    """
    ids = VERIFIED_IDS if verified_ids is None else verified_ids
    cid = item.get("capability_id")
    return bool(cid and cid in ids)


def load_verified_capabilities() -> set:
    """⇒ `capabilities.yaml` 里 `level == "verified"` 的 id 集（★ 本轮新增）。

    ★★★ 2026-10-03（轮 549）**为什么加这个**（★ 那是一个真实记账 bug）：
      ★ `tier()` 原先**只用台账里手填的 `level`** —— 而**本脚本自己的 docstring 就写着**
      「台账那三条 `level` / `entry` 都是 2026-10-03 五轮问答时手填的，★ **之后从不自动更新**」⚠
      ⇒ ★★ **后果**：★ 轮 529-542 我把 **旋转曲面 / 等距曲面 / 平面区域 / 替换面 / 放样曲面 /
        水平尺寸 / 竖直尺寸** 等做成了 `verified`（★ 有真机证据），
        ★ 而**台账仍标它们「不能 / 没验过」** ⇒ ★ **下一步的攻关清单是错的** ⚠
      ⇒ ★ 修法：★ **先查 capabilities** —— ★ 台账条目可用 `capability_id` 指向能力条目，
        ★ 那条已 `verified` ⇒ ★ **直接判「已能」**（★ 而**不再依赖手填的 `level`**）✓
    """
    try:
        data = json.loads(CAPABILITIES.read_text(encoding="utf-8"))
    except Exception:                                                     # noqa: BLE001
        return set()
    caps = data.get("capabilities") or []
    return {c.get("id") for c in caps if c.get("level") == "verified" and c.get("id")}


def index_swapi() -> tuple[set, set]:
    """⇒ `(接口名小写集, 成员名小写集)`。"""
    ifaces, members = set(), set()
    t = SWAPI / "types"
    if not t.is_dir():
        return ifaces, members
    for d in t.iterdir():
        if not d.is_dir():
            continue
        ifaces.add(d.name.lower())
        try:
            for f in d.iterdir():
                if f.is_file() and f.suffix == ".md":
                    members.add(f.stem.lower())
        except OSError:
            pass
    return ifaces, members


def verify(api: str, ifaces: set, members: set) -> dict:
    """★ 逐条核：★ 取 api 文本里所有 `标识符`，看有没有命中官方源。"""
    ids = re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", api or "")
    hit_iface = [i for i in ids if i.lower() in ifaces]
    hit_member = [i for i in ids if i.lower() in members]
    return {"api_iface_hits": hit_iface, "api_member_hits": hit_member,
            "api_verified": bool(hit_iface or hit_member)}


def repo_index() -> dict:
    """★ **建「本仓源码索引」**：模块 → 该模块里定义的名字集 + 全仓源码拼成的文本。

    ★★★ 2026-10-03（轮 483）**为什么加这一层** ——
      上一轮（轮 482）核实 X 段时发现台账的**系统性盲点**（★ 已记进 **事实 379**）：
      · 台账那三条 `level` / `entry` **都是 2026-10-03 五轮问答时手填的**，★ **之后从不自动更新**；
      · 而★ `entry` 里填的名字**有的根本不存在** ⚠ ——
        ★ 实例：`"线性阵列"` 的 `entry` 写的是 **`sw_part.linear_pattern`**，
        而★ 本仓的真名是 **`sw_pattern.configure_linear_pattern`**（★ 模块都不一样）；
      · ★★ **而没有任何门禁查 `entry` 是否真存在** ⇒ ★ 那是个**假入口**，
        它让那条**显示成"待验证"而不是"可攻关"** ⇒ ★ **于是永远轮不到被攻关** ⚠

    ★ 本函数给两层**自动核实**依据：
      ① **`entry_exists`**：把 `entry`（`模块.函数`）拿去 `scripts/<模块>.py` 的 AST 里**真查**
         —— ★ 查不到就是**假入口**（★ 该降到"可攻关"，★ 而不是"待验证"）；
      ② **`implemented_hits`**：把 `api` 文本里的标识符拿去**全仓源码文本**里搜
         —— ★ 搜到就说明**本仓引用过那个官方成员**（★ 是"可能已实现"的强线索，
           ★ 而**不等于**"已能" —— ★ 那要真机证据，★ 见 `tier()`）。
    """
    mods: dict = {}
    srcs: list = []
    for d in (R / "scripts", R / "mcp-server", R / "tools"):
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.py")):
            try:
                txt = f.read_text(encoding="utf-8")
            except OSError:
                continue
            srcs.append(txt)
            names = set()
            if d.name == "scripts":
                try:
                    for n in ast.walk(ast.parse(txt)):
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                            names.add(n.name)
                except SyntaxError:
                    pass
            mods.setdefault(f.stem, set()).update(names)
    return {"modules": mods, "all_source": "\n".join(srcs)}


def check_repo(it: dict, idx: dict, official_ids: set) -> dict:
    """★ 对**一条台账**做两层本仓核实（★ 见 `repo_index` 的说明）。"""
    out = {"entry_exists": None, "entry_why": "", "implemented_hits": []}

    #: ① entry 真的存在吗（★ 只在 `scripts/` 里查 —— 台账的 entry 按约定指 `模块.函数`）
    #:
    #: ★★★ 2026-10-03（轮 483）**收紧判据 —— 第一版把通配当成了“不存在”** ⚠
    #:   ★ 第一版把 `sw_sketch_dimensions.*`、`sw_hole_features.*_report`、
    #:     `sw_sweep.create_sweep_report(cut=True)` **全判成“假入口”**（★ 共 10 条）
    #:     —— ★★ 而它们只是**模糊声明**（通配符 / 带参数的调用形式）。
    #:   ★★ 这正是**事实 62**：「一个门禁写了不等于它有效 —— **负例测试是唯一的证明**」。
    #:   ⇒ ★ 现在：**通配 / 带参 ⇒ 只核模块在不在**；★ 只有**具体函数名**才核函数在不在 ✓
    raw = str(it.get("entry") or "").strip()
    if raw:
        if ("*" in raw) or ("(" in raw):
            mod_only = raw.split(".")[0].strip()
            out["entry_exists"] = mod_only in idx["modules"]
            out["entry_why"] = "模糊声明（通配/带参）：只核模块 `%s`" % mod_only
        else:
            mod, _, fn = raw.partition(".")
            names = idx["modules"].get(mod)
            if names is None:
                out["entry_exists"] = False
                out["entry_why"] = "模块 `%s` 不在 scripts/ 里" % mod
            elif fn and fn not in names:
                out["entry_exists"] = False
                out["entry_why"] = "模块 `%s` 里没有 `%s`" % (mod, fn)
            else:
                out["entry_exists"] = True
                out["entry_why"] = "查到了"

    #: ② 本仓源码里出现没出现过那些官方标识符
    hits = sorted({i for i in official_ids
                   if i not in ("Entry", "Ref", "None") and i in idx["all_source"]})
    out["implemented_hits"] = hits
    return out


#: ★ 本仓索引（★ 由 `main()` 填）—— 两层本仓核实用（轮 483）
_IDX: dict = {}


def main() -> int:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    items = data["items"]
    ifaces, members = index_swapi()
    print("  官方源索引：接口 %d · 成员 %d" % (len(ifaces), len(members)))

    #: ★★ 两层本仓核实（轮 483）—— 见 `repo_index` 的说明
    _IDX.clear()
    _IDX.update(repo_index())
    print("  本仓索引：模块 %d 个 · 源码 %.1f 万字" % (len(_IDX["modules"]),
                                              len(_IDX["all_source"]) / 10000.0))

    for it in items:
        it.update(verify(it.get("api", ""), ifaces, members))
        #: ★★ 两层本仓核实（轮 483 加）—— ★ 见 `repo_index` 的说明
        ids = re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", it.get("api", "") or "")
        it.update(check_repo(it, _IDX, set(ids)))

    #: \u2605 \u5206\u6863\uff1a\u53ef\u505a = \u5f53\u524d"\u4e0d\u80fd/\u6ca1\u9a8c\u8fc7" \u4e14 api \u6838\u5b9e\u547d\u4e2d \u4e14 \u672c\u4ed3\u65e0\u5165\u53e3
    global VERIFIED_IDS
    VERIFIED_IDS = load_verified_capabilities()

    def tier(it: dict) -> str:
        #: ★★★ 2026-10-03（轮 549）**最先查 capabilities** —— ★ 修一个记账 bug：
        #:   原判据只用**手填的 `level`**（★ 而本脚本 docstring 自己写着「之后从不自动更新」）
        #:   ⇒ ★ 做成了的能力**永远不会被台账知道** ⚠
        #:   ★ 现在：条目若有 `capability_id` 且那条已 `verified` ⇒ **直接判「已能」** ✓
        #: ★ 改调**模块级函数**（★ 而不是内联 —— ★ 那样单测会 NameError）
        #: ★★ 而**不传第二个参数** ⇒ 走它的默认 `VERIFIED_IDS`（★ 那才是"自洽"的意思）
        if promoted_by_capability(it):
            return "已能"
        if it.get("level") == "\u80fd":
            return "\u5df2\u80fd"
        if not it.get("api_verified"):
            return "\u5f85\u67e5"
        #: ★★★ 轮 483 修掉那个盲点（★ 事实 379）：★ 原判据是 `not it.get("entry")`，
        #:   而 `entry` 是**手填的**、且**没人查它真不真** ⇒ ★ **假入口**
        #:   （如 `sw_part.linear_pattern`，真名其实在 `sw_pattern`）会让那条卡在“待验证”，
        #:   ★★ **永远轮不到被攻关** ⚠
        #:   ⇒ ★ 现在：**entry 不存在 ⇒ 按“无入口”算**（降为“可攻关”）✓
        real_entry = bool(it.get("entry")) and it.get("entry_exists") is not False
        return "\u53ef\u653b\u5173" if not real_entry else "\u5f85\u9a8c\u8bc1"

    for it in items:
        it["tier"] = tier(it)
    c = Counter(it["tier"] for it in items)
    c_tb = Counter(it["tb"] for it in items if it["tier"] == "\u53ef\u653b\u5173")
    print("  \u53f0\u8d26 %d \u6761 \u21d2 %s" % (len(items), dict(c)))
    print("  \u53ef\u653b\u5173\u6309\u5de5\u5177\u6761\uff1a%s" % dict(c_tb))

    #: \u2605 \u751f\u6210\u4eba\u770b\u7684\u53f0\u8d26
    lines = [
        "# 工具栏攻关台账",
        "",
        "> **本文件由 `tools/build_toolbar_ledger.py` 生成，不要手改。**",
        "> 数据源：`docs/toolbar-ledger.json`（用户 2026-10-03 五轮截图问过的全部条目 = 需求原文）。",
        "",
        "## 口径",
        "",
        "| 档 | 含义 |",
        "|---|---|",
        "| **已能** | 本仓有入口**且**有真机证据（`capabilities.yaml` 的 `verified` / evidence 文件） |",
        "| **可攻关** | 本仓**无入口**，而**官方成员在 `C:\\swapi\\` 里核到了** ⇒ 可以按官方签名立柱实现 |",
        "| **待验证** | 本仓有入口，但我还没跑成（判据要重做或入口要修） |",
        "| **待查** | 我填的 api 名在官方源里**没核到** ⇒ 按铁律 5 记「查不到」，先查清再动手 |",
        "",
        "## 汇总",
        "",
        "| 档 | 条数 |",
        "|---|---|",
    ]
    for k in ("已能", "可攻关", "待验证", "待查"):
        lines.append("| %s | %d |" % (k, c.get(k, 0)))
    lines.append("| **合计** | **%d** |" % len(items))
    lines += ["", "## 逐条", "", "| 工具条 | 条目 | 档 | 官方成员（已核） | 本仓入口 |", "|---|---|---|---|---|"]
    order = {"可攻关": 0, "待验证": 1, "待查": 2, "已能": 3}
    for it in sorted(items, key=lambda x: (order.get(x["tier"], 9), x["tb"], x["zh"])):
        hits = it["api_iface_hits"] + it["api_member_hits"]
        lines.append("| %s | %s | **%s** | %s | %s |" % (
            it["tb"], it["zh"], it["tier"],
            (", ".join("`%s`" % h for h in hits[:3]) or "—"),
            ("`%s`" % it["entry"]) if it.get("entry") else "—"))
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(
        {"_": "\u53f0\u8d26 + \u5b98\u65b9\u6e90\u6838\u5b9e\u7ed3\u679c", "summary": dict(c),
         "by_toolbar_gap": dict(c_tb), "items": items},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("  产物：%s" % OUT_MD)
    print("  产物：%s" % OUT_JSON)
    missing = [it["zh"] for it in items if it["tier"] == "\u5f85\u67e5"]
    if missing:
        print("  \u2605 \u5f85\u67e5\uff08api \u6ca1\u6838\u5230\uff0c\u5148\u67e5\u6e05\uff09\uff1a%s" % ", ".join(missing[:12]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
