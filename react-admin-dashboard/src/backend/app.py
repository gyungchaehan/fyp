from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from io import StringIO

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

@app.on_event("startup")
async def startup_event():
    global model, price_scaler
    model = load_model('model/best_model.h5')
    
    # Initialize scaler with reasonable defaults
    price_scaler = MinMaxScaler(feature_range=(0, 1))

# Add OPTIONS handler for preflight requests
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
        csv_string = StringIO(contents.decode('utf-8'))
        df = pd.read_csv(csv_string)

        # Validate columns
        required_columns = {'sentiment_score', 'historical_price'}
        if not required_columns.issubset(df.columns):
            raise HTTPException(
                status_code=400,
                detail="CSV must contain 'sentiment_score' and 'historical_price' columns"
            )

        # Validate minimum data points
        if len(df) < 14:
            raise HTTPException(
                status_code=400,
                detail="Minimum 14 data points required"
            )

        # Apply MinMax scaling
        prices = df['historical_price'].values.reshape(-1, 1)
        df['scaled_price'] = price_scaler.fit_transform(prices)

        # Prepare input data
        input_data = []
        for _, row in df.iterrows():
            input_data.append([
                row['scaled_price'],
                row['sentiment_score']
            ])
        prediction = model.predict(np.array([input_data]))
        prediction = price_scaler.inverse_transform(prediction)
        return JSONResponse(
            content={
                "status": "success",
                "prediction": float(prediction[0][0])
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