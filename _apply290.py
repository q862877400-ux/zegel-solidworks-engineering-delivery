import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

E1 = ("python 真机（轮 373）★ **PASS 5/5** —— `RenderMaterialSpec(file_name=<真实 .p2m>)` 打通整族："
      "`create` ok · `add_entity` ok · `add_render_material` ok · **`list_render_materials` 读到 1 个** · "
      "`GetRenderMaterialsCount2(2, names)` 也回 **1** ⇒ 命中 5/5。★ 同时验证新契约："
      "`RenderMaterialSpec()`（空 `file_name`）**明确抛 ValueError**。证据 output/render-material-evidence.json")
E2 = ("python 真机（轮 373）★ **真因是 `FileName` 必须绑 `.p2m`** —— 四轮收窄的终点（known-facts 287→290）："
      "`CreateRenderMaterial(name)` 建出的外观**没有绑定材质文件**时，"
      "`AddDisplayStateSpecificRenderMaterial` **照样回 true** 且 `GetLinkedDisplayStates` **显示已链接**，"
      "而 `GetMaterialIds` 回 `None`、`GetRenderMaterialsCount2` 恒 **0**"
      "（★ 一个「看起来成功、实际不算数」的外观）。★ 设 `FileName = '<真实 .p2m>'` 之后："
      "`GetMaterialIds` 回 `id1=6`、`GetRenderMaterialsCount2` 回 **2**、我们自己的 "
      "`list_render_materials` 读到条目。")
E3 = ("python 真机（轮 367）★ **顺带修掉第 12 处「设属性写成取或调」**：`create_render_material` 的 "
      "`spec.extra` 循环原为 `get_com_member(material, key, float(value))`（事实 227）⇒ `TypeError`；"
      "已改 `set_com_member`（★ 前人轮 319 修了 11 处，这一处漏了）。")
E4 = ("python 真机（轮 371/372）★ **观察点**：`IRenderMaterial.GetLinkedDisplayStates()` 直接回答"
      "「外观挂到了哪些显示状态」，★ 不经过「清单」那条可疑中介 ⇒ 用它证明 `Add…` 的**链接**确实生效"
      "（而清单仍空）。")
L1 = "★★ **2026-10-02（轮 373）已真机 PASS 5/5**（`file_name` 绑定真实 `.p2m` 之后）。"
L2 = ("⚠ **`file_name` 是必需项** —— 空值会被 `RenderMaterialSpec.validate()` 拒掉"
      "（★ 而不是静默建一个不会被收录的外观）。SW 自带材质在 "
      "`<install>\\data\\graphics\\Materials\\**\\*.p2m`。")
L3 = ("⚠ **`IRenderMaterial.MaterialID` 属性自 SOLIDWORKS 2011 起已废弃、恒回 0**"
      "（官方原文：Not supported in SOLIDWORKS 2011 and later. Superseded by GetMaterialIds）"
      "⇒ ★ 取 ID 要用 **`GetMaterialIds(out, out)`**。")
L4 = ("⚠ 本族只验了「建外观 → 绑 `.p2m` → 挂实体 → 加到显示状态 → 读清单」这一条链；"
      "★ **删除**（`DeleteDisplayStateSpecificRenderMaterial`）与**改属性回读**未单独真机验。")
NOTE = ("★ 2026-10-02（轮 367–373）：本族此前停在 stitched，★ 真因是**外观必须绑 `.p2m`**"
        "（`FileName` 为空时 `Add…` 会「回 true 而清单不增」）。")

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "render_material_library")
x["level"] = "verified"
x["verified_versions"] = x.get("verified_versions") or ["2026"]
x["evidence"] = [E1, E2, E3, E4]
x["limitations"] = [L1, L2, L3, L4]
y = next((z for z in d["capabilities"] if z["id"] == "costing"), None)
if y is not None:
    lim = list(y.get("limitations") or [])
    if not any("GetLinkedDisplayStates" in t for t in lim):
        lim.insert(0, NOTE)
    y["limitations"] = lim
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
vf = sum(1 for z in d["capabilities"] if z.get("level") == "verified")
st = sum(1 for z in d["capabilities"] if z.get("level") == "stitched")
print("  ok · verified=%d stitched=%d" % (vf, st))
