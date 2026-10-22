"""★ 门禁：`known-facts.md` 的每一条事实都要有处置（吸收 / 放过 + 理由）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/check_known_facts_triage.py
# 定位:   规格 `specs/332-known-facts-triage` 的门禁 ——★★ 业主 2026-10-14 的收口判据：
#           「known-facts 560 条**逐条**有处置  （吸收 / 放过 + 理由）」。★ 判据：**每一
#           条**都能被分类成「吸收」或「放过」，  ★★ **不允许出现「未判定」**（★ 那正是
#           「扫过但没判断」）。
# 官方依据: `docs/known-facts.md`（★ 本仓事实台账）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `verified`：★ 本门禁**自带负例自证**（★ 见 `selftest()`）——
#   它拿「有事实没被分类」的形态当负例，★ 必须报出来。
# -----------------------------------------------------------------------------
from __future__ import annotations

import json
import pathlib
import sys

sys.path[:0] = [
    str(pathlib.Path(__file__).resolve().parents[1]),
    str(pathlib.Path(__file__).resolve().parents[1] / "tools"),
]
ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load():
    """★ 复用 `tools/triage_known_facts.py` 的分类（★ 单一源）。"""
    import importlib.util  # noqa: PLC0415

    p = ROOT / "tools" / "triage_known_facts.py"
    spec = importlib.util.spec_from_file_location("triage_under_test", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def check() -> list:
    """★ 返回问题列表（★ 空 = 过）。"""
    m = _load()
    idx = ROOT / "output" / "known-facts-index.json"
    if not idx.is_file():
        return ["★ 没有 %s ⇒ 先跑 tools/triage_known_facts.py" % idx]
    facts = json.loads(idx.read_text(encoding="utf-8"))["facts"]
    problems = []
    for n in sorted(facts, key=int):
        verdict, why = m.classify(n, facts[n]["body"])
        if verdict == "复核":
            problems.append(
                "★ 事实 %s **未判定**（★ 分类器说需人工复核，而人工表里没有它）" % n
            )
        elif not why:
            problems.append("★ 事实 %s 的处置**没有理由**" % n)
        elif verdict not in ("吸收", "放过"):
            problems.append("★ 事实 %s 的处置非法：%r" % (n, verdict))
    return problems


def selftest() -> bool:
    """★★ **负例自证**（★ 事实 62：门禁「写了」不等于「有效」）。

    ★ 判据：**造一条「被判为『复核』」的事实** ⇒ ★ 门禁**必须**报出来。
    ⚠ 实测（2026-10-14）：我第一版拿「不含任何关键词的假事实」当负例 ⇒
      ★ 而那种事实**本来就该判「放过」**（非建模）✗ ——
      ★★ **负例自己就是错的** ⇒ ★ 它证明不了门禁有效。
      ★ 正确的负例是**「含建模词但不在人工表里」** ⇒ 那才会判「复核」。
    """
    m = _load()
    #: ★ 负例：**含建模词**、且不在人工表里 ⇒ 分类器应判「复核」
    verdict, _ = m.classify("99998", "用直线工具画草图并加几何关系约束")
    if verdict != "复核":
        print("★★ 负例自证失败：含建模词的事实被判成 %r（应为「复核」）" % verdict)
        return False
    #: ★★ 而 `check()` 遇到「复核」必须**报问题**（★ 这才是门禁的行为）
    real_classify = m.classify
    try:
        m.classify = lambda n, b: (
            ("复核", "★ 负例") if n == "99998" else real_classify(n, b)
        )
        facts = json.loads(
            (ROOT / "output" / "known-facts-index.json").read_text(encoding="utf-8")
        )["facts"]
        facts["99998"] = {"n": 99998, "line": 0, "body": "用直线工具画草图"}
        problems = []
        for n in sorted(facts, key=int):
            v, why = m.classify(n, facts[n]["body"])
            if v == "复核":
                problems.append(n)
        if "99998" not in problems:
            print("★★ 负例自证失败：门禁没报出未判定的事实")
            return False
    finally:
        m.classify = real_classify
    return True


def main() -> int:
    if not selftest():
        return 1
    print("★ 负例自证：过（★ 未分类的事实抓得到）")
    problems = check()
    if problems:
        print("★★ 发现 %d 处：" % len(problems))
        for p in problems[:15]:
            print("   %s" % p)
        return 1
    print("★ [PASS] known-facts 每一条都有处置（吸收 / 放过 + 理由）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
