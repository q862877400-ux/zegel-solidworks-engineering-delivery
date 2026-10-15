"""★ spec 283：**`create_draft` 首次真机验证** —— ★★ **建出来了**（★ 需 方向项 mark1 + 待拔模面 mark2）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   output/_probe283_draft.txt（★ 18 臂 · 报文恒定「此拔模方向尚未定义。」）
#         output/_probe283_draft_dir.txt（★ 决定性：★ Front Plane + 面#0 ⇒ **成功**「拔模1」）
#         scripts/sw_sheet_metal.py:736（★ `create_draft` 的 docstring **本来就写着**「方向项 mark 1、待拔模面 mark 2、拔模边 mark 4」）
#         specs/239-*/（★ 把路径从 `CreateDefinition(3)` 改到 `InsertMultiFaceDraft` —— ★ **离线切片**）
# 定位:   ★ 业主**已授权**（GOAL §三 C）⇒ ★ 本轮**首次真机跑** `create_draft` ⇒ ★ 从「未测」变「可用」。
# 官方依据: `C:/swapi/types/IFeatureManager/InsertMultiFaceDraft.md`（★ 6 参 · ★ mark 1/2/4）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   只读（★ 真机读数由探针产出；★ 本文件不连 COM）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#: ★★★ **真机读数 1**（SW **34.4.1** · 2026-10-10）：★ **只给面**（6 面 × 3 标记 = **18 臂**）⇒ **全失败**，
#:   且报文**恒定**。★ 这一条把「是不是选错面 / 选错标记」**排除了**。
ONLY_FACE_ARMS = 18
ONLY_FACE_MSG = "此拔模方向尚未定义"
#: ★★★ **真机读数 2**（决定性）：★ **方向项（平面 · mark 1）+ 待拔模面（mark 2）** ⇒ ★★ **成功**。
WIN = {"plane": "Front Plane", "face_index": 0, "selected": 2, "feature_name": "拔模1"}
#: ★★★ **真机结论**：★ 需要**两个**选择。
NEEDS = ("方向项（mark 1 · 一个**平面**）", "待拔模面（mark 2）")
#: ★★ **规格 239 的路径改动**（★ 离线切片）⇒ ★ 本轮**真机确认**。
PATH_239 = "IFeatureManager::InsertMultiFaceDraft"
#: ★★★ **对 282 那条假说的反例**：★ 这个 API **吃得到面选择**（★ 配平面后）⇒ ★ 假说**被削弱**。
HYPOTHESIS_282 = "本机的特征创建 API 似乎吃不到「边 / 面」类选择"


def _failures(arms, msg, win, needs, path, hyp, block) -> list[str]:
    """★ 纯函数：① 18 臂全失败；② 报文对；③ 决定性那臂成功且是 `拔模1`；④ 需求两条；⑤ 路径；⑥ 表已订正为 `True`。"""
    bad: list[str] = []
    if arms != 18:
        bad.append("★ 应 18 臂，实测 %r" % (arms,))
    if "拔模方向尚未定义" not in msg:
        bad.append("★ 报文应是「此拔模方向尚未定义」")
    if not win.get("feature_name"):
        bad.append("★ 决定性那臂没记特征名")
    if len(needs) != 2:
        bad.append("★ 需要**两个**选择（方向项 + 待拔模面）")
    if "InsertMultiFaceDraft" not in path:
        bad.append("★ 路径应是 `InsertMultiFaceDraft`")
    if not hyp:
        bad.append("★ 282 那条假说要引出来（★ 它是反例）")
    if not block:
        bad.append("★ 回源码核失败：取不到 `create_draft` 那一条")
    elif "未测" in block and "订正" not in block:
        bad.append("★ `create_draft` 那条**仍写着「未测」而没有订正**")
    return bad


# ── ① ★★★ 只给面 ⇒ **18 臂全失败**（★ 排除「选错面/标记」） ─────────
def test_face_only_always_fails():
    """★★★ 真机：★ **6 个面 × 3 种标记 = 18 臂**⇒ ★ **全失败**，★ 且报文**恒定**：
    ★「**此拔模方向尚未定义。**」⇒ ★★ **不是「选错了面」也不是「选错了标记」**。
    """
    assert ONLY_FACE_ARMS == 18
    assert "拔模方向尚未定义" in ONLY_FACE_MSG


# ── ② ★★★ 加**方向项**⇒ **成功** ─────────────────────────────────
def test_adding_a_direction_reference_succeeds():
    """★★★ 真机（决定性）：★ **方向项（`Front Plane` · mark 1）+ 待拔模面（mark 2）** ⇒
    ★★ **`create_draft` 建出来了**：★ 新特征 **`拔模1`**（★ 选中 2 个）。
    ⇒ ★★★ **规格 239 的路径改动（`InsertMultiFaceDraft`）是对的**，★ 缺的只是**方向项**。
    """
    assert WIN["plane"] == "Front Plane"
    assert WIN["selected"] == 2, "★ 应选中**两个**（平面 + 面）"
    assert WIN["feature_name"] == "拔模1"
    assert len(NEEDS) == 2


# ── ③ ★★★ 这是 282 那条假说的**反例** ─────────────────────────────
def test_it_is_a_counterexample_to_the_282_hypothesis():
    """★★★ 282 提出过一条假说（★「本机的特征创建 API 似乎吃不到「边 / 面」类选择」）⇒
    ★★ 而本轮证明：★ `InsertMultiFaceDraft` **吃得到面选择**（★ 只要**同时**给方向项）
    ⇒ ★★★ **假说被削弱** —— ★ 「吃不到」**不是普遍现象**，★ 是**按 API 逐个**看的。
    """
    assert "边 / 面" in HYPOTHESIS_282
    assert "InsertMultiFaceDraft" in PATH_239


# ── ④ ★★★ 状态表**确实**订正为 `True`（★ 回源码核） ───────────────
def test_status_entry_is_promoted_to_true():
    """★★★ 回源码核：★ `SHEET_METAL_RUNTIME_STATUS["create_draft"]` **不再是 `(None, …)`**
    ⇒ ★ 它现在是**真机验证可用**（★ 且写明**两个选择**的前提）。
    """
    src = (ROOT / "scripts" / "sw_sheet_metal.py").read_text(encoding="utf-8", errors="replace")
    m = re.search(r'"create_draft":\s*\(', src)
    assert m, "★ 取不到 `create_draft` 那一条"
    rest = src[m.end():]
    nxt = re.search(r'\n\s*"[a-z_]+":\s*\(', rest)
    block = rest[:nxt.start()] if nxt else rest
    assert "None" not in block.split(",")[0], "★ 那一格**不该**还是 `None`"
    assert "拔模1" in block or "真机" in block, "★ 订正里要写**真机证据**"


# ── ⑤ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 六组负例：① 臂数不对；② 报文不对；③ 没记特征名；④ 需求不是两条；⑤ 路径不对；⑥ 表仍写「未测」。"""
    good = "…真机建成「拔模1」…订正…"
    args = (ONLY_FACE_ARMS, ONLY_FACE_MSG, WIN, NEEDS, PATH_239, HYPOTHESIS_282, good)
    assert not _failures(*args), "正常读数被判红 ⇒ 判据过严"
    assert _failures(6, ONLY_FACE_MSG, WIN, NEEDS, PATH_239, HYPOTHESIS_282, good), "臂数不对却未判出"
    assert _failures(ONLY_FACE_ARMS, "另一种", WIN, NEEDS, PATH_239, HYPOTHESIS_282, good), \
        "报文不对却未判出"
    assert _failures(ONLY_FACE_ARMS, ONLY_FACE_MSG, dict(WIN, feature_name=""), NEEDS,
                     PATH_239, HYPOTHESIS_282, good), "没记特征名却未判出"
    assert _failures(ONLY_FACE_ARMS, ONLY_FACE_MSG, WIN, ("只有一个",), PATH_239,
                     HYPOTHESIS_282, good), "需求不是两条却未判出"
    assert _failures(ONLY_FACE_ARMS, ONLY_FACE_MSG, WIN, NEEDS, "CreateDefinition", HYPOTHESIS_282,
                     good), "路径不对却未判出"
    assert _failures(ONLY_FACE_ARMS, ONLY_FACE_MSG, WIN, NEEDS, PATH_239, HYPOTHESIS_282,
                     "…未测…"), "表仍写「未测」却未判出"
