import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── ① 给 sw_connect 加**只读**检测（把"发现"与"点掉"分开）──────────
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_connect.py")
t = P.read_text(encoding="utf-8")
NEW = '''

def count_residual_dialogs(target, *, settle_seconds=0.0, poll_ms=200):
    """★ **只读**检测残留模态框（**不点掉任何东西**）。

    ⚠ 与 `dismiss_residual_dialogs` 分开，是为了让调用方能**分别报告**
    「**发现**了几个」与「**点掉**了几个」—— 2026-10-01（轮 167）实测时把两者混在一个
    计数里，读日志时误判成「没点掉」。**发现与处置是两件事，计数也要分开。**
    """
    import time
    pid = _resolve_pid(target)
    best = (0, 0)
    deadline = time.time() + max(0.0, float(settle_seconds))
    while True:
        handles, total = _dialog_handles(pid)
        if len(handles) > best[0]:
            best = (len(handles), total)
        if time.time() >= deadline:
            break
        time.sleep(max(0.02, poll_ms / 1000.0))
    return best
'''
if "def count_residual_dialogs(" not in t:
    t = t.replace("def dismiss_residual_dialogs(", NEW.strip() + "\n\n\ndef dismiss_residual_dialogs(", 1)
    P.write_text(t, encoding="utf-8")
    ast.parse(t)
    print("  ok ① count_residual_dialogs 已加（只读检测）")

# ── ② 验证脚本：复现改**空零件** + 发现/点掉分开计数 ────────────────
P2 = Path(r"C:\swprojects\sw-skill-fork\tools\verify_modal_dialog_lifecycle.py")
t2 = P2.read_text(encoding="utf-8")
#: ⚠ 原复现建了实体 ⇒ **有实体的零件上不弹框**（实测）⇒ 改成**空零件**（那才是根因场景）
t2 = t2.replace('''doc = sw_connect.new_document(sw, "part")
sw_part.start_sketch(doc)
sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, 50.0, 30.0)
sw_part.end_sketch(doc)
sw_part.extrude_boss(doc, "草图1", 10.0)
print("TRIGGER: 有实体的零件已建好", flush=True)''',
'''doc = sw_connect.new_document(sw, "part")
#: ⚠⚠⚠ **必须用空零件** —— 轮 167 实测：**有实体**的零件上 SolidWorks 能自己推断方向
#: ⇒ **不会弹框**（第一次复现因此失败：「竟然没弹框就返回了」）；
#: 而**空零件**上无方向可推断 ⇒ 才会弹「此拔模方向尚未定义。」
print("TRIGGER: 空零件已建好（**故意的**）", flush=True)''')
#: 发现/点掉分开
t2 = t2.replace('''    found_at = None
    t0 = time.time()
    while time.time() - t0 < 45.0:
        d, scanned = sw_connect.dismiss_residual_dialogs(sw, settle_seconds=0.0)
        if d:
            found_at = time.time() - t0
            ev["found_after_seconds"] = round(found_at, 2)
            ev["scanned_windows"] = scanned
            print("  ③ ★ 第 **%.1f 秒** 发现模态框（扫了 %d 个窗口）" % (found_at, scanned))
            break
        time.sleep(0.25)''',
'''    found_at = None
    t0 = time.time()
    while time.time() - t0 < 45.0:
        n_dlg, scanned = sw_connect.count_residual_dialogs(sw)      #: ★ **只读**，不点
        if n_dlg:
            found_at = time.time() - t0
            ev["found_after_seconds"] = round(found_at, 2)
            ev["found_count"] = n_dlg
            ev["scanned_windows"] = scanned
            print("  ③ ★ 第 **%.2f 秒** **发现** %d 个模态框（扫了 %d 个窗口）"
                  % (found_at, n_dlg, scanned))
            break
        time.sleep(0.25)''')
P2.write_text(t2, encoding="utf-8")
ast.parse(t2)
print("  ok ② 验证脚本已改（空零件复现 + 发现/点掉分开计数）")
