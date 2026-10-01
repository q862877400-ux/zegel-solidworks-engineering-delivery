import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
caps = d["capabilities"]

# ── ① 更正 sketch_edit_ops 里那句「架构性限制」（轮 122 的误判）──────
n_fix = 0
for c in caps:
    if c.get("id") == "sketch_edit_ops":
        lim = c.get("limitations") or []
        lim.insert(0, "".join([
            "★★★ **2026-10-01（轮 164）更正轮 122 的定性**：轮 122 看到 `type=2` 报",
            "`com_error 0x80010105` 就判它「**架构性限制、到不了**」并停手 —— **那是误判**。",
            "★ 轮 164 用 `tools/probe_chamfer_forms.py` **逐类型试 + 回读线段数**（`tools/probe_chamfer_forms.py`）：",
            "`type=0`（默认）/ `type=1` ⇒ 段数 **2 → 2**（没变）且返回 `None`；",
            "**`type=2`（`distance_equal`）⇒ 段数 `2 → 3`（倒角真的建出来了）**，",
            "只是**返回对象拿不到**（`com_error 0x80010105`）。",
            "⇒ ★★ 真正的限制是「**拿不到返回对象**」，**不是**「做不了倒角」。",
            "★ 根因：轮 122 **只看异常、没回读副作用** —— 与事实 94 那一族（**不信返回值，回读状态**）同源。",
            "⇒ ★ 已把倒角拆成独立条目 `sketch_chamfer`（`level: verified`，真机 **10/10**）；",
            "本条目**仍为 `stitched`**：`sketch_mirror` 与 `convert_entities` **本轮未单独取证**。",
        ]))
        c["limitations"] = lim
        n_fix += 1
print("  ok 更正 sketch_edit_ops 的 limitations：%d 处" % n_fix)

# ── ② 拆出独立条目 sketch_chamfer（verified）──────────────────────
if not any(c.get("id") == "sketch_chamfer" for c in caps):
    caps.append({
        "id": "sketch_chamfer",
        "label": "草图倒角（CreateChamfer）",
        "level": "verified",
        "backends": ["solidworks-com-pywin32"],
        "verified_versions": ["2026 SP4.1"],
        "dependencies": ["python"],
        "limitations": [
            "⚠ **只有 `swSketchChamfer_DistanceEqual`(2) 能成** —— "
            "`type=0`（默认 `distance_angle`）/ `type=1`（`distance_distance`）实测**都不做事**"
            "（段数不变、返回 `None`）",
            "⚠ **拿不到返回对象**：`type=2` 建成后，取 `SketchSegment` 返回值会抛 "
            "`com_error 0x80010105`（pywin32 迟到绑定）⇒ `create_sketch_chamfer` 改为"
            "**回读线段数**判定成功，建成时返回 `None`",
            "官方前置**必须选中两条草图实体**；⚠ 判「选上没有」一律**回读**选区计数（事实 94）",
            "⚠ 只证「线段数 2 → 3」（**倒角建出来了**），**不证倒角距离 5mm 的数值对不对**",
        ],
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "evidence": [
            "python tools/verify_sketch_edit_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1："
            "新零件 → 进草图 → 两条相接直线 → 选中两条（选区计数 **2**）→ "
            "`create_sketch_chamfer(chamfer_type=2, distance_mm=5)` ⇒ "
            "**线段数 2 → 3**）—— **10/10** `verdict: pass`",
            "python tools/probe_chamfer_forms.py（**真机**，逐类型试：type0/type1 段数不变 · "
            "**type2 段数 2 → 3**）",
        ],
        "source": "original",
        "source_evidence": "scripts/sw_sketch_edit.py 的 create_sketch_chamfer"
                            "（照官方 `ISketchManager.CreateChamfer(Int32, Double, Double)` 签名自建）",
    })
    print("  ok 已拆出独立条目 sketch_chamfer（level=verified）")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
