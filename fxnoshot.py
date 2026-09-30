from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_batch.py")
s = p.read_text(encoding="utf-8")
# 删掉截图找按钮的整个函数
a = s.index("def _bottom_button_candidates(")
b = s.index("def _wait_generated(")
s = s[:a] + s[b:]
# 生成段：只用 UIA（并集遍历已能拿到按钮）
a2 = s.index("    # 组装候选点：")
b2 = s.index("    # ⑤ **逐个试候选 + 验收**")
new = '''    # ⚑ 只用 UIA 定位按钮 —— 并集遍历修好后 ``L.locate`` 已能稳定拿到
    #   （实测 `Button '生成预览' (2362,1271,2445,1303)`）。
    #   **不再有截图兜底**：截图是症状级补丁，根因是遍历漏节点，已修。
    if btn is None:
        rec["stage"] = "无生成按钮"
        _shot(h, w, "FAIL_nobtn_%s" % code)
        rec["secs"] = time.time() - t0
        return rec
    r_btn = btn.rectangle()
    cands = [((r_btn.left + r_btn.right) // 2, (r_btn.top + r_btn.bottom) // 2)]
'''
s = s[:a2] + new + s[b2:]
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("batch 已去掉截图兜底")