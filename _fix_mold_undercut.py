import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")

# ── ① 修 sw_mold.mold_undercut_detect：**参数名照官方 + 方向校验** ──
P = R / "scripts" / "sw_mold.py"
t = P.read_text(encoding="utf-8")
i = t.find("def mold_undercut_detect")
j = t.find("\n\n\n", i)
OLD = t[i:j]
NEW = '''def mold_undercut_detect(model, *, col_undercut: int = 0, col_base: int = 0,
                         b_coord_input: bool = True, dx: float = 0.0,
                         dy: float = 0.0, dz: float = 1.0):
    """**底切检测**（官方 `IFeatureManager.MoldUndercutDetect`，6 参，返回 `Void`）。

    ★★ **2026-10-01（轮 167）按官方 md 的参数名与语义**（旧版参数名与官方**全不对应**）：
    ```
      Int32  ColUndercut   —— 某个方向上不可见、构成底切的面的**颜色**（COLORREF）
      Int32  ColBase       —— 不构成底切的面（除底切面外的全部）的**颜色**
      bool   BCoordInput   —— ★ **True = 启用坐标输入来指定拉拔方向**
      Double Dx/Dy/Dz      —— ★ **拉拔方向**的三个分量（仅当 `BCoordInput=True` 时生效）
    ```
    ⚠⚠⚠ **为什么旧版会弹模态框**（轮 167 根因）：
    旧签名是 `(direction, option, include_hidden, a, b, c)`，第 3 位传的是
    `include_hidden=False` —— 那**恰好落在官方第 3 参 `BCoordInput` 上** ⇒
    **"不启用坐标输入"** ⇒ SolidWorks 改用**模型自己已定义的拉拔方向**；
    而**空零件/未定义方向的零件上根本没有** ⇒ 弹「**此拔模方向尚未定义。**」且**卡住会话**。
    ⇒ ★ **根因解决**：默认 **`b_coord_input=True` + 非零方向 `(0,0,1)`**
      ⇒ **不依赖模型已定义方向** ⇒ **从根上不弹框**。

    :raises ValueError: `b_coord_input=True` 而方向**全零** ——
        零向量等于"没给方向"，会退回弹框那条路，故**在发调用之前就拒**（不硬编码、不静默）。
    :returns: ``None``（官方是 ``Void``）。⚠ **检测结果不在返回值里**（如何取**仍未查证**）。
    """
    if b_coord_input and not any((float(dx), float(dy), float(dz))):
        raise ValueError(
            "b_coord_input=True 但拉拔方向是**零向量** (0,0,0) —— "
            "零向量不等于"给了方向"，SolidWorks 会退回「用模型已定义方向」那条路，"
            "而在**未定义方向**的零件上会**弹模态框并卡住会话**。"
            "⇒ 请给一个**非零**方向（如默认的 (0,0,1)），或显式 `b_coord_input=False`"
            "（⚠ 后者要求模型**已定义**拉拔方向，否则同样会弹框）。"
        )
    fm = get_com_member(model, "FeatureManager")
    return get_com_member(fm, "MoldUndercutDetect",
                          int(col_undercut), int(col_base), bool(b_coord_input),
                          float(dx), float(dy), float(dz))
'''
t = t[:i] + NEW + t[j:]
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok ① sw_mold.mold_undercut_detect 已按官方参数名改 + 方向校验")
