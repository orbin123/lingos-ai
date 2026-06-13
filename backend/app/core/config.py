"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Central configuration object.

    Reads values from .env file at project root.
    All fields are type-validated on startup - missing/wrong values
    will crash the app immediately with a clear error.
    """

    # Application
    environment: str = "development"
    debug: bool = True
    log_level: str = "info"

    # Sentry error tracking. Empty = disabled (local/test default).
    sentry_dsn: str = ""
    # Fraction of requests traced for performance (0.0–1.0). 0.1 = 10%.
    sentry_traces_sample_rate: float = 0.1

    # Schema-boundary strictness. When False (prod default during rollout), a
    # contract-projection or agent-input validation failure is logged and the
    # legacy payload is delivered unchanged. When True (set in tests), the same
    # failure raises so contract violations surface loudly instead of silently
    # falling back. Env: STRICT_CONTRACTS.
    strict_contracts: bool = True

    # Database
    database_url: str 

    # Redis
    redis_url: str

    # Auth
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 480

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"

    # Frontend
    frontend_url: str = "http://localhost:3000"

    # Billing / access
    # A one-time course purchase grants this many years of access from the
    # purchase date. Surfaced in the admin Subscribers view as access_expires_at.
    ACCESS_WINDOW_YEARS: int = 2
    # Free-trial length. Stored on the subscription row when the user
    # starts their trial (start-trial endpoint).
    TRIAL_DAYS: int = 7

    # Email delivery — "console" logs emails to the app logger (dev/test
    # default, the OTP shows up in the uvicorn console); "resend" sends real
    # email via the Resend API. Missing RESEND_API_KEY falls back to console.
    EMAIL_PROVIDER: str = "console"
    RESEND_API_KEY: str = ""
    # Resend sandbox (no verified domain) requires the resend.dev sender and
    # only delivers to the Resend account owner's address.
    EMAIL_FROM: str = "LingosAI <onboarding@resend.dev>"
    # Where the marketing-site contact form delivers submissions.
    CONTACT_RECIPIENT_EMAIL: str = "support@lingosai.com"

    # Email OTP verification. The pepper keys the HMAC of stored codes —
    # set a dedicated random value in prod; empty falls back to jwt_secret.
    OTP_HASHING_SECRET: str = ""
    OTP_LENGTH: int = 6
    OTP_TTL_MINUTES: int = 10
    OTP_RESEND_COOLDOWN_SECONDS: int = 60
    OTP_MAX_SENDS_PER_HOUR: int = 5
    OTP_MAX_VERIFY_ATTEMPTS: int = 5
    # Local dev only — accepts "123456" without the HMAC check. NEVER true in prod.
    DEV_OTP_BYPASS: bool = False

    # Auth sessions (refresh tokens). Access tokens issued by the session
    # flow are short; the refresh cookie keeps users logged in. The legacy
    # jwt_access_token_expire_minutes stays for non-session tokens (e.g.
    # OAuth relink state).
    ACCESS_TOKEN_TTL_MINUTES: int = 20
    REFRESH_TOKEN_TTL_DAYS: int = 30
    REFRESH_TOKEN_REMEMBER_DAYS: int = 90
    # False for http://localhost dev; MUST be true behind https in prod.
    # The refresh cookie is SameSite=Lax — frontend and backend must share a
    # registrable domain in prod (subdomains are fine).
    AUTH_COOKIE_SECURE: bool = False

    # Razorpay (Test Mode) — wired in Phase 4; placeholders so .env can be
    # filled ahead of time.
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""

    # AI / LLM
    OPENAI_API_KEY: str
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_API_KEY: str
    LANGCHAIN_PROJECT: str = "ai-english-coach"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"

    # AI observability — when True, each instrumented LLM collaborator call
    # writes one operational row to ai_request_logs (latency, tokens, status,
    # trace_id). Best-effort and off the request session; flip to False to kill
    # the seam entirely if it ever misbehaves.
    AI_REQUEST_LOGGING_ENABLED: bool = True

    # Rate limiting (AI endpoints) — per-user sliding-window limits on every
    # route that spends money on an AI provider call. Backed by Redis when
    # reachable (multi-worker safe); falls back to in-memory buckets so dev
    # and tests need no Redis. Limits are deliberately generous to start —
    # tighten with data from ai_request_logs per-user counts.
    AI_RATE_LIMIT_ENABLED: bool = True
    AI_RATE_LIMIT_PER_MINUTE: int = 30
    AI_RATE_LIMIT_TRANSCRIBE_PER_MINUTE: int = 20
    # Learning-session WebSocket: max incoming messages per user per minute.
    WS_MESSAGE_RATE_PER_MINUTE: int = 20
    # A2Z game: max Deepgram stream connections per user per minute
    # (connection-level only — audio frames inside a stream are never throttled).
    WS_A2Z_STREAMS_PER_MINUTE: int = 10

    # AI quality (LLM-as-judge, Part B Phase 2) — a stronger model scores live
    # feedback for quality and writes one ai_evaluations row, joined to the
    # operational log by trace_id. Online sampling only (cost control); the
    # judge runs post-commit, fire-and-forget, and never blocks the learner.
    AI_EVAL_ENABLED: bool = True
    AI_EVAL_SAMPLE_RATE: float = 0.1
    AI_EVAL_JUDGE_MODEL: str = "gpt-4.1"
    AI_EVAL_TIMEOUT_S: float = 20.0
    # Mentor-note (RAG) judging sample rate (Part B Phase 3). Notes are produced
    # once per session completion — far rarer than per-activity feedback — and
    # RAG faithfulness is the highest-value bug-catcher, so judge every one.
    AI_EVAL_MENTOR_SAMPLE_RATE: float = 1.0

    # AI / TTS (text-to-speech)
    # `gpt-4o-mini-tts` is the newest + cheapest TTS model from OpenAI.
    # It uniquely supports the `instructions` parameter (e.g. "speak slowly,
    # sound encouraging") which is gold for a tutor app.
    # Voices for this model: alloy, ash, ballad, coral, echo, fable,
    # onyx, nova, sage, shimmer, verse.
    OPENAI_TTS_MODEL: str = "gpt-4o-mini-tts"
    OPENAI_TTS_VOICE: str = "alloy"
    # Where synthesized audio files are cached on disk. Path is RELATIVE
    # to the backend/ directory so it works regardless of where uvicorn
    # is launched from. Override per-environment via env var.
    TTS_CACHE_DIR: str = "app/ai/tts/_cache"
    # Public URL prefix the audio files are served under by FastAPI's
    # StaticFiles mount. Frontend uses these URLs in <audio src=...>.
    TTS_PUBLIC_URL_PREFIX: str = "/audio"

    # AI / STT (speech-to-text)
    # We use whisper-1 because it's the ONLY OpenAI model that supports
    # word-level timestamps (needed for fluency analysis on speak_*
    # tasks). gpt-4o-mini-transcribe is newer + cheaper but only returns
    # plain text. Sticking with whisper-1 keeps one model for all STT.
    OPENAI_STT_MODEL: str = "whisper-1"
    # Where transcript JSON sidecars are cached on disk. Different
    # directory from TTS so retention/cleanup policies stay independent
    # (transcripts may have privacy implications audio doesn't).
    STT_CACHE_DIR: str = "app/ai/stt/_cache"
    # Where learner-uploaded speaking clips live. These are not mounted as
    # public StaticFiles; they are served through an owner-checked route.
    LEARNER_AUDIO_DIR: str = "app/ai/stt/_learner_audio"

    # Deepgram — real-time streaming STT for A2Z challenge
    # Get a key at console.deepgram.com → API Keys → Create Key
    DEEPGRAM_API_KEY: str = ""

    # AI / Pronunciation (Azure Speech Pronunciation Assessment)
    # Optional at startup so Phase 4 code doesn't break environments that
    # haven't created an Azure Speech resource yet. The pronunciation route
    # fails fast with a clear error if these remain unset at call time.
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = ""
    # Where pronunciation-score JSON sidecars are cached on disk.
    PRONUNCIATION_CACHE_DIR: str = "app/ai/pronunciation/_cache"

    # AI / Image Generation (OpenAI)
    # `gpt-image-2` is the current OpenAI flagship image-generation
    # model. We keep output as PNG because the API returns base64 bytes
    # and PNG is the simplest format to serve/debug locally.
    OPENAI_IMAGE_MODEL: str = "gpt-image-2"
    OPENAI_IMAGE_QUALITY: str = "medium"
    OPENAI_IMAGE_OUTPUT_FORMAT: str = "png"
    IMAGEGEN_CACHE_DIR: str = "app/ai/imagegen/_cache"
    IMAGEGEN_PUBLIC_URL_PREFIX: str = "/images"

    # Blog cover images. Stored on disk like the AI media blobs and served
    # publicly via a StaticFiles mount (set up in app/main.py). Path is
    # RELATIVE to backend/ so it works regardless of where uvicorn launches.
    BLOG_MEDIA_CACHE_DIR: str = "app/modules/blog/_media"
    BLOG_MEDIA_PUBLIC_URL_PREFIX: str = "/blog-media"

    # Vector DB (Pinecone)
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str = "lingosai-responses"
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"
    PINECONE_FEEDBACK_NAMESPACE: str = "feedback_memory"

    # RAG / Embeddings
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSIONS: int = 1024
    # A normalized mistake must appear in at least this many of the learner's
    # past activities to count as a "recurring pattern" in the Coach's Note.
    RAG_RECURRENCE_MIN_COUNT: int = 2
    # Phase 2: make per-activity feedback memory-aware (advisory only, never
    # changes scoring). Off by default — keeps current behavior unchanged.
    RAG_PER_ACTIVITY_FEEDBACK: bool = False
    # Kept short so RAG retrieval fails fast and degrades gracefully: when a
    # vector call is slow, retrieve_context_for_feedback drops the Pinecone
    # context and the Coach's Note is still generated from Postgres-only data.
    OPENAI_EMBEDDING_TIMEOUT_S: float = 8.0
    PINECONE_OPERATION_TIMEOUT_S: float = 8.0
    # Whole-operation ceiling for the Coach's Note. The completion path streams
    # the scorecard immediately, shows a "generating…" placeholder, then awaits
    # ensure_mentor_note up to this long before showing a fallback. It must
    # comfortably cover embedding + Pinecone retrieval + the LLM generation.
    RAG_MENTOR_NOTE_TIMEOUT_S: float = 30.0
    # Cap on the (flagged) per-activity memory retrieval so enabling
    # RAG_PER_ACTIVITY_FEEDBACK can never add tens of seconds to a submit.
    RAG_PER_ACTIVITY_TIMEOUT_S: float = 5.0

    # Find and read .env file
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )



# Single shared instance
settings = Settings()
