import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"D:\AI\SW\docs\plan-10h.md")
t = p.read_text(encoding="utf-8")
MARK = "★★ W4 范围更正（轮 228 实测后）"
if MARK in t:
    print("  已在，跳过")
else:
    NEW = """### W4 · 零件特征族（`specs/135`）· 约 90 分钟 · ★★ **2026-10-01 轮 228 实测后改范围（见下）**

```
★★★ **改范围的理由（实测，不是估的）**：⑯ 那 28 个缺口名**逐个核过之后**——
   ① **已有对应 15 个**：`chamfer` `fillet` `extrude` `extrude_cut` `revolve` `shell` `loft`
      `sweep` `draft` `dome` `helix` `hole` `mirror` `linear_pattern` `pattern_circular` …
   ② **名字对不上 13 个**：`combine_bodies` `delete_body` `split_body` `scale_body` `move_body`
      `intersect` `wrap` `fill_pattern` `pattern_features` `save_body_as_part` `sweep` …
   ⇒ ★★ **这 28 个**全是"建 / 改"操作**，而原计划写的是 W4 取「**回读**」
     ⇒ ★ **两者不对口**：回读**已经有**（`solidworks_collect_model_summary` 就是特征树回读）
     ⇒ 照原计划做 W4 = **做重复功**（与 W2/W3 同一个教训）。
   ★★ 而实测查出一件更该做的事：**首参可注入、且没挂的"建特征"函数有 10 个** ——
     `sw_part.extrude_boss` / `extrude_cut` / `extrude_midplane` / `chamfer` / `fillet` /
     `shell` / `insert_dome` / `linear_pattern` · `sw_helix.insert_helix` ·
     `sw_sketch_edit.create_sketch_chamfer`
     ⇒ ★ 而 MCP 里**已经有** `solidworks_revolve_boss`（batch17）与
       `solidworks_create_hole_feature` ⇒ ★★ **不对称：会旋转、会打孔，却不会拉伸！**
     ▸ **base flange** 也是这一族（batch4 已挂）⇒ 短板在**最基础的拉伸/切除/倒角**。

★ **所以 W4 改为**：挂**建特征**的一小批（拉伸 / 切除 / 倒角），
  ★ 且**验证方式与只读批不同** —— 必须**读写配对**：
    建草图 → 拉伸/切除 → ★ **用只读工具回读断言形状真的变了**
    （`collect_model_summary` 看特征树 · `part_bounding_box` 看包围盒 · W1 的草图读数看草图）
  ⇒ 这是本阶段核心判据（A/B 配对）在"写"类批次上的自然延伸。
★ ⚠ 不做高风险写操作（保存 / 另存 / 删除）—— 本批**只改新文档**，收尾关件不保存。

来源 / license：本项目自身（MIT）；官方依据 `IFeatureManager.FeatureExtrusion3`（23 参数）·
  `FeatureCut4`（★ 事实 1：切除的正确入口是它，不是 `FeatureExtrusion3(Flip=true)`）
验收①：工具数 + 门禁；②：`python tools/capture_feature_evidence.py` ⇒ `verdict: pass`
```

"""
    anchor = "### W5 · 检查 / 测量 / 反馈族"
    i = t.find(anchor)
    assert i > 0, "锚点不符"
    #: 用新段替换掉旧的 W4 段（旧段从 "### W4" 到 "### W5" 之前）
    j = t.find("### W4 · 零件特征族")
    assert j > 0
    t = t[:j] + NEW + t[i:]
    p.write_text(t, encoding="utf-8")
    print("  ✓ W4 段已替换")
u = p.read_text(encoding="utf-8")
for k in ("W4 范围更正", "读写配对", "不会拉伸"):
    print("  含「%s」: %s" % (k, k in u))
