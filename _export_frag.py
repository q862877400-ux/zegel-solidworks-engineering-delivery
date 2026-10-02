

# ── 24h 计划 段 4（Spec Kit `147`）：**导出族**的"回读报告"包装 ──────────────────────
# ★★★ 为什么导出要包（而配置族不用）：
#   配置族 6 个**全部回 dict** ⇒ ★ **可 JSON 化** ⇒ 直挂；
#   而导出的这些回 `_export_generic(...)` / `p` / `success`（bool 或路径），
#   ⇒ ★★ **本项目铁律**：「COM 返回值凡不能自证，一律以回读为判据」
#   ⇒ ★★★ **导出的判据显然是**「**那个文件真的存在、且非空**」** —— ★ 不是"函数说成功了"。
# ★★ 判据（★ 三条，都有据）：
#     ① `output_path` **存在**；② **大小 > 0**；③ ★ 函数自身不抛异常。
#   ⇒ ★ `ok` 三条都真才算（★ 任何一条不过都**如实报**，不静默）。


def _export_report(model, output_path: str, call, fmt: str) -> dict[str, Any]:
    """★ 通用：**导出 → 回读文件是否真的落盘**（★ 不看返回值，看文件）。"""
    p = Path(output_path).expanduser()
    existed_before = p.is_file()
    size_before = p.stat().st_size if existed_before else 0
    err = None
    ret = None
    try:
        ret = call()
    except Exception as exc:                                   # noqa: BLE001
        err = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    exists = p.is_file()
    size = p.stat().st_size if exists else 0
    return {
        "ok": err is None and exists and size > 0,
        "format": fmt,
        "output_path": str(p),
        "returned": (str(ret)[:120] if ret is not None else None),
        "exists": exists,
        "size_bytes": size,
        "existed_before": existed_before,
        "size_before": size_before,
        "grew_or_created": (exists and (not existed_before or size != size_before)),
        "error": err,
        "★": ("ok = 无异常 **且** 文件存在 **且** 大小 > 0 —— ★ 判据是**文件**，不是返回值"
              "（本项目铁律：回读优先）"),
    }


def export_step_report(model, output_path: str):
    """★ **导出 STEP** 并回**回读报告**（★ 判据 = 文件存在且非空）。"""
    return _export_report(model, output_path, lambda: export_to_step(model, output_path), "step")


def export_stl_report(model, output_path: str, quality: str = "fine"):
    """★ **导出 STL** 并回**回读报告**。"""
    return _export_report(model, output_path,
                          lambda: export_to_stl(model, output_path, quality), "stl")


def export_iges_report(model, output_path: str):
    """★ **导出 IGES** 并回**回读报告**。"""
    return _export_report(model, output_path, lambda: export_to_iges(model, output_path), "iges")


def export_parasolid_report(model, output_path: str):
    """★ **导出 Parasolid** 并回**回读报告**。"""
    return _export_report(model, output_path,
                          lambda: export_to_parasolid(model, output_path), "parasolid")


def export_dxf_report(model, output_path: str):
    """★ **导出 DXF** 并回**回读报告**。"""
    return _export_report(model, output_path, lambda: export_to_dxf(model, output_path), "dxf")


def export_bmp_report(model, output_path: str, width: int = 0, height: int = 0):
    """★ **导出 BMP** 并回**回读报告**（★ 既有冒烟 `tools/verify_bmp_smoke.py` 覆盖它）。"""
    return _export_report(model, output_path,
                          lambda: export_to_bmp(model, output_path, width, height), "bmp")
