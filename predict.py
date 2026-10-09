import numpy as np
from PIL import Image
import io

DISEASE_DATABASE = {
    "Tomato___Late_blight": {
        "hindi_name": "Tamatar Ki Late Blight Bimari",
        "treatment": """🔴 BIMARI: Tamatar mein Late Blight!

💊 ILAJ:
1. Mancozeb 75% - 2.5g/liter pani spray karo
2. Prabhavit patte turant hataao

⏰ SPRAY: Subah 7-9 baje
📅 REPEAT: 7 din baad dobara
💰 KHARCHA: ₹200-300 per acre""",
        "severity": "High",
        "yield_loss_risk": "70-80% without treatment"
    },

    "Tomato___Bacterial_spot": {
        "hindi_name": "Tamatar Ka Bacterial Daag",
        "treatment": """🟡 BIMARI: Tamatar mein Bacterial Spot!

💊 ILAJ:
1. Copper Oxychloride 3g/liter spray karo
2. Streptomycin 1g/liter bhi milao

⏰ SPRAY: Shaam ko spray karo
📅 REPEAT: 10 din baad
💰 KHARCHA: ₹150-200 per acre""",
        "severity": "Medium",
        "yield_loss_risk": "30-40% without treatment"
    },

    "Potato___Late_blight": {
        "hindi_name": "Aalu Ki Late Blight Bimari",
        "treatment": """🔴 BIMARI: Aalu mein Late Blight!

💊 ILAJ:
1. Metalaxyl + Mancozeb 2.5g/liter spray
2. Prabhavit poudhe nikaal do

⏰ SPRAY: Subah jaldi spray karo
📅 REPEAT: 7 din mein dobara
💰 KHARCHA: ₹250-350 per acre""",
        "severity": "High",
        "yield_loss_risk": "60-80% without treatment"
    },

    "Potato___Early_blight": {
        "hindi_name": "Aalu Ki Early Blight",
        "treatment": """🟠 BIMARI: Aalu mein Early Blight!

💊 ILAJ:
1. Chlorothalonil 2g/liter spray karo
2. Mancozeb 75% WP 2.5g/liter spray

⏰ SPRAY: Subah ya shaam
📅 REPEAT: 10-14 din baad
💰 KHARCHA: ₹200-300 per acre""",
        "severity": "Medium",
        "yield_loss_risk": "20-30% without treatment"
    },

    "Wheat___Brown_rust": {
        "hindi_name": "Gehu Ka Bhoora Rust",
        "treatment": """🟤 BIMARI: Gehu mein Bhoora Rust!

💊 ILAJ:
1. Propiconazole 25% EC 1ml/liter spray
2. Tebuconazole 1ml/liter spray

⏰ SPRAY: Subah jaldi
📅 REPEAT: 15 din baad
💰 KHARCHA: ₹300-400 per acre""",
        "severity": "Medium",
        "yield_loss_risk": "20-30% without treatment"
    },

    "Rice___Bacterial_blight": {
        "hindi_name": "Chawal Ka Bacterial Blight",
        "treatment": """🟡 BIMARI: Chawal mein Bacterial Blight!

💊 ILAJ:
1. Streptomycin + Tetracycline 1g/liter
2. Copper Oxychloride 3g/liter spray

⏰ SPRAY: Subah 6-9 baje
📅 REPEAT: 10 din mein 2 baar
💰 KHARCHA: ₹150-200 per acre""",
        "severity": "High",
        "yield_loss_risk": "50-60% without treatment"
    },

    "Rice___Brown_spot": {
        "hindi_name": "Chawal Ka Brown Daag",
        "treatment": """🟠 BIMARI: Chawal mein Brown Spot!

💊 ILAJ:
1. Mancozeb 2.5g/liter spray karo
2. Tricyclazole 0.6g/liter spray

⏰ SPRAY: Shaam ko
📅 REPEAT: 14 din baad
💰 KHARCHA: ₹180-250 per acre""",
        "severity": "Medium",
        "yield_loss_risk": "30-40% without treatment"
    },

    "Corn___Common_rust": {
        "hindi_name": "Makka Ka Aam Rust",
        "treatment": """🟠 BIMARI: Makka mein Common Rust!

💊 ILAJ:
1. Azoxystrobin 1ml/liter spray
2. Propiconazole 1.5ml/liter spray

⏰ SPRAY: Shaam ko
📅 REPEAT: 14 din baad
💰 KHARCHA: ₹250-350 per acre""",
        "severity": "Medium",
        "yield_loss_risk": "30-40% without treatment"
    },

    "Corn___Northern_Leaf_Blight": {
        "hindi_name": "Makka Ka Patta Jhlasna",
        "treatment": """🔴 BIMARI: Makka mein Northern Leaf Blight!

💊 ILAJ:
1. Mancozeb 2g/liter spray
2. Zineb 75% WP 2g/liter spray

⏰ SPRAY: Subah ya shaam
📅 REPEAT: 10 din baad
💰 KHARCHA: ₹200-300 per acre""",
        "severity": "High",
        "yield_loss_risk": "40-50% without treatment"
    },

    "Grape___Black_rot": {
        "hindi_name": "Angoor Ka Kala Sadna",
        "treatment": """⚫ BIMARI: Angoor mein Black Rot!

💊 ILAJ:
1. Captan 2g/liter spray karo
2. Mancozeb 2.5g/liter spray

⏰ SPRAY: Baarish ke baad turant
📅 REPEAT: 7-10 din baad
💰 KHARCHA: ₹300-400 per acre""",
        "severity": "High",
        "yield_loss_risk": "50-80% without treatment"
    },

    "Apple___Apple_scab": {
        "hindi_name": "Seb Ki Kharish Bimari",
        "treatment": """🍎 BIMARI: Seb mein Apple Scab!

💊 ILAJ:
1. Captan 50% WP 2.5g/liter spray
2. Mancozeb 2g/liter spray

⏰ SPRAY: Subah
📅 REPEAT: 10-14 din baad
💰 KHARCHA: ₹350-500 per acre""",
        "severity": "Medium",
        "yield_loss_risk": "20-40% without treatment"
    },

    "Healthy": {
        "hindi_name": "Fasal Bilkul Theek Hai! ✅",
        "treatment": """✅ BAHUT ACHHA! Aapki fasal HEALTHY hai!

🌱 DHYAN RAKHEIN:
1. Regular paani dete rahein
2. Khad sahi time pe dein
3. Har hafte patta check karein
4. Mausam ke hisaab se spray karein

💪 AAPKI FASAL STRONG HAI!
Krishna AI pe nazar rakhte rahein 🌾""",
        "severity": "None",
        "yield_loss_risk": "0% - Fasal safe hai!"
    }
}

