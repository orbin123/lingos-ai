"""HTTP routes for the contact form.

A single public, unauthenticated endpoint. The IP-based rate limiter in
`app/core/rate_limit.py` caps `POST /contact` as spam defense-in-depth.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.modules.contact.exceptions import ContactDeliveryError
from app.modules.contact.schemas import ContactRequest, ContactResponse
from app.modules.contact.service import ContactService

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("", response_model=ContactResponse)
def submit_contact_message(payload: ContactRequest) -> ContactResponse:
    try:
        ContactService().submit(payload)
    except ContactDeliveryError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not send your message right now. Please try again later.",
        ) from exc
    return ContactResponse()
