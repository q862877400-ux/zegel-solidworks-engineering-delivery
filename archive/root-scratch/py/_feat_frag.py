

# ── 24h 计划 段 3（Spec Kit `146`）：**建特征工具的"回读确认"包装** ────────────────
# ★★★ 规则 6：「**建特征之后查 `EditRebuild3` + `GetWhatsWrong2`，不静默成功**」。
#   ⚠ 而 `GetWhatsWrong2` 在本机两套源里**不存在**（★ 规则文本的一处失真）——
#     真正的成员是 `IModelDocExtension.GetWhatsWrongCount`（★ 已记进
#     `scripts/sw_feature_readback.py` 的 docstring）。
# ⇒ ★ 本段三个包装**统一走 `sw_feature_readback.feature_readback`**（那个判据已真机打磨三遍）：
#     · `shell`        ⇒ 抽壳（`InsertFeatureShell`）
#     · `rib`          ⇒ 筋（`InsertRib`）
#     · `insert_dome`  ⇒ 圆顶
#   ★ 它们的共同点：**都回 COM 对象**（⇒ MCP 回不了）**且都该按规则 6 回读确认**。
# ⇒ ★★ 判据 = ★ **特征在树里 + `EditRebuild3` 真 + `GetWhatsWrongCount == 0`**（三条都真才 ok）。


def _feature_report(model, feature_name: str, call, label: str) -> dict[str, Any]:
    """★ 通用：**先看特征名在不在（建之前）→ 调用 → 回读确认**。

    ★ 这样报告里能区分「**本来就有**」与「**这次建出来的**」（★ 比只看"在不在"硬）。
    """
    from sw_feature_readback import feature_readback, feature_present

    before = feature_present(model, feature_name)
    err = None
    obj = None
    try:
        obj = call()
    except Exception as exc:                                   # noqa: BLE001
        err = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    rb = feature_readback(model, feature_name)
    return {
        "ok": err is None and bool(rb.get("ok")),
        "feature": label,
        "feature_name_expected": feature_name,
        "present_before": before,
        "readback": rb,
        "created_object": type(obj).__name__ if obj is not None else None,
        "error": err,
        "★": "ok = 无异常 **且** 回读三条全真（特征在树里 + EditRebuild3 真 + 查错数 0）",
    }


def shell_report(model, thickness_mm: float, feature_name: str = ""):
    """★ **抽壳**并回**回读报告**（★ 规则 6：不静默成功）。

    ⚠ `thickness` 在能力层的单位**随文档单位**（本项目零件按毫米 ⇒ 传毫米值）；
      ★ 本函数收的形参名带 `_mm`（规则 2），**由调用方保证口径一致**。
    ⚠ `feature_name` 默认取中文 UI 的「抽壳1」（★ 也可由调用方给）。
    """
    return _feature_report(model, feature_name or "抽壳1",
                           lambda: shell(model, float(thickness_mm)), "shell")


def rib_report(model, sketch_name: str, thickness_mm: float, feature_name: str = "",
               direction: bool = True):
    """★ **筋**并回**回读报告**（★ 规则 6）。"""
    return _feature_report(model, feature_name or "筋1",
                           lambda: rib(model, sketch_name, float(thickness_mm), direction), "rib")


def insert_dome_report(model, height_mm: float, feature_name: str = "",
                       reverse: bool = False, elliptic: bool = False):
    """★ **圆顶**并回**回读报告**（★ 规则 6）。"""
    return _feature_report(model, feature_name or "圆顶1",
                           lambda: insert_dome(model, float(height_mm), reverse, elliptic), "dome")


def insert_composite_curve_report(model, feature_name: str = ""):
    """★ **复合曲线**并回**回读报告**。

    ★ 能力层的 `insert_composite_curve` **本身已经 raise on False**（★ 不是"假通过"），
      所以这里主要补"**建完之后特征在不在 + 重建 + 查错**"那三条（★ 规则 6）。
    ⚠ 调用前**必须先用 mark = 1 选好实体**（官方 Remarks；与 `insert_dome` 同一个坑）。
    """
    return _feature_report(model, feature_name or "复合曲线1",
                           lambda: insert_composite_curve(model), "composite_curve")
