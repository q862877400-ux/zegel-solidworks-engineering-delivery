import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

DOC = """# 脚本层的单位声明 —— **没有可机器化的守卫**

> 来源：`tools/probe_unit_declarations.py`（2026-10-01 轮 133，Spec Kit `052`）
> ⚠⚠ **结论：做不成门禁。** 理由见下 —— 而且这次的假阳性率是 **4/4**。

## 一、起因
`051`（轮 132）实测发现 `scripts/sw_part.py` 的 **14 处** docstring 写「单位: 米」，
而**实际是毫米**（半径 25 的圆 ⇒ 边界框跨度 50）。
★ 关键不是"写错了"，而是：**脚本层的单位声明没有任何机器约束** ——
工具层有「并入六条规则」的规则 2（参数名 `_mm` 后缀 + `mm()` 换算）守着，
**脚本层不受那条规则约束**。

⇒ 本轮去试：能不能给脚本层也装一个。

## 二、判法（**有界、可复核**，不是"聪明的启发式"）
```
① 显式的**长度词表**：radius / diameter / depth / thickness / distance / width / height /
   length / offset / spacing / pitch / cx / cy / cz / dx / dy / dz / x1 y1 z1 x2 y2 z2 / size
② 某模块的**公开函数**里出现这些**形参名** ⇒ 认为它"带长度参数"
③ 看它的源码里有没有**单位声明**（`单位` / `毫米` / `米` / `mm` / `meter` …）
```
结果：**带长度参数且已声明单位 10 个 · 一处都没声明 4 个**。

## 三、★★ 那 4 个**逐条人工看** —— **4/4 全是假阳性**
| 模块 | 命中词 | 真相 |
|---|---|---|
| `sw_costing.set_lot_size(cost_analysis, lot_size)` | `lot_size` | **批量大小**（件数），**不是长度** |
| `sw_jlcfa_gui.drag(x1,y1,x2,y2)` | `x1 y1 x2 y2` | **屏幕坐标**（文件里有「屏幕」）|
| `sw_jlcfa_gui.find_node(root,name,depth,maxd)` | `depth` | **树的深度** |
| `sw_jlcfa_select.crop_region(img,rect,dx,dy,w,h)` | `dx dy` | **像素**（文件里有「像素」）|
| `sw_view.set_view_frame(view,left,top,width,height)` | `width height` | **窗口几何**（像素）|
| `sw_view.translate_view(view,dx,dy)` | `dx dy` | **像素** |

⇒ ★★ **假阳性率 4/4 = 100%** —— 比本项目此前几次都高
（`029` 26% · `032` 50% · `037` 59%）。

## 四、★★ 为什么这次**根本做不成**
```
`size` / `depth` / `width` / `dx` 这些词，在**非几何**语境里同样常用：
    批量大小（lot_size）· 树的深度（depth）· 窗口宽度（width）· 屏幕偏移（dx/dy）
⇒ ★ **「长度词表」无法区分「几何长度」与「同名的非几何量」** ——
  那是**语义**判断，不是词形判断。
⇒ 而若把词表缩小到"只认 radius/diameter"，那它就只能覆盖**一小撮**参数，
  **漏掉的比抓到的多** ⇒ 那种门禁的价值还不如它的维护成本。
```
★ 这也反过来解释了 `051` 那个错**为什么能活那么久**：
**不是没人管，而是"管不了"** —— 任何按名字的词表都**必然**把 `lot_size` / `depth` / `width` 卷进来。

## 五、处置
1. **不做成门禁**（假阳性 100%）；
2. 探针**保留**（`tools/probe_unit_declarations.py`）—— 它能给出**供人工扫一眼**的清单；
3. ⚠ **探针源码里写明"不下「该接门禁」的结论"**（免得下一个人拿它当判据）；
4. ★ **真正的守卫是"实测"**：`051` 那次能改对，**靠的是真机量了一遍**（圆 → 边界框），
   不是靠读代码 —— ⇒ **这就是脚本层单位唯一的可靠办法**。

## 六、可复用的认识（第 4 次强调同一类事）
```
本项目"按名字判有无/对错"的检查失败记录：
  020/021/022  核样：按名字分档，四档全要打折
  027          探针：连着两版假阳性
  029          废弃成员：38 条里 10 条假阳性（26%）⇒ 不成门禁
  032          废弃成员核完：20 条里 10 条（50%）⇒ 更不成门禁
  037          模块覆盖：两版全败（59%）**而且问错了问题**
  133          单位声明：**4/4（100%）**，且**根本做不成**（词形判不了语义）
```
★★ **这次的结论比前几次更硬**：前几次是"假阳性太多"，这次是
**「这个判据的原理就不成立」** —— 因为「是不是长度」**不在名字里**。
"""

P = Path(r"C:\swprojects\sw-skill-fork\docs\script-layer-units.md")
P.write_text(DOC, encoding="utf-8")
print("  ok 已写 docs/script-layer-units.md（%d 行）" % len(DOC.splitlines()))
