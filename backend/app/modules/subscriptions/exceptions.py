"""Domain exceptions for the subscription/entitlement state machine.

Routes translate these to HTTPExceptions with stable `code` fields.
"""


class SubscriptionError(Exception):
    """Base class for subscription domain errors."""


class PlanNotFound(SubscriptionError):
    """plan_id is not in PLAN_CATALOG."""


class PlanLocked(SubscriptionError):
    """Plan can no longer be changed (trial started or subscription active)."""


class NoPlanSelected(SubscriptionError):
    """start_trial called before select_plan."""


class TrialAlreadyUsed(SubscriptionError):
    """The one free trial was already consumed."""


class NotCancellable(SubscriptionError):
    """cancel called with no trial/active subscription to cancel."""
