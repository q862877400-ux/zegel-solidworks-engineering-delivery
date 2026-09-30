from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_misumi.py")
s = p.read_text(encoding="utf-8")

old = '''# ⚑ 接入三件套（本机实测，缺一不可）
# ----------------------------------------
#   ① 主机     https://api.cn.misumi.com.cn
#   ② 请求头   applicationId: 77f56fb2-4165-4116-b82f-e495838bb6e1
#               —— 该值在官网页面 ``window.__NUXT__.config`` 里**明文**给出；
#                  日站社区文档称其为「公开应用标识（非用户密钥）」
#   ③ 会话     先 GET 官网首页拿 cookie（实测得到 ``acw_tc``）'''
new = '''# ⚑ 接入三件套（本机实测，缺一不可）
# ----------------------------------------
#   ① 主机     https://api.cn.misumi.com.cn
#   ② ★ applicationId 必须走 **query string**（不是请求头）
#               值 77f56fb2-4165-4116-b82f-e495838bb6e1，
#               在官网页面 ``window.__NUXT__.config`` 里**明文**给出；
#               日站社区文档称其为「公开应用标识（非用户密钥）」。
#               ⚠⚑ 本机四组对照实测（2026-09-30）——
#                  只放 header          -> 400 API000101
#                  完全不带            -> 400 API000101
#                  **只走 query**       -> 200 ✅
#                  两者都带             -> 200 ✅（header 是冗余的）
#                  ⇒ 放 header **不算数**，必须走 query。
#   ③ 会话     先 GET 官网首页拿 cookie（实测得到 ``acw_tc``）'''
assert old in s, "块1"
s = s.replace(old, new, 1)

old2 = '''    s.headers.update({
        "User-Agent": _UA,
        "applicationId": APPLICATION_ID,
        "lang": "CHN",
        "Referer": LANDING,
        "Origin": "https://www.misumi.com.cn",
    })'''
new2 = '''    # ⚠ applicationId **只**由 ``_get`` 拼进 query string —— 放 header 无效
    #   （四组对照实测：只放 header -> 400 API000101）
    s.headers.update({
        "User-Agent": _UA,
        "Referer": LANDING,
        "Origin": "https://www.misumi.com.cn",
    })'''
assert old2 in s, "块2"
s = s.replace(old2, new2, 1)

old3 = '''    r = s.get(API_HOST + path,
              params=dict(params, applicationId=APPLICATION_ID, lang="CHN"),
              timeout=20)'''
new3 = '''    r = s.get(API_HOST + path,
              params=dict(params, applicationId=APPLICATION_ID, lang="CHN"),
              timeout=20)   # applicationId 必须走 query（见文件头四组对照）'''
assert old3 in s, "块3"
s = s.replace(old3, new3, 1)
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  已改：header 移除，注释写明四组对照证据")