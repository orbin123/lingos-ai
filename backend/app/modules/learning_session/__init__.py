"""Learning session module — chat-driven learning loop.

Owns the conversational state machine that guides a learner through
teaching → practice → evaluation → feedback → follow-up. Each session
is anchored to one pre-generated task and persisted in the
LearningSession table so the WebSocket can reconnect.
"""
