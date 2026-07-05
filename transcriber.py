"""
On-device speech-to-text using faster-whisper (CTranslate2-based Whisper).
Fully local - no audio or text ever leaves the machine.

Model is downloaded once from Hugging Face on first use and cached locally
(under %USERPROFILE%\\.cache\\huggingface), then runs fully offline afterward.
"""
import numpy as np
from faster_whisper import WhisperModel


class Transcriber:
    def __init__(self, model_size: str = "base", device: str = "cpu",
                 compute_type: str = "int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None

    def _ensure_loaded(self):
        if self._model is None:
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )

    def reload(self, model_size: str = None, device: str = None, compute_type: str = None):
        """Call this if the user changes model/device settings at runtime."""
        if model_size:
            self.model_size = model_size
        if device:
            self.device = device
        if compute_type:
            self.compute_type = compute_type
        self._model = None
        self._ensure_loaded()

    def transcribe(self, audio: np.ndarray, language: str = None) -> str:
        """
        audio: mono float32 numpy array sampled at 16kHz
        language: ISO 639-1 code (e.g. "en") or None to auto-detect
        """
        if audio.size == 0:
            return ""
        self._ensure_loaded()
        segments, _info = self._model.transcribe(
            audio,
            language=language,
            vad_filter=True,          # trims leading/trailing silence, skips non-speech
            beam_size=5,
        )
        text_parts = [seg.text.strip() for seg in segments]
        return " ".join(p for p in text_parts if p).strip()
