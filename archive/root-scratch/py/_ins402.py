import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           402 🎯 **Spec Kit `065`：补 `export_image` —— 用****定量往返****取证**（轮 146）——
               ★ 本轮**刻意收窄**（前几轮动辄 3~4 个真缺陷、几十个文件）。
               入口 `IModelDoc2.SaveBMP(String, Int32, Int32) -> Boolean`：**三源一致**（铁律 4），
               签名干净（返回 `Boolean` ⇒ 成败可查），★ 而 **宽高是入参** ⇒ 能做**定量往返**。
            403 ★ **真机冒烟 8/8**：
               ```
               ✓ export_to_bmp(800x600) 未抛异常 · 文件 1440054 字节
               ✓ ★★ **定量往返**：BMP 头里的尺寸 == 800x600   ← 读回 (800, 600)（偏移 18/22，小端）
               ✓ ★ 官方 Remarks：宽高 ≤ 0 ⇒ 按窗口尺寸        读回 (1460, 1049)
               ✓ ★ 扩展名不是 .bmp ⇒ 明确拒绝（ValueError）
               ```
               ★ 与 `scripts/sw_capture.py` **分工**（**不重造**）：那个走 GDI `PrintWindow`
                 抓**窗口**、不受遮挡；本函数走 SolidWorks 自己的 `SaveBMP` 抓**当前视图**、
                 无需窗口在前台。
            404 ★★ **本轮真正的方法论收获：「入参里有没有可回读的量」决定证据强度**：
               ```
               弱证据（空操作也能满足）：没抛异常 · 文件存在 · 返回 True
               强证据（空操作满足不了）：★ **写进去的尺寸 == 读回来的尺寸**
               ⇒ ★ 挑任务时**先看官方签名里有没有"可回读的入参"** ——
                 有（宽高 / 角度 / 直径…）⇒ 能做定量往返；没有 ⇒ 只能找侧证（边界框 / 特征树）。
               ```
               ★ 这把 `040`（螺旋线 50mm ⇒ 读回 0.05）· `044`（反向验证）那一族的经验
                 **变成了选任务的准则**。
            405 ⚑ **一处主动收窄的边界**：官方 `SaveBMP` **只出 `.bmp`**；png/jpg 要走 `SaveAs`
               的图片过滤器 —— **本轮没查、没做** ⇒ 限度里写明，**不假装覆盖了全部格式**。
               ⚑ **未查证**：只证「尺寸按请求走 + 文件合法」，**不证画面内容**（不比对像素）；
                 ⚠ **无头环境下 `SaveBMP` 是否可用，未测**；png/jpg 那条路**未查**。
               已知事实 **86** 入库 · 回归 **1214 passed** · `release_check` exit 0。
               下轮候选：① 查 `SaveAs` 图片过滤器能不能出 png/jpg；② 回到「真缺」继续补；
               ③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+402 ", before, re.M):
    print("  游标 402 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+405 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 405 行已存在 ✓")
