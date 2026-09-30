using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Web.Http;
using SolidworksExecution.Infrastructure;
using SolidworksExecution.Models;
using SolidworksExecution.Services;

namespace SolidworksExecution.Controllers
{
    [RoutePrefix("api/tool")]
    public class ToolController : ApiController
    {
        private readonly SolidWorksService _service;
        private readonly IOperationGuard _guard;

        public ToolController() : this(OperationGuard.Instance) { }

        public ToolController(IOperationGuard guard)
        {
            _guard = guard;
            _service = new SolidWorksService(guard);
        }

        // Read-only resync endpoint: returns the current authoritative state_version
        // WITHOUT a state_version check or increment. The adapter calls this to recover
        // from a desync (e.g. the execution server was restarted after a rebuild).
        [HttpGet]
        [Route("state")]
        public HttpResponseMessage GetState()
        {
            return Request.CreateResponse(HttpStatusCode.OK, new
            {
                stateVersion = _guard.GetCurrentStateVersion()
            });
        }

        // Health endpoint (P0.6). `~/` escapes the api/tool prefix → GET /health. Reports the server is
        // up, the current state_version, and whether SolidWorks COM is currently attachable (probed on the
        // STA thread — COM_ATTACH is lazy/per-request, so this is a fresh attach attempt) plus the active
        // document. Never 500s: a COM probe failure is reported as comAttached=false, not an error status.
        [HttpGet]
        [Route("~/health")]
        public HttpResponseMessage Health()
        {
            var info = new Dictionary<string, object>
            {
                ["status"] = "UP",
                ["stateVersion"] = _guard.GetCurrentStateVersion(),
                ["serverTimeUtc"] = DateTime.UtcNow.ToString("o"),
            };
            try
            {
                var com = StaExecutor.Instance.Run(() => _service.GetHealthInfo());
                foreach (var kv in com) info[kv.Key] = kv.Value;
            }
            catch (Exception ex)
            {
                info["comAttached"] = false;
                info["comError"] = ex.Message;
            }
            object attached;
            info.TryGetValue("comAttached", out attached);
            ExecLog.Write($"<- health UP comAttached={attached}");
            return Request.CreateResponse(HttpStatusCode.OK, info);
        }

        // Lifecycle bootstrap (ensure_ready). `~/` escapes the api/tool prefix → POST /ensure_ready.
        // POST because it is side-effecting: it launches SolidWorks via COM if it isn't running.
        // Distinct from /health (a read-only probe) — this one makes the environment ready. Does NOT
        // open/create a document. Runs on the STA thread (touches COM) and never 500s (a launch
        // failure is reported as comAttached=false). Not part of the state_version/idempotency
        // envelope — it's a lifecycle call, not a CAD operation.
        [HttpPost]
        [Route("~/ensure_ready")]
        public HttpResponseMessage EnsureReady()
        {
            var info = new Dictionary<string, object>
            {
                ["status"] = "UP",
                ["stateVersion"] = _guard.GetCurrentStateVersion(),
                ["serverTimeUtc"] = DateTime.UtcNow.ToString("o"),
            };
            try
            {
                // ★ health is the most common victim of a stuck modal dialog (it touches COM) — sweep first.
                DialogGuard.Sweep(force: true);
                var com = StaExecutor.Instance.Run(() => _service.EnsureReady());
                foreach (var kv in com) info[kv.Key] = kv.Value;
            }
            catch (Exception ex)
            {
                info["comAttached"] = false;
                info["ensureError"] = ex.Message;
            }
            object attached, launched;
            info.TryGetValue("comAttached", out attached);
            info.TryGetValue("swLaunched", out launched);
            ExecLog.Write($"<- ensure_ready UP comAttached={attached} swLaunched={launched}");
            return Request.CreateResponse(HttpStatusCode.OK, info);
        }

