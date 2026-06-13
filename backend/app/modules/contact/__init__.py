"""Contact module — the marketing-site contact form.

A visitor submits the public contact form and the message is emailed to the
support inbox (`settings.CONTACT_RECIPIENT_EMAIL`), with the visitor's address
set as the email's reply-to. Nothing is persisted — this is a thin, route +
service module (no DB layers), like `responses/`:

    routes.py     → public `POST /contact` endpoint
    service.py    → renders + sends the email (owns the email client)
    schemas.py    → Pydantic request/response shapes
    exceptions.py → domain exceptions (routes translate these to HTTP)
"""
