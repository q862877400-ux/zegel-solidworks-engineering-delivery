import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_gtol.py")
t = P.read_text(encoding="utf-8")
# 在 add_gtol_indicator 之前插入两个新函数
anchor = "def add_gtol_indicator(gtol, *, tol_type, datum: str = \"\","
NEW = '''def add_gtol_frame(gtol):
    """给 Gtol **加一帧**（官方 `IGtol.AddFrame()`，**0 参**）。

    ⚑ **为什么必须有这个函数**（**轮 120 真机冒烟查出来的**）：
    `InsertGtol()` 建出来的是**空符号**，`GetFrameCount()` 是 **0** ⇒
    **直接 `GetFrame(1)` 会返回 `None`**（轮 119 的实现就栽在这里）。
    ⇒ 必须先 `AddFrame()` 才能取到第 1 帧。
    官方 Remarks：本方法**只对 SW 2022 及以后建的 Gtol 有效**。

    :returns: `True`。
    :raises RuntimeError: 官方返回 `False`。
    """
    got = get_com_member(gtol, "AddFrame")
    if got is None or not got:
        raise RuntimeError(
            "IGtol.AddFrame() 返回 False（失败）—— 官方：本方法**只对 SW 2022 及以后建的 Gtol 有效**"
        )
    return True


def ensure_gtol_frame(gtol, frame: int = FIRST_FRAME):
    """确保第 `frame` 帧**存在**（不够就 `AddFrame()` 补到够）。

    ⚠ 本函数**会改 Gtol 的状态**（加帧）—— 这是**有意**的，因为：
    新 Gtol 的 `GetFrameCount()` 是 **0**，**不加帧就取不到任何帧**。

    :returns: 补完后 `GetFrameCount()` 的读数。
    """
    want = int(frame)
    if want < 1:
        raise ValueError("frame 是 **1 基**，不能小于 1（收到 %r）" % frame)
    have = int(get_com_member(gtol, "GetFrameCount") or 0)
    while have < want:
        add_gtol_frame(gtol)
        new = int(get_com_member(gtol, "GetFrameCount") or 0)
        if new <= have:
            raise RuntimeError(
                "IGtol.AddFrame() 之后 `GetFrameCount()` 没涨（%d → %d）"
                " ⇒ 该 Gtol 可能不是 2022 格式" % (have, new)
            )
        have = new
    return have


'''
if "def add_gtol_frame" not in t:
    i = t.index(anchor)
    P.write_text(t[:i] + NEW + t[i:], encoding="utf-8")
    print("  ok 已插入 add_gtol_frame / ensure_gtol_frame")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
