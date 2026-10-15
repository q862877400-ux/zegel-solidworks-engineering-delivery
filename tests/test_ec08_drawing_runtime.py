"""★ EC08 真机判据 —— **工程图**（★ 关掉「工程图真机未出图」这条残留）。

★★★ **为什么要有它**：★ EC08 上一轮只做了**验收方法层**（★ 纯离线判据）——
  ★★ **真机没出过图** ⇒ ★ 「视图/标注**回读比对**」这条**没有真读数** ✗
★ 本轮**真出图**（★ 证据 `output/_probe_ec08_drawing.json` · ★ 走 `sw_guard`）：
  · ★ 源件：★ 建成并存盘（**63 KB**）
  · ★ 工程图：★ 真出图（**87 KB**）· ★ **三视图**（`工程图视图1/2/3` · 比例 **1:5**）
  · ★ **技术要求注释**：★ `created=True` · ★ `verified=True` · ★ `status=pass`
  · ★ **逐视图回读**：★ `view_annotations_report` 读到 **3 个视图**（★ 每视图标注数**可读**）
★★ **如实登记**：★ 那 3 个视图的**标注数都是 0** —— ★ 因为注释是**图纸级**的，
  ★★ **不是视图级标注** ⇒ ★ 本判据**不**要求标注数 > 0（★ 不假装）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/310-ec08-drawing-and-processes/spec.md`（★ EC08A 工程图基础）
#         `output/_probe_ec08_drawing.json`（★ 真机证据）
#         `scripts/sw_drawing.py`（★ `create_standard_views` · `add_note` · `get_all_views`）
#         `scripts/sw_drawing_query.py`（★ `view_annotations_report` —— ★ 本仓已有的读侧）
# 定位:   ★ 守卫 EC08A 的**真机**面。
# 官方依据: `IDrawingDoc::CreateDrawViewFromModelView3` · `IDrawingDoc::InsertNote`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 读证据 JSON —— ★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "output" / "_probe_ec08_drawing.json"


@pytest.fixture(scope="module")
def ev() -> dict:
    if not EVIDENCE.is_file():
        pytest.skip("★★ 缺真机证据 `%s` ⇒ 跑 `sw_guard` 探针后再判"
                    % EVIDENCE.relative_to(ROOT))
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_evidence_is_from_a_real_machine(ev):
    """★★ 证据来自真机（★ 有版本号 · ★ 未被阻塞）。"""
    assert ev.get("revision"), "★★ 没有 SolidWorks 版本号"
    assert not ev.get("blocked"), "★ 那次被阻塞：%r" % ev.get("blocked")


def test_source_part_was_built_and_saved(ev):
    """★★ 源件**建成并落盘**（★ 工程图要有真源模型）。"""
    assert ev.get("part_built") is True, "★ 源件没建成"
    assert ev.get("part_saved") is True, "★ 源件没存盘"
    assert ev.get("part_bytes", 0) > 0, "★★ 源件是零字节"


def test_drawing_file_is_real(ev):
    """★★★★ **工程图真的出图了**（★ 判据是**文件** —— ★ 承 EC00 的导出口径）。"""
    assert ev.get("drawing_file_exists") is True, "★★ 图档不存在 ⇒ 没真出图"
    assert ev.get("drawing_bytes", 0) > 0, "★★★ 图档是**零字节** ⇒ ★ 假成功"


def test_three_standard_views_were_created(ev):
    """★★★★★ **三视图真的建出来了**（★ 逐字承 EC08A：★「★ **视图**/剖视/局部放大」）。

    ★★ 判据：★ 从**工程图文档**回读视图清单 ⇒ ★ **≥ 3 个**且**各有比例** ✓
    """
    views = (ev.get("readback") or {}).get("views") or []
    assert len(views) >= 3, "★★ 视图数 %d < 3 ⇒ 三视图没建出来" % len(views)
    for v in views:
        assert v.get("name"), "★ 视图没有名字"
        assert v.get("scale"), "★ 视图 %r 没有比例" % v.get("name")
    #: ★ 比例 1:5（★ 200×150×10 的板 ⇒ 合理）
    assert views[0]["scale"] == [1.0, 5.0], "★ 比例不是 1:5：%r" % views[0]["scale"]


def test_technical_requirement_note_was_verified(ev):
    """★★★★ **技术要求注释**（★ 逐字承 EC08A：★「★ ……**技术要求**……」）。

    ★★ 判据：★ `add_note` 回读必须 **`created` + `verified` + `status=pass`** ——
      ★ 那正是本仓的**回读而非取返回值**口径 ✓
    """
    note = ev.get("add_note") or {}
    assert not ev.get("add_note_error"), "★★ 加注释报错：%r" % ev.get("add_note_error")
    assert note.get("created") is True, "★★ 注释没创建"
    assert note.get("verified") is True, "★★ 注释没通过回读验证"
    assert note.get("status") == "pass", "★★ 注释状态 = %r" % note.get("status")
    #: ★★ **文本要能回读出来**（★ 与请求的一致）
    assert note.get("text_evidence") == note.get("text"), (
        "★★ 回读文本 ≠ 请求文本：%r vs %r" % (note.get("text_evidence"), note.get("text")))


def test_per_view_readback_works(ev):
    """★★★★ **逐视图回读可用**（★ 逐字承 EC08A：★「★ 尺寸值、基准、公差、
    模型配置版本都能**回读比对**」）。

    ★★ 判据：★ `view_annotations_report` 必须**读到视图**且**每视图有可读的计数字段** ——
      ★★ **不要求计数 > 0**（★ 图纸级注释不算视图标注 —— ★ 如实，★ 不假装）✓
    """
    a = (ev.get("readback") or {}).get("annotations") or {}
    assert not (ev.get("readback") or {}).get("annotations_error"), (
        "★★ 标注回读报错：%r" % (ev.get("readback") or {}).get("annotations_error"))
    assert a.get("view_count", 0) >= 3, "★★ 标注回读只看到 %r 个视图" % a.get("view_count")
    for v in (a.get("views") or []):
        assert "annotation_count_by_api" in v, (
            "★★ 视图 %r 没有可读的标注计数字段" % v.get("name"))
        assert "display_dimension_count" in v, "★★ 缺 `display_dimension_count` 读数"


def test_no_residue_after_the_run(ev):
    """★★★★ **零残留**（★ 关两个文档 + ★ 删两个工件）。"""
    assert set(ev.get("closed") or []) == {"drawing", "part"}, (
        "★★ 文档没关全：%r" % ev.get("closed"))
    assert set(ev.get("artifacts_removed") or []) == {
        "_ec08_drawing.SLDDRW", "_ec08_part.SLDPRT"}, (
        "★★ 工件没删干净：%r" % ev.get("artifacts_removed"))


def test_drawing_standard_does_not_imply_machine_compliance(ev):
    """★★★★★ **制图标准符合 ≠ 整机安全合规**（★ 逐字承 EC08 验收）。

    ★★ 判据：★ 本特性（★ `processes.py`）必须**带着那条免责声明常量** ——
      ★★ 真机出图**不改变**这一点 ✓
    """
    import engineering.processes as P
    assert "不代表" in P.NOT_A_SAFETY_COMPLIANCE_STATEMENT
    assert "EC11" in P.NOT_A_SAFETY_COMPLIANCE_STATEMENT
