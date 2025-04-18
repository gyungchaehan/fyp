from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from io import StringIO
from price import download_oil_prices
from articles import fetch_and_store_news
# from nlp import analyze_news_articles
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

# @app.options("/predict")
# async def options_predict():
#     return JSONResponse(
#         content=None,
#         headers={
#             "Access-Control-Allow-Origin": "http://localhost:3000",
#             "Access-Control-Allow-Methods": "POST, OPTIONS",
#             "Access-Control-Allow-Headers": "Content-Type"
#         }
#     )

# @app.post("/predict")
# async def predict(file: UploadFile = File(...)):
#     try:
#         # Read CSV
#         contents = await file.read()
#         df = pd.read_csv(StringIO(contents.decode('utf-8')))

#         # Validate columns
#         required_columns = {'sentiment_score', 'historical_price'}
#         if not required_columns.issubset(df.columns):
#             raise HTTPException(400, "CSV must contain 'sentiment_score' and 'historical_price'")

#         # Validate minimum data points
#         if len(df) < 14:
#             raise HTTPException(400, "Minimum 14 data points required")

#         # Scale prices
#         prices = df['historical_price'].values.reshape(-1, 1)
#         df['scaled_price'] = price_scaler.fit_transform(prices)

#         # Prepare sequences (adjust `sequence_length` based on model)
#         sequence_length = 14
#         input_sequences = []
#         for i in range(len(df) - sequence_length + 1):
#             seq = df[['scaled_price', 'sentiment_score']].iloc[i:i+sequence_length].values
#             input_sequences.append(seq)
#         input_data = np.array(input_sequences)

#         # Debug input shape
#         print(f"Input shape: {input_data.shape}")

#         # Predict
#         prediction = model.predict(input_data)
#         prediction = price_scaler.inverse_transform(prediction.reshape(-1, 1))

#         return JSONResponse(
#             content={"status": "success", "prediction": float(prediction[-1][0])},
#             headers={"Access-Control-Allow-Origin": "http://localhost:3000"}
#         )

#     except HTTPException as he:
#         return JSONResponse(
#             status_code=he.status_code,
#             content={"error": he.detail},
#             headers={"Access-Control-Allow-Origin": "http://localhost:3000"}
#         )
#     except Exception as e:
#         print(f"❌ Server error: {e}")
#         return JSONResponse(
#             status_code=500,
#             content={"error": str(e)},
#             headers={"Access-Control-Allow-Origin": "http://localhost:3000"}
#         )


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
        print(data.get("try"))  # Debugging

        # UNCOMMENT THESE
        # Price API
        # download_oil_prices()
        # fetch_and_store_news()
        # analyze_news_article()

        # TEST
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