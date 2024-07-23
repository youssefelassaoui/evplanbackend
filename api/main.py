# from broadcaster import Broadcast

# from fastapi import FastAPI, WebSocket, Request
# from fastapi.responses import HTMLResponse
# from fastapi.concurrency import run_until_first_complete


from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware

import api.routers.websocket as websocket
import api.routers.values as values
import api.routers.input_layers as input_layers
import api.routers.auth as auth
import api.routers.map as map
import api.routers.algorithms as algorithms
from api.constants import CORS_ORIGINS
from api.database import engine
from api.models import models

app = FastAPI()

  

    
# Config app middlewares (gzip and CORS)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Connect with DB
models.Base.metadata.create_all(bind=engine)

# Include endpoints routers
app.include_router(websocket.router)
app.include_router(values.router)
app.include_router(input_layers.router)
app.include_router(auth.router)
app.include_router(map.router)
app.include_router(algorithms.router)