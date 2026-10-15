"""★ spec 244：多后继条目的「同名链接优先」规则（先红后绿）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   specs/202-user-coverage-gaps/recon/official-obsolete-index.json
#         C:/swapi/types/IModelDoc2/SketchTrim.md（实证页）
# 定位:   官方那句「Superseded by A and B」点多个链接时，**与被废弃成员同名**的那个
#         才是真后继（接口迁移）；索引生成器 `tools/build_obsolete_index.py` 用
#         `re.search` 只留第一个 ⇒ 有同名链接时可能取错。
# 官方依据: C:/swapi/types/IModelDoc2/SketchTrim.md:12
#         「Superseded by [[ISketchManager::SketchExtend]] and [[ISketchManager::SketchTrim]]」
#         ★ 实证：SketchExtend 的语义是「Adds to the length」（延伸），
#         SketchTrim 的语义是「Trims the selected sketch entities」（剪裁）
#         ⇒ 真后继是**同名**的 ISketchManager::SketchTrim，不是第一个链接。
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读索引与官方页；★ 不改索引生成器（改它要重跑并复核全部 1671 条，属独立工作）
# ────────────────────────────────────────────────────────────────────
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "specs" / "202-user-coverage-gaps" / "recon" / "official-obsolete-index.json"

#: 官方那句里的 wikilink：[[Iface::Member]]
LINK = re.compile(r"\[\[([^\]]+)\]\]")

#: ★★ **已知偏差登记**（★ 索引取错、但真后继已查证）。
#: 键 = (被废弃接口, 被废弃成员)；值 = (真后继全名, 查证依据)。
#: ★★★ **spec 251 起本表为空** —— 生成器的「**同名链接优先**」规则已接上，那 6 条**全部修好**。
#:   ★ 修法前**先量**：全 1671 条里只有 **6** 条会变（`output/_probe251_rule_impact.py`）。
#: ★★ **空的登记表不许让判据变空** ⇒ 修好后的**正向**断言在 `_FIXED_BY_251` 与判据 ② 里。
_KNOWN_WRONG: dict[tuple[str, str], tuple[str, str]] = {}

#: ★★★ **spec 251 修好的 6 条**（★ 值 = 真后继全名）。★ 它是 `_KNOWN_WRONG` 的**正向替代**：
#:   ★ 判据要求**索引当前的后继必须等于这里的值** —— ★ 生成器规则被改坏时当场红。
_FIXED_BY_251: dict[tuple[str, str], str] = {
    ("IModelDoc2", "SketchTrim"): "ISketchManager::SketchTrim",
    ("IFeature", "GetBody"): "IFace2::GetBody",
    ("IFeature", "IGetBody"): "IFace2::IGetBody",
    ("INote", "IGetTextFormat"): "IAnnotation::IGetTextFormat",
    ("INote", "ISetTextFormat"): "IAnnotation::ISetTextFormat",
    ("ISheet", "ICreateOLEObject"): "IModelDocExtension::ICreateOLEObject",
}


def _split(qualified: str) -> tuple[str, str]:
    iface, _, member = qualified.partition("::")
    return iface.strip(), member.strip().rstrip(".")


def _entries() -> list[dict]:
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))["entries"]


def _multi() -> list[dict]:
    """★ 多后继条目 = obsolete_line 里 >=2 个 wikilink。"""
    return [e for e in _entries() if len(LINK.findall(e.get("obsolete_line", ""))) >= 2]


def test_multi_successor_count_is_frozen():
    """★ 多后继条目的**下界**（★ 只允许增不允许减 —— 减少 = 索引读取器漏了）。"""
    n = len(_multi())
    assert n >= 254, "多后继条目从 254 降到 %d ⇒ 索引读取器可能漏了" % n


def test_same_name_link_is_the_real_successor():
    """★★ 核心规则：句中有**同名**链接时，索引后继必须是它（或已登记的偏差）。

    ★ 这是**能红的判据**：未登记偏差时，6 条有同名链接的条目会当场失败。
    """
    bad = []
    checked = 0
    for e in _multi():
        links = [_split(x) for x in LINK.findall(e["obsolete_line"])]
        same = [l for l in links if l[1] == e["member"]]
        if not same:
            continue                      # ★ 无同名链接 ⇒ 索引取第一个，本判据不管
        checked += 1
        rec = _split(e["successor"]) if "::" in e["successor"] else ("", e["successor"])
        if rec in same:
            continue                      # ★ 取对了
        key = (e["interface"], e["member"])
        if key in _KNOWN_WRONG:
            expected, _why = _KNOWN_WRONG[key]
            #: ★ 登记项必须**对得上**：真后继在同名链接里（★ 251 起本表为空，此支路不再走）
            assert _split(expected) in same, (
                "登记的真后继 %s 不在同名链接 %s 里 ⇒ 登记表写错了" % (expected, same))
            continue
        bad.append((e["interface"], e["member"], e["successor"],
                    ["%s::%s" % s for s in same]))
    #: ★★ **检查量下界**（★ 事实 46：检查量为 0 判失败）—— ★ 含同名链接的条目实测 **11** 条。
    assert checked >= 11, "含同名链接的条目只剩 %d 条 ⇒ 本判据的空转风险" % checked
    assert not bad, (
        "有同名链接但索引取错、且未登记偏差 %d 条：\n%s"
        % (len(bad), "\n".join("  %s::%s 索引给 %s，真后继应是 %s" % b for b in bad)))


def test_known_wrong_registry_matches_index():
    """★ 登记表必须**与索引现状一致**：索引改了（或修好了）⇒ 本表要同步删行。

    ★★ **spec 251 修了一个潜伏 bug**：原判据写的是 `e["successor"] == _split(expected)`
    —— ★ **`str` 与 `tuple` 永不相等** ⇒ ★ 这条「过期检测」**从来没生效过**（★ 空判据）。
    ★ 现改为两边都 `_split` 后比较。
    """
    by_key = {(e["interface"], e["member"]): e for e in _entries()}
    stale = []
    for (iface, member), (expected, _why) in _KNOWN_WRONG.items():
        e = by_key.get((iface, member))
        if e is None:
            stale.append("%s::%s 已不在索引里" % (iface, member))
            continue
        if e["successor"] and _split(e["successor"]) == _split(expected):
            stale.append("%s::%s 的索引后继已变成 %s（已修好？）⇒ 删本表的这一行"
                         % (iface, member, expected))
    assert not stale, "登记表过期：\n" + "\n".join("  " + s for s in stale)


def test_fixed_by_251_successors_are_in_the_index():
    """★★★ **spec 251 的正向断言**：那 6 条的**索引后继必须等于真后继**。

    ★ 这是 `_KNOWN_WRONG` 清空后的**非空替代** —— ★ 生成器规则被改坏 / 索引被回滚 ⇒ 当场红。
    ★ 且 `_KNOWN_WRONG` 必须为空（★ 否则说明还有没修的偏差）。
    """
    assert len(_FIXED_BY_251) >= 6, \
        "修好的条目从 6 降到 %d ⇒ 本判据变空" % len(_FIXED_BY_251)
    assert not _KNOWN_WRONG, \
        "`_KNOWN_WRONG` 非空 ⇒ 还有未修的索引偏差：%s" % list(_KNOWN_WRONG)
    by_key = {(e["interface"], e["member"]): e for e in _entries()}
    for key, expected in _FIXED_BY_251.items():
        assert "::" in expected, "%s 的真后继必须写全名（接口::成员）" % (key,)
        e = by_key.get(key)
        assert e is not None, "%s 已不在索引里" % (key,)
        assert e["successor"] == expected, \
            "索引里 %s::%s 的后继是 %r，应为 %r ⇒ 生成器规则没生效" \
            % (key[0], key[1], e["successor"], expected)


def test_registry_entries_have_evidence():
    """★ 每条**修好的**条目都要有依据（★ 依据在 `specs/251-*/acceptance.md` 里逐条列了官方原句）。"""
    from pathlib import Path as _P
    acc = _P(__file__).resolve().parents[1] / "specs" / "251-index-successor-rule" / "acceptance.md"
    assert acc.exists(), "spec 251 的 acceptance.md 不在本机 ⇒ 依据无落点"
    text = acc.read_text(encoding="utf-8")
    for key, expected in _FIXED_BY_251.items():
        assert ("%s::%s" % key) in text, "%s 的官方原句没写进 spec 251 的 acceptance.md" % (key,)
        assert expected in text, "%s 的真后继 %s 没写进 acceptance.md" % (key, expected)