        [HttpPost]
        [Route("execute")]
        public HttpResponseMessage Execute([FromBody] ToolRequest request)
        {
            if (request == null || string.IsNullOrEmpty(request.OperationId) || string.IsNullOrEmpty(request.Tool))
                return Request.CreateResponse(HttpStatusCode.BadRequest,
                    new { error = "operation_id and tool are required." });

            ExecLog.Write($"-> {request.Tool} op={request.OperationId} sv={request.StateVersion}");

            ExecutionResponse response;

            try
            {
                // ★★ DIALOG GUARD. Decision is by control ID (structure), not by button text —
                //    see DialogGuard's header for why text matching was wrong.
                //    If it finds a dialog it will not auto-answer, that is reported to the caller
                //    instead of silently hanging or pretending success.
                int swept = DialogGuard.Sweep(force: true);
                if (swept > 0) ExecLog.Write($"   dialog-guard acted {swept}: {DialogGuard.LastReport}");
                string needsHuman = DialogGuard.NeedsHuman();
                if (needsHuman.Length > 0)
                {
                    ExecLog.Write($"   dialog-guard NEEDS HUMAN: {needsHuman}");
                    return Request.CreateResponse(HttpStatusCode.OK, new ExecutionResponse
                    {
                        OperationId = request.OperationId,
                        Status = "FAILED",
                        StateVersion = _guard.GetCurrentStateVersion(),
                        Error = new ExecutionError { Code = "NEEDS_HUMAN_DIALOG", Message = needsHuman }
                    });
                }

                response = StaExecutor.Instance.Run(() => Dispatch(request));

                int after = DialogGuard.Sweep(force: true);
                if (after > 0) ExecLog.Write($"   dialog-guard post-swept {after}: {DialogGuard.LastReport}");
            }
            catch (System.Exception ex)
            {
                // ★ If SolidWorks raised a dialog while the call was in flight, that is very likely why it
                //   failed. Clear it and say so, instead of leaking an opaque 500 to the caller.
                int rescued = DialogGuard.Sweep(force: true);
                if (rescued > 0)
                {
                    ExecLog.Write($"<- {request.Tool} FAILED_CAUSED_BY_DIALOG: {DialogGuard.LastReport}");
                    return Request.CreateResponse(HttpStatusCode.OK, new ExecutionResponse
                    {
                        OperationId = request.OperationId,
                        Status = "FAILED",
                        StateVersion = _guard.GetCurrentStateVersion(),
                        Error = new ExecutionError
                        {
                            Code = "BLOCKED_BY_MODAL_DIALOG",
                            Message = "SolidWorks was showing a modal dialog (" + DialogGuard.LastReport
                                    + "). It has been dismissed automatically — the call can be retried."
                        }
                    });
                }
                ExecLog.Write($"<- {request.Tool} UNHANDLED {ex.GetType().Name}: {ex.Message}\n{ex.StackTrace}");
                return Request.CreateResponse(HttpStatusCode.InternalServerError,
                    new { error = ex.Message });
            }

            if (response == null)
            {
                ExecLog.Write($"<- {request.Tool} UNKNOWN_TOOL");
                return Request.CreateResponse(HttpStatusCode.BadRequest,
                    new { error = $"Unknown tool: {request.Tool}" });
            }

            if (response.Status == "FAILED")
                ExecLog.Write($"<- {request.Tool} FAILED {response.Error?.Code}: {response.Error?.Message}");
            else
                ExecLog.Write($"<- {request.Tool} {response.Status} sv={response.StateVersion}");

            return Request.CreateResponse(HttpStatusCode.OK, response);
        }

        // Routes a tool request to its service method. Runs on the STA thread (see Execute).
        // Returns null for an unknown tool so the caller can emit the BadRequest response.
        /// <summary>
        /// bearing_test — 判别实验：AddBearingLoad(坐标系, 面, err) 只有 3 个参数、
        /// 【不传 DispArray】。若它能成功，就证明 AddRestraint 24 轮失败的症结是"传几何数组"，
        /// 而不是许可问题或研究状态。UI 文本输入不可靠时这也是更稳的建载荷路径。
        /// </summary>
        private static ExecutionResponse BearingTestHarness(ToolRequest request)
        {
            string part = @"D:\AI\SW\AI Solidworks\模型\主轴壳体_Housing.sldprt";
            double loadN = 10000.0;
            try
            {
                var jo = request.Params as Newtonsoft.Json.Linq.JObject;
                if (jo != null)
                {
                    if (jo["part_path"] != null) part = (string)jo["part_path"];
                    if (jo["load_n"] != null) loadN = (double)jo["load_n"];
                }
            }
            catch { }

            string log;
            try { log = BearingTest.Run(part, loadN); }
            catch (Exception ex) { log = "EXCEPTION: " + ex.GetType().Name + ": " + ex.Message; }

            return new ExecutionResponse
            {
                OperationId = request.OperationId,
                Status = "COMPLETED",
                CadState = new Models.CadState
                {
                    StateVersion = 0,
                    ActiveDocument = "主轴壳体_Housing.sldprt",
                    DocumentType = "Part",
                    Features = new System.Collections.Generic.List<string>(log.Split('\n'))
                }
            };
        }

