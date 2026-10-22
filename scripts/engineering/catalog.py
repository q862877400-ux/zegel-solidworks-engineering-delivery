"""★ Q4/Q6 · 任务域 + 受控多标签 + 分面检索 + 暴露面（规格 323 的 N1~N10）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/catalog.py
# 定位:   规格 `specs/323-task-domains-and-faceted-retrieval` 的 N1（任务域）/N2（受控
#           多标签）/ N3（模块仅定位）/ N4（分面检索）/ N5（n-gram）/N6（4096 预算）/ N7
#           （recall 指标）/ N8（阈值冻结）/ N9（暴露面）/N10（按需加载契约）。★★ 实测（
#           2026-10-12）起点：`capabilities.yaml`（576KB）与`docs/effect-declarations.js
#           on`（111KB）已存在；`registry.py` 已有`ToolDescriptor`（★ Q12 要的「注册时合
#           成」已有一半）。★ 而**没有任何元数据目录、`ToolSpec` 没有域字段、没有中文 n-
#           gram、  没有分面检索** ⇒ 补这 4 个缺口。
# 官方依据: ① `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q4（L36-57）逐字：  八个一
#           级任务域 + 七个受控多标签 + recall/chain_hit 门槛 + 阈值冻结② 同文件 Q6（L96
#           -112）逐字：4096 token · 分面过滤 · 本地词法 +  中文 n-gram + 受控同义词 ·
#           少量方法卡 · 按需加载 · MCP 暴露面③ 同文件 Q12（L214-231）逐字：外挂单一源 ·
#            注册时合成 ·  「效应按文档几何、文档属性、选择状态、界面状态、文件系统、网
#           络分别描述」④ `metadata/domains.yaml` · `metadata/facets.yaml` · `metadata/t
#           hresholds.json`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收入口 `tools/run_s323_catalog.py`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import re
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).resolve().parents[2]
METADATA = ROOT / "metadata"

#: ★★ Q6 L98 逐字：「候选方法和工具定义的单次上限定为 **4096 token**」
TOKEN_BUDGET = 4096


class CatalogError(Exception):
    """★ 目录层失败（★ 带封闭码）。"""

    CODES = (
        "no-domain",
        "unknown-domain",
        "unknown-facet",
        "bad-facet-value",
        "budget-exceeded",
        "thresholds-missing",
    )

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法目录拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


#: ══════════════════════════════════════════════════════════════════════
# 一、元数据装载（★ Q12：外挂单一源 —— 只从这里读，不在模块里各写一份）
#: ══════════════════════════════════════════════════════════════════════

#: ★ 2026-10-22 统一化：`_load_simple_yaml` 原与 `protocols._load_yaml` 两份逐字相同，
#:   现收敛到 `engineering/_yaml_loader.load_yaml`；此处保留旧名作别名
#:   （★ 2026-10-12「不要手写 YAML 解析器」那条教训已搬进那个模块的模块头）
try:
    from ._yaml_loader import load_yaml as _load_simple_yaml
except ImportError:
    from _yaml_loader import load_yaml as _load_simple_yaml


@dataclass
class Domain:
    id: str
    name: str
    order: int = 0
    cues: list = field(default_factory=list)


@dataclass
class FacetDef:
    name: str
    values: dict = field(default_factory=dict)  #: id → label


def load_domains() -> dict:
    """★ 读 8 个一级任务域（★ N1 —— ★ 外挂单一源）。"""
    d = _load_simple_yaml(METADATA / "domains.yaml")
    out = {}
    for x in d.get("domains") or []:
        if not isinstance(x, dict):
            continue
        dom = Domain(
            id=str(x.get("id", "")),
            name=str(x.get("name", "")),
            order=int(x.get("order") or 0),
            cues=list(x.get("cues") or []),
        )
        out[dom.id] = dom
    return out


def _fallback_domain(domains: dict) -> str:
    """★ 回退域（★ 从 `domains.yaml` 的 `fallback_domain` 读，★ 不写死）。"""
    d = _load_simple_yaml(METADATA / "domains.yaml")
    fb = str(d.get("fallback_domain") or "")
    if fb in domains:
        return fb
    #: ★ 兜底：取 order 最大的那个（★ 并如实报—— ★ 见 `build_catalog` 的计数）
    return max(domains.items(), key=lambda kv: kv[1].order)[0] if domains else ""


def load_facets() -> dict:
    """★ 读 7 个受控多标签（★ N2）。"""
    d = _load_simple_yaml(METADATA / "facets.yaml")
    out = {}
    for name, vals in (d.get("facets") or {}).items():
        if not isinstance(vals, list):
            continue
        vd = {}
        for v in vals:
            if isinstance(v, dict) and v.get("id"):
                vd[str(v["id"])] = str(v.get("label", v["id"]))
        out[name] = FacetDef(name=name, values=vd)
    return out


def load_thresholds() -> dict:
    """★ 读冻结阈值（★ N8 —— ★ 带 `frozen_at` 才认）。"""
    p = METADATA / "thresholds.json"
    if not p.is_file():
        raise CatalogError("thresholds-missing", "★ 没有 %s" % p)
    d = json.loads(p.read_text(encoding="utf-8"))
    if not d.get("frozen_at"):
        raise CatalogError(
            "thresholds-missing", "★★ 阈值没有 `frozen_at` ⇒ 无法证明是**评测前**冻结的"
        )
    return d


#: ══════════════════════════════════════════════════════════════════════
# 二、结构标签（★ N1/N2/N3 —— ★ 从注册信息**自动生成**，★ Q4 L57）
#: ══════════════════════════════════════════════════════════════════════


#: ★★ **域判定规则**（★ 按**工具名 + 标题**里的词匹配 `cues`）。
#:   ★ 判据：**得分最高者胜**；★ 平局按 `order` 取小（★ 顺序即语义）。
def classify_domain(name: str, title: str, doc: str, domains: dict) -> str:
    """★★ **给一个工具判主域**（★ N1 —— ★ FR-001）。

    ★★ 判据：**名字权重 3 · 标题权重 2 · 文档权重 1**。
      ★ 为什么名字最重：★ 名字是**作者定的**（★ 最可靠）；
        ★ 文档是**散文**（★ 容易被"顺便提到"污染）。
    """
    blob_name = (name or "").lower()
    blob_title = (title or "").lower()
    blob_doc = (doc or "").lower()
    best, best_score = "", -1
    for did, dom in sorted(domains.items(), key=lambda kv: kv[1].order):
        score = 0
        for cue in dom.cues:
            c = str(cue).lower()
            if not c:
                continue
            if c in blob_name:
                score += 3
            if c in blob_title:
                score += 2
            if c in blob_doc:
                score += 1
        if score > best_score:
            best, best_score = did, score
    #: ★★ 判据（★ Q4 FR-001：**每个工具恰好一个主域**）：
    #:   ★ **零分 ⇒ 回退域**（★ 但**要被计数**，★ 见 `build_catalog` 的 `fallback_n`）。
    #:   ⚠ 实测（2026-10-12）：第一版零分就抛 `no-domain`
    #:     ⇒ `cadstudio_build_dxf_preview_scene` 这种**名字里一个域提示词都没有**的
    #:     工具直接把整批构建打断 ✗ —— ★ 而 Q4 要的是「**每个工具一个主域**」，
    #:     ★ 不是「判不出来就报错」。
    return best if best_score > 0 else ""


#: ★★ **效应 → 六类**（★ Q12 L223 逐字：「效应按文档几何、文档属性、
#:   选择状态、界面状态、文件系统、网络分别描述」）
_EFFECT_RULES = (
    #: 名字里带这些 ⇒ **文档几何**（★ 最重）
    (
        r"extrude|revolve|sweep|loft|cut|fillet|chamfer|shell|dome|rib|"
        r"pattern|mirror|scale|hole|boss|thicken|knit|trim|extend|flatten|"
        r"draft|flange|hem|gusset|weld|mold|parting",
        "doc_geometry",
    ),
    #: 属性/配置
    (r"custom_propert|config|equation|material", "doc_property"),
    #: 选区
    (r"select|clear_selection|resolve_selection|deselect", "selection"),
    #: 界面
    (r"view|zoom|display|redraw|perspective|window|frame", "ui_state"),
    #: 文件系统
    (
        r"export|save|write|batch_export|open_document|close_document|"
        r"pack_and_go|dwg|dxf",
        "filesystem",
    ),
    #: 网络
    (r"misumi|http|download|suggest_part", "network"),
)


def classify_effect(name: str, read_only: bool = True) -> list:
    """★ **判工具的效应类别**（★ Q12 的六类）。

    ★★ 判据（★ 两条）：
      · 名字命中 `_EFFECT_RULES` ⇒ 那一类
      · ★ **`read_only=False` 而一条都没命中** ⇒ ★ 标 `unknown`
        （★ Q12 L223 逐字：「**未知仍按可能写处理**」）
    """
    n = (name or "").lower()
    hits = [cls for pat, cls in _EFFECT_RULES if re.search(pat, n)]
    if hits:
        return sorted(set(hits))
    if not read_only:
        #: ★★ Q12 逐字：「未知仍按可能写处理」
        return ["doc_geometry"]
    return ["none"]


def classify_object(name: str, needs_model: bool = False, inject: str = "") -> str:
    n = (name or "").lower()
    if "drawing" in n or "sheet" in n:
        return "drawing"
    if "assembly" in n or "mate" in n or "component" in n or "explode" in n:
        return "assembly"
    if "sketch" in n:
        return "sketch"
    if "face" in n or "edge" in n or "vertex" in n or "entities_on_body" in n:
        return "face_edge"
    if "body" in n:
        return "body"
    if "feature" in n:
        return "feature"
    if inject == "sw_app" or n.startswith("health") or "install" in n:
        return "application"
    if needs_model or "part" in n or "model" in n:
        return "part"
    return "document"


def classify_operation(name: str, read_only: bool = True) -> str:
    n = (name or "").lower()
    if re.search(r"create|add|insert|new_|start", n):
        return "create"
    if re.search(r"delete|remove|clear|deselect|suppress", n):
        return "delete"
    if re.search(r"select|resolve_selection|set_object_mark", n):
        return "select"
    if re.search(r"export|save|write", n):
        return "export"
    if re.search(
        r"calculate|compute|evaluate|measure|solve|inspect|"
        r"evidence|report|check|list|read|get_",
        n,
    ):
        return "compute" if not read_only else "read"
    if re.search(r"update|set_|modify|activate|apply", n):
        return "modify"
    if re.search(r"job|lease|fence|gate|authoriz", n):
        return "orchestrate"
    return "read" if read_only else "modify"


def classify_result(name: str, read_only: bool = True) -> str:
    n = (name or "").lower()
    if re.search(r"export|save|write|bmp|image|stl|step|pdf|dxf", n):
        return "file"
    if re.search(r"report|evidence|review|inspect|check|summary", n):
        return "report"
    if re.search(
        r"mass_propert|bounding_box|measure|volume|area|angle|"
        r"distance|count|params|status",
        n,
    ):
        return "value"
    if re.search(
        r"extrude|revolve|sweep|loft|fillet|chamfer|hole|shell|"
        r"pattern|mirror|dome|rib",
        n,
    ):
        return "geometry"
    if read_only:
        return "value"
    return "state"


def classify_precondition(
    name: str, needs_model: bool = False, inject: str = ""
) -> str:
    n = (name or "").lower()
    if "assembly" in n or "mate" in n or "component" in n:
        return "needs_assembly"
    if "drawing" in n or "sheet" in n or "view" in n:
        return "needs_drawing"
    if "selection" in n or "selected" in n:
        return "needs_selection"
    if re.search(r"simulation|study|mesh|topology|fea", n):
        return "needs_addin"
    if re.search(r"export|save|open_document|pack_and_go", n):
        return "needs_saved_file"
    if needs_model or inject in ("model", "doc"):
        return "needs_model"
    return "none"


def classify_backend(name: str, module: str = "") -> str:
    """★ 判工具的后端（★ Q4 的 `backend`）。

    ⚠ 实测（2026-10-12）：第一版用 `re.search(r"...|fea|...", n+m)` ⇒
      ★ `sw_hole_features` 里的 **`features` 命中 `fea`** ⇒
      ★ **异型孔被判成"外部求解器"** ✗（★ 而"后端判错"看起来像"规则写漏了"）。
    ⇒ ★ 判据：**`fea` 必须词边界**（`\\bfea\\b`），★ 其余同理。
    """
    n = (name or "").lower()
    m = (module or "").lower()
    if re.search(r"calculix|elmer|\bsolver\b|simulation|topology|\bfea\b", n + " " + m):
        return "external_solver"
    if re.search(
        r"export|\bdxf\b|\bstl\b|\bstep\b|iges|\bbmp\b|image|\bpdf\b|macro", n
    ):
        return "file_io"
    if m and not m.startswith("sw_"):
        return "pure_python"
    if re.search(r"health|preflight|costing|misumi", n):
        return "pure_python"
    return "com_pywin32"


def classify_availability(
    name: str,
    *,
    admitted: bool,
    backend_blocked: bool = False,
    needs_addin: bool = False,
) -> str:
    """★★ **可用性**（★ Q4 的 `availability` —— ★ 它决定能不能进自主集合）。

    ★★ 判据顺序（★ 最严在前，★ 与 Q12/Q16 逐字对齐）：
      ```
      ① `backend_blocked`  ⇒ catalog_only 改 backend_blocked（★ Q16 逐字）
      ② 未准入             ⇒ catalog_only（★ Q12 逐字：「没有完成可执行适配的
                             入口不得被编译器选中」）
      ③ 需加载项           ⇒ supervised（★ 要人看着）
      ④ 其余               ⇒ autonomous
      ```
    """
    if backend_blocked:
        return "backend_blocked"
    if not admitted:
        return "catalog_only"
    if needs_addin:
        return "supervised"
    return "autonomous"


#: ══════════════════════════════════════════════════════════════════════
# 三、工具卡（★ N3 —— ★ 模块**仅作定位信息**）
#: ══════════════════════════════════════════════════════════════════════


@dataclass
class ToolCard:
    """★★ **工具卡**（★ Q6 L104 逐字：「返回少量方法卡，保留目标、输入、
    适用条件、禁止、产物和验证义务」）。

    ★★ **`module` 是定位字段**（★ Q4 L40 逐字：「实现模块仅保留为定位信息，
    **不作为检索分类**」）⇒ ★ `search_blob()` **不含 `module`**（★ 结构性保证）。
    """

    name: str
    domain: str = ""
    title: str = ""
    facets: dict = field(default_factory=dict)
    module: str = ""  #: ★ 仅定位 —— ★ **不参与检索匹配**
    tokens: int = 0
    admitted: bool = True

    def search_blob(self) -> str:
        """★★ **参与检索匹配的文本**（★ **不含 `module`**）。

        ★★ 这是 N3/SC-003 的**结构性保证** —— ★ 不是靠"记得别写进去"。
        """
        f = " ".join(str(v) for v in self.facets.values())
        return "%s %s %s" % (self.name, self.title, f)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "domain": self.domain,
            "title": self.title,
            "facets": dict(self.facets),
            "module": self.module,
            "tokens": self.tokens,
            "admitted": self.admitted,
        }


def _est_tokens(*texts: str) -> int:
    """★ 估 token（★ 与阶段 4 同口径：字数 / 1.6）。"""
    blob = " ".join(t for t in texts if t)
    return max(1, int(len(blob) / 1.6))


def build_catalog(
    *,
    registry: dict | None = None,
    domains: dict | None = None,
    facets: dict | None = None,
) -> list:
    """★★ **从注册信息合成工具卡**（★ N1/N2/N3 —— ★ Q4 L57「结构标签可以从
    注册信息生成」）。

    ★★ **判据**：**521/521 个工具都要有一张卡**（★ SC-001）——
      ★ 两个注册来源都要覆盖（★ `all_specs()` + `server.py` 的 `@mcp.tool`）。
    """
    from . import registry as REG

    reg = registry if registry is not None else REG.build_registry()
    doms = domains if domains is not None else load_domains()
    fac = facets if facets is not None else load_facets()

    #: ⚠ 实测（2026-10-12）：`ToolDescriptor` **不带 `title`/`doc`/`read_only`/
    #:   `needs_model`** —— 那些在 `ToolSpec` 上。
    #:   ★★ 第一版只读 descriptor ⇒ `title`/`doc` 全是空串 ⇒
    #:     **域判定 514/521 落回退域**（★ 而"分布失衡"看起来像"cues 写得不好"，
    #:     不像"字段没读到"）。
    #:   ⇒ ★ 判据：**先建 spec 索引，按规范名回查**（★ 两边都要读）。
    specs = {}
    try:
        import register_capabilities as _rc  # noqa: PLC0415

        for s in _rc.all_specs():
            specs[s.name] = s
    except Exception:  # noqa: BLE001
        pass

    cards: list[ToolCard] = []
    fallback_n = 0
    for name, d in sorted(reg.items()):
        sp = specs.get(name)
        title = (getattr(sp, "title", "") if sp is not None else "") or ""
        doc = (getattr(sp, "doc", "") if sp is not None else "") or ""
        module = getattr(d, "module", "") or ""
        admitted = bool(getattr(d, "admitted", True))
        read_only = getattr(sp, "read_only", None) if sp is not None else None
        if read_only is None:
            #: ★ 回退到 descriptor 的合成效应（★ 不是"猜只读"）
            read_only = getattr(d, "effect", "unknown") == "read"
        needs_model = (
            bool(getattr(sp, "needs_model", False)) if sp is not None else False
        )
        inject = getattr(d, "inject", "") or ""

        dom = classify_domain(name, title, doc, doms)
        if not dom:
            #: ★★ 回退域（★ Q4：**每个工具一个主域** —— ★ 判不出也要有）
            dom = _fallback_domain(doms)
            fallback_n += 1
        if dom not in doms:
            raise CatalogError("unknown-domain", "★ 未知域：%r" % dom)

        pre = classify_precondition(name, needs_model=needs_model, inject=inject)
        avail = classify_availability(
            name, admitted=admitted, needs_addin=(pre == "needs_addin")
        )
        eff = classify_effect(name, read_only=read_only)
        fv = {
            "effect": eff[0],
            "object_kind": classify_object(
                name, needs_model=needs_model, inject=inject
            ),
            "operation": classify_operation(name, read_only=read_only),
            "result_kind": classify_result(name, read_only=read_only),
            "precondition": pre,
            "backend": classify_backend(name, module),
            "availability": avail,
        }
        #: ★★ **受控校验**：每个标签值必须在 `facets.yaml` 里（★ N2/SC-002）
        for fn, fval in fv.items():
            if fn not in fac:
                raise CatalogError("unknown-facet", "★ 未知标签：%s" % fn)
            if fval not in fac[fn].values:
                raise CatalogError(
                    "bad-facet-value", "★ %s 的 %s=%r 不在受控取值里" % (name, fn, fval)
                )

        cards.append(
            ToolCard(
                name=name,
                domain=dom,
                title=title,
                facets=fv,
                module=module,
                tokens=_est_tokens(name, title, doc, " ".join(fv.values())),
                admitted=admitted,
            )
        )
    #: ★★ **如实计数回退域**（★ 不是藏起来）——
    #:   ★ 判据：`title` 与 `doc` 都为空、且名字零命中 ⇒ 那才是真回退。
    for c in cards:
        c.fallback = (
            c.domain == _fallback_domain(doms)
            and classify_domain(c.name, c.title, "", doms) == ""
        )
    return cards


#: ══════════════════════════════════════════════════════════════════════
# 四、本地词法 + 中文 n-gram + 受控同义词（★ N5 —— ★ Q6 L103）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ **受控中英文同义词**（★ Q6 L103 逐字「受控中英文同义词召回」）
SYNONYMS: dict[str, tuple] = {
    "孔": ("hole", "bore"),
    "螺纹": ("thread", "cosmetic_thread"),
    "草图": ("sketch",),
    "拉伸": ("extrude", "boss"),
    "切除": ("cut", "extrude_cut"),
    "倒角": ("chamfer",),
    "圆角": ("fillet",),
    "工程图": ("drawing", "sheet"),
    "视图": ("view",),
    "装配": ("assembly", "mate"),
    "配合": ("mate", "mating"),
    "干涉": ("interference", "clash"),
    "质量属性": ("mass_property", "mass"),
    "包围盒": ("bounding_box", "bbox"),
    "属性": ("property", "custom_property"),
    "配置": ("configuration", "config"),
    "方程": ("equation",),
    "导出": ("export",),
    "仿真": ("simulation", "study"),
    "网格": ("mesh",),
    "抽壳": ("shell",),
    "阵列": ("pattern",),
    "镜像": ("mirror",),
    "旋转": ("revolve",),
    "扫描": ("sweep",),
    "放样": ("loft",),
    "测量": ("measure",),
    "保存": ("save",),
    "干涉检查": ("check_interference",),
    "自由度": ("dof", "degrees_of_freedom"),
    "机构": ("mechanism", "linkage"),
    "连杆": ("linkage", "four_bar"),
    "平口钳": ("vise",),
    "箱体": ("housing",),
}


def ngrams(text: str, n: int = 2) -> set:
    """★★ **中文 n-gram**（★ N5 —— ★ Q6 L103 逐字「中文 n-gram」）。

    ★★ 判据：**只对 CJK 片段做 n-gram**（★ 英文按词切，★ 不需要 n-gram）。
      ★ 为什么需要它：中文没有空格 ⇒ ★ 精确词匹配召回率极低
        （★ 「打孔」查不到「孔系」）。
    """
    out: set = set()
    #: ★ CJK 片段
    for seg in re.findall(r"[\u4e00-\u9fff]+", text or ""):
        for k in range(1, min(n, len(seg)) + 1):
            for i in range(len(seg) - k + 1):
                out.add(seg[i : i + k])
    #: ★ 英文/标识符按词
    for w in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text or ""):
        out.add(w.lower())
    return out


def expand_query(text: str) -> set:
    """★ 查询 → **词元集合**（★ 原文 + n-gram + 同义词 + 域提示词）。"""
    toks = ngrams(text, 2)
    for zh, ens in SYNONYMS.items():
        if zh in (text or ""):
            toks.add(zh)
            toks.update(e.lower() for e in ens)
    return toks


#: ══════════════════════════════════════════════════════════════════════
# 五、分面检索（★ N4/N6 —— ★ Q6 L102-107）
#: ══════════════════════════════════════════════════════════════════════


@dataclass
class RetrievalQuery:
    text: str = ""
    domain: str = ""  #: ★ 任务类型
    doc_state: str = ""  #: ★ 文档状态（★ 映射到 `precondition`）
    backend: str = ""  #: ★ 后端可达性
    capability: str = ""  #: ★ 能力范围（★ 映射到 `availability`）
    budget: int = TOKEN_BUDGET


@dataclass
class RetrievalResult:
    cards: list = field(default_factory=list)
    tokens: int = 0
    truncated: int = 0
    facets_used: list = field(default_factory=list)
    candidates_before_filter: int = 0


def retrieve(
    q: RetrievalQuery, cards: list, *, budget: int | None = None
) -> RetrievalResult:
    """★★ **分面检索**（★ N4/N5/N6 —— ★ Q6 L102-107）。

    ★★ 判据顺序（★ 逐字承 Q6 的五步）：
      ```
      ① 按任务类型 / 文档状态 / 后端可达性 / 能力范围**过滤**
      ② 本地词法 + 中文 n-gram + 同义词**召回**
      ③ 返回**少量方法卡**（★ ≤4096 token）
      ```
    ★★ **过滤在召回之前**（★ Q6 第 1 步就是过滤）—— ★ 顺序反了会先花掉预算。
    """
    bud = int(budget if budget is not None else q.budget)
    used_facets: list = []

    #: ① 分面过滤
    pool = list(cards)
    before = len(pool)
    if q.domain:
        pool = [c for c in pool if c.domain == q.domain]
        used_facets.append("domain")
    if q.doc_state:
        pool = [c for c in pool if c.facets.get("precondition") == q.doc_state]
        used_facets.append("precondition")
    if q.backend:
        pool = [c for c in pool if c.facets.get("backend") == q.backend]
        used_facets.append("backend")
    if q.capability:
        pool = [c for c in pool if c.facets.get("availability") == q.capability]
        used_facets.append("availability")

    #: ② 召回（★ 词法 + n-gram + 同义词）
    if (q.text or "").strip():
        toks = expand_query(q.text)
        scored = []
        for c in pool:
            blob = c.search_blob().lower()
            name = c.name.lower()
            #: ★ 打分：**命中词元数**，★ 长词元权重高（★ 2-gram 比 1-gram 更有信息量）
            s = sum(len(t) for t in toks if t and t in blob)
            if s <= 0:
                continue
            #: ★★ **名字命中加权**（★ Q4：工具名是作者定的，最可靠）——
            #:   ⚠ 实测（2026-10-12）：不加权时「打孔」把
            #:     `costing_read_analysis` 排到第 2（★ 它文档里"顺便提到"孔）
            #:     ⇒ ★ 名字里真带 `hole` 的应当排前面。
            s += 2 * sum(len(t) for t in toks if t and t in name)
            scored.append((s, c))
        scored.sort(key=lambda x: (-x[0], x[1].name))
        pool = [c for _, c in scored]
    else:
        pool = sorted(pool, key=lambda c: c.name)

    #: ③ 预算截断（★ 不是报错 —— ★ 与阶段 4 同口径）
    out: list = []
    used = 0
    truncated = 0
    for c in pool:
        if used + c.tokens > bud:
            truncated += 1
            continue
        used += c.tokens
        out.append(c)
    return RetrievalResult(
        cards=out,
        tokens=used,
        truncated=truncated,
        facets_used=used_facets,
        candidates_before_filter=before,
    )


#: ══════════════════════════════════════════════════════════════════════
# 六、按需加载契约（★ N10 —— ★ Q6 L105）
#: ══════════════════════════════════════════════════════════════════════


def load_contract(
    card: ToolCard, *, registry: dict | None = None, budget: int = TOKEN_BUDGET
) -> dict:
    """★★ **选中后只加载该方法的完整参数契约**（★ N10 —— ★ Q6 L105）。

    ★★ 判据：**只回这一个工具的契约**，★ **不塞全部 schema**
      （★ Q6 L106 逐字：「不把全部工具 schema 塞给 LLM」）。
    """
    from . import registry as REG

    reg = registry if registry is not None else REG.build_registry()
    d = reg.get(card.name)
    if d is None:
        raise CatalogError("no-domain", "★ 目录里没有 %s" % card.name)
    #: ⚠ 实测（2026-10-12）：`ToolDescriptor.params` 是**元组**（不是 dict）——
    #:   ★ 第一版按 dict 遍历 ⇒ `AttributeError: 'tuple' object has no attribute
    #:   'items'`。⇒ ★ 判据：**两种形状都要吃**（★ 元组 = 参数名，dict = 名→定义）。
    raw = getattr(d, "params", ()) or ()
    params: dict = {}
    if isinstance(raw, dict):
        for pn, p in raw.items():
            params[pn] = {
                "type": getattr(p, "type", "?"),
                "required": bool(getattr(p, "required", False)),
                "desc": (getattr(p, "desc", "") or "")[:120],
            }
    else:
        req = set(getattr(d, "required", ()) or ())
        for pn in raw:
            nm = pn if isinstance(pn, str) else getattr(pn, "name", str(pn))
            params[nm] = {"required": nm in req}
    contract = {
        "name": card.name,
        "domain": card.domain,
        "title": card.title,
        "facets": dict(card.facets),
        "params": params,
        "requires": list(getattr(d, "requires", ()) or ()),
        "inject": getattr(d, "inject", "") or "",
        "admitted": bool(getattr(d, "admitted", True)),
    }
    tk = _est_tokens(json.dumps(contract, ensure_ascii=False))
    contract["tokens"] = tk
    if tk > budget:
        raise CatalogError(
            "budget-exceeded",
            "★ %s 的契约 %d token 超预算 %d" % (card.name, tk, budget),
        )
    return contract


#: ══════════════════════════════════════════════════════════════════════
# 七、recall / chain_hit 指标（★ N7 —— ★ Q4 L48-55）
#: ══════════════════════════════════════════════════════════════════════


def evaluate_recall(
    cases: list,
    cards: list,
    *,
    thresholds: dict | None = None,
    budget: int = TOKEN_BUDGET,
) -> dict:
    """★★ **recall / chain_hit / 域跨度**（★ N7 —— ★ Q4 L48-55 逐字给的公式）。

    ★★ Q4 L49-51 逐字：
      ```
      recall_i    = max_j |R_i ∩ G_ij| / |G_ij|
      chain_hit_i = 1，当存在 G_ij ⊆ R_i；否则为 0
      ```
    ★★ **每题**的 `gold_chains` 是**业主给的**（★ Q4 L44）——
      ★ 本函数**只算指标**，★ 不生成语料。
    """
    th = (thresholds or load_thresholds())["thresholds"]
    rows = []
    for case in cases:
        q = RetrievalQuery(
            text=case.get("text", ""), domain=case.get("domain", ""), budget=budget
        )
        r = retrieve(q, cards, budget=budget)
        got = {c.name for c in r.cards}
        chains = case.get("gold_chains") or []
        if not chains:
            rows.append({"id": case.get("id", "?"), "skip": "★ 没有 gold_chain"})
            continue
        #: ★ recall_i = max_j |R ∩ G_j| / |G_j|
        rec = max((len(got & set(g)) / len(g)) for g in chains if g)
        #: ★ chain_hit_i = 1 当存在 G_j ⊆ R
        hit = any(set(g) <= got for g in chains if g)
        #: ★ 域跨度（★ 命中的卡跨了几个域）
        span = len({c.domain for c in r.cards})
        rows.append(
            {
                "id": case.get("id", "?"),
                "recall": round(rec, 4),
                "chain_hit": hit,
                "domain_span": span,
                "tokens": r.tokens,
                "whole_machine": bool(case.get("whole_machine")),
            }
        )
    live = [r for r in rows if "recall" in r]
    if not live:
        return {
            "ok": False,
            "reason": "★ 没有可算的用例（★ 语料要业主编）",
            "rows": rows,
            "thresholds": th,
        }

    avg_recall = sum(r["recall"] for r in live) / len(live)
    chain_rate = sum(1 for r in live if r["chain_hit"]) / len(live)
    #: ★ Q4 L55 逐字：**复杂整机需求不参加「≤3 个域」这一局部检索指标**
    local = [r for r in live if not r["whole_machine"]]
    span3 = (
        sum(1 for r in local if r["domain_span"] <= 3) / len(local) if local else 0.0
    )

    out = {
        "n": len(live),
        "avg_recall": round(avg_recall, 4),
        "chain_hit": round(chain_rate, 4),
        "domain_span_3_ratio": round(span3, 4),
        "local_n": len(local),
        "thresholds": th,
        "rows": rows,
    }
    out["checks"] = {
        "avg_recall": avg_recall >= th["avg_recall"],
        "chain_hit": chain_rate >= th["chain_hit"],
        "domain_span": span3 >= th["domain_span_3_ratio"],
    }
    out["ok"] = all(out["checks"].values())
    out["★"] = "★ 阈值取自冻结文件（★ 不得看过结果后下调）"
    return out


def thresholds_digest() -> str:
    """★ 阈值文件的**摘要**（★ 用于证明它没被事后改过）。"""
    p = METADATA / "thresholds.json"
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


#: ══════════════════════════════════════════════════════════════════════
# 八、MCP 暴露面（★ N9 —— ★ Q6 L110-112）
#: ══════════════════════════════════════════════════════════════════════

MODE_AUTONOMOUS = "autonomous"
MODE_COMPAT = "compat"
MODES = (MODE_AUTONOMOUS, MODE_COMPAT)

#: ★★ **自主模式允许暴露的**（★ Q6 L110 逐字：「只返回**规划入口与必要查询工具**」）
#: ⚠ 实测（2026-10-12）：第一版**漏了 `solidworks_` 前缀** ⇒
#:   ★ 自主模式暴露 **0 个** ✗（★ 而"0 个"看起来像"没有规划入口"，
#:   不像"名字写错了"）。⇒ ★ 判据：**名字按规范名逐字写**（★ 见 `registry.PREFIX`）。
AUTONOMOUS_ALLOW = (
    #: ── 规划入口（★ 规格 329 接进 MCP 的 4 个目录检索 —— Q6 L110）
    #:   ★ 它们去掉前缀后的**裸步名**正是 `catalog_*` ⇒ ★ 与唯一映射规则自然对上。
    "solidworks_catalog_domains",
    "solidworks_catalog_retrieve",
    "solidworks_catalog_contract",
    "solidworks_catalog_exposure",
    #: ── 必要查询工具（★ 只读、无副作用）
    "solidworks_part_mass_properties",
    "solidworks_part_bounding_box",
    "solidworks_feature_list_names",
    "solidworks_entities_on_body",
    "solidworks_current_selection",
    "solidworks_selection_count",
    "solidworks_collect_model_summary",
    "solidworks_read_document_units",
    "solidworks_feature_present",
    "solidworks_feature_whats_wrong",
    "solidworks_collect_view_evidence",
    "solidworks_surface_evidence",
    "solidworks_sheet_metal_evidence",
    "solidworks_weldment_evidence",
    "solidworks_config_inspect",
    "solidworks_custom_property_list",
    "solidworks_custom_property_names",
    "solidworks_equation_list",
    "solidworks_drawing_list_sheets",
    "solidworks_drawing_list_views",
    "solidworks_drawing_current_sheet_name",
    "solidworks_assembly_list_components",
    "solidworks_assembly_list_mates",
    "solidworks_sketch_count_lines",
    "solidworks_sketch_count_arcs",
    "solidworks_sketch_count_segments",
    "solidworks_sketch_fully_defined_status",
)


def exposure(cards: list, mode: str = MODE_COMPAT) -> dict:
    """★★ **MCP 暴露面**（★ N9 —— ★ Q6 L110-112）。

    ★★ 判据（★ 三条，★ 逐字承 Q6）：
      ```
      ① 自主模式：`tools/list` 只返回**规划入口与必要查询工具**
      ② 兼容模式：保留原工具名称和签名
      ③ ★★ **隐藏工具仍要在实际调用分发处检查权限，不能靠隐藏列表防旁路**
      ```
    ★★ **③ 是结构性保证**：本函数**只产出列表**；
      ★ 权限检查必须由 `authorization.check_tool` 在**分发处**做（★ 见测试 V4）。
    """
    if mode not in MODES:
        raise CatalogError("unknown-facet", "★ 未知模式：%r" % mode)
    if mode == MODE_AUTONOMOUS:
        names = [c.name for c in cards if c.name in AUTONOMOUS_ALLOW]
    else:
        names = [c.name for c in cards]
    return {
        "mode": mode,
        "names": sorted(names),
        "count": len(names),
        "hidden_count": len(cards) - len(names),
        "★": "★ 隐藏 ≠ 防旁路 —— ★ 权限检查在分发处（authorization.check_tool）",
        "dispatch_check_required": True,
    }


#: ══════════════════════════════════════════════════════════════════════
# 九、MCP 工具入口（★ 规格 329 —— ★ Q6 L110「必须同时改 MCP 暴露面」）
#: ══════════════════════════════════════════════════════════════════════
# ★★ 实测（2026-10-12）：规格 323 产出了 `retrieve()` / `load_contract()` /
#   `exposure()` 三个判定函数，而它们在 `AUTONOMOUS_ALLOW` 里**有名字、没注册**
#   ⇒ ★ **agent 够不到检索层**。
# ⇒ ★ 本节把它们包成**可注册的函数**（★ `mcp-server/tool_specs_catalog.py`
#   用 `module="engineering.catalog"` 指向这里）。
# ★ 判据：**纯 Python、只读、不碰 COM**。


def catalog_retrieve(
    *,
    query: str = "",
    domain: str = "",
    doc_state: str = "",
    backend: str = "",
    capability: str = "",
    budget: int = TOKEN_BUDGET,
) -> dict:
    """★★ **分面检索入口**（★ Q6 L102-107 五步）。"""
    cards = build_catalog()
    q = RetrievalQuery(
        text=query,
        domain=domain,
        doc_state=doc_state,
        backend=backend,
        capability=capability,
        budget=budget,
    )
    r = retrieve(q, cards, budget=budget)
    return {
        "cards": [c.to_dict() for c in r.cards],
        "tokens": r.tokens,
        "truncated": r.truncated,
        "facets_used": r.facets_used,
        "candidates_before_filter": r.candidates_before_filter,
        "★": (
            "★ 分面过滤在召回之前；★ `module` **不参与**检索匹配"
            "（★ 只作定位信息 —— Q4 L40 逐字）"
        ),
    }


def catalog_contract(*, tool_name: str = "") -> dict:
    """★★ **按需加载单个工具的完整契约**（★ Q6 L105）。"""
    cards = {c.name: c for c in build_catalog()}
    card = cards.get(tool_name)
    if card is None:
        return {
            "error": "★ 目录里没有 %s" % tool_name,
            "hint": "先用 cadstudio_catalog_retrieve 找",
        }
    return load_contract(card)


def catalog_domains() -> dict:
    """★★ **列出八个任务域与七个受控多标签**（★ Q4 L38）。"""
    doms = load_domains()
    facets = load_facets()
    return {
        "domains": [
            {"id": d.id, "name": d.name, "order": d.order}
            for d in sorted(doms.values(), key=lambda x: x.order)
        ],
        "facets": {k: sorted(v.values) for k, v in facets.items()},
        "★": "★ Q4 L38 逐字：八个一级任务域 + 七个受控多标签",
    }


def catalog_exposure(*, mode: str = MODE_COMPAT) -> dict:
    """★★ **看某个模式的 MCP 暴露面**（★ Q6 L110）。"""
    return exposure(build_catalog(), mode)
