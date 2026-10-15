from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_misumi.py")
s = p.read_text(encoding="utf-8")
old = '''# ⚠ 为何不实现登录与下载'''
new = '''# ⚠ 官方明写的两条硬约束（调研 2026-09-30 逐条核对官网原文）
# ------------------------------------------------------------------
# 1. **下载 CAD 只要「个人会员」**，不需要企业账号、不需要订购权限
#    （https://www.misumi.com.cn/cmsweb/view/guide/5077/ 的权限矩阵：
#    未注册 ✗ / 个人会员 ✓ / 企业会员 ✓）
#    ⇒ 正规路径是**免费注册一个个人会员**，不是逆向登录。
#    ⚠ 注册本身要手机号 + 短信码 + 拖动滑块 + 身份 + 邮箱
#      （guide/5075），且**拒绝自然人注册**（contents/terms/use.html 第1条）。
# 2. **CAD 输出格式含 SolidWorks ≥2015 原生 .sldprt**
#    （https://www.misumi.com.cn/cmsweb/view/guide/5030/）⇒ 目录型标准件
#    不必自己从 STEP 转。
#    另：2D 图纸包 https://www.misumi.com.cn/linked/material/*.zip
#    社区实测**免登录可直取**（未在本项目核实，标为社区经验）。
#
# ⚠ 为何不实现登录与下载'''
assert old in s
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  官方硬约束已补入")