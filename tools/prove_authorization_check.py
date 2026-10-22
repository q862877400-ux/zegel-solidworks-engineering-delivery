"""@brief 判据有效性检验：R11 的静态检查必须能抓到迁移前那两处真实泄漏。

「门禁绿」本身不构成证据 —— 一个永远绿的检查也是绿的。
本脚本用**迁移前的真实代码行**喂给它，确认命中；再用**修复后的行**喂它，确认放过。

# ── 来源 ──
# 仓库:   本项目自身（执行方对上游能力清单的迁移改造，非第三方移植）
# 文件:   tools/prove_authorization_check.py
# 定位:   docs/capabilities-schema-proposal.md §五 R11；
#         AGENTS.md 铁律 1 与「验收判据写成可 grep 项」——
#         门禁必须证明它能拒绝一个真实的反例，不能只有绿灯。
# 许可:   本仓库 MIT。本文件为原创实现，无第三方代码引入。
# ⚠ 未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）；本脚本是纯文本判据的单元验证。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_union_conventions import (  # noqa: E402
    AUTHORIZATION_ASSIGN,
    LEVEL_IN_LINE,
    _authorization_functions,
)

#: 2026-10-03（接手轮）强制 stdout 为 UTF-8 —— 本脚本会 print 中文/箭头/勾这类符号，
#:   而 stdout 是管道时（测试正是用管道抓输出）默认按 locale（本机 GBK）编码
#:   ⇒ UnicodeEncodeError: 'gbk' codec can't encode character ... ⇒ 脚本自己崩掉。
#:   known-facts 58 那一族（中文 Windows 上两侧默认编码不一致 —— 病灶在输出侧）。
#: ★ 插在**多行 import 的右括号之后**（第一版插在 `from ...(` 那行后面，把它劈开了 ⇒ Syn
#: taxError）。
sys.stdout.reconfigure(encoding="utf-8")

#: 迁移前**真实存在**的授权推断（2026-10-01 实测的 4 条路径里的 2 条）+ 两种违规形状
MUST_CATCH = (
    (
        "scripts/sw_capability_probe.py:142（迁移前的真实泄漏）",
        '            "ready_for_unattended_use": manifest_index.get(CAPABILITY_ALIASES[capability], {}).get("level") == "verified" and len(matches) == len(interface_names),',
    ),
    ("形状①：写死授权变量", '        authorized = item.get("level") == "verified"'),
    (
        "形状①：无人值守标志",
        '    unattended = capabilities[cid]["level"] == CapabilityLevel.VERIFIED',
    ),
)

#: **形状②**：授权函数体内按 level 判授权 —— 即 unattended_allowed() 被改回旧实现
MUST_CATCH_IN_FUNCTION = (
    (
        "形状②：unattended_allowed 被改回旧实现",
        "unattended_allowed",
        [
            "def unattended_allowed(capability_ids, payload=None) -> bool:",
            '    return all(capability_level(cid, payload) == "verified" for cid in capability_ids)',
        ],
    ),
    (
        "形状②：另一个授权函数",
        "ready_for_unattended_use",
        [
            "def ready_for_unattended_use(cid):",
            '    return index[cid].get("level") == "verified"',
        ],
    ),
)

#: 修复后**真实存在**的行，以及合法的等级断言 —— 都不该被命中
MUST_PASS = (
    (
        "scripts/sw_capability_probe.py:154（修复后）",
        '            "ready_for_unattended_use": UNATTENDED_MODE in (manifest_index.get(x, {}).get("allowed_modes") or []) and len(matches) == len(interface_names),',
    ),
    (
        "apps/.../engineering_orchestrator.py:383（消费授权结论，合法）",
        '            if report_item.get("ready_for_unattended_use") is False and level == CapabilityLevel.VERIFIED:',
    ),
    (
        "合法的等级断言（测试里常见）",
        '    assert index["part_and_features"]["level"] == "verified"',
    ),
    (
        "合法的 CAD 版本断言",
        '        if lv == "verified" and is_cad and not c.get("verified_versions"):',
    ),
    ("R11 校验本身", '        if "unattended" in modes and lv != "verified":'),
)


def main() -> int:
    failed = 0
    print("必须命中 —— 形状①（赋值式授权推断）：")
    for label, line in MUST_CATCH:
        hit = bool(AUTHORIZATION_ASSIGN.match(line))
        print("   %s %s" % ("✓ 命中" if hit else "✗ 放过", label))
        if not hit:
            failed += 1

    print()
    print("必须命中 —— 形状②（授权函数体内按 level 判）：")
    for label, func, body in MUST_CATCH_IN_FUNCTION:
        src = "\n".join(body) + "\n"
        auth = _authorization_functions(src)
        hit = any(
            n in auth and LEVEL_IN_LINE.search(ln) for n, ln in enumerate(body, 1)
        )
        print("   %s %s" % ("✓ 命中" if hit else "✗ 放过", label))
        if not hit:
            failed += 1

    print()
    print("必须放过 —— 修复后的写法与合法断言：")
    for label, line in MUST_PASS:
        hit = bool(AUTHORIZATION_ASSIGN.match(line))
        print("   %s %s" % ("✗ 误报" if hit else "✓ 放过", label))
        if hit:
            failed += 1
    # 合法函数体里不该因函数名而误报
    legal_src = (
        "\n".join(
            [
                "def unattended_allowed(capability_ids, payload=None) -> bool:",
                '    return all(UNATTENDED_MODE in (i.get("allowed_modes") or []) for i in items)',
            ]
        )
        + "\n"
    )
    auth = _authorization_functions(legal_src)
    body = legal_src.splitlines()
    legal_hit = any(
        n in auth and LEVEL_IN_LINE.search(ln) for n, ln in enumerate(body, 1)
    )
    print(
        "   %s 修复后的 unattended_allowed（合法）"
        % ("✗ 误报" if legal_hit else "✓ 放过")
    )
    if legal_hit:
        failed += 1

    print()
    if failed:
        print("判据有效性检验未通过：%d 项。门禁的绿灯不可信。" % failed)
        return 1
    print("判据有效性检验通过：5 命中 / 6 放过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
