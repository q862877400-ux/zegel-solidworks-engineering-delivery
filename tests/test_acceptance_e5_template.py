"""★ E5 的 `template_ok` 判据：不合格必拒，但「模板名带 GB」**不是**通过的理由。

## 洞（第 21 轮实测）

`template_ok` 一直在采集，但判定器从没读过它。实测：

```python
collect_drawing(..., template_ok=False)  # 其余全对
judge_drawing(...) ⇒ pass                # ← 模板不合格的图纸也能过
```

## 两侧都要测

E5 的「不能当替代品」栏逐字：**注释数量达标、文件非空、模板名带 GB** 都不算理由。

⇒ 所以本文件两侧都钉：

| 侧 | 断言 |
|---|---|
| **该拒的** | `template_ok=False` ⇒ **fail** |
| **不该当理由的** | `template_ok=True` 但别的缺失 ⇒ **仍然 fail**（模板合格不构成通过） |
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from engineering.acceptance.e5_e6_drawing import (  # noqa: E402
    collect_drawing,
    judge_drawing,
)
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-E5"

_ITEMS = (
    {"name": "孔径", "evidence": "D1@图纸1", "value_ok": True},
    {"name": "孔位", "evidence": "D2@图纸1", "value_ok": True},
)


def _obs(**kw):
    base = dict(
        target="板1 工程图",
        required_items=("孔径", "孔位"),
        bound_items=_ITEMS,
        model_revision="rev1",
        drawing_revision="rev1",
        material_from_requirement=True,
        template_ok=True,
    )
    base.update(kw)
    return collect_drawing(**base)


def test_模板不合格必须判fail() -> None:
    """★★★ 核心：模板不合格 ⇒ 整张图不合规。"""
    res = judge_drawing(_obs(template_ok=False), requirement_id=REQ)
    assert res.status is Status.FAIL, "★ 模板不合格应判 fail，实得 %s" % res.status.value
    assert "模板" in res.reason


def test_模板合格本身不是通过理由() -> None:
    """★★ 反向：`template_ok=True` 但别的缺失 ⇒ 仍然 fail。

    ★ E5 的「不能当替代品」栏逐字写着「模板名带 GB」不算理由。
      本断言防的正是「加了 template 判据之后，把它当成通过条件」。
    """
    res = judge_drawing(_obs(template_ok=True, required_items=()), requirement_id=REQ)
    assert res.status is not Status.PASS, (
        "★ 必填清单为空却判 pass ⇒ 判据空转（实得 %s）" % res.status.value
    )


def test_模板合格但材料是默认值仍fail() -> None:
    """★ 模板合格 + 材料默认 ⇒ fail（材料那条不能被模板盖过）。"""
    res = judge_drawing(
        _obs(template_ok=True, material_from_requirement=False), requirement_id=REQ
    )
    assert res.status is Status.FAIL
    assert "材料" in res.reason


def test_模板合格但证据为空仍fail() -> None:
    """★ 模板合格 + 证据空 ⇒ fail（R-06 那条不能被模板盖过）。"""
    items = (
        {"name": "孔径", "evidence": "", "value_ok": True},
        {"name": "孔位", "evidence": "D2@图纸1", "value_ok": True},
    )
    res = judge_drawing(_obs(template_ok=True, bound_items=items), requirement_id=REQ)
    assert res.status is Status.FAIL
    assert "证据" in res.reason


def test_全对才pass() -> None:
    """★ 右侧：模板合格 + 全绑好 + 证据非空 + 值对 + 同修订 + 材料来自需求 ⇒ pass。"""
    res = judge_drawing(_obs(template_ok=True), requirement_id=REQ)
    assert res.status is Status.PASS, "★ 全对应判 pass，实得 %s（%s）" % (
        res.status.value,
        res.reason,
    )


def test_模板判据在材料判据之前() -> None:
    """★ 顺序有意义：模板不合格时先报模板，避免被后面的问题盖住。"""
    res = judge_drawing(
        _obs(template_ok=False, material_from_requirement=False), requirement_id=REQ
    )
    assert res.status is Status.FAIL
    assert "模板" in res.reason, "★ 模板问题应优先报出，实得：%s" % res.reason
