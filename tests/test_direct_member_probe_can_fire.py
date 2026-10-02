"""★★★ 证明「直接属性访问」探针**能抓到** —— 不许是个永远返回 0 的检查。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_direct_member_probe_can_fire.py
# 定位:   2026-10-01（轮 160）探针升到**第三版**后扫出 **0 处** ——
#         ⚠⚠ **一个永远返回 0 的检查等于没有检查**（事实 62 / 79 / 88 那一族）。
#         ⇒ 本文件给探针**喂合成的负例**，证明它**真的会响**。
# 官方依据: 不适用（本项目内部纪律 + 出厂反射 `D:\\AI\\SW\\_raw\\**\\iface_*.txt`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools" / "probe_direct_member_access.py"


def _load_probe():
    spec = importlib.util.spec_from_file_location("probe_dma", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _scan(src: str, tmp_path: Path):
    """把源码写进临时文件，让探针扫它。"""
    p = Path(str(tmp_path)) / "synthetic.py"
    p.write_text(src, encoding="utf-8")
    mod = _load_probe()
    known = mod.members_from_reflection()
    assert known, "反射读不到 ⇒ 判据无法判，测试应显式失败"
    return mod._scan_file(p, known)


def test_it_fires_on_the_real_defect(tmp_path):
    """@brief ★★★ **喂 077 那个真缺陷的同形代码** ⇒ 探针必须命中。"""
    src = (
        "def export_to_pdf(model, output_path):\n"
        "    holder = get_com_member(model, 'Extension')\n"   #: 让 `model` 成为「被当 COM 对象用过」
        "    sw = model.GetSldWorksObject()\n"                #: ★ 真缺陷的形态
        "    return sw\n"
    )
    hits = _scan(src, tmp_path)
    names = [h["name"] for h in hits]
    assert "GetSldWorksObject" in names, (
        "探针**没抓到** `model.GetSldWorksObject()` ⇒ 它是个不会响的检查（事实 62）")


def test_it_fires_on_the_interference_defect(tmp_path):
    """@brief ★★★ 喂 159 那个真缺陷的同形代码 ⇒ 也要命中。"""
    src = (
        "def f(asm_model):\n"
        "    hook = get_com_member(asm_model, 'Extension')\n"
        "    it = asm_model.InterferenceDetectionManager\n"
        "    return it.GetInterference(0)\n"                 #: ★ 官方只有**复数**
    )
    hits = _scan(src, tmp_path)
    assert "GetInterference" in [h["name"] for h in hits], (
        "探针没抓到单数 `GetInterference`")


def test_it_does_not_fire_on_python_objects(tmp_path):
    """@brief ★★ **反面**：普通 Python 对象上的大驼峰调用**不许**报（第一版就栽在这）。"""
    src = (
        "import argparse, winreg\n"
        "def f(parser, key):\n"
        "    parser.add_argument('x') if False else None\n"
        "    a = argparse.ArgumentParser()\n"
        "    b = winreg.OpenKey(key, 'x')\n"
        "    return a, b\n"
    )
    hits = _scan(src, tmp_path)
    assert not hits, "普通 Python 对象被误报了：%r" % (hits,)


def test_it_does_not_fire_on_docstrings(tmp_path):
    """@brief ★★ **反面**：docstring/注释里提到坏名字**不许**报（本会话栽过 5 次）。"""
    src = (
        "def f(model):\n"
        '    """说明：以前这里写的是 `model.GetSldWorksObject()`，是个不存在的成员。"""\n'
        "    hook = get_com_member(model, 'Extension')\n"
        "    return hook\n"
    )
    hits = _scan(src, tmp_path)
    assert not hits, "docstring 里的举例被误报了：%r" % (hits,)


def test_it_does_not_fire_for_com_infrastructure(tmp_path):
    """@brief ★★ **反面**：`QueryInterface` 是 COM 基础设施（IUnknown），不许报。"""
    src = (
        "def f(doc):\n"
        "    hook = get_com_member(doc, 'Extension')\n"
        "    return doc.QueryInterface('x')\n"
    )
    assert not _scan(src, tmp_path), "COM 基础设施被误报了"


def test_scope_is_per_function(tmp_path):
    """@brief ★★★ **反面**：**别的函数**里把同名变量当 COM 用，**不该牵连本函数**（事实 51）。"""
    src = (
        "def g(thing):\n"
        "    hook = get_com_member(thing, 'Extension')\n"     #: 这里 `thing` 是 COM
        "    return thing\n"
        "\n"
        "def h(thing):\n"
        "    return thing.IsDone()\n"                          #: ★ 这里的 `thing` 是 OCP 对象
    )
    hits = _scan(src, tmp_path)
    assert not hits, (
        "跨函数同名变量被牵连了（**事实 51**：分析范围要贴合组织单元）：%r" % (hits,))
