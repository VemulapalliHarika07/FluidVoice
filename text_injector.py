"""
Types text into whatever application currently has keyboard focus.

Uses the `keyboard` library's write() which sends real keystroke events
via the Windows SendInput API under the hood - this is what makes it
work in literally any app (browsers, Word, Slack, terminals, etc.),
the same trick FluidVoice's "Smart Typing" uses on macOS via
Accessibility APIs.
"""
import time
import keyboard


def type_text(text: str, add_trailing_space: bool = True,
              strip_trailing_punct: bool = False) -> None:
    if not text:
        return

    if strip_trailing_punct:
        text = text.rstrip(" .")

    if add_trailing_space and not text.endswith(" "):
        text = text + " "

    # Small delay avoids swallowing the tail of the hotkey release event
    time.sleep(0.05)
    keyboard.write(text, delay=0)
