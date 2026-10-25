"""★ 清理代码写了 ≠ 清理执行过（第 50 轮，用户当场指出）。

## 现场

用户：「你每次开一个新窗口，里面两个板子都离得特别远」。
一查 SolidWorks 里开了 **7 个**文档：1 个零件 + **6 个未保存装配**（装配体8…13）。

而探针的 `finally` **本来就写了关文档**：

```python
for d in list(sw.GetDocuments() or []):   # ← 这一行抛 TypeError
    _try(sw.CloseDoc, ...)
```

本机 `ISldWorks.GetDocuments` 是**属性**不是方法 ⇒ `sw.GetDocuments()` 抛
`TypeError: 'tuple' object is not callable` ⇒ **`finally` 一开头就炸**，后面一句没执行。

★★ 这是「返回值 ≠ 实际结果」的变体：**清理代码写了 ≠ 清理执行过**。
   更坏：它**从不报错给人看**（异常被外层吞掉），表现只是「窗口越堆越多」。

## 本文件钉什么

① 探针的收尾**不许**用 `sw.GetDocuments()`（带括号）
② 收尾必须**回读计数**并写进证据（`docs_left`）
③ 收尾仍 >0 时要有兜底（`CloseAllDocuments`）
④ 收尾段**不许裸露调用**（逐段 `try`），否则又会静默失效
⑤ 仓库里**所有**探针都不许出现 `sw.GetDocuments()`（一次都不许）
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

_PROBE = REPO / "tools" / "probe_e4_assembly.py"


def _src() -> str:
    return _PROBE.read_text(encoding="utf-8")


def _code_lines(text: str) -> list:
    """★ 只保留**代码部分**（去掉 `#` 之后的注释）—— 注释里引用 API 不算违规。"""
    out = []
    for line in text.splitlines():
        code = line.split("#", 1)[0]
        if code.strip():
            out.append(code)
    return out


def test_探针收尾不用_GetDocuments_带括号() -> None:
    """★★ 核心：本机它是属性，带括号就 TypeError。"""
    bad = [
        ln
        for ln in _code_lines(_src())
        if re.search(r"\.GetDocuments\s*\(\s*\)", ln)
    ]
    assert not bad, (
        "★ 探针里仍有 `.GetDocuments()`（本机是属性，会 TypeError）：%r" % (bad[:3],)
    )


def test_收尾回读计数并写进证据() -> None:
    src = _src()
    i = src.find("finally:")
    assert i > 0, "★ 找不到 finally"
    seg = src[i:]
    assert "docs_left" in seg, "★ 收尾没有回读 `docs_left`"
    assert "open_doc_count" in seg, "★ 收尾没有真正回读计数"


def test_收尾有兜底清除() -> None:
    src = _src()
    i = src.find("finally:")
    seg = src[i:]
    assert "CloseAllDocuments" in seg, (
        "★ 收尾没有兜底 `CloseAllDocuments` ⇒ 脏文档关不掉时会继续堆"
    )


def test_收尾不许裸调用() -> None:
    """★ 收尾里每段都要 `try` —— 否则一处异常就把后面的清理全废掉。"""
    src = _src()
    i = src.find("finally:")
    seg = src[i:]
    assert seg.count("try:") >= 2, (
        "★ 收尾段的 try 太少（实测一次 TypeError 就让整段清理失效）"
    )


def test_仓库所有探针都不许带括号调用() -> None:
    """★★ 这条是**全仓扫描**：同类写法不该在别的探针里再出现。"""
    #: ★ 排除 `diag_getdocuments.py` —— 它**就是**用来诊断这个坑的
    #:   （`_show("sw.GetDocuments()", lambda: sw.GetDocuments())` 是故意写的）。
    offenders = []
    for p in (REPO / "tools").glob("*.py"):
        if p.name == "diag_getdocuments.py":
            continue
        for ln in _code_lines(p.read_text(encoding="utf-8", errors="replace")):
            if re.search(r"\.GetDocuments\s*\(\s*\)", ln):
                offenders.append(p.name)
                break
    assert offenders == [], (
        "★ 这些文件里还有 `.GetDocuments()`（属性被当方法调）：%r" % (offenders,)
    )
