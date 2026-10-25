"""★ S3 阻塞台账的双向校验门禁。

## 判据（两个方向都查，缺一侧就是盲区）

| 方向 | 情形 | 结论 |
|---|---|---|
| ① | `s3-acceptance.md` 有不合格项，台账里没登记 | **fail** —— 有阻塞没登记，读者会当成「没跑」 |
| ② | 台账登记了，但报告里已不在不合格项 | **fail** —— 陈旧阻塞，问题解决了却没删 |
| ③ | 台账的 `evidence` 指向的文件不存在 | **fail** —— 证据断了 |
| ④ | `cause` / `owner` 不在封闭词表 | **fail** —— 分类自造 |

★ 报告是**机器生成**的（`tools/run_s3_acceptance.py` → `report.py`），
  台账是**人写的**；门禁把两者钉在一起 ⇒ 谁都不能单方面漂移。

## 报告里怎么找「不合格项」

`report.py` 渲染的 markdown 有两段固定标题：

```
## 不合格的项
- `E2.rebuild`：…
## 未测到的项（不等于合格）
- `E2.hole_readback`：…
```

门禁**只认这两段里出现的 `E<数字>.<名字>` 形态**，不猜别的位置 ——
若 `report.py` 改了标题，本门禁会因「一段都找不到」而红（宁可红，不可静默空转）。

## 负例自证

`tests/test_s3_blockers_gate.py` 用三种伪造台账证明本门禁抓得到：
① 少登记一条 ② 多登记一条（陈旧）③ 证据路径不存在。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把「阻塞也必须被核对」做成静态门禁）
# 文件:   scripts/check_s3_blockers.py
# 定位:   校验 docs/s3-blockers.yaml 与**机器生成**的
#          specs/350-first-part-delivery/s3-acceptance.md 双向一致：
#          ① 报告里有不合格项、台账没登记 ⇒ 红（读者会当成「没跑」）
#          ② 台账登记了、报告里已不阻塞 ⇒ 红（陈旧断言）
#          ③ 台账 evidence 指向的文件不存在 ⇒ 红
#          ④ cause/owner 不在封闭词表 ⇒ 红
#          这四种失效在本仓都发生过（事实 422 陈旧 22 天 · 第 26 轮的成功读数
#          第 27 轮复现不出来）⇒ 把「阻塞」也变成机器可判的契约。
# 官方依据: 不适用（纯本地静态比对，不调 SolidWorks API、不联网）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "specs" / "350-first-part-delivery" / "s3-acceptance.md"
LEDGER = ROOT / "docs" / "s3-blockers.yaml"

#: 封闭词表
CAUSES = frozenset({"toolchain", "requirement", "environment"})
OWNERS = frozenset({"agent", "user"})

#: 报告里「不合格 / 未测到」两段的固定标题（`report.py` 渲染）
_SECTIONS = ("## 不合格的项", "## 未测到的项（不等于合格）")

_CHECK_ID = re.compile(r"`(E[1-7]\.[A-Za-z0-9_]+)`")


def failing_check_ids(markdown: str) -> tuple[set, list]:
    """★ 从报告里抽出「不合格 + 未测到」的 check_id，并回报每段各抽到几条。

    ★ 第二个返回值是 `[(段标题, 抽到的数量), ...]` —— 让调用方看到
      **是哪一段空了**，而不是只得到一个空集合。
    """
    ids: set = set()
    detail: list = []
    lines = markdown.splitlines()
    for head in _SECTIONS:
        try:
            start = lines.index(head)
        except ValueError:
            detail.append((head, -1))  #: -1 = 这一段没找到
            continue
        found = 0
        for line in lines[start + 1:]:
            if line.startswith("## "):
                break
            for m in _CHECK_ID.finditer(line):
                ids.add(m.group(1))
                found += 1
        detail.append((head, found))
    return ids, detail


def load_ledger(text: str) -> tuple[list, list]:
    """★ 解析台账；返回 `(blockers, problems)`，problems 是**结构问题**清单。"""
    problems: list = []
    try:
        data = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        return [], ["台账不是合法 YAML：%s" % str(exc)[:160]]
    blockers = data.get("blockers")
    if not isinstance(blockers, list):
        return [], ["台账缺 `blockers` 列表"]
    for i, b in enumerate(blockers):
        if not isinstance(b, dict):
            problems.append("第 %d 项不是字典" % (i + 1))
            continue
        cid = b.get("check_id")
        if not re.match(r"^E[1-7]\.[A-Za-z0-9_]+$", str(cid or "")):
            problems.append("第 %d 项的 check_id 形态不对：%r" % (i + 1, cid))
        if b.get("cause") not in CAUSES:
            problems.append(
                "第 %d 项 cause=%r 不在封闭词表 %s"
                % (i + 1, b.get("cause"), sorted(CAUSES))
            )
        if b.get("owner") not in OWNERS:
            problems.append(
                "第 %d 项 owner=%r 不在封闭词表 %s"
                % (i + 1, b.get("owner"), sorted(OWNERS))
            )
        if not str(b.get("summary") or "").strip():
            problems.append("第 %d 项 summary 为空" % (i + 1))
        ev = b.get("evidence")
        if not isinstance(ev, list) or not ev:
            problems.append("第 %d 项 evidence 不是非空列表" % (i + 1))
            continue
        for p in ev:
            if not (ROOT / str(p)).exists():
                problems.append("第 %d 项的证据文件不存在：%s" % (i + 1, p))
    return blockers, problems


def check(report_text: str, ledger_text: str) -> tuple[bool, list]:
    """★ 双向校验。返回 `(是否通过, 问题清单)`。"""
    problems: list = []

    if not report_text.strip():
        return False, ["验收报告是空的（先跑 tools/run_s3_acceptance.py）"]

    failing, detail = failing_check_ids(report_text)
    missing_sections = [h for h, n in detail if n < 0]
    if len(missing_sections) == len(_SECTIONS):
        return False, [
            "报告里一段「%s」都没找到 ⇒ 渲染格式变了，门禁无法判断（宁可红）"
            % " / ".join(_SECTIONS)
        ]

    blockers, struct = load_ledger(ledger_text)
    problems.extend(struct)

    declared = {str(b.get("check_id")) for b in blockers if isinstance(b, dict)}

    #: ① 有不合格项但没登记
    for cid in sorted(failing - declared):
        problems.append(
            "★ 报告里 `%s` 不合格，但 `docs/s3-blockers.yaml` 没登记 "
            "⇒ 读者会把它当成「没跑」" % cid
        )

    #: ② 登记了但已经不阻塞（陈旧）
    for cid in sorted(declared - failing):
        problems.append(
            "★ `docs/s3-blockers.yaml` 登记了 `%s`，但报告里它已不在不合格项 "
            "⇒ 陈旧阻塞，必须删掉或更新" % cid
        )

    return (not problems), problems


def main() -> int:
    if not REPORT.is_file():
        print("★ 找不到验收报告：%s" % REPORT)
        print("  ⇒ 先跑 `python tools/run_s3_acceptance.py`")
        return 1
    if not LEDGER.is_file():
        print("★ 找不到阻塞台账：%s" % LEDGER)
        return 1
    ok, problems = check(
        REPORT.read_text(encoding="utf-8"), LEDGER.read_text(encoding="utf-8")
    )
    failing, detail = failing_check_ids(REPORT.read_text(encoding="utf-8"))
    print("★ 报告里的不合格/未测到项：%s" % (sorted(failing) or "（无）"))
    for head, n in detail:
        print("   %s ⇒ 抽到 %s 条" % (head, "段缺失" if n < 0 else n))
    blockers, _ = load_ledger(LEDGER.read_text(encoding="utf-8"))
    print("★ 台账登记：%d 条 —— %s" % (len(blockers), sorted(
        str(b.get("check_id")) for b in blockers)))
    if ok:
        print("★ [PASS] 阻塞台账与验收报告双向一致（无未登记、无陈旧、证据齐全）")
        return 0
    print("★ [FAIL] %d 处：" % len(problems))
    for p in problems:
        print("   - %s" % p)
    return 1


if __name__ == "__main__":
    sys.exit(main())
