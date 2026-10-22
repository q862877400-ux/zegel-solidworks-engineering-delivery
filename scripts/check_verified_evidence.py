"""★ 门禁：**`level: verified` 必须带我们自己的运行证据**（★ A4 的机器判据）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁）
# 文件:   scripts/check_verified_evidence.py
# 定位:   ★ 2026-10-03（轮 594）★ 把 **A4** 那句「`verified` 必须有我们自己的运行证据
#           」固化成门禁。
#
#   ★★ **为什么需要**（★ 本仓纪律 A4 逐字）：
#     > 每个条目的 `level` 取自五级枚举；**`verified` 必须有我们自己的运行证据**。
#     ★ 而 `AGENTS.md` 又写明 **`level: verified` 只表示「有我们自己的运行证据」** ——
#       ★ **不是**「代码是我们写的」（★ A2 那条注释）。
#
#   ★★★ **而实测（轮 594）**：`capabilities.yaml` 里 `verified` **95** 条、
#     ★ **其中无 `evidence` 的 0 条** —— ★ **数据是干净的** ✓
#     ★ 而**没有任何门禁在守它** ⇒ ★ **下一次谁把一条标成 `verified` 而忘了写证据，没人会知道** ⚠
#     ★ 那正是**事实 40** 的另一种形态：★ **"守卫存在但没人用" ≡ "没有守卫"**；
#       ★ 而这里更微妙 —— ★ **数据干净、而没有任何东西保证它继续干净**。
#
#   ★ 判据：★ 对每条 `level == "verified"`，★ 断言 `evidence` 是**非空列表**、
#     ★ 且**至少有一条非空字符串**（★ 空串不算证据）。
#   ★ 另有**提示级**：`evidence` 里找不到**证据文件/脚本名**的（★ `.py` / `.json` / `tests/`），
#     ★ 只提示、不拦（★ 因为口述证据也可以是证据，★ 而**可核**的更好）。
#
#   ★ 退出码：★ 违规 ⇒ 1；★ 只有提示 ⇒ 0。
#   ★ 配套负例：`tests/test_verified_evidence_gate.py`（★ 事实 62：门禁"写了"不等于"有效"）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

#: 2026-10-03（接手轮）强制 stdout 为 UTF-8 —— 本门禁会 print 中文与箭头/勾这类符号，
#:   而 stdout 是管道时（测试正是用管道抓输出）默认按 locale（本机 GBK）编码
#:   ⇒ UnicodeEncodeError: 'gbk' codec can't encode character … ⇒ 门禁自己崩掉。
#:   known-facts 58 那一族（中文 Windows 上两侧默认编码不一致 —— 病灶在输出侧）；
#:   而测试那侧的 subprocess.run 已经带了 encoding='utf-8'。
sys.stdout.reconfigure(encoding="utf-8")

R = Path(__file__).resolve().parent.parent
CAPS = R / "capabilities.yaml"

#: \u2605 **\u53ef\u6838**\u7684\u8bc1\u636e\u5f62\u6001\uff08\u2605 \u6587\u4ef6\u540d / \u811a\u672c\u540d / \u6d4b\u8bd5\u8def\u5f84\uff09
CITE_RE = re.compile(r"[\w./\\-]+\.(?:py|json|md|txt)|tests/[\w./-]+")


def _load() -> list[dict]:
    raw = CAPS.read_text(encoding="utf-8")
    return json.loads(raw)["capabilities"]


def check(caps: list[dict] | None = None) -> tuple[list[str], list[str]]:
    """★ 返回 ``(违规, 提示)`` —— ★ 纯函数，供测试注入伪造数据。"""
    bad: list[str] = []
    warn: list[str] = []
    for c in (caps if caps is not None else _load()):
        if c.get("level") != "verified":
            continue
        ev = c.get("evidence")
        cid = c.get("id", "?")
        if not ev:
            bad.append("`%s` \u6807\u4e86 `verified` \u800c**\u6ca1\u6709 evidence** \u5b57\u6bb5"
                       "\uff08\u2605 A4\uff1a`verified` \u5fc5\u987b\u5e26**\u6211\u4eec\u81ea\u5df1\u7684\u8fd0\u884c\u8bc1\u636e**\uff09" % cid)
            continue
        if not isinstance(ev, list):
            bad.append("`%s` \u7684 `evidence` \u4e0d\u662f\u5217\u8868\uff08\u2605 \u5f62\u72b6\u4e0d\u5bf9\uff09" % cid)
            continue
        if not any(str(x).strip() for x in ev):
            bad.append("`%s` \u7684 `evidence` **\u5168\u662f\u7a7a\u4e32**\uff08\u2605 \u7a7a\u4e32\u4e0d\u7b97\u8bc1\u636e\uff09" % cid)
            continue
        if not any(CITE_RE.search(str(x)) for x in ev):
            warn.append("`%s` \u7684\u8bc1\u636e\u91cc**\u627e\u4e0d\u5230\u53ef\u6838\u7684\u6587\u4ef6\u540d**"
                        "\uff08\u2605 \u5982 `output/xxx.json` \u6216 `tests/xxx.py`\uff09\u2014\u2014 "
                        "\u2605 \u53ea\u63d0\u793a\uff0c\u4e0d\u62e6" % cid)
    return bad, warn


def main() -> int:
    try:
        caps = _load()
    except Exception as exc:                                              # noqa: BLE001
        print("[FAIL] \u8bfb\u4e0d\u4e86 `capabilities.yaml`\uff1a%s" % exc)
        return 1
    bad, warn = check(caps)
    ver = [c for c in caps if c.get("level") == "verified"]
    print("\u2605 A4 \u95e8\u7981\uff1a`verified` \u5fc5\u987b\u5e26\u8fd0\u884c\u8bc1\u636e")
    print("   \u2605 `verified` \u6761\u76ee\uff1a**%d** \u6761\uff1b\u5176\u4e2d**\u65e0 evidence**\u7684\uff1a**%d** \u6761"
          % (len(ver), sum(1 for c in ver if not (c.get("evidence") or []))))
    print()
    if bad:
        print("   \u2605\u2605 **\u8fdd\u89c4 %d \u5904**\uff1a" % len(bad))
        for x in bad:
            print("      %s" % x)
        print()
    if warn:
        print("   \u2605 \u63d0\u793a\uff08\u4e0d\u62e6\uff09\uff1a%d \u6761\u7684\u8bc1\u636e\u91cc\u627e\u4e0d\u5230\u53ef\u6838\u7684\u6587\u4ef6\u540d\uff1a" % len(warn))
        for x in warn[:8]:
            print("      %s" % x)
        if len(warn) > 8:
            print("      \u2026\u8fd8\u6709 %d \u6761" % (len(warn) - 8))
        print()
    if not bad:
        print("   [ok] \u6bcf\u6761 `verified` \u90fd\u5e26\u8bc1\u636e\uff08\u2605 \u800c\u8fd9\u53ea\u8bf4\u660e"
              "\u201c**\u5b57\u6bb5\u5728**\u201d\uff0c\u2605 **\u4e0d\u8bc1\u660e\u8bc1\u636e\u771f\u7684\u652f\u6301\u90a3\u4e2a\u7ed3\u8bba**\uff09")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
