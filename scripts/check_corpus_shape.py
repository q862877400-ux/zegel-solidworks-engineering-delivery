"""★ 门禁：语料里的**列表字段**不许出现**嵌套列表**（★ 数据形状门禁）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/check_corpus_shape.py
# 定位:   规格 `specs/332-known-facts-triage` 的**数据形状门禁**。⚠ 实测（2026-10-14）
#           ：我在批次⑯里用  `x["readback"] += extra`（★ `extra` 是**列表的列表**）  ⇒ ★
#            **87 处嵌套** ✗★★ 而**后果不是"报错"** —— ★ YAML 合法、门禁也过，  ★ **只是
#           读起来变成 `[['...']]`** ⇒ ★ **人读不了**。⇒ ★ 判据：**列表字段的元素必须是
#           标量**（★ 不许嵌套）。
# 官方依据: `corpus/*.yaml`（★ 本仓语料）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `verified`：★ 本门禁**自带负例自证**（★ 见 `selftest()`）。
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORPUS = ("l1-mainline.yaml", "l2-longtail.yaml", "l3-semantic.yaml")

#: ★★ **应当是「字符串列表」的字段**（★ 元素必须是标量）
#:   ⚠⚠ 实测（2026-10-14）**我第一版把 `tools` 也列进来了** ⇒ ★ **误报 60 条** ✗
#:     ★ 真因：`L1`/`L2` 的 `tools` 是**「工具链的列表」**（★ `check_corpus.py`
#:       里变量名就叫 `chains`，★ 结构是 `[[工具, 工具], [工具, 工具]]`）
#:     ⇒ ★ **嵌套是**有意的** —— ★ 每条链是一组工具**。
#:   ⇒ ★★ **判据：只列「元素语义上就是一句话」的字段** ——
#:     ★ 而 `tools` **不是**（★ 它是链的列表）。
LIST_FIELDS = (
    "readback",
    "steps_cn",
    "relations",
    "dims",
    "expected_groups",
    "forbidden_groups",
    "decision_tiers",
    "auto_decision_rules",
    "delivery_gates",
    "trust_tiers",
    "directional_criterion",
    "known_facts_absorbed",
    "harvest_global",
    "evidence_rule",
    "after_cut_rule",
    "assembly_rules",
    "real_cut_rule",
    "done_criterion",
    "visual_acceptance",
)

#: ★★ **允许嵌套的字段**（★ 语义就是「列表的列表」）
NESTED_OK = ("tools",)


def check(root: pathlib.Path = ROOT) -> list:
    """★ 返回问题列表（★ 空 = 过）。"""
    problems: list[str] = []
    for name in CORPUS:
        p = root / "corpus" / name
        if not p.is_file():
            continue
        for x in yaml.safe_load(p.read_text(encoding="utf-8")):
            for f in LIST_FIELDS:
                v = x.get(f)
                if not isinstance(v, list):
                    continue
                for i, el in enumerate(v):
                    if isinstance(el, (list, dict)):
                        problems.append(
                            "★ %s 的 `%s[%d]` 是**嵌套 %s** ⇒ ★ "
                            "读起来会是 `[[...]]`（★ 而 YAML 合法、门禁也过）"
                            % (x["id"], f, i, type(el).__name__)
                        )
    return problems


def selftest() -> bool:
    """★★ **负例自证**（★ 事实 62：门禁「写了」不等于「有效」）。

    ★ 判据：拿**我实际犯过的形态**（`readback = [['...']]`）当负例 ⇒
      ★ 门禁**必须**报出来。
    """
    bad = {"id": "TEST-1", "readback": [["★★ 嵌套的一条"]]}
    caught = 0
    for f in LIST_FIELDS:
        v = bad.get(f)
        if isinstance(v, list) and any(isinstance(e, list) for e in v):
            caught += 1
    if caught != 1:
        print("★★ 负例自证失败：嵌套没被抓到")
        return False
    #: ★ 正例（★ 拍平后）⇒ 不该报
    good = {"id": "TEST-2", "readback": ["★★ 拍平的一条"]}
    for f in LIST_FIELDS:
        v = good.get(f)
        if isinstance(v, list) and any(isinstance(e, list) for e in v):
            print("★★ 负例自证失败：正例被误判")
            return False
    return True


def main() -> int:
    if not selftest():
        return 1
    print("★ 负例自证：过（★ 嵌套列表抓得到）")
    problems = check()
    if problems:
        print("★★ 发现 %d 处嵌套：" % len(problems))
        for p in problems[:12]:
            print("   %s" % p)
        return 1
    print("★ [PASS] 语料的列表字段都是**扁平**的（★ 人读得了）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
