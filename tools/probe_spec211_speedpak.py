"""★ 探针：`IAssemblyDoc::CreateSpeedPak` —— ★ 前置 = **选中的子装配**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B6 SpeedPak 的真机探针）
# 文件:   tools/probe_spec211_speedpak.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的「装配 / SpeedPak」。
# 官方依据（★ 三样逐字读过，★ 含回读成员）：
#   · ★★ `C:\swapi\types\IAssemblyDoc\CreateSpeedPak.md`
#     `System.bool CreateSpeedPak( System.int SpeedPakType )` ⇒ ★ 参数式 **1 参** ✓
#     ★ `## Parameters` 逐字：**1 = Mated** · **2 = Graphics** ✓
#     ★★★ `## Returns` 逐字：「True if SpeedPak is created for the active configurations of the
#       **selected subassemblies** in this assembly, false if not」✗
#       ⇒ ★★ **前置 = 选中的**子装配**** ✓（★ 不是顶层零件 ✓）
#     ★ `## Remarks`：★ 已选子装配**已有 SpeedPak 时再调不会新建** ✓
#     ★★ 另有三份官方示例（C# / VB.NET / VBA）✓
#   · ★★ **回读成员**：★ **`IComponent2::IsSpeedPak`** ✓（★ 也有 `IConfiguration::IsSpeedPak` ✓）
#     ⇒ ★★★ 按**第 38 轮刚立的定则**：★ **判据要落在「它真正改变的东西」上** ✓ ——
#       ★ 顶层特征树看不见 SpeedPak ✗ ⇒ ★ **判据 = `IComponent2::IsSpeedPak` 的回读** ✓
# 前置链（★ 上一批已打通、本批复用 ✓）：
#   ★ ① 零件要**落盘**（★ `add_component` 要磁盘路径 ✓）⇒ ★ 写到**仓库内 `output/`**（★ 非用户目录 ✓）
#   ★ ② **子装配本身也要落盘** —— ★ 因为顶层装配要 `add_component(<子装配路径>)` ✓
#   ★ ③ 选择用 **`IComponent2.Select4`**（★ 事实 32：★ 按**对象**选 ✓；★ 该成员**没有 mark 参数** ✓
#      —— ★ 而 `CreateSpeedPak` **没有 mark 表** ⇒ ★ 只需"选中" ✓）
# 判据:   ★★ 主判据 = **`IComponent2::IsSpeedPak` 回读**（★ `False → True` ⇒ 建成 ✓）
#   ★★ 前置逐条落布尔字段（★ 「读数无效」与「真的不建」长得一模一样 —— ★ 已四次 ✓）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

WORK = ROOT / "output" / "spec211-b6-speedpak"     #: ★ 仓库内产物目录（★ 非用户目录 ✓）


def _make_part(sw, name: str, w_mm: float) -> Path | None:
    import sw_connect
    import sw_part
    m = sw_connect.new_document(sw, "part")
    if m is None:
        return None
    sw_part.start_sketch(m, "Front Plane")
    sw_part.sketch_corner_rectangle(m, 0.0, 0.0, w_mm, 20.0)
    sk = sw_part.current_sketch_name(m)
    sw_part.end_sketch(m)
    sw_part.extrude_boss(m, sk, 10.0)
    p = WORK / name
    try:
        sw_connect.save_document(m, str(p))
    except Exception:                                                   # noqa: BLE001
        return None
    return p if p.is_file() else None


def _components(model) -> list:
    import sw_connect
    #: ★★ 只要**顶层**组件（★ `False` 会把子装配**里面**的零件也递归带出来 ✗ ——
    #:   实测：顶层只加了 1 个子装配，而 `GetComponents(False)` 回了 **3 个** ✗
    #:   ⇒ ★ 那会让 `comps[0]` 可能是"子装配里的零件"、★ 而它**不在顶层可见** ⇒ `Select4` 不生效 ✓）
    raw = sw_connect.get_com_member(model, "GetComponents", True)
    return [c for c in (raw or []) if c is not None]


def main() -> int:
    import sw_connect
    import sw_assembly

    out: dict = {"official": "IAssemblyDoc.CreateSpeedPak",
                 "step": "前置 = 选中的子装配；判据 = IComponent2::IsSpeedPak 回读",
                 "speedpak_type_enum": {"1": "Mated", "2": "Graphics"}}
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    WORK.mkdir(parents=True, exist_ok=True)

    #: ① 两个零件落盘
    p1 = _make_part(sw, "sp1.sldprt", 40.0)
    p2 = _make_part(sw, "sp2.sldprt", 25.0)
    out["parts_saved"] = [bool(p1), bool(p2)]
    print("★ ① 零件落盘 ⇒ %r" % out["parts_saved"])
    if not (p1 and p2):
        out["verdict"] = "★★ 前置缺：★ 零件落盘失败 ✗"
        print(out["verdict"])
        return 0

    #: ② 建**子装配**（★ 它是"被选中的那个" ✓）并落盘
    sub = sw_connect.new_document(sw, "assembly")
    sub_ok = False
    if sub is not None:
        try:
            sw_assembly.add_component(sub, str(p1), 0.0, 0.0, 0.0)
            sw_assembly.add_component(sub, str(p2), 60.0, 0.0, 0.0)
            sub_path = WORK / "sub.SLDASM"
            sw_connect.save_document(sub, str(sub_path))
            sub_ok = sub_path.is_file()
        except Exception as e:                                          # noqa: BLE001
            out["sub_error"] = "%s: %s" % (type(e).__name__, str(e)[:130])
    out["subassembly_saved"] = sub_ok
    print("★ ② 子装配落盘 ⇒ %r" % sub_ok)

    #: ③ 建**顶层装配**并加**子装配**
    top = sw_connect.new_document(sw, "assembly")
    inst_ok = False
    if top is not None and sub_ok:
        try:
            sw_assembly.add_component(top, str(WORK / "sub.SLDASM"), 0.0, 0.0, 0.0)
            inst_ok = True
        except Exception as e:                                          # noqa: BLE001
            out["top_error"] = "%s: %s" % (type(e).__name__, str(e)[:130])
    out["subassembly_inserted"] = inst_ok
    print("★ ③ 顶层装配加子装配 ⇒ %r" % inst_ok)

    #: ④ **按对象选**那个组件（★ `IComponent2.Select4`，★ 无 mark ✓）
    comps = _components(top) if top is not None else []
    out["component_count"] = len(comps)
    sel_ok = False
    is_sp_before = None
    if comps:
        try:
            is_sp_before = bool(sw_connect.get_com_member(comps[0], "IsSpeedPak"))
            sw_connect.get_com_member(comps[0], "Select4", False,
                                      sw_connect.create_empty_dispatch_variant())
            import sw_selection_spec as SS
            sel_ok = SS.get_selection_count(top) > 0
        except Exception as e:                                          # noqa: BLE001
            out["select_error"] = "%s: %s" % (type(e).__name__, str(e)[:130])
    out["component_selected"] = sel_ok
    out["is_speedpak_before"] = is_sp_before
    print("★ ④ 选组件 ⇒ %r · 组件数=%r · 选前 IsSpeedPak=%r"
          % (sel_ok, len(comps), is_sp_before))

    #: ⑤ **调**（★ `SpeedPakType = 1` = Mated ✓）
    ret = None
    exc = None
    if top is not None:
        try:
            #: ★★★ 按**契约**调：★ `sw_assembly_doc.call_assembly_doc(doc, member, *args)`
            #:   **直接拿 `doc` 当 `IAssemblyDoc`** ✓（★ 我第一版写
            #:   `get_com_member(top, "AssemblyDoc")` ⇒ ★ `AttributeError: <unknown>.AssemblyDoc` ✗
            #:   —— ★ **装配体文档本身就是 `IAssemblyDoc`** ✓）
            #:   ★★ 且它**有实参个数登记表** ⇒ ★ 名字不在表里会**抛 `KeyError`（不静默忽略）** ✓
            import sw_assembly_doc as AD
            ret = AD.call_assembly_doc(top, "CreateSpeedPak", 1)
            out["arity_checked"] = True
        except Exception as e:                                          # noqa: BLE001
            exc = e
    #: ⑥ **回读**（★ 判据 = 「它真正改变的东西」✓）
    is_sp_after = None
    if comps:
        try:
            is_sp_after = bool(sw_connect.get_com_member(comps[0], "IsSpeedPak"))
        except Exception:                                               # noqa: BLE001
            is_sp_after = None
    out.update({"returned": str(ret), "is_speedpak_after": is_sp_after,
                "exception": None if exc is None else "%s: %s" % (type(exc).__name__, str(exc)[:150])})

    if is_sp_after:
        out["verdict"] = ("★★★★★ **建成** —— ★ `IComponent2::IsSpeedPak` **%r → %r**"
                          "（★ 回读、不是信返回值 ✓）· ★ `CreateSpeedPak` 回 %r ✓"
                          % (is_sp_before, is_sp_after, ret))
    elif exc is not None:
        out["verdict"] = "★★ **抛**：%s" % out["exception"]
    else:
        out["verdict"] = ("★★ **不建**（★ 回 %r · ★ IsSpeedPak 仍 %r）⇒ ★ **还不算试死** —— "
                          "★ 前置复核：★ 零件=%r · 子装配=%r · 插入=%r · 选中=%r"
                          "（★ 定则：「读到静默」≠「判定试死」✓）"
                          % (ret, is_sp_after, out["parts_saved"], sub_ok, inst_ok, sel_ok))
    print("★★ 调用后 ⇒ 回 %r · ★★ IsSpeedPak = %r" % (ret, is_sp_after))
    print("★★★ 判定 ⇒ %s" % out["verdict"])

    p = ROOT / "output" / "spec211-b6-speedpak.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    import traceback
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:                                              # noqa: BLE001
        tb = traceback.format_exc()
        (ROOT / "output" / "spec211-b6-speedpak-traceback.txt").write_text(tb, encoding="utf-8")
        print("★★ 异常已落盘：\n%s" % tb[-1200:])
        raise SystemExit(3)