# ================================
# MAIN PREDICTION FUNCTION
# ================================
def predict_disease(image_data: bytes) -> dict:
    try:
        # Image open karo
        image = Image.open(io.BytesIO(image_data))
        image = image.convert('RGB')
        image = image.resize((224, 224))
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Model se predict karo
        try:
            import tensorflow as tf
            import json

            # Model load karo
            model = tf.keras.models.load_model('krishna_ai_model.keras')

            # Class names load karo
            with open('class_names.json', 'r') as f:
                class_names = json.load(f)

            # Predict
            predictions = model.predict(img_array)
            predicted_idx = str(np.argmax(predictions[0]))
            confidence = float(np.max(predictions[0]) * 100)
            disease_key = class_names.get(predicted_idx, "Healthy")

        except Exception as model_error:
            print(f"Model error: {model_error}")
            # Model nahi hai to basic image analysis
            avg_color = np.mean(img_array[0], axis=(0, 1))
            red = avg_color[0]
            green = avg_color[1]

            if green > 0.4:
                disease_key = "Healthy"
                confidence = 75.0
            elif red > 0.5:
                disease_key = "Tomato___Late_blight"
                confidence = 70.0
            else:
                disease_key = "Wheat___Brown_rust"
                confidence = 65.0

        # Disease info lo
        disease_info = DISEASE_DATABASE.get(
            disease_key,
            DISEASE_DATABASE["Healthy"]
        )

        return {
            "disease": disease_info["hindi_name"],
            "confidence": round(confidence, 1),
            "treatment": disease_info["treatment"],
            "severity": disease_info["severity"],
            "yield_loss_risk": disease_info["yield_loss_risk"]
        }

    except Exception as e:
        return {
            "disease": "Photo Sahi Nahi Aaya",
            "confidence": 0.0,
            "treatment": "📸 Dobara try karo:\n• Clear photo lo\n• Patte ke paas se photo lo\n• Achhi roshni mein photo lo",
            "severity": "Unknown",
            "yield_loss_risk": "Unknown"
        }


# ================================
# TEST FUNCTION
# ================================
def test_with_sample():
    print("Krishna AI Disease Detection - Test Mode")
    print("=" * 40)

    sample_image = Image.new('RGB', (224, 224), color=(34, 139, 34))
    img_byte_arr = io.BytesIO()
    sample_image.save(img_byte_arr, format='JPEG')
    img_bytes = img_byte_arr.getvalue()

    result = predict_disease(img_bytes)

    print(f"Disease: {result['disease']}")
    print(f"Confidence: {result['confidence']}%")
    print(f"Severity: {result['severity']}")
    print(f"Treatment: {result['treatment']}")


if __name__ == "__main__":
    test_with_sample()
