from __future__ import annotations
import logging, whisper
from functools import lru_cache
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

MODEL_NAME = "base"  # "base" test rapides, "small" un peu plus lent mais plus précis


@lru_cache()
def charge_asr() -> whisper.Whisper:
    """
    Charge le modèle (ici Whisper) une seule fois et le met en cache.
    """
    logger.info("ASR model: %s", MODEL_NAME)
    try:
        model = whisper.load_model(MODEL_NAME)
    except Exception as e:
        logger.exception("Failed to load transcription model")
        raise RuntimeError("Impossible de charger le modèle de transcription") from e
    return model


def save_upload_temp(upload_file: UploadFile) -> Path:
    """
    Sauvegarde un UploadFile FastAPI dans un fichier temporaire et
    renvoie son chemin.
    """
    suffix = Path(upload_file.filename or "").suffix or ".tmp"

    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(upload_file.file.read())
            tmp_path = Path(tmp.name)
    except Exception as e:
        logger.exception("Error reading audio file")
        raise HTTPException(status_code=500, detail="Erreur lors de la lecture du fichier audio") from e

    return tmp_path


def transcribe_lang(audio_path: Path, language: Optional[str] = None) -> Tuple[str, str]:
    """    
    Lance le modele et retourne:
        transcript: texte 
        detected_language: code ('fr', 'en')
    """
    model = charge_asr()

    try:
        result = model.transcribe(
            str(audio_path),
            language=language,     # auto-détection par whisper si None
            temperature=0.0,
            beam_size=1,
            fp16=model.device != "cpu",
        )
    except Exception as e:
        logger.exception("Audio transcription error on %s", audio_path)
        raise HTTPException(status_code=500, detail="Erreur transcription audio") from e

    transcript: str = result.get("text", "").strip()
    detected_language: str = result.get("language", "")

    return transcript, detected_language


def transcrire(file: UploadFile, language: Optional[str] = None) -> Tuple[str, str]:
    """
    Fonction principale de transcription :

    - Sauvegarde le fichier audio dans un temporaire
    - Lance Whisper
    - Renvoie (transcript, langue).
    """
    audio_path = save_upload_temp(file)

    try:
        transcript, detected_language = transcribe_lang(audio_path, language=language)
    finally:
        # Nettoyage du fichier temporaire
        try:
            audio_path.unlink(missing_ok=True)
        except Exception as e:
            logger.warning("Unable to delete temp file %s: %s", audio_path, e)

    return transcript, detected_language


