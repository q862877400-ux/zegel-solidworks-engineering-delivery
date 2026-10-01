import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))

EV = ("python tools/verify_dome_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1：`insert_dome(8)` 在 "
      "100×60×20 的板顶面建成 ⇒ 边界框**逐分量**变化 Z 20 → **34.2222**；特征树 19 → 20；"
      "**9/9**，其中两条**如实标注**为「未查明」与「不可达」）")
L1 = ("⚑ 2026-10-01（轮 143）**补 `dome`**（`insert_dome`，真缺档）。★★ **官方 Remarks 是钥匙**："
      "「Before using this method, you must select the face for the dome using a "
      "**selection mark of 1**」—— 用 mark=0 时 `InsertDome` 报 `0x8002000F`"
      "（`DISP_E_PARAMNOTOPTIONAL`，中文「非选择性的参数」），★ **那个错误看不出是 mark 的问题**"
      "（与事实 33 同一类坑）。★ `swFmDome` **不存在**（枚举 0 命中、35 个合法常量里没有）"
      "⇒ 圆顶**走不了 `CreateDefinition`**，只能走 `IModelDoc2.InsertDome`（**`void` 返回**）。")
L2 = ("★★★ **同一轮查出 `sw_connect.get_com_member` 的一个危险设计**：它在**没有实参**时会"
      "「**先试调一次**」来分辨属性与方法 ⇒ ★ **对 COM 成员，「取」就等于「调」**！"
      "实证：`get_com_member(doc, \"InsertDome\")` **自己抛** `0x8002000F`（因为 `InsertDome` "
      "有 3 个必填参数）⇒ 说明它**真的调了一次**。⚠ **危险在于**：无必填参数且有副作用的成员"
      "（如 `InsertDeleteHole()`、任何 `File*` 写盘方法）会**被「取」这个动作静默执行**。"
      "⇒ 本轮最小修法：把 `DISP_E_PARAMNOTOPTIONAL` 也纳入「**返回成员、不调用**」"
      "（未改成"永不调用" —— 那会动到全仓库依赖的既有语义）。⚠ **`insert_dome` 起初完全不能工作，"
      "根因就是这个**（不是圆顶本身的问题）。")
L3 = ("⚠ **未查明**：① 我传 `Height=8`（毫米），而 Z 方向实测增长 **14.2222** —— **两者不等**，"
      "`Height` 的语义（圆顶是曲面，其包围盒高度与参数不是同一件事？）**未查明**；"
      "② **特征树里哪一个是圆顶未查明**（`FeatureByPositionReverse` 的顺序语义没查清 —— "
      "取列表最前得到的是 `凸台-拉伸1`）；③ `IDomeFeatureData2` 的读回（官方示例那条路）"
      "**到不了** ⇒ 标为**不可达**（官方示例写 `data.AccessSelections(...)`，而那族在 pywin32 "
      "迟到绑定下到不了 —— 事实 47/68）。⚠ 另外 `GetFeatureCount` 是**属性**不是方法（调它会得到 "
      "`'int' object is not callable`）。")

for c in d["capabilities"]:
    if c.get("id") == "part_and_features":
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        c["limitations"].insert(0, L1)
        c["limitations"].insert(1, L2)
        c["limitations"].insert(2, L3)
        print("  ok part_and_features 已更新")
    if c.get("id") == "com_plumbing":
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        c["limitations"].insert(0, L2)
        print("  ok com_plumbing 已更新")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

FACT = ("| 84 | **★★★ `sw_connect.get_com_member` 在"取"一个 COM 方法时**会真的把它调一次** —— "
        "对有副作用的成员，「取」就等于「调」** —— 2026-10-01（轮 143）在补 `dome` 时查出："
        "该函数「没有实参就先 `member()` 试一次」以分辨属性/方法，而**只把"
        "「找不到成员」（`-2147352573`）纳入"返回成员不调用"的白名单** ⇒ "
        "`DISP_E_PARAMNOTOPTIONAL`（`0x8002000F`，中文「非选择性的参数」）**会抛出去**。"
        "实证：`get_com_member(doc, \"InsertDome\")` **自己抛** `0x8002000F`"
        "（`InsertDome` 有 3 个必填参数）⇒ ★ 它**真的调了一次**。"
        "⚠⚠ **危险面**：**无必填参数且有副作用**的成员（`InsertDeleteHole()`、任何 `File*` 写盘方法）"
        "会**被"取"这个动作静默执行**。★ 最小修法：把 `DISP_E_PARAMNOTOPTIONAL` 也纳入"
        "「**返回成员、不调用**」（**未**改成"永不调用" —— 那会动到全仓库依赖的既有语义）。"
        "★★ 附带：**`insert_dome` 起初完全不能工作，根因就是这个**（不是圆顶本身）。"
        "★ 另记三条同轮的坑：① `InsertDome` 要求选面用 **mark=1**（官方 Remarks；用 mark=0 报的"
        "`0x8002000F` **看不出是 mark 的问题**）；② **`swFmDome` 不存在**（枚举 0 命中、不在 "
        "`CreateDefinition` 的 35 个合法常量里）⇒ 只能走 `IModelDoc2.InsertDome`（`void` 返回）；"
        "③ **`GetFeatureCount` 是属性不是方法**（调它得到 `'int' object is not callable`）。"
        "⚠ 未查明：`Height=8` 而 Z 增长 **14.2222**（语义待查）；特征树里哪一个是圆顶；"
        "`IDomeFeatureData2` 读回**不可达**（事实 47/68）。 | `tools/verify_dome_smoke.py`（**9/9**）；"
        "`tools/diag_insert_dome.py`（根因定位）；`scripts/sw_connect.py` 的 `get_com_member`；"
        "`C:\\swapi\\types\\IModelDoc2\\InsertDome.md` 的 Remarks；"
        "`C:\\swapi\\examples\\Create_and_Modify_Dome_Feature_Example_CSharp.md`；事实 33 / 40 / 47 / 68 |")

K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
if "会真的把它调一次" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 84")
else:
    print("  已有 84")
