from mmvm.main import app
from uvicorn import run

if __name__ == "__main__":
    run(
        "mmvm.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[
            "./src",
            "./config"
        ],
        reload_includes=[
            "*.py",
            "*.yaml",
            "*.env"
        ],
        reload_excludes=[
            "*.log",
            "__pycache__",
            "tests/*"
        ],
        log_level="info"
    )
