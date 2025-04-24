from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from io import StringIO

# internal modules
import articles, price, nlp, spider

from lstm import LSTMPredictor
from bigru import BiGRUPredictor


app = FastAPI()

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app's URL
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],  # Specify only needed methods
    allow_headers=["Content-Type", "Authorization"],  # Specify needed headers
    expose_headers=["Content-Disposition"]  # Expose custom headers if needed
)

@app.on_event("startup")
async def startup_event():
    global lstm_pred, bigru_pred
    lstm_pred = LSTMPredictor()
    bigru_pred = BiGRUPredictor()


@app.options("/getRealTime")
async def options_getRealTime():
    return JSONResponse(
        content=None,
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )


@app.post("/getRealTime")
async def getRealTime(request: Request):
    try:
        data = await request.json()
        # print(data.get("try"))  # Debugging

        price.start()
        articles.start()
        spider.start()
        nlp.start()

        lstm_predictions = lstm_pred.run_lstm_pipeline()
        bigru_pred.set_lstm_prices(lstm_predictions)
        final = bigru_pred.run_bigru_pipeline()
        
        return JSONResponse(
            content={
                "status": "success",
                "message": "Real-time prediction received",
                "data": final
            },
            headers={
                "Access-Control-Allow-Origin": "http://localhost:3000",
                "Access-Control-Expose-Headers": "*"
            }
        )

    except HTTPException as he:
        return JSONResponse(
            status_code=he.status_code,
            content={"error": he.detail},
            headers={
                "Access-Control-Allow-Origin": "http://localhost:3000"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
            headers={
                "Access-Control-Allow-Origin": "http://localhost:3000"
            }
        )
