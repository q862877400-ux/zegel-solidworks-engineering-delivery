import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           251 🎯 **Spec Kit `035`：方向变了 —— 不再补新能力，改把已有的一条**验实****（轮 116）——
               `023`/`024`/`028`/`034` 连着补了 **4 条 `stitched`**，**都只有静态证据**。
               ★ 再生产只会**堆更多没验过的条目** —— 那正是我在 `014`/`015` 批评过的
                 「孤立函数从没跑过」。⇒ **与其再堆一条，不如把已有的一条验实。**
               挑**真机风险最低**的 ⇒ `equations`（只需一个新零件，不建几何）。
            252 ★ **冒烟 5/5 通过**（只在新零件上跑，绝不碰用户文档）：
               ```
               ✓ 新建临时零件（零件15）
               ✓ add_equation('"SMOKE_B" = 2')    下标=0
               ✓ list_equations                    1 条；首条='"SMOKE_B" = 2'
               ✓ evaluate_equations                ok
               ✓ 收尾无残留模态框  ← 已知事实 64 的产物（CommandInProgress 压不住所有弹框）
               （已关闭临时零件，不保存）
               ```
            253 ★★ **什么才算"强证据"：往返一致**：
               ```
               弱证据：「调用没抛异常」          —— **空操作也能满足**
               强证据：「写进去的 == 读回来的」  —— **空操作满足不了**
               ```
               ⇒ 本轮刻意把**读回内容**打出来比对，而不是只报"列到 1 条"。
               ⚠ 与 `012` 的教训一致：那时 `list_render_materials` 返回 **0 个材质**，
                 「没报错」**什么都没证明**。
            254 ✅ **等级 `stitched` → `verified`**：能力分布 **verified 27 → 28 · stitched 6 → 5**。
               已配齐 `verified_versions: ["2026"]` + `evidence`（2 条）；
               并**加了一条测试「禁止降级」**（源码里必须写 `验证等级：verified`）。
            255 ⚠ **但这不等于"方程式功能全验过了"**：只验了**全局变量方程式**一种；
               维度方程式 · 含 VB `IIf` 的 · `delete_equation` · `evaluate` 的返回值语义
               **都未验**。★ `verified` 的定义是「**有我们自己的运行证据**」——
               **不是**「代码是我们写的」，**也不是**「全部功能都验过」。
               ⚠ 另 3 条 `stitched`（螺旋线 / 草图编辑 / 转换实体引用）**仍需前置条件**
                 （进草图编辑态）才能冒烟 —— **未做**（轮 98 的模态框正是那样触发的）。
               回归 **1091 passed**。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+251 ", before, re.M):
    print("  游标 251 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+255 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 255 行已存在 ✓")
