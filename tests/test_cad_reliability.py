"""CAD Studio 能力门禁、诊断和连接策略回归测试。"""
# ── 来源 ──
# 仓库:   本项目自身（执行方对上游能力清单的迁移改造，非第三方移植）
# 文件:   tests/test_cad_reliability.py
# 定位:   docs/capabilities-schema-proposal.md §1.2（`pilot`→五级迁移，裁断走选项 A）
#         与 §五 R11；AGENTS.md 铁律 1「每加一个能力必须能指认出处」。
# 许可:   本仓库 MIT。本文件为原创实现，无第三方代码引入。
# ⚠ 未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。本次是清单形状与授权判据的迁移，
#   不改变任何 COM 调用；授权等价性由 tests/test_unattended_equivalence.py 对冻结基线守住。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "apps" / "desktop"))

from cad_diagnostics import create_diagnostic_bundle, _redact  # noqa: E402
from cad_doctor import run_doctor  # noqa: E402
from capabilities import capability_index, load_capabilities, unattended_allowed  # noqa: E402
from cad_workbench.queue_worker import process_job, read_job  # noqa: E402
from sw_connect import _prog_id_for_version, close_owned_solidworks  # noqa: E402
import cad_installation  # noqa: E402
from cad_installation import discover_installation, resolve_shortcut_target  # noqa: E402
import cad_doctor  # noqa: E402


