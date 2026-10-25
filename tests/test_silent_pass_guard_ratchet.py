"""★ 棘轮：字段守护式判据的清单只允许**逐条登记**，新出现的一律红。

## 为什么做棘轮而不是只做一次扫描

第 33 / 35 / 36 轮各修一处同类缺陷，机制完全相同：

> 判据写成 `if <字段真值>:`，体内 fail，**假分支什么都不做** ⇒
> 只要不声明（让字段为空/假），判据就不生效，函数一路走到 `PASS`。

第 37 轮扫描 `scripts/engineering/acceptance/` 全部 `judge_*`，收紧判据后**共 10 处**：

- 9 处是**正确用法**：`not v["opened_existing"]` ⇒ fail（这事本来就必须做），
  或 `not v["clearance_basis"]` ⇒ fail（间隙无依据）
- 1 处（`v["evidence_version"] and v["artifact_version"]`）**曾是缺口**，
  第 36 轮已由采集层的 `complete` 守住

⇒ 一次性扫描的价值会随时间蒸发。**做成棘轮**：清单钉在下面，
    新出现第 11 处 ⇒ 本测试红 ⇒ 必须先判断它是缺口还是合法用法，再登记。

★ 为什么用 `test` 源码文本而不是行号做键：行号会随无关改动漂移，
  源码文本只在判据真的变了时才变。

## 登记纪律

要往 `_BASELINE` 里加一条，必须回答两个问题：

1. 这个字段为假/空时，函数**去了哪里**？
2. 那个去处是 `unknown`（可接受）还是 `pass`（缺口）？

答不出就说明还没读懂，不许登记。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO))

import pytest  # noqa: E402

from audit_silent_pass_guards import TARGET, scan  # noqa: E402

#: ★ 已核过的 10 处。每条写清「字段为假时去哪里」。
#:   key = "文件::判定器::条件源码"
_BASELINE = {
    "scripts/engineering/acceptance/e2_e3_solid.py::judge_rebuild"
    "::not v['opened_existing']":
        "fail ⇒ 本来就该 fail（必须打开既有件），不是缺口",
    "scripts/engineering/acceptance/e2_e3_solid.py::judge_rebuild"
    "::not v['downstream_linked']":
        "fail ⇒ 本来就该 fail（下游没联动就是 E2 fail）",
    "scripts/engineering/acceptance/e2_e3_solid.py::judge_rebuild"
    "::not v['reopened_ok']":
        "fail ⇒ 本来就该 fail（重开失败就是不可重建）",
    "scripts/engineering/acceptance/e2_e3_solid.py::judge_feature_tree"
    "::not v['editable_prefix_verified']":
        "fail ⇒ 本来就该 fail（前序不可编辑）",
    "scripts/engineering/acceptance/e4_assembly.py"
    "::judge_assembly_interference::not v['clearance_basis']":
        "fail ⇒ 间隙无依据（ENGINEERING-PATH 点名的负例）",
    "scripts/engineering/acceptance/e4_assembly.py"
    "::judge_assembly::not v['clearance_basis']":
        "fail ⇒ 同上，两处子项各自判",
    "scripts/engineering/acceptance/e5_e6_drawing.py"
    "::judge_drawing::not v['material_from_requirement']":
        "fail ⇒ 默认材料（ENGINEERING-PATH 点名的负例）",
    "scripts/engineering/acceptance/e7_provenance.py"
    "::judge_provenance::v['evidence_version'] and v['artifact_version']":
        "★ 曾是缺口（为空则整条跳过 ⇒ 静默 pass），第 36 轮已由采集层 complete 守住",
    "scripts/engineering/acceptance/e7_provenance.py"
    "::judge_provenance::not v['outputs']":
        "fail ⇒ 无复算依据（ENGINEERING-PATH 点名的负例）",
}


def _key(row: dict) -> str:
    return "%s::%s::%s" % (row["file"], row["judge"], row["test"])


def _current() -> dict:
    rows = []
    for p in sorted(TARGET.glob("*.py")):
        rows.extend(scan(p))
    return {_key(r): r for r in rows}


def test_没有未登记的字段守护式判据() -> None:
    """★★ 新出现第 11 处 ⇒ 红。必须判断它是缺口还是合法用法，再登记。

    ★ 这条挡的是本仓最系统性的缺陷类（33/35/36 三轮同一机制）。
    """
    cur = _current()
    new = sorted(set(cur) - set(_BASELINE))
    assert new == [], (
        "★ 出现未登记的「字段守护式判据」%d 处 —— 逐条判断「字段为假时去了哪里」：\n%s\n"
        "★ 若去处是 `pass` ⇒ 这是缺口（不声明就能绕过）；若是 `unknown`/`fail` ⇒ "
        "登记进 _BASELINE 并写明理由。"
        % (len(new), "\n".join("   - %s" % k for k in new))
    )


def test_已登记的都还在() -> None:
    """★★ 名单腐坏：登记的判据已经不存在（被删/被改）⇒ 红，必须同步删登记。

    ★ 与 `docs/gate-wiring-exemptions.json` 的「豁免了不该豁免的」同一口径。
    """
    cur = _current()
    gone = sorted(set(_BASELINE) - set(cur))
    assert gone == [], (
        "★ 登记里有 %d 条已不存在 ⇒ 名单腐坏，请同步删除登记：\n%s"
        % (len(gone), "\n".join("   - %s" % k for k in gone))
    )


def test_每条登记都写了归属() -> None:
    """★ 没有理由的登记等于没登记。"""
    for key, why in _BASELINE.items():
        assert str(why).strip(), "★ %s 没有登记理由" % key


def test_扫描器本身抓得到伪造样本() -> None:
    """★★ 负例自证：扫描器必须抓得到「字段守护式 `if` 体内 fail」。

    ★ 否则「10 处全是正确用法」这个结论可能只是扫描器没在看。
    """
    import textwrap

    fake = textwrap.dedent(
        '''
        def judge_fake(obs):
            v = obs
            if v["suspicious_field"]:
                return "Status.FAIL"
            return "Status.PASS"
        '''
    )
    tmp = Path(REPO / "output" / "_fake_guard.py")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(fake, encoding="utf-8")
    try:
        rows = scan(tmp)
    finally:
        tmp.unlink(missing_ok=True)
    assert len(rows) == 1, "★ 扫描器没抓到伪造样本：%r" % (rows,)
    assert rows[0]["test"] == "v['suspicious_field']"
    assert rows[0]["has_else"] is False
