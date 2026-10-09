import requests
import os

META_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID", "")

# ================================
# MAIN MESSAGE HANDLER
# ================================
async def handle_message(data: dict):
    try:
        entry = data.get("entry", [])
        if not entry:
            return

        changes = entry[0].get("changes", [])
        if not changes:
            return

        value = changes[0].get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return

        message = messages[0]
        from_number = message.get("from", "")
        msg_type = message.get("type", "")

        # Text message
        if msg_type == "text":
            text = message["text"]["body"].strip().lower()
            await handle_text(from_number, text)

        # Image message (Disease Detection)
        elif msg_type == "image":
            image_id = message["image"]["id"]
            await handle_image(from_number, image_id)

        # Other types
        else:
            send_message(
                from_number,
                "🌾 Sirf text ya photo bhejein!\n"
                "Help ke liye 'Hi' type karein."
            )

    except Exception as e:
        print(f"Handle message error: {e}")

# ================================
# TEXT MESSAGE HANDLE
# ================================
async def handle_text(phone: str, text: str):
    try:
        # Welcome
        if any(w in text for w in [
            "hi", "hello", "namaste",
            "start", "shuru", "help", "helo"
        ]):
            send_welcome(phone)

        # Disease Detection
        elif any(w in text for w in [
            "1", "bimari", "rog",
            "disease", "photo", "patta"
        ]):
            send_message(
                phone,
                "📸 *Fasal Ki Photo Bhejo!*\n\n"
                "Apni fasal ke patte ki CLEAR photo bhejo\n"
                "Main 30 second mein bata dunga! 🌱\n\n"
                "_Tip: Achhi roshni mein photo lo_"
            )

        # Mandi Price
        elif any(w in text for w in [
            "2", "bhav", "price",
            "mandi", "rate", "dam"
        ]):
            await send_mandi_price(phone)

        # Weather
        elif any(w in text for w in [
            "3", "mausam", "weather",
            "baarish", "barish", "garmi"
        ]):
            await send_weather(phone)

        # Fertilizer
        elif any(w in text for w in [
            "4", "khad", "fertilizer",
            "urea", "dap", "potash"
        ]):
            send_fertilizer_info(phone)

        # Register
        elif any(w in text for w in [
            "5", "register", "join",
            "naam", "name"
        ]):
            send_message(
                phone,
                "📝 *Register Karo Krishna AI Mein!*\n\n"
                "Apna naam aur gaon bhejo:\n"
                "Format: NAAM | GAON | FASAL\n\n"
                "Example:\n"
                "Ramu | Sitapur | Gehu"
            )

        # Default
        else:
            send_message(
                phone,
                "🌾 *Krishna AI*\n\n"
                "Main samajh nahi paya! 😊\n"
                "Neeche se option chunein:\n\n"
                "1️⃣ Fasal Rog Pehchano\n"
                "2️⃣ Mandi Bhav Dekho\n"
                "3️⃣ Mausam Jankari\n"
                "4️⃣ Khaad Ki Salah\n"
                "5️⃣ Register Karo\n\n"
                "_Number type karo (1/2/3/4/5)_"
            )

    except Exception as e:
        print(f"Handle text error: {e}")

# ================================
# IMAGE HANDLE (Disease Detection)
# ================================
async def handle_image(phone: str, image_id: str):
    try:
        # Processing message bhejo
        send_message(
            phone,
            "⏳ *Photo Check Ho Rahi Hai...*\n"
            "30 second wait karo! 🔍"
        )

        # Image download karo
        image_url = get_image_url(image_id)
        if not image_url:
            send_message(
                phone,
                "❌ Photo nahi aaya!\n"
                "Dobara bhejne ki koshish karo 📸"
            )
            return

        image_data = download_image(image_url)
        if not image_data:
            send_message(
                phone,
                "❌ Photo process nahi hua!\n"
                "Thoda baad try karo 🙏"
            )
            return

        # Disease detect karo
        from predict import predict_disease
        result = predict_disease(image_data)

        # Result message
        response = f"""🔍 *KRISHNA AI RESULT:*

🌿 *Bimari:* {result['disease']}
📊 *Pakka:* {result['confidence']}%
⚠️ *Khatarnak:* {result['severity']}
📉 *Nuksan Risk:* {result['yield_loss_risk']}

{result['treatment']}

━━━━━━━━━━━━━━━
🌾 *Krishna AI*
_Koi sawaal? Help type karo_"""

        send_message(phone, response)

        # Database mein save karo
        try:
            from database import save_disease_query
            save_disease_query(
                farmer_phone=phone,
                disease=result['disease'],
                confidence=result['confidence'],
                treatment=result['treatment'],
                severity=result['severity']
            )
        except Exception as db_error:
            print(f"DB save error: {db_error}")

    except Exception as e:
        print(f"Handle image error: {e}")
        send_message(
            phone,
            "😔 Kuch gadbad ho gayi!\n\n"
            "Dobara try karo:\n"
            "• Clear photo lo\n"
            "• Patte ke paas se photo lo\n"
            "• Achhi roshni mein photo lo 📸"
        )

