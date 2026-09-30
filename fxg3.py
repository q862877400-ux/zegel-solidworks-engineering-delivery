from pathlib import Path
p = Path(r"D:\AI\SW\sw_gui.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''#: SolidWorks 主窗口标题包含该串（实测："SOLIDWORKS Design Premium 2026 SP4.1"）
TITLE_MATCH = "SOLIDWORKS"''',
'''#: SolidWorks 主窗口标题**必须以**该串开头。
#: ⚠⚑ 早先写成「包含」，结果抓到 Edge —— 它的标题里恰好含
#:    「SolidWorks Automation Skil - DSH 本地构建」=> 误判。
#:    教训：窗口匹配要**锚定开头**，不是子串包含。
TITLE_PREFIX = "SOLIDWORKS"''')
s = s.replace('if t and TITLE_MATCH in t.upper():',
              'if t and t.upper().startswith(TITLE_PREFIX):')
s = s.replace('    "TITLE_MATCH", "find_solidworks_window", "focus_window",',
              '    "TITLE_PREFIX", "find_solidworks_window", "focus_window",')
s = s.replace("import win32guiui", "import win32ui")
s = s.replace("win32guiui.", "win32ui.")
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("patched: TITLE_PREFIX + win32ui")