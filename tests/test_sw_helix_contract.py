"""螺旋线模块的守卫测试（**不依赖 `mcp` 库、不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_sw_helix_contract.py
# 定位:   守 `scripts/sw_helix.py`（轮 104：从「真缺」档补的第一条能力）。
# 官方签名依据: `iface_sldworks.txt` + `C:\\swapi\\types\\IModelDoc2\\InsertHelix.md`
# 许可:   本仓库 MIT。无第三方代码引入。
#
# ★ **为什么这几条判据重要**：
#   本模块**没有真机运行证据**（等级 `stitched`）⇒ **静态判据是它唯一的防线**。
#   尤其「枚举值」与「单位换算」—— 本模块第一版**把两个枚举值写反了**（凭记忆），
#   被查证拦下 ⇒ 这里把两件事都钉住。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (REPO_ROOT, REPO_ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from scripts import sw_helix  # noqa: E402


#: ★ 官方枚举值（**两源互证**：反射 `enum_values_sldworks.txt` +
#: `C:\\swapi\\enums\\swHelixDefinedBy_e.md`）。
#: ⚠ 独立抄在这里 —— 若实现里被改错，这条会红。
OFFICIAL_HELIX_DEFINED_BY = {
    "pitch_and_revolution": 0,
    "height_and_revolution": 1,
    "height_and_pitch": 2,
    "spiral": 3,
}


def test_helix_enum_values_match_the_official_two_sources():
    """@brief ★ 枚举值必须与官方一致 —— **本模块第一版正是这里写反了**。"""
    assert sw_helix.HELIX_DEFINED_BY == OFFICIAL_HELIX_DEFINED_BY


def test_helix_args_match_the_official_order():
    """@brief 官方 10 个参数，顺序一个不差。"""
    assert sw_helix.HELIX_ARGS == (
        "reversed", "clockwise", "tapered", "outward", "helix_def",
        "height_mm", "pitch_mm", "revolution", "taper_angle_deg", "start_angle_deg",
    )


def test_insert_helix_signature_exposes_exactly_those_units():
    """@brief 公开签名里**长度参数必须以 `_mm` 结尾、角度以 `_deg` 结尾**（并入规则 2）。"""
    params = list(inspect.signature(sw_helix.insert_helix).parameters)
    assert params[0] == "model"
    for name in ("height_mm", "pitch_mm", "taper_angle_deg", "start_angle_deg"):
        assert name in params, "并入规则 2：长度/角度参数必须在签名里且带单位后缀"


class _FakeFeature:
    def __init__(self, name):
        self._n = name

    @property
    def Name(self):
        return self._n


class _FakeExtension:
    """桩：`GetLastFeatureAdded()`（轮 121 改用它，不再用 `FirstFeature`）。"""

    def __init__(self, feat):
        self._feat = feat

    def GetLastFeatureAdded(self):      # noqa: N802 - 官方成员名
        return self._feat


class _FakeModel:
    """桩：记下 10 个实参，并给一个「刚加进去」的特征。"""

    def __init__(self, feature_name="Helix1"):
        self.calls = []
        self._feat = _FakeFeature(feature_name) if feature_name else None

    def InsertHelix(self, *args):      # noqa: N802 - 官方成员名
        self.calls.append(args)

    @property
    def Extension(self):      # noqa: N802 - 官方成员名
        return _FakeExtension(self._feat)


def test_units_are_converted_at_the_boundary():
    """@brief ★ 毫米→米、度→弧度，**只在边界换算一次**（并入规则 2）。

    官方：`Height` 单位是**米**、`Startangle` 单位是**弧度**。
    """
    m = _FakeModel()
    sw_helix.insert_helix(m, height_mm=100.0, pitch_mm=10.0, start_angle_deg=180.0)
    (args,) = m.calls
    assert args[5] == pytest.approx(0.1), "height_mm 100 应换算成 0.1 米"
    assert args[6] == pytest.approx(0.01), "pitch_mm 10 应换算成 0.01 米"
    assert args[9] == pytest.approx(3.14159265), "start_angle_deg 180 应换算成 π 弧度"


def test_all_ten_arguments_are_passed_in_official_order():
    """@brief 10 个实参一个不少、顺序照官方。"""
    m = _FakeModel()
    sw_helix.insert_helix(
        m, height_mm=50.0, pitch_mm=5.0, revolution=8.0, helix_def=3,
        reversed=True, clockwise=True, tapered=True, outward=True,
        taper_angle_deg=15.0, start_angle_deg=90.0,
    )
    (args,) = m.calls
    assert len(args) == 10
    assert args[0:5] == (True, True, True, True, 3)
    assert args[7] == pytest.approx(8.0)
    assert args[8] == pytest.approx(15.0)


def test_returns_the_new_feature_name():
    """@brief `InsertHelix` 官方返回 void ⇒ 本模块回读特征名。"""
    m = _FakeModel("Helix7")
    assert sw_helix.insert_helix(m, height_mm=10.0) == "Helix7"


def test_raises_diagnosable_error_when_nothing_was_created():
    """@brief ★ 没建出来时必须抛**带原因**的 `RuntimeError`（不许静默成功）。

    ⚠ 与 `015` 的修法一致：**让失败可见**。最常见原因是没选定义用的圆。
    """
    m = _FakeModel(feature_name=None)
    with pytest.raises(RuntimeError) as ei:
        sw_helix.insert_helix(m, height_mm=10.0)
    msg = str(ei.value)
    assert "圆" in msg, msg
    # ⚑ 轮 121：取"最后加的特征"的成员从 `FirstFeature` 改成了
    #   `IModelDocExtension.GetLastFeatureAdded` ⇒ 错误信息里的成员名**跟着变**。
    assert "GetLastFeatureAdded" in msg, msg


def test_module_declares_verified_with_real_machine_evidence():
    """@brief ★ 等级是 `verified`，且来源块**写明真机证据从哪来**。

    ⚑ 2026-10-01（轮 121）：由 `stitched` 升为 `verified` ——
    依据是 `tools/verify_helix_smoke.py` 真机 **13/13**（含**读回定义**的往返一致）。
    ⚠ **等级不许往回降**：谁改回 `stitched`，这条会红。
    """
    t = (REPO_ROOT / "scripts" / "sw_helix.py").read_text(encoding="utf-8")
    assert "验证等级：`verified`" in t, "等级声明必须是 verified"
    assert "verify_helix_smoke" in t, "来源块必须指认真机证据脚本"
    assert "往返一致" in t, "要写明关键证据"
    assert "验证等级：`stitched`" not in t, "不许把等级降回去"


def test_newest_feature_uses_GetLastFeatureAdded_not_FirstFeature():
    """@brief ★★ **轮 121 冒烟抓到的缺陷**：不许再读 `FirstFeature` 当「最新的」。

    实测：`FirstFeature` 是**特征树的第一个**（`收藏`），
    而新建的是 `螺旋线/涡状线1` ⇒ 必须用官方 `GetLastFeatureAdded()`。
    ⚠ 这个错**不抛异常、返回一个看起来合理的字符串**，静态测试抓不到 ——
    所以这条判据是**用真机结论换来的**。
    """
    t = (REPO_ROOT / "scripts" / "sw_helix.py").read_text(encoding="utf-8")
    impl = t.rsplit("# ── 来源", 1)[0]
    assert "GetLastFeatureAdded" in impl
    assert '"FirstFeature"' not in impl, "不许再用 FirstFeature 当最新特征"
