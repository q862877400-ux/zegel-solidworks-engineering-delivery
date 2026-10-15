r"""@brief 验证 `create_gusset` 补上的官方属性**真的被接受**（正面证据）。

## 为什么单独验这一步
第 31 轮补上了官方 `ISMGussetFeatureData` Remarks **步骤 3 的头一句**
（`ProfileDimensionScheme`）以及官方明写「必须」的 `UseAngleDimForProfile` / `UseOffset`。
**但 `CreateFeature(118)` 仍然失败** ⇒ 必须分清两件事：
* **属性层**：这次补的属性**有没有**设进去（读回即可证）
* **创建层**：`CreateFeature` 失败的原因**是不是**属性缺失（由本探针判定）

**⇒ 若属性全部读回正确、而 `CreateFeature` 仍失败
⇒ 说明**失败原因不在属性层**，而在官方步骤 2（预选「一个折弯的两个平面」）
⇒ 与第 24 轮的判断一致（夹具是平板、造不出折弯）。**

# ── 来源 ──
# 仓库:   SolidWorks 官方 API 文档
# 文件:   `C:\swapi\types\ISMGussetFeatureData\_overview.md` 的 Remarks（4 步）
#         `ProfileDimensionScheme.md` / `UseAngleDimForProfile.md` / `UseOffset.md` / `OffsetDistance.md`
# 定位:   把「属性层已修」与「创建层仍失败」两件事**分开取证**，避免把
#         「我改对了属性」说成「我修好了工具」。
# 官方签名依据: 同上 5 份官方页
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；只取 FeatureData、调 `CreateFeature` 看结果、**不保存**。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part  # noqa: E402
from scripts import sw_sheet_metal as SM  # noqa: E402

PROBES = ("ProfileDimensionScheme", "UseAngleDimForProfile", "UseOffset", "OffsetDistance",
          "GussetThickness", "ProfileHeightDim", "ProfileLengthDim", "ProfileAngleDim")


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        SM.create_base_flange(model, "Sketch1",
                              SM.BaseFlangeSpec(thickness=0.002, bend_radius=0.002, depth=0.05))
        mgr = get_com_member(model, "FeatureManager")
        print("[参照] %r（**平板基体法兰，没有折弯**）" % title)

        print()
        print("=== ① 属性层：按 `create_gusset` 的 `_apply` 原样设一遍，再**读回** ===")
        data = get_com_member(mgr, "CreateDefinition", SM.SW_FM_SM_GUSSET)
        if data is None:
            print("  ✗ CreateDefinition(118) 返回 None"); return 1
        # 与模块 _apply 一致的赋值（**数值取模块的默认 spec**）
        spec = SM.GussetSpec(thickness=0.002, profile_distance_1=0.01)
        data.ProfileDimensionScheme = SM.GUSSET_PROFILE_DIMENSIONS
        data.UseAngleDimForProfile = True
        data.GussetThickness = float(spec.thickness)
        data.ProfileHeightDim = float(spec.profile_distance_1)
        data.ProfileLengthDim = float(spec.profile_distance_2)
        data.ProfileAngleDim = float(spec.profile_angle)
        data.UseOffset = True
        data.OffsetDistance = 0.0
        ok = 0
        for p in PROBES:
            try:
                v = getattr(data, p)
                print("    %-26s → ✓ %r" % (p, v))
                ok += 1
            except Exception as exc:  # noqa: BLE001
                print("    %-26s → ✗ %s" % (p, str(exc)[:52]))
        print("  **属性层：%d/%d 读回成功** ⇒ 这次补的官方属性**确实被接受**" % (ok, len(PROBES)))

        print()
        print("=== ② 创建层：同一个 data 直接 `CreateFeature` ===")
        feat = get_com_member(mgr, "CreateFeature", data)
        print("  CreateFeature(118) → %s" % ("✓ 返回非 None（**建成**）" if feat is not None
                                             else "✗ **None**（未建成）"))

        print()
        print("=== 结论（把两件事分开说）===")
        if ok == len(PROBES) and feat is None:
            print("  ✅ **属性层已修对**（官方要求的全部属性都设进去且读得回）")
            print("  ❌ **创建层仍失败** ⇒ 失败原因**不在属性层**")
            print("  ⇒ 与第 24 轮一致：官方步骤 2 要求**预选「一个折弯的两个平面」**，")
            print("     而本夹具是**平板（无折弯）** ⇒ 造不出那个前置。")
            print("  ⇒ **不宣称 `create_gusset` 可用**；本次修复的价值是**除掉了一个确证的缺陷**。")
        elif feat is not None:
            print("  🎉 **建成了** —— 属性缺失确实是阻塞（**这会是重大结果，需复核**）")
        else:
            print("  ⚠ 属性层也没全通 ⇒ 另有问题，需继续查")
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if title:
                sw.CloseDoc(title)
                print("  [收尾] 文档已关闭（未保存）")
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
