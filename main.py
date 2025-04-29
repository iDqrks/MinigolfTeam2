from fastapi import FastAPI
import config
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    docs_url=None,
    redoc_url=None,
)

origins = config.allowed_origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)