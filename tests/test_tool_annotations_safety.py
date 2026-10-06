"""★ 工具注解的**安全契约**：未知就不外发 —— 钉住那两个曾经对外「误报」的字段。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_registry.py` 的 `_tool_annotations` / `uniform_safety_fields`
# 定位:   ★★ 规格外的一次**安全修复**（2026-10-06，由外部评审促成）。★ 起因：
#   ★★★ 我们对外暴露的 MCP 工具注解里**有两个误报**，且都是客户端**据以决定
#     要不要确认、能不能重试**的字段：
#     ① `idempotentHint` 原本对 **448 个工具全部为 True**（因为 `idempotent` 默认值就是 True），
#        而其中绝大多数是**创建/插入/阵列**类 —— ★★ 客户端超时重试会**重复改模型**；
#     ② `destructiveHint` **硬编码 False** —— ★ 删除/覆盖保存类工具也宣称「非破坏性」。
# 判据:   ★ 依据 MCP 的**缺省语义**（这是修复的立足点，不是我猜的）：
#     ★ `destructiveHint` **缺省即视为「可能破坏」** ⇒ ★ **省略就是保守**；
#     ★ `idempotentHint` 缺省即「未声明」 ⇒ ★ 客户端**不得**假定可重试 ✓
# 官方依据: MCP 工具注解三字段的缺省语义（`readOnlyHint` 缺省 False · `destructiveHint` 缺省 True ·
#   `idempotentHint` 缺省 False）；★ 我们的宿主据此消费它们，见 `tool_registry.py` 的注册路径。
# ⚠ 限度: ★ 本文件只验**注解形状**，不验「某个工具到底幂不幂等」—— ★ 后者要靠真机指纹差分（另行）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as rc                            # noqa: E402
from tool_registry import ToolSpec, _tool_annotations, uniform_safety_fields   # noqa: E402


def _spec(**kw) -> ToolSpec:
    base = dict(name="t_x", title="t", module="sw_part", function="noop")
    base.update(kw)
    return ToolSpec(**base)


def test_undeclared_idempotency_is_not_advertised():
    """★★ 未声明幂等 ⇒ **不发 `idempotentHint`**（★ 原来默认发 True，等于宣称「可安全重试」）✓"""
    ann = _tool_annotations(_spec())
    assert "idempotentHint" not in ann, ann


def test_explicit_idempotency_is_advertised():
    """★ 真的声明了才发（★ 三态：未声明 / 是 / 否）✓"""
    assert _tool_annotations(_spec(idempotent=True))["idempotentHint"] is True
    assert _tool_annotations(_spec(idempotent=False))["idempotentHint"] is False


def test_undeclared_destructive_is_omitted_for_writers():
    """★★ 非只读且未声明破坏性 ⇒ **不发 `destructiveHint`** —— ★ 依据 MCP 缺省语义，
    缺省 = 可能破坏 ⇒ ★ **省略就是保守**（★ 原来是硬编码 False，等于宣称「安全」）✓"""
    ann = _tool_annotations(_spec(read_only=False))
    assert "destructiveHint" not in ann, ann


def test_read_only_tools_may_declare_non_destructive_explicitly():
    """★ 只读工具**确定**不做破坏性更新 ⇒ 可以明确发 False（★ 这是「知道」，不是「猜」）✓"""
    ann = _tool_annotations(_spec(read_only=True))
    assert ann["readOnlyHint"] is True
    assert ann["destructiveHint"] is False


def test_explicit_destructive_wins():
    ann = _tool_annotations(_spec(read_only=False, destructive=True))
    assert ann["destructiveHint"] is True


def test_uniform_safety_fields_gate_fires_on_the_old_bug():
    """★★★ **负例（事实 62：门禁写了不等于有效，负例是唯一的证明）** ——
    把「448 个工具全是 True」的**旧形态**喂进去，门禁**必须**报出来；
    而「全体未声明」（诚实状态）**不许**报 ✓"""
    old = [_spec(name="a", idempotent=True), _spec(name="b", idempotent=True)]
    #: ★ 这两个合成 spec 的 `read_only` 也都是默认 False ⇒ ★ **两个单值字段都要报出来** ✓
    assert uniform_safety_fields(old) == {
        "read_only": {"value": False, "count": 2},
        "idempotent": {"value": True, "count": 2},
    }, uniform_safety_fields(old)
    #: ★⚠ "诚实状态"的合成样本**必须把 `read_only` 造成不齐** —— ★ 否则它自己就是个单值字段
    #:   （★ 那是**真阳性**，不是误报；★ 我第一版就是这么写错的）✓
    honest = [_spec(name="a", read_only=True), _spec(name="b", read_only=False)]
    assert uniform_safety_fields(honest) == {}, uniform_safety_fields(honest)


def test_real_declarations_have_no_uniform_safety_field():
    """★ 真实声明里**不许**再有「某个安全字段被默认值填满」的形态 ✓"""
    assert uniform_safety_fields(rc.all_specs()) == {}


def test_real_annotations_never_claim_idempotency_or_safety_we_do_not_know():
    """★ 端到端：448 个真实工具里，★ **一个都不许**出现「未声明却发了幂等/破坏性注解」的组合 ✓"""
    bad = []
    for s in rc.all_specs():
        ann = _tool_annotations(s)
        if "idempotentHint" in ann and getattr(s, "idempotent", None) is None:
            bad.append((s.name, "idempotentHint"))
        if "destructiveHint" in ann and getattr(s, "destructive", None) is None \
                and not s.read_only:
            bad.append((s.name, "destructiveHint"))
    assert bad == [], bad[:5]