        private ExecutionResponse Dispatch(ToolRequest request)
        {
            switch (request.Tool)
            {
                case "open_new_part":          return _service.OpenNewPart(request);
                case "open_document":          return _service.OpenDocument(request);
                case "create_sketch":          return _service.CreateSketch(request);
                case "add_sketch_entity":      return _service.AddSketchEntity(request);
                case "add_sketch_entities":    return _service.AddSketchEntities(request);
                case "add_dimension":          return _service.AddDimension(request);
                case "add_sketch_constraint":  return _service.AddSketchConstraint(request);
                case "add_edge_feature":       return _service.AddEdgeFeature(request);
                case "create_rib":             return _service.CreateRib(request);
                case "create_drawing":         return _service.CreateDrawing(request);
                case "add_drawing_view":       return _service.AddDrawingView(request);
                case "add_flat_pattern_view":  return _service.AddFlatPatternView(request);
                case "add_drawing_dimension":  return _service.AddDrawingDimension(request);
                case "auto_dimension_drawing": return _service.AutoDimensionDrawing(request);
                case "auto_center_marks":      return _service.AutoCenterMarks(request);
                case "add_hole_callout":       return _service.AddHoleCallout(request);
                case "add_section_view":       return _service.AddSectionView(request);
                case "save_document":          return _service.SaveDocument(request);
                case "export_document":        return _service.ExportDocument(request);
                case "batch_export":           return _service.BatchExport(request);
                case "extrude_feature":        return _service.ExtrudeFeature(request);
                case "verify_state":           return _service.VerifyState(request);
                case "close_document":         return _service.CloseDocument(request);
                case "analyze_model":          return _service.AnalyzeModel(request);
                case "analyze_slddrw_test":    return _service.AnalyzeDrawing(request);
                case "get_selection":          return _service.GetSelection(request);
                case "edit_sketch":            return _service.EditSketch(request);
                case "add_reference_geometry": return _service.AddReferenceGeometry(request);
                case "create_pattern":         return _service.CreatePattern(request);
                case "set_part_material":      return _service.SetPartMaterial(request);
                case "sheet_metal_feature":    return _service.SheetMetalFeature(request);
                case "modify_dimension":       return _service.ModifyDimension(request);
                case "edit_feature":           return _service.EditFeature(request);
                case "activate_document":      return _service.ActivateDocument(request);
                case "analyze_assembly":       return _service.AnalyzeAssembly(request);
                case "open_new_assembly":      return _service.OpenNewAssembly(request);
                case "insert_component":       return _service.InsertComponent(request);
                case "add_mate":               return _service.AddMateTool(request);
                case "save_body_as_part":      return _service.SaveBodyAsPart(request);
                // ---- capability extension batch 2026-09-27 ----
                case "bom_from_assembly":      return _service.BomFromAssembly(request);
                case "list_standard_parts":    return _service.ListStandardParts(request);
                case "insert_standard_part":   return _service.InsertStandardPart(request);
                case "lcsc_fetch_step":        return _service.LcscFetchStep(request);
                case "motion_study":           return _service.MotionStudy(request);
                case "topology_optimize":      return _service.TopologyOptimize(request);
        case "solve_static":               return _service.SolveStatic(request);   // ★ 设材料+网格+求解+读.OUT
        case "probe_add_restraint":          return _service.ProbeAddRestraint(request);   // ★★ SAFEARRAY 绕行实验
        case "layout_drawing":             return _service.LayoutDrawing(request);   // ★ 图纸自适应布局
        case "add_surface_finish":        return _service.AddSurfaceFinish(request);   // ★ 粗糙度符号
        case "import_study_features":    return _service.ImportStudyFeaturesTool(request);  // ★★ 绕开 DispArray 的正路
        case "read_sim_feature":       return _service.ReadSimFeature(request);   // ★ 读 UI 建的力特征数据
        case "run_macro":              return _service.RunMacro(request);   // ★ VBA 主线程后端
                case "design_check":       return _service.DesignCheck(request);
                case "product_probe":      return _service.ProductProbe(request);
                case "electrical":             return _service.ElectricalProbe(request);
                case "bearing_test":           return BearingTestHarness(request);
                default:                       return null;
            }
        }
    }
}


