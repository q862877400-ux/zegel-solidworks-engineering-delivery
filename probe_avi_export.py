r"""@brief 探针：走通 `IMotionStudy::SaveToAVI` —— 护城河第三域「动画导出 AVI」能不能真的出文件。

## 为什么探这一条
`capabilities.yaml` 的 `animation_export` 是**护城河三域里唯一剩下的空缺**（现 `not_implemented`），
而 2026-10-01（轮 62/63）在官方反射里查到了**确切成员**：
```
Boolean      IMotionStudy::SaveToAVI(String, AVIParameter)
AVIParameter IMotionStudyManager::CreateAVIParameter()
```
⚠ 这**推翻**了我此前写进仓库的一句结论「AVI 由哪个成员写出尚未查证到」——
那是**检索疏漏**（只搜了 `SaveAnimation`/`SaveMovie`，**没搜 `SaveToAVI`**）。

## 本探针要回答
1. Motion 类型库能不能加载（`ensure_motion_type_library`）；
2. 装配体的 `GetMotionStudyManager` 能不能拿到；
3. **`CreateAVIParameter()` 返回什么**；
4. **`SaveToAVI(path, param)` 之后文件**真的**出现吗**（⚠ 返回值不可信 ⇒ 以文件为准）。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_avi_export.py
# 定位:   AGENTS.md 铁律 2 的第二关。签名依据 `IMotionStudy` / `IMotionStudyManager` /
#         `IAVIParameter` 的官方反射（`D:\AI\SW\_raw\reflect\iface_swmotionstudy.txt`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；**只用自己新建的文档**；收尾恢复 CommandInProgress 并关自己的文档。
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_REPO = Path(r"C:\swprojects\sw-skill-fork")
for _p in (str(_REPO), str(_REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_motion as M  # noqa: E402


def step(label, fn):
    try:
        v = fn()
        print("   %-40s ⇒ %r" % (label, v))
        return v
    except Exception as exc:  # noqa: BLE001
        print("   %-40s ⇒ ✗ %s: %s" % (label, type(exc).__name__, str(exc)[:100]))
        return None


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        print("=== ① Motion 类型库 ===")
        step("ensure_motion_type_library()", lambda: M.ensure_motion_type_library())

        print()
        print("=== ② 自建装配体（**只碰自己的文档**）===")
        model = new_document(sw, doc_type="assembly")
        title = get_com_member(model, "GetTitle")
        print("   文档: %r" % title)
        if title is None:
            print("   ⚠ 装配体没建起来 ⇒ 停")
            return 1

        mgr = step("get_motion_study_manager(model)", lambda: M.get_motion_study_manager(model))
        if mgr is None:
            print("   ⚠ 拿不到 MotionStudyManager ⇒ 停（Motion 加载项/许可？）")
            return 2

        print()
        print("=== ③ 建运动算例 ===")
        study = step("create_motion_study(model)", lambda: M.create_motion_study(model))
        step("study.GetDuration()", lambda: M.motion_member(study, "GetDuration") if study else None)

        print()
        print("=== ④ ★ CreateAVIParameter（工厂在 manager 上）===")
        param = step("create_avi_parameter(mgr)", lambda: M.create_avi_parameter(mgr))
        if param is not None:
            for name in ("FramePerSecond", "SaveEntireAnimation", "ImageSize",
                         "OutputType", "RendererType", "ScreenWidth", "ScreenHeight"):
                step("  param.%s（默认值回读）" % name,
                     lambda n=name: getattr(param, n))
            applied = step("configure_avi_parameter(FramePerSecond=12, SaveEntireAnimation=True)",
                           lambda: M.configure_avi_parameter(
                               param, FramePerSecond=12.0, SaveEntireAnimation=True))
            print("     回读: %r" % (applied,))

        print()
        print("=== ⑤ ★★ SaveToAVI（**以文件为准，不看返回值**）===")
        out = os.path.join(tempfile.gettempdir(), "mcp_avi_probe.avi")
        if os.path.isfile(out):
            os.remove(out)

        # ⚠ 先算一遍：空算例大概率**没有动画数据** ⇒ 导出的文件是 0 字节
        #   （实测：不 Calculate 而直接 SaveToAVI ⇒ `returned=True` 但文件 0 字节）
        print("   ── 先 Calculate（否则算例没有动画数据）──")
        step("calculate_and_play(study, play=False)",
             lambda: M.calculate_and_play(study, play=False))
        step("study.GetDuration()（算后）",
             lambda: M.motion_member(study, "GetDuration") if study else None)

        if study is not None:
            res = step("export_motion_study_avi(study, %s)" % out,
                       lambda: M.export_motion_study_avi(study, out, param))
            print()
            if res:
                print("   ★ 文件存在 = %s · 大小 = %s 字节" % (res["exists"], res["size_bytes"]))
                print("   ★ 官方返回值 = %r（⚠ 本项目纪律：**返回值不可信，以文件为准**）"
                      % (res["returned"],))
                print("   ★ 判定 = %s" % ("**通过**" if res["ok"] else "**未通过**"))
                if not res["ok"]:
                    print("   ⇒ 返回 True 但文件 0 字节 = **「返回码撒谎」的又一例**："
                          "空装配体没有动画可导。")
        else:
            print("   跳过（没有 study）")
        return 0
    finally:
        try:
            if title:
                sw.CloseDoc(title)
        except Exception:  # noqa: BLE001
            pass
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        print()
        print("收尾完成（文档未保存；CommandInProgress 已恢复）")


if __name__ == "__main__":
    raise SystemExit(main())
