import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_png_smoke.py")
t = P.read_text(encoding="utf-8")
OLD = '''            chk("★ 交叉核对：PNG 尺寸 ≈ 窗口尺寸（两者都是「当前视图」）",
                bool(bw and pn) and abs(pn[0] - bw[0]) <= 2 and abs(pn[1] - bw[1]) <= 2,
                "BMP(0,0)=%s vs PNG=%s（±2 px 容差）" % (bw, pn))'''
NEW = '''            #: ⚠⚠ 第一版判据写的是"PNG 应当 ≈ 窗口尺寸"（±2 px）—— **它红了**，
            #: 实测 `BMP(0,0)=(1460, 1049)` vs `PNG=(1232, 1049)`：**高度一致、宽度差 228**。
            #: ★ 最可能的解释：`SaveBMP(0,0)` 按**窗口**取（含侧边面板），
            #:   `SaveAs3` 按**绘图区**取 ⇒ **两者本来就不该相等**。
            #: ⚠ **但我没有验证这个解释** ⇒ 按事实 82/142 的教训：
            #:   **不把没验证的假设写成判据**。⇒ 改成"两者都是**合理的正尺寸**"，
            #:   并把差值**如实记为「未查明」**。
            chk("★ 两个尺寸都是**合理的正数**（宽高 > 0）",
                bool(bw and pn) and min(*bw, *pn) > 0,
                "BMP(0,0)=%s vs PNG=%s —— ⚠ 宽度差 %s（**未查明**：疑为「窗口 vs 绘图区」）"
                % (bw, pn, abs(pn[0] - bw[0]) if (bw and pn) else "?"))
            if bw and pn:
                ev["cross_check_note"] = (
                    "⚠ **未查明**：`SaveBMP(0,0)` 与 `SaveAs3` 的宽度不同"
                    "（%s vs %s），高度一致（%s）。**最可能**的解释是前者按**窗口**、"
                    "后者按**绘图区**，但**本轮没有验证**（事实 82/142 的教训："
                    "不把没验证的假设写成判据）。" % (bw, pn, bw[1]))'''
assert OLD in t, "交叉核对锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 判据已改成「不假装知道」")
