"""★ 把指纹标定结果落成**可提交的记录**（规格 210 · B2 的收口产物）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（生成器）
# 文件:   tools/gen_fingerprint_calibration.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B2 收口**。★ 验收判据原话：
#   ★「**每一类状态都有灵敏度证据**，**或明写「这类写入当前不可见」**」✓
#   ⇒ ★ 所以 B2 的产物**不是**「全都敏感」，★ 而是**逐类都有结论 + 证据** ✓
# 判据:   ★ 读 `output/spec210-fingerprint-calib.json`（真机跑出来的），
# ★ 生成 `docs/spec210-fingerprint-calibration.md`：★ 每类一行，写**结论 + 写操作 + 前后
# 值 + 说明** ✓
#   ★★ 三档语义（★ 严格区分，不许混）：
#     `sensitive`   = ★ 写操作**动了**这一类 ⇒ **有灵敏度证据** ✓
# `not_detected`= ★ 写操作**成功**而读数**没动** ⇒ ★ **这一类在本形状下不可见**（★ 如实
# 记）✓
#     `unreadable`  = ★ **读数本身读不到** ⇒ ★ 与「不可见」**不是一回事**（★ 读数要修）✓
#     `untested`    = ★ 本轮**没试** ⇒ ★ **不许**当上面任何一档 ✓
# 官方依据: 读数出处见 `scripts/sw_fingerprint.py` 的 `OFFICIAL`
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
SRC = ROOT / "output" / "spec210-fingerprint-calib.json"
OUT = ROOT / "docs" / "spec210-fingerprint-calibration.md"

VERDICT_NOTE = {
    "sensitive": "★ **有灵敏度证据**（写操作动了这一类）",
    "not_detected": "★★ **这一类在本形状下不可见**（写操作**成功**而读数没动）",
    "unreadable": "★★ **读数本身读不到**（★ 与「不可见」**不是一回事** —— 读数要修）",
    "untested": "★ **本轮没试**（★ 不许当上面任何一档）",
}


def main() -> int:
    if not SRC.is_file():
        print("★ 没有标定结果：%s ⇒ 先跑 tools/probe_fingerprint_sensitivity.py" % SRC)
        return 1
    d = json.loads(SRC.read_text(encoding="utf-8"))
    s0 = d.get("step0_readonly") or {}
    classes = d.get("classes") or {}
    counts: dict = {}
    for v in classes.values():
        counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1

    lines = [
        "# 规格 210 · 指纹标定记录（B2 的收口产物）",
        "",
        "> ★ 由 `tools/gen_fingerprint_calibration.py` 从**真机标定结果**生成 —— **不要手改**。",
        "> ★★ 验收判据（规格 210 · B2）：**每一类状态都有灵敏度证据，或明写「这类写入当前不可见」** ✓",
        "",
        "## 第 0 格 · 读数只读（★ 先验「量具本身不改状态」）",
        "",
        "★ 连读三次、**只比第 2 与第 3 次**（★ 第 1 次当「加热」，★ 因为刚建好的零件还在自己稳）：",
        "**%s**"
        % (
            "完全相等 ✓ —— 读数**没有副作用**"
            if s0.get("equal")
            else "★ 不相等 ✗ —— 读数里有东西会自己变"
        ),
        "",
        "★ 读不到的类：%s" % (", ".join(sorted(s0.get("missing") or {})) or "（无）"),
        "",
        "## 逐类结论",
        "",
    ]
    for cls in sorted(classes):
        v = classes[cls]
        lines += [
            "**`%s`** ⇒ `%s`" % (cls, v["verdict"]),
            "",
            "· 结论：%s" % VERDICT_NOTE.get(v["verdict"], "?"),
            "· 写操作：`%s`（返回体说成功：%s）"
            % (v.get("writer") or "（无）", v.get("writer_ok")),
            "· 读数：前 `%r` ⇒ 后 `%r`" % (v.get("before"), v.get("after")),
        ]
        why = v.get("why")
        if why:
            lines.append("· 说明：%s" % str(why)[:220])
        lines.append("")

    lines += [
        "## 三档统计",
        "",
        "★ 「 + 」 · ".join("%s **%d**" % (k, n) for k, n in sorted(counts.items())),
        "",
        "★★ **收口判据的满足情况**：★ 有灵敏度证据的 **%d** 类；★ 明确记「不可见 / 读数待修 / 没试」的 **%d** 类；"
        "★ 两者相加 = **%d**，★ 与九类相等则**每一类都有结论** ✓"
        % (
            counts.get("sensitive", 0),
            sum(n for k, n in counts.items() if k != "sensitive"),
            len(classes),
        ),
        "",
        "## ⚠ 本记录的限度（★ 不许当成「九类全都敏感」）",
        "",
        "· ★ **`not_detected` 不等于「读数瞎」** —— ★ 真机查明它多半是"
        "「**写操作没有真的改变任何东西**」（★ 前置已满足 / 参数被复用 / 缺前置）✓",
        "· ★ **`unreadable` 与 `not_detected` 是两件事**（★ 前者是**读数**的问题，★ 后者是**这一类不可见**）✓",
        "· ★ 标定**每一类各用一个新零件** —— ★ 同一文档上顺序标定会**互相污染**（★ 真机踩过："
        "前面的类把文档弄脏/用掉草图 ⇒ 后面的类「没得变了」）✓",
        "",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("★ 已生成 %s" % OUT)
    print("★ 三档：%s" % counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
