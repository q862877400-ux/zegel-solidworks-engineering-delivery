

# ── 24h 计划 段 6 续（Spec Kit `164`）：**图纸比例的读与写** ────────────────────────
# ★★★★★ 2026-10-01（轮 301）真机确证：**`ISheet.SetScale` 是**通的**** ——
#   · ★ 读：`ISheet.GetProperties` 回 `[6.0, 12.0, **1.0, 1.0**, 1.0, 0.297, 0.21]`
#     （★ 官方 Remarks 明写「You can get the two scale values from the sheet by using
#      `ISheet::GetProperties`」）—— ★ 位置 3 / 4 就是 **Numerator / Denominator**；
#   · ★ 写：`SetScale(1.0, 2.0, False, False)` ⇒ **回 `True`**，★ **而读回变成 `[6.0, 12.0, 1.0, 2.0, …]`**
#     ⇒ ★★★ **即图纸比例真的从 1:1 改成了 1:2** ✓
#   ★★ **它与"视图比例"形成对照**：★ `IView.ScaleRatio` **读得到、写不进**（★ 事实 227/294）·
#      ★ 而 `ISheet.SetScale` **写得进** ⇒ ★★★ **所以"想改比例"的正解是改**图纸**的比例**
#      （★ 而视图默认 `UseSheetScale=True` ⇒ ★ 它会跟着变）✓
#
# ★ 判据：★ **写之后必须读回**（★ 规则 6 的精神）—— ★ 而读回的判据是
#   **`GetProperties` 的位置 3 / 4 真的变成了 (numerator, denominator)**。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_drawing_query.py —— 本段
# 定位:   段 6 续：图纸比例的读取与设置（★ 声明式：按图纸名，★ 不传坐标）。
# 官方签名依据: `C:\swapi\types\ISheet\SetScale.md`
#   （`bool SetScale(double Numerator, double Denominator, bool ScaleAnnoPosition,
#     bool ScaleAnnoTextHeight)` · "Sets the scale for this drawing sheet." ·
#     "You can get the two scale values from the sheet by using ISheet::GetProperties"）·
#   `C:\swapi\types\ISheet\GetProperties.md`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def _sheet_by_name(model, sheet_name: str = ""):
    """★ **按名字取图纸对象**（★ 空名字 ⇒ 当前图纸）。★ 回 `(sheet, err)`。"""
    from sw_connect import get_com_member as _get
    if model is None:
        return None, "model 为 None"
    try:
        if not sheet_name:
            sh = _get(model, "GetCurrentSheet")
            return (sh, None) if sh is not None else (None, "当前图纸取不到（★ 文档是工程图吗）")
        try:
            sh = _get(model, "GetSheetByName", str(sheet_name))
        except Exception:                                      # noqa: BLE001
            sh = None
        if sh is None:
            #: ★ 退路：遍历 GetSheetNames 找同名（★ 有些版本 GetSheetByName 不稳）
            try:
                names = list(_get(model, "GetSheetNames") or [])
            except Exception as exc:                           # noqa: BLE001
                return None, "取图纸名清单失败：%s: %s" % (type(exc).__name__, str(exc)[:120])
            if str(sheet_name) not in [str(n) for n in names]:
                return None, "没有名为 %r 的图纸（现有：%s）" % (str(sheet_name), names)
            sh = _get(model, "GetCurrentSheet")
        return (sh, None) if sh is not None else (None, "图纸对象取不到")
    except Exception as exc:                                   # noqa: BLE001
        return None, "取图纸失败：%s: %s" % (type(exc).__name__, str(exc)[:140])


def get_sheet_scale_report(model, sheet_name: str = "") -> dict:
    """★ **读图纸比例**（★ 走官方 Remarks 指定的 `ISheet.GetProperties`）。

    ★ 回 `{"ok", "sheet_name", "numerator", "denominator", "ratio_text", "properties"}`。
    ⚠ **`GetProperties` 的位置 3 / 4 是比例的两个数**（★ 位置 0/1 是纸张尺寸 · 位置 2 是视图比例标志 ·
      位置 5/6 是宽高）；★ **本函数只认那两位**，★ 其余原样回在 `properties` 里供核对。
    """
    from sw_connect import get_com_member as _get
    sheet, err = _sheet_by_name(model, sheet_name)
    if err:
        return {"ok": False, "error": err}
    try:
        props = list(_get(sheet, "GetProperties") or [])
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "error": "GetProperties 失败：%s: %s" % (type(exc).__name__, str(exc)[:150])}
    if len(props) < 5:
        return {"ok": False, "error": "GetProperties 只回了 %d 个元素（★ 预期 ≥7）" % len(props),
                "properties": [str(x)[:30] for x in props]}
    num, den = float(props[3]), float(props[4])
    return {"ok": True, "sheet_name": str(sheet_name) or "(当前)", "numerator": num, "denominator": den,
            "ratio_text": "%g:%g" % (num, den),
            "properties": [str(x)[:30] for x in props],
            "★": "位置 3/4 是比例的两个数（官方 Remarks 指定 GetProperties 读比例）"}


def set_sheet_scale_report(model, numerator: float, denominator: float,
                           scale_anno_position: bool = False, scale_anno_text_height: bool = False,
                           sheet_name: str = "") -> dict:
    """★ **设图纸比例并回读**（★ 走 `ISheet.SetScale` —— 官方签名 4 参，★ 回 bool）。

    ★ 判据：★ **`SetScale` 回真** · ★ **且回读的 (位置 3, 位置 4) 真的变成了 (numerator, denominator)**。
    ⇒ ★ 两者缺一 ⇒ `ok: False`（★ 规则 6：不静默成功）。
    """
    from sw_connect import get_com_member as _get
    sheet, err = _sheet_by_name(model, sheet_name)
    if err:
        return {"ok": False, "error": err}
    try:
        num, den = float(numerator), float(denominator)
    except (TypeError, ValueError) as exc:
        return {"ok": False, "error": "比例两个数必须是数字：%s" % str(exc)[:120]}
    if num <= 0 or den <= 0:
        return {"ok": False, "error": "比例的两个数都必须 > 0（★ 收到 %r:%r）" % (num, den)}
    before = get_sheet_scale_report(model, sheet_name)
    try:
        ret = _get(sheet, "SetScale", num, den, bool(scale_anno_position), bool(scale_anno_text_height))
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "set", "asked": [num, den], "before": before,
                "error": "SetScale 失败：%s: %s" % (type(exc).__name__, str(exc)[:180])}
    after = get_sheet_scale_report(model, sheet_name)
    ok_readback = bool(after.get("ok") and abs(after.get("numerator", -1) - num) < 1e-9
                       and abs(after.get("denominator", -1) - den) < 1e-9)
    return {"ok": bool(ret) and ok_readback, "asked": [num, den], "set_scale_returned": bool(ret),
            "before": before, "after": after, "readback_matches": ok_readback,
            "★": "回读判据 = GetProperties 的位置 3/4 真的变了（★ 规则 6）"}
