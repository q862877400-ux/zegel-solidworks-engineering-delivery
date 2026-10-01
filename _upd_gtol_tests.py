import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_gtol_contract.py")
t = P.read_text(encoding="utf-8")

OLD = '''class _FakeGtol:
    def __init__(self, frame=None):
        self._frame = frame
        self.frame_calls = []

    def GetFrame(self, i):      # noqa: N802
        self.frame_calls.append(i)
        return self._frame
'''
NEW = '''class _FakeGtol:
    """桩：`GetFrameCount` 可配，`AddFrame` 会把它 +1（模拟官方语义）。"""

    def __init__(self, frame=None, count=1, add_ok=True):
        self._frame = frame
        self._count = count
        self._add_ok = add_ok
        self.frame_calls = []
        self.add_calls = 0

    def GetFrameCount(self):        # noqa: N802
        return self._count

    def AddFrame(self):             # noqa: N802
        self.add_calls += 1
        if not self._add_ok:
            return False
        self._count += 1
        return True

    def GetFrame(self, i):      # noqa: N802
        self.frame_calls.append(i)
        return self._frame
'''
assert OLD in t, "桩锚点不符"
t = t.replace(OLD, NEW, 1)

ADD = '''

# ── 轮 120：真机冒烟查出的那一步（帧要先存在）──────────────────────

def test_add_indicator_ensures_the_frame_exists_first():
    """@brief ★ **新 GTol 可能一帧都没有** ⇒ 取帧前必须补帧。

    ⚑ 轮 120 真机实测：`InsertGtol()` 建的 GTol `GetFrameCount()` 可能是 0/1，
    而 `GetFrame(1)` **返回 None** ⇒ 轮 119 的实现就栽在这里。
    """
    fr = _FakeFrame(ret=True)
    g = _FakeGtol(frame=fr, count=0)          # 一帧都没有
    assert sw_gtol.add_gtol_indicator(g, tol_type=23) is True
    assert g.add_calls == 1, "应当补 1 帧"
    assert g.frame_calls == [1]


def test_add_indicator_does_not_add_frames_when_already_enough():
    """@brief 帧已经够时**不该多补**（补帧会改 Gtol 状态）。"""
    g = _FakeGtol(frame=_FakeFrame(ret=True), count=1)
    sw_gtol.add_gtol_indicator(g, tol_type=23)
    assert g.add_calls == 0


def test_ensure_gtol_frame_rejects_zero_based_index():
    """@brief `frame` 是**1 基**，传 0 要拦下（官方 `FrameIndex` 1 基）。"""
    with pytest.raises(ValueError):
        sw_gtol.ensure_gtol_frame(_FakeGtol(), 0)


def test_ensure_gtol_frame_raises_when_count_does_not_grow():
    """@brief ★ `AddFrame()` 之后计数不涨 ⇒ **抛**（说明该 Gtol 不是 2022 格式）。"""
    with pytest.raises(RuntimeError) as ei:
        sw_gtol.ensure_gtol_frame(_FakeGtol(count=0, add_ok=False), 1)
    assert "2022" in str(ei.value), str(ei.value)


def test_add_gtol_frame_raises_on_false():
    """@brief `AddFrame()` 返回 `False` ⇒ **抛**（不静默）。"""
    with pytest.raises(RuntimeError):
        sw_gtol.add_gtol_frame(_FakeGtol(add_ok=False))


def test_module_documents_that_the_frame_path_is_unreachable_on_this_machine():
    """@brief ★★ **本轮最重要的判据**：源码里必须**如实写明**那条路在这台机器上到不了。

    ⚠ 没有这条，下一个人会以为 `add_gtol_indicator` 是能用的。
    """
    t = (REPO_ROOT / "scripts" / "sw_gtol.py").read_text(encoding="utf-8")
    assert "验证等级：分成两半" in t, "文件头要分开声明两半的等级"
    assert "不可用" in t
    assert "事实 53" in t, "要写明为什么停手"
'''
anchor = "\ndef test_insert_gtol_raises_when_nothing_created():"
assert anchor in t, "插入锚点不符"
if "test_add_indicator_ensures_the_frame_exists_first" not in t:
    t = t.replace(anchor, ADD + anchor, 1)
P.write_text(t, encoding="utf-8")
import ast
ast.parse(t)
print("  ok 测试已更新（桩 + 6 条新判据）；语法 OK")
