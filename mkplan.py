import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.loads(Path(r"C:\swprojects\sw-skill-fork\scripts\jlcfa_index.json").read_text(encoding="utf-8"))
# 四大类 -> 库里对应分类
MAP = {
    "直线运动零件": ["直线导轨", "直线轴承", "光轴", "滚珠丝杠", "交叉滚子导轨"],
    "机床防护罩":   ["风琴罩", "防护罩"],
    "传动零部件":   ["同步轮", "联轴器", "平皮带", "V带", "齿轮"],
    "轴承附件":     ["带座轴承", "轴承", "联轴轴承", "轴承用"],
}
plan = []
for ui_cat, cats in MAP.items():
    codes = []
    for c in cats:
        for p in d["parts"]:
            if c in (p["category"] or []) and p["code"] not in codes:
                codes.append(p["code"])
            if len(codes) >= 4:
                break
        if len(codes) >= 4:
            break
    plan.append((ui_cat, codes[:3]))
print("抽查计划（型号全部来自真实库）:")
for cat, codes in plan:
    print("  %-10s -> %s" % (cat, codes))
Path(r"D:\AI\SW\audit_plan.py").write_text(
    "# -*- coding: utf-8 -*-\n"
    '"""抽查目标：四大类各 3 个差异大的零件（型号全部来自 sw_jlcfa_index.json 真实库）。"""\n\n'
    "TARGETS = " + repr(plan).replace("[", "[\n    ").replace("]", ",\n]") + "\n",
    encoding="utf-8")
print()
print("已写入 audit_plan.py")