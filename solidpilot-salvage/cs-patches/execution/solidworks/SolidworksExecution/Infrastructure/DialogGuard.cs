using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

namespace SolidworksExecution.Infrastructure
{
    /// <summary>
    /// ★★ 2026-09-28 — Modal-dialog guard (the root-cause fix for "tool just returns ERR").
    ///
    /// THE MECHANISM: SolidWorks is an out-of-process COM server. A MODAL dialog (#32770) stops it
    /// pumping RPC, so the cross-process COM call our tool is blocked inside HANGS — the caller sees
    /// an opaque 500 and the log says nothing useful. A message pump in OUR STA thread does not help:
    /// the pump is ours, the blocked call is an outbound RPC, and the dialog belongs to SLDWORKS.exe.
    ///
    /// ★★★ DECISION BY CONTROL ID, NOT BY TEXT (2026-09-28, after the user called this out).
    /// The first version matched on the button TEXT ("保存"/"全部保存"). That is wrong: a dialog the
    /// guard has never seen falls through to WM_CLOSE, and WM_CLOSE on a "do you want to save?" prompt
    /// means CANCEL — it silently destroys the user's work. Observed: the guard closed
    /// "您想保存 Simulation 数据吗?" by X, i.e. answered 否, because the text did not contain 保存.
    ///
    /// Button control IDs are a STRUCTURAL, language-independent property of a Win32 dialog:
    ///     IDYES(6) / IDNO(7) / IDOK(1) / IDCANCEL(2) / IDABORT(3) / IDRETRY(4) / IDIGNORE(5)
    /// Policy, and it generalises to dialogs we have never seen:
    ///   · IDYES present          → answer Yes  (= keep the user's work)
    ///   · else IDOK present      → press OK
    ///   · else IDNO is the ONLY affirmative action → press No  (nothing is being offered to keep)
    ///   · else IDCANCEL only     → ★ DO NOT TOUCH IT. Report it and let the human decide.
    ///   · no recognisable buttons → ★ DO NOT TOUCH IT. Report it.
    /// The last two are the important ones: "I don't know" must never degrade into "press X".
    /// </summary>
    public static class DialogGuard
    {
        public const int IDOK = 1, IDCANCEL = 2, IDABORT = 3, IDRETRY = 4, IDIGNORE = 5, IDYES = 6, IDNO = 7;
        private const uint WM_COMMAND = 0x0111;
        private const uint WM_CLOSE = 0x0010;

        private delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

        // ★ CRITICAL: every W-suffixed import MUST declare CharSet.Unicode, or the CLR marshals it as
        // ANSI and the buffer comes back holding only the FIRST CHARACTER (GetClassNameW returned
        // "#32770" as "#"). That is why an earlier version of this guard silently matched nothing.
        [DllImport("user32.dll")] private static extern bool EnumWindows(EnumWindowsProc cb, IntPtr p);
        [DllImport("user32.dll")] private static extern bool EnumChildWindows(IntPtr parent, EnumWindowsProc cb, IntPtr p);
        [DllImport("user32.dll", CharSet = CharSet.Unicode, EntryPoint = "GetWindowTextW")]
        private static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
        [DllImport("user32.dll", CharSet = CharSet.Unicode, EntryPoint = "GetClassNameW")]
        private static extern int GetClassNameW(IntPtr h, StringBuilder s, int n);
        [DllImport("user32.dll")] private static extern bool IsWindowVisible(IntPtr h);
        [DllImport("user32.dll")] private static extern int GetDlgCtrlID(IntPtr h);
        [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
        [DllImport("user32.dll")] private static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, IntPtr l);

        private static DateTime _lastSweep = DateTime.MinValue;
        private static DateTime _untouchableAt = DateTime.MinValue;   // ★ when the report was produced
        private static readonly List<string> _untouchable = new List<string>();

        /// <summary>Dialogs the guard found but deliberately did NOT click (human decision needed).</summary>
        public static List<string> Untouchable => new List<string>(_untouchable);
        public static string LastReport { get; private set; } = "";

        private sealed class Dlg
        {
            public IntPtr H;
            public string Title = "";
            public HashSet<int> ButtonIds = new HashSet<int>();
            public List<string> ButtonTexts = new List<string>();
        }

