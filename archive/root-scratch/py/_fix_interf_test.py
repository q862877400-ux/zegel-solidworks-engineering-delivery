import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_assembly_interference.py")
t = P.read_text(encoding="utf-8")

OLD = '''def test_interference_report_pass_and_warn():
    class Item:
        Name = "干涉-1"
        Volume = 1.25

    class Detection:
        TreatSubAssembliesAsComponents = True
        TreatCoincidenceAsInterference = True

        def Done(self):
            return None

        def GetInterferenceCount(self):
            return 1

        def GetInterference(self, index):
            assert index == 0
            return Item()

    class Model:
        InterferenceDetection = Detection()

    report = get_interference_detection(Model())
    assert report["status"] == "warn"
    assert report["interference_count"] == 1
    assert report["manual_review_required"] is True
    assert report["items"][0]["name"] == "干涉-1"'''

NEW = '''def test_interference_report_blocks_when_interference_found():
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
    assert report["status"] == "blocked", (
        "有干涉时应当 `blocked`（⚠ 旧断言 `warn` 是照着**坏接口名**的降级行为写的）")
    assert report["interference_count"] == 1
    assert report["manual_review_required"] is True
    assert report["items"][0]["volume"] == 1.25'''
assert OLD in t, "测试锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 测试已改成官方真名 + 正确期望值")
