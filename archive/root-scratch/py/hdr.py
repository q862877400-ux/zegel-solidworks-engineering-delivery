from pathlib import Path
J = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_gui.py")
C = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_capture.py")

hdr_j = '''r"""嘉立创 FA 选型插件的 GUI 自动化 —— 实测跑通全链路（2026-09-30）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机已安装并实测驱动）
# 定位:   用脚本驱动插件完成「搜索型号 -> 选参数 -> 生成预览」，
#         产出真实 .SLDPRT 到插件 BuildFile 目录。
#
# ⚑ 已实测跑通的完整链路
# ----------------------------------------
#   找窗口(按进程名) -> 拖动面板刷新 -> 点插件标签(第 9 个 JLC)
#   -> 颜色扫描量搜索框 -> 输入型号 -> 回车 -> 点结果卡
#   -> 等参数页加载 -> 点「生成预览」 -> **文件落盘**
#   实测产出：经济型法兰型直线轴承 引导式 双衬(E-LMHP13LUU).SLDPRT  133.3 KB
#   cadmpeg 复核：format: sldprt (detected high)，entries: 61
#
# ⚑⚑ 本轮踩的七个坑（详见各函数注释）
# --------------------------------------
# 1. 拖动幅度过大会把 SolidWorks 拖到最小化（rect 变 -32000）→ ensure_window() 断言
# 2. 不能用「标签列坐标」当搜索框坐标（实测偏 97 像素）→ 颜色扫描量白底矩形
# 3. 窗口标题不能用来过滤（浏览器标签页标题也含 SolidWorks）→ 按进程名 sldworks.exe
# 4. pywin32 的 win32ui 不含 GDI 绘图函数 → 截图走 ctypes（见 sw_capture.py）
# 5. ctypes 不声明 restype/argtypes 报 "int too long to convert"（64 位句柄）
# 6. 拖动不能代替滚轮（WinForms Panel 不响应拖动滚动）→ MOUSEEVENTF_WHEEL
# 7. 参数太复杂的型号跑不通（带【去填写】的空规格段填不满时按钮禁用）
#
# ⚠ 已知不足（未解决，勿当已支持）
# ----------------------------------
# · 带【去填写】空规格段的型号**跑不通**（插件面板可能比窗口宽，右侧在屏幕外）
# · 每个坐标都要重新量（布局会变），不能硬编码
# · 插件内部子控件读不到，只能按坐标点
#
# 覆盖:   后续同级定义
# ⚠ 本模块会**驱动 GUI 并操作 SolidWorks**，调用方须先读上方「已知不足」。
# ────────────────────────────────────────────────────────────────────
"""
'''
s = J.read_text(encoding="utf-8")
s = hdr_j + s[s.index("from __future__"):]
J.write_text(s, encoding="utf-8")

hdr_c = '''r"""不受遮挡地抓取窗口内容（ctypes 直接调 GDI + PrintWindow）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 定位:   GUI 验证的取证手段 —— 截图必须是**窗口自身**的缓冲，不是屏幕区域。
#
# ⚑ 为什么不能用 ``ImageGrab.grab(bbox)``
# ----------------------------------------
# bbox 是**屏幕坐标**，被遮挡时抓到的就是**遮挡物**。
# 本轮实测：SolidWorks 被浏览器盖住时，截出来是浏览器（QwenCloud 定价页）。
# ⇒ 必须用 ``PrintWindow(hwnd, hdc, PW_RENDERFULLCONTENT)`` 抓窗口自身。
#
# ⚑⚑ pywin32 的 ``win32ui`` **不含** GDI 绘图函数（没有 CreateCompatibleDC），
#   所以这里全用 ctypes 调 user32/gdi32。
# ⚑⚑ 64 位下 GDI/USER 句柄是 64 位，ctypes 默认按 32 位 ⇒ 报
#   "int too long to convert"，必须逐个按真实签名声明 restype/argtypes
#   （**不要统一套**，各函数参数个数不同，套错会让调用错位）。
#
# 覆盖:   后续同级定义
# ⚠ 只读操作（不点击、不输入），不连接 SolidWorks。
# ────────────────────────────────────────────────────────────────────
"""
'''
s = C.read_text(encoding="utf-8")
s = hdr_c + s[s.index("import ctypes"):]
C.write_text(s, encoding="utf-8")
import ast
for f in (J, C):
    ast.parse(f.read_text(encoding="utf-8"))
    print("  %s OK" % f.name)