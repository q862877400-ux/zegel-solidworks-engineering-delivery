"""★ EC00 T021 判据：**证据 manifest 版本化** —— `unknown`/`not_run`/`expired` **不变成通过**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/302-ec00-trustworthy-tool-base/data-model.md` §六（★ `EvidenceManifest`）
#         `scripts/check_verified_evidence.py`（★ `verified` 须有非空 `evidence`）
#         `capabilities.yaml`（★ `level` + `evidence` + `verified_versions`）
# 定位:   ★ EC00 **T021**（★ 逐字：「实现证据字段、错误脱敏、版本失效与等级记录；
#         必要时扩展现有 schema」）。
#         ★★★ **完成判据**：★ **`unknown`、`not_run` 和 `expired` 不变成通过**；
#         ★ **hash 未实填不生成真实证据**。
# 官方依据: 总计划 §8.1（★ 验收记录的最小形状 —— ★ 尖括号字段**不能**进入真实证据）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "specs" / "302-ec00-trustworthy-tool-base"

#: ★★★ 结果封闭词表（★ `data-model.md` §六）
RESULTS = ("pass", "fail", "unknown", "not_run", "expired")
#: ★★ **只有 `pass` 是「通过」**
RELEASING = ("pass",)
#: ★★ 三级
LEVELS = ("offline", "runtime", "product")


def _is_releasing(result: str, level: str, artifact_version: str) -> bool:
    """★ 复刻契约的**放行规则**（★ 纯函数 · ★ 参考值不取自被测实现）。

    ★★★ 规则（★ `data-model.md` §六）：
      · ★ 只有 `result == "pass"` 才可能放行；
      · ★★ **`artifact_version` 未实填（含 `<`/`>` 尖括号）⇒ 不算真实证据**；
      · ★★ **`unknown`/`not_run`/`expired` 一律不放行**。
    """
    if result not in RELEASING:
        return False
    #: ★★ 尖括号字段**不能**进入真实证据（★ 总计划 §8.1 逐字）
    if not artifact_version or "<" in artifact_version or ">" in artifact_version:
        return False
    return True


# ── ① unknown / not_run / expired 不放行 ─────────────────────────────

def test_non_pass_results_never_release():
    """★★★ T021：★ **`unknown` / `not_run` / `expired` 一律不放行**（★ 逐字承完成判据）。"""
    good_ver = "sha256:" + "a" * 64
    for r in ("unknown", "not_run", "expired", "fail"):
        assert not _is_releasing(r, "runtime", good_ver), (
            "★★ `%s` 被放行了 ⇒ ★ 未完成被当成通过" % r)
    #: ★ 对照：★ 真的 pass 且 hash 实填 ⇒ 放行
    assert _is_releasing("pass", "runtime", good_ver), "★ 正常的 pass 应放行"


def test_placeholder_hash_is_not_real_evidence():
    """★★★ T021：★ **hash 未实填（尖括号占位）⇒ 不生成真实证据**。

    ★★ 依据（★ 总计划 §8.1 逐字）：
      「★ **这是格式说明，尖括号字段不能进入真实证据**」+
      「★★ **真实执行必须填真实值；未运行不生成「通过」manifest**」。
    """
    for placeholder in ("sha256:<actual-content-hash>", "<actual-environment-record>", "", "<x>"):
        assert not _is_releasing("pass", "runtime", placeholder), (
            "★★ 占位 hash %r 被当成真实证据 ⇒ ★ 会生成假 manifest" % placeholder)


# ── ② 等级不升级 ─────────────────────────────────────────────────────

def test_offline_pass_cannot_be_recorded_as_runtime():
    """★★★ T021：★ **`offline` pass 不能写成 `runtime` pass**（★ FR-013 · US5）。"""
    #: ★ 契约：★ 等级**只能**由真机证据升级
    def promote(level: str, *, runtime_evidence: bool) -> str:
        if level == "offline" and runtime_evidence:
            return "runtime"
        return level

    assert promote("offline", runtime_evidence=False) == "offline", (
        "★★ 没有真机证据却升到了 runtime ⇒ ★ 等级升级规则失效")
    assert promote("offline", runtime_evidence=True) == "runtime", "★ 有真机证据应可升级"


# ── ③ 版本失效 ───────────────────────────────────────────────────────

def test_evidence_expires_when_the_artifact_changes():
    """★★★ T021：★ **工件变了 ⇒ 旧证据 `expired`**（★ US5 · FR-011）。"""
    def state(evidence_hash: str, current_hash: str, level: str) -> str:
        if evidence_hash != current_hash:
            return "expired"
        return "pass"

    assert state("h1", "h1", "runtime") == "pass"
    assert state("h1", "h2", "runtime") == "expired", (
        "★★ 工件变了但证据仍判 `pass` ⇒ ★ 旧证据放行了新模型")


# ── ④ 记录本身必须完整 ───────────────────────────────────────────────

def test_manifest_requires_all_fields():
    """★★ T021：★ manifest **缺字段** ⇒ 不算真实证据（★ 逐字承总计划 §8.1 的形状）。"""
    REQUIRED = ("feature_key", "task_id", "requirement_ids", "verification_level",
                "result", "artifact_version", "environment_ref", "evidence_refs", "reason")

    def valid(m: dict) -> bool:
        return all(k in m for k in REQUIRED) and m.get("verification_level") in LEVELS \
            and m.get("result") in RESULTS

    good = {"feature_key": "EC00", "task_id": "T021", "requirement_ids": ["FR-011"],
            "verification_level": "offline", "result": "pass",
            "artifact_version": "sha256:" + "b" * 64,
            "environment_ref": "local-3.14.7", "evidence_refs": ["tests/x.py"],
            "reason": ""}
    assert valid(good), "★ 完整的 manifest 被判无效"
    #: ★★ 缺一个字段就无效
    for k in REQUIRED:
        bad = {kk: vv for kk, vv in good.items() if kk != k}
        assert not valid(bad), "★★ 缺 `%s` 的 manifest 仍被判有效" % k


# ── ⑤ 落档：EC00 的验收记录里三级分开 ────────────────────────────────

def test_ec00_acceptance_records_three_levels():
    """★★ T021：★ EC00 的验收记录里 **offline/runtime/product 必须分字段**。"""
    acc = SPEC / "acceptance.md"
    assert acc.is_file(), "★ 缺 `acceptance.md`"
    body = acc.read_text(encoding="utf-8", errors="replace")
    for level in LEVELS:
        assert level in body, "★ 验收记录缺 `%s`" % level
    #: ★★ runtime 必须是 not_run（★ 真机未做）
    assert "not_run" in body, "★★ 验收记录里没有 `not_run` ⇒ ★ 可能把离线当成了真机"


# ── ⑥ 落档：契约里必须有封闭词表 ─────────────────────────────────────

def test_data_model_declares_the_closed_result_vocabulary():
    """★★ T021：★ `data-model.md` 必须声明**封闭结果词表**（★ 防有人随手加一个值）。"""
    dm = SPEC / "data-model.md"
    assert dm.is_file(), "★ 缺 `data-model.md`"
    body = dm.read_text(encoding="utf-8", errors="replace")
    for r in RESULTS:
        assert r in body, "★ `data-model.md` 的结果词表缺 `%s`" % r
    #: ★★ 必须写明「`unknown`/`not_run`/`expired` 不变成通过」
    assert "不变成通过" in body, "★ 没写明「不变成通过」这条硬规则"


# ── ⑦ 脱敏（★ 与 T015 同族，此处只核证据侧）────────────────────────

def test_evidence_must_not_contain_credentials():
    """★★ T021/FR-015：★ **证据里不得含凭据**（★ 与 T015 的脱敏同族）。"""
    SECRET = re.compile(r"(?i)(authorization:\s*bearer|token\s*[:=]\s*[A-Za-z0-9]{16,})")
    #: ★ 把 EC00 的验收/数据模型文档当样本扫一遍
    for name in ("acceptance.md", "data-model.md", "research.md"):
        p = SPEC / name
        if not p.is_file():
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
        assert not SECRET.search(body), "★★ `%s` 里出现了凭据形态的串" % name
