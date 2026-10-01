import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_sketch_edit.py")
t = P.read_text(encoding="utf-8")
i = t.find("    skm = get_com_member(model, \"SketchManager\")")
j = t.find("\n", t.find("int(angle_or_distance)", i))
seg_call = t[i:j + 1]
print("  ── 要替换的调用段 ──")
print(seg_call)

NEW = '''    skm = get_com_member(model, "SketchManager")
    if skm is None:
        raise RuntimeError("IModelDoc2.SketchManager 为 None ⇒ 当前不在草图编辑态？")

    #: ⚠⚠⚠ **2026-10-01 轮 164 更正轮 122 的定性**：轮 122 看到
    #: `type=2` 报 `com_error 0x80010105`（「服务器出现意外情况」）就判它
    #: 「**架构性限制、到不了**」，并**按事实 53 停手**。
    #: ★ 但轮 164 用 `tools/probe_chamfer_forms.py` **回读线段数**后发现：
    #: ```
    #:   type=0（默认）/ type=1  ⇒ 段数 2 → 2（**没变**）· 返回 None
    #:   type=2（距离-相等）      ⇒ 段数 **2 → 3**（**变了 ✚**）· com_error 0x80010105
    #: ```
    #: ⇒ ★★★ **倒角其实建成了** —— 那个 `com_error` 是在**取返回值**（`SketchSegment`）
    #:   那一步抛的（pywin32 迟到绑定拿不到返回对象），**不影响倒角本身**。
    #: ⇒ ★★ 所以真正的限制是「**拿不到返回对象**」，不是「做不了倒角」。
    #: ★ 修法照**事实 94** 那一族：**不信返回值/异常，回读状态**（线段数）。
    def _seg_count():
        try:
            sk = get_com_member(model, "GetActiveSketch2")
            if sk is None:
                sk = get_com_member(get_com_member(model, "SketchManager"), "ActiveSketch")
            segs = get_com_member(sk, "GetSketchSegments") if sk is not None else None
            return len(list(segs)) if segs else 0
        except Exception:      # noqa: BLE001
            return -1

    before = _seg_count()
    try:
        seg = get_com_member(skm, "CreateChamfer",
                             int(chamfer_type),
                             float(distance_mm) / 1000.0,
                             float(angle_or_distance))
    except Exception as exc:      # noqa: BLE001
        after = _seg_count()
        if after > before >= 0:
            #: ★ **倒角建成了**（线段数变多）⇒ 只是**返回对象拿不到** ⇒ 不算失败
            return None
        raise RuntimeError(
            "ISketchManager.CreateChamfer 失败：%s\\n"
            "⚠ 已**回读线段数**（%s → %s）确认**没有建成**。"
            "最常见原因：没有选中两条草图实体；或 `chamfer_type` / 参数不合适"
            "（★ 实测：只有 `distance_equal`(2) 能成）。" % (exc, before, after)
        ) from exc
    if seg is None:
        after = _seg_count()
        if after > before >= 0:
            return None      #: 同上：建成了，只是没有返回对象
        raise RuntimeError(
            "ISketchManager.CreateChamfer 返回 None 且**线段数没变**（%s → %s）⇒ 没建成。"
            "⚠ 官方前置：**必须选中两条草图实体**（选完请**回读**选区计数，事实 94）。"
            % (before, after)
        )
    return seg
'''
t = t[:i] + NEW + t[j + 1:]
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok create_sketch_chamfer 已改成**回读线段数**判定")
