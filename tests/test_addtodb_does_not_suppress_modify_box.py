"""★ `SetAddToDB(True)` **不能**省掉「修改」属性框（第 53 轮排除）。

## 为什么要钉

第 52 轮发现 `IModelDocExtension.AddDimension` 可用，但它建完尺寸会弹 SolidWorks 的
「修改」属性框并**同步阻塞** ⇒ 必须另一个进程按 ESC。

第 53 轮试了官方看起来最对症的手段 —— `IModelDoc2.SetAddToDB(True)`：

> 官方 Remarks 逐字：benefits of adding sketch entities directly to the database is that you can
> **avoid grid and entity snapping** … After setting `SetAddToDB` to True, you must set it back
> to false to restore SOLIDWORKS to its normal operating mode.

**实测（真机）**：

```
12 秒时仍未返回 ⇒ ★ 需要 ESC ⇒ 仍然被框住（hwnd=2707436）
② 返回 ok=True dim=False · 尺寸 0 → 1
```

⇒ `SetAddToDB(True)` **没有**省掉那个框：调用照样阻塞、照样要外部 ESC，
   尺寸照样建成（0 → 1）。

★★ 这条的价值：**下一个接手的人必然会想到「用 AddToDB 免弹框」这个主意**，
   钉在这里省他一次真机试错。

## 本文件钉什么

① 探针里保留了 `--addtodb` 开关（可复现，不是一次性脚本）
② 收尾必须把 `SetAddToDB` **设回 False**（官方逐字要求，否则 SolidWorks 停在非正常模式）
③ 文档里记了「它不能免弹框」这个结论
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

_PROBE = REPO / "tools" / "probe_extension_add_dimension.py"
_T008 = REPO / "specs" / "350-first-part-delivery" / "s3-t008-dimension-driven.md"


def _src() -> str:
    return _PROBE.read_text(encoding="utf-8")


def test_探针保留了_addtodb_开关() -> None:
    """★ 可复现：不是一次性脚本。"""
    src = _src()
    assert '"--addtodb"' in src, "★ 没有 `--addtodb` 开关 ⇒ 这条排除无法复现"
    assert "SetAddToDB" in src


def test_必须把_AddToDB_设回_False() -> None:
    """★★ 官方逐字：`you must set it back to false to restore SOLIDWORKS to its normal operating mode`。"""
    src = _src()
    i = src.find("SetAddToDB")
    assert i > 0
    tail = src[i:]
    assert 'SetAddToDB", False' in tail, (
        "★ 没有把 SetAddToDB 设回 False ⇒ SolidWorks 会停在非正常模式"
    )


def test_文档记了它不能免弹框() -> None:
    """★★ 下一个接手的人一定会想到这个主意 —— 钉住省他一次试错。"""
    t = _T008.read_text(encoding="utf-8")
    assert "SetAddToDB" in t, "★ T008 文档里没记这条排除"
    assert "不能" in t or "没有" in t, "★ 没写清「它不能省掉那个框」"


def test_文档记了勘察到的结构() -> None:
    """★ 结构是下一步动手的依据，必须可查。"""
    t = _T008.read_text(encoding="utf-8")
    for key in ("M6 间隙孔", "草图1", "100", "20.0"):
        assert key in t, "★ T008 文档缺结构事实：%s" % key


def test_文档没有把_fail_写成_pass() -> None:
    """★★ 现状仍是 fail，不许在文档里悄悄升级。"""
    t = _T008.read_text(encoding="utf-8")
    i = t.find("## 十、第 53 轮勘察")
    assert i > 0
    seg = t[i:]
    assert "仍是 **fail**" in seg or "仍是 fail" in seg, (
        "★ 勘察节必须写明 E2.rebuild 现状仍是 fail"
    )
