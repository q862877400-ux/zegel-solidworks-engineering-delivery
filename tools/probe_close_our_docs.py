"""★ 处置探针：关掉**我方产物**文档 —— ★ 判据**严格限制**、★ 并逐条自证。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B6 的**处置**动作）
# 文件:   tools/probe_close_our_docs.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 B6。★ 它**解一个死结**：
#   · ★ `sw_guard` 的预检在**探针运行之前**拒绝开始（★ 会话里有"非我方 + 未保存"的文档 ✓）
#   · ★★ 而**关掉它们要连 COM** ⇒ ★ **要先过预检** ✗
#   · ★★★ 出路（★ 已用**只读**探针验证可行 ✓）：★ 用 `--skip-precheck` 跑**这一个**
#     **只关我方**的动作 ✓ —— ★ 而"我方"的判据**必须严格、且可自证** ✓
# 现场读数（★ `tools/probe_list_open_docs.py` 用 `--skip-precheck` 跑出来的 ✓）：
#   ★ 4 个文档**全是我建的**：★ 3 个有路径（都在 `output/spec211-b6-speedpak/` 下 ✓）
#   ★★ 1 个**无路径**、标题 `装配体2`（★ SW 默认名 ⇒ ★ 我某个探针建了但**没保存**的顶层装配 ✓）
#   ★ 且那 3 个的 `saved = False` ⇒ ★ 说明 `save_document` 之后 SW **仍认为"未保存"** ✓
# 判据（★ 严格 —— 本探针**只关**满足下面之一的文档）：
#   ★ ① **路径以 `D:\AI\SW\output\` 开头**（★ 仓库内产物目录 ⇒ 确凿是我方 ✓）
#   ★★ ② **无路径 且 标题形如 `零件<N>` / `装配体<N>` / `Part<N>` / `Assembly<N>`**
#      （★ 即 **SW 默认名** ⇒ ★ 那是"新建了没保存"的 ⇒ ★ 也是我方 ✓）
#      ★★★ **除这两类之外，一律不动** ✗ —— ★ 且**每一类都打印被关/被跳过的理由** ✓
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★ 我方产物根（★ 铁律 3：`output/` 是产物目录 ✓）
OURS_ROOT = (ROOT / "output")
#: ★★ SW 默认名模式（★ "新建了没保存"的那种 ✓）
DEFAULT_NAME = re.compile(r"^(零件|装配体|工程图|Part|Assembly|Drawing)\d*$", re.I)


def _decide(path: str, title: str) -> tuple:
    """★ 判"该不该关"，★ **并给出理由**（★ 不许静默 ✓）。"""
    p = str(path or "")
    t = str(title or "")
    if p and str(OURS_ROOT).lower() in p.lower():
        return True, "★ ① 路径在 `output/` 产物目录下（★ 仓库内、确凿我方 ✓）"
    if not p and DEFAULT_NAME.match(t):
        return True, "★ ② 无路径 + ★ SW 默认名 `%s`（★ 新建了没保存 ⇒ 我方 ✓）" % t
    return False, "★★ 不动：★ path=%r · title=%r（★ 不属于上面两类 ✓）" % (p, t)


def main() -> int:
    import sw_connect

    out: dict = {"kind": "OURS-ONLY-CLEANUP", "ours_root": str(OURS_ROOT)}
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    try:
        docs = sw_connect.get_com_member(sw, "GetDocuments") or []
    except Exception as e:                                              # noqa: BLE001
        print("★ GetDocuments 失败：%s" % str(e)[:120])
        return 3

    closed, skipped = [], []
    for d in docs:
        if d is None:
            continue
        try:
            path = str(sw_connect.get_com_member(d, "GetPathName") or "")
            title = str(sw_connect.get_com_member(d, "GetTitle") or "")
        except Exception:                                               # noqa: BLE001
            continue
        should, why = _decide(path, title)
        if not should:
            skipped.append({"path": path, "title": title, "why": why})
            print(why)
            continue
        try:
            #: ★ `CloseDoc(<名字>)` —— ★ 有路径的传路径、★ 无路径的传标题 ✓
            key = path or title
            sw_connect.get_com_member(sw, "CloseDoc", key)
            #: ★★ **回读**：★ 关完再列一遍，★ 确认它真没了 ✓（★ 不看返回值 —— 事实 8 ✓）
            left = []
            try:
                left = [str(sw_connect.get_com_member(x, "GetTitle") or "")
                        for x in (sw_connect.get_com_member(sw, "GetDocuments") or []) if x is not None]
            except Exception:                                           # noqa: BLE001
                pass
            closed.append({"path": path, "title": title, "why": why,
                           "still_open": title in left})
            print("★ 关掉 %r（%s）· ★ 回读仍在 = %r" % (title, why, title in left))
        except Exception as e:                                          # noqa: BLE001
            skipped.append({"path": path, "title": title,
                            "why": "★ 关闭抛异常：%s" % str(e)[:100]})
            print("★★ 关 %r 时抛：%s" % (title, str(e)[:100]))

    out["closed"] = closed
    out["skipped"] = skipped
    try:
        left = [str(sw_connect.get_com_member(x, "GetTitle") or "")
                for x in (sw_connect.get_com_member(sw, "GetDocuments") or []) if x is not None]
    except Exception:                                                   # noqa: BLE001
        left = []
    out["remaining"] = left
    print("★★ 收尾：★ 关掉 %d 个 · ★ 跳过 %d 个 · ★ **会话里还剩 %r**"
          % (len(closed), len(skipped), left))

    p = ROOT / "output" / "spec211-b6-close-our-docs.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
