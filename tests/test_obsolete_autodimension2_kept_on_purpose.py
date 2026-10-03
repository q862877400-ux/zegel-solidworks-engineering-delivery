"""★ 测 `AutoDimension2` 的记档：★ **后继已验证可调、★ 而**判据立不起来**故暂不换**（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\`）
# 文件:   `scripts/sw_part.py::auto_dimension_sketch`（★ 生产）·
#         `tools/probe_fullydefinesketch{,2}.py`（★ 探针、★ 只报不动）·
#         `output/fullydefinesketch{,2}-probe-evidence.json`
# 定位:   ★ 阶段 2 · T1 的逐条流程 ①（查官方）与 ②（**真机验证后继可不可调**）✓
#   ★★ **官方逐字**（★ `ISketch/AutoDimension2.md`）：
#     「**Obsolete. Superseded by `ISketchManager::FullyDefineSketch`**.」· 旧签名 **5 参** ✓
#   ★★★ **后继逐字**：★ **现行** · **10 参** · ★★ **`## Returns` 是**「Not currently defined」**** ✓
#   ★★★★ **调用序必须读官方示例**（★ `Fully_Define_Underdefined_Sketch_Example_VB.md`）：
#     ★ 逐字用 `lMarkHorizontal = 2` / `lMarkVertical = 4` + `SelectByID2("Point1@Origin", …)` +
#     `FullyDefineSketch(True, True, <V Or H>, True, 1, Nothing, 1, Nothing, 1, 1)` ✓
#   ★★★★★ **真机两轮的结果**：★ `None` ⇒ **`类型不匹配`（位置 6）** ·
#     ★★ **空 `Dispatch` ⇒ 回 `4` · 零错误** · ★★★ 而**选不选原点都回 `4`** ✓
#   ★★★★★★ **∴ 记档的理由是**判据**（★ 不是"后继到不了"）：
#     ★ `GetDimensionCount` / `GetSketchDimensions` **两种读法都量不到**（回 `-1`）⇒
#     ★★ **"它有没有真建出尺寸"没有可核读数** ⇒ ★★★ **按三态：量不到 ⇒ `None`** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_part.py"
E1 = REPO / "output" / "fullydefinesketch-probe-evidence.json"
E2 = REPO / "output" / "fullydefinesketch2-probe-evidence.json"
OFF_OLD = Path(r"C:\swapi\types\ISketch\AutoDimension2.md")
OFF_NEW = Path(r"C:\swapi\types\ISketchManager\FullyDefineSketch.md")


def test_official_successor_returns_not_defined() -> None:
    """★★★ **前提断言**：★ 后继的 `## Returns` **确实**是「Not currently defined」（★ 判据的锚点）✓"""
    if not OFF_NEW.is_file():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t = OFF_NEW.read_text(encoding="utf-8", errors="replace")
    assert "Not currently defined" in t, "★ 后继的 Returns 段变了 ⇒ 判据要重看"
    old = OFF_OLD.read_text(encoding="utf-8", errors="replace") if OFF_OLD.is_file() else ""
    if old:
        assert "Obsolete" in old, "★ 旧页不再废弃了"


def test_evidence_none_fails_but_empty_dispatch_works() -> None:
    """★★★ 核心断言：★ 证据里**`None` 报错、★ 空 `Dispatch` 回 4** ✓"""
    if not E1.is_file():
        return
    d1 = json.loads(E1.read_text(encoding="utf-8", errors="replace"))
    rows = {r["form"]: r for r in d1["rows"]}
    nn = rows.get("new_nulls") or {}
    ed = rows.get("new_empty_dispatch") or {}
    assert nn.get("error") and "类型不匹配" in nn["error"], "★ `None` 竟然不报错了"
    assert "6" in nn["error"], "★ 出错位置不是 6（★ `HorizontalDatumDisp`）"
    assert not ed.get("error"), "★ 空 Dispatch 报错了：%r" % ed.get("error")
    assert ed.get("returned") == "4", "★ 空 Dispatch 的返回值变了：%r" % ed.get("returned")


def test_negative_case_return_code_cannot_distinguish() -> None:
    """★★★ **负例 · 返回码分不出**：★ 第二轮的"选原点 / 不选"**都回 4** ✓

    ★★ **本条要守的判据**：★★★ **那个返回码**不能**当"成功"用** ——
      ★ 因为**两种不同的输入回了同一个值** ⇒ ★★ **它不携带"做没做"的信息** ✓
      ★ 而官方**本身就写着** `## Returns` = 「**Not currently defined**」⇒ ★ **铁律 5** ✓
    """
    if not E2.is_file():
        return
    d2 = json.loads(E2.read_text(encoding="utf-8", errors="replace"))
    rets = {r["tag"]: r.get("returned") for r in d2["rows"]}
    assert len(rets) >= 2, "★ 第二轮的对照不全：%r" % rets
    vals = set(rets.values())
    assert vals == {"4"}, "★ 返回码现在能区分了（%r）⇒ 那就可以拿它当判据 ⇒ 请复核" % rets


def test_negative_case_reason_is_the_measurement_not_the_call() -> None:
    """★★★ **负例 · 记档理由要写对**：★ 必须写明「**后继能调、★ 而判据立不起来**」✓

    ★★ **为什么**：★ 若只写「不可换」，★ 后人会以为**后继调不了**（★ 那与证据相反）⇒
      ★★★ **理由必须指向**真正的那一环**（★ 判据）✓
      ★ 而 docstring 里要能看到 **两种失败的读法** + **三态判据** 的措辞 ✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    i = t.find("def auto_dimension_sketch")
    seg = t[i:i + 9000]
    assert "记档保留" in seg, "★ 没写「记档保留」"
    assert "量不到" in seg, "★ 没写明「量不到」（★ 那才是真因）"
    assert "三态" in seg or "None" in seg, "★ 没写三态判据"
    assert "已验证" in seg and "可调" in seg, "★ 没写明后继**已验证可调**（★ 否则与证据相反）"
