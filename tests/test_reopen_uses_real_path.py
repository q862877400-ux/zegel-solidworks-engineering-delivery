"""★ 保存后重开必须用**实际路径**（`GetPathName()`）—— 第 55 轮修的真 bug。

## 现场

`E2.rebuild` 的四个读数全对（孔心位移 `[20.0]×4`、重建错误 0、bbox 100→120）
却判 **fail**，理由「保存后重开不成立 ⇒ 参数化关系没有真正落进文件」。

## 根因

运行器保存后这样重开：

```python
ok_r, doc2 = _try(c_.open_document, sw, str(copy))   # copy 是**沙箱前**的路径
```

而 **`sw_guard` 会把输入文件改名**（实测形如 `板1_rev-1__44.SLDPRT`）。
按 `copy` 路径重开读到的是**另一个文件**（仍是 100mm 宽）
⇒ `extent_after_reopen != 120` ⇒ 被误判成「参数关系没落盘」。

★★ 这条本仓早有记载（「sw_guard 沙箱会重命名输入文件 ⇒ 必须用 `GetPathName()`」），
   第 55 轮又踩了一次。**踩一次记一次，钉成测试才不会再踩第三次。**

## 本文件钉什么

① 重开那一步**不许**用 `str(copy)`
② 必须有 `GetPathName` 取实际路径
③ 两个尺寸读数（保存前 / 重开后）必须写进证据（否则下次又要靠猜）
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_RUNNER = REPO / "tools" / "run_s3_acceptance.py"


def _src() -> str:
    return _RUNNER.read_text(encoding="utf-8")


def test_重开不许用沙箱前的_copy_路径() -> None:
    """★★ 核心：`open_document(..., str(copy))` 是那个 bug 的原形。

    ★ 只查**保存之后**那一段 —— 初次打开用 `str(copy)` 是**对的**
      （那时还没有改名问题；改的是同一个文件的路径）。
      第一版测试没分段，把初次打开的合法调用也算了进去（第 55 轮误报一次）。
    """
    src = _src()
    i_save = src.find("save_document")
    assert i_save > 0, "★ 找不到保存那一步"
    tail = src[i_save:]
    bad = re.findall(r"open_document,\s*sw,\s*str\(copy\)", tail)
    assert not bad, (
        "★ 保存之后重开又用了 str(copy) —— 沙箱会改名，"
        "读到的是另一个文件（第 55 轮实测）"
    )


def test_必须用_GetPathName_取实际路径() -> None:
    src = _src()
    i = src.find("save_document")
    assert i > 0
    #: 保存/重开附近必须出现 GetPathName
    seg = src[max(0, i - 600):i + 900]
    assert "GetPathName" in seg, (
        "★ 保存/重开附近没有 GetPathName() ⇒ 又会读到错的文件"
    )
    assert "real_path" in seg, "★ 没有把实际路径存下来复用"


def test_证据里记两个尺寸读数() -> None:
    """★ 没有这两个数，「重开不成立」只能靠猜。"""
    src = _src()
    for key in ("extent_before_save_mm", "extent_after_reopen_mm"):
        assert key in src, "★ 证据里缺 `%s`" % key


def test_实际路径写进证据() -> None:
    src = _src()
    assert '"real_path"' in src, "★ 证据里没记实际路径（下次排查又要猜读的是哪个文件）"
