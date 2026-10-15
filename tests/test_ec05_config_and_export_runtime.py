"""★ EC05 T07 真机判据 —— **配置切换往返** + **导出比较**（★ 关掉 `not_run`）。

★★★ **为什么要有它**：★ EC05-T07 逐字要「★ 保存重开/**配置切换**/**导出比较**」——
  ★ 上一轮只做了**保存重开**（★ 三重一致 ✓），★ 另两项记 `not_run` ✗
★ 本轮**真跑**（★ 证据 `output/_probe_ec05_t07.json` · ★ 走 `sw_guard`）：
  · ★ 配置：★ `默认` → `EC05_T07` → `默认` ⇒ ★ **真的变过 + 能切回来** ✓
  · ★ 导出：★ STEP **15827 B** · STL **684 B** ⇒ ★ 两者**都存在且非零** ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/307-ec05-first-part-loop/spec.md`（★ FR-007 · EC05-T07）
#         `output/_probe_ec05_t07.json`（★ 真机证据）
#         `scripts/engineering/part_loop.py`（★ `config_switch_verdict` · `export_compare_verdict`）
# 定位:   ★ 守卫 EC05-T07 的**真机**面。
# 官方依据: `IConfigurationManager::AddConfiguration` · `IModelDocExtension::SaveAs3`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 读证据 JSON —— ★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "output" / "_probe_ec05_t07.json"
TARGET = "EC05_T07"


@pytest.fixture(scope="module")
def ev() -> dict:
    if not EVIDENCE.is_file():
        pytest.skip("★★ 缺真机证据 `%s` ⇒ 跑 `sw_guard` 探针后再判"
                    % EVIDENCE.relative_to(ROOT))
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_evidence_is_from_a_real_machine(ev):
    """★★ 证据来自真机（★ 有 SolidWorks 版本号 · ★ 未被阻塞）。"""
    assert ev.get("revision"), "★★ 没有 SolidWorks 版本号"
    assert not ev.get("blocked"), "★ 那次被阻塞：%r" % ev.get("blocked")
    assert ev.get("plate_built") is True, "★ 试件没建成 ⇒ 后面两项无从谈起"


def test_config_really_switched_and_switched_back(ev):
    """★★★★★ 配置**真的切过去、也切得回来**（★ 逐字承 EC05-T07）。

    ★★ 判据（★ 与 EC00 T026 同口径）：★ 名字**真的变过** ⇒ 不是「没报错就算过」；
      ★ 且**能切回来** ⇒ 不「串」✓
    """
    assert ev.get("config_after_create") == TARGET, (
        "★★ 没切到目标配置：%r" % ev.get("config_after_create"))
    back = ev.get("config_after_switch_back")
    assert back and back != TARGET, (
        "★★ 卡在目标配置 %r ⇒ ★ 会「串」" % back)
    assert back == ev.get("config_before"), (
        "★★ 切回来了但**不是原来那个**：%r ≠ %r" % (back, ev.get("config_before")))
    assert not ev.get("create_error") and not ev.get("switch_back_error"), (
        "★★ 有错误：%r / %r" % (ev.get("create_error"), ev.get("switch_back_error")))


def test_config_verdict_is_ok(ev):
    """★★★ 判定器（★ 本仓的 `config_switch_verdict`）必须 **ok**。"""
    v = ev.get("config_verdict") or {}
    assert v.get("ok") is True, "★★ 判定不 ok：%r" % v
    assert v.get("switched_to_target") is True
    assert v.get("switched_back") is True


def test_exports_are_real_nonempty_files(ev):
    """★★★★ **导出比较**：★ 判据是**文件**（★ 存在且**非零字节** —— ★ 承 EC00 口径）。

    ★★ 依据（★ EC00 的导出口径）：★「★ **判据是文件**」——
      ★ 不看 API 返回值，★ 看磁盘上真的有一个非空文件 ✓
    """
    exports = ev.get("exports") or {}
    assert exports, "★★ 没有任何导出读数"
    for fmt, info in exports.items():
        assert info.get("exists") is True, "★★ %s 没导出" % fmt
        assert info.get("bytes", 0) > 0, (
            "★★★ %s 是**零字节** ⇒ ★ 那是**假成功**（EC00 抓到过这种）" % fmt)


def test_export_verdict_is_ok(ev):
    """★★★ 导出判定器必须 **ok**。"""
    v = ev.get("export_verdict") or {}
    assert v.get("ok") is True, "★★ 导出判定不 ok：%r" % v
    assert v.get("items"), "★ 没有逐项读数"


def test_no_residue_after_the_run(ev):
    """★★★★ **零残留**（★ 关文档 + ★ 删自有工件 —— ★ 承 EC00 的收尾纪律）。"""
    assert ev.get("closed") is True, "★★ 没关掉自己开的文档"
    removed = ev.get("artifacts_removed") or []
    assert set(removed) == {"_ec05_t07.STEP", "_ec05_t07.STL"}, (
        "★★ 自有工件没删干净：%r" % removed)
