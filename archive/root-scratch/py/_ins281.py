import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           281 🎯 **Spec Kit `041`：草图编辑真机冒烟 —— **倒角到不了，而且是架构性限制****（轮 122）——
               **8/10**：✅ 造出两条相接直线、**同时选中两条（选区计数 = 2）** ⇒ **前置成立**；
               ❌ `create_sketch_chamfer` 失败；✓ 无残留模态框。
            282 ★ **定向探针量到的：不是「参数没调对」，是架构限制**：
               ```
               新零件 → 进草图 → 两条相接直线 → 确认选区 = 2 → 调 CreateChamfer(2, 0.005, 0.0)
                 ⇒ **pywintypes.com_error: (-2147417851, '服务器出现意外情况')**
               ```
               ★ `0x80010105` **正是事实 47（`AccessSelections`）与事实 28（`CreateBsplineSurface`）
                 那个错误码** ⇒ 归入「pywin32 迟到绑定到不了需要真实指针的接口」。
               ⚠ **按事实 53 停手**，不再试别的类型/参数组合。
            283 ★★ **连着三轮冒烟，产出各不相同 —— 三种结果都是"产出"**：
               ```
               039（GTol）    ：API **到不了** —— 但**不是我的错**（那条路径在本机不通）
               040（螺旋线）  ：**我的实现写错了** —— 且"看着像对的" ⇒ **修好并升 verified**
               041（草图倒角）：**到不了，而且认得出原因** ⇒ 归到已知架构限制，**不再浪费轮次**
               ```
            284 ★ **本轮没有犯「继续变着法试」的错**：
               ```
               第一反应可以是「是不是没选中？」⇒ 冒烟里**先确认选区计数 = 2**（前置已排除）
               第二反应可以是「是不是类型/角度没传对？」⇒ 写探针把三种组合列出来试
               ⇒ 第一个组合就抛 `0x80010105` ⇒ **认出错误码 ⇒ 归到架构限制 ⇒ 停**
               ```
               ★ 若没有"认出错误码"这一步，会接着试 `distance_angle=45°` / `distance_distance` /
                 换 `SetAddToDB`…… **每一版都会再失败一次，而根因根本不是参数。**
            285 ⚠ **处置：如实分裂声明** —— `convert_entities` ⚠未测 · `create_sketch_chamfer` ❌到不了 ·
               `sketch_mirror` ⚠未测 ⇒ 等级**仍留 `stitched`**（三条里只验了一条前置），
               但 `limitations` 逐条写清。**已知事实 67** 入库。
               ⚠ **一个没被裁决的旧冲突**：`swSketchChamferType_e` 的 `distance_distance`
                 （反射 1 vs md −1）**本轮没能用真机裁决** —— 在"选型"之前调用就报错了
                 ⇒ 该冲突**仍然悬着**，不要因为"跑过一次"就以为它被验证了。
               回归 **1108 passed**。
               下轮候选：① 继续给剩下 3 条 `stitched` 冒烟（`surface_modeling` / `mold_tools` /
                 `animation_export` —— 前两条已知缺运行期、第三条缺 Motion 插件，预期也是"记下到不了"）；
               ② 继续补「真缺」；③ A5 的 2 条存疑。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+281 ", before, re.M):
    print("  游标 281 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+285 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 285 行已存在 ✓")
