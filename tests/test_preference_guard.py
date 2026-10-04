"""★ 用户偏好守卫的负例测试（★ 含"异常路径也必须还原"与"不许静默留下痕迹"）。

★ 事实 62：**没有负例的判据不算数** —— ★ 本文件用**假 SW 对象**逐个证明那几条契约。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（`C:\swapi\types\ISldWorks\Get/SetUserPreference*.md`）
# 文件:   `scripts/sw_preference_guard.py`（★ 被测）
# 定位:   ★★★ 交付纪律的可执行判据：**改全局用户偏好 → 必须还原**（事实 525）。
#   ★ 真机背景：全仓曾有 **8 处 `SetUserPreference*`** 直接写、多数不还原
#     ⇒ 别人装一次我们的工具，他的 SolidWorks 设置就被改掉且回不去 ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from sw_preference_guard import Preference, preference_guard  # noqa: E402


class FakeSw:
    """★ 假 SW：只实现四个 Get/Set 偏好方法，并**记下每一次调用**。"""

    def __init__(self, initial=None):
        self.values = dict(initial or {})
        self.calls = []
        self.fail_set_for = set()
        self.fail_get_for = set()
        #: ★ 只让**还原那一次**的写失败（★ 用来测"还原失败要可见"这条契约）
        self.fail_second_set_for = set()
        self._set_seen = {}

    def _key(self, name, pref_id):
        return "%s:%s" % (name.replace("Set", "Get"), pref_id)

    def _get(self, name, pref_id):
        self.calls.append(name)
        if pref_id in self.fail_get_for:
            raise RuntimeError("读不到 %s" % pref_id)
        return self.values.get(self._key(name, pref_id))

    def _set(self, name, pref_id, value):
        self.calls.append(name)
        n = self._set_seen.get(pref_id, 0) + 1
        self._set_seen[pref_id] = n
        if pref_id in self.fail_set_for:
            raise RuntimeError("设不上 %s" % pref_id)
        if pref_id in self.fail_second_set_for and n >= 2:
            raise RuntimeError("还原那一次设不上 %s" % pref_id)
        self.values[self._key(name, pref_id)] = value
        return True

    # ★ 与 get_com_member 的「取或调」等价：带实参调用
    GetUserPreferenceStringValue = property(lambda self: lambda i: self._get("GetUserPreferenceStringValue", i))
    GetUserPreferenceIntegerValue = property(lambda self: lambda i: self._get("GetUserPreferenceIntegerValue", i))
    GetUserPreferenceToggle = property(lambda self: lambda i: self._get("GetUserPreferenceToggle", i))
    GetUserPreferenceDoubleValue = property(lambda self: lambda i: self._get("GetUserPreferenceDoubleValue", i))
    SetUserPreferenceStringValue = property(lambda self: lambda i, v: self._set("SetUserPreferenceStringValue", i, v))
    SetUserPreferenceIntegerValue = property(lambda self: lambda i, v: self._set("SetUserPreferenceIntegerValue", i, v))
    SetUserPreferenceToggle = property(lambda self: lambda i, v: self._set("SetUserPreferenceToggle", i, v))
    SetUserPreferenceDoubleValue = property(lambda self: lambda i, v: self._set("SetUserPreferenceDoubleValue", i, v))


def _sw(initial=None):
    sw = FakeSw(initial)
    sw.values["GetUserPreferenceIntegerValue:78"] = 0        # STL 质量原本 coarse
    sw.values["GetUserPreferenceToggle:111"] = False
    sw.values["GetUserPreferenceStringValue:20"] = "D:\\old\\part.prtdot"
    return sw


def test_the_value_is_restored_on_success() -> None:
    """★★ 核心契约：**用得着就用、用完必须还回去**。"""
    sw = _sw()
    with preference_guard(sw, [Preference("integer", 78, 1, why="导精细 STL")]) as rep:
        assert sw.values["GetUserPreferenceIntegerValue:78"] == 1, "★ 设进去了吗"
    assert sw.values["GetUserPreferenceIntegerValue:78"] == 0, "★ 没还原！"
    assert rep.restored and rep.restored[0]["match"] is True, rep.as_dict()
    assert rep.kept == [], "★ 不该有任何 keep"


def test_the_value_is_restored_even_when_the_body_raises() -> None:
    """★★ 异常路径也必须还原（★ `finally` 的全部意义）。"""
    sw = _sw()
    try:
        with preference_guard(sw, [Preference("toggle", 111, True)]):
            assert sw.values["GetUserPreferenceToggle:111"] is True
            raise ValueError("模拟业务异常")
    except ValueError:
        pass
    assert sw.values["GetUserPreferenceToggle:111"] is False, "★ 异常路径没还原！"


def test_string_preference_restored_case_insensitively() -> None:
    """★ 字符串路径按**大小写不敏感**比较（★ Windows 路径）——
    ★★ 故"只差大小写"时**一次都不写**，★ 原值（连同它原来的大小写）**原样不动**。"""
    sw = _sw()
    with preference_guard(sw, [Preference("string", 20, "d:\\OLD\\part.prtdot")]) as rep:
        pass
    assert sw.values["GetUserPreferenceStringValue:20"] == "D:\\old\\part.prtdot", (
        "★ 只差大小写 ⇒ 不该动它（也不该改它的写法）")
    assert rep.changed == [], "★ 没变却记成 changed：%r" % rep.changed
    #: ★ 而**真的不同**时，必须设进去、且**必须还回来**
    with preference_guard(sw, [Preference("string", 20, "E:\\other\\part.prtdot")]) as rep2:
        assert sw.values["GetUserPreferenceStringValue:20"] == "E:\\other\\part.prtdot"
    assert sw.values["GetUserPreferenceStringValue:20"] == "D:\\old\\part.prtdot", "★ 没还原"
    assert rep2.changed and rep2.restored, rep2.as_dict()


def test_unchanged_value_is_not_written_at_all() -> None:
    """★ 值本来相同 ⇒ **一次都不写**（★ 免得制造无谓的改动历史）。"""
    sw = _sw()
    with preference_guard(sw, [Preference("integer", 78, 0)]):
        pass
    assert "SetUserPreferenceIntegerValue" not in sw.calls, "★ 值没变却写了：%r" % sw.calls
    assert "GetUserPreferenceIntegerValue" in sw.calls, "★ 但旧值要读（那是判据的前提）"


def test_keep_leaves_it_and_says_so() -> None:
    """★ `keep` 是**唯一**能留下的路 —— ★ 且必须在报告里说出来（★ 不许静默留痕）。"""
    sw = _sw()
    with preference_guard(sw, [Preference("integer", 78, 1)], keep=[78]) as rep:
        pass
    assert sw.values["GetUserPreferenceIntegerValue:78"] == 1, "★ keep 应当留下"
    assert rep.kept and rep.kept[0]["pref_id"] == 78, rep.as_dict()
    assert "★ 调用方显式 keep" in rep.kept[0]["note"]


def test_restore_false_also_reports() -> None:
    """★ `restore=False` 同样要**留在报告里**（★ 它是"故意不还"，不是"忘了还"）。"""
    sw = _sw()
    with preference_guard(sw, [Preference("integer", 78, 1)], restore=False) as rep:
        pass
    assert sw.values["GetUserPreferenceIntegerValue:78"] == 1
    assert rep.kept and "restore=False" in rep.kept[0]["note"], rep.as_dict()


def test_read_failure_does_not_write_garbage() -> None:
    """★★ 读不到旧值 ⇒ **那一条不写**（★ 否则会把"读不到"变成"写了个错的旧值回去"）。"""
    sw = _sw()
    sw.fail_get_for.add(78)
    with preference_guard(sw, [Preference("integer", 78, 1)]) as rep:
        pass
    assert rep.read_errors, "★ 读失败要如实报"
    assert "SetUserPreferenceIntegerValue" not in sw.calls, (
        "★ 读不到旧值却写了新值 ⇒ 那条设置就永远回不去了：%r" % sw.calls)


def test_restore_failure_is_visible_not_swallowed() -> None:
    """★★ 还原失败 **必须可见**（★ 事实 517：不把失败写成成功）。

    ★ 造法：★ 让**第一次写成功、还原那一次失败** —— ★ 否则测不到这条（第一版就是那样漏掉的）。
    """
    sw = _sw()
    sw.fail_second_set_for.add(78)
    with preference_guard(sw, [Preference("integer", 78, 1)]) as rep:
        assert sw.values["GetUserPreferenceIntegerValue:78"] == 1
    d = rep.as_dict()
    assert d["ok"] is False and d["restore_errors"], d


def test_set_failure_is_reported_separately_and_nothing_is_left_changed() -> None:
    """★ **设都设不上** ⇒ 记进 `set_errors`（★ 不是 `restore_errors`），★ 且没留下改动。"""
    sw = _sw()
    sw.fail_set_for.add(78)
    with preference_guard(sw, [Preference("integer", 78, 1)]) as rep:
        pass
    d = rep.as_dict()
    assert d["set_errors"] and not d["changed"], d
    assert sw.values["GetUserPreferenceIntegerValue:78"] == 0, "★ 没设上却变了"


def test_unknown_kind_is_rejected() -> None:
    """★ 类别写错 ⇒ **抛**（★ 不静默按别的类别写 —— 那会改错设置）。"""
    try:
        Preference("stringgg", 1, "x")
    except ValueError as exc:
        assert "kind" in str(exc)
    else:
        raise AssertionError("★ 非法 kind 没被拒")


# ── 直接运行 ──────────────────────────────────────────────────────────────

def _main() -> int:
    fails = []
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("  [ok] %s" % name)
            except AssertionError as exc:
                fails.append(name)
                print("  [FAIL] %s: %s" % (name, exc))
    print("★ %d 条失败" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(_main())
