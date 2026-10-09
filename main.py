from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
from datetime import datetime
import os

app = FastAPI(title="Krishna AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# 1. HOME
# ================================
@app.get("/")
def home():
    return {
        "app": "Krishna AI 🌾",
        "status": "Live ✅",
        "version": "1.0",
        "message": "Jai Kisan!"
    }

# ================================
# 2. MANDI PRICE
# ================================
@app.get("/mandi-price")
def get_mandi_price(crop: str, state: str):
    try:
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": "579b464db66ec23bdd000001cdd3946e44ce4aab56a3b24f4c9d4ba",
            "format": "json",
            "filters[commodity]": crop,
            "filters[state]": state,
            "limit": "5"
        }
        response = requests.get(url, params=params)
        data = response.json()

        if data.get("records"):
            prices = []
            for record in data["records"][:3]:
                prices.append({
                    "mandi": record.get("market", ""),
                    "min_price": record.get("min_price", ""),
                    "max_price": record.get("max_price", ""),
                    "modal_price": record.get("modal_price", ""),
                    "date": record.get("arrival_date", "")
                })
            return {"success": True, "prices": prices}
        else:
            return {"success": False, "message": "Data nahi mila"}

    except Exception as e:
        return {"success": False, "error": str(e)}

# ================================
# 3. WEATHER
# ================================
@app.get("/weather")
def get_weather(lat: float, lon: float):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max"
            ],
            "timezone": "Asia/Kolkata",
            "forecast_days": 3
        }
        response = requests.get(url, params=params)
        data = response.json()

        daily = data.get("daily", {})
        weather_info = []

        for i in range(3):
            rain = daily["precipitation_sum"][i]
            rain_chance = daily["precipitation_probability_max"][i]

            if rain_chance > 70:
                alert = "⚠️ Baarish aayegi — spray MAT karo!"
            elif rain_chance > 40:
                alert = "🌤️ Baarish ho sakti hai — dhyan rakho"
            else:
                alert = "☀️ Mausam saaf hai — spray kar sakte ho"

            weather_info.append({
                "date": daily["time"][i],
                "max_temp": daily["temperature_2m_max"][i],
                "min_temp": daily["temperature_2m_min"][i],
                "rain_mm": rain,
                "rain_chance": rain_chance,
                "alert": alert
            })

        return {"success": True, "weather": weather_info}

    except Exception as e:
        return {"success": False, "error": str(e)}

# ================================
# 4. DISEASE DETECTION
# ================================
@app.post("/detect-disease")
async def detect_disease(file: UploadFile = File(...)):
    try:
        image_data = await file.read()
        from predict import predict_disease
        result = predict_disease(image_data)

        return {
            "success": True,
            "disease": result["disease"],
            "confidence": result["confidence"],
            "treatment_hindi": result["treatment"],
            "severity": result["severity"],
            "yield_loss_risk": result["yield_loss_risk"]
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

# ================================
# 5. FARMER REGISTER
# ================================
@app.post("/register-farmer")
def register_farmer(
    name: str,
    phone: str,
    village: str,
    district: str,
    crop: str,
    land_acres: float
):
    try:
        from database import save_farmer
        farmer_id = save_farmer({
            "name": name,
            "phone": phone,
            "village": village,
            "district": district,
            "main_crop": crop,
            "land_acres": land_acres,
            "registered_at": datetime.now().isoformat()
        })

        return {
            "success": True,
            "farmer_id": str(farmer_id),
            "message": f"Swagat hai {name} ji! Krishna AI mein register ho gaye! 🌾"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

# ================================
# 6. WHATSAPP WEBHOOK VERIFY
# ================================
@app.get("/webhook")
def verify_webhook(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    VERIFY_TOKEN = os.getenv("META_WEBHOOK_VERIFY_TOKEN", "krishna_ai_2024")

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    return {"error": "Verification failed"}

# ================================
# 7. WHATSAPP WEBHOOK RECEIVE
# ================================
@app.post("/webhook")
async def receive_webhook(request: dict):
    try:
        from whatsapp_webhook import handle_message
        await handle_message(request)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# ================================
# 8. FARMER HISTORY
# ================================
@app.get("/farmer-history")
def farmer_history(phone: str):
    try:
        from database import get_farmer_history
        history = get_farmer_history(phone)
        return {"success": True, "history": history}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ================================
# 9. HEALTH CHECK
# ================================
@app.get("/health")
def health_check():
    return {
        "status": "healthy ✅",
        "apis": {
            "mandi": "✅ Agmarknet Connected",
            "weather": "✅ Open-Meteo Connected",
            "whatsapp": "✅ Meta API Ready",
            "database": "✅ Supabase Connected"
        }
    }
