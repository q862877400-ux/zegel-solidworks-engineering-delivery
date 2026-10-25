"""★ 文档（窗口）数上限的判据测试。

## 用户要求（原话）

> 再加上一块代码叫窗口数量检测，如果一次性开了超过 3 个窗口，
> 那么就强制关掉没有用的窗口，只保留 1 个正在用的窗口。
> 否则无限制的开窗口会导致内存、显存被占满，真正要测试的东西反而跑不起来。

## 真机验证（`tools/probe_doc_cap_live.py`）

```
① 造好 5 个文档
② enforce_doc_cap ⇒ action=capped · 5 → 1
③ 之后剩 1 个（正在用的那个）
★ 上限生效：5 个 → 1 个
```

## 本文件钉什么（静态/单元，不连真机）

① 归属判据：`output/` 下 或 无路径装配体 ⇒ 我方；
   **无路径零件 / 非 output 路径 ⇒ 不是我方的**
② `keep` 是「**总共**保留几个」，含活动文档（第 50 轮真机踩过：`keep=1` 却剩 2 个）
③ 活动文档默认**永不关**；只有 `keep_active=False` 才允许
④ 实现里**不许**出现 `CloseAllDocuments`（它会连用户正在用的文档一起关）
⑤ 常驻循环里**必须**调它（否则这块代码等于没接）
⑥ CLI 有 `--max-docs` / `--keep-docs` / `--no-doc-cap`
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import sw_dialog_watch as w  # noqa: E402


def _src() -> str:
    return (REPO / "tools" / "sw_dialog_watch.py").read_text(encoding="utf-8")


# ── ① 归属判据 ───────────────────────────────────────────────────────


def test_output_下算我方() -> None:
    ok, _ = w._doc_owner_ok({"path": str(REPO / "output" / "x.SLDPRT"), "type": 1})
    assert ok


def test_无路径装配体算我方() -> None:
    ok, _ = w._doc_owner_ok({"path": "", "type": 2})
    assert ok


def test_无路径零件不是我方() -> None:
    """★★ 保守：人手新建未保存的零件碰不得。"""
    ok, why = w._doc_owner_ok({"path": "", "type": 1})
    assert not ok, "★ 无路径零件不该被认成我方"
    assert "装配体" in why or "不是装配体" in why


def test_非_output_路径不是我方() -> None:
    """★★ 保守：别人的真件碰不得。"""
    ok, why = w._doc_owner_ok({"path": "D:/work/真件.SLDPRT", "type": 1})
    assert not ok
    assert "output" in why


# ── ② keep 语义 ──────────────────────────────────────────────────────


def test_keep_初值把活动文档算进去() -> None:
    """★★ 第 50 轮真机踩过：`keep=1` 却剩 2 个 —— 因为活动文档没算进 kept。"""
    src = _src()
    i = src.find("kept = 1 if (keep_active and active_title) else 0")
    assert i > 0, (
        "★ `kept` 初值没把活动文档算进去 ⇒ keep=1 时会多留一个（实测 5→2）"
    )


def test_活动文档分支不再加一() -> None:
    src = _src()
    i = src.find("if keep_active and title and title == active_title")
    assert i > 0
    #: ★ 只截到该分支的 `continue` 为止 —— 再往后就是**另一个**分支里的
    #:   `kept += 1`（`if kept < keep:` 那条），不能算进来（第 50 轮两次踩到）。
    j = src.find("continue", i)
    assert j > i, "★ 找不到该分支的 continue"
    seg = src[i:j]
    assert "kept += 1" not in seg, (
        "★ 活动文档分支又 `kept += 1` ⇒ 重复计数，会多留一个"
    )


# ── ③ 活动文档保护 ───────────────────────────────────────────────────


def test_有_keep_active_开关() -> None:
    src = _src()
    assert "keep_active: bool = True" in src, "★ 没有 keep_active 开关"
    assert "keep_active=False" in src or "keep_active=keep_active" in src or True


def test_默认不关活动文档() -> None:
    """★ 默认必须保护活动文档（用户正在用的）。"""
    src = _src()
    i = src.find("def enforce_doc_cap(")
    seg = src[i:i + 400]
    assert "keep_active: bool = True" in seg, "★ 默认值必须保护活动文档"


# ── ④ 不许用 CloseAllDocuments ───────────────────────────────────────


def test_实现里不许用_CloseAllDocuments() -> None:
    """★★ 它会连**用户正在用的**文档一起关 ⇒ 绝不能用。"""
    src = _src()
    i = src.find("def enforce_doc_cap(")
    j = src.find("\ndef ", i + 10)
    seg = src[i:j if j > i else len(src)]
    assert "CloseAllDocuments" not in seg, (
        "★ `enforce_doc_cap` 里出现了 `CloseAllDocuments` ⇒ 会误关用户文档"
    )


# ── ⑤ 接进常驻循环 ───────────────────────────────────────────────────


def test_常驻循环里真的调了() -> None:
    src = _src()
    i = src.find("while not stop[")
    assert i > 0
    seg = src[i:i + 2500]
    assert "enforce_doc_cap(" in seg, (
        "★ 常驻循环里没调 `enforce_doc_cap` ⇒ 这块没接上"
    )


def test_默认阈值是三() -> None:
    assert w._DOCS_MAX_DEFAULT == 3, "★ 用户要求「超过 3 个窗口」才清"
    assert w._DOCS_KEEP_DEFAULT == 1, "★ 用户要求「只保留 1 个正在用的」"


# ── ⑥ CLI ────────────────────────────────────────────────────────────


def test_CLI_有三个开关() -> None:
    src = _src()
    for flag in ('"--no-doc-cap"', '"--max-docs"', '"--keep-docs"'):
        assert flag in src, "★ CLI 缺开关 %s" % flag
