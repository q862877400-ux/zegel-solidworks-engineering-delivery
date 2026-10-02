"""钉住 `sw_export.export_to_image` 的契约（不连 SolidWorks）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_sw_export_image_contract.py
# 定位:   轮 147 收掉轮 146 标下的边界（`SaveBMP` 只出 `.bmp`）。
#         ⚠ 本函数在真机上踩过**两个坑**，都要钉住：
#           ① 反射里那个 **3 参** `SaveAs3` 重载在 pywin32 下报
#              `DISP_E_PARAMNOTOPTIONAL` ⇒ **必须按 7 参调**（末两个 `out Int32`）；
#           ② `ExportData` / `AdvancedSaveAsOptions` 传 `None` 报 **`类型不匹配`**
#              ⇒ 必须用 `create_empty_dispatch_variant()`（事实 12 / 33）。
# 官方依据: `C:\\swapi\\types\\IModelDocExtension\\SaveAs3.md`（三级废弃链：SaveAs ⇒ SaveAs2 ⇒ SaveAs3）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def _load():
    import importlib
    if "sw_export" in sys.modules:
        del sys.modules["sw_export"]
    mod = importlib.import_module("sw_export")
    calls = []

    def rec(obj, name, *args):
        calls.append((name, args))
        return getattr(obj, "_ret", True)

    mod.get_com_member = rec
    mod.out_i4 = lambda v=0: ("OUT", v)
    mod.create_empty_dispatch_variant = lambda: "EMPTY"
    return mod, calls


def _real_png(tmp_path):
    """造一个**真的、非空**的 `.png`（只为过「文件在且非空」那一关）。"""
    p = Path(str(tmp_path)) / "x.png"
    p.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
    return p


class _Ext:
    def __init__(self, ret):
        self._ret = ret


class _Model:
    def __init__(self, ret=True):
        self._ret = ret
        self.Extension = _Ext(ret)


def test_calls_the_seven_arg_form(tmp_path):
    """@brief ★★ 必须按**7 参**调 `SaveAs3`（3 参那个在 pywin32 下到不了）。

    ⚠ 实测：3 参形式报 `0x8002000F`（`DISP_E_PARAMNOTOPTIONAL`）⇒ 解析到的是 7 参那个。
    """
    mod, calls = _load()
    mod.export_to_image(_Model(True), str(_real_png(tmp_path)))
    name, args = calls[-1]
    assert name == "SaveAs3", calls
    assert len(args) == 7, "要传 7 个实参，实际 %d：%r" % (len(args), args)
    assert args[0].endswith(".png"), args[0]


def test_empty_dispatch_variants_for_the_object_params(tmp_path):
    """@brief ★★ 第 5/6 个实参（两个 `Object`）必须是**空 Dispatch**，不能是 `None`。

    ⚠ 实测传 `None` 报 `类型不匹配`（位置 4）—— 事实 12 / 33 那一族。
    """
    mod, calls = _load()
    mod.export_to_image(_Model(True), str(_real_png(tmp_path)))
    _name, args = calls[-1]
    #: ⚠ 下标要对：0=路径 1=Version 2=Options **3=ExportData 4=AdvancedSaveAsOptions**
    #: 5/6=两个 `out Int32`（出参占位）。**第一版我把 3/4 写成了 4/5** ⇒ 断言错。
    assert args[3] != None and args[4] != None, "两个 Object 入参不能是 None"  # noqa: E711
    assert args[3] == "EMPTY" and args[4] == "EMPTY", args[3:5]
    assert args[5] == ("OUT", 0) and args[6] == ("OUT", 0), args[5:7]


def test_false_raises():
    """@brief ★ 官方（7 参）返回 `False` ⇒ 必须**抛**。"""
    mod, _ = _load()
    try:
        mod.export_to_image(_Model(False), r"D:\AI\SW\output\x.png")
    except RuntimeError:
        return
    raise AssertionError("返回 False 时没有抛")


def test_missing_file_after_success_raises(tmp_path=None):
    """@brief ★★ 返回成功但**文件不在** ⇒ 也要抛（「0 不代表成功」那条纪律）。"""
    mod, _ = _load()
    #: 让 get_com_member 返回 True，但目标路径确实不存在
    try:
        mod.export_to_image(_Model(True), r"D:\AI\SW\output\definitely-not-here-147.png")
    except RuntimeError as exc:
        assert "文件不在" in str(exc) or "为空" in str(exc), str(exc)
        return
    raise AssertionError("返回成功但文件不存在 ⇒ 没有抛")


def test_rejects_other_extensions():
    """@brief ★ 只接受 `.png` / `.jpg` / `.jpeg`。"""
    mod, _ = _load()
    for bad in (".bmp", ".tif", ".pdf", ""):
        try:
            mod.export_to_image(_Model(True), r"D:\AI\SW\output\x" + bad)
        except ValueError:
            continue
        raise AssertionError("扩展名 %r 没有被拒绝" % bad)


def test_docstring_pins_the_two_traps():
    """@brief ★★ docstring 要写明**两个坑**（3 参到不了 + 空 Dispatch）。"""
    src = (REPO_ROOT / "scripts" / "sw_export.py").read_text(encoding="utf-8")
    i = src.index("def export_to_image(")
    doc = src[max(0, i - 2600):i + 2400]
    assert "三级废弃链" in doc, "要写明三级废弃链（SaveAs ⇒ SaveAs2 ⇒ SaveAs3）"
    assert "DISP_E_PARAMNOTOPTIONAL" in doc, "要写明 3 参那个到不了"
    assert "create_empty_dispatch_variant" in doc, "要写明两个 Object 入参要空 Dispatch"
    assert "轮 147" in doc, "要标注实测轮次"


def test_out_i4_is_reachable_at_module_scope():
    """★★ **轮 403 真机抓到的真 bug 的锁**：`export_to_image` 里用了 `out_i4()`，
    ★ 而 `sw_export.py` **漏了导入它** ⇒ 一调就 `NameError: name 'out_i4' is not defined`。

    ★★ **本文件原来那些测试为什么抓不到**（★ 机制性的原因，不是疏忽）：
    ★ 它们走 `_load()`，而那个帮手会**把替身直接赋到模块上**
    （`mod.out_i4 = lambda…` · `mod.get_com_member = rec`）⇒
    ★★ **替身注入恰好把「真实导入缺失」这件事掩盖了** —— ★ 于是"全绿"。
    ⇒ ★ 所以本条测试**故意绕开 `_load()`**：★ 用 `importlib` 拿**干净**的模块，
    ★ 只问一件事：★ **真实模块里到底有没有 `out_i4`**。
    ★★ 教训：**「契约测试全绿」≠「函数能跑」** —— ★ 替身注入既能让测试不依赖 COM，
    ★ 也能**顺手掩盖导入缺失**；★ 两者要分开测。
    """
    import importlib
    import inspect as _inspect
    if "sw_export" in sys.modules:
        del sys.modules["sw_export"]
    mod = importlib.import_module("sw_export")          #: ★ 干净加载（★ 不注入任何替身）
    src = _inspect.getsource(mod)
    if "out_i4(" in src:
        assert hasattr(mod, "out_i4"), (
            "★ export_to_image 用了 out_i4() 而模块里拿不到它 ⇒ 一调就 NameError")
