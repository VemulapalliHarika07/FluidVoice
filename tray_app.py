"""
Windows system-tray icon (menu bar equivalent) with a right-click menu
for switching model size, toggling the overlay, and quitting.
"""
import threading
from PIL import Image, ImageDraw
import pystray

import config as cfg_mod


def _make_icon_image(color="#4A90D9") -> Image.Image:
    """Draws a simple microphone-ish circle icon procedurally (no asset files needed)."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((4, 4, size - 4, size - 4), fill=color)
    draw.rounded_rectangle((size * 0.38, size * 0.18, size * 0.62, size * 0.58),
                            radius=10, fill="white")
    draw.rectangle((size * 0.47, size * 0.58, size * 0.53, size * 0.78), fill="white")
    draw.line((size * 0.35, size * 0.78, size * 0.65, size * 0.78), fill="white", width=4)
    return img


class TrayApp:
    def __init__(self, on_quit, on_model_change, get_state_text):
        self._on_quit = on_quit
        self._on_model_change = on_model_change
        self._get_state_text = get_state_text
        self._icon = None

    def _model_menu_items(self):
        cfg = cfg_mod.load_config()
        sizes = ["tiny", "base", "small", "medium", "large-v3"]

        def make_handler(size):
            return lambda icon, item: self._on_model_change(size)

        return [
            pystray.MenuItem(
                size,
                make_handler(size),
                checked=lambda item, s=size: cfg_mod.load_config()["model_size"] == s,
                radio=True,
            )
            for size in sizes
        ]

    def _build_menu(self):
        return pystray.Menu(
            pystray.MenuItem(lambda item: self._get_state_text(), None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Model", pystray.Menu(*self._model_menu_items())),
            pystray.MenuItem("Open config folder", self._open_config_folder),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit FluidVoiceWin", self._quit),
        )

    def _open_config_folder(self, icon, item):
        import os
        os.startfile(cfg_mod.get_config_dir())  # Windows-only helper

    def _quit(self, icon, item):
        icon.stop()
        self._on_quit()

    def run(self):
        image = _make_icon_image()
        self._icon = pystray.Icon("FluidVoiceWin", image, "FluidVoiceWin", self._build_menu())
        self._icon.run()

    def run_detached(self):
        threading.Thread(target=self.run, daemon=True).start()

    def notify(self, title: str, message: str):
        if self._icon:
            try:
                self._icon.notify(message, title)
            except Exception:
                pass
