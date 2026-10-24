"""B 维度观测器：读全部 ToolSpec 声明，输出可复核读数（只读）。

用途：`docs/state/facts/B-tools.md` 里每条读数的复现入口。
纪律：只读；不启动 MCP 服务、不连 SolidWorks、不改仓库文件（只写自己的 JSON 输出）。

跑法：
    python docs\\state\\probes\\probe_all_specs.py
    python docs\\state\\probes\\probe_all_specs.py --json docs/state/inventory-b.json
"""
from __future__ import annotations

import argparse
import collections
import dataclasses
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "mcp-server"))
sys.path.insert(0, str(ROOT / "scripts"))

import register_capabilities as rc  # noqa: E402

NAME_OK = re.compile(r"^solidworks_[a-z][a-z0-9_]*$")
SUSPECT_UNIT = re.compile(
    r"(depth|width|height|length|radius|diameter|thickness|gap|offset|clearance|angle)$",
    re.I,
)


def collect() -> dict:
    specs = rc.all_specs()
    data: dict = {"total_specs": len(specs)}
    data["tool_spec_fields"] = [f.name for f in dataclasses.fields(specs[0])]

    # 命名
    data["name_rule_violations"] = [s.name for s in specs if not NAME_OK.match(s.name)]
    data["name_segment_histogram"] = dict(
        sorted(collections.Counter(len(s.name.split("_")) for s in specs).items())
    )
    data["name_two_segment"] = [s.name for s in specs if len(s.name.split("_")) == 2]

    # 参数与单位
    params = [(s.name, p) for s in specs for p in getattr(s, "params", [])]
    data["param_total"] = len(params)
    data["param_mm"] = sum(1 for _, p in params if p.name.endswith("_mm"))
    data["param_deg"] = sum(1 for _, p in params if p.name.endswith("_deg"))
    data["param_suspect_no_unit"] = [
        {"tool": t, "param": p.name}
        for t, p in params
        if SUSPECT_UNIT.search(p.name) and not p.name.endswith(("_mm", "_deg"))
    ]

    # inject
    data["inject_histogram"] = dict(
        collections.Counter(getattr(s, "inject", "") or "" for s in specs).most_common()
    )

    # doc
    docs = [(s.name, (getattr(s, "doc", "") or "").strip()) for s in specs]
    lens = sorted(len(d) for _, d in docs)
    data["doc_empty"] = [n for n, d in docs if not d]
    data["doc_length"] = {
        "min": lens[0],
        "median": lens[len(lens) // 2],
        "max": lens[-1],
    }
    data["doc_first_char_top5"] = collections.Counter(
        d[0] if d else "<空>" for _, d in docs
    ).most_common(5)

    # title / read_only / writes
    titles = collections.Counter(s.title for s in specs)
    data["title_empty"] = sum(1 for s in specs if not s.title)
    data["title_duplicates"] = {t: c for t, c in titles.items() if c > 1}
    data["read_only_histogram"] = dict(
        collections.Counter(str(getattr(s, "read_only", None)) for s in specs)
    )
    data["writes_declared"] = sum(1 for s in specs if getattr(s, "writes", None))

    # 重名 + 一实现多名
    names = collections.Counter(s.name for s in specs)
    data["duplicate_tool_names"] = {k: v for k, v in names.items() if v > 1}
    pairs: dict[str, list[str]] = collections.defaultdict(list)
    for s in specs:
        if s.module and s.function:
            pairs[f"{s.module}.{s.function}"].append(s.name)
    data["impl_with_multiple_names"] = {
        k: v for k, v in pairs.items() if len(v) > 1
    }
    data["distinct_impls"] = len(pairs)

    # 注册前门禁
    try:
        from tool_registry import check_specs  # noqa: PLC0415

        data["check_specs_problems"] = list(check_specs(specs))
    except Exception as exc:  # noqa: BLE001
        data["check_specs_problems"] = [f"<调用失败> {type(exc).__name__}: {exc}"]

    return data


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="", help="把结果写到这个路径")
    args = ap.parse_args()

    data = collect()
    print(f"声明总数            : {data['total_specs']}")
    print(f"命名违规            : {len(data['name_rule_violations'])}")
    print(f"2 段名              : {len(data['name_two_segment'])} {data['name_two_segment']}")
    print(f"参数 / _mm / _deg   : {data['param_total']} / {data['param_mm']} / {data['param_deg']}")
    print(f"疑似缺单位          : {len(data['param_suspect_no_unit'])}")
    print(f"inject 取值种类     : {len(data['inject_histogram'])}")
    print(f"doc 空 / 中位       : {len(data['doc_empty'])} / {data['doc_length']['median']}")
    print(f"title 重复          : {len(data['title_duplicates'])}")
    print(f"read_only           : {data['read_only_histogram']}")
    print(f"writes 覆盖         : {data['writes_declared']}/{data['total_specs']}")
    print(f"同名重复            : {data['duplicate_tool_names']}")
    print(f"一实现多名          : {len(data['impl_with_multiple_names'])}/{data['distinct_impls']}")
    print("check_specs 返回    :")
    for p in data["check_specs_problems"]:
        print("  -", p)

    if args.json:
        out = (ROOT / args.json) if not pathlib.Path(args.json).is_absolute() else pathlib.Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("已写出:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())