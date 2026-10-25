"""docstring 的参数块必须与签名对得上 —— 本轮错误的**第三个根因**的回归测试。

## 那件事

`add_component` 的形参早改名成 `x_m, y_m, z_m`，而 docstring 还写：

```
x, y, z: 放置位置（米）
```

⇒ 我读文档，以为「就是个位置」，**从没意识到还有轴方向** ⇒ 把 +Z 说成「抬高」，
   业主从屏幕上看出两块**一样高**。

★★ 这类 bug 特别坏：代码能跑、ruff 不管、**而人是靠文档理解参数的**。
   ⇒ 文档骗人比代码写错更隐蔽，值得一道门禁。

## 这些测试钉什么

① 一行多个名字（`cx, cy: …`）要能解析 —— 第一版只取第一个，产生误报
② 声明了签名里没有的名字 ⇒ 报
③ 签名里有、文档没写 ⇒ 报
④ **`add_component` 的 `x_m/y_m/z_m` 必须都在文档里**（本轮的直接回归）
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO))

import check_docstrings_match_signatures as G  # noqa: E402


def test_一行多个名字能解析() -> None:
    """★ 第一版只取第一个名字 ⇒ `sketch_arc` 等被误报。误报会让门禁被关掉。"""
    doc = """
    参数:
        cx, cy: 圆心坐标（毫米）
        radius: 半径（毫米）

    返回:
        int
    """
    names = G._declared_params(doc)
    assert names[:3] == ["cx", "cy", "radius"], names


def test_英文Args块也能解析() -> None:
    doc = """
    Args:
        path: 文件路径
        mode: 模式
    Returns:
        bool
    """
    assert G._declared_params(doc)[:2] == ["path", "mode"]


def test_没有参数块返回空() -> None:
    assert G._declared_params("只有一句话。") == []


def test_声明了签名里没有的名字会报() -> None:
    violations, _files = G.scan()
    #: ★ 当前基线里不允许出现「文档写了不存在的形参」这类**假文档**
    bogus = [v for v in violations if v["missing_in_sig"]]
    assert bogus == [], (
        "★ 这些 docstring 声明了签名里不存在的参数（假文档）：%s"
        % [(v["target"], v["missing_in_sig"]) for v in bogus]
    )


def test_add_component_三个轴都写进了文档() -> None:
    """★★★ 本轮错误的直接回归。

    `x_m/y_m/z_m` 三个形参都必须出现在文档的参数块里 ——
    上一版写的是过时的 `x, y, z`，正是我误判的入口。
    """
    violations, _files = G.scan()
    hit = [v for v in violations if v["target"].endswith("sw_assembly.py::add_component")]
    assert hit == [], "★ add_component 的文档与签名不一致：%s" % hit

    src = (REPO / "scripts" / "sw_assembly.py").read_text(encoding="utf-8")
    i = src.find("def add_component(")
    seg = src[i:i + 1800]
    for name in ("x_m", "y_m", "z_m"):
        assert name in seg, "★ 文档里没写 `%s`" % name
    #: ★ 轴方向必须写出来（「抬高」= Y），否则下一个人还会犯同样的错
    assert "上下" in seg and "深度" in seg, (
        "★ 文档没说明 Y 是上下、Z 是深度 ⇒ 还会有人把 +Z 当抬高"
    )


def test_门禁整体有上界() -> None:
    """★ 棘轮存在：基线文件在，且是个整数。"""
    import json

    p = REPO / "docs" / "docstring-params-baseline.json"
    assert p.is_file(), "★ 缺基线 ⇒ 棘轮没有起点"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert isinstance(data.get("ceiling"), int)
