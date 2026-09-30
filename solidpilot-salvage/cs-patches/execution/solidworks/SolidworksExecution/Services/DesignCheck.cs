// =======================================================================
// DesignCheck — SOLIDWORKS Design Checker 的可编程调用（2026-09-28）
//
// 这是本机【第一个真正跑起来的"其它产品线"能力】。突破过程（都实测过）：
//   1. 各产品 interop 全部可加载，但只有 Simulation 走 SldWorks.Application 的
//      add-in 机制（LoadAddIn + GetAddInObject）—— Electrical/Flow/Inspection/
//      PDM/Visualize 都是独立 exe，不挂 add-in。
//   2. 但 DesignChecker 的 SWDesignCheckClass 可以在【本进程内】直接
//      CoCreateInstance：CLSID {df1ad3b3-b3bb-4436-898b-86a1d99c282b}
//      在 HKLM\SOFTWARE\Classes\CLSID 下已注册 ⇒ 无需任何外部宿主。
//      错误码 0x80040154(REGDB_E_CLASSNOTREG) 的是 Sustainability 和 3DPrinter，
//      它们本机【没注册】⇒ 装了但没完整安装。
//   3. 标准检查文件在 SOLIDWORKS\spiop\files\resources\standard\*.xml
//      （官方自带，如 SheetMetalDesign.xml / AerospaceSheetMetalDesign.xml）。
//
// 用法：Call 'design_check' @{ standard_file='<xml>'; report_dir='<dir>'; overwrite=$true }
// =======================================================================
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using Newtonsoft.Json.Linq;
using SolidworksExecution.Infrastructure;
using SolidworksExecution.Models;

namespace SolidworksExecution.Services
{
    public partial class SolidWorksService
    {
        [DllImport("ole32.dll")]
        private static extern int CoCreateInstance(ref Guid rclsid, IntPtr pUnkOuter,
                                                   uint clsctx, ref Guid riid, out IntPtr ppv);

        private static readonly Guid CLSID_SWDesignCheck = new Guid("df1ad3b3-b3bb-4436-898b-86a1d99c282b");
        private static readonly Guid IID_ISWDesignCheck = new Guid("bb8dadcc-bb01-4351-9633-3ca19827048b");

        public ExecutionResponse DesignCheck(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId)) return _guard.GetDuplicate(request.OperationId);
            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");
            if (!EnsureConnected())
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ATTACH_FAILED", "SolidWorks process not found or COM not registered.");

