from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_batch.py")
s = p.read_text(encoding="utf-8")
# ⚠ 我改了 first_result_point 的签名（去掉 hwnd），但忘了改调用点：
#   传两个参数 ⇒ win 收到 hwnd(int)、log 收到 win ⇒ 必然「无搜索结果」。
s = s.replace("pt = SR.first_result_point(h, w)", "pt = SR.first_result_point(w)")
s = s.replace("pt2 = SR.first_result_point(h, w)", "pt2 = SR.first_result_point(w)")
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("已修 batch 的两处调用")