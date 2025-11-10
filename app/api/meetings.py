from pathlib import Path
import time, logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from app.services.transcription import transcrire
from app.services.notes import meeting_notes, notes_to_markdown

logger = logging.getLogger(__name__) #Log pour debugger

router = APIRouter(
    prefix="/meetings",
    tags=["meetings"],
)


@router.post("/", response_class=FileResponse,
    summary="Générer un rapport de réunion à partir d'un fichier audio",
)

def gen_meeting_report(file: UploadFile = File(...)) -> FileResponse:
    """
    Reçoit un fichier audio et renvoie un rapport de réunion Markdown.
    - transcription avec un modele asr (ici whisper)
    - génération du résumé et de notes (sujets, décisions, actions)
    - Markdown téléchargé dans 'downloads' et sauvé sur disque
    """
    
    if not file.filename: 
        raise HTTPException(status_code=400, detail="Aucun fichier audio fourni")

    #En plus de la transcription, on relève sa longueur et la langue detectée
    transcript, lang = transcrire(file)
    logger.info("Transcription done (lang=%s, length=%d chars)", lang, len(transcript)) 

    # Resumé et Notes
    notes = meeting_notes(transcript)
    logger.info("Meeting notes generated")
    
    markdown = notes_to_markdown(notes, lang=lang)
    logger.info("Markdown report generated")
    
    output_dir = Path("downloads")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    markdown_path = output_dir / f"rapport_reunion_{timestamp}.md" #Nom unique à chaque reunion

    with markdown_path.open("w", encoding="utf-8") as f:
        f.write(markdown) 
    logger.info("Meeting report saved to %s", markdown_path)

    
    return FileResponse(
        path=markdown_path,
        filename=markdown_path.name,      # on garde le meme nom
        media_type="text/markdown",
    )
