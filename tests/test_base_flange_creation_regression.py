"""★ spec 262：**造钣金件失败** —— `create_base_flange` 本机建不出来（★ 与 261 无关，已静态排除）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   tests/solidworks_sheet_metal_regression.py（★ 仓里**维护好的**造件配方 —— 它也失败）
#         scripts/sw_sheet_metal.py::create_base_flange（★ 失败点：`CreateFeature` 回 None）
#         docs/known-facts.md 事实 34（★ **2026-10-01 记它成功**）⇒ ★ 这是**回归**
#         specs/261-routing-batch1-adapt-args/（★ 261 只改了**读**路径 —— 本文件要**静态排除**它）
# 定位:   ★ 261 的未过门 1「`_read_k_factor` 未被真机走到」⇒ ★ 本文件查**为什么造不出件**。
# 官方依据: SW rev **34.4.1** 真机（走 `tools/sw_guard.py`）
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读 `scripts/`；★ 真机部分由**仓里维护的**回归脚本跑
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★★ **真机读数**（`tests/solidworks_sheet_metal_regression.py` · SW rev **34.4.1**）：
#:   ★ 该脚本是**仓里维护的**配方（mtime `10-03 07:17`）⇒ ★ **它也失败** ⇒ ★ 不是探针写错。
MACHINE = {
    "status": "failed",
    "error": "CreateFeature(IBaseFlangeFeatureData) 创建失败",
    "script": "tests/solidworks_sheet_metal_regression.py",
    "known_fact_34": "2026-10-01 记 `create_base_flange` **成功**（特征树出现「基体-法兰1」）",
    "regression": True,
}

#: ★★ `create_base_flange` 里**写** K 因子的那一行（★ 261 **没有**碰它）。
WRITE_PATH = 'bend_allowance.KFactor = float(spec.k_factor)'
#: ★ 261 改的是**读**路径（★ 在 `sheet_metal_evidence` 里）。
READ_PATH_OLD = 'float(get_com_member(definition, "KFactor") or 0.0)'


def _create_flange_body() -> str:
    """★ 取 `create_base_flange` 的函数体源码（★ 按名字定位）。"""
    src = (SCRIPTS / "sw_sheet_metal.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "create_base_flange":
            return ast.get_source_segment(src, node) or ""
    return ""


def _failures(m: dict, body: str) -> list[str]:
    """★ 纯函数：① 失败要如实记；② ★ 261 **没有**碰 `create_base_flange`。"""
    out: list[str] = []
    if m["status"] != "failed":
        out.append("真机状态变了（%r）⇒ 请复核本文件的结论" % m["status"])
    if "CreateFeature" not in m["error"]:
        out.append("失败点变了（%r）⇒ 请复核" % m["error"])
    #: ★★ 261 的「读」路径改动**不该**出现在 `create_base_flange` 里。
    if READ_PATH_OLD in body:
        out.append("`create_base_flange` 里出现了 261 换掉的**旧读法** ⇒ 复核")
    if "_read_k_factor" in body:
        out.append("`create_base_flange` 里出现了 `_read_k_factor` ⇒ 261 确实碰了它 ⇒ **结论要改**")
    #: ★ 它的**写**路径必须在（★ 那是它自己的事，★ 261 没动）。
    if WRITE_PATH not in body:
        out.append("`create_base_flange` 里找不到写 K 因子的那行 ⇒ 函数被改过了")
    return out


# ── ① ★★★ 真机失败必须如实记录（★ 且是**回归**）──────────────────────
def test_machine_failure_is_recorded():
    """★★★ 本机 `create_base_flange` **建不出特征** —— ★ 且仓里**维护好的**回归脚本**也失败**。

    ★★ **为什么单独立一条**：★ 事实 34（2026-10-01）记它**成功** ⇒ ★ 这是**回归**；
    ★ 不记下来 ⇒ ★ 下一个人会以为「只是夹具零件没有 `BaseFlange`」，★ 而**真相是造不出来**。
    """
    bad = _failures(MACHINE, _create_flange_body())
    assert not bad, "记录不合格：\n" + "\n".join("  " + b for b in bad)
    assert MACHINE["regression"] is True, "必须如实标为**回归**（★ 事实 34 记过成功）"


# ── ② ★★★ 静态排除：**261 没有碰 `create_base_flange`** ──────────────
def test_261_did_not_touch_create_base_flange():
    """★★★ 261 只改了**读**路径（`_read_k_factor`）⇒ ★ **不该**出现在 `create_base_flange` 里。

    ★ 依据：★ 261 的两处改动是 ① 新增 `_read_k_factor`（★ 在 `sheet_metal_evidence` 的读路径上调用）；
    ② `sw_simulation` 的读法。★ `create_base_flange` 用的是 `bend_allowance.KFactor = ...`（★ **写**）。
    ⇒ ★★ **本判据的作用是「把嫌疑对象排除掉」**，★ 免得下一个人先去怀疑 261。
    """
    body = _create_flange_body()
    assert body, "取不到 `create_base_flange` 的源码 ⇒ 判据失效"
    assert "_read_k_factor" not in body, "261 的函数出现在 `create_base_flange` 里 ⇒ 结论要改"
    assert WRITE_PATH in body, "`create_base_flange` 的**写**路径不见了 ⇒ 函数被改过"


# ── ③ ★★ 阻塞链必须写清：造不出件 ⇒ `_read_k_factor` 验不了 ──────────
def test_blocking_chain_is_explicit():
    """★★ `_read_k_factor` 验不了的**真因**是「造不出 `BaseFlange`」，★ **不是**「没有夹具零件」。

    ★★ 这两者在**只看结论**时同形（★ 都是「未验」）⇒ ★ 必须把**真因**写下来。
    """
    assert "造不出" in MACHINE["known_fact_34"] or MACHINE["regression"] is True, \
        "真因没写清"
    assert "CreateFeature" in MACHINE["error"], "真因必须指向失败点"


# ── ④ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 状态改 ok；② 失败点改掉；③ `create_base_flange` 里出现 261 的东西。"""
    good = _create_flange_body()
    assert not _failures(MACHINE, good), "正常读数被判红 ⇒ 判据过严"
    assert _failures(dict(MACHINE, status="ok"), good), "状态改 ok 未判出 ⇒ **空判据**"
    assert _failures(dict(MACHINE, error="别的原因"), good), "失败点改掉未判出 ⇒ **空判据**"
    assert _failures(MACHINE, good + "\n    _read_k_factor(x)"), \
        "`create_base_flange` 里出现 261 的函数却未判出 ⇒ **空判据**"
