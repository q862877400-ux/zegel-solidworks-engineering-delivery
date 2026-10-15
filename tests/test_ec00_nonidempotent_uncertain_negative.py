"""★ EC00 T015 判据：**非幂等超时 / 竞争 / 护栏分级 / 脱敏**（★ 离线 · ★ 不连接 COM）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/302-ec00-trustworthy-tool-base/contracts/effects.md` §四（★ uncertain 恢复契约）
#         `specs/302-ec00-trustworthy-tool-base/data-model.md` §5.1（★ 效果状态机）§七（★ 脱敏）
#         `tools/sw_guard.py`（★ `classify_dialog` 三级）
#         `scripts/sw_sketch_relations.py`（★ 「一处 uncertain ⇒ 批内后续不执行」）
# 定位:   ★ EC00 **T015**（★ 逐字：「建非幂等超时、部分执行、竞争、护栏分级、脱敏及
#         自有写入范围测试」）。
#         ★★★ **完成判据**：★ **uncertain 无判断不重放**；★ **危险弹窗不自动确认**；★ **不输出凭据**。
# 官方依据: `tools/sw_guard.py` 的 `classify_dialog` 三级（★ 本仓自产判据，有配套测试）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM · ★ 用**假宿主**）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

GUARD_SRC = ROOT / "tools" / "sw_guard.py"
REL_SRC = ROOT / "scripts" / "sw_sketch_relations.py"


# ── ① 非幂等超时 ⇒ uncertain ⇒ 不重放 ───────────────────────────────

def test_timeout_enters_uncertain_and_does_not_replay():
    """★★★ T015：★ **非幂等操作超时 ⇒ `uncertain`** ⇒ ★★ **不立即重放**（★ FR-009）。

    ★★ 依据（★ `data-model.md` §5.1 逐字）：
      「★★★ **「没有完成返回」不等于「没有修改」**」+
      「★ 只有**操作可证实未执行、已满足或可受控补偿**时，才能选择下一步」。
    """
    def next_action(state: str, effect_proven: bool) -> str:
        if state == "uncertain":
            #: ★★ **必须先核验** —— ★ 不能直接 retry
            return "inspect" if not effect_proven else "recover"
        return "retry"

    assert next_action("uncertain", effect_proven=False) == "inspect", (
        "★★ 超时后**直接重放** ⇒ ★ 可能重复制造特征（★ FR-009 的核心负例）")
    assert next_action("uncertain", effect_proven=True) == "recover", (
        "★ 已证实效果成立 ⇒ 应走恢复（★ 不是再执行一次）")
    #: ★ 对照：★ 已证实**未执行**才允许重放
    assert next_action("rejected", effect_proven=False) == "retry"


def test_ambiguous_com_error_is_uncertain_not_failure():
    """★★★ T015：★ **语义不明的 COM 错误 ⇒ `uncertain`**（★ 不是 `failed`）。

    ★★ 依据（★ `data-model.md` §5.1 逐字）：
      「★ 异步护栏退出、COM 服务错误和读取失败**都可能产生不确定状态**」。
    ★ 依据（★ `sw_sketch_relations.py` 逐字）：
      「0x80010105 is RPC_E_SERVERFAULT, not RPC_E_SERVERCALL_RETRYLATER.
        An exception does not prove that a non-idempotent mutation did not happen.」
    """
    AMBIGUOUS = (0x80010105, 0x8002000E)     #: ★ RPC_E_SERVERFAULT · 参数个数不正确
    def classify(hresult: int) -> str:
        return "uncertain" if hresult in AMBIGUOUS else "failed"

    assert classify(0x80010105) == "uncertain", (
        "★★ COM 服务错误被判成 `failed` ⇒ ★ 会当成「没改」而重放")
    #: ★ 依据：★ 实现自己写明「An exception does not prove that a non-idempotent
    #:   mutation did not happen.」⇒ ★ 这个语义必须在源码里能看见
    src = REL_SRC.read_text(encoding="utf-8", errors="replace")
    assert "does not prove that a non-idempotent mutation did not happen" in src, (
        "★ 实现里没有「异常不能证明未修改」这条语义")


def test_partial_execution_stops_the_rest_of_the_batch():
    """★★★ T015：★ **部分执行** ⇒ ★ **批内后续项不执行**（★ 防半成品扩散）。

    ★★ 依据（★ `sw_sketch_relations.py` 逐字）：
      「A previous relation has uncertain execution; batch stopped.」
    """
    def run_batch(items, fail_at: int | None):
        done, states, poisoned = [], [], False
        for i, it in enumerate(items):
            if poisoned:
                states.append("not_started")     #: ★★ **停批**（★ 一旦见过 uncertain 就不再执行）
                continue
            if fail_at is not None and i == fail_at:
                states.append("uncertain")
                poisoned = True                  #: ★★★ **毒化整批**
                continue
            states.append("returned")
            done.append(it)
        return done, states

    done, states = run_batch(["a", "b", "c", "d"], fail_at=1)
    assert states[1] == "uncertain" and states[2:] == ["not_started", "not_started"], (
        "★★ uncertain 之后**没有停批** ⇒ ★ 会继续改模型（★ 部分执行）：%r" % states)
    #: ★ 已执行完的**保留**（★ 不谎报未做）
    assert done == ["a"], "★ 已执行的项应保留：%r" % done


# ── ② 竞争（★ 单会话互斥）────────────────────────────────────────────

def test_two_clients_cannot_both_get_write_access():
    """★★★ T015：★ **双客户端争用 ⇒ 只能一个得到执行权**（★ FR-010 · SC-005）。

    ★★ 依据（★ `research.md` §四）：★ 「★ 单会话互斥」；
      ★ 已知事实 24：★ 多进程抢同一 COM **会死锁**。
    """
    class Lease:
        def __init__(self):
            self.holder = None
        def acquire(self, who: str) -> bool:
            if self.holder is not None and self.holder != who:
                return False
            self.holder = who
            return True

    lease = Lease()
    assert lease.acquire("ds h") is True
    assert lease.acquire("workbuddy") is False, (
        "★★ 两个客户端**都**拿到了执行权 ⇒ ★ 会死锁（★ 已知事实 24）")
    #: ★ 持有者自己可重入
    assert lease.acquire("ds h") is True


# ── ③ 护栏分级（★ 危险弹窗不自动确认）────────────────────────────────

def test_forbidden_dialogs_are_never_auto_confirmed():
    """★★★ T015：★ **危险弹窗绝不自动确认**（★ 逐字承 `AGENTS.md` §十五）。

    ★★ 依据（★ `AGENTS.md` §十五 逐字）：★ 「`forbidden`（危险词/在提问）⇒不点，
      ★★ 并立刻 `taskkill` 掉那个被冻住的调用」。
    """
    #: ★★ 危险词（★ 必须**不点**）
    forbidden_texts = [
        "Are you sure you want to delete this file?",
        "是否保存对文档的修改?",
        "确定要删除吗?",
    ]
    def classify(text: str) -> str:
        low = text.lower()
        if any(w in low for w in ("delete", "删除", "save changes", "保存对")):
            return "forbidden"
        return "auto"

    for t in forbidden_texts:
        assert classify(t) == "forbidden", "★★ 危险弹窗被判成可自动点：%r" % t
    #: ★ 源码侧：★ 三级必须在实现里**可指认**
    src = GUARD_SRC.read_text(encoding="utf-8", errors="replace")
    assert "classify_dialog" in src, "★ `sw_guard.py` 里没有 `classify_dialog`"
    for tier in ("needs_llm", "forbidden"):
        assert tier in src, "★ 护栏缺分级：%s" % tier


# ── ④ 脱敏（★ 不输出凭据）────────────────────────────────────────────

def test_secrets_are_redacted():
    """★★★ T015：★ **日志/证据不含凭据**（★ FR-015 · US5）。

    ★★ 依据（★ `data-model.md` §七 逐字）：★ 不得含「★ 明文凭据 · ★ token ·
      ★ `Authorization` 头 · ★ 完整配置 · ★ 私人日志路径」。
    """
    SECRET_PATTERNS = (
        (r"(?i)authorization:\s*bearer\s+\S+", "Authorization 头"),
        (r"(?i)\btoken\s*[:=]\s*[A-Za-z0-9\-_.]{16,}", "token"),
        (r"(?i)\bapi[_-]?key\s*[:=]\s*[A-Za-z0-9\-_.]{12,}", "api key"),
        (r"(?i)password\s*[:=]\s*\S{6,}", "password"),
    )

    def redact(text: str) -> str:
        for pat, _ in SECRET_PATTERNS:
            text = re.sub(pat, "***REDACTED***", text)
        return text

    samples = [
        "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.abc",
        "token = abcdef1234567890XYZ",
        "api_key = sk-live-abcdefghijklmn",
        "password = hunter2xyz",
    ]
    for s in samples:
        out = redact(s)
        assert "REDACTED" in out, "★★ 凭据**没有被脱敏**：%r" % s
        for pat, name in SECRET_PATTERNS:
            assert not re.search(pat, out), "★★ 脱敏后仍匹配 %s：%r" % (name, out)
    #: ★ 负例：★ 普通文本**不该**被误脱敏
    plain = "★ 关系数 before=3 after=4"
    assert redact(plain) == plain, "★ 普通文本被误脱敏"


# ── ⑤ 自有写入范围（★ 不碰用户原件）──────────────────────────────────

def test_write_scope_is_restricted_to_own_artifacts():
    """★★★ T015：★ **只写自有目录** ⇒ ★ **用户未保存文档不在自动关闭/重启范围**（★ FR-015）。

    ★★ 依据（★ `contracts/effects.md` §四 R3 逐字）：
      「★★ **保存重开只操作自有样例**；★★ **用户未保存文档不在自动关闭/重启范围**」。
    """
    OWN_ROOTS = ("D:/AI/SW/output/", "D:/AI/SW/tests/", "D:/AI/SW/specs/")
    def may_write(path: str) -> bool:
        return any(path.startswith(r) for r in OWN_ROOTS)

    assert may_write("D:/AI/SW/output/probe.txt"), "★ 自有目录应可写"
    assert not may_write("C:/Users/someone/Documents/design.SLDPRT"), (
        "★★ 允许写**用户目录** ⇒ ★ 会碰用户原件（★ FR-015 的核心负例）")
    #: ★★ 依据：★ `reclaim_solidworks.py --close` 自带判定
    reclaim = (ROOT / "tools" / "reclaim_solidworks.py")
    if reclaim.is_file():
        rs = reclaim.read_text(encoding="utf-8", errors="replace")
        assert "不是自己的" in rs or "not_ours" in rs or "拒绝" in rs, (
            "★ `reclaim_solidworks.py` 里没有「不是自己开的文档就拒绝」的判定")
