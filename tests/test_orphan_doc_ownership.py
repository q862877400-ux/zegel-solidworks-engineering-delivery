"""★ 孤儿文档清理的**归属判据**（第 48 轮）。

## 为什么需要这个判据

`CloseAllDocuments(IncludeUnsaved=True)` 是**唯一**能关掉 `dirty` 文档的路
（`SetSaveFlag()` 按官方定义是「把文档**标脏**」，不能清脏 —— 事实族 561）。
但它**会连非我方文档一起关** ⇒ 调用前必须逐条核归属。

## 实测现场（第 48 轮）

E4 探针快跑了几轮，留下 3 个：

```
板1_rev-1.SLDPRT  type=1 dirty=False path=...\\output\\stage2\\...
装配体2            type=2 dirty=True  path=''
装配体3            type=2 dirty=True  path=''
```

- 有路径且 `dirty=False` 的，`CloseDoc` 能关
- **`dirty=True` 的关不掉**（`CommandInProgress=True` 下弹窗被抑制 ⇒ 关不动）

## 判据

| 情形 | 归属 |
|---|---|
| 路径在 `<仓库根>/output/` 下 | 我方（`output/` 已 gitignore） |
| 无路径且 `type==2`（装配体） | 我方（`new_document("assembly")` 建的） |
| 无路径且 `type==1`（零件） | **非我方**（可能是人手新建、还没存，碰不得） |
| 有路径但不在 `output/` 下 | **非我方** |

★ 最后两条刻意保守：**宁可拒绝清理，也不关别人的文档**。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import pytest  # noqa: E402

import close_my_orphans as cmo  # noqa: E402


def _info(**kw):
    base = {"title": "x", "type": 2, "dirty": True, "path": ""}
    base.update(kw)
    return base


def test_output_下算我方() -> None:
    i = _info(path=str(REPO / "output" / "stage2" / "板1.SLDPRT"), type=1, dirty=False)
    ok, why = cmo._mine(i)
    assert ok, "★ output/ 下的应算我方：%s" % why


def test_无路径装配体算我方() -> None:
    ok, why = cmo._mine(_info(type=2, path=""))
    assert ok, "★ 无路径装配体应算我方：%s" % why


def test_无路径零件不算我方() -> None:
    """★★ 保守：人手新建未保存的零件碰不得。"""
    ok, why = cmo._mine(_info(type=1, path=""))
    assert not ok, "★ 无路径零件不该被认成我方"
    assert "人工确认" in why


def test_不在_output_下的有路径文档不算我方() -> None:
    """★★ 保守：别人的真件碰不得（哪怕标题很像）。"""
    ok, why = cmo._mine(_info(path="D:/somewhere/板1.SLDPRT", type=1))
    assert not ok, "★ 非 output/ 路径不该被认成我方"
    assert "不在 output/" in why


def test_大小写不敏感() -> None:
    """★ Windows 路径大小写不敏感 —— 判据别在这上面漏。"""
    i = _info(path=str(REPO / "OUTPUT" / "x.SLDPRT").upper(), type=1)
    ok, _ = cmo._mine(i)
    assert ok, "★ 大写 OUTPUT 也应算我方"


def test_清理工具只走_CloseAllDocuments_带_IncludeUnsaved() -> None:
    """★★ 结构断言：必须带 `True`（含未保存），否则脏文档永远关不掉。"""
    src = (REPO / "tools" / "close_my_orphans.py").read_text(encoding="utf-8")
    i = src.find("CloseAllDocuments")
    assert i > 0, "★ 没调 CloseAllDocuments"
    seg = src[i:i + 80]
    assert "True" in seg, "★ CloseAllDocuments 没带 IncludeUnsaved=True：%r" % seg


def test_有非我方文档时不调_CloseAll() -> None:
    """★★ 结构断言：`bad` 非空时必须 return，不能走到 CloseAllDocuments。"""
    src = (REPO / "tools" / "close_my_orphans.py").read_text(encoding="utf-8")
    #: ★ 从 `def main()` 之后开始找 —— 模块文档串里也提到 CloseAllDocuments，
    #:   从文件头找会先命中文档串（第 48 轮实测：i_bad=3223 而 i_close=529）。
    body = src[src.find("def main()"):]
    i_bad = body.find("if bad:")
    #: ★ 用**调用形态**定位 —— 裸名字会命中 abort 消息里的
    #:   「不调 CloseAllDocuments」那句话（第 48 轮实测：seg 被截断在 ev["abort"] 那行）。
    i_close = body.find('get_com_member(sw, "CloseAllDocuments"')
    assert 0 < i_bad < i_close, "★ `if bad:` 必须在真正的 CloseAllDocuments 调用之前"
    seg = body[i_bad:i_close]
    assert "return 1" in seg, "★ `if bad:` 分支里没有提前返回 ⇒ 会走到 CloseAll 误关"


@pytest.mark.parametrize("ctype", [1, 2, 3])
def test_返回二元组且理由是字符串(ctype: int) -> None:
    ok, why = cmo._mine(_info(type=ctype, path=""))
    assert isinstance(ok, bool)
    assert isinstance(why, str) and why.strip(), "★ 理由不能为空（空理由等于没判）"