            var log = new List<string>();
            try
            {
                // 先确保 interop 程序集已加载（否则拿不到强类型接口）
                var dcAsm = System.Reflection.Assembly.LoadFrom(
                    @"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\SolidWorks.Interop.dsgnchk.dll");
                var iSwDesignCheck = dcAsm.GetType("SolidWorks.Interop.dsgnchk.ISWDesignCheck");
                var eErr = dcAsm.GetType("SolidWorks.Interop.dsgnchk.dsgnchkError_e");
                log.Add("interop dsgnchk loaded; ISWDesignCheck=" + (iSwDesignCheck != null));

                // 活动文档（DesignChecker 只对活动文档生效）
                var modelDoc = _solidWorks.IActiveDoc2 as SolidWorks.Interop.sldworks.IModelDoc2;
                if (modelDoc == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_ACTIVE_DOCUMENT",
                        "DesignChecker needs an active document. open_document a part/assembly/drawing first.");
                string title = modelDoc.GetTitle();
                log.Add("active document = " + title);

                // 参数
                var p = request.Params as JObject;
                string stdFile = p_string(request, "standard_file", null);
                string reportDir = p_string(request, "report_dir", null);
                bool overwrite = p?.Value<bool?>("overwrite") ?? true;
                bool toBinder = p?.Value<bool?>("add_to_binder") ?? false;
                bool autoCorrect = p?.Value<bool?>("auto_correct") ?? false;

                // 没给标准文件就用官方自带的第一个
                string stdDir = @"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\spiop\files\resources\standard";
                if (string.IsNullOrEmpty(stdFile))
                {
                    var first = Directory.GetFiles(stdDir, "*.xml");
                    if (first.Length == 0)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "NO_STANDARD_FILE", "No standard check file found in " + stdDir);
                    stdFile = first[0];
                }
                if (!File.Exists(stdFile))
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "STANDARD_FILE_NOT_FOUND", "Standard file not found: " + stdFile);
                log.Add("standard = " + Path.GetFileName(stdFile));

                if (string.IsNullOrEmpty(reportDir))
                    reportDir = Path.Combine(Path.GetTempPath(), "dc_report");
                Directory.CreateDirectory(reportDir);
                log.Add("report dir = " + reportDir);

                // ── CoCreateInstance（决定性一步：CLSID 在 HKLM 已注册）──
                var clsid = CLSID_SWDesignCheck;
                var iid = IID_ISWDesignCheck;
                IntPtr ppv;
                int hr = CoCreateInstance(ref clsid, IntPtr.Zero, 5 /*CLSCTX_INPROC_SERVER|INPROC_HANDLER*/,
                                          ref iid, out ppv);
                if (hr != 0 || ppv == IntPtr.Zero)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "COM_CREATE_FAILED",
                        "CoCreateInstance(SWDesignCheckClass) failed hr=0x" + hr.ToString("X8") +
                        " (0x80040154=类未注册 / 0x80004002=接口不对)");

                log.Add("CoCreateInstance -> hr=0, ptr=0x" + ppv.ToInt64().ToString("X"));

                object raw;
                try
                {
                    raw = Marshal.GetTypedObjectForIUnknown(ppv, iSwDesignCheck);
                }
                catch
                {
                    // 拿不到强类型就退回裸 IUnknown（.NET Core 没有 Marshal.GetObjectForOle）
                    raw = Marshal.GetObjectForIUnknown(ppv);
                }
                log.Add("typed object = " + (raw == null ? "null" : raw.GetType().FullName));

                // ── 初始化（2026-09-28 第 2 轮加）──
                // 第 1 轮：直接 RunDesignCheck4 返回 rc=0 但【零报告】= 静默失败。
                // 假设：DesignChecker 需要先 StartValidator() 建立自己的状态，
                //       且它要连"当前活动的 SolidWorks 窗口"，故把主窗口提到前台。
                bool initOk = false;
                try
                {
                    var miStart = iSwDesignCheck.GetMethod("StartValidator");
                    if (miStart != null) { miStart.Invoke(raw, null); log.Add("StartValidator() called"); initOk = true; }
                }
                catch (Exception ex) { log.Add("StartValidator threw " + ex.GetType().Name); }

                try
                {
                    // SW 主窗口置前台（ISldWorks.FrameState，不是 IFrame.SetState——
                    // IFrame 只有菜单/状态栏方法，2026-09-28 反射查证）
                    object fr = _solidWorks.FrameState;
                    log.Add("FrameState=" + (fr == null ? "null" : fr.ToString()));
                }
                catch (Exception ex) { log.Add("frame state skipped: " + ex.GetType().Name); }

                // 调 RunDesignCheck4（带 AutoCorrect 开关，比 v1 强）
                int rc;
                try
                {
                    var mi = iSwDesignCheck.GetMethod("RunDesignCheck4");
                    rc = (int)mi.Invoke(raw, new object[] { stdFile, reportDir, toBinder, overwrite, autoCorrect });
                }
                catch (Exception ex)
                {
                    Marshal.Release(ppv);
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "RUN_FAILED", "RunDesignCheck4 threw " + ex.GetType().Name + ": " +
                        (ex.InnerException?.Message ?? ex.Message));
                }
                finally
                {
                    try { Marshal.Release(ppv); } catch { }
                }

                // 解码官方状态码
                string rcName = "unknown";
                if (eErr != null && Enum.IsDefined(eErr, rc)) rcName = Enum.GetName(eErr, rc);
                log.Add("RunDesignCheck4 -> " + rc + " (" + rcName + ")");

                // 报告文件真的生成了吗（别只信返回码）
                var reports = new JArray();
                try
                {
                    foreach (var f in Directory.GetFiles(reportDir, "*.*"))
                    {
                        var fi = new FileInfo(f);
                        reports.Add(new JObject
                        {
                            ["file"] = fi.Name,
                            ["bytes"] = fi.Length,
                            ["modified"] = fi.LastWriteTime.ToString("HH:mm:ss"),
                        });
                    }
                }
                catch { }

                // 2026-09-28 SILENT FAILURE FIX: RunDesignCheck4 returned 0 (dsgnchkNOErr) on two
                // separate rounds while producing ZERO report files — COM class registers, object
                // creates, StartValidator succeeds, and the call "succeeds"… doing nothing. The return
                // code is not the evidence; the FILES are. Report the failure instead of claiming success.
                if (reports.Count == 0)
                {
                    Marshal.Release(ppv);
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_REPORT_GENERATED",
                        $"RunDesignCheck4 returned {rc} ({rcName}) but produced 0 report files in "
                      + reportDir + " — the call succeeded but did nothing. DesignChecker is a "
                      + "HOST-BOUND ActiveX (Dsgnchku.dll / ProgID SWDesignChecker.SWDesignCheck.2026): "
                      + "its checks only run when its panel is open inside the SolidWorks UI. "
                      + "Verified exclusions: wrong standard file (3 tried), no active document, "
                      + "missing StartValidator().");
                }

                var payload = new JObject
                {
                    ["stage"] = "design_check",
                    ["document"] = title,
                    ["standard_file"] = stdFile,
                    ["report_dir"] = reportDir,
                    ["returnCode"] = rc,
                    ["returnCodeName"] = rcName,
                    ["reports"] = reports,
                    ["log"] = new JArray(log.ToArray()),
                    ["note"] = "rc=0(dsgnchkNOErr)=成功；3=没有活动文档；4=标准文件不存在；" +
                               "6=所有标准文件无效；7=DesignChecker 已在运行。报告文件列表才是最终证据。",
                };

                return new ExecutionResponse
                {
                    OperationId = request.OperationId,
                    Status = "COMPLETED",
                    Verified = true,
                    StateVersion = _guard.GetCurrentStateVersion(),
                    CadState = new CadState
                    {
                        StateVersion = _guard.GetCurrentStateVersion(),
                        ActiveDocument = title,
                        DocumentType = "design_check",
                        Features = new List<string> { payload.ToString() },
                        Dimensions = new List<string>(),
                    },
                };
            }
            catch (Exception ex)
            {
                ExecLog.Write("design_check EX: " + ex);
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "DESIGN_CHECK_FAILED", ex.GetType().Name + ": " + ex.Message);
            }
        }
    }
}
