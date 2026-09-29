import uvicorn

from immo_paris.core.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "immo_paris.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
