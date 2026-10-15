from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_cards.py")
s = p.read_text(encoding="utf-8")
# category_cards / locate_category 接受外部控件列表（避免再走一遍树）
s = s.replace("def category_cards(win) -> list[tuple[str, Any]]:",
              "def category_cards(win, allc=None) -> list[tuple[str, Any]]:")
s = s.replace('''    cr = L.container_rect(win)
    if cr is None:
        return []
    SKIP = {"swCaption", "SearchBox", "swCmdMgr", "swMenu", "任务窗格",
            "EM Frame", "header", "taskPaneConfig", "expandCollapse", "pin",
            "swInnerFrame", "Task Pane Tabs Wnd", "工作区", "设置"}
    out = []
    seen = set()
    for c in L._controls(w):''',
'''    if allc is None:
        allc = L._controls(win)
    cr = L.container_rect(win)
    if cr is None:
        return []
    out = []
    seen = set()
    for c in allc:''')
s = s.replace('        if not t or t in SKIP or t in seen:',
              '        if not t or t in SKIP_NAMES or t in seen:')
s = s.replace("def locate_category(win, name: str):",
              "def locate_category(win, name: str, allc=None):")
s = s.replace("    for t, r in category_cards(win):",
              "    for t, r in category_cards(win, allc):")
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("category_cards / locate_category 已支持传入控件列表")