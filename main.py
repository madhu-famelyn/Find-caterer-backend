from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Import your API router
from apis.caterer.caterer import router as caterer_router  # <-- Import router
from apis.user.user import router as user_router
from apis.admin.admin import router as admin_router 
from apis.message.message import router as message_router

# -------------------------------------------------
# Lifespan (startup / shutdown)
# -------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    print("🚀 FastAPI application starting...")
    # Example: await connect_to_db()
    yield
    # SHUTDOWN
    print("🛑 FastAPI application shutting down...")
    # Example: await close_db()

# -------------------------------------------------
# App initialization
# -------------------------------------------------
app = FastAPI(
    title="Find Caterer Backend",
    description="FastAPI backend service",
    version="1.0.0",
    lifespan=lifespan
)

# -------------------------------------------------
# CORS (adjust for production)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Health Check
# -------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "service": "fastapi",
        }
    )

# -------------------------------------------------
# Root endpoint
# -------------------------------------------------
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "FastAPI server is running successfully"
    }

# -------------------------------------------------
# Include Caterer router
# -------------------------------------------------
app.include_router(caterer_router, prefix="/api/v1/caterers", tags=["Caterers"])
app.include_router(user_router, prefix="/api/v1/user", tags=["User"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(message_router, prefix="/api/v1/admin", tags=["Message"])

# -------------------------------------------------
# Run with: python main.py
# -------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
