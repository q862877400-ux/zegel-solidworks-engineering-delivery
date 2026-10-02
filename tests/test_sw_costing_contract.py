"""@brief `sw_costing` 的契约测试（**不连 SolidWorks**）。

# ── 来源 ──
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_sw_costing_contract.py
# 定位:   给 2026-10-01（轮 61）升 `verified` 的 `costing` 补**可离线跑**的契约测试。
#         起因是一个**真机抓到的真缺陷**：`read_cost_analysis` 等 7 处写的是 `int(x or -1)`，
#         而 `CostingType` 真值为 **`0`** 时会被吞成 **`-1`**（把「机加工」误报成「未知」）。
#         真机证明：修前 `costing_type=-1`，修后 **`0`**。
# 官方签名依据: `ICostAnalysis` / `ICostManager` / `ICostPart` / `IModelDocExtension` 的官方反射
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
for _p in (str(REPO), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_costing  # noqa: E402


class _Fake:
    """最小的假 COM 对象：按名字给值，并**记录收到的实参**。"""

    def __init__(self, **vals):
        self._vals = vals
        self.calls: list = []

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)

        def _get(*args):
            self.calls.append((name, args))
            return self._vals.get(name)

        return _get


# ── ① 核心：`_num` 不能吞掉合法的 0 ─────────────────────────────────

def test_num_preserves_a_legitimate_zero() -> None:
    """★★ **本文件存在的理由**：`0` 是合法值，`_num` 必须原样返回。

    ⚠ 反例（**修复前的写法**）：`int(get_com_member(x, "CostingType") or -1)`
    ⇒ `0 or -1` == **`-1`** ⇒ 静默给出错值。真机实测正是如此。
    """
    obj = _Fake(CostingType=0)
    assert sw_costing._num(obj, "CostingType", -1) == 0, "0 被吞掉了！"


def test_num_falls_back_only_on_none() -> None:
    """只有成员**缺席**（`None`）才回落。"""
    assert sw_costing._num(_Fake(X=None), "X", -1) == -1
    assert sw_costing._num(_Fake(X=0.0), "X", 9.9) == 0.0, "0.0 被吞掉了！"
    assert sw_costing._num(_Fake(X=7), "X", -1) == 7


def test_num_passes_arguments_through() -> None:
    """★ 成员**带参数**时要透传。

    ⚠ 这是我在验收脚本里踩到的：`GetManufacturingMethod(Int32)` 少传参数会得到
    `com_error: 非选择性的参数` —— **那个报错看不出是「少传了参数」**。
    """
    obj = _Fake(GetManufacturingMethod=0)
    assert sw_costing._num(obj, "GetManufacturingMethod", -1, 0) == 0
    assert obj.calls == [("GetManufacturingMethod", (0,))], obj.calls


# ── ② `read_cost_analysis` 端到端（假对象）──────────────────────────

def test_read_cost_analysis_keeps_zero_valued_fields() -> None:
    """`read_cost_analysis` 的**零值字段**必须原样出来（真机 `CostingType = 0`）。"""
    fake = _Fake(
        CostingTemplateName="machiningtemplate_default(englishstandard).sldctm",
        CostingType=0, LotSize=100, TotalQuantity=100,
        MarkUpType=2, MarkUpPercent=0.0,
        CurrencyCode="USD", CurrencyName="美元", CurrencySeparator=".",
        LengthUnit=1, MassUnit=1, UnitSystem=1,
        GetMaterialCost=3.2714499345031918,
        GetManufacturingCost=0.0, GetSetupCost=0.0,
        GetTotalCostToManufacture=3.2714499345031918,
        GetTotalCostToCharge=3.2714499345031918,
    )
    d = sw_costing.read_cost_analysis(fake)
    assert d["costing_type"] == 0, "costing_type 被吞成 -1 了（真机就是这个缺陷）"
    assert d["markup_type"] == 2
    assert d["markup_percent"] == 0.0
    assert d["manufacturing_cost"] == 0.0
    assert abs(d["material_cost"] - 3.2714499345031918) < 1e-12
    assert d["total_to_charge"] == d["total_to_manufacture"]
    assert d["currency_name"] == "美元"
    assert ".sldct" in d["template"]


def test_read_cost_analysis_rejects_none() -> None:
    """`None` ⇒ 显式报错（不静默给一堆默认值）。"""
    try:
        sw_costing.read_cost_analysis(None)
    except ValueError:
        return
    raise AssertionError("read_cost_analysis(None) 应抛 ValueError")


def test_read_cost_body_keeps_zero_valued_fields() -> None:
    """`read_cost_body` 的 `body_type` / `body_status` 同样不能吞 0。"""
    fake = _Fake(GetName="实体1", GetBodyType=0, BodyStatus=0, GetSWBody=object(),
                 GetCostAnalysis=object())
    d = sw_costing.read_cost_body(fake)
    assert d["body_type"] == 0 and d["body_status"] == 0
    assert d["has_sw_body"] is True and d["has_cost_analysis"] is True


# ── ③ 入口（真机确认的那条路）──────────────────────────────────────

def test_get_costing_manager_uses_the_extension_entry() -> None:
    """★ 入口必须是 `Extension.GetCostingManager`（**不是** `GetAddInObject(<ProgID>)`）。

    ⚠ 真机实测：4 个 ProgID（含 `swcCostingAddin.SwcAddin`）**全返 None**，
    而 `GetCostingManager()` 返回非 None ⇒ 后者才是正解。
    """
    marker = object()
    model = _Fake(Extension=_Fake(GetCostingManager=marker))
    assert sw_costing.get_costing_manager(model) is marker


def test_get_costing_manager_raises_when_extension_missing() -> None:
    """`Extension` 为 None ⇒ 显式报错（带原因），不返回 None 让人误以为「没有成本功能」。"""
    try:
        sw_costing.get_costing_manager(_Fake(Extension=None))
    except ValueError as exc:
        assert "Extension" in str(exc)
        return
    raise AssertionError("应抛 ValueError")
