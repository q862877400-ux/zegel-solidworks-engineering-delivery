"""★ **靶子表扩容的准入判据**（spec 242）—— 让「能不能收进 `DEPRECATED_ENTRIES`」变成可跑的判据。

## 一、为什么要它
```
★ 上一轮（spec 241）交接单的待办 1 是「靶子表扩容」：官方索引
  `specs/202-user-coverage-gaps/recon/official-obsolete-index.json`（1671 条 / 1455 个成员名）。
★ 本轮**先量**（★ 纪律：先量两样 —— ① 目标规模 ② **加词的爆炸半径**）：
  ① 目标规模：1671 条 ⇒ 真树上**被调用的**废弃成员名只有 **82** 个；
  ② 爆炸半径：索引里 **115 / 1455** 个成员名按「官方字面后继」看是歧义名；
     ★★ 而按**链终点**看（★ 见下 §二 关 2）只有 **79** 个是**真歧义**
     （★ `SaveAs` 是"假歧义"：两条链的终点都是 `SaveAs3`）。
     ★ 真树在调的 82 个废弃名里，真歧义的有 **11** 个（`Select2` 一名 **6** 个不同终点！）。
★★ 而 `deprecated_successor(member)` 是**公开 MCP 工具**（`mcp-server/tool_specs_batch80.py`），
   ★ 它**只按成员名查** ⇒ 一旦把真歧义名收进表，它会**静默返回一个错的**后继
   （★ 与「静默降级」同病：读出来的东西**看起来像答案**）。
⇒ ★★ 结论：**扩容的前置条件不是"多写几行表"，而是先让"按名歧义"不可能静默存在**。
```

## 二、★★ 准入三关（★ 每条候选都要逐条过）
```
关 0 ★ 按名歧义：★ 同一个成员名在表里映射到**不同后继** ⇒ 红（★ 现在 0 条）。
关 1 ★ 官方索引里有它：★ `(接口, 成员)` 必须真在官方 `Obsolete` 索引里。
关 2 ★ 后继 = **官方链的终点**：★ 官方 `Superseded by` **可能指向一个自己也已废弃的成员**
        （★ 本仓的 `IModelDocExtension::SaveAs` 就是 —— 官方指向 `SaveAs2`、而 `SaveAs2` 又指向 `SaveAs3`）
        ⇒ ★★ **必须沿链走到第一个不再废弃的**；★ 表里记的必须是**链终点**，不是官方那一句的字面值。
关 3 ★ 后继**在仓库里真的被调用**（★ 与 spec 241 判据②同源：否则"互锁"退化成"全都不许用"）。
```

## 三、★ 本文件**不改表**
```
★ 本规格**只立判据**（★ 与 224/237 同族顺序：先立准入、再谈扩容）——
   ★ 真树现表 **11 条**逐条过三关（★ 有靶子，不是空判据）；★ 将来谁要扩容，跑这个文件就知道能不能收。
```
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_deprecated_table_admission.py
# 定位:   规格 `specs/242-deprecated-table-admission/` FR-003/FR-004 的判据。
# 官方依据: `specs/202-user-coverage-gaps/recon/official-obsolete-index.json`
#   （★ `tools/build_obsolete_index.py` 生成，★ 只读官方 `C:\swapi\types\**\*.md` 的 `Obsolete` 段）·
#   `scripts/sw_com_traps.DEPRECATED_ENTRIES` · `scripts/sw_com_traps.deprecated_successor`。
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_com_traps as TRAPS                                        # noqa: E402
from tests.test_deprecated_entry_interlock import (                 # noqa: E402
    _scan_all_modules,
    _scan_calls,
)

INDEX_PATH = ROOT / "specs" / "202-user-coverage-gaps" / "recon" / "official-obsolete-index.json"

#: ★ 官方类型页根（★ 关 6 要判后继页是否存在、是否**自己还是废弃的**）。
SWAPI_TYPES = Path("C:/swapi/types")

#: ★★ **歧义名的豁免名单**（★ 空 = 一条都不许）—— ★ **有盲区即红**的形态：
#: ★ 若将来真要把一个「索引里同名 · 后继不同」的名字收进表，★ 必须**先**在这里写下
#: 「为什么按接口分派是安全的」，★ 而不是让 `deprecated_successor(名)` 继续**猜**。
_AMBIGUOUS_NAME_ALLOWLIST: set[str] = set()

#: ★★★ **多后继的人工表态表**（spec 247）—— 键 `(接口, 成员)`；值 = **依据**。
#: ★ **什么时候必须来表态**：★ 官方那句的**真后继个数机械判不出**（`_official_successor_count` 回 `None`）
#:   而该条目又要进表 ⇒ ★ **未表态即红**（`successor-count-undecidable`）。
#: ★★ **什么时候不该来表态**：★ 官方那句是「`Superseded by A and B`」⇒ **两个都是后继**
#:   ⇒ ★ 靶子表的值是**裸成员名**、**表达不了"两个都要"** ⇒ ★ 那种条目**一律不收**，
#:   ★ **不许**用本表把它们放行（★ 由 `test_superseded_by_pairs_are_not_adjudicated` 守）。
#: ★ 每条依据必须写明「哪几个链接是/不是后继、为什么」，且**引用官方页路径**。
_MULTI_SUCCESSOR_ADJUDICATED: dict[tuple[str, str], str] = {
    #: ★ 现为空 —— ★ **真树在调的多链接条目 18 条**（`SUPERSEDED-BY 16` + `SEE+REMARKS 2`）
    #: 全部**机械可判**（★ 见 `output/_probe247_multi.py`）⇒ 没有需要人工表态的条目。
    #: ★★ **空 ≠ 空判据**：★ `_official_successor_count` 是**纯函数**，由
    #: `tests/test_deprecated_multi_successor_adjudication.py` 直接喂**合成输入**证明三态都能红。
}


def _index_entries() -> list[dict]:
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))["entries"]


def _index_map(entries: list[dict]) -> dict[tuple[str, str], str]:
    return {(e["interface"], e["member"]): e["successor"] for e in entries}


def _split(qualified: str) -> tuple[str, str]:
    """★ 把官方那句 `Iface::Member.` 切成 `(Iface, Member)`（★ 尾点要剥）。"""
    iface, _, member = qualified.partition("::")
    return iface.strip(), member.strip().rstrip(".")


def _chain_terminal(iface: str, member: str, imap: dict, limit: int = 8):
    """★ 从**已废弃**的 `(iface, member)` 出发，沿官方链走到**第一个不再废弃**的成员。

    ★ 返回 `(iface, member)` 或 `None`（★ 断链 / 自环 / 超限 ⇒ 显式 `None`，★ 不静默降级）。
    """
    cur = (iface, member)
    for _ in range(limit):
        succ = imap.get(cur)
        if not succ:
            return None                    # ★ 起点不在索引里 ⇒ 调用方用错
        nxt = _split(succ)
        if nxt == cur:
            return None                    # ★ 自环
        if nxt not in imap:
            return nxt                     # ★★ 终点：后继页不再废弃
        cur = nxt
    return None                            # ★ 超限 / 成环


def _called_names() -> set[str]:
    """★ 真树被调用（两形态）的成员名（★ 口径 import 自 spec 241，不重写）。"""
    out = set()
    for _name, tree in _scan_all_modules():
        for _ln, member in _scan_calls(tree):
            out.add(member)
    return out


def _admission_failures(table: dict, imap: dict, called: set[str], entries: list[dict],
                        adjudicated: "dict | None" = None) -> list[tuple]:
    """★★ **纯函数**：逐条判**六关**。★ 返回 `[(条目, 原因码), …]`（★ 空 = 全过）。

    ★ 抽成纯函数（★ 纪律：真树上不会自然触发的自证 ⇒ 由单测直接喂输入）。
    ★★ `entries`（★ spec 243 新增）：官方索引的**原始条目** —— 关 5/关 6 要看
      `obsolete_line`（官方那句点名了几个后继）与后继页本身，★ 这些**不在** `imap` 里。
    ★★ `adjudicated`（★ spec 247 新增）：**多后继的人工表态表**（缺省 = 模块级那张）。
      ★ 显式传入是为了让单测能喂**合成表态表**（★ 真表现在是空的 ⇒ 否则关 5 的那条判据是**空判据**）。
    """
    adjudicated = _MULTI_SUCCESSOR_ADJUDICATED if adjudicated is None else adjudicated
    fails: list[tuple] = []
    entry_by_key = {(e["interface"], e["member"]): e for e in entries}
    #: ★ 关 0：按名歧义（★ 同名 · 不同后继）
    for name, succs in TRAPS.ambiguous_deprecated_members(table).items():
        fails.append(((None, name), "ambiguous-name:%s" % (succs,)))
    for (iface, member), succ in table.items():
        key = (iface, member)
        #: ★ 关 1：官方索引里有它
        if key not in imap:
            fails.append((key, "not-in-official-index"))
            continue
        #: ★ 关 2：后继 = 官方链的**终点**（★ 不是那句的字面值）
        term = _chain_terminal(iface, member, imap)
        if term is None:
            fails.append((key, "chain-broken"))
            continue
        if term[1] != succ:
            fails.append((key, "successor-is-not-chain-terminal:%s!=%s" % (succ, term[1])))
            continue
        #: ★★ 关 4（spec 243）：后继**成员名**必须 ≠ 被废弃的成员名。
        #:   ★ 相等 ⇒ 那是**接口迁移**（`IModelDoc2::FeatureCut4` → `IFeatureManager::FeatureCut4`），
        #:   ★ 而靶子表的值是**裸成员名** ⇒ **表达不了**它（★ 收了会与互锁测试的 `succ != member` 打架）。
        if succ == member:
            fails.append((key, "successor-same-name"))
            continue
        #: ★★ 关 5（spec 243，★ spec 247 **细化为三态**）：官方那句到底点名了**几个真后继**。
        #:   ★ `build_obsolete_index.py` 用 `re.search` ⇒ 多个链接时**只留第一个**（有损）
        #:   ⇒ ★ 多后继必须**人工表态**，不得自动放行（★ 真案例 `IModelDoc2::SketchTrim`）。
        #:   ★★ **247 的细化**：243 只数「全部 `[[…]]` 链接」—— ★ 而官方常写
        #:     「`See [[X]] and the Remarks in [[Y]]`」⇒ ★ **`Y` 不是后继**（是数据接口）。
        #:   ⇒ ★ 改按 `_official_successor_count` 的**三态**判：
        #:     `1` ⇒ 过 · `>1` ⇒ 红（表表达不了）· `None` ⇒ ★ **必须在 `_MULTI_SUCCESSOR_ADJUDICATED` 里人工表态**。
        n_succ = _official_successor_count(entry_by_key[key].get("obsolete_line", ""))
        if n_succ is None:
            if key not in adjudicated:
                fails.append((key, "successor-count-undecidable"))
            continue
        if n_succ > 1:
            fails.append((key, "multiple-official-successors:%d" % n_succ))
            continue
        #: ★ 唯一那个官方后继必须**在通往本表后继的链上**（★ 允许跳代：242 的 `_chain_terminal`）
        only = _official_successor_links(entry_by_key[key].get("obsolete_line", "")) or []
        if only:
            o_iface, o_member = _split(only[0])
            if (o_iface, o_member) not in imap:
                o_term_member = o_member          # ★ 官方那个链接**自己不废弃** ⇒ 它就是终点
            else:
                o_term = _chain_terminal(o_iface, o_member, imap)
                o_term_member = o_term[1] if o_term else None
            if o_term_member != succ:
                fails.append((key, "successor-not-on-official-chain:%s" % only[0]))
                continue
        #: ★★ 关 6（spec 243）：后继页**必须存在**，且**自己不是废弃的**。
        #:   ★ `_chain_terminal` 把"不在索引里"当终点 —— ★ 而"页不存在"与"页存在且不废弃"
        #:     **同形** ⇒ ★ 必须另判（★ 不许静默降级）。
        first = _page_first_body_line(str(_successor_page(term[0], term[1])))
        if first is None:
            fails.append((key, "successor-page-missing:%s::%s" % term))
            continue
        if first.lower().startswith("obsolete"):
            fails.append((key, "successor-still-obsolete:%s" % first[:60]))
            continue
        #: ★ 关 3：后继在仓库里**真的被调用**（★ 否则"互锁"退化成"全都不许用"）
        if succ not in called:
            fails.append((key, "successor-never-called"))
    return fails


def _successor_links(line: str) -> list[str]:
    """★ 官方那句里的 `[[…]]` 链接（★ 多个 = 官方点名了**多个**后继）。"""
    return re.findall(r"\[\[([^\]]+)\]\]", line or "")


#: ★ 官方「只看 Remarks」的两种写法（★ 247 实测：`Remarks in` 与 `Remarks of` **都出现过**）。
_REMARKS_RE = re.compile(r"\band the Remarks (?:in|of)\b")
#: ★ 官方「后继子句」的两种开头。
_SUPERSEDED_RE = re.compile(r"\bSuperseded by\b")
_SEE_RE = re.compile(r"\bSee\b")


def _official_successor_links(line: str) -> list[str] | None:
    """★★ 从官方那句里抽出**真后继**链接（★ 纯函数；★ 三态语义）。

    ★★ 为什么必须有它（★ spec 247）：243 的关 5 只数「全部 `[[…]]` 链接」——
      ★ 而官方常写「`See [[X]] and the Remarks in [[Y]]`」⇒ ★ **`Y` 是数据接口、不是后继**
      （★ 实测 `ILinearPatternFeatureData` 的页**根本不存在**）。
    ★ 三种形态（★ 247 在 254 条多链接条目上量过：`SUPERSEDED-BY 235 · SEE+REMARKS 14 · SEE(other) 5`）：

    | 形态 | 例 | 真后继 |
    |---|---|---|
    | `Superseded by A and B` | `SketchTrim` | ★ **A 与 B 都是**（⇒ 表表达不了 ⇒ 关 5 拒） |
    | `See X and the Remarks in/of Y` | `FeatureLinearPattern5` | ★ **只有 X**（Y 是数据接口） |
    | 其它 `See …` | `See [[IProjectionCurveFeatureData]] and [[IFeatureManager::CreateDefinition]]` | ★ **判不出**（★ 顺序不可靠：数据接口**可能在前**） ⇒ 回 `None` |

    :returns: 真后继链接列表；★ **`None` = 机械判不出**（⇒ 必须人工表态）。
    """
    line = line or ""
    m = _SUPERSEDED_RE.search(line)
    if m:
        clause = line[m.end():]
        return _successor_links(clause.split(".")[0])
    m = _SEE_RE.search(line)
    if m:
        clause = line[m.end():]
        rm = _REMARKS_RE.search(clause)
        if rm is None:
            return None                      # ★ 形态不可靠 ⇒ 人工表态
        return _successor_links(clause[:rm.start()])
    return None


def _official_successor_count(line: str) -> int | None:
    """★ `_official_successor_links` 的计数版（★ `None` 原样透传 = 判不出）。"""
    links = _official_successor_links(line)
    return None if links is None else len(links)


def _successor_page(iface: str, member: str) -> Path:
    """★ 后继成员的官方页路径（★ 缺省根 `C:/swapi/types`）。"""
    return SWAPI_TYPES / iface / (member + ".md")


def _page_first_body_line(page: str) -> str | None:
    """★ 官方页「标题之后、第一个 `## ` 之前」那一段的**首个非头部行**。

    ★ 口径同 `tools/build_obsolete_index.py`（★ 不重写：那边也是取「标题之后、`## ` 之前」）。
    ★★ 回 `None` = **页不存在** —— ★ 与"页存在但不废弃"**必须分开**（★ 不许静默降级）。
    ★★ **不许**全文搜 `obsolete`：★ `IModelDocExtension\\SaveAs3.md` 正文里就有
      「the now obsolete [[IModelDocExtension::SaveAs2]]」⇒ 全文搜会**假红**。
    """
    p = Path(page)
    if not p.exists():
        return None
    try:
        txt = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in txt.split("\n## ", 1)[0].splitlines():
        s = line.strip()
        if not s or s.startswith(("#", "---")):
            continue
        if re.match(r"^(type|member|kind|assembly|namespace|category):", s):
            continue
        return s
    return ""


# ── ① ★ 真树：现表逐条过三关（★ 有靶子，不是空判据）────────────────────
def test_real_target_table_passes_admission():
    """★★ 真树判据：`DEPRECATED_ENTRIES` 的**每一条**都过三关（★ 现在 11 条 —— spec 246/247 扩容后）。

    ★ 这条判据的**真价值**：★ 将来谁往表里加一条，跑它就知道**能不能收**
      （★ 而不是"看起来对就收"）。
    """
    entries = _index_entries()
    imap = _index_map(entries)
    fails = _admission_failures(TRAPS.DEPRECATED_ENTRIES, imap, _called_names(), entries)
    assert not fails, "★ 靶子表里有条目**没过准入三关**：%s" % (fails,)


# ── ② ★ 表内不许有按名歧义 ─────────────────────────────────────────────
def test_target_table_has_no_ambiguous_names():
    """★★ 表内**按名歧义 = 0**（★ 现在 11 条名字互不相同）。

    ★ 为什么单列：★ `deprecated_successor(member)` **只按成员名查** ⇒
      同名映射到两个后继时，它只能**猜**。
    """
    amb = TRAPS.ambiguous_deprecated_members()
    assert not amb, (
        "★ 靶子表里出现**按名歧义**（★ 同一个成员名映射到不同后继）⇒ "
        "`deprecated_successor(名)` 无法回答，只能猜：%s" % (amb,))


# ── ③ ★ 歧义名**不猜**（★ 合成表负例）────────────────────────────────
def test_ambiguous_name_is_not_guessed():
    """★★★ **歧义名必须显式报出来、不许猜** —— ★ 合成表（★ 真表上永远不会触发）。

    ★ 用**合成表**替换模块级 `DEPRECATED_ENTRIES`（★ 用完还原）⇒
      ★ 若实现退回"按名取第一个"，本判据**必红**（★ 那就是旧行为）。
    """
    synthetic = {
        ("IAnnotation", "Select2"): "Select3",
        ("IEntity", "Select2"): "Select4",
    }
    saved = dict(TRAPS.DEPRECATED_ENTRIES)
    try:
        TRAPS.DEPRECATED_ENTRIES.clear()
        TRAPS.DEPRECATED_ENTRIES.update(synthetic)
        amb = TRAPS.ambiguous_deprecated_members()
        assert amb == {"Select2": ["Select3", "Select4"]}, amb
        assert TRAPS.deprecated_successor("Select2") is None, (
            "★ 歧义名 `Select2` **被猜了一个后继** ⇒ 必须返回 None（★ 不猜）")
        #: ★ 边界冻结：**给了接口**就要查得准（★ 放宽"不猜"必须配"加什么能查到"的断言）
        assert TRAPS.deprecated_successor("Select2", interface="IEntity") == "Select4"
        assert TRAPS.deprecated_successor("Select2", interface="IAnnotation") == "Select3"
        assert TRAPS.deprecated_successor("Select2", interface="Nope") is None
    finally:
        TRAPS.DEPRECATED_ENTRIES.clear()
        TRAPS.DEPRECATED_ENTRIES.update(saved)


# ── ④ ★ 三关各自的负例（★ 合成表；★ 判据必须能在合成输入上红）──────────
def _imap_for(entries):
    return _index_map(entries)


def test_successor_must_be_chain_terminal_not_literal():
    """★★ **关 2**：官方那句 `Superseded by` 指向的后继**可能自己也已废弃** ⇒ 必须走到链终点。

    ★ 用**真的官方索引**里的 SaveAs 链（★ 不是编的）：
      `IModelDocExtension::SaveAs` → `SaveAs2` → `SaveAs3`（★ `SaveAs3` 不在索引里）。
      ★ 记 `SaveAs2`（官方字面值）⇒ **红**；记 `SaveAs3`（链终点）⇒ 绿。
    """
    entries = _index_entries()
    imap = _imap_for(entries)
    called = _called_names()
    bad = {("IModelDocExtension", "SaveAs"): "SaveAs2"}
    fails = _admission_failures(bad, imap, called, entries)
    assert fails and fails[0][1].startswith("successor-is-not-chain-terminal"), fails
    good = {("IModelDocExtension", "SaveAs"): "SaveAs3"}
    assert not _admission_failures(good, imap, called, entries), "★ 链终点 `SaveAs3` 应判过"


def test_unknown_entry_and_uncalled_successor_are_rejected():
    """★ **关 1**（不在官方索引里）+ **关 3**（后继一次都没被调用）各自的负例。"""
    entries = _index_entries()
    imap = _imap_for(entries)
    called = _called_names()
    #: ★ 关 1：编一个官方索引里没有的条目
    f1 = _admission_failures({("IAnnotation", "NoSuchMember"): "Nope"}, imap, called, entries)
    assert f1 and f1[0][1] == "not-in-official-index", f1
    #: ★ 关 3：真条目、真链终点，但**后继在仓库里没有被调用**
    f3 = _admission_failures({("IModelDocExtension", "SaveAs2"): "SaveAs3"}, imap, {"CreateMate"}, entries)
    assert f3 and f3[0][1] == "successor-never-called", f3


def test_self_successor_is_rejected():
    """★ **关 2 的自环**：官方那句点名**它自己**（事实 271 的一类假阳性）⇒ 红。"""
    imap = {("IAnnotation", "Select"): "IAnnotation::Select"}
    fails = _admission_failures({("IAnnotation", "Select"): "Select"}, imap, {"Select"}, _index_entries())
    assert fails and fails[0][1] == "chain-broken", fails


# ── ⑤ ★★ 边界冻结：索引里的歧义名**不许静默进表** ────────────────────────
def test_ambiguous_official_names_are_not_silently_in_the_table():
    """★★★ **边界冻结**（★ 断言"不加什么"）：★ 官方**链终点跨接口不同**的名字，
    **未经表态不得**出现在靶子表里。

    ★★ 口径为什么是**链终点**而不是官方那句字面值（★ 本轮**先量**推翻的第一版口径）：
      ★ 第一版按「后继字面值」判 ⇒ `SaveAs` 立刻命中（★ 官方把 `IModelDoc2::SaveAs` 指向
        `IModelDocExtension::SaveAs`、而 `IModelDocExtension::SaveAs` 指向 `SaveAs2` ⇒ 两个不同字面值）
      ⇒ ★ **假红**。★ 而沿链走到底：**两条链的终点都是 `IModelDocExtension::SaveAs3`**
      ⇒ ★★ 对**任何**接口按名问 `SaveAs`，答案都是 `SaveAs3` ⇒ **它其实不是歧义名**。
    ★ 实测：真歧义（链终点跨接口不同）**79 / 1455** 个名；★ 表内 4 个名**一个都不在其中**。
    ★★ 豁免只能走 `_AMBIGUOUS_NAME_ALLOWLIST`（★ 现在为空），★ 且必须写清按接口分派的理由。
    """
    entries = _index_entries()
    imap = _index_map(entries)
    by_name: dict[str, list[tuple[str, str]]] = {}
    for e in entries:
        by_name.setdefault(e["member"], []).append((e["interface"], e["member"]))
    ambiguous = set()
    for name, keys in by_name.items():
        terminals = {_chain_terminal(i, m, imap) for (i, m) in keys}
        if len(terminals) > 1:
            ambiguous.add(name)
    #: ★ 夹具自证：索引里**确实存在**真歧义名（★ 否则本判据是空的 —— "检查量为 0 判失败"）
    assert len(ambiguous) > 50, "★ 官方索引里真歧义名只有 %d 个 ⇒ 本判据的靶子不成立" % len(ambiguous)

    in_table = {m for (_i, m) in TRAPS.DEPRECATED_ENTRIES}
    offenders = sorted((in_table & ambiguous) - _AMBIGUOUS_NAME_ALLOWLIST)
    assert not offenders, (
        "★ 这些名字的官方**链终点跨接口不同**，却被收进了靶子表：%s\n"
        "★ 要么写进 `_AMBIGUOUS_NAME_ALLOWLIST` 并写明理由，要么别收。" % (offenders,))


# ── ⑥ ★ 量测读数不许腐烂：索引规模下限（★ 棘轮下界）─────────────────────
def test_official_index_scale_is_still_what_we_measured():
    """★ 索引规模**下界**（★ 只许增不许减 —— ★ 减少 = 生成器漏了，不是"问题解决了"）。"""
    entries = _index_entries()
    assert len(entries) >= 1600, "★ 官方废弃索引只剩 %d 条（下界 1600）" % len(entries)


# ══════════════════════════════════════════════════════════════════════
# ★★ spec 243：把「82 个候选逐条筛」变成判据 —— 关 4 / 关 5 / 关 6
# ══════════════════════════════════════════════════════════════════════
#: ★ 本规格**先量**（探针 `output/_probe243_admission.py`）出的 82 个
#: 「真树在调用的废弃名」分桶（★ 口径 = 242 的三关 + 本规格新增的关 4）：
#: ```
#:   successor-same-name    34   ← ★ 接口迁移（`IModelDoc2::FeatureCut4` → `IFeatureManager::FeatureCut4`）
#:   terminal-never-called  23
#:   admissible             15
#:   ambiguous-terminal      9
#:   chain-broken-all        1
#: ```
#: ★★ 而**关 4 是 242 缺的**：★ 那 34 个在 242 的三关下**全部"过关"**
#:   ⇒ ★ 若照 242 的口径扩表，会把**表达不了**的条目收进表（★ 见下 `test_interface_migration...`）。


def _census(entries: list[dict], imap: dict, called: set[str]) -> dict[str, str]:
    """★ **纯函数**：对「真树在调用的废弃名」逐个定桶（★ 名字级口径：取该名的**全部**索引条目）。

    ★ 桶 = `chain-broken-all` / `ambiguous-terminal` / `successor-same-name` /
      `terminal-never-called` / `admissible`（★ 封闭词表）。
    ★ 抽成纯函数（★ 纪律：真树上不会自然触发的自证 ⇒ 由单测直接喂输入）。
    """
    by_name: dict[str, list[tuple[str, str]]] = {}
    for e in entries:
        by_name.setdefault(e["member"], []).append((e["interface"], e["member"]))
    out: dict[str, str] = {}
    for name in sorted(set(by_name) & called):
        terms = {_chain_terminal(i, m, imap) for (i, m) in by_name[name]}
        terms.discard(None)
        if not terms:
            out[name] = "chain-broken-all"
        elif len(terms) > 1:
            out[name] = "ambiguous-terminal"
        else:
            t = next(iter(terms))
            if t[1] == name:
                out[name] = "successor-same-name"          # ★ 关 4
            elif t[1] not in called:
                out[name] = "terminal-never-called"
            else:
                out[name] = "admissible"
    return out


# ── ⑦ ★★★ 关 4：接口迁移型（后继**成员名 == 被废弃的成员名**）────────────
def test_interface_migration_is_rejected_by_admission():
    """★★★ **关 4**：★ 官方那句 `Superseded by` 常常是**接口迁移** ——
    `IModelDoc2::FeatureCut4` → `IFeatureManager::FeatureCut4`（★ 同一成员名、**换了接口**）。

    ★★ 为什么必须拒：★ 靶子表的值是**裸成员名**、互锁判据也**按成员名比** ⇒
      ★ **它表达不了"接口迁移"**（`succ != member` 是互锁测试的硬断言）
      ⇒ ★ 收进来会**同时**踩两条：表里记着"用 `FeatureCut4` 代替 `FeatureCut4`"（无意义）。
    ★ 真表 11 条**没有**这种条目 ⇒ ★ **必须用合成负例**才触发得到。
    """
    entries = _index_entries()
    imap = _index_map(entries)
    called = _called_names()
    bad = {("IModelDoc2", "FeatureCut4"): "FeatureCut4"}
    fails = _admission_failures(bad, imap, called, entries)
    assert fails and fails[0][1] == "successor-same-name", fails


def test_census_buckets_are_all_non_empty():
    """★★ **普查不许"检查量为 0"**：★ 82 个候选里**五个桶各自都要有货**（★ 下界，不写精确数）。

    ★ 为什么用**下界**：★ 官方索引与真树都会变；★ 精确数写在
      `specs/243-*/acceptance.md` 里（★ 那是**量测报告**，不是判据）。
    ★★ 若 `successor-same-name == 0` ⇒ ★ 说明**关 4 的靶子没了**（不是"问题解决了"）。
    """
    entries = _index_entries()
    imap = _index_map(entries)
    called = _called_names()
    census = _census(entries, imap, called)
    assert len(census) >= 70, "★ 真树在调的废弃名只剩 %d 个 ⇒ 普查前提不成立" % len(census)
    from collections import Counter
    n = Counter(census.values())
    assert n["successor-same-name"] >= 30, "★ 接口迁移型只剩 %d 个（下界 30）⇒ 关 4 没靶子" % n["successor-same-name"]
    assert n["terminal-never-called"] >= 10, n
    assert n["ambiguous-terminal"] >= 5, n
    assert n["admissible"] >= 5, n
    assert n["chain-broken-all"] >= 1, n
    assert sum(n.values()) == len(census), n


# ── ⑧ ★★★ 关 5：官方那句点名了**多个**后继 ⇒ 索引只留第一个 ⇒ 不许自动收 ──
def test_multi_successor_official_line_is_rejected():
    """★★★ **关 5**：★ 官方那句常写「`Superseded by A and B`」——
    ★ 而 `tools/build_obsolete_index.py` 用 `re.search` ⇒ **只留第一个**（★ 有损）。

    ★★ 真案例（★ 不是编的）：`C:\\swapi\\types\\IModelDoc2\\SketchTrim.md:12` 逐字
      「`Obsolete. Superseded by [[ISketchManager::SketchExtend]] and [[ISketchManager::SketchTrim]].`」
      ⇒ ★ **spec 251 起**生成器用「**同名链接优先**」⇒ 索引记的是 `SketchTrim`（★ 真后继）。
      ★ 但**官方那句仍然点名了多个** ⇒ ★ 这类**必须人工表态**，**不得**由准入判据自动放行。
    ★ 量：索引 1671 条里 **254 条**官方点名了多个后继。
    """
    entries = _index_entries()
    imap = _index_map(entries)
    called = _called_names()
    #: ★ 251 后索引给的是**链终点**（`SketchTrim`）⇒ ★ 关 6 过、**关 5**（多后继）才轮到它拒。
    #: ★★ **251 起不能再拿 `SketchTrim` 当靶子** —— 索引修好后它的后继是**同名**的 `SketchTrim`
    #:   ⇒ ★ **关 4（successor-same-name）会先触发**，关 5 轮不到。
    #: ★ 换 `IModelDoc2::MaterialIdName`：官方那句也是 `Superseded by A and B`（2 个链接），
    #:   而后继 `GetMaterialPropertyName2` **与成员名不同** ⇒ ★ 关 4 过、**关 5** 来拒。
    #: ★ 靶子表的值是**裸成员名**（★ 247 已定），链终点 `term[1]` 也是裸名。
    fails = _admission_failures({("IModelDoc2", "MaterialIdName"): "GetMaterialPropertyName2"},
                                imap, called, entries)
    assert fails and fails[0][1].startswith("multiple-official-successors"), fails
    #: ★ 夹具自证：索引里**确实有**多后继条目（★ 否则本判据是空的）
    import re as _re
    multi = [e for e in entries if len(_re.findall(r"\[\[", e["obsolete_line"] or "")) > 1]
    assert len(multi) >= 200, "★ 索引里多后继条目只剩 %d 条 ⇒ 本判据的靶子不成立" % len(multi)


# ── ⑨ ★★ 关 6：后继页**必须存在**、且**自己不是废弃的** ─────────────────
def test_successor_page_must_exist_and_not_be_obsolete():
    """★★ **关 6**：★ `_chain_terminal` 把「后继页不在索引里」当成**终点**
    —— ★ 而"不在索引里"**有两种**含义：① 页存在且不废弃 ✓ ② **页根本不存在** ✗
    ⇒ ★ 两者**同形**（★ 静默降级）⇒ ★ 必须另判。

    ★ 合成负例（★ 真表 11 条都过 ⇒ 必须喂合成输入才触发得到）。
    ★★ 判据用的是**页首行**（★ 口径同 `build_obsolete_index.py`：
      「标题之后、第一个 `## ` 之前」的**首个非头部行**以 `Obsolete.` 开头）——
      ★ **不是**全文搜 `obsolete`：★ `IModelDocExtension\\SaveAs3.md` 正文里就有
      「the now obsolete [[IModelDocExtension::SaveAs2]]」⇒ ★ 全文搜会**假红**（★ 见下面的边界冻结）。
    """
    #: ① 页不存在 ⇒ 红
    fake = [{"interface": "IFoo", "member": "Bar", "successor": "IFoo::Baz",
             "obsolete_line": "Obsolete. Superseded by [[IFoo::Baz]].", "page": ""}]
    f1 = _admission_failures({("IFoo", "Bar"): "Baz"}, {("IFoo", "Bar"): "IFoo::Baz"}, {"Baz"}, fake)
    assert f1 and f1[0][1].startswith("successor-page-missing"), f1
    #: ② 页存在、而**自己还是废弃的** ⇒ 红
    fake2 = [{"interface": "IFoo", "member": "Bar", "successor": "IModelDocExtension::SaveAs2",
              "obsolete_line": "Obsolete. Superseded by [[IModelDocExtension::SaveAs2]].", "page": ""}]
    f2 = _admission_failures({("IFoo", "Bar"): "SaveAs2"},
                             {("IFoo", "Bar"): "IModelDocExtension::SaveAs2"}, {"SaveAs2"}, fake2)
    assert f2 and f2[0][1].startswith("successor-still-obsolete"), f2
    #: ★★ 边界冻结：`SaveAs3` 页正文里**有** "obsolete" 一词，而它**不是**废弃页 ⇒ 不许假红
    real = _index_entries()
    assert not _admission_failures({("IModelDocExtension", "SaveAs2"): "SaveAs3"},
                                   _index_map(real), _called_names(), real)
