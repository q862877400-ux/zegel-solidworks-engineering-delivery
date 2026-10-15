import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\probe_dwg_magic.py")
t = P.read_text(encoding="utf-8")

OLD = '''        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc)
        sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, 60.0, 40.0)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, "草图1", 10.0)
        print("  造出 60x40x10 的板")'''
NEW = '''        doc = sw_connect.new_document(sw, "part")
        #: ⚠⚠ 第一版用**普通拉伸件** ⇒ 两条都报
        #: `ValueError: 导出展开 DXF 前必须先保存钣金零件`（**错误清晰、是对的**）
        #: ⇒ ★ 零件路径要求：**钣金件** + **必须先保存** ⇒ 改用钣金基体法兰。
        from scripts import sw_sheet_metal
        sw_part.start_sketch(doc)
        sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, 60.0, 40.0)
        sw_part.end_sketch(doc)
        sw_sheet_metal.create_base_flange(
            doc, sketch_ref="草图1", thickness_mm=1.0, bend_radius_mm=1.0, depth_mm=40.0)
        #: ★ 官方要求先保存（本探针存到 **output/**，scratch 用途，收尾会删）
        SAVED = Path(r"D:\\AI\\SW\\output\\magic-probe-part.sldprt")
        if SAVED.exists():
            SAVED.unlink()
        sw_connect.save_document(doc, str(SAVED))
        print("  造出钣金件并**已保存**到 %s" % SAVED.name)'''
assert OLD in t, "锚点不符"
t = t.replace(OLD, NEW, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已改用钣金件 + 先保存")
