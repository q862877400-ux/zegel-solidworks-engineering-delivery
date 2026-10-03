"""钉住 `sw_export.export_to_bmp` 的契约（不连 SolidWorks）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_sw_export_bmp_contract.py
# 定位:   轮 146 补 `export_image`（真缺档）⇒ 钉住三条**不依赖真机**的契约：
#         返回 `False` 要抛 · 扩展名守卫 · docstring 要写明来源与分工。
# 官方依据: `C:\\swapi\\types\\IModelDoc2\\SaveBMP.md`（Returns: True if created）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def _load():
    """取仓库里**真**的 `sw_export` 模块。

    ⚠ 第一版想"把 `sw_connect` 等全换成最小桩" ⇒ **追名字追不完**
    （`create_empty_dispatch_variant` / `import_com_dependencies` / `read_custom_property`…）。
    ⇒ ★ 改成**用真模块**（它们**导入时不连 COM**），只把 `get_com_member` 换成记录器。
    """
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import importlib
    if "sw_export" in sys.modules:
        del sys.modules["sw_export"]
    mod = importlib.import_module("sw_export")
    calls = []

    def rec(obj, name, *args):
        calls.append((name, args))
        return getattr(obj, "_ret", None)

    #: ★ 只替换这一个 —— `export_to_bmp` 是唯一用到它的地方
    mod.get_com_member = rec
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    mod.set_com_member = rec
    return mod, calls


class _Model:
    """假 `IModelDoc2`：`SaveBMP` 返回预先指定的值。"""

    def __init__(self, ret=True):
        self._ret = ret


def test_returns_false_raises():
    """@brief ★★ 官方返回 **`False`** ⇒ 必须**抛**（官方：True 才是写出来了）。"""
    mod, calls = _load()
    try:
        mod.export_to_bmp(_Model(False), r"D:\AI\SW\output\x.bmp", 10, 10)
    except RuntimeError as exc:
        assert "False" in str(exc) or "没写出" in str(exc), str(exc)
    else:
        raise AssertionError("返回 False 时**没有抛** —— 静默失败")


def test_passes_width_and_height_through():
    """@brief ★★ 宽高要**原样传下去**（那是定量往返的基础）。"""
    mod, calls = _load()
    mod.export_to_bmp(_Model(True), r"D:\AI\SW\output\x.bmp", 800, 600)
    assert calls[-1][0] == "SaveBMP", calls
    assert calls[-1][1] == (r"D:\AI\SW\output\x.bmp", 800, 600), calls[-1][1]


def test_rejects_non_bmp_extension():
    """@brief ★ 官方 Remarks 要求扩展名 `.bmp` ⇒ 别的扩展名要**明确拒绝**。"""
    mod, _ = _load()
    for bad in (".png", ".jpg", ""):
        try:
            mod.export_to_bmp(_Model(True), r"D:\AI\SW\output\x" + bad, 10, 10)
        except ValueError:
            continue
        raise AssertionError("扩展名 %r 没有被拒绝" % bad)


def test_docstring_pins_the_source_and_the_division_of_labour():
    """@brief ★★ docstring 要写明来源、返回值语义，与 `sw_capture` 的**分工**。"""
    mod, _ = _load()
    src = (REPO_ROOT / "scripts" / "sw_export.py").read_text(encoding="utf-8")
    i = src.index("def export_to_bmp(")
    #: ⚠ 判据窗口要**包含紧邻的来源块**（轮次标注在本仓的惯例是写在来源块里，
    #: 不是写在函数 docstring 里）⇒ 往前多取 2000 字。
    doc = src[max(0, i - 2000):i + 2200]
    assert "轮 146" in doc, "要标注实测轮次"
    assert "SaveBMP" in doc, "要点名官方成员"
    assert "sw_capture" in doc, "要写明与 sw_capture 的分工（GDI vs 原生）"
    assert "≤ 0" in doc or "<= 0" in doc, "要写明「宽高 ≤ 0 ⇒ 按窗口尺寸」这条官方 Remarks"
