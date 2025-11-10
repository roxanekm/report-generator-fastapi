from __future__ import annotations
import logging, re
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Tuple
from transformers import pipeline

logger = logging.getLogger(__name__)


@dataclass
class MeetingNotes:
    """
    Structure standard de notes
    """
    transcript: str
    summary: str
    topics: str
    decisions: List[str]
    actions: List[str]


@lru_cache()
def charge_model():
    """
    Charge le modèle de résumé une seule fois. 
    Modèle entraîné sur des dialogues (SAMSum).
    """
    logger.info("Load summarization model: philschmid/bart-large-cnn-samsum")
    return pipeline("summarization", model="philschmid/bart-large-cnn-samsum")


def gen_resume(transcript: str, max_size: int = 2000) -> str:
    """
    Génère un résumé à partir d'une transcription decoupée en plusieurs segments
    """
    if not transcript.strip():
        return ""

    model_asr = charge_model()

    #Les segments sont des morceaux du transcript de taille max_size 
    # car le modèle ne traite pas (correctement) les longs textes
    segments = [
        transcript[i : i + max_size]
        for i in range(0, len(transcript), max_size)
    ]

    list_resumes: List[str] = [] # Résumés partiels pour chaque segment
    for seg in segments:
        try:
            res = model_asr(
                seg,
                max_length=250, # Reduire à 150 pour tests rapides
                min_length=80, # 60
                do_sample=False, #déterministe
            )
            list_resumes.append(res[0]["summary_text"])
        except Exception as e:
            logger.exception("Error segment summary: %s", e)            
            continue

    return " ".join(list_resumes).strip() # On retourne l'ensemble des résumés comme un seul


def gen_topics(summary: str) -> str:
    """
    Extrait une ou deux phrases qui résument les sujets abordés à partir du résumé.
    """
    phrases = [
        s.strip() for s in re.split(r"(?<=[\.\!\?])\s+", summary) if s.strip()
    ]
    if not phrases:
        return summary.strip()

    # On prend les 1 à 2 premières phrases comme 'topics'
    topic = " ".join(phrases[:2])
    return topic


def decisions_actions(summary: str) -> Tuple[List[str], List[str]]:
    """
    Parcourt le resumé pour identifier décisions et actions
    à partir de mots-clés FR ou EN. 
    """
    decisions: List[str] = []
    actions: List[str] = []

    phrases = [
        s.strip() for s in re.split(r"(?<=[\.\!\?])\s+", summary) if s.strip()
    ]

    # Listes à compléter avec d'autres keywords si besoin
    decision_keywords = ["décidé", "décision", "convenu", "agreed", "will decide"]
    action_keywords = ["à faire", "faire", "action", "follow", "implement", "to do"]

    for s in phrases:
        low = s.lower() #Case-insensitive
        if any(kw in low for kw in decision_keywords):
            decisions.append(s)
        elif any(kw in low for kw in action_keywords):
            actions.append(s)

    return decisions, actions


def meeting_notes(transcript: str) -> MeetingNotes:
    """
    Pipeline :
    - résumé
    - extraction des sujets
    - extraction décisions / actions
    """
    
    summary = gen_resume(transcript)
    logger.info("Summary generated")
    
    topics = gen_topics(summary)
    logger.info("Topics: %s", topics)
    
    decisions, actions = decisions_actions(summary)
    logger.info(" %d decisions; %d actions", len(decisions), len(actions))

    return MeetingNotes(
        transcript=transcript,
        summary=summary,
        topics=topics,
        decisions=decisions,
        actions=actions,
    )


def notes_to_markdown(notes: MeetingNotes, lang: str) -> str:
    """
    Génère un rapport Markdown à partir des notes
    """
    if notes.decisions:
        decisions_block = "- " + "\n- ".join(notes.decisions)
    else:
        decisions_block = "NA"

    if notes.actions:
        actions_block = "- " + "\n- ".join(notes.actions)
    else:
        actions_block = "NA"

    if lang.startswith("fr"): #On verifie la langue
        md = f"""# Compte-rendu de réunion

## Sujets abordés
{notes.topics}

## Décisions
{decisions_block}

## Actions
{actions_block}

## Résumé
{notes.summary}

## Transcription complète
{notes.transcript}
"""
    else:
        md = f"""# Meeting Report

## Topics Discussed
{notes.topics}

## Decisions
{decisions_block}

## Action Items
{actions_block}

## Summary
{notes.summary}

## Full Transcript
{notes.transcript}
"""
    return md
