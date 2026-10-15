import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_part.py")
t = P.read_text(encoding="utf-8")

NEW = '''

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_part.py —— 「合成曲线」这一段（2026-10-01 轮 151）。
# 定位:   补 `docs/union-gap-triage.md`「真缺」档里的 `composite_curve`。
# 官方依据: ① 出厂类型库反射 `iface_sldworks.txt`：`Boolean InsertCompositeCurve()`
#             （在 **`IModelDoc2`** 上）· 接口 `ICompositeCurveFeatureData` / `CompositeCurveFeatureData`
#           ② `C:\\swapi\\types\\IModelDoc2\\InsertCompositeCurve.md`：
#             `bool InsertCompositeCurve()` —— **零参**；Returns ⇒ **True 才是成功**
#             · Remarks：**要先用 `SelectByID2` 以 mark number of 1 选实体**
#           ③ ★ 官方示例 `examples\\Insert_a_Composite_Curve_Example_CSharp.md`：
#             `SelectByID2("Sketch2","SKETCH",…,false,**1**,null,0)`
#             `SelectByID2("Sketch1","SKETCH",…,true, **1**,null,0)`
#             `swModel.InsertCompositeCurve()`
#             ⇒ 建完后 `SelectByID2("CompCurve1","REFERENCECURVES",…)` +
#               `((CompositeCurveFeatureData)feat.GetDefinition()).GetEntitiesToJoinCount()`
#               ⇒ ★★ **能读回"并了几个实体"** ⇒ 这是**定量往返**的抓手。
#           ④ ⚠⚠ 本函数**必须用 `call_com_member`**（不是 `get_com_member`）：
#             官方签名**零参** ⇒ 而 `get_com_member` 在无实参时会「**先试调一次**」
#             （已知事实 84：对 COM 成员，"取"就等于"调"）⇒ 那样会**替调用方悄悄调一次**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块文档化 `insert_composite_curve` 一个单元。
# ─────────────────────────────────────────────────────────────────────
def insert_composite_curve(model):
    """把**当前选中的实体**合成一条曲线（官方 `IModelDoc2.InsertCompositeCurve`）。

    ⚠ **调用前必须先用 mark = 1 选好实体**（官方 Remarks；与 `insert_dome` 同一个坑）。

    :returns: 官方返回的 `bool`（**True 才是成功**）。
    :raises RuntimeError: 官方返回 `False`。

    ★ **用 `call_com_member` 而不是 `get_com_member`**：官方签名**零参**，
    而 `get_com_member` 对零参成员会**先试调一次**（已知事实 84）⇒
    用它会**在"取"的时候把这个动作做掉**，调用方失去控制。
    """
    ok = call_com_member(model, "InsertCompositeCurve")
    if not ok:
        raise RuntimeError(
            "IModelDoc2.InsertCompositeCurve 返回 False ⇒ 合成曲线没建出来。"
            "⚠ 官方 Remarks：**必须先用 `SelectByID2(..., mark=1)` 选好实体**；"
            "且实体类型要合法（见 SOLIDWORKS Help）。"
        )
    return True
'''

if "def insert_composite_curve" not in t:
    t = t.rstrip() + "\n" + NEW
    P.write_text(t, encoding="utf-8")
    print("  ok 已追加 insert_composite_curve")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
#: ⚠ 确认 `call_com_member` 在本文件可用（轮 145 加的）
print("  call_com_member 在导入里: %s" % ("call_com_member" in t.split("def ")[0]))
