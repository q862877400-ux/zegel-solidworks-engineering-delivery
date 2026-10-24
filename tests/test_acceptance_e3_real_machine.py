"""★ E3 真机读数 → 判定器：把第 15 轮实测值钉进测试。

## 真机读数（`tools/probe_s3_e3_feature_tree.py`，2026-10-25）

交付件 `板1_rev-1` 的副本上：

```
① 特征 15 个 · 类型词表（**量出来的**）：ProfileFeature / Extrusion / ICE
   草图1        type=ProfileFeature  faces=0 父=2 子=1
   凸台-拉伸1    type=Extrusion       faces=6 父=3 子=4
   草图2..5     type=ProfileFeature  faces=0 父=1 子=1
   切除-拉伸1..4 type=ICE            faces=1 父=3 子=0
   错误/警告：GetWhatsWrongCount = 0
② 尺寸 D1@草图1 = 100.0 → 改成 120.0（改**已有**尺寸，不是新建）
③ 下游：错误 0 · 特征数 15 不变 · 孔特征 4 个仍在 · 包围盒 X 100.0 → 120.0 mm
```

★ 类型名是**测出来的**，不是猜的 —— `ICE` 就是本机给「切除-拉伸」的类型名，
  若按印象写 `"Cut"` / `"Extrusion"` 会判错（铁律 5）。

## 这份测试钉什么

把上面那组真实数值喂给 `collect_feature_tree` + `judge_feature_tree`，
断言它判 **pass**；再钉住几个负例与「不能当替代品」的边界。
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from engineering.acceptance.e2_e3_solid import (  # noqa: E402
    collect_feature_tree,
    judge_feature_tree,
)
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-E3"

#: ★ 真机量出来的类型词表（`GetTypeName2` 原样回读）
NATIVE_TYPES = ("ProfileFeature", "Extrusion", "ICE")


def _obs(**kw):
    """真机读数作默认值。"""
    base = dict(
        target="板1_rev-1(副本)",
        feature_count=15,
        native_features=15,
        imported_solids=0,
        dangling_refs=0,
        errors=0,
        warnings=0,
        editable_prefix_verified=True,
        version="2026-10-25",
    )
    base.update(kw)
    return collect_feature_tree(**base)


def test_真机读数判pass() -> None:
    """★★ 核心：15 个原生特征、零错误、前序可编辑且下游跟随 ⇒ pass。"""
    res = judge_feature_tree(_obs(), requirement_id=REQ)
    assert res.status is Status.PASS, "★ 真机读数应判 pass，实得 %s（%s）" % (
        res.status.value,
        res.reason,
    )


def test_导入死实体冒充原生必须判fail() -> None:
    """★ E3 的负例：只有导入实体、没有原生特征。"""
    res = judge_feature_tree(
        _obs(feature_count=1, native_features=0, imported_solids=1), requirement_id=REQ
    )
    assert res.status is Status.FAIL
    assert "原生" in res.reason or "导入" in res.reason


def test_悬空引用必须判fail() -> None:
    res = judge_feature_tree(_obs(dangling_refs=2), requirement_id=REQ)
    assert res.status is Status.FAIL
    assert "悬空" in res.reason


def test_特征树有错误必须判fail() -> None:
    res = judge_feature_tree(_obs(errors=1), requirement_id=REQ)
    assert res.status is Status.FAIL
    assert "错误" in res.reason


def test_采集不完整判unknown() -> None:
    """★ 没采齐 ⇒ unknown，不得判绿。"""
    from engineering.acceptance.e2_e3_solid import collect_feature_tree as C

    obs = C(
        target="x",
        feature_count=0,
        native_features=0,
        imported_solids=0,
        dangling_refs=0,
        errors=0,
        warnings=0,
        editable_prefix_verified=False,
    )
    res = judge_feature_tree(obs, requirement_id=REQ)
    assert res.status is not Status.PASS, "★ 采集不完整不得判 pass"


def test_类型词表是真机测的而非猜的() -> None:
    """★★ 防「凭印象写类型名」：词表必须来自实测，且不含猜出来的名字。

    ★ 本机给「切除-拉伸」的类型名是 **`ICE`** ——
      若后人按印象改成 `"Cut"` / `"CutExtrude"`，这条会红。
    """
    assert "ICE" in NATIVE_TYPES, "★ 切除-拉伸 的本机类型名是 ICE（实测），不要改成 Cut"
    assert "ProfileFeature" in NATIVE_TYPES
    assert "Extrusion" in NATIVE_TYPES
    for guess in ("Cut", "CutExtrude", "Extrude", "Sketch"):
        assert guess not in NATIVE_TYPES, "★ %r 是凭印象的名字，不是实测值" % guess
