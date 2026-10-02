"""示例 10: 原生曲面几何（路线 A —— 脚本直接造几何曲面）

本域存在**两条互补路线**，本示例走的是其中一条（见下）。

路线 A · 脚本造几何曲面（本示例）
    ISldWorks.GetModeler() → IModeler 的 19 个非指针 Create*Surface。
    产出的曲面是几何体，**不进入特征树**。

路线 B · 界面创建 + 脚本参数化（本示例不覆盖）
    用户在界面 Insert ▸ Surface 建好特征，脚本用
    ``GetDefinition()`` + ``AccessSelections`` / ``ReleaseSelectionAccess``
    取回参数化。Radiate / Planar / Extend / Knit / Fill **没有脚本创建入口**
    （唯一例外是 ``IFeatureManager.PostTrimSurface(Boolean)``）。
    官方示例依据见 ``docs/usage-guide.md`` 的「专题 · 域 7 曲面的两条互补路线」。

⚠ 本文件是**文档与参考实现**，编写过程中未在本机运行（见 AGENTS.md 铁律 2）：
  它会连接并驱动真实 SolidWorks。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名 + 官方使用示例（非开源项目，无第三方许可）
# 文件:   签名: D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IModeler 段
#         示例: C:\swapi\examples\Create_Planar_Surface_Feature_Example_CSharp.md
#               C:\swapi\examples\Create_Radiate_Surface_Example_CSharp.md
#               C:\swapi\examples\Create_Trimmed_Surface_Feature_Example_CSharp.md
#               C:\swapi\examples\Access_Selections_Example_VB.md
# 定位:   本文件演示**路线 A**。官方那几个 Create_*_Surface_* 示例演示的是
#         **路线 B**（界面创建 + GetDefinition 取回），两者不可混用 ——
#         详见本文件 docstring 与 docs/usage-guide.md 的专题节。
# 被调用的实现: scripts/sw_surface.py::get_modeler / create_planar_surface /
#              create_cylindrical_surface / create_coons_b_surface /
#              collect_surface_evidence / DEFAULT_TOLERANCE
# 覆盖:   全文件 —— 本文件是自包含示例，各步骤注释已标明对应的官方签名。
# ⚠ 本文件为静态翻译，未在本机实测（见 AGENTS.md 铁律 2）
# ⚠ 本文件会连接并驱动真实 SolidWorks，编写过程中未运行过。
# ────────────────────────────────────────────────────────────────────
import sys

sys.path.insert(0, r"../scripts")

from sw_connect import connect_solidworks  # noqa: E402
from sw_surface import (  # noqa: E402
    DEFAULT_TOLERANCE,
    collect_surface_evidence,
    create_coons_b_surface,
    create_cylindrical_surface,
    create_planar_surface,
    get_modeler,
)


def main():
    # ⚠ 本函数会启动/附着 SolidWorks。编写与核对本示例的过程中**没有执行过**它。
    print("连接 SolidWorks...")
    sw, _ = connect_solidworks()

    # ── 1. 取 IModeler ─────────────────────────────────────────────
    # 官方提供两个入口：GetModeler() 返回 Object（Automation 友好，Python 可用）
    # 与 IGetModeler() 返回 Modeler 指针版（进程内非托管 C++ 专用，不可用）。
    print("取 IModeler...")
    modeler = get_modeler(sw)
    # 形态确认：create_* 系列都是薄封装，参数已按官方签名顺序固定，
    # 这里再取出一次只为展示「入口对象确实是 Modeler」这一事实。
    assert modeler is not None

    # ── 2. 造一个平面 ─────────────────────────────────────────────
    # 官方签名：CreatePlanarSurface(Object Point, Object Normal) —— 2 参。
    # ⚠ 官方文档未在本地离线源中注明几何参数的单位，故此处**不做单位换算**，
    #   原样透传。以下坐标按米制书写（与本仓库其余模块一致）。
    print("造平面...")
    plane = create_planar_surface(sw, point=[0.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
    print(f"  平面: {plane}")

    # ── 3. 造一个圆柱面 ───────────────────────────────────────────
    # 官方签名：CreateCylindricalSurface(Object Origin, Object Axis, Double Radius)
    # —— 3 参，半径是 Double。
    print("造圆柱面...")
    cylinder = create_cylindrical_surface(
        sw, origin=[0.0, 0.0, 0.0], axis=[0.0, 0.0, 1.0], radius=0.01
    )
    print(f"  圆柱面: {cylinder}")

    # ── 4. 造 Coons B 样条面（四条边界曲线）────────────────────────
    # 官方签名：CreateCoonsBSurface(Curve, Curve, Curve, Curve, Boolean)
    # —— 5 参，末位是 Boolean。曲线需由调用方先在文档里画好并取出。
    # 这里只示范调用形状，曲线对象请按自己的文档准备。
    print("造 Coons B 样条面（需要 4 条已建好的边界曲线）...")
    # coons = create_coons_b_surface(
    #     sw, curve_v=..., curve_u=..., curve_v2=..., curve_u2=..., closed=False
    # )
    print("  （本示例不实际创建，缺少边界曲线对象）")

    # ── 5. 证据回读 ───────────────────────────────────────────────
    print("回读曲面能力证据...")
    evidence = collect_surface_evidence(sw)
    print(f"  Modeler 可用        : {evidence['has_modeler']}")
    print(f"  已登记创建方法      : {evidence['registered_count']} 个")
    print(f"  指针版本可用        : {evidence['pointer_variants_available']}")
    print(f"  说明                : {evidence['pointer_variants_note']}")
    print(f"  默认几何容差        : {DEFAULT_TOLERANCE} m")
    print(f"  平面 / 圆柱面       : {plane} / {cylinder}")
    return evidence


# ⚠ 关于「造出来的曲面怎么进实体」:
#   本模块的 create_* 只返回曲面对象，**不自动建实体**。
#   官方还提供 IBody2 / IModeler 的建体入口，但那些接口的指针版本
#   （ICreate*）属进程内非托管 C++，Python 迟到绑定不可用；
#   Automation 版本的参数表本轮未逐个核签名，故本模块刻意不做半成品。
#   需要带实体时，请在拿到曲面后自行按官方 IModeler/IBody2 文档接续。


if __name__ == "__main__":
    main()
