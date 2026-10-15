import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_gtol.py")
t = P.read_text(encoding="utf-8")

# ① 文件头的等级块：改成诚实的分裂声明
old_head = """# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ **验证等级：`stitched`** —— 只有**静态**证据（签名两源互核 + 契约测试），
#   **没有本机运行证据**（未建过形位公差）⇒ **不得标 `verified`**。
# ─────────────────────────────────────────────────────────────────────────"""
new_head = """# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
#
# ⚠⚠ **验证等级：分成两半**（2026-10-01 轮 120 **真机冒烟**查出来的结果）：
#   ```
#   insert_gtol            ✅ **真机可用** —— InsertGtol() 返回一个 GTol 对象
#   add_gtol_indicator     ❌ **真机到不了** —— 见下
#   ```
#   ★★ **量到的事实**（`tools/verify_gtol_smoke.py` + 两次定向探针，均在**新零件**上）：
#   ```
#   GetFrameCount()（新建后）                = 1
#   AddFrame()                               -> False
#   GetFrame(0) / GetFrame(1) / GetFrame(2)  -> **全 None**
#   CanConvertFormat() -> True
#   ConvertFormat()    -> **0（成功）**
#   ConvertFormat 后 GetFrameCount()         = **0**（从 1 掉到 0）
#   ConvertFormat 后 GetFrame(1) / (2)       -> **仍全 None**
#   ```
#   ⇒ **"2022 格式的帧路径"在本机（SW 2026 SP4.1 / pywin32 迟到绑定）上取不到帧。**
#   ⚠ **按事实 53 停手**（同一处已试 3 次：补帧 / 直接取 / 先转换），**不再变着法试**。
#   ⚠ 本模块**保留** `add_gtol_indicator`（**不删**）—— 它是**可复算的证据**，
#     也便于别的后端（如 `comtypes`）上重试；但它**当前不可用**。
#   ⚠ 未查证：换后端能否走通；`SetSymbolXml`（XML 路径）**未试**。
# ─────────────────────────────────────────────────────────────────────────"""
if "验证等级：分成两半" not in t:
    assert old_head in t, "文件头锚点不符"
    t = t.replace(old_head, new_head, 1)
    print("  ok 文件头已改为分裂声明")
else:
    print("  文件头已是新声明")

# ② add_gtol_indicator 的 docstring 里加"当前不可用"警示
old_doc = "    ⚑ **轮 120 的修正**：调用前会先 `ensure_gtol_frame()` ——"
new_doc = ("    ⚠⚠ **本函数当前「不可用」（2026-10-01 轮 120 真机实测）** ——\n"
           "    `IGtol.GetFrame(n)` 在**新建的** GTol 上**任何 n 都返回 `None`**：\n"
           "    `GetFrameCount()` 是 1、`AddFrame()` 返回 **False**；\n"
           "    走 `CanConvertFormat()`→`ConvertFormat()`（返回 **0 成功**）之后 `GetFrameCount()` **掉到 0**，\n"
           "    而 `GetFrame` **仍然全 `None`**。⚠ **按事实 53 停手，不再变着法试。**\n"
           "    ★ 保留本函数是为了**留下可复算的证据**，不是为了「应该能用」。\n\n"
           "    ⚑ **轮 120 的修正**：调用前会先 `ensure_gtol_frame()` ——")
if "本函数当前**不可用**" not in t:
    assert old_doc in t, "docstring 锚点不符"
    t = t.replace(old_doc, new_doc, 1)
    print("  ok docstring 已加不可用警示")
else:
    print("  docstring 已有警示")

P.write_text(t, encoding="utf-8")
import ast
ast.parse(t)
print("  语法 OK")
