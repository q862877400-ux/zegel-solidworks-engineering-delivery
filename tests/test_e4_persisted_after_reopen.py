"""E4 存盘重开 + `SaveAs` 参数个数：把第 63 轮的实测结论钉成回归测试。

## 为什么要有「数参数个数」这种测试

`IModelDocExtension.SaveAs` 是 **6 参**（`Name, Version, Options, ExportData,
out Errors, out Warnings`）。我第一版按 7 个写，得到的是

```
com_error (-2147352571, '类型不匹配。', None, 4)
```

—— ★ 错误只说「第 4 参不对」，**真因是实参个数错位**。
这种错静态看不出来、真机报错又指错位置 ⇒ 值得用 ast 数一遍实参个数钉住。

## 还测什么

- 采集器确实做了「存盘 → 关文档 → 重开 → **再数一次**配合」
  （只在内存里成立的配合没有价值）
- 验收报告确实把 `persisted` 带出来了（证据不能只躺在采集器里）
"""
from __future__ import annotations

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
COLLECTOR = REPO / "tools" / "collect_e4_standalone.py"
RUNNER = REPO / "tools" / "run_s3_acceptance.py"


def _saveas_calls(src: str) -> list:
    """找出所有把 `"SaveAs"` 当成员名传的调用，返回它们的实参个数。"""
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and arg.value == "SaveAs":
                #: 实参里含成员名字符串 + 之后的真参数
                out.append(len(node.args))
                break
    return out


def test_saveas_是六参() -> None:
    """★★ 官方签名 6 参。多传或少传都会得到「第 4 参类型不匹配」这种**误导性**错误。"""
    counts = _saveas_calls(COLLECTOR.read_text(encoding="utf-8"))
    assert counts, "★ 采集器里找不到 SaveAs 调用"
    #: 调用形态是 `get_com_member(fn, obj, "SaveAs", Name, Version, Options,
    #: ExportData, out_errors, out_warnings)`
    #: ⇒ 实参 = fn + obj + 成员名 + 官方 6 参 = **9**
    for n in counts:
        assert n == 9, (
            "★ `get_com_member(..., \"SaveAs\", <官方 6 参>)` 应有 9 个实参"
            "（fn + obj + 成员名 + 6）；实测 %d 个。"
            "多一个或少一个都会得到「第 4 参类型不匹配」这种**误导性**错误" % n
        )


def test_采集器做了存盘重开校验() -> None:
    src = COLLECTOR.read_text(encoding="utf-8")
    for token in ("SaveAs", "CloseDoc", "reopen_ok", "mates_after_reopen"):
        assert token in src, "★ 采集器缺存盘重开校验的一环：%s" % token
    #: 重开后必须**重新数**配合，不能复用存盘前的列表
    #: ★ 计数那行在**赋值之前**就调了一次汇总函数，所以窗口要往前看
    i = src.find('persisted["mates_after_reopen"]')
    assert i > 0, "★ 找不到重开后的配合计数赋值"
    seg = src[max(0, i - 700):i]
    assert "collect_mate_feature_summary" in seg, (
        "★ 重开后没有重新数配合 ⇒ 读数可能来自存盘前的内存状态"
    )


def test_报告带出持久化证据() -> None:
    src = RUNNER.read_text(encoding="utf-8")
    assert '"persisted"' in src, "★ 验收报告没把 persisted 带出来 ⇒ 证据只躺在采集器里"
    assert 'get("persisted")' in src or "steps" in src, "★ persisted 的取值路径不明确"


def test_存盘路径在产物区() -> None:
    """★ 产物必须落 `output/`（gitignore 的产物区），不能塞进仓库源码目录。"""
    src = COLLECTOR.read_text(encoding="utf-8")
    i = src.find("首件装配_rev-1.SLDASM")
    assert i > 0, "★ 找不到存盘文件名"
    seg = src[max(0, i - 200):i]
    assert '"output"' in seg, "★ 存盘路径不在 output/ 下"
