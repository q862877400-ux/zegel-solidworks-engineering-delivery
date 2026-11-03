# Zegel-SWE · SolidWorks Engineering Delivery System

[中文](README.md) · [English](README.en.md)

Drive SolidWorks from one natural-language instruction and get models and drawings a mechanical engineer will actually use. Under the hood it is a local MCP server that wraps the SolidWorks COM interface into 544 allow-listed tools, plus a set of checks tuned for Chinese mechanical design practice.

## 1. What counts as done

This project does not treat "the model got built" as done. All seven of the following have to hold:

| # | Standard | What passing looks like |
|---|---|---|
| E1 | Fully constrained sketch | The solver reports fully defined with no under-constrained entities; position, shape and size are driven by geometric and dimensional constraints rather than dragged coordinates |
| E2 | Parametrically rebuildable | Change a driving parameter on a copy of the delivered part, rebuild, and the key dimensions and downstream relations update correctly; still true after saving and reopening |
| E3 | Editable feature tree | No errors or warnings, no dangling references; an earlier sketch or parameter can actually be edited and the result verified |
| E4 | Closed assembly degrees of freedom | Mated objects and remaining motion can be read back; the target degrees of freedom match design intent, interference is zero and key clearances are within spec |
| E5 | Compliant drawings | The annotation list comes from function, manufacturing and inspection requirements, each item bound to a real drawing object with its value, datum, referenced geometry and revision checked |
| E6 | Manufacturable | Checked against the actual geometry and process inputs for the confirmed route: tool reach, hole depth, wall thickness allowance, fixturing space |
| E7 | Traceable conclusions | Every engineering judgement resolves to valid evidence or a recomputable basis, including source text or algorithm, applicability, revision and artifact binding |

## 2. Requirements

| Item | Requirement |
|---|---|
| Operating system | Windows (SolidWorks is a Windows desktop COM application) |
| CAD | SolidWorks 2024 or 2026 SP01.1 (the versions that have been regression-tested); AutoCAD 2024 for the 2D side |
| Python | 3.10 or newer, 64-bit, matching the SolidWorks bitness |

## 3. Install and self-check

```powershell
# 1. Dependencies
pip install -r mcp-server\requirements.txt

# 2. Environment self-check: what is missing, which format it affects, how to install it
python scripts\cad_doctor.py
```

Once the self-check passes, add the MCP server to your client (DSH shown here; Claude Code and Cursor work the same, replace the path with your clone):

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

After connecting, call `solidworks_health_check` once to confirm this machine can reach SolidWorks.

**Do not run more than one SolidWorks MCP on the same machine.** The server serializes COM calls behind a global lock, and several processes competing for one COM connection will deadlock.

## 4. Four ways to use it

| Entry point | Good for | How to start |
|---|---|---|
| MCP Server | You already use an MCP-capable client and want the model to drive SolidWorks directly | `python mcp-server\server.py`, launched as a child process by the client |
| Skill | Your client can import a skill package | Load the repository root as a skill, see [SKILL.md](SKILL.md) |
| Desktop | You want a GUI: projects, task queue, review, preview, delivery packages | [apps/workbench-ui](apps/workbench-ui) (React + Tauri, the real client, with a 23-command Rust backend; you build it yourself with `npm install` and `cargo build`) or [apps/desktop](apps/desktop) (PySide6 prototype, CAD execution is mocked, useful only to look at the UI design) |
| DSH preset | You use DSH and want all 544 tools in one session | `python -B tools\dsh-preset\install_preset.py --apply`, see [docs/dsh-preset-sw-engineer.md](docs/dsh-preset-sw-engineer.md) |

> The desktop app runs its tasks through its own local worker (the `codex` command line) and **does not go through the MCP server**; the two are parallel entry points. Use MCP to batch-run the same capabilities; use the desktop app to manage tasks and delivery packages with a GUI.

### A first part from scratch

```text
1. Start the MCP server and confirm the client can list solidworks_* tools
2. Have the model run solidworks_read_document_units first, to confirm document units
3. Sketch -> add constraints -> extrude -> read back volume and bounding box
4. Build views and annotations only when you need drawings
```

Every step returns readings (volume, bounding box, body count, sketch constraint state). Look at the readings, not just at whether the call succeeded.

## 5. Scope and limits

`capabilities.yaml` is the single source of truth for capabilities, and every entry carries a level:

| Level | Meaning | Current |
|---|---|---|
| `verified` | Has real-machine run evidence on this project | 100 |
| `stitched` | Implementation follows official signatures, but lacks our own run evidence | 38 |
| `not_implemented` | Explicitly not done | 2 |

Domains held under controlled `pilot` (configuration families, sheet-metal U-profile flange and flat-pattern DXF, HSS rectangular weldment frames and cut lists, Simulation/FEA, Routing, complex surfaces, moulds) are marked item by item and are not treated as native complete delivery. Entries at `stitched` work, but you should verify their results yourself.

## 6. Repository layout

