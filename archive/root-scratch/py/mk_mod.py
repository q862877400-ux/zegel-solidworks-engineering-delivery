from pathlib import Path
import re
S = Path(r"D:\AI\SW")
src = (S / "jlc_auto.py").read_text(encoding="utf-8")
shot = (S / "shot.py").read_text(encoding="utf-8")
# 把 shot.py 的内容并进 jlc_auto.py 末尾（去重复的 import 头）
shot_body = shot[shot.index("import ctypes"):]
doc = '''r"""嘉立创 FA 选型插件的 GUI 自动化 —— 实测跑通全链路（2026-09-30）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机已安装并实测）
# 定位:   用脚本驱动插件完成「搜索型号 -> 选参数 -> 生成预览」，
#         产出真实的 .SLDPRT 到插件的 BuildFile 目录。
#
# ⚑ 已实测跑通的完整链路（2026-09-30）
# ----------------------------------------
#   找窗口(按进程名) -> 拖动面板刷新 -> 点插件标签(第 9 个 JLC)
#   -> 颜色扫描量搜索框 -> 输入型号 -> 回车 -> 点结果卡
#   -> 等参数页加载 -> 点「生成预览」 -> **文件落盘**
#   实测产出：经济型法兰型直线轴承 引导式 双衬(E-LMHP13LUU).SLDPRT  133.3 KB
#   cadmpeg 复核：format: sldprt (detected high)，entries: 61
#
# ⚑⚑ 本轮踩的七个坑（都写在代码注释里，别再踩第二遍）
# --------------------------------------------------------
# 1. **拖动幅度过大会把 SolidWorks 拖到最小化** —— 窗口 rect 变成
#    (-32000,-32000,...)，之后所有点击都落在屏幕外，
#    症状是「点搜索框没反应」，原因却离得很远 ⇒ 必须有 ensure_window() 断言。
# 2. **不能用「标签列坐标」当搜索框坐标**（实测偏了 97 像素）——
#    搜索框要用**颜色扫描**找白底矩形，量出真实位置。
# 3. **窗口标题不能用来过滤** —— 浏览器标签页标题
#    「SolidWorks Automation Skil — DSH 本地构建」也以 SolidWorks 开头，
#    实测抓到过 Edge ⇒ 改按**进程名 sldworks.exe** 过滤。
# 4. **pywin32 的 win32ui 不含 GDI 绘图函数**（没有 CreateCompatibleDC）——
#    截图必须 ctypes 直接调 gdi32/user32。
# 5. **ctypes 不声明 restype/argtypes 会报 "int too long to convert"** ——
#    64 位下 GDI 句柄是 64 位。⚠ 只设 restype，**不要统一套 argtypes**
#    （各函数参数个数不同，套错会让调用错位）。
# 6. **拖动不能代替滚轮** —— WinForms Panel 不会响应拖动滚动，
#    实测截图字节数完全一样 ⇒ 用 MOUSEEVENTF_WHEEL。
# 7. **参数太复杂的型号跑不通** —— 带【去填写】的空规格段填不完时
#    「生成预览」按钮是禁用的。⚠ 实测插件面板可能比窗口宽，
#    右侧内容在屏幕外（未解决，见下方「已知不足」）。
#
# ⚠ 已知不足（未解决，勿当已支持）
# ----------------------------------
# · 带【去填写】空规格段的型号**跑不通**（面板超宽，右侧在屏幕外）
# · 每个窗口坐标都需重新量（布局会变），不能硬编码
# · 选型是 GUI 控件，只能按坐标点；uiautomation 读不到插件内部子控件
#
# 覆盖:   后续同级定义
# ⚠ 本模块会**驱动 GUI 并启动/操作 SolidWorks**，
#   调用方须先阅读上方「实测跑通的完整链路」与「已知不足」。
# ────────────────────────────────────────────────────────────────────
"""
# 替换原文件的模块 docstring
body = src[src.index("from __future__"):]
body = body.replace("import shot", "from sw_gui_capture import capture_window  # noqa: F401")
Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_gui.py").write_text(doc + "\n" + body, encoding="utf-8")
print("  已写 scripts/sw_jlcfa_gui.py")