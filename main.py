from fastapi import FastAPI
import config
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    docs_url=None,
    redoc_url=None,
)

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def read_root():
    return JSONResponse(content={"message": "Hello we are BrainPutt"})

origins = config.allowed_origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)