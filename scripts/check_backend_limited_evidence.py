"""★ 门禁：**「后端到不了」名单**的每条都必须**写明依据**（★ 任务书那句的机器判据）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁）
# 文件:   scripts/check_backend_limited_evidence.py
# 定位:   ★ 2026-10-03（轮 600）★ 给**第五桶**（`docs/backend-limited-items.json`）配
#           门禁。
#
#   ★★ **为什么需要**（★ 事实 40）：★ **一个没人查的桶，等于没有桶** ——
#     ★ 而轮 599 刚把那个桶接进台账（`tier()` 的第五桶）⇒ ★ **它现在会被读了**；
#     ★ 而**名单本身的内容**还没有任何东西守着 ⚠
#
#   ★★★ **而门禁的判据就是任务书那句的机器版** —— 任务书逐字：
#     > 凡属 pywin32 后端结构性到不了的（…），**写明依据并单列**，不假装做到。
#     ⇒ ★ **"写明依据" = 每条必须能指到**依据****：★ 一个 `section`（★ 边界文档的小节）
#       **且** 至少一个 `facts`（★ 事实编号）✓
#
# ★ 另查：★ **不能是空名单**（★ 空名单就等于"什么都没单列"，★ 而那与任务书说的三族矛盾）
# ；
# ★ 而 `toolbar` / `member` / `where` 三字段**必须非空**（★ 否则那一行读不出"哪里到不了"
# ）。
#
#   ★ 退出码：★ 违规 ⇒ 1。
#   ★ 配套负例：`tests/test_backend_limited_evidence_gate.py`（★ 事实 62）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

#: 2026-10-03（接手轮）强制 stdout 为 UTF-8 —— 本门禁会 print 中文与箭头/勾这类符号，
#:   而 stdout 是管道时（测试正是用管道抓输出）默认按 locale（本机 GBK）编码
#:   ⇒ UnicodeEncodeError: 'gbk' codec can't encode character … ⇒ 门禁自己崩掉。
#:   known-facts 58 那一族（中文 Windows 上两侧默认编码不一致 —— 病灶在输出侧）；
#:   而测试那侧的 subprocess.run 已经带了 encoding='utf-8'。
sys.stdout.reconfigure(encoding="utf-8")

R = Path(__file__).resolve().parent.parent
ITEMS = R / "docs" / "backend-limited-items.json"
LIMITS_DOC = R / "docs" / "toolbar-gaps-backend-limits.md"

#: \u2605 \u6bcf\u6761**\u5fc5\u987b\u975e\u7a7a**\u7684\u5b57\u6bb5
REQUIRED = ("toolbar", "member", "where", "section")


def check(data: dict | None = None) -> list[str]:
    """★ 返回违规清单 —— ★ **纯函数**，供测试注入伪造数据。"""
    bad: list[str] = []
    if data is None:
        try:
            data = json.loads(ITEMS.read_text(encoding="utf-8"))
        except Exception as exc:                                          # noqa: BLE001
            return ["`docs/backend-limited-items.json` 读不了或不是 JSON：%s" % str(exc)[:120]]
    items = data.get("items")
    if not isinstance(items, list):
        return ["`items` 不是列表（★ 名单形状不对）"]
    if not items:
        return ["★ **名单是空的** —— ★ 而任务书点名的三族**至少有一条**，"
                "空名单等于\u201c什么都没单列\u201d（★ 与任务书矛盾）"]
    for i, it in enumerate(items):
        tag = "第 %d 条（%s）" % (i + 1, str(it.get("toolbar") or "?")[:24])
        for k in REQUIRED:
            if not str(it.get(k) or "").strip():
                bad.append("%s 的 `%s` 是空的（★ 任务书：**写明依据**）" % (tag, k))
        #: \u2605 **\u4f9d\u636e\u4e4b\u4e00\uff1a\u81f3\u5c11\u4e00\u4e2a\u4e8b\u5b9e\u
        #: 7f16\u53f7**
        facts = it.get("facts")
        if not isinstance(facts, list) or not facts:
            bad.append("%s **没有 `facts`**（★ 至少指一个事实编号 —— 那才是\u201c写明依据\u201d）" % tag)
        else:
            for f in facts:
                if not isinstance(f, int) or f <= 0:
                    bad.append("%s 的 `facts` 里有非法编号：%r" % (tag, f))
        #: \u2605 **\u4f9d\u636e\u4e4b\u4e8c\uff1a`section` \u5f15\u7684\u5c0f\u8282\u77
        #: 1f\u5b58\u5728\u4e8e\u8fb9\u754c\u6587\u6863**
        sec = str(it.get("section") or "").strip()
        if sec:
            try:
                doc = LIMITS_DOC.read_text(encoding="utf-8")
                if sec not in doc:
                    bad.append("%s 的 `section` = %r **在 `%s` 里找不到**"
                               "（★ 依据要能指到**真存在**的小节）"
                               % (tag, sec, LIMITS_DOC.name))
            except Exception as exc:                                      # noqa: BLE001
                bad.append("读不了 `%s`：%s" % (LIMITS_DOC.name, str(exc)[:80]))
    return bad


def main() -> int:
    bad = check()
    try:
        n = len(json.loads(ITEMS.read_text(encoding="utf-8")).get("items") or [])
    except Exception:                                                     # noqa: BLE001
        n = -1
    print("★ 「后端到不了」名单的证据门禁（★ 任务书：**写明依据并单列**）")
    print("   名单：`docs/backend-limited-items.json` · **%d** 条" % n)
    print()
    if bad:
        print("   ★★ **违规 %d 处**：" % len(bad))
        for x in bad:
            print("      %s" % x)
        print()
        return 1
    print("   [ok] 每条都写明依据（★ `section` 真存在 + 至少一个 `facts` 编号）"
          "（★ 而这只说明\u201c**依据指得到**\u201d，★ **不证明依据本身成立**）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
