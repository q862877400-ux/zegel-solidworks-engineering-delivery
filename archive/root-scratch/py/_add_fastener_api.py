import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_hole_features.py")
t = P.read_text(encoding="utf-8")

NEW = '''

def list_fastener_types(sw, standard_name: str, hole_type_id: int = 0):
    """列出某孔标准下的**紧固件类型**（官方 `IHoleStandardsData.GetFastenerTypes`）。

    ★ 真机量到：出参是两组**各 14 元**的 `tuple` —— 一个是 **ID**、一个是**名称**，
    **一一对应**。⚠ **名称随 UI 语言变**（本机中文 UI ⇒ 拿到 `'六角精致螺栓'` 这样的中文）。

    :param standard_name: 孔标准名，取自 `list_hole_standards()` 的 `name`
        （例 `'ANSI Inch'` / `'ISO'`）。
    :returns: `[{"id": int, "name": str}, …]`。
    :raises RuntimeError: 拿不到 `IHoleStandardsData`，或官方返回 `False`。
    """
    data = _hole_standards_data(sw, hole_type_id)
    ids, names = _out_container(), _out_container()
    ok = get_com_member(data, "GetFastenerTypes", str(standard_name), ids, names)
    if not ok:
        raise RuntimeError(
            "IHoleStandardsData.GetFastenerTypes(%r) 返回 False —— "
            "常见原因：标准名拼错（用 `list_hole_standards()` 里的 `name`）" % standard_name
        )
    return _pair(ids, names, "FastenerTypes")


def list_fastener_table_types(sw, standard_name: str, fastener_id: int,
                              hole_type_id: int = 0):
    """列出某紧固件的**表类型 ID**（官方 `IHoleStandardsData.GetFastenerTableTypes`）。

    ⚠ **官方第 2 参是 `Int32`（紧固件 ID），不是尺寸名** ——
    真机第一版就栽在这（传尺寸名 ⇒ 「类型不匹配」，位置 2）。
    紧固件 ID 取自 `list_fastener_types()` 的 `id`。

    :returns: `[int, …]`（本机实测：`GetFastenerTableTypes('ANSI Inch', 4)` ⇒ `[0, 1, 2]`）。
    :raises RuntimeError: 拿不到数据、或官方返回 `False`。
    """
    data = _hole_standards_data(sw, hole_type_id)
    out = _out_container()
    ok = get_com_member(data, "GetFastenerTableTypes", str(standard_name),
                        int(fastener_id), out)
    if not ok:
        raise RuntimeError(
            "IHoleStandardsData.GetFastenerTableTypes(%r, %r) 返回 False —— "
            "常见原因：`fastener_id` 不在 `list_fastener_types()` 返回的 id 里"
            % (standard_name, fastener_id)
        )
    return _as_list(out)


def get_fastener_table(sw, standard_name: str, fastener_id: int, table_id: int,
                       hole_type_id: int = 0):
    """取某紧固件的**孔表本体**（官方 `IHoleStandardsData.GetFastenerTable`）。

    ⚠⚠ **本函数当前「不可用」（2026-10-01 轮 125 真机实测）** ——
    官方签名 `Boolean GetFastenerTable(String StandardName, Int32 FastenerID,
    Int32 TableID, **out Object** HoleTable)`，第 4 参是 `out IHoleDataTable`。
    用**同一套**已经验过的容器形态 `VARIANT(VT_BYREF|VT_VARIANT, None)` 传：
    ```
    GetFastenerTable('ANSI Inch', 4, 0) ⇒ com_error -2147352571「类型不匹配」**位置 4**
    GetFastenerTable('ANSI Inch', 4, 1) ⇒ 同上
    GetFastenerTable('ANSI Inch', 4, 2) ⇒ 同上
    ```
    ★ **同族的另外三个成员用同一形态都通**（`GetHoleStandards` / `GetFastenerTypes` /
    `GetFastenerTableTypes`）⇒ **只有这一个到不了**。
    ⚠ **按事实 53 停手**（不再变着法试）；保留本函数作**可复算的证据**。

    :raises RuntimeError: 取不到表（当前必然）。
    """
    data = _hole_standards_data(sw, hole_type_id)
    out = _out_container()
    ok = get_com_member(data, "GetFastenerTable", str(standard_name),
                        int(fastener_id), int(table_id), out)
    if not ok:
        raise RuntimeError(
            "IHoleStandardsData.GetFastenerTable(%r, %r, %r) 返回 False —— "
            "⚠ 真机实测该成员**在 pywin32 后台上报「类型不匹配（位置 4）」**，"
            "属同族里唯一到不了的一个（见模块来源块与已知事实）"
            % (standard_name, fastener_id, table_id)
        )
    return _out_value(out)
'''

ANCHOR = "\n\n# ── 来源 ─"
i = t.index(ANCHOR)
if "def list_fastener_types" not in t:
    t = t[:i] + NEW + t[i:]
    P.write_text(t, encoding="utf-8")
    print("  ok 已加 list_fastener_types / list_fastener_table_types / get_fastener_table")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
