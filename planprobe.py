import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.loads(Path(r"C:\swprojects\sw-skill-fork\scripts\jlcfa_index.json").read_text(encoding="utf-8"))
want = ["直线导轨","滚珠丝杠","同步轮","联轴器","平皮带/圆皮带","带座轴承",
        "风琴罩","机床防护罩","导向轴","花键","拖链","位移台","直线轴承",
        "无油衬套","交叉滚子导轨/滑台","链轮/链条","V带·V带轮","滑轮/惰轮"]
for w in want:
    hits=[p for p in d["parts"] if w in (p["category"] or [])]
    print("%-18s %4d 个  例: %s" % (w, len(hits), [h["code"] for h in hits[:3]]))