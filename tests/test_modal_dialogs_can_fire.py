"""★★★ 证明「查残留模态框」的判据**真的能响**（事实 62：负例是唯一的证明）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_modal_dialogs_can_fire.py
# 定位:   轮 148/149 把判据改成「不过滤可见性 + 返回总数」，但**只证明了"在扫"**
#         （窗口数 1 → 49）—— **没有证明它真能抓到一个模态框**。
#         ★ 本文件起一个**真的 `#32770`**（靶子）去抓，并**同时演示旧判据会漏掉它**。
# 官方依据: 靶子见 `tools/fake_modal_dialog.py`（Win32 预定义对话框类 `#32770`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT))

TARGET = REPO_ROOT / "tools" / "fake_modal_dialog.py"


def _spawn_target():
    """起靶子进程，返回 `(proc, pid)`；失败返回 `(None, None)`。"""
    proc = subprocess.Popen([sys.executable, str(TARGET)],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace")
    pid = None
    deadline = time.time() + 15
    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            break
        if line.startswith("PID="):
            pid = int(line.split()[0].split("=")[1])
            break
    return proc, pid


def test_the_check_can_actually_find_a_real_dialog():
    """@brief ★★★ 造一个**真 `#32770`** ⇒ 判据必须抓到它。

    ⚑ 这是**事实 62** 那条纪律的落点：**判据必须能被负例（这里是被正例）证伪/证实**。
    """
    if not TARGET.is_file():
        import pytest
        pytest.skip("靶子脚本不在")
    proc, pid = _spawn_target()
    if pid is None:
        proc.kill()
        import pytest
        pytest.skip("靶子起不来（环境不支持建窗口）")
    try:
        import sw_connect
        #: ★ 给它一点时间让窗口真的建出来
        time.sleep(0.5)
        dialogs, total = sw_connect.residual_dialogs(pid)
        assert total > 0, "连靶子进程的窗口都没扫到 ⇒ 判据根本没在看"
        assert any("假模态框" in d for d in dialogs), (
            "★ **判据没抓到那个真的 `#32770`**：dialogs=%r（扫了 %d 个窗口）"
            % (dialogs, total))
    finally:
        proc.kill()
        try:
            proc.wait(timeout=10)
        except Exception:      # noqa: BLE001
            pass


def test_the_old_visibility_filter_would_miss_it():
    """@brief ★★★ **对照**：旧的「只可见」口径**会漏掉**那个模态框。

    ⚑ 靶子窗口**故意不置 `WS_VISIBLE`** —— 这正是旧判据的失效模式：
    ```
    旧口径（only_visible=True） ⇒ 扫不到它 ⇒ **会报「无残留」**
    新口径（默认）              ⇒ 抓得到   ⇒ **报得出来**
    ```
    ⇒ ★ 这条把"漏检"从一个**说法**变成了**可复现的演示**。
    """
    if not TARGET.is_file():
        import pytest
        pytest.skip("靶子脚本不在")
    proc, pid = _spawn_target()
    if pid is None:
        proc.kill()
        import pytest
        pytest.skip("靶子起不来")
    try:
        import sw_connect
        time.sleep(0.5)
        new_dialogs, new_total = sw_connect.residual_dialogs(pid)
        old_dialogs, old_total = sw_connect.residual_dialogs(pid, only_visible=True)
        assert any("假模态框" in d for d in new_dialogs), "新口径应当抓到"
        assert not any("假模态框" in d for d in old_dialogs), (
            "★ 旧口径竟然也抓到了 —— 那说明靶子窗口是可见的，本对照不成立"
            "（old=%r, new=%r）" % (old_dialogs, new_dialogs))
        #: ★ 两个口径的**窗口总数**也要能看出差别（旧口径更少）
        assert old_total <= new_total, "旧口径的窗口数不该比新口径多"
    finally:
        proc.kill()
        try:
            proc.wait(timeout=10)
        except Exception:      # noqa: BLE001
            pass
