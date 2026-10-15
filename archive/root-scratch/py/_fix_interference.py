import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_assembly.py")
t = P.read_text(encoding="utf-8")

OLD = "        interference = asm_model.InterferenceDetection"
NEW = ("        #: ⚠⚠⚠ **两处成员名都错**（2026-10-01 轮 159 查出）：\n"
       "        #: ① 入口属性是 **`InterferenceDetectionManager`**（**带 `Manager`**）——\n"
       "        #:    出厂反射的拼写是 `get_InterferenceDetectionManager()`；\n"
       "        #: ② 取结果用 **`GetInterferences()`**（**复数**），没有 `GetInterference(index)`。\n"
       "        #: ★ 两处都在 `try:` 里 ⇒ **此前静默降级**（不炸，但**永远拿不到数据**）。\n"
       "        interference = asm_model.InterferenceDetectionManager")
assert OLD in t, "入口锚点不符"
t = t.replace(OLD, NEW, 1)

OLD2 = '''                item = interference.GetInterference(index)'''
NEW2 = '''                item = items_all[index] if index < len(items_all) else None'''
assert OLD2 in t, "取结果锚点不符"
t = t.replace(OLD2, NEW2, 1)

#: 在计数之后、循环之前，一次取回全部干涉项
OLD3 = "        count = int(safe_get_com_member(interference, \"GetInterferenceCount\") or 0)"
NEW3 = ("        count = int(safe_get_com_member(interference, \"GetInterferenceCount\") or 0)\n"
        "        #: ★ **复数**接口一次取回（官方 `IInterferenceDetectionMgr.GetInterferences`）；\n"
        "        #: ⚠ 返回形状**未在本轮查证**（是数组还是 Dispatch）⇒ 用 `list(...)` 兜一下，\n"
        "        #: 拿不到就让下面的逐项 `try` 如实记错误。\n"
        "        try:\n"
        "            _got = call_com_member(interference, \"GetInterferences\")\n"
        "            items_all = list(_got) if _got is not None else []\n"
        "        except Exception:      # noqa: BLE001\n"
        "            items_all = []")
assert OLD3 in t, "计数锚点不符"
t = t.replace(OLD3, NEW3, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok sw_assembly.get_interference_detection 已修（两处成员名）")
