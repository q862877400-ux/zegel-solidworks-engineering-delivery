"""修一个**真实运行时 bug**：被 `derived_args` 消费的 spec 字段必须显式标记「不传」。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁，非第三方移植）
# 文件:   D:\\AI\\SW\\patch_consumed_params.py
# 定位:   batch4 的守卫测试抓到的 bug：注册器把**所有**声明参数都当 kwarg 传给目标函数，
#         而 **spec 字段**（`thickness_mm` 等）是由 `derived_args` 消费的、
#         目标函数（如 `create_base_flange(model, sketch_ref, spec)`）**并不接受**它们
#         ⇒ **真机 `TypeError: unexpected keyword argument`**。
#
#  ⚠⚠ **batch3 也中招** —— 它是我上一轮写的，当时那批测试**没覆盖「假目标收 kwargs」这条路**，
#     所以绿灯了但真机跑不了。**⇒ 这轮的价值就是把它堵掉。**
#
#  ⚠ 为什么用**已有的** `param_alias={name: None}` 而不是新加一个机制：
#     注册器早就定义了这个语义（「由解析器/派生器消费，**不传给目标函数**」），
#     spec 字段正是它的第二个使用者。**能复用就不新增**（本轮不再加第 4 个机制）。
#     并且守卫测试会强制：**每个声明参数要么映射到真形参、要么 alias=None、要么进 spec。**
#
# 官方签名依据: 不适用（纯 Python 文本补丁）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BATCH3 = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch3.py")
BATCH4 = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch4.py")

HELPER = '''

def _consumed(*names: str) -> dict:
    """构造 `param_alias`：**这些入参由 `derived_args` 消费，不传给目标函数**。

    ⚠ 为什么必须显式：注册器会把每个声明参数当 kwarg 传给目标函数，
    而 spec 字段（如 `thickness_mm`）目标函数**并不接受** ⇒ 不标记就 `TypeError`。
    **⇒ 显式，不靠猜**（本项目一贯纪律）。
    """
    return {n: None for n in names}

'''


def patch_batch3() -> int:
    t = BATCH3.read_text(encoding="utf-8")
    # ① 插入 helper
    anchor = "#: 长度字段 → 米"
    if anchor not in t:
        print("  ✗ batch3 未找到插入锚点")
        return 1
    t = t.replace(anchor, HELPER.strip() + "\n\n\n" + anchor, 1)

    # ② 两处 param_alias 展开
    t = t.replace(
        '        param_alias={"sketch_name": "sketch_ref"},\n'
        '        derived_args=lambda p: {"spec": _base_flange_spec(p)},',
        '        param_alias=dict(\n'
        '            {"sketch_name": "sketch_ref"},\n'
        '            **_consumed("thickness_mm", "bend_radius_mm", "depth_mm", "k_factor",\n'
        '                        "relief_ratio", "reverse_direction", "reverse_thickness"),\n'
        '        ),\n'
        '        derived_args=lambda p: {"spec": _base_flange_spec(p)},', 1)
    t = t.replace(
        '        param_alias={"sketch_name": "sketch_ref"},\n'
        '        derived_args=lambda p: {"spec": _one_bend_spec(p)},',
        '        param_alias=dict(\n'
        '            {"sketch_name": "sketch_ref"},\n'
        '            **_consumed("bend_radius_mm", "angle_deg", "reverse_direction",\n'
        '                        "use_default_radius"),\n'
        '        ),\n'
        '        derived_args=lambda p: {"spec": _one_bend_spec(p)},', 1)
    BATCH3.write_text(t, encoding="utf-8")
    print("  ✓ batch3：新增 _consumed helper + 2 处 param_alias 展开")
    return 0


def patch_batch4() -> int:
    t = BATCH4.read_text(encoding="utf-8")
    anchor = "_MM = 0.001"
    if anchor not in t:
        print("  ✗ batch4 未找到插入锚点")
        return 1
    t = t.replace(anchor, anchor + "\n" + HELPER, 1)

    reps = [
        ('        param_alias={"selection": None},\n        pre_call=_pre_edge_flange,',
         '        param_alias=dict(\n'
         '            {"selection": None},\n'
         '            **_consumed("bend_radius_mm", "flange_length_mm", "angle_deg",\n'
         '                        "use_default_radius", "reverse_direction"),\n'
         '        ),\n        pre_call=_pre_edge_flange,'),
        ('        param_alias={"selection": None},   # 同上：由 pre_call 消费，不进函数\n'
         '        pre_call=_pre_gusset,',
         '        param_alias=dict(\n'
         '            {"selection": None},\n'
         '            **_consumed("thickness_mm", "profile_distance_1_mm",\n'
         '                        "profile_distance_2_mm", "profile_angle_deg"),\n'
         '        ),\n        pre_call=_pre_gusset,'),
        ('        param_alias={"selection": None},   # 同上：由 pre_call 消费，不进函数\n'
         '        pre_call=_pre_draft,',
         '        param_alias=dict(\n'
         '            {"selection": None},\n'
         '            **_consumed("angle_deg", "depth_mm", "reverse_direction"),\n'
         '        ),\n        pre_call=_pre_draft,'),
    ]
    n = 0
    for old, new in reps:
        if old in t:
            t = t.replace(old, new, 1)
            n += 1
        else:
            print("  ⚠ batch4 未匹配一处：%s" % old[:46])
    # swept：所有 spec 字段都消费
    old_swept = '        param_alias={"path_selection": None, "profile_selection": None},'
    new_swept = ('        param_alias=dict(\n'
                 '            {"path_selection": None, "profile_selection": None},\n'
                 '            **_consumed(\n'
                 '                "start_offset_mm", "end_offset_mm", "thickness_mm",\n'
                 '                "bend_radius_mm", "use_default_radius", "flange_position",\n'
                 '                "flatten_along_path", "trim_side_bends",\n'
                 '                "use_default_bend_relief", "use_gauge_table",\n'
                 '                "use_material_parameters", "override_default_sheet_metal_parameters",\n'
                 '                "reverse_direction",\n'
                 '            ),\n'
                 '        ),')
    if old_swept in t:
        t = t.replace(old_swept, new_swept, 1)
        n += 1
    else:
        print("  ⚠ batch4 swept 未匹配")
    BATCH4.write_text(t, encoding="utf-8")
    print("  ✓ batch4：%d/4 处 param_alias 展开" % n)
    return 0


def main() -> int:
    rc = patch_batch3()
    patch_batch4()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