def test_capability_manifest_marks_unverified_workflows():
    """@brief 迁移后：跑过的标 verified，没跑过的标 stitched；授权由 allowed_modes 决定。

    2026-10-01 的 pilot→五级迁移（docs/capabilities-schema-proposal.md §1.2 走选项 A）把
    「证据强度」与「授权」拆成两个字段：原 13 条有 `verified_versions` 的 pilot 迁 `verified`
    （它们跑过，这是事实），但**不补** `unattended`（它们不够格无人值守）；
    原 6 条无证据的迁 `stitched`。本测试同时钉住这两件事。
    """
    index = capability_index(load_capabilities())
    assert index["part_and_features"]["level"] == "verified"
    # 原 pilot 且有运行证据 ⇒ verified（跑过是事实）
    assert index["external_spur_gear_geometry"]["level"] == "verified"
    assert index["external_spur_gear_geometry"]["verified_versions"] == ["2026"]
    assert index["parameter_updates"]["level"] == "verified"
    assert index["custom_properties_and_bom"]["level"] == "verified"
    assert index["pack_and_go"]["level"] == "verified"
    assert index["configurations_and_design_tables"]["level"] == "verified"
    assert index["configurations_and_design_tables"]["verified_versions"] == ["2026"]
    #: ★★★★★★★ 2026-10-04（轮 120）**本条随清单更正** —— ★ 处置这条**存量失败** ✓
    #:   ★ **真机读数**：★ `assert 'not_implemented' == 'verified'` ✓
    #:   ★★ **真因**：★ 本会话**阶段 1**（★ 提交 `a04c68c7`）**把这条降了级** ——
    #:     ★ 它原本写 `verified`、★ **而它的能力层**零实现****（★ **整条虚标**）⇒
    #:     ★★★ **⇒ 降成 `not_implemented`、★ 并从 `allowed_modes` 去掉 `unattended`** ✓
    #:   ★★★★ **⇒ 而本测试还在钉旧的 `verified`** ⇒ **红** ——
    #:     ★ 那与「mock 落后」「登记表落后」「ToolSpec 参数落后」**是同一个病**
    #:     （★ "改了清单/实现、★ 配套的断言没跟上"）✓
    #:   ★★★★★ **⚠ 而这次降级是**有据的****：★ `docs/known-facts.md` 与本仓的记录都写明
    #:     「★ 它的能力层**零实现**」⇒ ★★ **按 A4「`verified` 必须有我们自己的运行证据」**，
    #:     ★ **它本来就该是 `not_implemented`** ✓
    #:   ★★★★★★ **⇒ 判据**：★ 改成 `not_implemented`、★ **并把它**从"跑过 ⇒ verified"那一段
    #:     挪出来**（★ 它不属于那一段）✓
    assert index["drawing_dimension_insertion"]["level"] == "not_implemented", (
        "★ 本会话阶段 1 已把它降级（★ 能力层零实现 ⇒ 整条虚标）⇒ 这里要跟上")
    assert index["sheet_metal"]["level"] == "verified"
    assert index["sheet_metal"]["verified_versions"] == ["2026"]
    assert index["weldments"]["level"] == "verified"
    assert index["weldments"]["verified_versions"] == ["2026"]
    assert index["solidworks_addin_host"]["level"] == "verified"
    assert index["solidworks_addin_host"]["verified_versions"] == ["2026"]
    # ⚑ **2026-10-01 轮 78 起 `routing` 升为 `verified`** —— 依据是**我们自己的端到端验收**：
    #   `python tools/verify_routing_e2e.py`（**18/18 通过**，故意造违规逐条触发 limitations：
    #   碰撞/支撑不足/弯曲半径过小/输入只读/`readyForNativeWrite is False`）
    #   + `pytest tests/test_routing_review.py tests/test_sw_routing_contract.py`（23 passed）。
    #   ⚠ 它的 `limitations` **一条没删**（原生写入仍必须 blocked）；授权仍未放开
    #     （下面 `ready_for_unattended_use is False` 的断言**照旧**）。
    #: ★ 2026-10-01（轮 279）：routing **由 verified 降为 stitched**，依据是**可执行的探测** ——
    #:   `cadstudio_routing_preflight` 回 blocked / readyForNativeWrite=false /
    #:   error_code=routing_addin_or_license_unavailable，`addins: []`（★ 而类型库与三个接口都在）。
    #:   ⇒ ★ 基线跟着**新事实**走（★ 不是为过测试而放松：★ 本处 level 是**降**的）。
    assert index["routing"]["level"] == "stitched"
    assert index["routing"]["limitations"], "routing 标 stitched 就必须写明限制"
    # ⚑ **2026-10-01 轮 79（Spec Kit `004-dfm-verified`）起 `dfm_checks` 升为 `verified`** ——
    #   依据同样是**我们自己的端到端验收**：`python tools/verify_dfm_e2e.py`（**11/11 通过**，
    #   故意造违规逐条触发 limitations 的三句：四种工艺 · 单位归一 · Profile 能力交集 ·
    #   B-Rep 证据绑定 · **缺关键输入 ⇒ blocked + missingInputs 点名** ·
    #   `manualReviewRequired` · 「不等于制造认证」声明）。
    #   + `pytest tests/test_dfm_review.py tests/test_dfm_queue_worker.py`（19 passed）。
    #   ⚠ **本条的 `dependencies` 只有 `python`** —— 此前把它归入「需 B-Rep 证据（⇒ 需 OCP）」
    #     而搁置是**误判**：「B-Rep 证据绑定」指的是**输入由外部给**，不是它自己去跑 OCP。
    #     `limitations` **一条没删**；授权仍未放开。
    assert index["dfm_checks"]["level"] == "verified"
    assert index["dfm_checks"]["verified_versions"] == ["python 3.14.7"]
    assert index["dfm_checks"]["evidence"], "dfm_checks 标 verified 就必须带 evidence"
    # 仍**无运行证据**的（代码已并入、从未运行，或受外部依赖阻塞）
    assert index["surface_modeling"]["level"] == "stitched"
    # 每条 verified 都必须带 evidence（B4）
    for cid, item in index.items():
        if item.get("level") == "verified":
            assert item.get("evidence"), "能力 %s 标 verified 却没有 evidence" % cid
    # 授权：只有原本就 verified 的那 8 条带 unattended；升上来的 13 条不带
    assert unattended_allowed(["part_and_features"]) is True
    assert unattended_allowed(["sheet_metal"]) is False
    assert "unattended" not in (index["sheet_metal"].get("allowed_modes") or [])


