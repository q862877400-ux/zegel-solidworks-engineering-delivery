"""★ 门禁负例：`check_param_binding` 能不能抓到「**注入名 ≠ 目标函数形参名**」（事实 502）。

★ 手法（★ 事实 62 的纪律：**负例测试是门禁有效的唯一证明**）：
  取**真实的** spec（`solidworks_hole_standards`，其函数首参是 `sw`），
  用 `dataclasses.replace` **把 `inject` 改成 `"sw_app"`**（★ 那正是修前的真实形态），
  再把 `all_specs()` 换成 `[变异体]` ⇒ ★ 断言门禁**必须报**。
★ 正对照：不变异的那条 ⇒ ★ 断言门禁**不报**（★ 防止"永远报错"的假绿门禁）。
"""
from __future__ import annotations

import dataclasses
import importlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
for _p in (str(REPO), str(REPO / "mcp-server"), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

TARGET = "solidworks_hole_standards"


def _gate():
    return importlib.import_module("scripts.check_param_binding")


def _real_spec():
    rc = importlib.import_module("register_capabilities")
    for s in rc.all_specs():
        if getattr(s, "name", None) == TARGET:
            return rc, s
    raise AssertionError("★ 找不到 %s —— 门禁负例的前提没了，请换一条" % TARGET)


def _run_with(monkeypatch, specs):
    rc, _s = _real_spec()
    monkeypatch.setattr(rc, "all_specs", lambda: list(specs), raising=True)
    gate = _gate()
    return gate.check()


def test_positive_control_clean():
    """★ 正对照：**未变异**的那条不该报 —— ★ 防止门禁变成"永远报错"的假绿。"""
    _rc, spec = _real_spec()
    monkeypatch = None  # 不需要打桩：直接看真实树
    problems = _gate().check()
    #: ★ 真实树应当是干净的（★ 事实 502 修完之后）
    assert not any(TARGET in p and "inject=" in p for p in problems), \
        "★ 真实树里 %s 被判成注入名不符 —— 要么它真坏了，要么门禁误报：%s" % (TARGET, problems[:3])
    del monkeypatch, spec


def test_gate_catches_undeclared_required_param():
    """★★ **负例（判据 ⑤）**：把一个**必填形参**从 spec 的 `params` 里拿掉 ⇒ ★ 门禁**必须**报。

    ★★ 这用的就是**真出事过的那条工具的形状**：`solidworks_delivery_pack_and_go_audit_matrix`
      原先**只声明 3 个参数、而函数要 8 个** ⇒ 真机
      `TypeError: … missing 2 required positional arguments: 'associated_drawings' and 'outputs'`。
    ★ 手法与上面那条 ④ 的负例一致：★ 取**真实 spec**、用 `dataclasses.replace` **只改这一处**、
      打桩 `all_specs()` ⇒ ★ 断言门禁报出来；★ 正对照（不改）⇒ 断言**不报**。
    """
    import dataclasses  # noqa: PLC0415

    import pytest  # noqa: PLC0415

    rc = importlib.import_module("register_capabilities")
    gate = _gate()
    target = "solidworks_delivery_pack_and_go_audit_matrix"
    spec = next((s for s in rc.all_specs() if getattr(s, "name", None) == target), None)
    if spec is None:
        pytest.skip("★ 找不到 %s —— 门禁负例的前提没了，请换一条" % target)
    assert getattr(spec, "derived_args", None) is None, (
        "★ 这条 spec 有 derived_args ⇒ 判据 ⑤ 会豁免它，负例不成立，请换一条")
    names = [getattr(p, "name", None) for p in spec.params]
    assert "associated_drawings" in names, "★ 前提变了（那条 Param 不在）"
    keep = [p for p in spec.params if getattr(p, "name", None) != "associated_drawings"]
    mutated = dataclasses.replace(spec, params=keep)
    mp = pytest.MonkeyPatch()
    try:
        mp.setattr(rc, "all_specs", lambda: [mutated], raising=True)
        problems = gate.check()
    finally:
        mp.undo()
    hits = [p for p in problems if "必填形参" in p and "associated_drawings" in p]
    assert hits, ("★★ 门禁**没抓到**「必填形参没被声明」—— 那正是 "
                  "`solidworks_delivery_pack_and_go_audit_matrix` 逾期未修的原因。"
                  "返回的问题清单：%r" % problems[:5])


def test_gate_catches_inject_key_mismatch():
    """★★ **负例**：把 `inject` 改成与函数首参不符 ⇒ ★ 门禁**必须**报（事实 502 的形态）。"""
    import pytest  # noqa: PLC0415

    rc, spec = _real_spec()
    before = getattr(spec, "inject", None)
    assert before, "★ 这条 spec 本来就没有 inject，负例不成立"
    mutated = dataclasses.replace(spec, inject="sw_app" if before != "sw_app" else "manager")
    #: ★ 打桩：把 all_specs 换成 [变异体]
    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(rc, "all_specs", lambda: [mutated], raising=True)
        problems = _gate().check()
    finally:
        monkeypatch.undo()
    hits = [p for p in problems if "inject=" in p]
    assert hits, ("★★ 门禁**没抓到**「注入名 ≠ 目标函数形参名」—— 那正是事实 502 里 11 条全部漏过的原因。"
                  "返回的问题清单：%r" % problems[:5])
    assert any("形参" in h for h in hits), "★ 报是报了，但没说是形参不符：%r" % hits[:2]
