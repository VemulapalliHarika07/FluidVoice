"""
Minimal always-on-top overlay pill that shows recording / processing status,
similar in spirit to FluidVoice's Live Preview overlay on macOS.

Runs its own Tkinter mainloop on a background thread so it doesn't block
the hotkey listener or tray icon.
"""
import threading
import tkinter as tk


class Overlay:
    def __init__(self):
        self._root = None
        self._label = None
        self._ready = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._ready.wait(timeout=5)

    def _run(self):
        self._root = tk.Tk()
        self._root.overrideredirect(True)       # no title bar / border
        self._root.attributes("-topmost", True)
        self._root.attributes("-alpha", 0.92)
        try:
            self._root.attributes("-toolwindow", True)  # hide from taskbar/alt-tab (Windows)
        except tk.TclError:
            pass

        width, height = 220, 44
        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()
        x = (screen_w - width) // 2
        y = screen_h - 140
        self._root.geometry(f"{width}x{height}+{x}+{y}")

        self._label = tk.Label(
            self._root,
            text="",
            font=("Segoe UI", 11),
            bg="#1e1e1e",
            fg="#ffffff",
            padx=12,
            pady=8,
        )
        self._label.pack(fill="both", expand=True)
        self._root.configure(bg="#1e1e1e")
        self._root.withdraw()  # start hidden
        self._ready.set()
        self._root.mainloop()

    def _set(self, text: str, show: bool):
        def _apply():
            if not self._label:
                return
            self._label.config(text=text)
            if show:
                self._root.deiconify()
            else:
                self._root.withdraw()
        if self._root:
            self._root.after(0, _apply)

    def show_listening(self):
        self._set("🎤  Listening…", True)

    def show_processing(self):
        self._set("⏳  Transcribing…", True)

    def show_typed(self, preview: str):
        short = (preview[:40] + "…") if len(preview) > 40 else preview
        self._set(f"✓  {short}" if short else "✓  Done", True)
        if self._root:
            self._root.after(1200, lambda: self._set("", False))

    def hide(self):
        self._set("", False)
