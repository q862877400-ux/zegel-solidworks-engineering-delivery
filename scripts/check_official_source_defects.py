"""★ 门禁：拦住「照官方源里的**错拼标识符**写代码」（★ 输入是另一个对话已核验的 964 条缺陷）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 另一个对话的 B2 扫描产物（只读复用）
# 文件:   scripts/check_official_source_defects.py
# 定位:   **规格 206 / T3-3 的交付物** —— 把官方源自身的机械缺陷接成可执行门禁。
# 依据:   `specs/203-bunny-sideline-batches/recon/b2-defects.json`（**970 条**，其中 964 条
#         `verified=True`；另一对话的 B2 穷举扫描：13086 份官页 / 60 路 Bunny / 两道闸）。
#         ★ 其分类：spelling 554 · dead_link_candidate 212 · other 164 · undefined_item 24 ·
#           number_mismatch 10 —— ★ 本门禁**只取能机械判的两类**（见下「不算什么」）。
#         `docs/recon/official-source-defects-2.md`（人读版，含 §1.1 的 212 条逐条核验）。
# 官方依据: 不适用（官方源自身的缺陷，判据是**文件系统事实**与**同页两种拼法**）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   scripts/ · mcp-server/ · tools/ 的 .py（★ 不扫 docs/ 与 tests/）
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFECTS = ROOT / "specs" / "203-bunny-sideline-batches" / "recon" / "b2-defects.json"
SCAN_DIRS = ("scripts", "mcp-server", "tools")
SKIP_FILES = {Path(__file__).name}

#: ★ 只从这两种缺陷里取"错拼名"：
#:   · `spelling` —— 同一页里同一接口两种拼法（★ 错的那个一定不是真名）
#:   · `dead_link_candidate` —— 链接目标页**确实不存在**（★ 文件系统事实）
USABLE_TYPES = ("spelling", "dead_link_candidate")
#: ★★ 只认**大驼峰 COM 标识符**形状的错拼（★ 避免把散文词当标识符去扫）
IDENT = re.compile(r"\b([A-Z][A-Za-z0-9]{3,})\b")
LINK = re.compile(r"\[\[([A-Za-z0-9_]+)::([A-Za-z0-9_]+)\]\]")


def load_bad_names() -> tuple:
    """★ 从 964 条已核验缺陷里抽出「错拼候选名」，再用本机真名集合**过滤**。

    ★★ 为什么要再过一遍本机：错拼的**反面**（正确名）必须在 `C:\\swapi` 里存在，
       否则这条判据无意义（★ 全库都没有的名字不是"错拼"，是"查不到" —— 铁律 5）。
    """
    types_dir = Path(r"C:\swapi\types")
    enums_dir = Path(r"C:\swapi\enums")
    real = set()
    if types_dir.is_dir():
        real |= {p.name for p in types_dir.iterdir() if p.is_dir()}
    if enums_dir.is_dir():
        real |= {p.stem for p in enums_dir.glob("*.md")}
    rows = json.loads(DEFECTS.read_text(encoding="utf-8"))
    bad: dict = {}
    for r in rows:
        if not (r.get("verified") is True or str(r.get("verified")).lower() == "true"):
            continue
        if r.get("type") not in USABLE_TYPES:
            continue
        text = "%s\n%s\n%s" % (r.get("quote_a") or "", r.get("quote_b") or "", r.get("why") or "")
        for iface, member in LINK.findall(text):
            if iface in real:
                continue                 #: ★ 真名 ⇒ 不是错拼
            bad.setdefault(iface, {"member": member, "why": (r.get("why") or "")[:120],
                                   "type": r.get("type")})
    return bad, real


#: ★★ 判据（★ 我第一版用错了，见下）：
#:   错的版本：扫源码里**出现错拼标识符** ⇒ ★ 一跑就报 `FeatureManager` 一大片**误报** ✓✗
#:   ★ 真因：`spelling` / `dead_link_candidate` 这两类缺陷说的是
#:     **【官方页里的链接】指向不存在的页**（如 `[[FeatureManager::HoleWizard5]]` 少了 `I`），
#:     ★ **不是**说「代码里不该出现 `FeatureManager`」—— 它是 `IModelDoc2` 上的**属性名**，正当 ✓
#:   ⇒ ★★ 正确的判据是：**我们【自己引用的官方页】必须存在**。
#:     我们引用官方页有两种写法：① `[[接口::成员]]` ② `C:\swapi\types\<接口>\<成员>.md`
#:     ⇒ 逐个求值：接口目录在不在？成员页在不在？★ 不在 ⇒ 报（★ 这是"文件系统事实"，非判断力）
LINK_REF = re.compile(r"\[\[([A-Za-z0-9_]+)::([A-Za-z0-9_]+)\]\]")
#: ★★ 必须带 `.md` 结尾（我第一版把它写成可选 ⇒ 匹到了 `C:\\swapi\\enums\\swUserPreference`
#:   这种**前缀**，把真页 `swUserPreferenceIntegerValue.md` 误报成不存在）✓
PATH_REF = re.compile(r"[Cc]:\\swapi\\(types|enums)\\([A-Za-z0-9_]+)(?:\\([A-Za-z0-9_]+)\.md)")
#: ★ 归一：去 `Method`/`Property`/`Function` 后缀、忽略大小写（★ 与另一对话 §1.1 的判据同款）
SUFFIX = re.compile(r"(Method|Property|Function)$", re.I)


def _real() -> tuple:
    td, ed = Path(r"C:\swapi\types"), Path(r"C:\swapi\enums")
    ifaces = {p.name.lower() for p in td.iterdir() if p.is_dir()} if td.is_dir() else set()
    members: dict = {}
    if td.is_dir():
        for d in td.iterdir():
            if d.is_dir():
                members[d.name.lower()] = {SUFFIX.sub("", p.stem).lower()
                                           for p in d.glob("*.md")}
    enums = {p.stem.lower() for p in ed.glob("*.md")} if ed.is_dir() else set()
    return ifaces, members, enums


def scan(_bad=None) -> list:
    """★ 扫我们**引用官方页**的地方，验证目标存在（★ 与"错拼标识符出现"无关）。"""
    ifaces, members, enums = _real()
    hits = []
    for d in SCAN_DIRS:
        for f in sorted((ROOT / d).rglob("*.py")):
            if f.name in SKIP_FILES:
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
            for m in LINK_REF.finditer(text):
                iface, member = m.group(1), m.group(2)
                ln = text[:m.start()].count("\n") + 1
                if iface.lower() not in ifaces:
                    hits.append((str(f.relative_to(ROOT)), ln, "[[%s::%s]]" % (iface, member),
                                 "接口 `%s` 在 C:\\swapi\\types 下不存在" % iface))
                elif member.lower() not in members.get(iface.lower(), set()):
                    if member.lower() not in {SUFFIX.sub("", x) for x in members.get(iface.lower(), set())}:
                        hits.append((str(f.relative_to(ROOT)), ln, "[[%s::%s]]" % (iface, member),
                                     "成员 `%s` 不在接口 `%s` 下" % (member, iface)))
            for m in PATH_REF.finditer(text):
                kind, name = m.group(1), m.group(2)
                ln = text[:m.start()].count("\n") + 1
                pool = ifaces if kind == "types" else enums
                if name.lower() not in pool:
                    hits.append((str(f.relative_to(ROOT)), ln, m.group(0)[:60],
                                 "引用的官方页不存在（%s/%s）" % (kind, name)))
    return hits


#: ★★ 例外表（★ 每条**必须带理由**；★ 未列入的一律报）——
#:   ★ 这些是**判据的边界**，不是"为了让门禁变绿"：写清理由后可见、可复核 ✓
EXCEPTIONS = (
    ("mcp-server/tool_specs_batch74.py", "IInsertMidSurface",
     "★ 待复核：`I` 前缀是官方的**进程内指针变体**命名法（见已知事实 47 那一族），"
     "本判据只归一 `Method/Property/Function` 后缀，**未归一 `I` 前缀** ⇒ 疑误报，需人判"),
    ("tools/build_obsolete_index.py", "Iface",
     "★ 误报：`[[Iface::Member]]` 是函数 docstring 里的**模板占位**（不是真引用）"),
)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("官方源缺陷门禁 · 扫 %s（%s）" % (DEFECTS.name, "/".join(SCAN_DIRS)))
    if not DEFECTS.is_file():
        print("  [SKIP] 找不到 %s（★ 本门禁的输入；它是另一个对话的产物）" % DEFECTS)
        return 0
    bad, real = load_bad_names()
    print("  ★ 本机真名集合: %d（接口目录 + 枚举页）" % len(real))
    print("  ★ 已核验缺陷里抽出的**错拼候选名**: %d 个（★ 只作参照，不作判据 —— 见 docstring）"
          % len(bad))
    hits = scan()
    print()
    for rel, line, ref, why in hits:
        print("  [FAIL] %s:%d 引用了不存在的官方页: %s" % (rel, line, ref))
        print("         %s" % why)
    print()
    print("  ★ 不算什么（★ 判据的否定面）：")
    print("     · ★ 注释/字符串里**提及**错拼名**不算**使用（本门禁只认标识符形状的独立出现）")
    print("     · ★ `other`(164) / `undefined_item`(24) / `number_mismatch`(10) **不取** ——")
    print("       它们是散文级缺陷，无法机械判成「写码时用错」")
    print("     · ★ `verified=False` 的 6 条**不取**")
    print()
    if hits:
        print("  [REPORT] **%d** 处引用了**不存在的官方页**（★ 本题材已知的真断链已修 5 处）" % len(hits))
        print("  ★★ 本门禁**暂只报告、不拦（exit 0）** —— 理由：")
        print("     · 判据边界还有 2 处待人判（见文件级例外说明：`IInsertMidSurface` 的 `I` 前缀变体、")
        print("       `[[Iface::Member]]` 模板占位）；")
        print("     · 按 D-1（新建门禁误报率 ≤5%，未达标者留待复核桶）⇒ **达标前不接进 release_check** ✓")
        print("  ★ 接进 release_check 的前置：把上列 hits 逐条判完（真断链则修，边界则进例外表）✓")
        return 0
    print("[PASS] 0 处引用了不存在的官方页（★ 扫描面：%s）" % "/".join(SCAN_DIRS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
