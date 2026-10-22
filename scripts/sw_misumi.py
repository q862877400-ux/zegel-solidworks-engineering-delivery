r"""米思米（MISUMI）中国站检索客户端 —— 免登录可用的部分。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   米思米中国站 https://www.misumi.com.cn/（Nuxt SSR，本机可直连）
# 定位:   标准件来源之一。本模块只封装**免登录即可调用**的检索接口。
# 调研报告: D:\AI\SW\docs\research-misumi-api.md（含全部 URL 与引文）
#
# ⚑ 接入三件套（本机实测，缺一不可）
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
#   ③ 会话     先 GET 官网首页拿 cookie（实测得到 ``acw_tc``）
#
# ⚠ 能力边界（本机逐个端点实测，2026-09-30）
# ------------------------------------------
#   ✅ 免登录可用
#      /api/v1/category/search              13 个大类
#      /api/v1/brand/search                 1,267 个品牌
#      /api/v1/keyword/search               关键词联想
#      /api/v1/partNumber/suggest           规范化型号 + 品牌 + innerCode
#      /api/v1/fullText/search              全文检索（实测「轴承」1,287 条）
#   ❌ 需登录态（本模块**不实现**，理由见下）
#      /api/v1/cad/download      -> 400 「seriesCode为必须输入项」
#      /api/v1/cad/preview       -> 400 「seriesCode为必须输入项」
#      /api/v1/cad/termsOfUse    -> 400 「sessionId为必须输入项」
#      rd-cn-cadapi / rd-cn-caddata  -> 403
#   ❓ 参数未试对
#      /api/v1/partNumber/search         400（规格明细，端点在、参数未还原）
#      /api/v1/fullText/searchInCADComponents  200 但 totalCount 恒为 0
#
# ⚠ 官方明写的两条硬约束（调研 2026-09-30 逐条核对官网原文）
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
# ⚠ 为何不实现登录与下载
# ----------------------
# · 外部调研（2026-09-30）确认：**米思米没有对外发布的开放 API / 开发者门户**，
#   10 条候选文档路径全 404，根路径 401。``/api/v1/*`` 是其电商前端**自用内部 API**，
#   无公开契约、随时可能变。
# · 调研同时确认：中国站**无 WAF 可直连**（日站有 Akamai 拦截）。
#   ⚠ 这是**防护投入差异，不构成使用许可** —— 内部 API 仍应按「非公开」对待。
# · 正路是官方 SolidWorks 插件（需米思米账号，官网申请后邮件下发安装包）
#   或企业级 PunchOut / cXML（需企业合同）。
# ⇒ 本模块**只做免登录检索**。要文件请走官方插件或商务通道。
#
# 覆盖:   后续同级定义
# ⚠ 本模块不含任何 SolidWorks 调用（与本仓库其它模块无耦合）
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "API_HOST",
    "APPLICATION_ID",
    "LANDING",
    "session",
    "list_categories",
    "list_brands",
    "suggest_keywords",
    "suggest_part",
    "full_text_search",
    "CAPABILITY",
]

API_HOST = "https://api.cn.misumi.com.cn"
LANDING = "https://www.misumi.com.cn/"
#: 官网页面明文给出；日站社区文档称其为「公开应用标识，非用户密钥」
APPLICATION_ID = "77f56fb2-4165-4116-b82f-e495838bb6e1"

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
)

#: 本机实测的能力清单，供调用方自查（免登录 / 需登录 / 参数未还原）
CAPABILITY: dict[str, str] = {
    "/api/v1/category/search": "免登录 OK，13 个大类",
    "/api/v1/brand/search": "免登录 OK，1,267 个品牌",
    "/api/v1/keyword/search": "免登录 OK，关键词联想",
    "/api/v1/partNumber/suggest": "免登录 OK，型号+品牌+innerCode",
    "/api/v1/fullText/search": "免登录 OK，全文检索",
    "/api/v1/cad/download": "需登录态，本模块不实现",
    "/api/v1/cad/preview": "需登录态，本模块不实现",
    "/api/v1/partNumber/search": "端点存在，参数未还原",
}


def session() -> Any:
    """建一个带必需请求头的会话。⚠ 依赖 ``requests``，缺失时**明说**。"""
    try:
        import requests
    except ImportError as exc:  # noqa: PERF203
        raise ImportError("sw_misumi 需要 requests：pip install requests") from exc
    s = requests.Session()
    # ⚠ applicationId **只**由 ``_get`` 拼进 query string —— 放 header 无效
    #   （四组对照实测：只放 header -> 400 API000101）
    s.headers.update(
        {
            "User-Agent": _UA,
            "Referer": LANDING,
            "Origin": "https://www.misumi.com.cn",
        }
    )
    s.get(LANDING, timeout=20)  # 先拿 acw_tc cookie
    return s


def _get(path: str, sess: Any = None, **params: Any) -> dict[str, Any]:
    s = sess or session()
    r = s.get(
        API_HOST + path,
        params=dict(params, applicationId=APPLICATION_ID, lang="CHN"),
        timeout=20,
    )  # applicationId 必须走 query（见文件头四组对照）
    r.raise_for_status()
    return r.json()


def list_categories(sess: Any = None) -> list[dict[str, Any]]:
    """13 个大类（机械相关：mech / mech_screw / mech_material / press / mold / injection）。"""
    return _get("/api/v1/category/search", sess, categoryLevel=1).get(
        "categoryList", []
    )


def list_brands(sess: Any = None) -> list[dict[str, Any]]:
    """1,267 个品牌。⚠ 响应体较大，建议只调一次并缓存。"""
    return _get("/api/v1/brand/search", sess).get("brandList", [])


def suggest_keywords(keyword: str, sess: Any = None) -> list[str]:
    """关键词联想（输入「丝杠」返回丝杠模组/丝杆支座/丝杆螺母…）。"""
    return _get("/api/v1/keyword/search", sess, keyword=keyword).get("keywordList", [])


def suggest_part(
    keyword: str, count: int = 10, sess: Any = None
) -> list[dict[str, Any]]:
    """型号建议 —— **本模块最有用的一步**。

    返回每条含 ``partNumber`` / ``brandCode`` / ``brandName`` / ``innerCode``，
    其中 ``innerCode`` 是米思米内部主键（后续查规格要用）。
    """
    return _get(
        "/api/v1/partNumber/suggest",
        sess,
        keyword=keyword,
        count=count,
        field="@default,partNumberList.innerCode",
    ).get("partNumberList", [])


def full_text_search(
    keyword: str, page: int = 1, page_size: int = 10, sess: Any = None
) -> dict[str, Any]:
    """全文检索（实测「轴承」totalCount=1,287）。返回含 ``totalCount`` / ``resultList``。"""
    return _get(
        "/api/v1/fullText/search",
        sess,
        keyword=keyword,
        page=page,
        pageSize=page_size,
        field="@default",
    )
