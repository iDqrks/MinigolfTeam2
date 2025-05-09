from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg
import os
from queries import INSERT_SCORE, GET_SCORES

app = FastAPI(docs_url=None, redoc_url=None)

# CORS-instellingen
allowed_origins = ["*", "http://localhost:*", "https://brain-putt.vercel.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Databaseverbinding
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Pydantic model voor POST request
class Score(BaseModel):
    username: str
    score: int
    time_seconds: int

@app.get("/")
async def read_root():
    return {"message": "Hello we are BrainPutt"}

@app.post("/scores/add/")
async def create_score(score: Score):
    if not score.username or len(score.username) > 50:
        raise HTTPException(status_code=400, detail="Username must be between 1 and 50 characters")
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(INSERT_SCORE, (score.username, score.score, score.time_seconds))
                inserted_id = cur.fetchone()[0]
                conn.commit()
        return {"id": inserted_id, "message": "Score successfully added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scores/")
async def get_scores():
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(GET_SCORES)
                scores = cur.fetchall()
        return [
            {"username": score[0], "score": score[1], "time_seconds": score[2]}
            for score in scores
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))