"""带封闭拒绝码的异常基类（原先 4 个模块各写一份 __init__）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/engineering/_coded_error.py
# 定位:   ★ 2026-10-22（仓库统一化 · 待办「同一功能多份实现」）：`__init__` 原先在
#         `design_rules.RuleError` / `selection_calc.CalcError` /
#         `standard_parts.TableError` / `linkage.LinkageError` 里**各有一份、逐字相同**
#         （★ 只差 assert 的文案）⇒ 抽出本基类，四者只声明 `CODES` 与 `ASSERT_LABEL`。
#         判据 = `scripts/check_repo_uniformity.py` 指标⑤「跨文件同函数体组」只降不升。
# 官方依据: 不适用（本模块只做异常构造，不调 COM、不碰外部接口）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations


class CodedError(Exception):
    """★ 带**封闭拒绝码**的异常：★ 码必须在子类的 `CODES` 里，否则 `assert` 当场炸。

    ★ 为什么用「封闭码」：让上层能**机械判**失败类别（不必解析消息文本）；
      码表写死在类上是刻意的 —— ★ 新增码必须改代码，★ 不允许运行期拼一个出来。

    ★ 子类只需声明两样：
      · `CODES` —— 允许的拒绝码元组（★ 封闭词表）
      · `ASSERT_LABEL` —— 断言失败时那句话的前缀（★ 保留各模块自己的措辞）
    """

    #: 允许的拒绝码（★ 子类必须覆盖）
    CODES: tuple[str, ...] = ()
    #: 断言失败文案的前缀（★ 子类可覆盖；默认与四个原模块一致）
    ASSERT_LABEL = "★ 非法拒绝码"

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "%s：%r" % (self.ASSERT_LABEL, code)
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))
