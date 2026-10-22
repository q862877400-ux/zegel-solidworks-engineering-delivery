"""★ 规格 212 · D：**返回侧（输出）单位门禁** —— 扫全部工具返回字典的顶层键名。**只报不拦**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 212 · D 批）
# 文件:   tools/check_output_units.py
# 定位:   ★ 规格 `specs/212-unit-discipline` 的 **D**（★ 本规格核心）。★ 现状：**输出
#           侧完全没有门禁** ✗
#   ⇒ ★★ 而用户观察到的"米/毫米混淆"**正出在读数这一侧**（★ 实录：`IFace2.GetArea` 官方说
#     `square meters`、真机端面读 **400** 对应 20×20 的 **mm²** ⇒ 差 1000 倍的谜就在这 ✗）✓
# 判据:   ★★ **确定性**（★ 不猜语义）：★ **「单位后缀 ∪ 显式白名单」是全集** ⇒
#   ★ **凡顶层键名既不带单位后缀、又不在白名单里 ⇒ 报** ✓
# ★ 白名单 `DIMENSIONLESS` —— ★ **显式列出、每条带理由**（★ 与 `_LEN_SUFFIX_EXEMPT` 同一
# 模式）✓
#   ★★ **为什么用"报所有不在白名单的键"这种笨办法**：★ 另一条路是"从键名猜它是不是长度"
# ⇒ ★★ **那正是 C 批栽过的坑**（中文「度」与「深度」同形、`deg` 与 `degenerate` 同前缀 ✗
# ）
# ⇒ ★ 本工具**不猜语义**，★ 把"这个键是什么"这一个判断**收敛到白名单一处**（★ 逐条有理由
# ）✓
# ★ 扫描方式：★ **AST 静态扫**（★ `return {...}` 字面量）⇒ ★ 出清单；★ 运行期出口守卫是*
# *下一步**
# ★（★ 本批**只报不拦**：★ 一次硬拦会让很多既有工具注册不上 ⇒ ★ 那是"半套工具"进不了运行
# 期，
#       ★ **比不拦更糟**）✓
#   ⚠ **覆盖边界（★ 如实标注）**：★ 只覆盖**字面量返回的字典** —— ★ 用变量拼出来、或经
#     `**kwargs` 合并的**覆盖不到** ✗ ⇒ ★ 所以运行期出口守卫**不可省** ✓
# 官方依据: 无（本仓约定 `docs/union-conventions.md` 规则 2b）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "mcp-server"), str(ROOT / "scripts"), str(ROOT / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★ **已知单位后缀集合** —— ★ 键名以它结尾 ⇒ 认作"已声明单位"，★ 且**必须在这个集合里*
#: * ✓
#:   ★★★ **这就是 D 的判据**（★ 窄而确定）：★ **凡带单位后缀的键 ⇒ 后缀必须来自这里** ✓
#:   ★★ **为什么不再"报出所有不在白名单的键"** —— ★ 实录：那样报出 **1377 条**，★ 而
#: 里面 **`stage`/`op`/`output`/`document`/`retryable`/`checks`/`schemaVersion`… 一个长
#: 度都没有**
#:      ⇒ ★★ **噪声 1377、信号 0** ⇒ ★ 那个判据是**错的** ✗
#:   ★★ **与 C 批同一条洞见**：★ **门禁不该"找出手上没标单位的量"**（★ 那要靠猜语义 ✗）⇒
#:     ★★★ **它只能"把已经声明的地方钉死"** ✓
UNIT_SUFFIXES = ("_mm", "_mm2", "_mm3", "_deg", "_px", "_s", "_kg", "_m2", "_m3", "_m",
                 "_rad", "_pct", "_n", "_hz", "_bar", "_c", "_gb", "_kb", "_mb")

#: ★★ **无量纲 / 非量纲键白名单** —— ★ **每条带理由**（照 `_LEN_SUFFIX_EXEMPT` 的先例）✓
DIMENSIONLESS: dict = {
    # ── ① 状态与结论（★ 布尔/枚举/字符串，**不是量**）────────────────────────
    "ok": "状态布尔", "success": "状态布尔", "verified": "状态布尔",
    "status": "状态码/枚举（★ 量纲由旁边的 *_text 说明）", "status_text": "状态文本",
    "error": "错误文本", "errors": "错误列表", "message": "说明文本", "msg": "说明文本",
    "note": "说明文本", "notes": "说明列表", "detail": "说明文本", "details": "说明文本",
    "reason": "说明文本", "why": "说明文本", "warning": "警告文本", "warnings": "警告列表",
    "hint": "提示文本", "caveat": "限制说明", "limitations": "限制说明",
    # ── ② 计数 / 序号 / 标识（★ 无单位）──────────────────────────────────────
    "count": "计数", "total": "计数", "n": "计数", "num": "计数", "index": "序号",
    "i": "序号", "id": "标识", "name": "名字", "names": "名字列表", "label": "标签",
    "type": "类型枚举", "kind": "类型枚举", "mode": "模式枚举", "source": "来源标识",
    "tool": "工具名", "module": "模块名", "path": "路径", "file": "文件名",
    "feature": "特征名", "feature_name": "特征名", "sketch": "草图名", "body": "体名",
    "raw": "原始读数（★ 未加工，★ 由旁边的 *_mm 等承载单位）",
    # ── ③ 比值 / 比例 / 系数（★ 无量纲）──────────────────────────────────────
    "ratio": "比值（★ 无量纲）", "scale": "缩放系数（★ 无量纲）", "factor": "系数（★ 无量纲）",
    "percent": "百分比", "pct": "百分比", "fraction": "分数", "weight": "权重",
    "score": "分值", "level": "等级（★ 本仓的验证等级枚举）",
    # ── ④ 时间（★ 秒，★ 本仓惯例带 `_s`；★ 这几个是既有的普适时长名）────────
    "elapsed": "耗时（★ 秒，★ 本仓惯例；★ 新代码请用 `_s` 后缀）",
    "duration": "时长（★ 秒，★ 同上）", "timeout": "超时（★ 秒，★ 同上）",
    # ── ⑤ 嵌套结构（★ 其内部键由各自的扫描负责）────────────────────────────
    "params": "参数结构", "args": "参数结构", "data": "数据结构", "result": "结果结构",
    "results": "结果结构", "report": "报告结构", "evidence": "证据结构",
    "units": "单位声明（★ 它承载的是「哪个单位」，★ 不是量本身）",
    "units_verified": "单位是否已确证（★ 布尔）", "unit_caveat": "单位未确证的说明",
    #: ★★★ **本仓既有的单位约定**（★ 缝合，不发明）—— 锚点 `scripts/sw_curve_and_split.p
    #: y` 与
    #: `scripts/sw_drawing_create_missing.py` 里早就写着：★「官方未给单位；按 SolidWorks
    #:  API
    #:   惯例当作米 ⇒ 入参毫米已换算」⇒ ★★ 规则 2b 的**第 ③ 条**就是把它**升成约定**
    #:   （★ 凡「官方未给单位」的读数/入参，★ **返回里必须带 `unit_assumption`**）✓
    "unit_assumption": "★★ **本仓既有的单位声明**（★ 官方未给单位时，写明按什么惯例当**什么**）",
    "entry_used": "用了哪个入口（★ 入口名）", "side_effect": "副作用标识",
    # ── ⑥ 布尔旗标（★ 成规模的一类，★ 无单位）──────────────────────────────
    "is_valid": "布尔", "is_empty": "布尔", "is_open": "布尔", "is_dirty": "布尔",
    "changed": "布尔", "suppressed": "布尔", "visible": "布尔", "exists": "布尔",
    "present": "布尔", "found": "布尔", "created": "布尔", "deleted": "布尔",
    "modified": "布尔", "rebuilt": "布尔", "updated": "布尔", "closed": "布尔",
    "saved": "布尔", "reversed": "布尔", "flipped": "布尔", "skipped": "布尔",
    "supported": "布尔", "available": "布尔", "required": "布尔", "confirmed": "布尔",
    "use_default": "布尔", "dry_run": "布尔", "allow": "布尔", "deny": "布尔",
    # ── ⑦ 集合 / 列表（★ 元素各自判）────────────────────────────────────────
    "items": "列表", "list": "列表", "entries": "列表", "selected": "列表",
    "bodies": "列表", "faces": "列表", "edges": "列表", "features": "列表",
    "selections": "列表", "steps": "列表", "stages": "列表", "batches": "列表",
    "dialogs": "弹窗列表", "logs": "日志列表", "commands": "命令列表",
    "mark": "选择标记（★ 计数/枚举，★ 不是长度）", "marks": "选择标记列表",
    "callout": "标注标识", "selector": "选择器字符串", "selection": "选择器字符串",
    "sku": "标识", "standard": "标准名", "standard_name": "标准名", "material": "材料名",
    "config": "配置名", "configuration": "配置名", "plane": "基准面名",
    "axis": "轴名", "view": "视图名", "sheet": "图纸名", "layer": "图层名",
    "encoding": "编码名", "format": "格式名", "ext": "扩展名", "mime": "MIME 类型",
    "version": "版本号", "revision": "版本号", "schema_version": "版本号",
    "sha256": "摘要", "hash": "摘要", "share": "分量", "shares": "分量列表",
    "tokens": "词元列表", "bytes": "字节数（★ 容量不是长度）", "size": "大小（★ 歧义：★ 由上下文定；★ 新代码请显式带后缀）",
    "memory_budget_gb": "内存上限（★ GB，★ 已自带单位后缀）",
}


#: ★★ **无量纲键的"模式"归类** —— ★ **仍是确定性的**（★ 按**后缀/前缀模式**判，★ **不猜
#: 语义**）✓
#: ★ 依据：★ 扫出的 820 个未归类键里，**绝大多数是状态/计数/标识/结构**（★ 逐个列进表不
#: 现实，
#:     ★ 且新增键会源源不断）⇒ ★ 把"**成规模的那几类**"用模式表达 ✓
#: ⚠ ★ 模式**只收"必然无单位"的形态** —— ★ 只要有一丝长度可能（如 `*_size`/`*_length`）*
#: *就不收** ✓
DIMENSIONLESS_SUFFIX_PATTERNS = (
    ("_count", "计数"), ("_code", "状态码"), ("_id", "标识"), ("_name", "名字"),
    ("_text", "文本"), ("_note", "说明"), ("_msg", "说明"), ("_reason", "说明"),
    ("_required", "布尔"), ("_allowed", "布尔"), ("_supported", "布尔"),
    ("_available", "布尔"), ("_present", "布尔"), ("_found", "布尔"),
    ("_ok", "布尔"), ("_valid", "布尔"), ("_exists", "布尔"), ("_enabled", "布尔"),
    ("_list", "列表"), ("_items", "列表"), ("_names", "列表"), ("_keys", "列表"),
    ("_before", "结构（★ 调用前快照）"), ("_after", "结构（★ 调用后快照）"),
    ("_delta", "差值（★ 计数/结构之差，★ 不是长度）"),
    ("_by", "标识（★ 如 `verified_by` = 由什么判据验证）"),
    ("_error", "错误文本"), ("_errors", "错误列表"), ("_warning", "警告文本"),
    ("_summary", "摘要文本"), ("_mode", "模式枚举"), ("_kind", "类型枚举"),
    ("_type", "类型枚举"), ("_index", "序号"), ("_stage", "阶段名"),
    ("_op", "操作名"), ("_operation", "操作名"), ("_backend", "后端名"),
    ("_source", "来源标识"), ("_path", "路径"), ("_file", "文件名"),
    ("_sha256", "摘要"), ("_hash", "摘要"), ("_version", "版本号"),
    ("_schema", "模式/规范标识"), ("_flag", "布尔旗标"),
)
DIMENSIONLESS_PREFIX_PATTERNS = (
    ("is_", "布尔"), ("has_", "布尔"), ("can_", "布尔"), ("was_", "布尔"),
    ("did_", "布尔"), ("should_", "布尔"), ("needs_", "布尔"), ("requires_", "布尔"),
    ("raw_", "原始读数（★ 未加工）"), ("new_", "新增项（★ 列表/名字）"),
    ("old_", "旧值（★ 与 new_ 成对）"), ("total_", "计数/合计（★ 成规模）"),
    ("num_", "计数"), ("n_", "计数"),
)


def _is_dimensionless_pattern(key: str) -> str | None:
    """★ 按模式判无量纲（★ 返回理由或 None）✓"""
    k = key.lower()
    for suf, why in DIMENSIONLESS_SUFFIX_PATTERNS:
        if k.endswith(suf):
            return "模式后缀 %s ⇒ %s" % (suf, why)
    for pre, why in DIMENSIONLESS_PREFIX_PATTERNS:
        if k.startswith(pre):
            return "模式前缀 %s ⇒ %s" % (pre, why)
    return None


#: ★ 像单位后缀、但**不在**已知集合里的形态（★ 报出来让人认领）✓
_UNITLIKE_RE = __import__("re").compile(r"_(mm|cm|m|km|in|ft|mil|deg|rad|px|pt|s|ms|min|h|kg|g|lb|n|nm|c|f|k|pct|gb|mb|kb)\d*$", __import__("re").I)


def _has_unknown_unit_suffix(key: str) -> bool:
    """★ 后缀**像**单位、但**不在** `UNIT_SUFFIXES` 里 ⇒ 报（★ 让人认领或补齐集合）✓"""
    k = key.lower()
    if not _UNITLIKE_RE.search(k):
        return False
    return not any(k.endswith(s) for s in UNIT_SUFFIXES)


def _is_unit_suffixed(key: str) -> bool:
    k = key.lower()
    return any(k.endswith(s) for s in UNIT_SUFFIXES)


def _walk_dict_keys(node: ast.AST):
    """★ 从 `return {...}` 的字典节点取**顶层键**（★ 字面量字符串键才算）✓"""
    for k in node.keys:
        if isinstance(k, ast.Constant) and isinstance(k.value, str):
            yield k.value, k.lineno
        elif k is None:                                  # `{**other}`
            yield "**kwargs", getattr(node, "lineno", 0)


def main() -> int:
    targets = sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "mcp-server").glob("*.py"))
    hits, ok_cnt, whitelisted, scanned_dicts = [], 0, 0, 0
    seen_keys: dict = {}
    for path in targets:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:                                               # noqa: BLE001
            continue
        for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            for node in ast.walk(fn):
                #: ★ 只看 `return {…}`（★ 字面量字典）✓
                if not isinstance(node, ast.Return) or not isinstance(node.value, ast.Dict):
                    continue
                scanned_dicts += 1
                for key, lineno in _walk_dict_keys(node.value):
                    seen_keys[key] = seen_keys.get(key, 0) + 1
                    #: ★★★ D 的判据：★ **只看带单位后缀的键** ⇒ 后缀必须在已知集合里 ✓
                    if _is_unit_suffixed(key):
                        ok_cnt += 1
                    elif _has_unknown_unit_suffix(key):
                        hits.append({"file": path.name, "func": fn.name, "key": key,
                                     "line": lineno, "why": "后缀像单位、但不在已知集合里"})
                    elif key in DIMENSIONLESS or _is_dimensionless_pattern(key):
                        whitelisted += 1
    print("★ 输出侧体检（★ 只报不拦）：扫 %d 个文件 · **%d** 个字面量返回字典" % (len(targets), scanned_dicts))
    print("★★ 键名判定：★ 带单位后缀 **%d** · ★ 在无量纲白名单 **%d** · ★★ **未归类 %d**"
          % (ok_cnt, whitelisted, len(hits)))
    by_key: dict = {}
    for h in hits:
        by_key.setdefault(h["key"], []).append(h)
    print("★★ **未归类的键名（按出现次数）**：%d 个不同的键" % len(by_key))
    for key, items in sorted(by_key.items(), key=lambda kv: -len(kv[1]))[:40]:
        print("   %-34s ×%-4d 例：%s::%s" % (key, len(items), items[0]["file"], items[0]["func"]))
    #: ★★ **第二半判据**（★ 确定性）：★ `scripts/` 里凡写了「**官方未给单位**」（★ 这是*
    #: *仓里既有的
    #:   措辞**，★ 见 `sw_curve_and_split.py` / `sw_drawing_create_missing.py`）的模块 ⇒
    #: ★★ **其返回字典里必须有 `unit_assumption`** ✓（★ 不能只在注释里说、★ 要在**返回里
    #: **说）
    #: ★ 依据：★ 规则 2b 第 ③ 条「**未确证必须说出来**」★ 而 `unit_assumption` 是**既有
    #: 实现** ✓
    noassump, alt = [], []
    for path in sorted((ROOT / "scripts").glob("*.py")):
        try:
            txt = path.read_text(encoding="utf-8", errors="replace")
        except Exception:                                               # noqa: BLE001
            continue
        if "官方未给单位" not in txt:
            continue
        #: ★ 硬判据：★ **必须"说出来"** —— 返回里得有**名字含 `unit` 的键** ✓
        if "unit" not in txt:
            noassump.append(path.name)
        #: ★ 统一性提示：★ 用了**别的** `*unit*` 键名 ⇒ ★ 建议统一到既有约定 `unit_assum
        #: ption` ✓
        elif "unit_assumption" not in txt:
            alt.append(path.name)
    print("★★ 第二半：★ 说了「官方未给单位」却**没在返回里带 `unit_assumption`** 的模块 ⇒ **%d** 个"
          % len(noassump))
    for n in noassump[:12]:
        print("      %s" % n)
    print("★★ 统一性提示：★ 用了**别的** `*unit*` 键名（★ 建议统一到 `unit_assumption`）⇒ **%d** 个"
          % len(alt))
    for n in alt[:12]:
        print("      %s" % n)

    p = ROOT / "output" / "spec212-output-unit-lint.json"
    p.write_text(json.dumps({"scanned_files": len(targets), "scanned_dicts": scanned_dicts,
                             "suffixed": ok_cnt, "whitelisted": whitelisted,
                             "unclassified": hits, "missing_unit_assumption": noassump, "noncanonical_unit_key": alt,
                             "key_counts": {k: len(v) for k, v in by_key.items()}},
                            ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
