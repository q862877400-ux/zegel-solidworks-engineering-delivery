import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_in_context_reference_smoke.py")
t = P.read_text(encoding="utf-8")

OLD = '''        sw_part.start_sketch(asm)
        skm = sw_connect.safe_get_com_member(asm, "SketchManager")
        sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")'''
NEW = '''        #: ⚠⚠⚠ **关键**：进入「在上下文编辑」之后 **`sw.ActiveDoc` 已经变成那个零件** ——
        #: 草图操作必须落在**活动文档**上，**不是 `asm`**。
        #: ★ 轮 161 我一直对 `asm` 开草图/投影 ⇒ `convert_entities` 返回 ok
        #:   而**草图里一个实体都没有**（因为它作用在另一个文档上）。
        tgt_doc = sw_connect.safe_get_com_member(sw, "ActiveDoc") or asm
        ev["active_doc_is_asm"] = (tgt_doc is asm)
        print("     活动文档就是 asm 吗: %s（**应当不是**）" % ev["active_doc_is_asm"])
        sw_part.start_sketch(tgt_doc)
        skm = sw_connect.safe_get_com_member(tgt_doc, "SketchManager")
        sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")'''
assert OLD in t, "锚点不符"
t = t.replace(OLD, NEW, 1)

t = t.replace("            sw_sketch_edit.convert_entities(asm)",
              "            sw_sketch_edit.convert_entities(tgt_doc)", 1)
t = t.replace("        sw_part.end_sketch(asm)", "        sw_part.end_sketch(tgt_doc)", 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 草图操作已改到**活动文档**")
