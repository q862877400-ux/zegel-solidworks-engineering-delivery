"""@brief 环境坑门禁的契约测试（**含负例**）。

# ── 来源 ──
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_env_pitfalls_gate.py
# 定位:   给 `scripts/check_env_pitfalls.py`（轮 46 新增的**硬门禁**）补契约测试。
#         ⚠ 按本仓库纪律：**门禁必须有负例**（「一个存在但没人用的守卫与没有守卫等价」，
#         且「检查量太少本身就是假绿」）——
#         所以这里既断言**当前树是干净的**，也**故意种坏样本**断言它会被抓。
# 官方签名依据: 不适用（纯静态检查 + Python 标准库 `subprocess` / `pathlib` 语义）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location(
        "check_env_pitfalls", ROOT / "scripts" / "check_env_pitfalls.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_env_pitfalls"] = mod
    spec.loader.exec_module(mod)
    return mod


MOD = _load()


def test_current_tree_is_clean() -> None:
    """当前树里不该有环境坑（否则门禁该红）。"""
    assert MOD.main(["--root", str(ROOT)]) == 0


def test_missing_encoding_is_detected(tmp_path: Path) -> None:
    """★ **负例**：`subprocess(..., text=True)` 缺 `encoding=` 必须被抓（事实 58）。"""
    d = tmp_path / "scripts"
    d.mkdir()
    (d / "bad.py").write_text(textwrap.dedent('''
        import subprocess
        def go():
            return subprocess.run(["echo", "hi"], capture_output=True, text=True, check=False)
    ''').lstrip(), encoding="utf-8")
    hits = MOD.find_missing_encoding(d / "bad.py")
    assert len(hits) == 1, hits
    assert hits[0][0] == 3                      # 行号要准


def test_present_encoding_is_not_flagged(tmp_path: Path) -> None:
    """有 `encoding=` 就不该报（**防假阳性**）。"""
    d = tmp_path / "scripts"
    d.mkdir()
    (d / "ok.py").write_text(textwrap.dedent('''
        import subprocess
        def go():
            return subprocess.run(["echo", "hi"], capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", check=False)
    ''').lstrip(), encoding="utf-8")
    assert MOD.find_missing_encoding(d / "ok.py") == []


def test_drive_only_root_is_detected(tmp_path: Path) -> None:
    """★ **负例**：`Path("D:") / "x"` 必须被抓（事实 59）。"""
    d = tmp_path / "scripts"
    d.mkdir()
    (d / "bad.py").write_text(textwrap.dedent('''
        from pathlib import Path
        for drive in ("D:", "E:"):
            root = Path(drive)
            for candidate in (root / "AutoCAD 2024" / "acad.exe",):
                pass
    ''').lstrip(), encoding="utf-8")
    hits = MOD.find_drive_only_root(d / "bad.py")
    assert len(hits) == 1, hits
    # ⚠ `textwrap.dedent(...).lstrip()` 去掉了首行空行 ⇒ `root = Path(drive)` 在**第 3 行**
    #   （第一版我写成 4 ⇒ 测试自己错了，不是检测器错。**先读清契约再写负例。**）
    assert hits[0][0] == 3


def test_drive_root_with_slash_is_not_flagged(tmp_path: Path) -> None:
    """`Path(drive + "/")` 是**修好之后**的写法，不该报。"""
    d = tmp_path / "scripts"
    d.mkdir()
    (d / "ok.py").write_text(textwrap.dedent('''
        from pathlib import Path
        for drive in ("D:", "E:"):
            root = Path(drive + "/")
            for candidate in (root / "AutoCAD 2024" / "acad.exe",):
                pass
    ''').lstrip(), encoding="utf-8")
    assert MOD.find_drive_only_root(d / "ok.py") == []


def test_comments_and_strings_are_skipped(tmp_path: Path) -> None:
    """★★ **这是本会话踩过两次的坑（事实 60）**：说明文字里的示例**不能被当真调用**。

    把 `subprocess.run(..., text=True)` 写进**注释**与**字符串**里，门禁必须**看不见**它。
    """
    d = tmp_path / "scripts"
    d.mkdir()
    (d / "doc.py").write_text(textwrap.dedent('''
        # 说明：以前的写法是 subprocess.run(cmd, text=True) 缺 encoding=，会炸。
        DOC = "subprocess.run(cmd, text=True)"
        def go():
            pass
    ''').lstrip(), encoding="utf-8")
    assert MOD.find_missing_encoding(d / "doc.py") == []


def test_balanced_call_not_truncated_at_first_paren(tmp_path: Path) -> None:
    """★★ **事实 58 的假阳性来源**：按「第一个 `)`」截断会把**本来有 encoding=** 的

    多行调用误判。⇒ 这里断言一个**参数里含括号**的调用能被正确判为「有 encoding=」。
    """
    d = tmp_path / "scripts"
    d.mkdir()
    (d / "nested.py").write_text(textwrap.dedent('''
        import subprocess
        def go():
            return subprocess.run([sys.executable, str(p)], capture_output=True,
                                  text=True, encoding="utf-8", errors="replace", check=False)
    ''').lstrip(), encoding="utf-8")
    assert MOD.find_missing_encoding(d / "nested.py") == []


# ── ③ `x or <默认值>` 吞掉合法 0（2026-10-01 轮 61 加）─────────────────────

def test_falsy_zero_default_is_detected(tmp_path: Path) -> None:
    """★ **负例**：`int(get_com_member(x, "CostingType") or -1)` ⇒ 必须被抓到。

    ⚠ 这是**真机抓到的真缺陷**：`CostingType` 真值为 `0` 时被吞成 `-1`
    （把「机加工」误报成「未知」）。修复后真机复测 `costing_type == 0`。
    """
    p = tmp_path / "m.py"
    p.write_text('x = int(get_com_member(a, "CostingType") or -1)\n', encoding="utf-8")
    hits = MOD.find_falsy_zero_default(p)
    assert hits and hits[0][1] == "CostingType" and hits[0][2] == "-1", hits


def test_falsy_zero_idempotent_defaults_are_not_flagged(tmp_path: Path) -> None:
    """★★ **假阳性守卫**：`or 0` / `or 0.0` / `or ""` 是**幂等**的 ⇒ **不该报**。

    ⚠ 我第一版把 `or 0.0` 也标成有害 ⇒ **假阳性**（本项目纪律：「门禁首跑必然有假阳性
    ⇒ 必须用真实数据核对」，那次是**我自己**撞上的）。
    判据只有一条：**默认值 ≠ 该类型的 falsy 值** 才有害。
    """
    p = tmp_path / "m.py"
    p.write_text(
        'a = int(get_com_member(x, "GetBodyCount") or 0)\n'
        'b = float(get_com_member(x, "GetMaterialCost") or 0.0)\n'
        'c = str(get_com_member(x, "CurrencyCode") or "")\n',
        encoding="utf-8")
    assert MOD.find_falsy_zero_default(p) == []


def test_falsy_zero_baseline_is_not_stale() -> None:
    """**基线自检**：基线里的键**必须仍然存在于代码里**（否则基线自己在腐坏）。

    ⚠ 这条把「修好了但忘了删基线」变成**可见**的事 —— 否则基线会越来越长，
    最终没人知道哪些是真存量。
    """
    baseline = MOD.load_falsy_zero_baseline()
    assert baseline, "基线文件为空或不存在"
    now = set()
    for d in MOD.SCAN_DIRS:
        dd = MOD.ROOT / d
        if not dd.is_dir():
            continue
        for f in dd.rglob("*.py"):
            if ".git" in f.parts:
                continue
            rel = f.relative_to(MOD.ROOT).as_posix()
            for _ln, member, _default in MOD.find_falsy_zero_default(f):
                now.add("%s:%s" % (rel, member))
    stale = sorted(baseline - now)
    assert not stale, "基线下这些键已不存在（修好了就删掉）：%s" % stale

# ── ④ `keybd_event` 按下必须被 `finally` 抬起（2026-10-01 轮 62 加）─────────

def test_unguarded_keypress_is_detected(tmp_path: Path) -> None:
    """★ **负例**：按下 → `sleep` → 抬起，**没有 `finally`** ⇒ 必须被抓到。

    ⚠ 这是**用户 2026-10-01 实报现象**的可能机制：`sleep` 可被中断
    ⇒ 抬起永远到不了 ⇒ **Ctrl/Alt/Enter 卡在按下态**
    ⇒ 之后按 `A` 就是 `Ctrl+A` = **全选（蓝底）**；Alt 卡住则菜单被激活。
    """
    p = tmp_path / "m.py"
    p.write_text(
        "import time, win32api, win32con\n"
        "def bad():\n"
        "    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)\n"
        "    time.sleep(0.03)\n"
        "    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)\n",
        encoding="utf-8")
    hits = MOD.find_unguarded_keypress(p)
    assert [h[1] for h in hits] == ["bad"], hits


def test_guarded_keypress_is_not_flagged(tmp_path: Path) -> None:
    """★★ **假阳性守卫**：按下在 `try`、抬起在 `finally` ⇒ **不该报**。

    ⚠ 这条必须有 —— 否则修好的代码会被门禁自己反复打回（「把判据改坏去迁就实现」的反面）。
    """
    p = tmp_path / "m.py"
    p.write_text(
        "import time, win32api, win32con\n"
        "def good():\n"
        "    win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)\n"
        "    try:\n"
        "        time.sleep(0.1)\n"
        "    finally:\n"
        "        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)\n",
        encoding="utf-8")
    assert MOD.find_unguarded_keypress(p) == []


def test_safe_primitive_call_is_exempt(tmp_path: Path) -> None:
    """★ **豁免守卫**：调 `_press` / `_hold` 的地方**不该报**（原语内部已保证抬起）。"""
    p = tmp_path / "m.py"
    p.write_text(
        "def ok(gi, vk):\n"
        "    gi._press(vk)\n"
        "    gi._hold([1], vk)\n",
        encoding="utf-8")
    assert MOD.find_unguarded_keypress(p) == []


def test_current_tree_has_no_unguarded_keypress() -> None:
    """★ 当前仓库必须 **0 个**未设防的按下（本轮把 7 处全修了）。"""
    bad = []
    for d in MOD.SCAN_DIRS:
        dd = MOD.ROOT / d
        if not dd.is_dir():
            continue
        for f in dd.rglob("*.py"):
            if ".git" in f.parts:
                continue
            for ln, fn in MOD.find_unguarded_keypress(f):
                bad.append("%s:%d %s" % (f.relative_to(MOD.ROOT), ln, fn))
    assert not bad, "未设防的 keybd_event 按下：%s" % bad