from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add backend directories to path so imports work
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)
sys.path.append(os.path.join(backend_dir, "rag_service", "src"))
sys.path.append(os.path.join(backend_dir, "shap_service"))
sys.path.append(os.path.join(backend_dir, "rl_service"))

from rag_service.src.knowledge_assistant.api.main import app as rag_app
from rl_service.api import router as rl_router
from shap_service.app.main import app as shap_app

app = FastAPI(title="AI-VENGERS Unified API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the RAG service endpoints under /rag
app.mount("/rag", rag_app)

# Mount the SHAP service endpoints under /shap
app.mount("/shap", shap_app)

# Include the RL service router under /policy
app.include_router(rl_router, prefix="/policy")

@app.get("/health")
def health():
    return {"status": "ok", "message": "Unified AI-VENGERS backend is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
