from fastapi import FastAPI

app = FastAPI(
    title="ARGOS API",
    version="0.1.0",
    description="Asistente financiero inteligente"
)


@app.get("/")
def root():
    return {
        "project": "ARGOS",
        "version": "0.1.0",
        "status": "healthy"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }