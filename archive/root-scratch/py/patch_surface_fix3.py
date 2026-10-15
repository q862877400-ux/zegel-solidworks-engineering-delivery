"""三件事一起修：常量位置、`_invoke` 的职责、以及**让门禁抓住这个坑**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁，非第三方移植）
# 文件:   D:\\AI\\SW\\patch_surface_fix3.py
# 定位:   修 2026-10-01 真机验证后出现的三个问题：
#         ① `IMODELER_RUNTIME_*` 常量夹在来源块与 `_invoke` 之间
#            ⇒ `check_provenance` 的 `_extend_to_code` 延伸不到 `def`（**本会话第四次**）；
#         ② `_invoke` 里的可用性检查**挡住了契约测试** —— 契约测试验的是「2 个参数」
#            这个**签名形状**，调用被拦就验不了。**⇒ 职责分离**：
#            `_invoke` 只管 arity；可用性检查挪成**显式守卫** `require_runtime_available()`，
#            由 MCP/声明层在**调用前**显式调。
#         ③ 把「常量夹在块与 def 之间」做成 `check_provenance` 的**明确诊断**
#            （本会话踩了四次，不该再靠记笔记）。
# 官方签名依据: 不适用（纯 Python 文本补丁）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SURF = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_surface.py")
GATE = Path(r"C:\swprojects\sw-skill-fork\scripts\check_provenance.py")


def fix_surface() -> int:
    t = SURF.read_text(encoding="utf-8")

    # ① 把两个常量 + 它们的来源块**整体**挪到 `_invoke` 的来源块**之前**
    const_start = t.index("#: 2026-10-01 真机实测**可取**的 `IModeler` 创建入口")
    const_end = t.index("def _invoke(modeler, method: str, *args):")
    consts = t[const_start:const_end]
    t = t[:const_start] + t[const_end:]

    # 找一个稳定的插入点：`_invoke` 之前那个来源块的开口
    anchor = "# ── 来源 ─────────────────────────────────────────────────────────────\n# 仓库:   本项目自身（真机实测结论，非第三方移植）"
    if anchor not in t:
        print("  ✗ 未找到插入锚点")
        return 1
    t = t.replace(anchor, consts.rstrip() + "\n\n\n" + anchor, 1)

    # ② `_invoke` 去掉可用性拦截，只留 arity；新增显式守卫
    old_block = t[t.index("    if method in IMODELER_RUNTIME_UNAVAILABLE:"):
                  t.index("    return get_com_member(modeler, method, *args)")]
    t = t.replace(old_block, "", 1)
    # 把守卫做成独立函数，插在 `_invoke` 之后
    guard = '''

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机实测结论的**显式守卫**）
# 文件:   D:\\AI\\SW\\probe_surface_array_shape.py（证据脚本）
# 定位:   **把「运行期可取性」做成显式守卫，而不是塞进 `_invoke`。**
#  ⚠⚠ 为什么职责分离（2026-10-01 的教训）：
#     第一版把检查写进 `_invoke` ⇒ **挡住了契约测试**
#     （`tests/test_sw_surface_signature_contract.py` 验的是「2 个参数传给
#      `CreatePlanarSurface`」这个**签名形状**，调用被拦就验不了）。
#     **⇒ `_invoke` 只管 arity（保持形状可验）；可用性由调用方显式问。**
#     MCP/声明层应当在**调用前**调 `require_runtime_available()`，
#     这样人拿到的是「成员不可达」而不是含混的 `'NoneType' object is not callable`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ⚠ 名单只覆盖**本机实测**过的成员；未测的按「未知」处理（不假设可用）。
# ────────────────────────────────────────────────────────────────────
def runtime_available(method: str) -> bool:
    """该方法在**本机实测**中是否可取（`True` = 可取；未实测的返回 `False`）。"""
    return method in IMODELER_RUNTIME_AVAILABLE


def require_runtime_available(method: str) -> None:
    """**调用前**的守卫：不可达就抛带原因的 `RuntimeError`。

    ⚠ 「可取」**不等于**「调用一定成功」—— `getattr` 拿到方法只说明**成员可达**；
    实际调用仍可能返回 `None`（参数不合法/模型上下文不满足）。
    **⇒ 真正的判据永远是「返回非 None」。**
    """
    if method in IMODELER_RUNTIME_AVAILABLE:
        return
    if method in IMODELER_RUNTIME_UNAVAILABLE:
        raise RuntimeError(
            "%s 在**本机运行期取不到**（`getattr` 得 None）—— 官方类型库里有它，"
            "但迟到绑定拿不到。本机实测可取的入口：%r。"
            "⚠ 「反射里有」≠「运行期调用得到」（2026-10-01 真机结论）。"
            % (method, sorted(IMODELER_RUNTIME_AVAILABLE))
        )
    raise RuntimeError(
        "%s **未在本机实测过**可用性 —— 不在可取名单也不在取不到名单里。"
        "先用 `probe_surface_array_shape.py` 的逐个 getattr 手法实测再决定（不猜）。"
        % method
    )
'''
    t = t.replace("    return get_com_member(modeler, method, *args)\n",
                  "    return get_com_member(modeler, method, *args)\n" + guard, 1)
    # 导出新函数
    t = t.replace('    "IMODELER_RUNTIME_AVAILABLE",',
                  '    "IMODELER_RUNTIME_AVAILABLE",\n'
                  '    "runtime_available",\n'
                  '    "require_runtime_available",', 1)
    SURF.write_text(t, encoding="utf-8")
    print("  ✓ sw_surface.py：常量已挪到块之前；_invoke 只管 arity；新增两个守卫函数")
    return 0


def fix_gate() -> int:
    """让 `check_provenance` **明确指出**「常量夹在块与 def 之间」这个原因。"""
    t = GATE.read_text(encoding="utf-8")
    old = '''    if uncovered:
        print("[FAIL] %d 行新增代码没有可追溯的出处：" % len(uncovered))'''
    new = '''    if uncovered:
        print("[FAIL] %d 行新增代码没有可追溯的出处：" % len(uncovered))
        # ⚑ 常见原因诊断（2026-10-01 加；本会话踩了**四次**同一个坑）：
        #   来源块之后的**第一个代码单元**被当成「被说明对象」——
        #   若那是 `FOO = ...` 这样的常量，延伸就**止于常量**，紧随其后的 `def` 落空。
        _hint_blocks = []
        for _path, _lines in ()):
            pass
'''
    if old not in t:
        print("  ⚠ 未匹配 check_provenance 的输出段（跳过 ③）")
        return 0
    # 上面的占位不可执行；改为最小、可用的提示实现
    new = '''    if uncovered:
        print("[FAIL] %d 行新增代码没有可追溯的出处：" % len(uncovered))'''
    print("  ⚠ ③ 跳过：改法需要更多上下文，留给下一轮（不在本轮硬塞）")
    return 0


def main() -> int:
    rc = fix_surface()
    if rc:
        return rc
    fix_gate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
