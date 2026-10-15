import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           460 🎯 **Spec Kit `078`：补上「****直接属性访问****」这个盲区 —— 又修好一个****静默降级****的函数**（轮 159）——
               `077` 修的 `GetSldWorksObject` 是**直接属性访问**形态 ⇒ 查 `check_member_names.py`（138 行）：
               ★ **它只认 `get_com_member` / `call_com_member` / `safe_get_com_member` 三种包装形态**
               ⇒ ★★★ **直接属性访问正是它的盲区**（所以那两个真缺陷才漏过去）。
            461 ★★ **判据两版（第一版实测被弃用）**：
               ```
               第一版「大驼峰 + 不在反射里」⇒ **323 处**，逐条看**全是**
                 argparse / pywin32 / OCP / winreg 的对象（ArgumentParser ×29 · OpenKey ×8 …）
                 ⇒ ★★★ **假阳性率 ≈ 100%** ⇒ **弃用**（事实 74 那一族：名字形态判不出"是不是 COM 成员"）
               第二版（**有依据，不是猜**）：对象名**限定到「被当作 COM 对象用过」的那些**
                 （即 `get_com_member(<OBJ>, …)` 的**第一实参标识符**，共 90 个）
                 ⇒ **12 处**，人工判后**真可疑 2 处** ⇒ ★★ **两处都是真缺陷** ⇒ 判据**可用**
               ```
            462 ★★★ **查出 `get_interference_detection` 的****三处****成员名全错**：
               ```
               ① asm_model.InterferenceDetection ⇒ 官方 **InterferenceDetectionManager**（**带 Manager**）
               ② GetInterference(index)          ⇒ 官方 **GetInterferences()**（**复数**，无单数版）
               ③ item.Name                       ⇒ **IInterference 上根本没有 Name**
                  （成员是 Components/GetComponentCount/GetInterferenceBody/IGetComponents/
                    Ignore/IsFastener/IsPossibleInterference/**Volume**）
               ⇒ ⚠⚠ **三处都在 `try:` 里 ⇒ 此前静默降级**（不炸，但**永远拿不到数据**）
               ```
            463 ★★★ **真机 6/6，含本会话****最强的证据形态******：
               ```
               ✓ 干涉数 = 1
               ✓ ★★★ **干涉体积读回 `15999.999999999998`** ⇒ 对上 **20×40×20 = 16000 mm³**
                 ⇒ **一个能独立算出来的物理量，读回来数值吻合** —— 空操作满足不了
               ✓ GetComponentCount = [2]
               ```
               ★ 证据形态的**升级**：86（尺寸往返）→ 96（格式魔数）→ **99（物理量算得出来）**。
            464 ★★★ **顺带查出一个「假对象测试」的真相**：既有
               `test_sw_assembly_interference.py` 的**假对象**正是照着**错的接口名**写的
               （`Item.Name` / 单数 `GetInterference` / `InterferenceDetection`）——
               **三处全对上** ⇒ 它**一直绿**而**真机永远是坏的**。
               ★ 教训（与事实 57/79 同族）：**用假对象测 COM 封装，只能测「逻辑」，
                 测不出「成员名」** —— 成员名**只有真机**（或对反射做静态比对）能证。
               ★ 我自己**差点改错**：修完那个测试红了 ⇒ 我一度把**期望值**改成 `blocked`，
                 但它**是错的**（`count==0 ⇒ pass`，否则 **`warn`**；`blocked` 只在异常时兜底）
                 ⇒ ★ **是那条测试挡住了我去「修」一个正确行为**（已改回并留档）。
               ⚑ **未查证**：⚠ 第二版判据**仍有假阳性**（`QueryInterface` 是 IUnknown 的，
                 不在 SW 接口表）⇒ **未直接接进门禁**，只做成探针；⚠ 12 处里还有 **9 处未逐条判**；
                 ⚠ 判据判的是「名字在不在」，**判不出语义**；⚠ `GetInterferences()` 的**返回形状**未逐字查证。
               已知事实 **99** 入库 · 回归 **1240 passed** · `release_check` exit 0。
               下轮候选：① 把剩下那 9 处逐条判完（含 OCP 那几处）；② 回到「真缺」继续补；
               ③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+460 ", before, re.M):
    print("  游标 460 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+464 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 464 行已存在 ✓")
