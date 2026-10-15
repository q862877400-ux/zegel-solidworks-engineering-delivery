r"""@brief 「你能亲眼看」的验证：**不压 UI**，跑完把零件留在屏幕上。

## 为什么要写这个
用户质疑：「静力学整链复现，我完全没看到屏幕上的变化 —— 是后台快，还是幻觉？」

**两个必须分开回答的问题**：
1. **为什么屏幕上没变化？** —— 因为探针都设了 `sw.CommandInProgress = True`
   （AGENTS.md 铁律 2 要求：抑制模态对话框，防无人值守挂起）。
   **副作用就是 SolidWorks 的 UI 不刷新**，所以看起来「什么都没发生」。
2. **它到底有没有真跑？** —— 这个问题**不能靠解释回答，只能靠可观察的证据**。

## 本脚本的设计（为「可观察」而写）
| 与既有探针的区别 | 为什么 |
|---|---|
| **不设** `CommandInProgress = True` | 让 SolidWorks 的 UI 正常刷新，人能看见 |
| 每一步之间 **sleep 2 秒** | 给肉眼留出观察窗口 |
| **跑完不关闭文档** | 零件留在屏幕上，用户可自己检查特征树与尺寸 |
| 把窗口 **置前**（`SetForegroundWindow`） | 确保 SolidWorks 在最前面，不会在后台被忽略 |
| 把关键事实**同时打印到控制台** | 控制台与屏幕**双通道**，任何一条为假都能互相揭穿 |

**⇒ 如果这个脚本跑完，SolidWorks 窗口里应该出现一个带拉伸凸台的零件，且特征树可查。**
**若屏幕上什么都没有，那才是真的没跑。**

# ── 来源 ──
# 仓库:   本项目自身（可观察性验证，非第三方移植）
# 文件:   D:\AI\SW\probe_visible.py
# 定位:   AGENTS.md「验证：报告只写真跑过的命令；『验证过』需要一次新鲜的运行」
#         与「证据优于断言：贴输出、贴命令、贴返回值」。
# 官方签名依据: 不适用（本脚本不引入新 COM 成员，只用既有辅助函数）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机，**故意不压 UI**（与其它探针相反，见上表）。文档**不保存**、
#   **不关闭**（留给用户看；用户看毕可自行关闭，或由下一次运行清理）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part, sw_simulation as sim  # noqa: E402


def beep(n: int = 1) -> None:
    """出声提示 —— 让「正在发生」这件事有听觉通道。"""
    try:
        import winsound
        for _ in range(n):
            winsound.Beep(880, 220)
            time.sleep(0.08)
    except Exception:
        print("\a", end="", flush=True)


def main() -> int:
    print("=" * 64)
    print("【可观察验证】接下来每一步都会在 SolidWorks 窗口里**看得到**")
    print("  · 不设 CommandInProgress（UI 会刷新）")
    print("  · 每步之间停 2 秒")
    print("  · 跑完**不关文档**，零件留在屏幕上")
    print("=" * 64, flush=True)

    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    print("[0] 已连上 SolidWorks；当前文档: %r"
          % (get_com_member(sw, "ActiveDoc") is not None), flush=True)

    # 把 SolidWorks 窗口置前
    try:
        import win32gui
        hwnd = win32gui.FindWindow(None, "SOLIDWORKS Design Premium 2026 SP4.1")
        if not hwnd:
            hwnd = win32gui.FindWindow(None, "SOLIDWORKS")
        if hwnd:
            win32gui.ShowWindow(hwnd, 3)          # SW_MAXIMIZE
            win32gui.SetForegroundWindow(hwnd)
            print("    已把 SolidWorks 窗口置前（hwnd=%d）" % hwnd, flush=True)
            beep(2)
        else:
            print("    ⚠ 没找到窗口句柄（不影响后续，只是看不到置前效果）", flush=True)
    except Exception as exc:
        print("    窗口置前失败（不影响功能）: %s" % str(exc)[:60], flush=True)

    time.sleep(2)

    # ── ① 新建零件（屏幕上应出现新文档标签）──
    print()
    print(">>> 第 1 步：新建零件 —— 请看 SolidWorks，应出现一个新文档标签", flush=True)
    beep()
    model = new_document(sw, doc_type="part")
    title = get_com_member(model, "GetTitle")
    print("    控制台报告标题 = %r" % title, flush=True)
    time.sleep(2)

    # ── ② 画矩形（屏幕上应出现草图）──
    print()
    print(">>> 第 2 步：在前视基准面画 100×60 矩形 —— 屏幕应进入草图并出现矩形", flush=True)
    beep()
    sk = sw_part.sketch(model, "Front Plane")
    sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
    time.sleep(2)

    # ── ③ 拉伸 20mm（屏幕上应出现实体）──
    print()
    print(">>> 第 3 步：拉伸 20 mm —— 屏幕应出现一个长方体实体", flush=True)
    beep()
    sw_part.extrude_boss(model, sk, 0.02)
    time.sleep(2)

    # ── ④ 读回几何（独立于屏幕的自证：质量属性来自 SolidWorks 自己算的）──
    print()
    print(">>> 第 4 步：让 SolidWorks 自己报出几何（这是它算的，不是我编的）", flush=True)
    try:
        ext = get_com_member(model, "Extension")
        mp = get_com_member(ext, "GetMassProperties2", 1, 0, False)
        if mp:
            print("    体积 = %.9g m³ = %.1f mm³（理论 100×60×20 = 120000 mm³）"
                  % (mp[3], mp[3] * 1e9), flush=True)
            print("    表面积 = %.9g m² = %.1f mm²" % (mp[4], mp[4] * 1e6), flush=True)
            print("    质心 = (%.4f, %.4f, %.4f) m" % (mp[0], mp[1], mp[2]), flush=True)
    except Exception as exc:
        print("    ✗ 取质量属性失败: %s" % str(exc)[:70], flush=True)

    print()
    print("=" * 64)
    print("【请你看屏幕】现在 SolidWorks 里应该有一个：")
    print("  · 标题为 %r 的零件文档" % title)
    print("  · 特征树里有「凸台-拉伸1」" % ())
    print("  · 视口里有一个 100×60×20 mm 的长方体")
    print("  · 尺寸由 SolidWorks 自己量（上面第 4 步的体积是它算的）")
    print()
    print("⚠ 文档**保持打开、未保存** —— 请你自己看一眼确认。")
    print("   若屏幕上**什么都没有**，那就是我幻觉了，请直接告诉我。")
    print("=" * 64, flush=True)
    beep(3)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
