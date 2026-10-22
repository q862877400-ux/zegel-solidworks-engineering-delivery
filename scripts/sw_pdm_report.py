"""★ PDM 相邻证据工具的**工具层薄包装**（★ 显式签名，只为让参数绑定门禁对得上）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（真活在 `scripts/sw_pdm.py` 的 `collect_pdm_evidence`）
# 文件:   scripts/sw_pdm_report.py
# 定位:   ★ 规格 220（目标 145/145）第 24 轮：★ **让 `inject='model'` 与目标函数形参名
#           一致** ✓
# 官方依据: ★ 见 `scripts/sw_pdm.py` 的来源块（逐成员记着接口/成员）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ★★ 为什么要有这一层（★ 都是真机/门禁读数逼出来的）：
#   · ★ `collect_pdm_evidence(pdm_document)` 的形参名与 `inject="model"` **不符** ✗
#     ⇒ ★ 参数绑定门禁逐字判死两条：① inject 与形参不符 ② 必填形参未声明 ✓
#   · ★ 而 `param_alias={'model': 'pdm_document'}` **也没让门禁放行** ✗（第 22 轮实测）
#   · ★ 规格 219 末轮还实测过：★ `function=` 指向 `(model, **kwargs)` **同样被判死** ✗
#   ⇒ ★★ 唯一稳的形态：★ **目标函数用显式、名字对得上的形参** ⇒ ★ 就是这个薄包装 ✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations


def collect_pdm_evidence_report(model) -> dict:
    """★ 读一份文档的 **PDM 相邻证据**（★ 自定义属性 / 配置 / 外部引用）⇒ ★ 与工具层契约对齐 ✓

    ★ 真活在 `sw_pdm.collect_pdm_evidence`（★ 本层只做**形参名对齐**，★ 不加语义）✓
    ★★ 如实标注：★ 这是 **PDM 相邻**，★ **不是** SolidWorks PDM Professional（★ 那需 PDM 许可证）✓
    """
    import sw_pdm

    return sw_pdm.collect_pdm_evidence(model)
