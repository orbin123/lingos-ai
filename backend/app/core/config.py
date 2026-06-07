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
    # Free-trial length for users who have not purchased. Used to derive a
    # trial-end date (signup + TRIAL_DAYS) in the admin Subscribers view.
    TRIAL_DAYS: int = 7

    # AI / LLM
    OPENAI_API_KEY: str
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_API_KEY: str
    LANGCHAIN_PROJECT: str = "ai-english-coach"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"

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
