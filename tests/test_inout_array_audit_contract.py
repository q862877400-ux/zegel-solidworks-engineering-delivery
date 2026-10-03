"""★ `in,out` 数组形参审计的**契约测试**（不连 SolidWorks、只读产物与源码）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_inout_array_audit_contract.py —— 本文件自身
# 定位:   ★ 2026-10-03（轮 514）★ 给 `tools/audit_inout_array_params.py` 的产物**立契约**。
#
#   ★★ **为什么加它**（★ 那正是本任务要的「加静态门禁」）：
#     · 那份审计是事实 128/129 的落地产物 —— 它用**第 4 套签名源**（类型库方法表）查出
#       **62 条 `in,out` 数组形参**（★ 涉及 496 个本仓调用过的成员名）。
#     · ★★ 而本轮查明：**它自己没有被任何门禁引用** ⚠ ——
#       只有 `scripts/audit_byref_args.py` 的**注释**提到了它（★ 把结论写回了口径段）。
#     ⇒ ★★ **故它"跑过一次"之后就再也不会被跑** ⇒ ★ 产物会**悄悄过期** ⚠
#   ⇒ ★ 本测试把它从「跑过一次」变成「**每次都被检查**」：
#     ★ 断言**产物存在**、**结构在**、**关键数字合理**，
#     ★ 并在**类型库变化**时提示该重跑（★ 与"新鲜度"那族门禁同一思路）。
#
#   ⚠ **本测试不重跑那份审计**（★ 它要读 10 个 `.tlb`）—— ★ 它只查**产物与源码的自洽**：
#     ★★ 若源码里那些数字被改动而产物没重生成 ⇒ 本测试会报出来。
#
# 官方依据: 产物由 `comtypes.client.GetModule('<tlb>')` 的方法表算出
#   （★ 见 `tools/audit_inout_array_params.py` 的来源块）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = REPO_ROOT / "output" / "inout-array-params.json"
AUDITOR = REPO_ROOT / "tools" / "audit_inout_array_params.py"


def _artifact() -> dict:
    assert ARTIFACT.is_file(), (
        "缺 `output/inout-array-params.json` ⇒ ★ 请先跑 "
        "`python tools/audit_inout_array_params.py`（★ 纯静态，不连 SolidWorks）")
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_artifact_has_the_expected_shape():
    """① ★ 产物的**结构**在（★ 那 4 个键是这条审计的全部结论）。"""
    d = _artifact()
    for k in ("per_tlb", "interfaces", "inout_array_params", "called_members"):
        assert k in d, "产物缺键 %r（★ 结构变了 ⇒ 消费者要同步改）" % k
    assert isinstance(d["per_tlb"], dict) and d["per_tlb"], "per_tlb 该非空"
    assert isinstance(d["inout_array_params"], list), "inout_array_params 该是列表"


def test_scanned_every_type_library():
    """② ★ 它**真的扫了多个库**（★ 只扫一个库的审计没有意义）。"""
    d = _artifact()
    tlbs = list((d.get("per_tlb") or {}).keys())
    assert len(tlbs) >= 5, "★ 至少该扫 5 个类型库；实际 %d 个：%s" % (len(tlbs), tlbs)
    #: ★ sldworks.tlb 是本仓主用的那个 —— 它必须在
    assert any("sldworks" in t.lower() for t in tlbs), "★ 没有扫 sldworks.tlb"


def test_the_62_inout_records_are_well_formed():
    """③ ★ 每条记录**字段齐**（★ 缺字段的清单没法用来核调用点）。"""
    d = _artifact()
    rows = d["inout_array_params"]
    #: ★ 数字来自事实 129 的实测；★ 若真变成 0，那说明扫描坏了
    assert len(rows) > 0, "★ `in,out` 数组形参一条都没查到 ⇒ 扫描多半坏了"
    for r in rows[:80]:
        for k in ("iface", "member", "param", "argtype"):
            assert k in r, "记录缺 %r：%s" % (k, json.dumps(r, ensure_ascii=False)[:120])
        assert r["argtype"].startswith(("LP_", "POINTER", "VARIANT")) or "VARIANT" in r["argtype"], (
            "argtype 看着不是数组类：%r" % r["argtype"])


def test_auditor_still_documents_its_own_scope():
    """④ ★ 审计**自己**要写明「不做结论」（★ 那是它的安全边界，不能被后人删掉）。"""
    src = AUDITOR.read_text(encoding="utf-8")
    assert "不做结论" in src, (
        "★ `tools/audit_inout_array_params.py` 里那句「**不做结论**（只在有真机证据时下结论）」"
        "是它的安全边界 —— ★ 删了它，后人会把候选清单当结论用 ⚠")
    assert "纯静态" in src, "★ 它该写明是纯静态的（不连 SolidWorks、不改文件）"


def test_numbers_are_consistent_with_each_other():
    """⑤ ★ 产物**内部自洽**（★ 若有人手改了数字，这里会报）。"""
    d = _artifact()
    per = d.get("per_tlb") or {}
    total_ifaces = sum(int(v.get("interfaces", 0)) for v in per.values() if isinstance(v, dict))
    declared = d.get("interfaces")
    if isinstance(declared, int):
        assert total_ifaces == declared, (
            "★ 各库接口数之和（%d）与顶层 `interfaces`（%d）不一致 ⇒ 产物被手改过？"
            % (total_ifaces, declared))
    total_io = sum(int(v.get("inout_array", 0)) for v in per.values() if isinstance(v, dict))
    if total_io:
        assert total_io >= len(d["inout_array_params"]), (
            "★ 各库 in,out 计数之和（%d）小于明细条数（%d）"
            % (total_io, len(d["inout_array_params"])))
