import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 能力升级
P = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(P.read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("id") != "helix_and_spiral":
        continue
    c["level"] = "verified"
    c["verified_versions"] = ["2026"]
    c["evidence"] = [
        "python tools/verify_helix_smoke.py"
        "（**真机**，SW 2026 SP4.1 / 34.4.1：新零件 → 进草图 → 画圆 → 选中 → 建螺旋线 → "
        "**读回定义** → 关件不保存，**13/13 通过**，证据落 output/helix-smoke-evidence.json）",
        "pytest tests/test_sw_helix_contract.py（**契约测试，无 COM**）",
    ]
    c["limitations"] = [
        "⚑ 2026-10-01（轮 121）**由 `stitched` 升为 `verified`** —— 依据是真机冒烟 **13/13**，"
        "★ 而且证据是**往返一致**档的：传 `height_mm=50 / pitch_mm=10 / revolution=5`，"
        "**从 `IHelixFeatureData` 读回 `Height=0.05` 米 · `Pitch=0.01` 米 · `Revolution=5.0`** —— "
        "★★ **这同时证明了 mm→米 的换算是对的**（若换算错，读回的会是 50）。",
        "★★ **本轮冒烟抓到并修掉了一处自己的缺陷**：`_newest_feature_name` 原实现读 "
        "`model.FirstFeature`（**特征树的第一个**，实测是 `'收藏'` 收藏夹）"
        "而**不是刚加的那个** ⇒ 改名改用官方 "
        "`IModelDocExtension.GetLastFeatureAdded()`。"
        "⚠ 这个错**不抛异常、返回一个看起来合理的字符串** ⇒ 静态测试抓不到。",
        "⚠ 官方 `GetLastFeatureAdded` 的 Remarks 提醒：它**可能返回子特征**"
        "（配合、工程图视图等）—— 本模块的用途（取刚建的螺旋线）下未遇到，但**未穷尽验证**。",
        "⚠ 只验了 **`height_mm` / `pitch_mm` / `revolution`** 这一组参数；"
        "`reversed` / `clockwise` / `tapered` / `outward` / `taper_angle_deg` / `start_angle_deg` "
        "与 `helix_def` 的**其余三种取值**（height+pitch / height+revolution / spiral）**未测**。",
        "⚠ 只覆盖**定距**；变距（`IFeatureManager.InsertVariablePitchHelix`）**未实现**。",
        "⚠ 调用前置**必须选中定义直径的圆**（官方示例如此）；本模块**不代选**。",
        "⚠ 官方**未写** `Pitch` 与 `TaperAngle` 的单位 ⇒ 本模块按同类推断（Pitch 按米、TaperAngle 按度），"
        "★ 其中 **`Pitch` 的推断本轮已被真机证实**（读回 0.01 与传的 10 mm 相符）；"
        "**`TaperAngle` 仍未验证**。",
    ]
    print("  ok helix_and_spiral: stitched -> verified")
    break
else:
    raise SystemExit("  找不到 helix_and_spiral")
P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
import collections
print("  能力数 %d · level %s"
      % (len(d["capabilities"]), dict(collections.Counter(c.get("level") for c in d["capabilities"]))))

# ② 源码来源块同步
Q = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_helix.py")
tq = Q.read_text(encoding="utf-8")
old = ("# ⚠ **验证等级：`stitched`** —— 只有**静态**证据（签名三源互核 + 契约测试），\n"
       "#   **没有本机运行证据**（未在真机上建过螺旋线）⇒ 按五级枚举，**不得标 `verified`**。")
new = ("# ⚑ **验证等级：`verified`**（2026-10-01 轮 121 由 `stitched` 升上来）——\n"
       "#   依据 **真机冒烟** `python tools/verify_helix_smoke.py`（**13/13**，SW 2026 SP4.1 / 34.4.1）：\n"
       "#     新零件 → 进草图 → 画圆 → 选中 → `insert_helix(50mm, 10mm, 5 圈)` → **读回定义**。\n"
       "#   ★★ 证据是**往返一致**档的：读回 `Height=0.05` 米 · `Pitch=0.01` 米 · `Revolution=5.0`\n"
       "#     ⇒ **同时证明 mm→米 的换算是对的**（若换算错，读回的会是 50）。\n"
       "#   ★★ 本轮冒烟还**抓到并修掉了一处自己的缺陷**：`_newest_feature_name` 原读\n"
       "#     `model.FirstFeature`（**树的第一个**，实测是 `'收藏'`）而非刚加的那个 ⇒ 改用\n"
       "#     官方 `IModelDocExtension.GetLastFeatureAdded()`。")
if old in tq:
    Q.write_text(tq.replace(old, new, 1), encoding="utf-8")
    print("  ok sw_helix 来源块已改为 verified")
elif "验证等级：`verified`" in tq:
    print("  源码已是 verified")
else:
    print("  ⚠ 源码来源块锚点不符")
