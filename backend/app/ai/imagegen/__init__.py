"""Image-generation package.

Public surface (what callers should import):

    from app.ai.imagegen import (
        get_default_imagegen_service,
        CachedImageGenService,
        IImageGenClient,
        GeneratedImage,
        ImageResult,
        AspectRatio,
        ImageGenError,
        ImageGenValidationError,
    )
"""

from app.ai.imagegen.cache import (
    CachedImageGenService,
    _reset_default_imagegen_service,
    get_default_imagegen_service,
)
from app.ai.imagegen.exceptions import (
    ImageGenAuthError,
    ImageGenError,
    ImageGenProviderError,
    ImageGenRateLimited,
    ImageGenTimeout,
    ImageGenValidationError,
)
from app.ai.imagegen.interface import (
    AspectRatio,
    GeneratedImage,
    IImageGenClient,
    ImageResult,
)
from app.ai.imagegen.openai_client import (
    OpenAIImageGenClient,
    _reset_default_imagegen_client,
    get_default_imagegen_client,
)

__all__ = [
    "CachedImageGenService",
    "get_default_imagegen_service",
    "_reset_default_imagegen_service",
    "OpenAIImageGenClient",
    "get_default_imagegen_client",
    "_reset_default_imagegen_client",
    "IImageGenClient",
    "GeneratedImage",
    "ImageResult",
    "AspectRatio",
    "ImageGenError",
    "ImageGenTimeout",
    "ImageGenRateLimited",
    "ImageGenAuthError",
    "ImageGenProviderError",
    "ImageGenValidationError",
]
