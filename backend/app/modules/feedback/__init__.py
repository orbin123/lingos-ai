"""In-app feedback prompt: eligibility, cooldowns, randomized display.

Collected reviews are stored on the existing ``app_reviews`` table (see
``app.modules.reviews``) so the admin "User Reviews" page reads them directly.
This module owns the *when to ask* logic and the prompt audit log.
"""
