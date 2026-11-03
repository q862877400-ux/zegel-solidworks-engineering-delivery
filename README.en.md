# Zegel-SWE · SolidWorks Engineering Delivery System (DeepSeek Capability Library)

[中文](README.md) · [English](README.en.md)

This project compiles Chinese mechanical-design rules, acceptance criteria and modelling methods into capabilities that DeepSeek can call and that machines can verify, so that a single instruction can produce a SolidWorks model at the delivery standard of a mechanical engineer: fully constrained, parametrically rebuildable, editable feature tree, closed assembly degrees of freedom, compliant drawings, manufacturable process, traceable conclusions.

What is built here is the compilation of rules into capabilities; tools are only the end effectors. The full definition is in [docs/PROJECT-CHARTER.md](docs/PROJECT-CHARTER.md); the route and build order are in [docs/ENGINEERING-PATH.md](docs/ENGINEERING-PATH.md).

```text
Rules layer (L2) · Method layer (L3) · Tool layer (MCP / Skill / CLI) · Acceptance layer (E1–E7 collectors and judges)
```

## 1. Status and boundaries

| Item | Current position |
|---|---|
| Verified machine baseline | SolidWorks 2024, SolidWorks 2026 SP01.1, AutoCAD 2024 |
| Compatibility targets (not re-tested) | SolidWorks 2025 and other combinations not yet re-tested |
| Capability source of truth | [capabilities.yaml](capabilities.yaml). `verified` has our own run evidence, `stitched` is ported plus statically checked, `not_implemented` is explicitly not done |
| Model-visible tool surface | 544 MCP tools (499 declarative plus 45 handwritten), measured by a real `tools/list` handshake (`python -B tools/probe_mcp_stdio_handshake.py` returns 531 `solidworks_*` and 13 `cadstudio_*`) |
| Tool semantic provenance | 524 of them have an official-API page plus a verbatim anchor in the claims ledger ([docs/tool-official-claims/](docs/tool-official-claims/)); the remaining 20 are registered defects ([specs/353-mcp-tool-official-audit/](specs/353-mcp-tool-official-audit/)) |

Nothing unverified is presented as complete. The domains held under controlled `pilot` (configuration families, sheet-metal U-profile flange and flat-pattern DXF, HSS rectangular weldment frames and cut lists, Simulation/FEA, Routing, complex surfaces, moulds) are marked item by item in `capabilities.yaml` and are not treated as native complete delivery.

## 2. Four entry points

The four entry points are peers and share the same capabilities and scripts.

| Entry point | What it is | How to start |
|---|---|---|
| MCP Server | A local `stdio` MCP server exposing SolidWorks COM allow-listed tools plus open-format tools that need no CAD | `python mcp-server\server.py` (started as a child process by the MCP client) |
| Skill | Clients that support skill import can load the repository root directly | See [SKILL.md](SKILL.md) |
| Desktop | CAD Studio GUI: projects, conversation, tasks, preview, delivery | [apps/desktop](apps/desktop), [apps/workbench-ui](apps/workbench-ui) |
| DSH preset (optional) | The "Lean mode (SW engineer)" preset that gives a DSH session all 544 tools. The plugin and installer live in this repository, so no profile hand-editing on a new machine | `python -B tools\dsh-preset\install_preset.py --apply`, see [docs/dsh-preset-sw-engineer.md](docs/dsh-preset-sw-engineer.md) |

### Minimal run (MCP)

```powershell
# 1. Dependencies
pip install -r mcp-server\requirements.txt

# 2. Environment self-check (reports what is missing, which format it affects, how to install it)
python scripts\cad_doctor.py

# 3. Add an entry in your MCP client (DSH shown here; Claude Code / Cursor work the same, replace the path with your clone)
```

```json
{
  "mcpServers": {
    "solidworks": {
      "command": "python",
      "args": ["D:/path/to/this/repo/mcp-server/server.py"]
    }
  }
}
```

Calling `solidworks_health_check` confirms whether SolidWorks is reachable on this machine.

SolidWorks is a Windows desktop COM application. This server defaults to `stdio` and serializes calls internally with a global lock. Do not run more than one SolidWorks MCP on the same machine; several processes competing for one COM connection will deadlock.

