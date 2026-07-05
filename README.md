# FluidVoiceWin

An offline, open-source voice dictation app for **Windows**, inspired by
[FluidVoice](https://github.com/altic-dev/FluidVoice) (macOS). Press a hotkey,
speak, and your words get typed into whatever app has focus — entirely
on-device, no cloud, no API keys required.

## How it works

1. **Global hotkey** (default `Ctrl+Alt+Space`) starts/stops recording from
   your microphone.
2. Audio is transcribed **locally** using [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
   (a fast CTranslate2 implementation of OpenAI Whisper) — no internet
   connection needed after the model is downloaded once.
3. The transcribed text is typed directly into the focused window using
   simulated keystrokes, so it works in literally any app: Word, browsers,
   Slack, terminals, etc.
4. A small overlay pill shows recording/transcribing status, and a system
   tray icon lets you switch models or quit.

## Quick start

```bat
pip install -r requirements.txt
python main.py
```

- First run downloads the Whisper model you've configured (default: `base`,
  ~140 MB) from Hugging Face and caches it locally. After that, everything
  runs fully offline.
- Press `Ctrl+Alt+Space` anywhere to start talking; press it again to stop
  and have the text typed out.
- Right-click the tray icon to change model size or quit.

## Packaging as a standalone .exe

Run `build_exe.bat` on a Windows machine (needs Python 3.10+). This uses
PyInstaller to produce `dist\FluidVoiceWin.exe` — a single file you can
run without a Python install, similar to how the original ships a signed
`.app` via Homebrew.

## Configuration

Settings live in `%APPDATA%\FluidVoiceWin\config.json` (created on first
run). Key options:

| Key | Description |
|---|---|
| `hotkey` | Global hotkey string, e.g. `"ctrl+alt+space"` |
| `model_size` | `tiny` / `base` / `small` / `medium` / `large-v3` — bigger = more accurate, slower |
| `language` | `null` for auto-detect, or a code like `"en"`, `"hi"`, `"te"` to force a language |
| `device` | `"cpu"` (works everywhere) or `"cuda"` if you have an NVIDIA GPU + CUDA/cuDNN installed |
| `compute_type` | `"int8"` (recommended for CPU) or `"float16"` (recommended for GPU) |
| `show_overlay` | Show/hide the status pill |

Edit the file and restart the app to apply changes (or use the tray menu
for model switching, which applies live).

## What's included vs. the original macOS FluidVoice

This is a from-scratch Windows-native reimplementation of the core
dictation loop, not a line-for-line port (the original is ~99% Swift/AppKit,
which doesn't run on Windows). Included:

- ✅ Global hotkey → record → on-device transcription → auto-type into any app
- ✅ System tray integration (menu bar equivalent)
- ✅ Live status overlay
- ✅ Multiple Whisper model sizes, CPU or GPU
- ✅ Fully local, privacy-first (no audio/text leaves your machine)

Not (yet) included, since they'd each be substantial sub-projects:

- ❌ **Command Mode** (voice-triggered system actions/shortcuts)
- ❌ **Write Mode** (select-and-rewrite existing text in any field)
- ❌ **Fluid Intelligence**-style local LLM post-processing/formatting
  (you could add this by piping the transcript through a small local LLM
  like a quantized Llama model before typing — happy to build this next)
- ❌ Notch-aware live-preview overlay (Windows has no notch; a simpler
  floating pill is used instead)
- ❌ Audio history browser with ZIP export
- ❌ Auto-update mechanism

These are all buildable as incremental additions — this first version
gets the essential "talk instead of type" workflow working end-to-end.

## Requirements

- Windows 10/11
- Python 3.10–3.12 (if running from source)
- A microphone
- ~150 MB–3 GB free disk space depending on chosen model size

## Troubleshooting

- **Hotkey doesn't fire**: the `keyboard` library sometimes needs the app
  run as Administrator to intercept global hotkeys depending on what other
  app has focus (e.g. apps running elevated).
- **No text appears**: some apps (certain games, some elevated apps) block
  simulated keystrokes; try running FluidVoiceWin as Administrator too.
- **Slow first transcription**: the model is loading into memory; subsequent
  ones are much faster. Use a smaller model size (`tiny`/`base`) on modest
  hardware.

## License

MIT — do whatever you like with it. (The original FluidVoice is GPLv3;
this is an independent reimplementation and not a fork or derivative of
its Swift codebase.)
