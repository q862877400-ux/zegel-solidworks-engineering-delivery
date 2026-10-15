"""★ 规格 299 判据：`DeleteRenderMaterial` 的**后继不可调**必须有真机证据、且证据与记档一致。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_render_material.py:311-360`（★ `delete_render_material` 的「记档保留 2.0」）
#         `output/render-material-family-evidence.json`（★ 旧证据）
#         `output/_probe299_render_material.txt`（★ **本轮真机复验** · SW rev 34.4.1）
#         `C:/swapi/types/IModelDocExtension/DeleteDisplayStateSpecificRenderMaterial.md`（★ 官方后继）
# 定位:   ★★ 收 `AUTO_HANDOFF.md` ④ 段登记项 **③**：「`DeleteRenderMaterial` —— ★ 先**真机复核**后继是否可调」。
#         ★★★ 判据 = ★ 「保留旧入口」这个决定**必须有真机证据撑着**，且证据**能复跑**。
#         ★★ 且：★ 「取不到」与「调了报错」**必须分开**（★ 前者是 pywin32 迟到绑定，后者才是 API 语义）。
# 官方依据: 官方那页的措辞**不是** `Obsolete`，而是
#   「**Not supported in SOLIDWORKS 2011 and later. Superseded by …**」（★ **比 `Obsolete` 更强**）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM；★ 真机读数由探针产出）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts" / "sw_render_material.py"
EVIDENCE_OLD = ROOT / "output" / "render-material-family-evidence.json"
PROBE_TXT = ROOT / "output" / "_probe299_render_material.txt"
PROBE_PY = ROOT / "output" / "_probe299_render_material.py"

OLD_ENTRY = "DeleteRenderMaterial"
NEW_ENTRY = "DeleteDisplayStateSpecificRenderMaterial"


def test_the_successor_is_still_not_callable_on_this_machine():
    """★★★ 本轮真机复验：★ 后继**仍不可调**（★ 与既有证据**逐条一致**）。

    ★ 读数（★ `output/_probe299_render_material.txt` · SW rev **34.4.1**）：
      · `DeleteRenderMaterial(0, False)` ⇒ ★ **`ok=True` · `True`**
      · `DeleteDisplayStateSpecificRenderMaterial(0, False, 0)` ⇒ ★★ **`ok=False` · `TypeError`**
    """
    assert PROBE_TXT.is_file(), (
        "★ 缺本轮真机读数 `output/_probe299_render_material.txt` —— "
        "跑 `python tools/sw_guard.py --timeout 600 -- python output/_probe299_render_material.py`")
    body = PROBE_TXT.read_text(encoding="utf-8", errors="replace")
    assert "rev 34.4.1" in body or "rev " in body, "★ 读数里没有 SW 版本号"
    #: ★ 旧入口**能调**
    assert re.search(r"%s\(0, False\)\s+ok=True" % OLD_ENTRY, body), (
        "★ 旧入口的读数不见了或不是 `ok=True`")
    #: ★★ 新入口**不能调**
    assert re.search(r"%s\(0, False, 0\)\s+ok=False" % NEW_ENTRY, body), (
        "★ 新入口的读数不见了或**不是** `ok=False` ⇒ ★ 若它真能调，"
        "★ 那「保留旧入口」这个决定就**必须重新评估**")


def test_take_member_and_call_are_distinguished():
    """★★★ 「**取不到成员**」与「**调了报错**」必须**分开**（★ 事实 47 那一族）。

    ★ 真机读数：★ 两个名字的 `getattr` **都取得到**（★ 一个回 `method`、★ 一个回 `bool`）
      ⇒ ★★ **区别不在"取不到"、★ 而在"取回来的不可调用"** ——
        ★ 那是 **pywin32 迟到绑定造不出调用包装**（★ 不是 API 语义问题）。
    """
    body = PROBE_TXT.read_text(encoding="utf-8", errors="replace")
    #: ★ 探针的打印形状逐字是 `"  ★ %-46s getattr ⇒ %s" % (name, type(got).__name__)`
    #:   ⇒ 行里是 `<名字> …空格… getattr ⇒ <类型>`（★ **名字前没有** `getattr ` 前缀）
    #:   ⇒ ★ 按**行**判，★ 不猜形状（★ 这正是「判据要贴合实际书写形态」那条纪律）。
    def _type_of(name: str) -> str:
        for line in body.splitlines():
            if name in line and "getattr ⇒" in line:
                return line.split("getattr ⇒", 1)[1].strip()
        return "<NOT FOUND>"

    assert _type_of(OLD_ENTRY) == "method", (
        "★ 旧入口的 `getattr` 形态变了（★ 实得 %r，★ 应是 `method`）" % _type_of(OLD_ENTRY))
    assert _type_of(NEW_ENTRY) == "bool", (
        "★ 新入口的 `getattr` 形态变了（★ 实得 %r，★ 应是 `bool` —— ★ 那正是「不可调用」的直接证据）"
        % _type_of(NEW_ENTRY))


def test_the_decision_is_recorded_with_its_reason():
    """★★★ 保留旧入口这个决定**必须记档**、且写出**理由**（★ 不是"漏改"）。

    ★★ 判据（★ 事实 62 同族）：★ 「刻意保留」这句话**必须带可核理由**，
      ★ 否则它就是一句无法证伪的自称。
    """
    src = SRC.read_text(encoding="utf-8", errors="replace")
    assert "刻意保留旧入口" in src, "★ 记档里没有「刻意保留旧入口」的表态"
    assert "记档保留 2.0" in src, "★ 记档版本号不见了（★ 那是它与上一轮区分的标记）"
    #: ★★ 必须点明**后继不可调**这个真因
    assert "不可调用" in src, "★ 记档里没写清「后继**不可调用**」这个真因"
    #: ★★ 必须点出 pywin32 迟到绑定（★ 否则读者会以为是 API 语义）
    assert "迟到绑定" in src, "★ 记档里没点明「pywin32 迟到绑定」这个**架构性**原因"


def test_the_evidence_file_is_not_trusted_by_its_verdict():
    """★★★ **可复用判据**：★ 证据文件的 `verdict` 是**结论**、★ 逐条 `ok` 才是**事实**。

    ★ 记档逐字：「★★★ 证据文件里的 `verdict` 是**结论**、★ 而逐条 `ok` 才是**事实** ——
      两者打架时**以逐条为准**（★ 与事实 519 同族：★ "表里有"≠"它做到了"）」
    """
    src = SRC.read_text(encoding="utf-8", errors="replace")
    assert "逐条" in src and "verdict" in src, (
        "★ 记档里没写「以逐条 `ok` 为准、★ 不按 `verdict` 判」这条**可复用判据**")
    #: ★ 旧证据文件必须在（★ 它是**判据的靶子**）
    assert EVIDENCE_OLD.is_file(), "★ 旧证据 `output/render-material-family-evidence.json` 不见了"
    data = json.loads(EVIDENCE_OLD.read_text(encoding="utf-8"))
    blob = json.dumps(data, ensure_ascii=False)
    assert OLD_ENTRY in blob, "★ 旧证据里没有旧入口的读数"


def test_probe_is_reusable_and_self_contained():
    """★★ 判据要求「**证据要能复跑**」⇒ 探针必须在、且**自带清理**（★ 不留文档）。"""
    assert PROBE_PY.is_file(), "★ 缺真机探针 `output/_probe299_render_material.py`"
    body = PROBE_PY.read_text(encoding="utf-8", errors="replace")
    assert "CloseDoc" in body, "★ 探针没有清理（★ 会留文档在 SW 里 —— 事实 76）"
    assert "finally" in body, "★ 清理没放在 `finally` 里 ⇒ ★ 中途报错就会留残留"
