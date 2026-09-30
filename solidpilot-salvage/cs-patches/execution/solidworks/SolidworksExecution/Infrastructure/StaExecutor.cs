using System;
using System.Collections.Concurrent;
using System.Threading;

namespace SolidworksExecution.Infrastructure
{
    /// <summary>
    /// Runs delegates on a single, long-lived, dedicated STA thread. (P0.1)
    ///
    /// SolidWorks COM objects must be called from an STA apartment. OWIN / Web API request
    /// threads are MTA, and while COM marshaling lets lightweight calls (e.g. FeatureExtrusion3)
    /// limp across the apartment boundary, heavier or more apartment-sensitive calls fail off-STA:
    /// InsertSheetMetalBaseFlange2 silently returned null and add_edge_feature (edge fillet)
    /// deadlocked (ContextSwitchDeadlock). Routing ALL COM-touching work through one STA thread —
    /// including the GetActiveObject attach — makes the RCW live on the STA, fixing both.
    ///
    /// A single worker thread also serializes COM access, which suits the single-writer,
    /// process-global state model the OperationGuard already assumes.
    /// </summary>
    public sealed class StaExecutor
    {
        public static readonly StaExecutor Instance = new StaExecutor();

        private readonly BlockingCollection<Action> _queue = new BlockingCollection<Action>();

        private StaExecutor()
        {
            var thread = new Thread(Worker)
            {
                IsBackground = true,
                Name = "SolidWorksStaThread"
            };
            thread.SetApartmentState(ApartmentState.STA);
            thread.Start();
        }

        [System.Runtime.InteropServices.StructLayout(System.Runtime.InteropServices.LayoutKind.Sequential)]
        private struct MSG
        {
            public IntPtr hwnd; public uint message; public IntPtr wParam;
            public IntPtr lParam; public uint time; public int x; public int y;
        }

        [System.Runtime.InteropServices.DllImport("user32.dll")]
        private static extern bool PeekMessage(out MSG msg, IntPtr hwnd, uint min, uint max, uint remove);
        [System.Runtime.InteropServices.DllImport("user32.dll")]
        private static extern bool TranslateMessage(ref MSG msg);
        [System.Runtime.InteropServices.DllImport("user32.dll")]
        private static extern IntPtr DispatchMessage(ref MSG msg);

        private const uint PM_REMOVE = 0x0001, PM_NOREMOVE = 0x0000;

        /// <summary>
        /// Service the STA message queue.
        ///
        /// WHY THIS EXISTS (2026-09-27): the worker loop below used to be a bare
        /// foreach over the queue with no message pump at all. That is fine for purely
        /// in-process COM, but `study` / `lrm` come from ISldWorks.GetAddInObject, so they
        /// live in the SOLIDWORKS process — every call on them is a cross-process RPC whose
        /// inbound messages (callbacks, marshal replies) must be delivered on THIS thread.
        /// With no pump they are never delivered, the proxy state goes inconsistent, and the
        /// next call dereferences a stale pointer.
        ///
        /// The symptom that gave it away: MeshAndRun() succeeded while CreateMesh() — the
        /// same meshing work — crashed. Not a call-shape error; "needs a callback" vs
        /// "doesn't need a callback". Pumping between jobs, and (via DrainQueue) inside the
        /// wait, removes that asymmetry.
        /// </summary>
        private void PumpMessages()
        {
            MSG msg;
            while (PeekMessage(out msg, IntPtr.Zero, 0, 0, PM_REMOVE))
            {
                TranslateMessage(ref msg);
                DispatchMessage(ref msg);
            }
        }

        private void Worker()
        {
            // Install an IMessageFilter FIRST. While this thread is blocked inside a
            // cross-process COM call, our own PumpMessages() cannot run. Without a filter
            // COM treats an undeliverable inbound message as REJECTED and tears the proxy
            // down; with it, COM retries the delivery as soon as the thread pumps again.
            // This is the standard OLE-hosting incantation (what VBA/Add-in hosts do).
            OleMessageFilter.Install();

            while (true)
            {
                Action work;
                if (_queue.TryTake(out work))
                {
                    try { work(); }
                    catch { /* the job's own captured exception is what callers see */ }
                }
                PumpMessages();
                if (work == null) Thread.Sleep(1);
            }
        }

        /// <summary>Marshal <paramref name="func"/> onto the STA thread and block until it returns.</summary>
        public T Run<T>(Func<T> func)
        {
            T result = default(T);
            Exception captured = null;
            using (var done = new ManualResetEventSlim(false))
            {
                // ★★ 2026-09-28 ROOT-CAUSE FIX for "the dialog guard never ran".
                //   The previous design swept dialogs BEFORE and AFTER the call, from the caller's
                //   thread. A modal dialog raised BY the call itself lands in between:
                //       sweep (clean) -> COM call -> dialog pops -> RPC hangs -> thread never returns
                //   => the after-sweep is unreachable, and the request dies with an opaque timeout while
                //      the dialog sits there. This watcher sweeps for the WHOLE duration of the call.
                using (var stop = new ManualResetEventSlim(false))
                {
                    var watcher = new Thread(() =>
                    {
                        while (!stop.Wait(500))
                        {
                            try { DialogGuard.Sweep(force: true); } catch { /* never kill the caller */ }
                        }
                    })
                    { IsBackground = true, Name = "DialogGuardWatcher" };
                    watcher.Start();
                    try
                    {
                        _queue.Add(() =>
                        {
                            try { result = func(); }
                            catch (Exception ex) { captured = ex; }
                            finally { done.Set(); }
                        });
                        done.Wait();
                    }
                    finally
                    {
                        stop.Set();
                        watcher.Join(2000);
                    }
                }
            }
            if (captured != null)
                throw new InvalidOperationException("STA execution failed: " + captured.Message, captured);
            return result;
        }
    }
}
