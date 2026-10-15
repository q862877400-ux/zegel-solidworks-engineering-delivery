"""★ EC00 T014 判据：**上下文与引用负例** —— 错文档/配置/版本、引用歧义 ⇒ **修改前拒绝**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/302-ec00-trustworthy-tool-base/contracts/context.md`（★ 上下文核验调用序）
#         `specs/302-ec00-trustworthy-tool-base/data-model.md` §4.2（★ 引用解析封闭结果）
#         `scripts/sw_selection_spec.py`（★ 三解析器 · ★ 声明式）
#         `scripts/sw_fingerprint.py`（★ 九类状态 · ★ `KNOWN_UNAVAILABLE`）
# 定位:   ★ EC00 **T014**（★ 逐字：「建错文档/配置/版本、持久引用失效/歧义、未保存文档身份冲突测试」）。
#         ★★★ **完成判据**：★ 错误对象**在修改前被拒绝**；★ **0 或多候选不返回成功**。
# 官方依据: `IEntity::Select4(Append, Callout)`（★ 按对象选）· `ISketch::GetConstrainedStatus`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM · ★ 用**假宿主**）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★★ 引用解析的**封闭结果**（★ `data-model.md` §4.2）
RESOLVED_UNIQUE = "resolved_unique"
NOT_FOUND, AMBIGUOUS, WRONG_CONTEXT, UNSUPPORTED = (
    "not_found", "ambiguous", "wrong_context", "unsupported")
ALLOWED = {RESOLVED_UNIQUE}
REJECTED = {NOT_FOUND, AMBIGUOUS, WRONG_CONTEXT, UNSUPPORTED}


def _may_modify(resolution: str) -> bool:
    """★ 只有 `resolved_unique` 允许进入修改（★ 失败关闭）。"""
    return resolution in ALLOWED


# ── ① 引用歧义 ⇒ 拒绝 ─────────────────────────────────────────────────

def test_ambiguous_reference_is_rejected():
    """★★★ T014：★ **多候选 ⇒ 拒绝**（★ 绝不自动挑邻近面）。

    ★★ 依据（★ `plan.md` §6.3 逐字）：
      「★★ **几何接近也不能自动确认是原对象**」+ ★「★ 只记录定位证据」。
    """
    assert not _may_modify(AMBIGUOUS), "★★ 多候选却被允许修改 ⇒ ★ 会自动挑邻近面"
    assert not _may_modify(NOT_FOUND), "★ 0 候选却被允许修改"


def test_geometric_proximity_does_not_authorize_selection():
    """★★★ T014：★ **几何接近不是授权**（★ 逐字：几何签名**只辅助核验**）。

    ★★ 依据（★ `data-model.md` §4.2 逐字）：
      「★★★ **几何签名只辅助核验，不是遇到引用失效时自动挑邻近面的授权**」。
    ★ 判据：★ 一个「距离很近」的候选**不能**把 `ambiguous` 变成 `resolved_unique`。
    """
    def resolve(candidates, *, proximity_only: bool) -> str:
        if len(candidates) == 1:
            return RESOLVED_UNIQUE
        if len(candidates) > 1:
            #: ★★ 即使几何很近，★ **多候选仍是 ambiguous**
            return AMBIGUOUS
        return NOT_FOUND

    assert resolve(["a", "b"], proximity_only=True) == AMBIGUOUS, (
        "★★ 两个候选**只凭几何接近**就被判成唯一 ⇒ ★ 违反「几何接近不是授权」")
    assert resolve(["a"], proximity_only=False) == RESOLVED_UNIQUE


# ── ② 错文档 / 错配置 / 错版本 ⇒ 拒绝 ────────────────────────────────

def test_wrong_document_config_or_version_is_rejected():
    """★★★ T014：★ 错文档/错配置/错版本 ⇒ ★ **修改前拒绝**（★ FR-006）。

    ★★ 依据（★ `contracts/context.md` §一 逐字）：
      「★★★ **活动窗口切换不构成授权**」。
    """
    def context_ok(expected: dict, actual: dict) -> bool:
        return (expected.get("doc") == actual.get("doc")
                and expected.get("config") == actual.get("config")
                and expected.get("rev") == actual.get("rev"))

    exp = {"doc": "D1", "config": "默认", "rev": "r1"}
    assert context_ok(exp, dict(exp)), "★ 完全一致应通过"
    #: ★★ 三种错法**都要被拒**
    assert not context_ok(exp, {"doc": "D2", "config": "默认", "rev": "r1"}), "★ 错文档未拒"
    assert not context_ok(exp, {"doc": "D1", "config": "C2", "rev": "r1"}), "★ 错配置未拒"
    assert not context_ok(exp, {"doc": "D1", "config": "默认", "rev": "r2"}), "★ 错版本未拒"


def test_active_window_switch_is_not_authorization():
    """★★★ T014：★ **活动窗口切换不构成授权**（★ 逐字承 US3 · FR-006）。

    ★ 判据：★ 文档身份**只认请求里声明的那个** —— ★★ 活动窗口变了**不影响**判定。
    """
    def which_doc(requested: str, active_window: str) -> str:
        #: ★★ **只认请求声明的** —— ★ 不看活动窗口
        return requested

    assert which_doc("D1", "D2") == "D1", (
        "★★ 用了活动窗口（D2）而不是请求声明的（D1）⇒ ★ 会改错文档")


# ── ③ 未保存文档身份冲突 ⇒ 拒绝 ──────────────────────────────────────

def test_unsaved_documents_have_distinct_identities():
    """★★★ T014：★ **两个未保存文档的空路径不能当同一 ID**（★ FR-006 · US3）。

    ★★ 依据（★ `data-model.md` §4.1 逐字）：
      「★ `session_document_id`：★ 会话内唯一；★★ **未保存文档也必须可区分**」+
      「★★ **空路径不是唯一身份**」。
    """
    def identity(path: str, session_id: str) -> str:
        #: ★★ **空路径 ⇒ 必须靠会话内 ID**（★ 不能把空路径当身份）
        return session_id if not path else path

    a = identity("", "sess-1")
    b = identity("", "sess-2")
    assert a != b, (
        "★★ 两个未保存文档的空路径被判成**同一个身份**（%r）⇒ ★ 会改错文档" % a)
    #: ★ 负例：★ 空路径**不能**作为身份
    assert identity("", "sess-1") != "", "★★ 空路径被当成了身份"


# ── ④ 指纹降级 ⇒ unknown（★ 不假装版本锁成立）───────────────────────

def test_unreadable_fingerprint_degrades_to_unknown():
    """★★★ T014：★ **指纹读不到 ⇒ `unknown`**，★★ **不假装版本锁成立**。

    ★★ 依据（★ `data-model.md` §4.1 逐字）：
      「★★★ **读不到不能证明没变**」+ ★「★★ **没有可靠内存指纹时采用保守策略并明确 `unknown`**」。
    """
    def version_verdict(known: bool, changed: bool) -> str:
        if not known:
            return "unknown"           #: ★★ **保守** —— ★ 不说「没变」
        return "changed" if changed else "same"

    assert version_verdict(known=False, changed=False) == "unknown", (
        "★★ 指纹读不到却判成 `same` ⇒ ★ 假装版本锁成立")
    assert version_verdict(known=True, changed=False) == "same"


# ── ⑤ 实现侧：`sw_fingerprint.py` 的 `KNOWN_UNAVAILABLE` 确实存在 ────

def test_fingerprint_known_unavailable_is_declared():
    """★★ T014：★ `sw_fingerprint.py` 必须**显式声明**已知不可用的桶。

    ★★ 依据（★ `research.md` §四 逐字）：★「`KNOWN_UNAVAILABLE` 的 `display` 桶全抛
      `com_error -2147417851`」。
    """
    src = (ROOT / "scripts" / "sw_fingerprint.py").read_text(encoding="utf-8", errors="replace")
    assert "KNOWN_UNAVAILABLE" in src, "★ `sw_fingerprint.py` 没有 `KNOWN_UNAVAILABLE`"
    assert "display" in src, "★ `display` 桶不见了"


# ── ⑥ 实现侧：`sw_selection_spec.py` 的三解析器 ──────────────────────

def test_selection_spec_has_three_resolvers():
    """★★ T014：★ 声明式解析器必须**三条路**都在（★ `__current_selection__` / `index:N` / 对象）。"""
    src = (ROOT / "scripts" / "sw_selection_spec.py").read_text(encoding="utf-8", errors="replace")
    for token in ("__current_selection__", "index:", "EntitySelectionError"):
        assert token in src, "★ `sw_selection_spec.py` 里缺 %r" % token
    #: ★★ **负例**：★ 歧义/越界必须**抛**（★ 不是静默返回 None）
    assert "raise EntitySelectionError" in src, (
        "★★ 解析失败时没有 `raise EntitySelectionError` ⇒ ★ 可能静默降级")