def test_job_is_blocked_for_reference_only_capability(tmp_path):
    path = tmp_path / "job.json"
    job = {
        "schemaVersion": "2.0",
        "id": "job-blocked",
        "runId": "run-blocked",
        "kind": "create_shell",
        "title": "钣金任务",
        "detail": "门禁测试",
        "status": "queued",
        "progress": 0,
        "createdAt": "2026-01-01T00:00:00+00:00",
        "updatedAt": "2026-01-01T00:00:00+00:00",
        "projectId": "project-test",
        "conversationId": "conversation-test",
        "inputs": [],
        "stage": "intake",
        "capabilitySnapshot": {},
        "assumptions": [],
        "requiredArtifacts": [],
        "verificationEvidence": [],
        "capabilities": ["sheet_metal"],
        "policy": {"approval": "never"},
    }
    path.write_text(json.dumps(job), encoding="utf-8")
    result = process_job(path, handlers={"create_shell": lambda _: {"message": "should not run"}})
    assert result is not None
    assert result["status"] == "blocked"
    assert result["stage"] == "blocked"
    assert "sheet_metal" in result["blockedReasons"][0]
    assert read_job(path)["status"] == "blocked"


def test_diagnostics_redacts_sensitive_values(tmp_path):
    redacted = _redact({"prompt": "secret prompt", "apiKey": "abc", "projectPath": r"C:\Users\Alice\job"})
    assert redacted == {"prompt": "[redacted]", "apiKey": "[redacted]", "projectPath": "[redacted]"}
    bundle = create_diagnostic_bundle(tmp_path / "diagnostics.zip", events={"prompt": "private"})
    with zipfile.ZipFile(bundle) as archive:
        payload = json.loads(archive.read("diagnostic.json"))
    assert payload["events"]["prompt"] == "[redacted]"
    for installation in payload["doctor"].get("installations", {}).values():
        executable = installation.get("executable")
        assert not executable or "\\" not in executable


def test_doctor_returns_machine_readable_summary():
    result = run_doctor()
    assert result["schemaVersion"] == "1.0"
    assert result["summary"]["status"] in {"passed", "warning", "error"}
    assert all({"id", "status", "code", "message"} <= set(item) for item in result["checks"])
    assert isinstance(result["remediations"], list)


def test_doctor_missing_environment_includes_download_remediations(monkeypatch):
    """@brief 缺失环境必须给出官方入口或安装命令，并保留开放格式降级说明。"""
    monkeypatch.setattr(cad_doctor.importlib.util, "find_spec", lambda _name: None)
    monkeypatch.setattr(cad_doctor.shutil, "which", lambda _name: None)
    monkeypatch.setattr(cad_doctor, "_is_writable", lambda _path: True)
    monkeypatch.setattr(
        cad_doctor,
        "_solidworks_installation",
        lambda: {
            "registered": False,
            "executables": [],
            "executable": None,
            "source": None,
            "version": None,
            "servicePack": None,
            "displayName": None,
            "shortcut": None,
            "available": [],
        },
    )
    monkeypatch.setattr(
        cad_doctor,
        "discover_all",
        lambda: {"autocad": {"installed": False, "executable": None}},
    )
    #: ★★★ 2026-10-10 **业主架构指令**（★ 只继承工具 · 方法移出）：
    #:   ★ `fea_analysis` 是**方法**（★ FEA 判据）⇒ 已移出到
    #:     `archive/inherited-methods/scripts/` ⇒ ★★ **不能再 monkeypatch 它** ✗
    #:   ★★ 而 `cad_doctor` 里那处 `from fea_analysis import discover_solver`
    #:     **本来就有 `try/except`**（★ 找不到就 `calculix_ready = False`）✓
    #:   ⇒ ★ **本测试不需要那处 stub** —— ★ 删掉它，★ 剩下的 12 个断言照旧 ✓
    #:   ★ 判据：★ 本测试测的是**诊断器的机器可读输出**（★ 工具），
    #:     ★★ **不是** FEA 方法本身 ⇒ ★ **它该留下** ✓

    result = run_doctor()
    remediations = {item["id"]: item for item in result["remediations"]}

    assert len(remediations) == len(result["remediations"])
    assert remediations["python.pywin32"]["installCommand"].startswith("python -m pip install")
    assert remediations["python.ocp"]["downloadUrl"].startswith("https://")
    assert "CADSTUDIO_CALCULIX_EXE" in remediations["solver.calculix"]["title"]
    assert remediations["solver.calculix"]["downloadUrl"] == "https://www.calculix.de/"
    assert remediations["cad.solidworks"]["downloadUrl"] == "https://www.solidworks.com/"
    assert remediations["cad.autocad"]["downloadUrl"].startswith("https://www.autodesk.com/")
    assert "开放格式仍可使用" in next(item["message"] for item in result["checks"] if item["id"] == "cad.solidworks")
    assert "DXF/SVG/PDF/PNG" in next(item["message"] for item in result["checks"] if item["id"] == "cad.autocad")


