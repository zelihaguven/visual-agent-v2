"""Eldekileri soran sorular kayıtlardan cevaplanır."""

import asyncio
import logging
from dataclasses import replace

from visual_agent.ask.deps import AskDeps
from visual_agent.ask.steps import AskState
from visual_agent.domain.result import Inventory, InventoryDocument
from visual_agent.verification.text import identifiers_in

logger = logging.getLogger(__name__)

_MAX_LISTED_CODES = 200


def _build_inventory(state: AskState, deps: AskDeps) -> Inventory:
    documents = []
    for doc_id in state.allowed:
        codes = deps.identifiers.codes_of(doc_id)
        documents.append(
            InventoryDocument(
                doc_id=doc_id,
                title=deps.catalog.title(doc_id),
                codes=codes[:_MAX_LISTED_CODES],
                code_count=len(codes),
            )
        )
    return Inventory(
        documents=tuple(documents),
        document_count=len(documents),
        code_count=sum(document.code_count for document in documents),
    )


async def answer_inventory(state: AskState, deps: AskDeps) -> AskState:
    """Model listeyi eksik sayar; bu sorular aramaya gitmeden kayıtlardan cevaplanır."""
    classifier = deps.inventory_classifier
    if classifier is None or state.request.doc_ids or identifiers_in(state.question):
        return state
    try:
        is_inventory = await asyncio.wait_for(
            classifier(state.question), deps.inventory_limit_seconds
        )
    except Exception:
        logger.warning("Envanter sorusu denetlenemedi", exc_info=True)
        return state
    return replace(state, result=_build_inventory(state, deps)) if is_inventory else state
