"""
Microphone capture. Records audio into memory while active,
returns a float32 numpy array (mono, resampled to `target_rate`, default
16kHz - what Whisper expects) when stopped.

IMPORTANT: We record at the microphone's own native sample rate (queried
from the OS) rather than forcing 16kHz on the device directly. Many
Windows mics/drivers don't natively support 16kHz and will produce
distorted/garbled audio if you force it via WASAPI - this was causing
garbled transcriptions ("uuuuuuuu"-style hallucinations from Whisper).
Instead we record cleanly at the native rate and resample in software.
"""
import threading
import numpy as np
import sounddevice as sd


class AudioRecorder:
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.target_rate = sample_rate   # rate Whisper expects (16000)
        self.channels = channels
        self._native_rate = None
        self._frames = []
        self._stream = None
        self._lock = threading.Lock()
        self._recording = False

    def _get_native_rate(self) -> int:
        try:
            default_input = sd.query_devices(kind="input")
            rate = int(default_input.get("default_samplerate", 44100))
            return rate if rate > 0 else 44100
        except Exception:
            return 44100

    def _callback(self, indata, frames, time_info, status):
        with self._lock:
            if self._recording:
                self._frames.append(indata.copy())

    def start(self):
        with self._lock:
            self._frames = []
            self._recording = True
        self._native_rate = self._get_native_rate()
        self._stream = sd.InputStream(
            samplerate=self._native_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def _resample(self, audio: np.ndarray, orig_rate: int, target_rate: int) -> np.ndarray:
        if orig_rate == target_rate or audio.size == 0:
            return audio
        duration = audio.shape[0] / float(orig_rate)
        target_len = max(1, int(round(duration * target_rate)))
        orig_x = np.linspace(0.0, duration, num=audio.shape[0], endpoint=False)
        target_x = np.linspace(0.0, duration, num=target_len, endpoint=False)
        return np.interp(target_x, orig_x, audio).astype(np.float32)

    def stop(self) -> np.ndarray:
        with self._lock:
            self._recording = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        with self._lock:
            if not self._frames:
                return np.zeros((0,), dtype=np.float32)
            audio = np.concatenate(self._frames, axis=0)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        audio = audio.astype(np.float32)
        return self._resample(audio, self._native_rate or 44100, self.target_rate)

    def is_recording(self) -> bool:
        with self._lock:
            return self._recording

    @staticmethod
    def list_input_devices():
        """Returns list of (index, name) for available input devices - useful for settings UI."""
        devices = sd.query_devices()
        return [
            (i, d["name"])
            for i, d in enumerate(devices)
            if d.get("max_input_channels", 0) > 0
        ]