def test_doctor_does_not_prompt_for_other_agents_when_one_is_available(monkeypatch):
    """@brief Agent Provider 是替代关系，已安装一个时不应提示下载其余三个。"""
    checks = [
        cad_doctor._check("agent.codex", True, "codex 已发现"),
        cad_doctor._check("agent.claude", False, "claude 未发现", severity="warning", action="安装 claude CLI", download_url="https://example.invalid"),
    ]

    assert cad_doctor._collect_remediations(checks) == []


def test_versioned_progid_is_used_for_attach_and_launch():
    assert _prog_id_for_version(2024) == "SldWorks.Application.32"
    assert _prog_id_for_version("2026") == "SldWorks.Application.34"


def test_only_owned_solidworks_instance_can_be_closed():
    class FakeSolidWorks:
        closed = False

        def ExitApp(self):
            self.closed = True

    app = FakeSolidWorks()
    assert close_owned_solidworks(app, False) is False
    assert app.closed is False
    assert close_owned_solidworks(app, True) is True
    assert app.closed is True


def test_installer_shortcut_resolves_real_solidworks_executable():
    candidates = resolve_shortcut_target(
        r"C:\WINDOWS\Installer\{demo}\i386_SldWorks.exe",
        r"E:\Solidworks\SOLIDWORKS",
        "SLDWORKS.exe",
    )
    assert Path(r"E:\Solidworks\SOLIDWORKS\SLDWORKS.exe") in candidates
    assert Path(r"C:\WINDOWS\Installer\{demo}\i386_SldWorks.exe") not in candidates


def test_direct_autocad_shortcut_target_is_preserved():
    candidates = resolve_shortcut_target(
        r"D:\AutoCAD 2024\acad.exe",
        r"D:\AutoCAD 2024\UserDataCache",
        "acad.exe",
    )
    assert Path(r"D:\AutoCAD 2024\acad.exe") in candidates


def test_discover_installation_supports_injected_filesystem():
    # 发现逻辑接受 exists 注入，CI 不需要安装 CAD 也能覆盖候选排序与结构。
    result = discover_installation("autocad", exists=lambda path: str(path).lower() == r"d:\autocad 2024\acad.exe")
    assert result["installed"] is True
    assert result["executable"].lower().endswith(r"autocad 2024\acad.exe")


def test_discover_installation_prefers_newest_uninstall_registry_entry(monkeypatch):
    """@brief 多版本并存时必须选择最新版本，并兼容非标准安装目录名称。"""
    monkeypatch.setattr(cad_installation, "_shortcut_paths", lambda _product: [])
    monkeypatch.setattr(cad_installation, "_registry_paths", lambda _product: [])
    monkeypatch.setattr(cad_installation, "_common_candidates", lambda _product: [])
    monkeypatch.setattr(
        cad_installation,
        "_uninstall_registry_candidates",
        lambda _product: [
            {
                "path": Path(r"E:\Solidworks\SOLIDWORKS\SLDWORKS.exe"),
                "source": "uninstall-registry",
                "version": "2024",
                "service_pack": "SP03.1",
                "display_name": "SOLIDWORKS 2024 SP03.1",
                "shortcut": None,
            },
            {
                "path": Path(r"E:\SolidWroks2026\SOLIDWORKS\SLDWORKS.exe"),
                "source": "uninstall-registry",
                "version": "2026",
                "service_pack": "SP01.1",
                "display_name": "SOLIDWORKS 2026 SP01.1",
                "shortcut": None,
            },
        ],
    )

    result = discover_installation("solidworks", exists=lambda _path: True)

    assert result["version"] == "2026"
    assert result["servicePack"] == "SP01.1"
    assert result["executable"] == r"E:\SolidWroks2026\SOLIDWORKS\SLDWORKS.exe"
