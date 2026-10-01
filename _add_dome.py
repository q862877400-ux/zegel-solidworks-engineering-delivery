import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_part.py")
t = P.read_text(encoding="utf-8")

NEW = '''

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_part.py —— 「圆顶」这一段（2026-10-01 轮 143）。
# 定位:   补 `docs/union-gap-triage.md`「真缺」档里的 `dome`。
# 官方依据: ① 出厂类型库反射 `iface_*.txt`：
#             `Void InsertDome(Double, Boolean, Boolean)`（在 **`IModelDoc2`** 上）·
#             接口 `IDomeFeatureData` / `IDomeFeatureData2` / `DomeFeatureData` / `DomeFeatureData2`
#           ② `C:\\swapi\\types\\IModelDoc2\\InsertDome.md`：
#             `void InsertDome(double Height, bool ReverseDir, bool DoEllipticSurface)`
#             ⚠ 文档写 `Height` 是「in **meters**」—— 与草图侧的实测（事实 73）矛盾，
#             本函数按**毫米**并**在冒烟里量**（`tools/verify_dome_smoke.py`）。
#           ③ ★★ **`swFmDome` 不存在** —— 枚举转储 `enum_values_sldworks.txt` **0 命中**，
#             `CreateDefinition.md` 的 **35 个**合法常量里也**没有**它
#             ⇒ **圆顶走不了 `CreateDefinition` 那条路**（与事实 43 的 `swFmOneBend`/`swFmDraft` 同族）
#             ⇒ 只能走 `IModelDoc2.InsertDome`（**未标 Obsolete**）。
#             ★ `IDomeFeatureData2` 只能在**建完之后**从特征上取（`IFeature::GetDefinition`）。
#           ④ ⚠ **`InsertDome` 返回 `Void`** ⇒ **没有返回值可查** ⇒ 照事实 40：
#             失败必须用**别的**证据暴露（本函数的冒烟用**特征树** + **边界框增长**）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块文档化 `insert_dome` 一个单元。
# ─────────────────────────────────────────────────────────────────────
def insert_dome(model, height, reverse=False, elliptic=False):
    """给**已选中的面**加一个圆顶（官方 `IModelDoc2.InsertDome`）。

    ⚠ **调用前必须先选好一个面**（与同模块的 `fillet` / `chamfer` / `shell` 同一约定）。

    :param height: 圆顶高度（**毫米**）。⚠ 官方文档写「in meters」，
        本仓库按**实测**取毫米（`tools/verify_dome_smoke.py`，见已知事实 73 / 84）。
    :param reverse: 反向。
    :param elliptic: 是否做成**椭圆面**（官方 `DoEllipticSurface`）。
    :returns: **没有返回值** —— 官方签名是 `void`。
        ⇒ ★ 照已知事实 40：**要确认成功，必须看别的东西**
        （特征树里出现圆顶特征 / 边界框增长），不能靠"没抛异常"。

    ★ **为什么不用 `CreateDefinition`**：`swFmDome` **不在枚举里、也不在
    `CreateDefinition` 的 35 个合法常量里**（实测，轮 143）⇒ 那条路**不存在**。
    """
    get_com_member(model, "InsertDome")(float(height), bool(reverse), bool(elliptic))
'''

if "def insert_dome" not in t:
    t = t.rstrip() + "\n" + NEW
    P.write_text(t, encoding="utf-8")
    print("  ok 已追加 insert_dome")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
