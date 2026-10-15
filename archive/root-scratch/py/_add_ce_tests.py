import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_sketch_edit_contract.py")
t = P.read_text(encoding="utf-8")

ADD = '''

# ── convert_entities（轮 115：从「真缺」档补）────────────────────────

def test_convert_entities_uses_the_current_entry_not_the_obsolete_one():
    """@brief ★ 走 `ISketchManager.SketchUseEdge3`，**不走**已废弃的 `SketchUseEdge2`。

    官方 md 明写 `IModelDoc2.SketchUseEdge2` 是
    `Obsolete. Superseded by ISketchManager::SketchUseEdge.`
    """
    t = (REPO_ROOT / "scripts" / "sw_sketch_edit.py").read_text(encoding="utf-8")
    assert "SketchUseEdge3" in t
    assert "SketchUseEdge2" not in t.split("# ── 来源")[0], "实现里不许用已废弃的入口"
    assert "Obsolete" in t, "来源块应记下「为什么不用 SketchUseEdge2」"


def test_convert_entities_signature_follows_official():
    """@brief 官方 `SketchUseEdge3(Boolean Chain, Boolean InnerLoops)` —— 两参。"""
    params = list(inspect.signature(sw_sketch_edit.convert_entities).parameters)
    assert params[0] == "model"
    assert "chain" in params and "inner_loops" in params


class _FakeSketchManagerWithEdge:
    def __init__(self, ret=True, sketch=object()):
        self.calls = []
        self._ret = ret
        self._sketch = sketch

    def SketchUseEdge3(self, *args):      # noqa: N802
        self.calls.append(args)
        return self._ret

    @property
    def ActiveSketch(self):
        return self._sketch


def test_convert_entities_passes_both_official_arguments_in_order():
    """@brief 两个实参按官方顺序：`(Chain, InnerLoops)`。"""
    skm = _FakeSketchManagerWithEdge(ret=True)
    m = _FakeModel(skm)
    assert sw_sketch_edit.convert_entities(m, chain=False, inner_loops=True) is True
    assert skm.calls == [(False, True)]


def test_convert_entities_defaults_match_the_official_meaning():
    """@brief 默认 `chain=True`（整条链）/ `inner_loops=False`（不转内环）。"""
    skm = _FakeSketchManagerWithEdge(ret=True)
    sw_sketch_edit.convert_entities(_FakeModel(skm))
    assert skm.calls == [(True, False)]


def test_convert_entities_raises_when_official_returns_false():
    """@brief ★ 官方失败返回 `False` ⇒ **必须抛带原因的错**（不许静默成功）。

    ⚠ 这是本函数最要紧的一条：`False` 是"假值"，**很容易被 `if not got: pass` 吞掉**。
    """
    skm = _FakeSketchManagerWithEdge(ret=False)
    with pytest.raises(RuntimeError) as ei:
        sw_sketch_edit.convert_entities(_FakeModel(skm))
    msg = str(ei.value)
    assert "选中" in msg, msg


def test_convert_entities_raises_when_not_in_sketch_manager():
    """@brief 拿不到 `SketchManager` 时抛**带原因**的错。"""
    with pytest.raises(RuntimeError):
        sw_sketch_edit.convert_entities(_FakeModel(None))
'''

anchor = "\ndef test_module_declares_stitched_and_records_the_conflict():"
assert anchor in t, "锚点不符"
if "test_convert_entities_uses_the_current_entry" not in t:
    t = t.replace(anchor, ADD + anchor, 1)
    P.write_text(t, encoding="utf-8")
    print("  ok 已加 convert_entities 的 6 条测试")
else:
    print("  已有")
