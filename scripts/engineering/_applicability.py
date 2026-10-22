"""「适用域」判定的单一实现（原在两个 dataclass 里各有一份）。"""
# ── 来源 ───────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/engineering/_applicability.py
# 定位:   ★ 2026-10-22（仓库统一化）：`applies_to` 原在
#         `compiler.MethodSpec` 与
#         `rules.Rule` 两个 dataclass 里**各有一份、逐字相同**（都是
#         「`device_class in (self.applicable_devices or ())`」）⇒ 抽成 mixin，两个类继承。
#         判据 = `scripts/check_repo_uniformity.py` 指标⑤「跨文件同函数体组」只降不升。
# 官方依据: 不适用（本模块只做集合属性判定）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ──────────────────────────────────────────────────────────────
from __future__ import annotations


class ApplicabilityMixin:
    """★ 「适用域」形状：实现类必须有 `applicable_devices` 字段（元组）。

    ★★ **空适用域 ⇒ 不适用任何类别** —— ★ 不默认「通用」：
      没写适用域的条目是「还没标」，不是「什么都适用」✗
    """

    applicable_devices: tuple = ()

    def applies_to(self, device_class: str) -> bool:
        """⇒ 本条目是否适用于 `device_class`。"""
        return device_class in (self.applicable_devices or ())
