import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\check_member_owner_interface.py")
t = P.read_text(encoding="utf-8")

#: ⚠⚠⚠ **回退轮 174 的「保守退路」**（我自己加、自己证伪的那条）：
#: 它用「docstring 里出现的接口名**恰好 1 个**」推形参类型 ⇒ **实测两处都推错**：
#:   · `insert_parting_line` 等 5 个 ⇒ 推成 **`Feature`**（docstring 里的**散文词** "feature" 命中了接口名 `Feature`）
#:   · `mold_undercut_detect`      ⇒ 推成 **`IFeatureManager`**（docstring 提到的是**成员全名**
#:                                    `IFeatureManager.MoldUndercutDetect`，**不是参数的类型**）
#: ⇒ ★★★ **"恰好 1 个"不等于"它是参数的类型"** ⇒ 按事实 53/113：**这条判据不成立，回退**。
OLD_START = "    #: ★★ 2026-10-01（轮 174）：**没有 `:param` 段时**的保守退路 ——"
i = t.find(OLD_START)
assert i > 0, "找不到要回退的那段"
#: 找到这段的结束（下一个 `    return out` 之后）
j = t.find("    return out", i)
assert j > i
j = t.find("\n", j) + 1
t = t[:i] + t[j:]
#: 在函数 docstring 里写明"这条已试过并不成立"
MARK = "    ⚠ **依据必须来自反射**"
k = t.find(MARK)
assert k > 0
t = t[:k] + (
    "    ⚠⚠⚠ **2026-10-01（轮 174）试过一条"没有 `:param` 时从 docstring 猜"的退路 —— 实测**两处都推错**：**\n"
    "    ① `insert_parting_line` 等 5 个 ⇒ 推成 `Feature`（docstring 里的**散文词** `feature` 命中了接口名 `Feature`）；\n"
    "    ② `mold_undercut_detect` ⇒ 推成 `IFeatureManager`（docstring 提到的是**成员全名**\n"
    "       `IFeatureManager.MoldUndercutDetect`，**不是参数的类型**）。\n"
    "    ⇒ ★★★ **"恰好 1 个"不等于"它是参数的类型"** ⇒ **该退路已回退**（事实 53/113）。\n"
    "    ⇒ ★ 所以**只认 `:param <名>: <接口名>` 这一种写法**（显式 = 有依据；推断 = 会错）。\n"
) + t[k:]
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已回退那条退路，并把「试过、不成立」写进 docstring")
