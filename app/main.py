from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from app.pipeline.receipt_pipeline import run_pipeline
from app.calculate import calculate_total   

app = FastAPI(title="Carbon Scanner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict-carbon")
async def predict(file: UploadFile = File(...)):
    return run_pipeline(file)


@app.post("/calculate-carbon")
async def calculate_carbon(payload: dict):
    return calculate_total(payload["items"])
