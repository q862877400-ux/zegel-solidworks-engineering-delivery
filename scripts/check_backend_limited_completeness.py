"""★ 门禁：**名单的完整性** —— ★ 该进「后端到不了」的，有没有漏。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁）
# 文件:   scripts/check_backend_limited_completeness.py
# 定位:   ★ 2026-10-03（轮 602）★ 补**上一道门禁的缺口**（★ 事实 475）。
#
#   ★★ **上一道**（`check_backend_limited_evidence.py`）**只查名单**内部**：
#     ★ 字段齐不齐、依据指得到吗 —— ★ **而它不查「该在名单里的**漏了没**」** ⚠
#     ★ 而轮 601 实测：**「草图驱动的阵列」就漏在「可攻关」里**（★ 它与那四个同族）。
#
#   ★★★ **而完整性判据是**可执行的**（★ 事实 475 记下的那两条）**：
#     \u2460 **`api` \u91cc\u63d0\u5230\u4e00\u4e2a\u5e26 `AccessSelections` \u7684 `*FeatureData`**
#        \u21d2 \u2605 \u8be5\u6761**\u7591\u4f3c\u5e94\u8fdb\u540d\u5355**\uff08\u2605 \u800c\u5b83\u8fd8\u5728\u201c\u53ef\u653b\u5173\u201d\uff09\uff1b
#     \u2461 **`api` \u91cc\u7684\u540d\u5b57\u5728\u5168\u63a5\u53e3\u90fd\u67e5\u4e0d\u5230**\uff08\u2605 \u94c1\u5f8b 5\uff09
#        \u21d2 \u2605 **\u4e0d\u8be5\u7b97\u201c\u53ef\u653b\u5173\u201d**\uff08\u2605 \u90a3\u662f**\u53e6\u4e00\u4e2a\u6876**\u7684\u95ee\u9898\uff09\u3002
#
#   ★ \u5224\u636e\u53d6\u81ea**\u5168\u63a5\u53e3\u7d22\u5f15**\uff08`C:\\swapi\\types\\`\uff0c\u2605 \u9759\u6001\u3001\u53ef\u590d\u6838\uff09\u3002
#   ★ 退出码：★ 违规 ⇒ 1；★ 而**接口目录不存在时 SKIP**（★ 便携性守卫 —— ★ 与 §A8 那类同理）。
#   ★ 配套负例：`tests/test_backend_limited_completeness_gate.py`（★ 事实 62）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent
LEDGER = R / "docs" / "toolbar-ledger-verified.json"
ITEMS = R / "docs" / "backend-limited-items.json"
SWAPI_TYPES = Path(r"C:\swapi\types")

#: \u2605 \u4ece `api` \u91cc\u62bd `I*FeatureData` \u540d\u5b57
IFACE_RE = re.compile(r"\bI[A-Za-z0-9_]*FeatureData\b")
#: \u2605 \u4ece `api` \u91cc\u62bd\u4e00\u822c\u7684**\u6210\u5458\u540d**\uff08\u2605 \u7528\u6765\u67e5\u201c\u5168\u63a5\u53e3\u90fd\u6ca1\u6709\u201d\uff09
MEMBER_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]{4,})\b")


def build_index() -> dict[str, list[str]]:
    """★ 全接口索引：★ 成员名 → 拥有它的接口名列表。"""
    idx: dict[str, list[str]] = {}
    if not SWAPI_TYPES.exists():
        return idx
    for d in SWAPI_TYPES.iterdir():
        if not d.is_dir():
            continue
        for f in d.glob("*.md"):
            if not f.name.startswith("_"):
                idx.setdefault(f.stem, []).append(d.name)
    return idx


def has_access_selections(iface: str) -> bool:
    """★ 那个接口带 `AccessSelections` 吗（★ 那正是指针族的标记）。"""
    d = SWAPI_TYPES / iface
    if not d.exists():
        return False
    return any(f.stem == "AccessSelections" for f in d.glob("*.md"))


def is_obsolete(member: str) -> bool:
    """★ 那个成员**标了 `Obsolete` 吗**（★ 读它 md 的头顶）。

    ★★ 判据来源（★ 事实 433 那条纪律的**机器版**）：
      「凡台账 `api` 带 `2`/不带后缀的，**先读 md 头顶那句 `Obsolete`** —— 继任者名字就在那句里」。
    ★ 而轮 603 实测：★ 台账那条写 `InsertProtrusionSwept4`（**已废弃**）⇒
      ★ 而它的"继任者" `InsertSweepSurface` **三代也全废弃**、★ 最终指向
      `ISweepFeatureData`（★ **带 `AccessSelections`**）
      ⇒ ★ **而那一条恰恰逃过了当时那道门禁**（★ 判据只认 `*FeatureData` 字样）⚠
    """
    if not SWAPI_TYPES.exists():
        return False
    for d in SWAPI_TYPES.iterdir():
        if not d.is_dir():
            continue
        f = d / (member + ".md")
        if not f.exists():
            continue
        try:
            head = f.read_text(encoding="utf-8", errors="replace")[:2000]
        except OSError:
            continue
        if re.search(r"^Obsolete\.", head, re.M):
            return True
    return False


def check(idx: dict | None = None, has_acc=None,
          items: list | None = None, limited: set | None = None) -> tuple[list[str], list[str], bool]:
    """★ 返回 ``(违规, 提示, 是否跑得动)``。"""
    bad: list[str] = []
    warn: list[str] = []
    if idx is None:
        idx = build_index()
    if has_acc is None:
        has_acc = has_access_selections
    if not idx:
        return [], [], False          #: \u2605 \u4fbf\u643a\u6027\uff1a\u63a5\u53e3\u76ee\u5f55\u4e0d\u5728 \u21d2 SKIP
    #: ★ 台账与名单**可注入**（★ 否则测试只能测到“这台机器恰好没漏”）
    if items is None or limited is None:
        try:
            raw = json.loads(LEDGER.read_text(encoding="utf-8"))
            items = raw if isinstance(raw, list) else (raw.get("items") or [])
            limited = {str(i.get("toolbar")) for i in
                       (json.loads(ITEMS.read_text(encoding="utf-8")).get("items") or [])}
        except Exception as exc:                                          # noqa: BLE001
            return ["读不了台账或名单：%s" % str(exc)[:120]], [], True
    for it in items:
        if it.get("tier") != "\u53ef\u653b\u5173":
            continue
        api = str(it.get("api") or "")
        zh = str(it.get("zh") or "?")
        #: \u2605 \u5224\u636e \u2460\uff1aapi \u91cc\u63d0\u5230\u4e00\u4e2a**\u5e26 AccessSelections** \u7684 FeatureData
        for iface in set(IFACE_RE.findall(api)):
            if has_acc(iface) and zh not in limited:
                bad.append("\u300c%s\u300d\u7684 `api` \u63d0\u5230 **`%s`**\uff08\u2605 \u5b83**\u5e26 `AccessSelections`**\uff09"
                           "\u2014\u2014 \u2605 \u6545\u8be5\u6761**\u7591\u4f3c\u5e94\u8fdb\u300c\u540e\u7aef\u5230\u4e0d\u4e86\u300d\u540d\u5355**"
                           "\uff08\u2605 \u800c\u5b83\u8fd8\u5728\u201c\u53ef\u653b\u5173\u201d\uff09" % (zh, iface))
        #: \u2605 \u5224\u636e \u2461\uff1aapi \u91cc\u7684\u6210\u5458\u540d**\u5168\u63a5\u53e3\u90fd\u6ca1\u6709**
        missing = [m for m in set(MEMBER_RE.findall(api))
                   if m not in idx and not m.endswith("FeatureData") and m not in ("Surface", "Silhouette")]
        #: ★★ 2026-10-03（轮 604）**补上一个盲点**（★ 事实 476）：
        #:   判据 ① 只认 `api` 里的 **`*FeatureData` 字样**，
        #:   ★ 而**台账有些条写的是已废弃的旧入口**（如 `InsertProtrusionSwept4`）
        #:   ⇒ ★ 而它的新架构**可能也带 `AccessSelections`**（如 `ISweepFeatureData`）⚠
        #: ★ 故：**`api` 里点名的成员已标废弃** ⇒ ★ **提示**
        #:   （★ 而不拦 —— ★ 废弃本身不等于到不了，★ 事实 379 那类也有活路）
        for m in sorted(set(MEMBER_RE.findall(api))):
            if m in idx and is_obsolete(m):
                warn.append("「%s」的 `api` 点名的 **`%s` 已标废弃**"
                            "（★ 事实 433：**先读 md 头顶那句 `Obsolete`**，"
                            "继任者名字就在那句里）"
                            "—— ★ 而新架构**可能也带 `AccessSelections`**" % (zh, m))
                break
        if missing and len(missing) == len(set(MEMBER_RE.findall(api))):
            warn.append("\u300c%s\u300d\u7684 `api` \u5728\u5168\u63a5\u53e3\u90fd\u67e5\u4e0d\u5230\uff1a%s"
                        "\uff08\u2605 \u94c1\u5f8b 5 \u2014\u2014 \u2605 \u53ef\u80fd\u8be5\u6539\u5224\u201c\u67e5\u4e0d\u5230\u201d\u800c\u975e\u201c\u53ef\u653b\u5173\u201d\uff09"
                        % (zh, ", ".join(sorted(missing)[:4])))
    return bad, warn, True


def main() -> int:
    bad, warn, ran = check()
    print("\u2605 \u540d\u5355**\u5b8c\u6574\u6027**\u95e8\u7981\uff08\u2605 \u8be5\u8fdb\u300c\u540e\u7aef\u5230\u4e0d\u4e86\u300d\u7684\u6709\u6ca1\u6709\u6f0f\uff09")
    if not ran:
        print("   [SKIP] \u63a5\u53e3\u76ee\u5f55 `%s` \u4e0d\u5728\uff08\u2605 \u4fbf\u643a\u6027\u5b88\u536b\uff09" % SWAPI_TYPES)
        return 0
    print("   \u2605 \u5b8c\u6574\u6027\u5224\u636e\uff1a\u2460 `api` \u91cc\u6709\u5e26 `AccessSelections` \u7684 `*FeatureData`\uff1b"
          "\u2461 `api` \u7684\u540d\u5b57\u5168\u63a5\u53e3\u90fd\u67e5\u4e0d\u5230")
    print()
    if bad:
        print("   \u2605\u2605 **\u7591\u4f3c\u6f0f\u6536 %d \u5904**\uff1a" % len(bad))
        for x in bad:
            print("      %s" % x)
        print()
    if warn:
        print("   \u2605 \u63d0\u793a\uff08\u4e0d\u62e6\uff09\uff1a%d \u5904" % len(warn))
        for x in warn[:6]:
            print("      %s" % x)
        print()
    if not bad:
        print("   [ok] \u6ca1\u6709\u7591\u4f3c\u6f0f\u6536\uff08\u2605 \u800c\u8fd9\u53ea\u662f**\u9759\u6001**\u5224\u636e \u2014\u2014 "
              "\u2605 **\u4e0d\u4ee3\u8868\u540d\u5355\u5df2\u7ecf\u5b8c\u6574**\uff09")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