## 3. Repository layout

| Path | Contents |
|---|---|
| `mcp-server/` | MCP server and tool declarations (`server.py`, `tool_registry.py`, `tool_specs_batch*.py`) |
| `scripts/` | Capability layer and all gates (`sw_*.py` capability modules, `check_*.py` gates, `release_check.py`) |
| `tools/` | Real-machine guard (`guard_run.py`), probes, generators, round chain (`round_chain.ps1`) |
| `docs/` | Charter, route, plan, knowledge entries, measured ledgers (`docs/state/`), history archive (`docs/history/`) |
| `specs/` | Per-item specifications in Spec Kit form (spec / plan / tasks / acceptance readings) |
| `tests/` | Contract tests and gate self-proofs (including negative cases) |
| `apps/` | Desktop clients (Tauri plus web frontend) |
| `references/`, `subskills/`, `examples/` | Reference material, sub-skills, reproducible examples |
| `AI Solidworks/` | Local workspace for official documentation, models and screenshots (not committed, see `.gitignore`) |

## 4. Quality and acceptance

```powershell
# Full gate set (66 gates: conventions, signatures, units, evidence, gate wiring, tool contract, official claims, etc.)
python -B scripts\release_check.py

# One round chain (generators + release_check + focused tests, about 3–5 minutes)
pwsh -File tools\round_chain.ps1 -Tests tests\<changed>.py

# Real-machine commands always go through the guard (detects and handles modal dialogs, always prints a VERDICT line)
python -B tools\guard_run.py --timeout 300 -- <your command>
```

Acceptance criteria:

- The acceptance criteria are E1–E7 from the charter, not the number of tools. Collectors take readings from the actual artifacts; judges evaluate them against frozen requirements.
- Unit discipline: every dimensioned parameter carries a unit suffix in its name (`_mm`, `_m`, `_deg` and so on), and conversion happens once at the boundary.
- Official basis: read the official page first (signature, Remarks, Example) before touching any COM member. Tool descriptions must point back to verbatim anchors on official pages; `scripts/check_tool_official_claims.py` rejects invented quotations, wrong pages and unchecked members.

## 5. Documentation entry points

| Question | Where |
|---|---|
| Why the project exists, what success looks like | [docs/PROJECT-CHARTER.md](docs/PROJECT-CHARTER.md) |
| How it gets there (route and S0–S6) | [docs/ENGINEERING-PATH.md](docs/ENGINEERING-PATH.md) |
| What to do now | [docs/PLAN.md](docs/PLAN.md) |
| Readings and reproduction commands | [docs/state/INDEX.md](docs/state/INDEX.md) |
| Operating discipline (for people and for AI) | [AGENTS.md](AGENTS.md) |
| Known facts, dead ends, past pitfalls | [docs/known-facts.md](docs/known-facts.md), [docs/dead-ends.md](docs/dead-ends.md) |

## 6. Origins and licensing

- This repository is released under MIT, see [LICENSE](LICENSE).
- It has a code and documentation lineage relationship with the upstream `wzyn20051216/solidworks-automation-skill`. The upstream README is archived verbatim at [docs/history/README-upstream.md](docs/history/README-upstream.md); installation and usage are governed by this document.
- The scope and obligations for the four external MCP projects (MIT; Apache-2.0 with NOTICE retention; AGPL read for ideas only, no code copied) are in [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md). Crack-related sites are not touched at all.

## 7. References and acknowledgements

At the start of the project we read through and surveyed the public SolidWorks automation projects: their interface wrappers, test layering, error handling and understanding of the official API. That work decided how this project should be built and which paths were dead ends. The projects surveyed are listed below by purpose. The licence column was verified in 2026-11 by reading each repository's `LICENSE` file, not by trusting README badges.

**Code or design actually used**