# ================================
# WELCOME MESSAGE
# ================================
def send_welcome(phone: str):
    send_message(
        phone,
        "🌾 *Jai Kisan! Krishna AI Mein Swagat!*\n\n"
        "Main hoon aapka AI Kisan Mitra! 🤖\n"
        "Bilkul FREE | Hindi Mein | 24/7\n\n"
        "━━━━━━━━━━━━━━━\n"
        "Kya seva chahiye?\n\n"
        "1️⃣ *Fasal Rog Pehchano*\n"
        "   📸 Photo bhejo — turant pata chalega\n\n"
        "2️⃣ *Mandi Bhav Dekho*\n"
        "   💰 Aaj ke taaze rates\n\n"
        "3️⃣ *Mausam Jankari*\n"
        "   🌤️ 3 din ka mausam haal\n\n"
        "4️⃣ *Khaad Ki Salah*\n"
        "   🌱 Sahi khad ki jankari\n\n"
        "5️⃣ *Register Karo*\n"
        "   📝 Member bano — free!\n\n"
        "━━━━━━━━━━━━━━━\n"
        "_Number type karo (1/2/3/4/5)_ 👇"
    )

# ================================
# MANDI PRICE
# ================================
async def send_mandi_price(phone: str):
    try:
        send_message(
            phone,
            "💰 *Konsi Fasal Ka Bhav Chahiye?*\n\n"
            "Crop naam type karo:\n"
            "• Wheat (Gehu)\n"
            "• Rice (Chawal)\n"
            "• Tomato (Tamatar)\n"
            "• Potato (Aalu)\n"
            "• Onion (Pyaz)\n"
            "• Cotton (Kapas)\n\n"
            "_Naam English mein type karo_"
        )
    except Exception as e:
        print(f"Mandi price error: {e}")

# ================================
# WEATHER INFO
# ================================
async def send_weather(phone: str):
    try:
        import requests as req

        # Default UP ka weather (Lucknow)
        lat = 26.85
        lon = 80.95

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

        response = req.get(url, params=params)
        data = response.json()
        daily = data.get("daily", {})

        weather_text = "🌤️ *3 Din Ka Mausam:*\n\n"

        days = ["Aaj", "Kal", "Parson"]
        for i in range(3):
            rain = daily["precipitation_sum"][i]
            rain_chance = daily["precipitation_probability_max"][i]
            max_temp = daily["temperature_2m_max"][i]
            min_temp = daily["temperature_2m_min"][i]

            if rain_chance > 70:
                icon = "🌧️"
                alert = "⚠️ Spray MAT karo!"
            elif rain_chance > 40:
                icon = "⛅"
                alert = "Dhyan rakho"
            else:
                icon = "☀️"
                alert = "Spray kar sakte ho ✅"

            weather_text += (
                f"{icon} *{days[i]}:*\n"
                f"🌡️ Temp: {min_temp}°C - {max_temp}°C\n"
                f"💧 Baarish: {rain_chance}% chance\n"
                f"💡 {alert}\n\n"
            )

        weather_text += "━━━━━━━━━━━━━━━\n🌾 _Krishna AI_"

        send_message(phone, weather_text)

    except Exception as e:
        print(f"Weather error: {e}")
        send_message(
            phone,
            "😔 Mausam data abhi nahi mila!\n"
            "Thodi der baad try karo 🙏"
        )

# ================================
# FERTILIZER INFO
# ================================
def send_fertilizer_info(phone: str):
    send_message(
        phone,
        "🌱 *Khaad Ki Salah — Krishna AI*\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "🌾 *GEHU ke liye:*\n"
        "• DAP: 50kg/acre (bowaai ke waqt)\n"
        "• Urea: 33kg/acre (3 baar mein)\n"
        "• Potash: 20kg/acre\n\n"
        "🌾 *CHAWAL ke liye:*\n"
        "• DAP: 45kg/acre\n"
        "• Urea: 40kg/acre (2 baar)\n"
        "• Zinc Sulphate: 10kg/acre\n\n"
        "🌾 *TAMATAR ke liye:*\n"
        "• DAP: 30kg/acre\n"
        "• Urea: 20kg/acre\n"
        "• Potash: 25kg/acre\n\n"
        "━━━━━━━━━━━━━━━\n"
        "⚠️ _Soil test ke baad khaad do_\n"
        "🌾 _Krishna AI_"
    )

# ================================
# SEND MESSAGE
# ================================
def send_message(phone: str, text: str):
    try:
        if not META_TOKEN or not PHONE_NUMBER_ID:
            print(f"MSG to {phone}: {text[:50]}...")
            return

        url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {META_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": text}
        }
        response = requests.post(url, headers=headers, json=data)
        print(f"Message sent: {response.status_code}")

    except Exception as e:
        print(f"Send message error: {e}")

# ================================
# IMAGE URL GET KARO
# ================================
def get_image_url(image_id: str) -> str:
    try:
        url = f"https://graph.facebook.com/v18.0/{image_id}"
        headers = {"Authorization": f"Bearer {META_TOKEN}"}
        response = requests.get(url, headers=headers)
        return response.json().get("url", "")
    except Exception as e:
        print(f"Get image URL error: {e}")
        return ""

# ================================
# IMAGE DOWNLOAD KARO
# ================================
def download_image(url: str) -> bytes:
    try:
        headers = {"Authorization": f"Bearer {META_TOKEN}"}
        response = requests.get(url, headers=headers)
        return response.content
    except Exception as e:
        print(f"Download image error: {e}")
        return None
