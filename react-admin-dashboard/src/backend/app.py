from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from io import StringIO
from preprocessing import DataPreprocessor

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

model = None
price_scaler = None
preprocessor = DataPreprocessor()

@app.on_event("startup")
async def startup_event():
    global model, price_scaler
    model = load_model('model/best_model.h5')
    # TO DO: LOAD LSTM MODEL
    price_scaler = MinMaxScaler(feature_range=(0, 1))

@app.options("/predict")
async def options_predict():
    return JSONResponse(
        content=None,
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))

        # Validate columns
        required_columns = {'sentiment_score', 'historical_price'}
        if not required_columns.issubset(df.columns):
            raise HTTPException(400, "CSV must contain 'sentiment_score' and 'historical_price'")

        # Validate minimum data points
        if len(df) < 14:
            raise HTTPException(400, "Minimum 14 data points required")

        # Scale prices
        prices = df['historical_price'].values.reshape(-1, 1)
        df['scaled_price'] = price_scaler.fit_transform(prices)

        # Prepare sequences (adjust `sequence_length` based on model)
        sequence_length = 14
        input_sequences = []
        for i in range(len(df) - sequence_length + 1):
            seq = df[['scaled_price', 'sentiment_score']].iloc[i:i+sequence_length].values
            input_sequences.append(seq)
        input_data = np.array(input_sequences)

        # Debug input shape
        print(f"Input shape: {input_data.shape}")

        # Predict
        prediction = model.predict(input_data)
        prediction = price_scaler.inverse_transform(prediction.reshape(-1, 1))

        return JSONResponse(
            content={"status": "success", "prediction": float(prediction[-1][0])},
            headers={"Access-Control-Allow-Origin": "http://localhost:3000"}
        )

    except HTTPException as he:
        return JSONResponse(
            status_code=he.status_code,
            content={"error": he.detail},
            headers={"Access-Control-Allow-Origin": "http://localhost:3000"}
        )
    except Exception as e:
        print(f"❌ Server error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
            headers={"Access-Control-Allow-Origin": "http://localhost:3000"}
        )


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
        input_prices = preprocessor.process_new_prices("data/real_time_oil_prices.csv")
        input_vader = preprocessor.process_vader_scores("data/new_news_data.jsonl")
        print(input_prices)
        print(input_vader)
        predicted_price = preprocessor.predict_for_lstm()
        print(predicted_price)
        bigru_dataset = preprocessor.make_bigru_dataset()
        print(bigru_dataset)
        bigru_output = preprocessor.predict_for_bigru()
        print(bigru_output)
        return JSONResponse(
            content={
                "status": "success",
                "message": "Real-time prediction received",
                "data": data
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