| Project | Licence | What was taken |
|---|---|---|
| `wzyn20051216/solidworks-automation-skill` | MIT | The project's original source. `mcp-server/server.py` is kept unchanged (45 tool implementations), and 49 `scripts/*.py` modules plus `subskills/` are built on from there |
| `microsoft/UFO` | MIT | The configuration-driven GUI input layer design (`input_text_api`, `input_text_enter`, `input_text_inter_key_pause`), used in `sw_gui_input.py` and `sw_jlcfa_fill.py`. The pattern is borrowed; the code is ours |
| `Eduardof0nt/Solidworks-MCP-Server` | MIT | Which two actions the mould domain needs (parting line, shut-off surface). Its method names do not exist in the official type library, so only the idea was taken and the implementation follows the shipped type library |

**Evaluated, no code merged**

| Project | Licence | What was examined |
|---|---|---|
| `andrewbartels1/SolidworksMCP-python` | MIT | Comparison for tool grouping and parameter organisation |
| `vespo92/SolidworksMCP-TS` | MIT | The `mock-solidworks-adapter` test layering, macro-generator and several `.vba` samples |
| `Slacker-LLC/solidworks-mcp` | Apache-2.0 | Comparison of tool surface coverage. Nothing merged, so its NOTICE obligation is not triggered |

**Survey and cross-checking**

| Project | Licence | What was examined |
|---|---|---|
| `xarial/codestack` | MIT | View creation, document operations, assemblies, import/export, and its troubleshooting fault taxonomy |
| `angelsix/solidworks-api` | MIT | SolidDNA template idea (avoiding template dialogs) |
| `deloarts/pyswx` | MIT | How to organise type-library wrappers |
| `painezeng/CSharpAndSolidWorks` | MIT | Geometry algorithms (self-intersection, convexity, area) and `.SLDPRT` test parts |
| `alisamsam/Solidworks-MCP` | MIT | A corpus of 27 `.vbs` files, used to check VBScript-side usage |
| `delancy827/solidworks-skills` | MIT | Cross-checking (independent support for "23 parameters, not 17") |
| `djlex83/solidworks-automation-skill` | MIT | The concise `VARIANT(VT_DISPATCH, None)` form |
| `Sakikooooo/solidworks-auto-modeling` | MIT | Distinguishing `Nothing` (scalar Dispatch) from `Empty` (Variant) |
| `Mochaxgcc/solidworks-ai-bridge` | MIT | Evidence for passing 23 positional parameters bare |
| `guoleizhen717/solidworks-api-skill` | MIT | A counter-example: its claim that more than 12 parameters fails is wrong and should not be believed |
| `ZiChen-Ni/solidworks-com-automation-skill` | MIT | Minimal COM wrapper and Windows install script |
| `just1step/solidworks-mcp` | MIT | Comparison of tool surface coverage |
| `Cai-aa/CAD-Agent-Hub` | MIT | How agents and CAD are organised to work together |
| `kalyanpi4/pySW` | GPL-2.0 | Ideas read only, no code copied |
| `eyfel/mcp-server-solidworks` (product name SolidPilot) | AGPL | Ideas read only, no code copied. Its derivative `Bennyco86/q3ds-solidworks-mcp` is also AGPL |
| `pedropaulovc/offline-solidworks-api-docs` | No licence | Pipeline idea read only. The local `C:\swapi` layout was inspired by it; its output is not distributed with this repository |
| `pengxiaoan/solidworks-build-mechanical-models` | No licence | Ideas read only |
| `walterkken/doc-driven-engineering-software-skills` | All rights reserved | Only the methodology of a documentation-driven directory structure was taken |

Two official offline sources are used daily as the basis: the SolidWorks API help (unpacked CHM) and a structured markdown type library, used to check signatures, Remarks and the call order in official examples. They are not open-source projects and are mentioned here only for completeness.

The authors and maintainers of the projects above made that experience readable, and this project avoided many detours because of it. Thanks to them. If any licence determination or attribution above is wrong, please open an issue and it will be corrected to match the facts.

## 8. Maintenance rules

- Commit through `python tools/commit_mine.py -m <message file> <paths…>`. Do not use a bare `git commit -m "<multi-line>"`; PowerShell treats the quotes as a pathspec.
- Pushing to a remote, creating a new repository and publishing a release require owner approval; local commits do not.
- Round close: `round_chain` green, commit by path; state goes into `capabilities.yaml` and the `docs/` ledgers, not into the conversation.
