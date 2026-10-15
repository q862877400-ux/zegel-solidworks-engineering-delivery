import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(P.read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("id") != "sketch_edit_ops":
        continue
    c["evidence"] = [
        "python tools/verify_sketch_edit_smoke.py"
        "（**真机**，SW 2026 SP4.1 / 34.4.1：新零件 → 进草图 → 画两条相接直线 → "
        "选中两条 → 调 `create_sketch_chamfer`，**8/10** —— 选中前置成立，但倒角报错）",
        "pytest tests/test_sw_sketch_edit_contract.py（**16 条契约测试，无 COM**）",
    ]
    c["limitations"].insert(0, "★★ **2026-10-01（轮 122）真机实测：本能力**三条里只有前置能成立**：")
    c["limitations"].insert(1, "　 ✅ **「同时选中两条草图实体」这个前置能成立** —— 造两条相接直线后 "
                              "选区计数 = **2**（用 `sw_selection_spec.select_object` 带 `append`）。")
    c["limitations"].insert(2, "　 ❌ **`create_sketch_chamfer` 到不了** —— 选中 2 条后调 `CreateChamfer` 报 "
                              "`pywintypes.com_error: (-2147417851, '服务器出现意外情况')`。"
                              "★ `0x80010105` **正是已知事实 47 / 28 那个错误码** ⇒ "
                              "属「pywintypes 迟到绑定到不了需要真实指针的接口」这一**架构性限制**，"
                              "**不是参数没调对**。⚠ 按**事实 53** 停手。")
    c["limitations"].insert(3, "　 ⚠ `convert_entities` / `sketch_mirror` **未实测**（前者要选中的边/环/面，"
                              "后者要中心线 mark=2 的选中标记）—— **不得当成「验过了」**。")
    print("  ok sketch_edit_ops 已更新")
    break
else:
    raise SystemExit("  找不到 sketch_edit_ops")
P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# 记已知事实 67
Q = Path(r"D:\AI\SW\docs\known-facts.md")
tq = Q.read_text(encoding="utf-8")
add = """

| # | 事实 | 依据 |
|---|---|---|
| 67 | **`ISketchManager.CreateChamfer` 在 pywin32 后台上到不了（架构性限制，与事实 47 同族）** —— 2026-10-01（轮 122）真机：新零件 → 进草图 → 画两条相接直线 → 用 `sw_selection_spec.select_object`（第二条带 `append`）**确认选区计数 = 2** → 调 `CreateChamfer(2, 0.005, 0.0)` ⇒ **`pywintypes.com_error: (-2147417851, '服务器出现意外情况')`**。★ `0x80010105` **正是事实 47（`ISketchedBendFeatureData.AccessSelections`）与事实 28（`CreateBsplineSurface`）那个错误码** ⇒ 归入「pywin32 迟到绑定到不了需要真实指针的接口」。⚠ 按**事实 53** 停手，不再试别的类型/参数组合。⇒ `scripts/sw_sketch_edit.create_sketch_chamfer` **当前不可用**（保留作可复算证据）。⚠ 同模块的 `convert_entities` / `sketch_mirror` **未实测** | `tools/verify_sketch_edit_smoke.py`（8/10）· 定向探针 `_probe_chamfer_types.py`；事实 47 / 28 |
"""
if "CreateChamfer` 在 pywin32 后台上到不了" not in tq:
    Q.write_text(tq.rstrip() + add, encoding="utf-8")
    print("  ok known-facts 已加 67")
else:
    print("  已有 67")
