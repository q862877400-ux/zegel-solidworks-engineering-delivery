"""临时只读脚本：打印本仓库在 param 域的操作名集合（走 build_union_map 自己的口径，用完即删）。"""
import sys

sys.path.insert(0, r"D:\AI\SW\tools")
import build_union_map as B  # type: ignore

ours = B._our_operations()
print("our operations:", len(ours))
param = {op: d for op, d in ours.items() if d == "param"}
print("our param-domain ops:", len(param))
for op in sorted(param):
    print("   ", op)

print()
print("union param ops vs ours:")
union = {"delete_equation", "design_table", "design_table_create", "design_table_refresh",
         "diameter_dimension", "dimension", "equation", "global_var",
         "link_dimension_to_equation", "manage_design_table", "relation"}
for op in sorted(union):
    print("  %-28s ours=%s" % (op, op in ours))
