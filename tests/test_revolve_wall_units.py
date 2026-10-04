"""★ 测「旋转族 `GetWallThickness` 口径定案」+ 那条方法判据（★ 含负例 · 轮 138）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `IRevolveFeatureData2\\GetWallThickness.md` /
#         `IFeatureManager\\FeatureRevolve2.md` / `enums\\swThinWallType_e.md` +
#         真机证据 `output/revolve-wall-units-capability-recheck.json`
# 文件:   tests/test_revolve_wall_units.py（★ 新）
# 定位:   ★★★★★★★ 2026-10-04（轮 138）**口径定案**：
#     ★ `IRevolveFeatureData2::GetWallThickness` = **随文档单位（毫米）** ✓
#     **怎么量的**：★ 建**薄壁旋转**（★ `revolve_boss(…, thin={"type": 0, "thickness": 0.002})`）⇒
#       ★ 读回 `IsThinFeature = true` · `ThinWallType = 0` · `GetWallThickness = {0.002, 0.002}` ⇒
#       ★★ **而体积给出**精确判据**：★ 扫掠面积 = 600θ = 100π = **314.159265 mm²** ⇒
#         ★ 体积 = t × 314.159 ⇒ ★ **实测 0.628444** ⇒ **反推 t = 0.002000399** ✓
#         ★★★ **对照组**：★ 米口径该是 **628.319** ⇒ ★ **差 1000 倍** ⇒ 毫无歧义 ✓
#   ★★★★ **而它收掉了收口报告里的「下一步 ①」** ✓
#   ★★★★★ **而本轮还有一条**方法判据**：★ 我第一版把薄壁候选当**粗估**、
#     说「只到生效这一层」⇒ ★★ **⇒ 而其实可以算准**（★ 轮廓是折线 ⇒ 积分初等）⇒
#     ★★★ **⇒ 判据**：★★★ **"估算不了"常常是**我没把几何写出来**、★ 而不是真估不了** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
sys.path.insert(0, str(TESTS))
from _funcbody import func_source  # noqa: E402

SRC = REPO / "scripts" / "sw_feature_readback.py"
PART = REPO / "scripts" / "sw_part.py"
OUT = REPO / "output" / "revolve-wall-units-capability-recheck.json"


def test_the_measured_unit_is_recorded_as_a_conclusion() -> None:
    """★★★ 核心断言：★ 旋转族那条口径写成了**结论**（★ 不是"待办"）✓"""
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"), "revolve_params")
    assert "随文档单位" in body, "★ 口径的**结论**没写"
    #: ★★ 而**两个证据**都要在（★ 一个是读数、★ 一个是反推）✓
    assert "0.002000399" in body, "★ 反推出的壁厚没记下"
    assert "628.319" in body, "★ **对照组**（★ 若口径是米该是多少）没记下"


def test_the_thin_option_is_optional_and_does_not_change_semantics() -> None:
    """★★★★★ 核心断言：★ 薄壁参数是**显式可选**的（★ `None` ⇒ 实参逐字不变）✓

    ★★ **为什么最重要**：★ `revolve_boss` 是**既有能力**、★ 被多处调用 ⇒
      ★★★ **⇒ 加参数**不许**改变既有调用方的语义**（★ 与 `sweep` 的 `mutate=None` 同设计）✓
    """
    t = PART.read_text(encoding="utf-8", errors="replace")
    tree = __import__("ast").parse(t)
    fn = next(n for n in tree.body
              if isinstance(n, __import__("ast").FunctionDef) and n.name == "revolve_boss")
    names = [a.arg for a in fn.args.args]
    assert "thin" in names, "★ 签名里没有 `thin`"
    #: ★★ 它**必须有默认值**（★ 否则既有调用方全炸）✓
    defaults = fn.args.defaults
    dn = names[len(names) - len(defaults):]
    assert "thin" in dn, "★ `thin` 没有默认值 ⇒ 会破坏既有调用方"


def test_the_negative_case_the_arithmetic_is_right() -> None:
    """★★★★ 核心断言：★ 那条**算术**自己要对（★ 用代码重算一遍）✓

    ★★ **为什么**：★ 结论建立在 **扫掠面积 = 600θ** 上 ⇒
      ★★★ **⇒ 若那个算术错了、★ 结论也就是错的** ⇒ **⇒ 所以让机器独立重算一次** ✓
    """
    #: ★ 轮廓矩形的四段：★ (x=10,y:0→10) · ★ (x=20,y:0→10) · ★ (y=10,x:10→20) · ★ (y=0,x:10→20) ✓
    theta = math.pi / 6
    area = (10 + 20 + 15 + 15) * 10 * theta                    #: ∫r·θ ds 逐段 ✓
    assert abs(area - 100 * math.pi) < 1e-6, "★ 那段算术不对：%r" % area
    d = json.loads(OUT.read_text(encoding="utf-8"))
    vol = d["★_体积_实测"]
    t_fit = vol / area
    #: ★★ 反推出的壁厚要 ≈ `0.002`（★ 允许 1% 几何圆角化偏差）✓
    assert abs(t_fit - 0.002) < 2e-5, "★ 反推壁厚不对：%r" % t_fit
    #: ★★★ 而**对照组**要差三个量级（★ 那才叫"毫无歧义"）✓
    assert (2.0 * area) / vol > 500, "★ 对照组没拉开 ⇒ 判据不够硬"


def test_the_method_lesson_is_recorded() -> None:
    """★★★★ 核心断言：★ 「估算不了常常是**我没把几何写出来**」那条判据留下 ✓

    ★★ **为什么**：★ 我第一版把薄壁候选当**粗估**、★ 说「只到生效这一层」⇒
      ★★★ **⇒ 而那会让一条**本来能定案**的量**留在 unknown**（★ 与"不谎称"同样重要：
        ★ **反过来——能定案的别标未定案**）✓
    """
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"), "revolve_params")
    assert "估算不了" in body or "可以算准" in body, "★ 那条方法判据没留下"
    assert "积分" in body or "折线" in body, "★ 没写明「轮廓是折线 ⇒ 积分初等」这个理由"
