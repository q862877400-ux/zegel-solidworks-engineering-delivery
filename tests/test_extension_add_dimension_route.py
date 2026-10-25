"""★ `IModelDocExtension.AddDimension` 是本机唯一可用的建尺寸入口（第 52 轮）。

## 为什么这条必须钉住

事实 560 曾把「本机尺寸能力退化、E2 孔位联动没有可用机制」写进台账，
并据此让 E2.rebuild 一直挂着。事实 567 推翻了它：

```
before            0
select_Select2    {'ret': True, 'selected': 1}
call              {'ok': True, 'dim_none': False}   ← 返回真实 DisplayDimension
after             1                                  ← ★ 尺寸 0 → 1
```

★ 而 `IModelDoc2.AddDimension2` / `AddHorizontalDimension2` 会**连对照组都崩**
（RPC 服务器不可用），前后 4 次。

★★★ 关键机制：`Extension.AddDimension` 建完尺寸会弹 SolidWorks 的「修改」属性框
（控件树 `BUTTON×3 · SLIDER · THUMB WHEEL`，全是资源占位符 ⇒ 分级 `needs_llm`），
而且**方法本身同步阻塞** ⇒ 同一线程里看不到返回，
**必须从另一个进程按 ESC** 才能让调用返回。

★ 所以「崩」与「被模态框拖住」在 RPC 错误码上长得一样 ——
  区分办法是看有没有那个占位符控件树（`SLIDER` / `THUMB WHEEL` 是数值框的特征）。

## 本文件钉什么

① 探针用的是 `Extension.AddDimension`（不是那两个会崩的入口）
② 探针**先证明选得中**（用 `Select2`，`Select4` 实测失败）
③ 选中数为 0 时**不调** AddDimension（设置无效时的读数不算结论）
④ 探针在冒险那一句**之前**就落盘证据（进程被杀也能留证）
⑤ 事实里记了这条，且标注了它推翻什么
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

_PROBE = REPO / "tools" / "probe_extension_add_dimension.py"
_FACTS = REPO / "docs" / "known-facts.md"


def _src() -> str:
    return _PROBE.read_text(encoding="utf-8")


def test_用的是_Extension_AddDimension() -> None:
    """★★ 核心：这是本机唯一可用的入口。"""
    src = _src()
    assert "Extension" in src and "AddDimension" in src
    assert '"AddDimension"' in src, "★ 没真的调 `AddDimension`"


def test_不许调那两个会崩的入口() -> None:
    """★★★ `IModelDoc2.AddDimension2` / `AddHorizontalDimension2` 崩过 4 次，不能再撞。"""
    src = _src()
    #: ★ 只查**调用形态**（引号包起来当成员名用）——
    #:   文档串里解释「不要用它」不算违规（第 52 轮实测踩过这个误报）。
    for bad in ("AddDimension2", "AddHorizontalDimension2", "AddVerticalDimension2"):
        assert ('"%s"' % bad) not in src, (
            "★ 探针里真的调了 `%s` —— 那个入口会崩进程（事实 560）" % bad
        )


def test_先证明选得中再调用() -> None:
    """★★ 第 52 轮实测：`selected=0` 就调的话，读数没有意义（设置无效）。"""
    src = _src()
    i = src.find("if picked < 1:")
    j = src.find('"AddDimension"')
    assert i > 0, "★ 没有「选中数为 0 就不调」的保护"
    assert i < j, "★ 保护在调用之后 ⇒ 等于没保护"


def test_用_Select2_而不是只靠_Select4() -> None:
    """★ 实测 `IEntity.Select4` 对草图段失败（com_error），`Select2` 成功。"""
    src = _src()
    assert "Select2" in src, "★ 没有用 `Select2`（实测唯一选得中的那个）"


def test_冒险前先落盘() -> None:
    """★ 第 43 轮教训：进程被杀时 finally 不执行。"""
    src = _src()
    i = src.find("about_to_call")
    j = src.find('"AddDimension"')
    assert 0 < i < j, "★ 证据落盘不在调用之前"
    assert "_save(ev)" in src


def test_事实记了这条并标注推翻() -> None:
    t = _FACTS.read_text(encoding="utf-8")
    assert "AddDimension" in t and "Extension" in t, "★ 事实里没记 Extension.AddDimension"
    assert "推翻" in t, "★ 没标注它推翻了事实 560 的「没有可用机制」"


def test_事实记了修改框阻塞与_ESC_手法() -> None:
    """★★ 不知道这条的人会把「阻塞」当成「API 崩」，然后放弃整条路。"""
    t = _FACTS.read_text(encoding="utf-8")
    assert "ESC" in t, "★ 事实里没记「必须另一个进程按 ESC」这个手法"
    assert "SLIDER" in t or "修改" in t, "★ 事实里没记那个修改框的特征"