        private static List<Dlg> Scan()
        {
            var res = new List<Dlg>();
            var pids = new HashSet<uint>();
            foreach (var p in Process.GetProcessesByName("SLDWORKS")) pids.Add((uint)p.Id);
            if (pids.Count == 0) return res;

            EnumWindows((h, _) =>
            {
                uint pid; GetWindowThreadProcessId(h, out pid);
                if (!pids.Contains(pid) || !IsWindowVisible(h)) return true;
                var cls = new StringBuilder(256); GetClassNameW(h, cls, 256);
                // ★★ 2026-09-28 THIRD false positive found: SolidWorks' own "swWelcomeScreen" welcome
                //    window (and "SysShadow") are top-level, visible, button-less windows that the old
                //    guard counted as "unrecognised dialog" and then REFUSED to answer — which blocked
                //    every tool call. A real dialog is #32770; anything else is not one.
                string cn = cls.ToString();
                if (cn != "#32770") return true;             // structural, language-independent
                var t = new StringBuilder(512); GetWindowTextW(h, t, 512);
                var d = new Dlg { H = h, Title = t.ToString() };
                EnumChildWindows(h, (c, __) =>
                {
                    var cc = new StringBuilder(128); GetClassNameW(c, cc, 128);
                    if (cc.ToString() == "Button")
                    {
                        d.ButtonIds.Add(GetDlgCtrlID(c));
                        var ct = new StringBuilder(256); GetWindowTextW(c, ct, 256);
                        if (ct.Length > 0) d.ButtonTexts.Add(ct.ToString());
                    }
                    return true;
                }, IntPtr.Zero);
                res.Add(d);
                return true;
            }, IntPtr.Zero);
            return res;
        }

        /// <summary>Decide by control ID only. Returns the button to press, or 0 for "do not touch".
        /// The ID-0 "确定/OK" case is the one documented exception: some SolidWorks dialogs are built from
        /// MFC pages whose button carries NO standard control ID (GetDlgCtrlID returns 0). There, and ONLY
        /// when the dialog has exactly one button, pressing it is a pure acknowledgement — it cannot
        /// choose between "save" and "discard" because there is no other choice to make.</summary>
        private static int Decide(Dlg d)
        {
            if (d.ButtonIds.Contains(IDYES)) return IDYES;      // "keep my work"
            if (d.ButtonIds.Contains(IDOK)) return IDOK;        // acknowledgement
            // Only a "no" is offered and nothing to keep -> the safe answer is No, not X.
            if (d.ButtonIds.Contains(IDNO) && !d.ButtonIds.Contains(IDOK)) return IDNO;
            // Fallback for ID-less dialogs: exactly ONE button and it reads OK/确定/确定(&O).
            // Safe because a single-button dialog offers no destructive alternative.
            if (d.ButtonIds.Count == 1 && d.ButtonTexts.Count == 1)
            {
                string t = d.ButtonTexts[0] ?? "";
                if (t.Contains("确定") || t.StartsWith("OK") || t.StartsWith("确定"))
                    return -1;                                   // -1 = "press the only button"
            }
            return 0;   // ★ unknown / cancel-only / no standard buttons => do not touch
        }

        public static int Sweep(bool force = false)
        {
            if (!force && (DateTime.UtcNow - _lastSweep).TotalMilliseconds < 750) return 0;
            _lastSweep = DateTime.UtcNow;
            _untouchableAt = _lastSweep;   // ★ keep the report fresh; NeedsHuman() drops it after 2 s
            _untouchable.Clear();

            var acted = new List<string>();
            foreach (var d in Scan())
            {
                int press = Decide(d);
                if (press == 0)
                {
                    _untouchable.Add("untouched:[" + d.Title + "] " + Describe(d));
                    continue;
                }
                if (press == -1)
                {
                    // single-button acknowledgement: WM_COMMAND needs the real ID, so click the child.
                    IntPtr btn = IntPtr.Zero;
                    EnumChildWindows(d.H, (c, __) =>
                    {
                        if (btn == IntPtr.Zero)
                        {
                            var cc = new StringBuilder(128); GetClassNameW(c, cc, 128);
                            if (cc.ToString() == "Button") btn = c;
                        }
                        return true;
                    }, IntPtr.Zero);
                    if (btn != IntPtr.Zero)
                        SendMessage(btn, 0x00F5 /*BM_CLICK*/, IntPtr.Zero, IntPtr.Zero);
                    acted.Add("only-btn:[" + d.Title + "] " + Describe(d));
                }
                else
                {
                    SendMessage(d.H, WM_COMMAND, (IntPtr)press, IntPtr.Zero);
                    acted.Add("id" + press + ":[" + d.Title + "] " + Describe(d));
                }
            }
            LastReport = string.Join(" | ", acted);
            return acted.Count;
        }

        private static string Describe(Dlg d)
        {
            var ids = new List<string>();
            foreach (var i in d.ButtonIds) ids.Add(i.ToString());
            ids.Sort();
            return "{buttons=" + string.Join(",", ids) + " texts=" + string.Join("/", d.ButtonTexts) + "}";
        }

        /// <summary>Human-facing note about anything the guard refused to click.</summary>
        public static string NeedsHuman()
        {
            // ★★ 2026-09-28 FOURTH false positive: this report could be STALE. Sweep() is throttled to
            //   750 ms, so Untouchable could describe a dialog that opened and closed seconds earlier —
            //   the tool then refused to run against a dialog that no longer existed. Anything older
            //   than two seconds is worthless; drop it.
            if ((DateTime.UtcNow - _untouchableAt).TotalSeconds > 2) { _untouchable.Clear(); return ""; }
            if (_untouchable.Count == 0) return "";
            return "SolidWorks is showing a dialog this guard will not auto-answer (class #32770): "
                 + string.Join(" | ", _untouchable)
                 + ". Close it in the SolidWorks window (or the call will keep failing).";
        }
    }
}
