"""★ 设多值 COM 参数后必须**读回** —— 赋值「回 True」不等于值进去了。

## 现场（第 49 轮真机）

同一个 `ICoincidentMateFeatureData` 对象上，两种赋法：

```
① setattr(data, "EntitiesToMate", (f1, f2))
   ⇒ set_entities=True，但 **readback entities = 0** ⇒ 值根本没进去
② setattr(data, "EntitiesToMate", VARIANT(VT_ARRAY|VT_DISPATCH, [f1, f2]))
   ⇒ set_entities=True，**readback entities = 2** ⇒ 真的进去了
```

旁证：同一轮 `data.MateAlignment = 2`（`int`）**读回就是 2** ⇒ 差别在**类型**：
`System.int` vs `System.object`（VARIANT 里的对象数组）。

★★★ 这条**推翻**了第 45/48 轮记的「显式设 `EntitiesToMate` 也没用」——
  那次设置从未生效，所以那个「排除」不算数。

## 本文件钉什么

本仓的探针里，凡给多值 COM 参数赋值的地方都必须：
① 用 `VARIANT(VT_ARRAY|VT_DISPATCH, [...])` 而不是裸元组
② **读回**并记录 `setup_effective`
③ 只有 `setup_effective` 为真时，后续「建不出来」的结论才算数

★ 为什么不连真机跑：验证它需要一次真机装配会话；行为级证据在
  `tools/probe_e4_assembly.py` 的输出（`setup_effective: True`），
  这里钉的是**源码里必须有的两道**，防以后被改掉。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

_PROBE = REPO / "tools" / "probe_e4_assembly.py"
_FACTS = REPO / "docs" / "known-facts.md"


def _probe_src() -> str:
    return _PROBE.read_text(encoding="utf-8")


def test_用_VARIANT_对象数组而不是裸元组() -> None:
    """★★ 核心：裸元组会被静默存成 0。"""
    src = _probe_src()
    assert "VT_ARRAY" in src and "VT_DISPATCH" in src, (
        "★ 没有用 VARIANT(VT_ARRAY|VT_DISPATCH) ⇒ EntitiesToMate 会静默存成 0"
    )
    assert "EntitiesToMate" in src


def test_赋值后必须读回() -> None:
    """★★ 赋值「回 True」不等于值进去了 ⇒ 必须读回。"""
    src = _probe_src()
    i = src.find("EntitiesToMate")
    assert i > 0
    tail = src[i:]
    assert "readback" in tail, "★ 设完 EntitiesToMate 后没有读回"
    assert "setup_effective" in tail, "★ 没有把「设置是否生效」记成判据"


def test_setup_effective_要求两个都到() -> None:
    """★ 两个参数都要验：entities==2 **且** alignment==2。"""
    src = _probe_src()
    i = src.find("setup_effective")
    assert i > 0
    seg = src[max(0, i - 200):i + 200]
    assert 'back["entities"] == 2' in seg, "★ 没验 entities 读回"
    assert 'back["alignment"] == 2' in seg, "★ 没验 alignment 读回"


def test_事实里记了这条且标注了推翻() -> None:
    """★★ 过时的「排除」必须被标注 —— 否则后来人会照它绕开。"""
    t = _FACTS.read_text(encoding="utf-8")
    assert "VARIANT" in t and "VT_DISPATCH" in t, "★ 事实里没记 VARIANT 这条"
    assert "推翻" in t, "★ 事实里没标注它推翻了此前的「排除」"


def test_事实记了_GetDocuments_是属性() -> None:
    """★ 同一轮踩了两次：`sw.GetDocuments()` 会 TypeError。"""
    t = _FACTS.read_text(encoding="utf-8")
    assert "GetDocuments" in t, "★ 事实里没记 GetDocuments 是属性的坑"
