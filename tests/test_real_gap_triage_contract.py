"""★ 真缺口分诊的契约测试：三条规则 + 「该挂是默认」的反向保护。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_real_gap_triage_contract.py
# 定位:   ★ 2026-10-03（轮 396）24 小时计划 v2 的 T0.1 契约测试。★ 被锁的契约是
#   `tools/triage_real_gaps.classify(module, name)` 的三条规则：
#   ① `不做`（事实 40：`IModeler.Create*Surface` 返回值跨次都变）
#   ② `内部件`（不是函数：类/异常/数据类 · 或**显式管道名单**）
#   ③ **其余一律 `该挂`** —— ★★ 这一条是**反向保护**：★ 分诊**不许**退化成"凭名字把东西丢掉"，
#      否则会**静默丢掉真能力**（★ 与硬约束⑧冲突）。
# 官方依据: 不适用（本项目自身的判定规则）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "scripts"))

import triage_real_gaps as T                                        # noqa: E402

ARTIFACT = Path(r"D:\AI\SW\output\real-gap-triage.json")


@pytest.mark.parametrize("name", [
    "create_planar_surface", "create_cylindrical_surface", "create_spherical_surface",
    "create_conical_surface", "create_toroidal_surface", "create_offset_surface",
    "create_freeform_surface",
])
def test_unreliable_family_is_marked_not_doing(name: str) -> None:
    """★ `IModeler.Create*Surface` 族 ⇒ `不做`，且**带原因**（事实 40）。"""
    kind, why = T.classify("sw_surface", name)
    assert kind == "不做"
    assert "事实 40" in why, "不做必须写清原因（★ 不许静默丢）"


def test_not_doing_rule_is_scoped_to_the_unreliable_module() -> None:
    """★★ 反向保护：★ `不做` 这条**只对 sw_surface 生效** ——
    ★ 同一个名字在别的模块里必须是 `该挂`（★ 否则规则会误伤整仓）。"""
    #: ★ 注意：旧样本 `sw_surface_features.create_extruded_surface_report` 已经**真的有工具**
    #:   （`solidworks_surface_create_extruded`）⇒ 它现在判「已有」，★ 故换成一个名字里
    #:   带 `create_*_surface` 形状、而**不在** sw_surface 模块的真缺口。
    kind, _why = T.classify("sw_simulation_loads", "create_planar_surface")
    assert kind == "该挂", "★ 不做规则不许越出 sw_surface（★ 那会误伤已有的真工具）"


@pytest.mark.parametrize("module,name", [
    ("sw_hole_features", "HoleFeatureEvidence"),
    ("sw_part", "SketchSelectionRef"),
    ("sw_selection_spec", "EntitySelectionError"),
])
def test_class_and_exception_names_are_internals(module: str, name: str) -> None:
    """★ 不是函数（类 / 异常 / 数据类）⇒ `内部件`。"""
    kind, why = T.classify(module, name)
    assert kind == "内部件"
    assert "不是函数" in why


@pytest.mark.parametrize("module,name", [
    ("sw_surface", "get_modeler"),
    ("sw_simulation", "get_cosmosworks"),
    #: ★★ 2026-10-07（接手轮 · 规格 214 T-214-07）**样本第四次随事实更新** ——
    #:   ★ 原样本是 `("sw_simulation", "get_study_manager")`，★ 它今天判 **`已有`**、不再是 `内部件` ✗
    #:   ★★ **依据（实测，不是推断）**：`get_study_manager` **已经是一个已挂工具的实现** ——
    #:     `register_capabilities.all_specs()` 里逐字有
    #:     `solidworks_simulation_get_study_manager`（★ 其 `function` 就是 `get_study_manager`）✓
    #:     ⇒ ★ 分类器走的是 `exposed_by_wrapper` 那条**更准**的分支（"功能已由…包装暴露"），
    #:       ★ 而 `PLUMBING_WHY` 那条是"它还没被挂、只是内部管道"时的判法 ✓
    #:   ★ 这**正是**本文件 L82-83 写明的设计意图：「★ 一旦某个名字被挂上，本测试会红 ——
    #:     ★ 那是**有意**的：它提醒你『契约变了，来更新样本』」⇒ ★ 本条就是来更新的 ✓
    #:   ★ 换上的 `get_cw_document` 与 `get_study_manager` **同域同形**（都是仿真域的取入口助手），
    #:     ★ 且今天仍判 `内部件`、理由**逐字**等于 `PLUMBING_WHY` 里那条（★ 已复算）✓
    ("sw_simulation", "get_cw_document"),
    ("sw_export", "get_mass_property_override_options"),
])
def test_explicit_plumbing_names_are_internals(module: str, name: str) -> None:
    """★ **显式管道名单**里的名字 ⇒ `内部件`，且理由来自名单（★ 逐条可读）。"""
    kind, why = T.classify(module, name)
    assert kind == "内部件"
    assert why == T.PLUMBING_WHY[name], "理由必须就是名单里写的那条（★ 不许另编）"


@pytest.mark.parametrize("module,name", [
    #: ★ 样本要选**当前确实该挂**的（★ 而一旦某个名字被挂上，本测试会红 —— ★ 那是**有意**的：
    #:   ★ 它提醒你「契约变了，来更新样本」）。
    #: ⚠ 2026-10-03（轮 402）：先前这里被我一次替换**清空了**（pytest 报
    #:   `got empty parameter set`）⇒ ★★ **那条反向保护根本没在跑**（静默失效）。
    #:   ★ 教训：改完参数化要看 `-rs` 输出里有没有 `empty parameter set` ——
    #:   ★ 那等于把一个守卫**悄悄关掉**。
    ("sw_part", "linear_pattern"),                 #: ★ 故意未挂（真机未建成，事实 315）
    #: ★★ 2026-10-03（轮 432）**两处样本已随事实更新**（★ 而那两件事**确实做完了**）：
    #:   · `sw_part.add_dimension` ⇒ ★ **已由 `add_dimension_report` 包装**（★ 事实 320 恢复注册）
    #:   · `sw_weldment.create_structural_member` ⇒ ★ **已由 `create_structural_member_from_sketch` 包装**
    #:     （★ 事实 342/339）⇒ ★ 故这两条**不再是真缺口**，本测试里换成**仍是**真缺口的名字。
    ("sw_simulation_loads", "add_bolt_connector"),  #: ★ B 组载荷，尚未封
    #: ★★ 2026-10-03（轮 470）**样本第三次随事实更新** ——
    #:   ★ 原样本 `add_link_connector` 的注释写着「★ B 组载荷，尚未封（事实 341）」，
    #:   ★★ 而它**现在封了**：分诊判为「**已有**」，理由是
    #:     「功能已由 `add_link_connector_report` 包装暴露」
    #:     （★ 实测：`T.classify("sw_simulation_loads","add_link_connector")` ⇒ `已有`）。
    #:   ★ 换成**同类且仍是真缺口**的 `add_pin_connector`
    #:     （★ 同族连接件、★ 实测 classify ⇒ `该挂`、★ 与它并排的
    #:       `apply_pin_connector_report` 也仍是「该挂」⇒ 说明那是**另一种**包装形态，不是这一条）。
    ("sw_simulation_loads", "add_pin_connector"),   #: ★ B 组载荷（连接件），尚未封
    #: ★★ 2026-10-03（轮 436）**batch_export 已移出本名单** ——
    #:   ★ 它是 `batch_export_formats` 的**薄包装**，而后者已是工具
    #:   `solidworks_batch_export_files`（★ 已登记进 `ALIASED_BY_TOOL`）。
    #: ★★★ 2026-10-07（规格 213 · B1）**样本再次随事实更新**（★ 同上面那几轮的做法 ✓）：
    #:   ★ `export_flat_pattern_dxf` **已归入「已有」** ✓ —— ★ 因为规格 213 把它**挂成了工具**
    #:     （`solidworks_export_flat_pattern_dxf` ✓）；★ 而它能挂上的前提是**用户 2026-10-07
    #:     授权**了那条受控例外（★ 原话「**D 我允许你做**」✓）—— ★ 此前它**撞硬约束⑦**
    #:     （★ 「一律不保存文档」✗，★ 而官方真前置要「**已保存**的钣金件」✓）⇒ ★ **那时它到不了建成** ✓
    #:   ★★ **换成**仍是真缺口的 `export_flat_pattern_dxf_report` ✓ ——
    #:     ★ 实测 `T.classify("sw_export","export_flat_pattern_dxf_report")` ⇒ **`该挂`** ✓
    #:     （★ 它是那条能力的 `_report` 兄弟、★ 返回更富的证据字典 ✓）
    ("sw_export", "export_flat_pattern_dxf_report"),  #: ★ `_report` 兄弟，仍未挂
])
def test_real_capabilities_default_to_should_expose(module: str, name: str) -> None:
    """★★ 反向保护：★ **真能力一律 `该挂`**（默认不是"内部件"）。"""
    kind, why = T.classify(module, name)
    assert kind == "该挂", "★ 分诊不许凭名字把真能力丢掉"
    assert why == ""


def test_artifact_invariant_sum_of_three_kinds_equals_total() -> None:
    """★ 产物自洽：三类之和 == total（★ 数字从生成物来 —— 硬约束②）。"""
    if not ARTIFACT.exists():
        pytest.skip("尚未跑过 tools/triage_real_gaps.py")
    d = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    s = d["summary"]
    assert s["self_check"] is True
    #: ★ 四类之和 == total（★ 轮 399 加了第四类「已有」：*_report 包装已暴露）
    assert (s["该挂"] + s.get("已有", 0) + s["内部件"] + s["不做"]) == s["total"]
    assert s["total"] > 0
    kinds = {r["kind"] for r in d["rows"]}
    assert kinds <= {"该挂", "已有", "内部件", "不做"}
    #: ★ 每一行都要有分类；`不做` 行必须带原因
    for r in d["rows"]:
        if r["kind"] == "不做":
            assert r["why"], "不做必须写原因"

@pytest.mark.parametrize("module,name,wrapper", [
    #: ★ 真例（真机核过）：原名自己没工具，而 `*_report` 有
    ("sw_part", "shell", "shell_report"),
    ("sw_part", "rib", "rib_report"),
    ("sw_part", "insert_dome", "insert_dome_report"),
    ("sw_part", "insert_composite_curve", "insert_composite_curve_report"),
    ("sw_selection_spec", "resolve_entity", "resolve_entity_report"),
])
def test_wrapper_covered_names_are_marked_existing(module: str, name: str, wrapper: str) -> None:
    """★★ **第四层证据**（轮 399）：若 `name` 的包装变体已有工具 ⇒ 它**不是缺口**。
    ★ 否则分诊会把已有的能力当成缺口（★ 而再挂一遍只会**重复**）。"""
    kind, why = T.classify(module, name)
    assert kind == "已有", "被包装暴露的名字应判“已有”"
    assert wrapper in why, "理由里要写出是哪个包装"


def test_wrapper_rule_does_not_swallow_real_gaps() -> None:
    """★★ 反向保护：★ 包装规则**只对真的有包装的名字生效** ——
    ★ 没有 `*_report` 的真缺口不能被它吞掉。"""
    #: ★ 注意：`hole_wizard` **不在此列** —— 它已被第五层证据（空存根）判为「不做」，
    #:   ★ 那是**正确的**（★ 它函数体只有 `pass`）。
    #: ★★ 2026-10-03（轮 432）**样本已随事实更新**：★ 原来这里有 `add_dimension` 与 `add_force`，
    #:   ★ 而它们**现在都真的有包装了**（`add_dimension_report` / `apply_force_report`）
    #:   ⇒ ★ 拿它们当"没包装的真缺口"是**过期的**。★ 换成**确实还没有包装**的三条。
    #: ★★ 2026-10-03（轮 436）**样本再次随事实更新**：★ `batch_export` 已归入「已有」
    #:   （★ 它是 `batch_export_formats` 的薄包装，而后者已是工具）⇒ ★ 换成**确实还没有包装**的名字。
    #: ★★ 2026-10-03（轮 470）**样本再次随事实更新**（★ 同上面那条 parametrize 的理由）：
    #:   `add_link_connector` 已被 `add_link_connector_report` 包装暴露 ⇒ 换成 `add_pin_connector`。
    #: ★★★ 2026-10-07（规格 213 · B1）**再一次随事实更新**：
    #:   ★ `export_flat_pattern_dxf` **已归入「已有」**（★ 规格 213 把它挂成工具 ✓，
    #:     前置是**用户授权的受控例外** ✓）⇒ ★ **换上它的 `_report` 兄弟** ✓
    #:     （★ 实测仍是 `该挂` ✓ —— ★ 保持这条测试的**判别力**，★ 而不是把它删空 ✗）
    for module, name in (("sw_part", "linear_pattern"),
                         ("sw_export", "export_flat_pattern_dxf_report"),
                         ("sw_simulation_loads", "add_pin_connector")):
        kind, _ = T.classify(module, name)
        assert kind == "该挂", "%s.%s 是真缺口，不能被包装规则吞掉" % (module, name)

# ── 2026-10-03（轮 439）★ 补三条守卫：★ 针对**具体的静默退化** ──────────────────────
# ★★ 起因：★ `plan-200r-v3-convergence.md` §五 ④ —— ★ **分诊本身是判据**，
#    ★ 而它这一阶段**错了四次**（★ 事实 346/350/351/352）⇒ ★ 该照第 22 道门禁的做法管起来。
# ★ 而本文件**已有 8 条**覆盖旧规则（★ 含 `test_wrapper_rule_does_not_swallow_real_gaps` 那条负例）——
#    ★★ 故本轮只补**本阶段新加的两样**没被看住的地方。


def test_server_export_functions_is_not_silently_empty() -> None:
    """★★★ **`_server_export_functions()` 不许静默返回空集** —— ★ 那是本阶段最危险的退化。

    ★ 背景（事实 350/351）：★ 分诊原来看不见 `server.py` 侧那 **60 个** function ⇒
      ★ 把**已覆盖**的名字报成「该挂」。★ 而那个盲区是**靠读 `server.py` 的 `exports` 字典**修的。
    ★★ 而**若那个字典改名/挪走**，★ `_server_export_functions()` 会**静默返回空集** ⇒
      ★★ **盲区无声回来**（★ 而分诊仍会报一个**看着正常**的数字）⚠ ——
      ★ 那正是本仓那条「**一个存在但没人用的守卫与没有守卫等价**」的同族。
    ★ 判据：★ 非空 **且** 含一个**已知**名字（★ 那个字典里确实有的）。
    """
    funcs = T._server_export_functions()
    assert funcs, (
        "`_server_export_functions()` 返回空集 ⇒ 分诊会**无声地**退回「看不见 server.py」那个盲区"
        "（事实 351）。★ 检查 `mcp-server/server.py` 里那个 `exports = {…}` 字典是否还在原处/原名。")
    assert "batch_export_formats" in funcs, (
        "`batch_export_formats` 不在名单里 ⇒ 那个字典的读法可能变了"
        "（★ 而它是 `batch_export` 能判「已有」的结构性依据）")


def test_alias_table_entries_carry_a_real_reason() -> None:
    """★★ **别名表的每条都要够长** —— ★ 否则它会**变成永久补丁堆**。

    ★ 先例：★ `KNOWN_DEAD_ENDS` 那条测试（`len(why) > 60`）—— ★ 而理由**太短等于静默豁免**。
    ★★ 而本表（轮 436 加）与那张表**同一性质**：★ 记的是「**功能已由另一个名字覆盖**」，
      ★ 而那**是判据推不出来的东西** ⇒ ★★ **故必须每条都写出依据** ✓
    """
    for key, why in T.ALIASED_BY_TOOL.items():
        assert len(str(why)) > 40, (
            "%r 的理由太短（%d 字）⇒ 等于静默豁免。★ 本表每条都要写清"
            "「那个工具的 function 到底调没调它」" % (key, len(str(why))))


def test_cannot_be_tool_entries_carry_a_real_reason() -> None:
    """★★ **「不能当工具」那张表的每条也要够长** —— ★ 而它更严格。

    ★ 那张表记的是**有原则的"不做"**（★ 轮 438 加：`select_face_at` 的签名是裸坐标 ⇒ 规则 3 禁止）。
    ★★ 而它比"别名"更危险：★ 别名写错只是**多算一条已有**；
      ★ 它写错会把**真该挂的**判成"不做" ⇒ ★★ **故理由必须写出"是哪条规则"** ✓
    """
    for key, why in T.CANNOT_BE_A_TOOL_WHY.items():
        assert len(str(why)) > 40, (
            "%r 的理由太短（%d 字）⇒ 判「不做」而没说出是哪条规则" % (key, len(str(why))))
        assert "\u89c4\u5219" in str(why), (
            "%r 的理由里没提「规则」 ⇒ 「不能当工具」必须**引用一条本仓的规则**"
            "（★ 如规则 3「禁裸坐标」），★ 不是「我觉得难」（★ 那正是事实 53 的反面）" % (key,))

def test_the_blind_spot_can_really_come_back(monkeypatch) -> None:
    """★★★ **负例自证**：★ 证明那个"盲区无声回来"的失效模式**真的可达**（★ 事实 62）。

    ★ 事实 62：★「一个门禁『写了』不等于它『有效』—— **负例测试是唯一的证明**」。
    ★★ 而上面那条 `test_server_export_functions_is_not_silently_empty` 断言"返回非空" ——
      ★ 那**只有在本测试证明"它确实能返回空"之后**才有意义 ✓

    ★ 做法：★ 把 `ROOT` 指到一个**没有 `server.py`** 的地方 ⇒
      ★★ 读者会**静默返回空集**（★ 那正是它现在的行为）⇒ ★ 于是上面那条断言会红 ✓
    """
    from pathlib import Path as _P
    monkeypatch.setattr(T, "ROOT", _P(r"D:\AI\SW\__no_such_repo__"))
    assert T._server_export_functions() == set(), (
        "★ 指向不存在的仓库时它本该**静默返回空集**（★ 而那正是危险的失效模式）—— "
        "若它现在**不**返回空，说明读者变了，上面那条守卫的判据要重审")
