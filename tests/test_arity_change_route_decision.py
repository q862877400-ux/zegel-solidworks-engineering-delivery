"""★ spec 289：**两种改法对比 + 拍板** —— ★ 改表（5 类同步）↔ ★ `_checked` 自动补出参（1 处）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   specs/288-study-arity-change-surface/acceptance.md（★ 量出**4 类同步点**）
#         scripts/sw_api_cosworks.py:149（★ `ARITY` —— ★★ **第 5 类同步点**：★ 逐接口逐成员的**反射镜像**）
#         scripts/sw_simulation_study.py:191-201（★ `_checked` —— ★ 「只校验、不改造实参」）
#         scripts/check_dispatch_byref_guard.py（★ `arity` 桶 = **只计数、不判罪**）
#         specs/266-counted-positions-impact/（★ 判「改口径**不值**」）
# 定位:   ★ 288 量出 4 类同步点 ⇒ ★ 本轮**又发现第 5 类** ⇒ ★ 于是**先比方案、再拍板**（★ 授权 E）。
# 官方依据: 不适用（本项目内部设计决策）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   只读（★ 现场读源码；★ 本文件不写任何文件）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#: ★★★ **5 类同步点**（★ 甲方案要动的**全部**地方）—— ★ 前 4 类由 288 量出 · ★ 第 5 类本轮量出。
SYNC_POINTS = {
    "① 表值": "sw_simulation_study.py 的 `STUDY_MANAGER_ARITY`（★ 9 处）",
    "② 调用点": "5 个被调用的封装要传 `out_i4()`",
    "③ 标注": "`#: arity-reflect:` 的 `excluded` → `included`",
    "④ 测试对照表": "`tests/test_sw_simulation_study_contract.py` 的 `REFLECTED_MANAGER_ARITY`（★ 9 处）",
    "★ ⑤ 反射镜像表": "★ `scripts/sw_api_cosworks.py:149` 的 `ARITY['ICWStudyManager']`（★ 9 处）",
}
#: ★★★ **两种改法**。
ROUTES = {
    "甲 · 改表 + 改调用点": {
        "改动面": "★ **5 类 × 3 模块**",
        "静态 `arity` 桶": "★ 清空",
        "运行期": "★ 正确",
        "风险": "★ 高（★ 5 处要同步，★ 漏一处就红）",
    },
    "★ 乙 · `_checked` 按表补出参": {
        "改动面": "★★ **2 处 × 3 模块**（★ `_checked` + 一张「出参类型」小表）",
        "静态 `arity` 桶": "★ 不清空（★ 它本来就**只计数、不判罪**）",
        "运行期": "★ 正确（★ 补上占位 ⇒ 与官方形参数一致）",
        "风险": "★ 低（★ 集中在 `_checked` 一处）",
    },
}
#: ★★★ **拍板**（★ 授权 E）—— ★ 理由：★ `arity` 桶**只计数、不判罪**（★ 266 判「改口径不值」）
#:   ⇒ ★ **清空它没有硬价值**；★ 而**真正的目标**是「**运行期能调通**」⇒ ★ 乙用**最小改动**达成 ✓
VERDICT = "乙 —— `_checked` 按表补出参（★ 1 处集中改，★ 不动表/调用点/标注/镜像表）"
#: ★★ 乙方案要用到的**出参类型**（★ 273 已量出 3 种）。
OUT_KINDS = {"Int32&": "out_i4()", "Double&": "VARIANT(VT_BYREF | VT_R8, 0.0)",
             "SwDmTableError&": "out_i4()"}


def _failures(sync, routes, verdict, kinds, mods) -> list[str]:
    """★ 纯函数：① 5 类同步点齐；② 两条路都在；③ 拍板是乙；④ 3 种出参齐；⑤ 3 个模块齐。"""
    bad: list[str] = []
    if len(sync) != 5:
        bad.append("★ 同步点应 5 类，实测 %d" % len(sync))
    if not any("sw_api_cosworks" in v for v in sync.values()):
        bad.append("★ 第 5 类（反射镜像表）**没登记**")
    if len(routes) != 2:
        bad.append("★ 应有两条路，实测 %d" % len(routes))
    if "乙" not in verdict:
        bad.append("★ 拍板应是**乙**")
    if len(kinds) != 3:
        bad.append("★ 出参应 3 种，实测 %d" % len(kinds))
    if len(mods) != 3:
        bad.append("★ 模块应 3 个，实测 %d" % len(mods))
    return bad


# ── ① ★★★ **第 5 类同步点**（★ 反射镜像表） ──────────────────────
def test_the_fifth_sync_point_is_found():
    """★★★ 现场核：★ `scripts/sw_api_cosworks.py` 的 `ARITY` 表**逐接口逐成员镜像反射**
    ⇒ ★ 它的 `ICWStudyManager` 段**与 `STUDY_MANAGER_ARITY` 同一口径**（★ `CreateNewStudy: 3` 等）
    ⇒ ★★ **改表要同步它** —— ★ **288 只量出 4 类**，★ 这是**第 5 类** ✓
    """
    src = (ROOT / "scripts" / "sw_api_cosworks.py").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"'ICWStudyManager':\s*\{(.*?)\}", src, re.S)
    assert m, "★ 取不到 `ARITY['ICWStudyManager']`"
    d = {k: int(v) for k, v in re.findall(r"'(\w+)':\s*(\d+)", m.group(1))}
    assert d.get("CreateNewStudy") == 3, "★ 它应与 `STUDY_MANAGER_ARITY` 同口径"
    assert d.get("RunAllStudies") == 0, "★ `RunAllStudies` 也应是 0（★ 同口径）"
    assert len(SYNC_POINTS) == 5


# ── ② ★★★ **两条路的对比** ───────────────────────────────────────
def test_two_routes_are_compared():
    """★★★ 两条路：★ **甲** 改表 + 改调用点（★ **5 类 × 3 模块** · ★ `arity` 桶清空 · ★ 风险高）；
    ★ **乙** `_checked` 按表补出参（★ **2 处 × 3 模块** · ★ `arity` 桶不清空 · ★ 风险低）。
    """
    assert len(ROUTES) == 2
    assert "5 类" in ROUTES["甲 · 改表 + 改调用点"]["改动面"]
    assert "2 处" in ROUTES["★ 乙 · `_checked` 按表补出参"]["改动面"]


# ── ③ ★★★ **拍板**（★ 授权 E · ★ 理由要写死） ─────────────────────
def test_the_verdict_is_b_with_the_reason():
    """★★★ **拍板乙** —— ★ 理由：★ `arity` 桶**只计数、不判罪**（★ 266 判「改口径**不值**」）
    ⇒ ★ **清空它没有硬价值**；★ 而**真正的目标**是「**运行期能调通**」
    ⇒ ★★ 乙用**最小改动**达成 ✓（★ 且**不动**表 / 调用点 / 标注 / 镜像表）。
    """
    assert "乙" in VERDICT
    assert "`_checked`" in VERDICT


# ── ④ ★★ 乙方案要用的 3 种出参（★ 273 已量出） ────────────────────
def test_the_three_out_kinds_are_ready():
    """★★ 乙要在 `_checked` 里**按表补占位** ⇒ ★ 需要「成员 → 出参类型」⇒ ★ **只有 3 种**（★ 273 量出）
    ⇒ ★ `Int32&` ⇒ `out_i4()` · ★ `Double&` ⇒ `VT_BYREF | VT_R8` · ★ `SwDmTableError&`（枚举）⇒ `out_i4()`。
    """
    assert len(OUT_KINDS) == 3
    assert "VT_R8" in OUT_KINDS["Double&"]


# ── ⑤ ★★ 三个模块 ─────────────────────────────────────────────────
def test_three_modules_are_in_scope():
    """★★ 三张表（★ `RESULTS_ARITY` · `MESH_ARITY` · `STUDY_MANAGER_ARITY`）+ ★ `sw_pdm.py` 的 `PDM` 表
    ⇒ ★ 乙方案下**每个模块只改一处**（★ 它自己的 `_checked`）。
    """
    mods = ("sw_simulation_results.py", "sw_simulation_study.py", "sw_pdm.py")
    for m in mods:
        p = ROOT / "scripts" / m
        assert p.is_file(), "★ 找不到 %s" % m
        assert "def _checked" in p.read_text(encoding="utf-8", errors="replace"), \
            "★ %s 里没有 `_checked`" % m
    assert len(mods) == 3


# ── ⑥ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 五组负例：① 同步点少一类；② 第 5 类没登记；③ 拍板不是乙；④ 出参不是 3 种；⑤ 模块不是 3 个。"""
    good = ("sw_simulation_results.py", "sw_simulation_study.py", "sw_pdm.py")
    args = (SYNC_POINTS, ROUTES, VERDICT, OUT_KINDS, good)
    assert not _failures(*args), "正常读数被判红 ⇒ 判据过严"
    assert _failures({k: v for k, v in list(SYNC_POINTS.items())[:4]}, ROUTES, VERDICT, OUT_KINDS,
                     good), "同步点少一类却未判出"
    assert _failures({k: "无" for k in SYNC_POINTS}, ROUTES, VERDICT, OUT_KINDS, good), \
        "第 5 类没登记却未判出"
    assert _failures(SYNC_POINTS, ROUTES, "甲", OUT_KINDS, good), "拍板不是乙却未判出"
    assert _failures(SYNC_POINTS, ROUTES, VERDICT, {"Int32&": "x"}, good), "出参不是 3 种却未判出"
    assert _failures(SYNC_POINTS, ROUTES, VERDICT, OUT_KINDS, ("a",)), "模块不是 3 个却未判出"
