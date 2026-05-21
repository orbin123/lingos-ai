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

    # Embeddings (HuggingFace)
    HF_API_KEY: str
    HF_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Curriculum dev-mode override.
    # "db"   — read curriculum from CurriculumWeek/CurriculumDay rows (default).
    # "file" — read directly from `app/data/courses/curriculum_v2/source_24w.py`.
    #          In file mode the session flow bypasses CurriculumDayRepository
    #          and the planner; day identity is (week_number, day_index).
    CURRICULUM_SOURCE: str = "db"

    # When true, `SessionService.complete_session` skips
    # `apply_session_scorecard` and `StreakService.record_in_same_tx`.
    # Used during the file-driven authoring phase so we can iterate on
    # chat-session content without touching points/streak tables.
    STUB_PROGRESS_WRITES: bool = False

    # Ephemeral chat authoring mode.
    # Disabled by default. When enabled, the dev-only `/api/dev/learning/*`
    # and `/dev/ws/learning/*` endpoints read `source_24w.py` directly and
    # keep session state in memory instead of touching curriculum/session DB
    # tables. Intended only for local curriculum authoring.
    AUTHORING_CHAT_MODE: bool = False
    AUTHORING_CHAT_REQUIRE_AUTH: bool = False
    AUTHORING_CHAT_COURSE_LENGTH: str = "24w"

    # Find and read .env file
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )



# Single shared instance
settings = Settings()
