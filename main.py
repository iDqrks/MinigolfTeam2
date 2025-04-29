from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg
import os
import config
from queries import INSERT_SCORE

# Initialize app
app = FastAPI(
    docs_url=None,
    redoc_url=None,
)

# Allow CORS
origins = config.allowed_origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Define request model for posting scores
class Score(BaseModel):
    username: str
    score: int
    time_seconds: int

# Routes

@app.get("/")
def read_root():
    return JSONResponse(content={"message": "Hello we are BrainPutt"})

@app.post("/scores/")
async def create_score(score: Score):
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(INSERT_SCORE, (score.username, score.score, score.time_seconds))
                inserted_id = cur.fetchone()[0]
                conn.commit()

        return {"id": inserted_id, "message": "Score successfully added"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
