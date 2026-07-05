"""
FluidVoiceWin - offline voice dictation for Windows.

Press the global hotkey (default: Ctrl+Alt+Space) to start recording,
press it again to stop. The audio is transcribed fully on-device with
faster-whisper and the resulting text is typed into whichever app
currently has keyboard focus. Nothing is uploaded anywhere.

Run with: python main.py
Package to a standalone .exe with: pyinstaller --onefile --noconsole main.py
"""
import sys
import threading

import keyboard

import config as cfg_mod
from audio_recorder import AudioRecorder
from transcriber import Transcriber
from text_injector import type_text
from overlay import Overlay
from tray_app import TrayApp


class FluidVoiceWin:
    def __init__(self):
        self.cfg = cfg_mod.load_config()
        self.recorder = AudioRecorder(sample_rate=self.cfg["sample_rate"])
        self.transcriber = Transcriber(
            model_size=self.cfg["model_size"],
            device=self.cfg["device"],
            compute_type=self.cfg["compute_type"],
        )
        self.overlay = Overlay() if self.cfg["show_overlay"] else None
        self.tray = TrayApp(
            on_quit=self.quit,
            on_model_change=self.change_model,
            get_state_text=self.state_text,
        )
        self._state = "idle"  # idle -> recording -> processing -> idle
        self._lock = threading.Lock()

    def state_text(self) -> str:
        return {
            "idle": "FluidVoiceWin — idle",
            "recording": "FluidVoiceWin — listening…",
            "processing": "FluidVoiceWin — transcribing…",
        }.get(self._state, "FluidVoiceWin")

    def change_model(self, size: str):
        self.cfg = cfg_mod.update_config(model_size=size)
        # Reload lazily in a background thread so the tray doesn't hang
        threading.Thread(target=self.transcriber.reload, kwargs={"model_size": size}, daemon=True).start()
        self.tray.notify("FluidVoiceWin", f"Switched model to {size}")

    def toggle_recording(self):
        with self._lock:
            if self._state == "idle":
                self._start_recording()
            elif self._state == "recording":
                self._stop_and_transcribe()
            # ignore hotkey presses while "processing"

    def _start_recording(self):
        self._state = "recording"
        self.recorder.start()
        if self.overlay:
            self.overlay.show_listening()

    def _stop_and_transcribe(self):
        self._state = "processing"
        if self.overlay:
            self.overlay.show_processing()
        audio = self.recorder.stop()

        def worker():
            text = self.transcriber.transcribe(audio, language=self.cfg["language"])
            if text:
                type_text(
                    text,
                    add_trailing_space=self.cfg["auto_add_space"],
                    strip_trailing_punct=False,
                )
            if self.overlay:
                self.overlay.show_typed(text)
            self._state = "idle"

        threading.Thread(target=worker, daemon=True).start()

    def register_hotkey(self):
        hotkey = self.cfg["hotkey"]
        keyboard.add_hotkey(hotkey, self.toggle_recording)
        print(f"[FluidVoiceWin] Global hotkey registered: {hotkey}")
        print("[FluidVoiceWin] Press it once to start recording, again to stop & type.")

    def quit(self):
        print("[FluidVoiceWin] Shutting down.")
        sys.exit(0)

    def run(self):
        print("[FluidVoiceWin] Loading speech model (first run downloads it once)...")
        # Warm up model in background so first dictation isn't slow
        threading.Thread(target=self.transcriber._ensure_loaded, daemon=True).start()
        self.register_hotkey()
        self.tray.run_detached()
        keyboard.wait()  # blocks main thread, listens for hotkey forever


if __name__ == "__main__":
    if not sys.platform.startswith("win"):
        print("WARNING: FluidVoiceWin is designed for Windows (uses SendInput-based typing "
              "and Windows-style tray integration). It may partially run elsewhere for "
              "development, but global hotkeys / system typing require Windows.")
    app = FluidVoiceWin()
    app.run()
