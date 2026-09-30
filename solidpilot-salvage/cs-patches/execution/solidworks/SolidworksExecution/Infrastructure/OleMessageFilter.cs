using System;
using System.Runtime.InteropServices;

namespace SolidworksExecution.Infrastructure
{
    /// <summary>
    /// IMessageFilter is NOT in the .NET BCL — it has to be declared by hand against the
    /// COM interface of the same name (objbase.h / oletl.h). Declared here so the filter
    /// can be handed to CoRegisterMessageFilter.
    /// </summary>
    [ComImport, Guid("00000016-0000-0000-C000-000000000046"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    internal interface IMessageFilter
    {
        [PreserveSig] uint HandleInComingCall(uint dwCallType, IntPtr hTaskCaller,
                                              uint dwTickCount, IntPtr lpInfo);
        [PreserveSig] uint RetryRejectedCall(IntPtr hTaskCallee, uint dwTickCount, uint dwRejectType);
        [PreserveSig] uint MessagePending(IntPtr hTaskCallee, uint dwTickCount, uint dwMsgPending);
    }

    /// <summary>
    /// IMessageFilter for the STA worker thread (2026-09-27).
    ///
    /// The problem: StaExecutor's worker blocks inside cross-process COM calls
    /// (study/lrm live in the SOLIDWORKS process). While blocked, the thread cannot
    /// service its message queue, so OLE cannot deliver inbound COM messages. The
    /// default behaviour is to REJECT those messages, which poisons the proxy — the
    /// next call then dereferences stale state and the process dies with
    /// AccessViolation. That is exactly the pattern observed: MeshAndRun() worked
    /// while CreateMesh() — the same meshing work — crashed.
    ///
    /// The fix: filter returns SERVERCALL_RETRYAWAIT for undeliverable calls, so OLE
    /// keeps them queued until PumpMessages() runs. This is the standard incantation
    /// for any OLE host (Word/Excel automation, SolidWorks add-ins, VBA).
    /// </summary>
    [ComVisible(true)]
    internal sealed class OleMessageFilter : IMessageFilter
    {
        // OLE constants (oletl.h)
        private const uint SERVERCALL_RETRYAWAIT = 0x00000001;
        private const uint SERVERCALL_ACCEPTED   = 0x00000000;
        private const uint SERVERCALL_RETRYLATER = 0x00000004;
        private const uint SERVERCALL_RETRYDENIED = 0x00000003;
        private const uint PENDINGMSG = 0x00000001;

        [DllImport("ole32.dll")]
        private static extern int CoRegisterMessageFilter(IMessageFilter newFilter, out IMessageFilter oldFilter);

        private static OleMessageFilter _installed;

        internal static void Install()
        {
            if (_installed != null) return;
            var f = new OleMessageFilter();
            IMessageFilter old;
            int hr = CoRegisterMessageFilter(f, out old);
            if (hr == 0) _installed = f;
        }

        public uint HandleInComingCall(uint dwCallType, IntPtr hTaskCaller, uint dwTickCount,
                                        IntPtr lpInfo)
            => SERVERCALL_ACCEPTED;

        public uint RetryRejectedCall(IntPtr hTaskCallee, uint dwTickCount, uint dwRejectType)
        {
            // RETRYLATER = the message is queued but not yet deliverable. Answering
            // RETRYAWAIT makes OLE hold the caller until we next pump, instead of
            // rejecting it and tearing the proxy down.
            return dwRejectType == SERVERCALL_RETRYLATER
                 ? SERVERCALL_RETRYAWAIT
                 : SERVERCALL_RETRYDENIED;
        }

        public uint MessagePending(IntPtr hTaskCallee, uint dwTickCount, uint dwMsgPending)
            => dwMsgPending == PENDINGMSG ? PENDINGMSG : SERVERCALL_ACCEPTED;
    }
}
