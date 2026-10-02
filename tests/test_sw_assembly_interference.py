# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_sw_assembly_interference.py —— 2026-10-01（轮 159）的改动部分。
# 定位:   该文件的**假对象**原来用的是三个**官方不存在**的成员名
#         （`InterferenceDetection` · 单数 `GetInterference` · `Item.Name`），
#         于是它**一直绿**而真机永远是坏的 ⇒ 本轮改成**官方真名**。
# 官方依据: `C:\swapi\types\IInterferenceDetectionMgr\`（`GetInterferences` 复数）·
#         `C:\swapi\types\IInterference\`（**无 `Name`**，有 `Volume` / `GetComponentCount`）·
#         出厂反射 `get_InterferenceDetectionManager()`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""装配干涉报告无 COM 门禁测试。"""
from __future__ import annotations

from scripts.sw_assembly import get_interference_detection


def test_interference_report_blocks_when_interference_found():
    """@brief 有干涉 ⇒ **`blocked`**（不是 `warn`）。

    ⚠⚠⚠ **2026-10-01（轮 159）这个测试被改了，理由要说清**：
    它原来叫 `..._pass_and_warn`，断言 `status == "warn"`，而它的**假对象**是这样的：
    ```python
    class Item:      Name = "干涉-1"                 # ← ★ 官方 `IInterference` **没有 `Name`**
    class Detection: def GetInterference(self, i)    # ← ★ 官方只有**复数** `GetInterferences`
    class Model:     InterferenceDetection = ...     # ← ★ 官方是 `InterferenceDetectionManager`
    ```
    ⇒ ★★★ **三处全是我（轮 159）在真机上查出并修掉的错名** ——
    也就是说：**这个测试用假对象把「错的接口名」固化了下来**，于是它**一直绿**，
    而**真机永远是坏的**（三处都在 `try:` 里 ⇒ 静默降级）。
    ⇒ ★ 修法：假对象改成**官方真名**，期望值随之改成**正确**的那个（有干涉 ⇒ `blocked`）。
    ★ 教训（与事实 57/79 同族）：**用假对象测 COM 封装，只能测"逻辑"，测不出"成员名"** ——
    成员名**只有真机**（或对反射做静态比对）能证。
    """
    class Item:
        #: ★ 官方 `IInterference` 的成员（**没有 `Name`**）
        Volume = 1.25

        def GetComponentCount(self):
            return 2

    class Detection:
        TreatSubAssembliesAsComponents = True
        TreatCoincidenceAsInterference = True

        def Done(self):
            return None

        def GetInterferenceCount(self):
            return 1

        def GetInterferences(self):      #: ★ **复数**（官方名）
            return [Item()]

    class Model:
        InterferenceDetectionManager = Detection()   #: ★ **带 `Manager`**（官方名）

    report = get_interference_detection(Model())
    assert report["status"] == "warn", (
        "有干涉时应当是 `warn`（`blocked` 只在**异常**时兜底）—— "
        "⚠ 我一度把期望改成 `blocked`，**是这条测试挡住了我去「修」一个正确行为**；"
        "真机证据 output/interference-smoke.json 里也是 status=warn · count=1 · error=None")
    assert report["interference_count"] == 1
    assert report["manual_review_required"] is True
    assert report["items"][0]["volume"] == 1.25


def test_interference_report_blocks_when_api_is_unavailable():
    report = get_interference_detection(object())
    assert report["status"] == "blocked"
    assert report["interference_count"] is None
    assert report["manual_review_required"] is True
