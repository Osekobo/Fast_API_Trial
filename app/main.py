from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, applications, users, reviews, reports, announcements,payments
from .database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Borabu Bursary API", version="1.0")

# CORS – allow specific frontend origins
origins = [
    "http://localhost:5173",   # Vite default
    "http://localhost:3000",   # Alternative
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(users.router)
app.include_router(reviews.router)
app.include_router(reports.router)
app.include_router(announcements.router)
app.include_router(payments.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Database tables created/verified.")

@app.get("/")
async def root():
    return {"message": "Borabu Bursary API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)