| Path | Contents |
|---|---|
| `mcp-server/` | MCP server and tool declarations (`server.py`, `tool_registry.py`, `tool_specs_batch*.py`) |
| `scripts/` | Capability implementation, one module per domain (`sw_part.py`, `sw_assembly.py`, `sw_drawing.py` and so on) |
| `tools/` | Command-line utilities: the real-machine guard `guard_run.py`, probes and generators |
| `docs/` | Knowledge base and explanatory documents |
| `tests/` | Tests |
| `apps/` | Desktop clients |
| `references/`, `subskills/`, `examples/` | Reference material, sub-skills, examples |
| `AI Solidworks/` | Local workspace for official documentation, models and screenshots (not committed) |

## 7. References and acknowledgements

At the start of the project we read through a set of public SolidWorks automation projects: their interface wrappers, test layering, error handling and understanding of the official API. That work decided which approaches were viable and which were dead ends. The projects surveyed are listed below by purpose. The licence column was verified in 2026-11 by reading each repository's `LICENSE` file, not by trusting README badges.

**Code or design used**

| Project | Licence | What was taken |
|---|---|---|
| `wzyn20051216/solidworks-automation-skill` | MIT | The project's original source. `mcp-server/server.py` is kept unchanged (45 tool implementations), and 49 `scripts/*.py` modules plus `subskills/` are built on from there |
| `microsoft/UFO` | MIT | The configuration-driven GUI input layer design (`input_text_api`, `input_text_enter`, `input_text_inter_key_pause`), used in `sw_gui_input.py` and `sw_jlcfa_fill.py`. The pattern is borrowed; the code is ours |
| `Eduardof0nt/Solidworks-MCP-Server` | MIT | Which two actions the mould domain needs (parting line, shut-off surface). Its method names do not exist in the official type library, so only the idea was taken and the implementation follows the official signatures |

**Evaluated, no code merged**

| Project | Licence | What was examined |
|---|---|---|
| `andrewbartels1/SolidworksMCP-python` | MIT | Comparison for tool grouping and parameter organisation |
| `vespo92/SolidworksMCP-TS` | MIT | The `mock-solidworks-adapter` test layering, macro-generator and several `.vba` samples |
| `Slacker-LLC/solidworks-mcp` | Apache-2.0 | Comparison of tool coverage. Nothing merged, so its NOTICE obligation is not triggered |

**Survey and cross-checking**

| Project | Licence | What was examined |
|---|---|---|
| `xarial/codestack` | MIT | View creation, document operations, assemblies, import/export, and its fault taxonomy |
| `angelsix/solidworks-api` | MIT | The SolidDNA template idea (avoiding template dialogs) |
| `deloarts/pyswx` | MIT | How to organise type-library wrappers |
| `painezeng/CSharpAndSolidWorks` | MIT | Geometry algorithms (self-intersection, convexity, area) and test parts |
| `alisamsam/Solidworks-MCP` | MIT | A corpus of 27 `.vbs` files, used to check VBScript-side usage |
| `delancy827/solidworks-skills` | MIT | Independent cross-check on parameter counts |
| `djlex83/solidworks-automation-skill` | MIT | The concise `VARIANT(VT_DISPATCH, None)` form |
| `Sakikooooo/solidworks-auto-modeling` | MIT | Distinguishing `Nothing` (scalar Dispatch) from `Empty` (Variant) |
| `Mochaxgcc/solidworks-ai-bridge` | MIT | Evidence for how positional parameters are passed |
| `guoleizhen717/solidworks-api-skill` | MIT | A counter-example: its claim that more than 12 parameters fails is wrong |
| `ZiChen-Ni/solidworks-com-automation-skill` | MIT | Minimal COM wrapper and Windows install script |
| `just1step/solidworks-mcp` | MIT | Comparison of tool coverage |
| `Cai-aa/CAD-Agent-Hub` | MIT | How agents and CAD are organised to work together |
| `kalyanpi4/pySW` | GPL-2.0 | Ideas read only, no code copied |
| `eyfel/mcp-server-solidworks` (SolidPilot) | AGPL | Ideas read only, no code copied. Its fork `Bennyco86/q3ds-solidworks-mcp` is also AGPL |
| `pedropaulovc/offline-solidworks-api-docs` | No licence | Pipeline idea read only. The local official-documentation library was inspired by it; its output is not distributed with this repository |
| `pengxiaoan/solidworks-build-mechanical-models` | No licence | Ideas read only |
| `walterkken/doc-driven-engineering-software-skills` | All rights reserved | Only the methodology of a documentation-driven directory structure was taken |

The SolidWorks API help and official examples are used daily as the basis for checking signatures, Remarks and call order. They are not open-source projects and are mentioned here only for completeness.

The authors and maintainers of the projects above made that experience readable, and this project avoided many detours because of it. Thanks to them. If any licence determination or attribution above is wrong, please open an issue and it will be corrected to match the facts.

## 8. Licence

MIT, see [LICENSE](LICENSE). Third-party code and licence obligations are in [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
