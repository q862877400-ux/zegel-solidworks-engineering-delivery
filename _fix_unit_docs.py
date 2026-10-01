import ast
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_part.py")
before = P.read_text(encoding="utf-8")
n_before = len(before.splitlines())

#: 逐条精确替换（**只改长度类**；方向向量那处单列）
FIXES = [
    ('"""画直线（单位: 米）"""', '"""画直线（单位: **毫米**）"""'),
    ('"""以中心点画矩形（单位: 米）"""', '"""以中心点画矩形（单位: **毫米**）"""'),
    ('"""以对角线画矩形（单位: 米）"""', '"""以对角线画矩形（单位: **毫米**）"""'),
    ('"""画圆（单位: 米）"""', '"""画圆（单位: **毫米**）"""'),
    ("cx, cy: 圆心坐标（米）", "cx, cy: 圆心坐标（**毫米**）"),
    ("points: [(x1,y1), (x2,y2), ...] 控制点列表（单位: 米）",
     "points: [(x1,y1), (x2,y2), ...] 控制点列表（单位: **毫米**）"),
    ("depth: 拉伸深度（米）", "depth: 拉伸深度（**毫米**）"),
    ("depth: 切除深度（米），0 表示完全贯穿",
     "depth: 切除深度（**毫米**），0 表示完全贯穿"),
    ("total_depth: 总深度（米），每侧为 total_depth/2",
     "total_depth: 总深度（**毫米**），每侧为 total_depth/2"),
    ("radius: 圆角半径（米）", "radius: 圆角半径（**毫米**）"),
    ("distance: 倒角距离（米）", "distance: 倒角距离（**毫米**）"),
    ("thickness: 壁厚（米）", "thickness: 壁厚（**毫米**）"),
    ("thickness: 筋厚度（米）", "thickness: 筋厚度（**毫米**）"),
    # 方向向量那处：**不改**，改成"未测"标注（不假装知道）
    ("d1_*: 方向1 的方向向量、间距（米）和数量",
     "d1_*: 方向1 的方向向量、间距（**毫米**，⚠ 间距已测；**方向向量是否归一化未测**）和数量"),
]
t = before
done = 0
for old, new in FIXES:
    if old in t:
        t = t.replace(old, new, 1)
        done += 1
    else:
        print("  ⚠ 未命中: %s" % old[:56])

#: 加一段模块级说明，把"为什么改"留在源码里
HEAD = '''"""
SolidWorks 零件建模工具
提供草图绘制和特征创建的常用函数

⚠⚠ **长度单位：毫米**（2026-10-01 轮 132 实测校正）
本模块此前多处 docstring 写「单位: 米」——**与实际不符**。
实测（`tools/verify_ellipse_smoke.py`）：半径 **25** 的圆 ⇒ 边界框跨度 **50**（毫米）；
拉伸 **10** ⇒ 该方向跨度 **10**（毫米）。⇒ **传进去的就是毫米**，不要再换算。
★ 这与 `IBody2.GetBodyBox` 的返回单位一致（已知事实 71）。
"""'''
OLD_HEAD = '''"""
SolidWorks 零件建模工具
提供草图绘制和特征创建的常用函数
"""'''
if OLD_HEAD in t:
    t = t.replace(OLD_HEAD, HEAD, 1)
    print("  ok 已加模块级单位说明")

P.write_text(t, encoding="utf-8")
ast.parse(t)
n_after = len(P.read_text(encoding="utf-8").splitlines())
print("  替换 %d/%d 处 · 行数 %d -> %d" % (done, len(FIXES), n_before, n_after))
# ⚠ 事实 61：看 diff 有没有 deletions
r = subprocess.run(["git", "diff", "--stat", "--", "scripts/sw_part.py"],
                   capture_output=True, text=True, encoding="utf-8",
                   cwd=r"C:\swprojects\sw-skill-fork")
print("  git diff --stat: %s" % (r.stdout.strip() or "(空)"))
