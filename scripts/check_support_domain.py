"""★ 支持参数域的**校验器 + 域外拒绝器**（规格 350 · FR-013 / FR-014 / T027 / T028）。

## 两种用法，一个判据源

```
python -B scripts/check_support_domain.py --self-check          # 门禁用：校验声明本身
python -B scripts/check_support_domain.py --request req.json    # 判一个请求在不在域内
```

## `--self-check` 查什么（三条）

① **每条声明都有可核证据**：`evidence` 指向的文件必须存在，`#字段` 必须在 JSON 里真能找到。
   ★ 这一条是本文件的重点 —— 「声明支持什么」最容易变成**空口承诺**。
② `limits` 的每个区间 `min ≤ max`，且 `evidence` 非空。
③ `unsupported` 每项都要有 `reason`（不能只写「不支持」而不说为什么）。

## `--request` 判什么

请求形如：

```json
{"part_type": "plate_rect_holes", "plate_width_mm": 120, "hole_count": 4,
 "asks": ["图样"]}
```

三条判据，**任一不满足即域外**：
- `part_type` 必须在 `part_types` 里
- 数值参数必须在 `limits` 区间内
- `asks` 里任何词命中 `unsupported[].match` ⇒ 域外（**哪怕数值都合格**）

★ 域外一律回 `False` + 逐条理由。**不「尽力生成」**——那是 spec 里明写的虚假承诺。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]

DOMAIN = R / "docs" / "support-domain.yaml"


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（发布范围 · 门禁与域外拒绝）
# 文件:   scripts/check_support_domain.py
# 定位:   读 `docs/support-domain.yaml`：① 校验每条声明都有可核证据（门禁）
#          ② 判定请求是否在域内（域外必须拒绝，不勉强生成）。
# 官方依据: 不适用（本仓自定口径）；证据核验靠文件存在性 + JSON 字段可达性
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def load_domain() -> dict:
    import yaml

    return yaml.safe_load(DOMAIN.read_text(encoding="utf-8")) or {}


def _json_get(obj: object, dotted: str) -> tuple:
    """按点分路径取值，回 `(找到?, 值)`。列表用下标。"""
    cur = obj
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return False, None
    return True, cur


def check_evidence(evidence: str) -> tuple:
    """校验一条 `evidence`：文件在、字段可达。回 `(ok, 理由)`。"""
    raw = str(evidence or "").strip()
    if not raw:
        return False, "evidence 为空"
    path_part, _, field = raw.partition("#")
    f = R / path_part
    if not f.is_file():
        return False, "证据文件不存在：%s" % path_part
    if not field:
        return True, ""
    #: 只对 JSON 做字段核验（其它格式只验存在性，如实说明）
    if f.suffix.lower() != ".json":
        return True, ""
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return False, "证据文件读不了：%s" % type(exc).__name__
    found, _ = _json_get(data, field)
    if not found:
        return False, "证据文件 %s 里找不到字段 %s" % (path_part, field)
    return True, ""


def self_check() -> tuple:
    """校验声明本身。回 `(problems, checked)`。"""
    d = load_domain()
    problems: list = []
    checked = 0

    def _ev(where: str, ev: object) -> None:
        nonlocal checked
        checked += 1
        ok, why = check_evidence(str(ev or ""))
        if not ok:
            problems.append("%s：%s" % (where, why))

    env = d.get("environment") or {}
    for k, v in (env.get("solidworks") or {}).items():
        if k == "evidence":
            _ev("environment.solidworks", v)

    for item in d.get("part_types") or ():
        _ev("part_types.%s" % item.get("key"), item.get("evidence"))

    for key, spec in (d.get("limits") or {}).items():
        _ev("limits.%s" % key, (spec or {}).get("evidence"))
        lo, hi = (spec or {}).get("min"), (spec or {}).get("max")
        if lo is not None and hi is not None and float(lo) > float(hi):
            problems.append("limits.%s：min(%s) > max(%s)" % (key, lo, hi))

    for key, spec in (d.get("assembly") or {}).items():
        if isinstance(spec, dict):
            _ev("assembly.%s" % key, spec.get("evidence"))

    for item in d.get("unsupported") or ():
        if not str(item.get("reason") or "").strip():
            problems.append("unsupported.%s：缺 reason" % item.get("key"))
        if not item.get("match"):
            problems.append("unsupported.%s：缺 match 词表" % item.get("key"))

    return problems, checked


def classify(req: dict) -> tuple:
    """判定一个请求在不在域内。回 `(in_domain, reasons)`。"""
    d = load_domain()
    reasons: list = []

    #: ① 零件类型
    types = {str(t.get("key")) for t in (d.get("part_types") or ())}
    pt = str(req.get("part_type") or "")
    if pt not in types:
        reasons.append(
            "零件类型 %r 不在支持列表 %s 内" % (pt, sorted(types))
        )

    #: ② 数值参数
    for key, spec in (d.get("limits") or {}).items():
        if key not in req:
            continue
        val = req[key]
        if not isinstance(val, (int, float)):
            reasons.append("%s=%r 不是数值" % (key, val))
            continue
        lo, hi = (spec or {}).get("min"), (spec or {}).get("max")
        if lo is not None and float(val) < float(lo):
            reasons.append("%s=%s 低于下界 %s" % (key, val, lo))
        if hi is not None and float(val) > float(hi):
            reasons.append("%s=%s 高于上界 %s" % (key, val, hi))

    #: ③ 明确不支持的请求（**哪怕数值都合格也要拒**）
    asks = [str(a) for a in (req.get("asks") or ())]
    for item in d.get("unsupported") or ():
        for word in item.get("match") or ():
            if any(str(word).lower() in a.lower() for a in asks):
                reasons.append(
                    "请求含不支持的项「%s」（%s）" % (item.get("key"), word)
                )
                break

    return (not reasons), reasons


def main() -> int:
    if "--request" in sys.argv:
        k = sys.argv.index("--request")
        req = json.loads(Path(sys.argv[k + 1]).read_text(encoding="utf-8"))
        ok, reasons = classify(req)
        print(json.dumps({"in_domain": ok, "reasons": reasons}, ensure_ascii=False,
                         indent=2))
        return 0 if ok else 1

    problems, checked = self_check()
    print("支持域校验 · 核了 %d 条 evidence" % checked)
    if problems:
        print("★ [FAIL] %d 处：" % len(problems))
        for p in problems:
            print("   -", p)
        return 1
    d = load_domain()
    print(
        "★ [PASS] 声明自洽：零件类型 %d 种 · 参数域 %d 项 · 不支持项 %d 条 · 人工审核 %d 条"
        % (
            len(d.get("part_types") or ()),
            len(d.get("limits") or ()),
            len(d.get("unsupported") or ()),
            len(d.get("manual_review") or ()),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
