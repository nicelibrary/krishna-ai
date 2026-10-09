import os
import json
from datetime import datetime

# ================================
# SUPABASE CONNECTION
# ================================
def get_supabase():
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_KEY", "")
        if url and key:
            return create_client(url, key)
        return None
    except Exception as e:
        print(f"Supabase connect error: {e}")
        return None

# ================================
# 1. FARMER SAVE KARO
# ================================
def save_farmer(farmer_data: dict) -> str:
    try:
        supabase = get_supabase()

        if supabase:
            result = supabase.table("farmers")\
                .insert(farmer_data)\
                .execute()
            return result.data[0]["id"]
        else:
            # Local save (jab tak Supabase na ho)
            save_local("farmers.json", farmer_data)
            return farmer_data.get("phone", "unknown")

    except Exception as e:
        print(f"Save farmer error: {e}")
        save_local("farmers.json", farmer_data)
        return farmer_data.get("phone", "unknown")

# ================================
# 2. FARMER DHUNDO
# ================================
def get_farmer(phone: str) -> dict:
    try:
        supabase = get_supabase()

        if supabase:
            result = supabase.table("farmers")\
                .select("*")\
                .eq("phone", phone)\
                .execute()
            if result.data:
                return result.data[0]
            return None
        else:
            # Local se dhundo
            return get_local_farmer("farmers.json", phone)

    except Exception as e:
        print(f"Get farmer error: {e}")
        return None

# ================================
# 3. DISEASE QUERY SAVE KARO
# ================================
def save_disease_query(
    farmer_phone: str,
    disease: str,
    confidence: float,
    treatment: str,
    severity: str
):
    try:
        query_data = {
            "farmer_phone": farmer_phone,
            "detected_disease": disease,
            "confidence": confidence,
            "treatment_given": treatment,
            "severity": severity,
            "query_date": datetime.now().isoformat()
        }

        supabase = get_supabase()

        if supabase:
            supabase.table("disease_queries")\
                .insert(query_data)\
                .execute()
        else:
            save_local("disease_queries.json", query_data)

        print(f"✅ Query saved: {disease} for {farmer_phone}")

    except Exception as e:
        print(f"Save query error: {e}")

# ================================
# 4. FARMER HISTORY DEKHO
# ================================
def get_farmer_history(phone: str) -> list:
    try:
        supabase = get_supabase()

        if supabase:
            result = supabase.table("disease_queries")\
                .select("*")\
                .eq("farmer_phone", phone)\
                .order("query_date", desc=True)\
                .limit(5)\
                .execute()
            return result.data
        else:
            return get_local_history("disease_queries.json", phone)

    except Exception as e:
        print(f"Get history error: {e}")
        return []

# ================================
# 5. PRICE QUERY SAVE KARO
# ================================
def save_price_query(
    farmer_phone: str,
    crop: str,
    state: str,
    prices: list
):
    try:
        query_data = {
            "farmer_phone": farmer_phone,
            "crop_queried": crop,
            "state": state,
            "prices_returned": json.dumps(prices),
            "query_date": datetime.now().isoformat()
        }

        supabase = get_supabase()

        if supabase:
            supabase.table("price_queries")\
                .insert(query_data)\
                .execute()
        else:
            save_local("price_queries.json", query_data)

    except Exception as e:
        print(f"Save price query error: {e}")

# ================================
# 6. WEATHER QUERY SAVE KARO
# ================================
def save_weather_query(
    farmer_phone: str,
    district: str,
    weather_data: dict
):
    try:
        query_data = {
            "farmer_phone": farmer_phone,
            "district": district,
            "weather_data": json.dumps(weather_data),
            "query_date": datetime.now().isoformat()
        }

        supabase = get_supabase()

        if supabase:
            supabase.table("weather_queries")\
                .insert(query_data)\
                .execute()
        else:
            save_local("weather_queries.json", query_data)

    except Exception as e:
        print(f"Save weather error: {e}")

# ================================
# 7. TOTAL STATS DEKHO
# ================================
def get_stats() -> dict:
    try:
        supabase = get_supabase()

        if supabase:
            farmers = supabase.table("farmers")\
                .select("id", count="exact")\
                .execute()
            queries = supabase.table("disease_queries")\
                .select("id", count="exact")\
                .execute()

            return {
                "total_farmers": farmers.count or 0,
                "total_queries": queries.count or 0,
                "status": "Supabase Connected ✅"
            }
        else:
            return {
                "total_farmers": 0,
                "total_queries": 0,
                "status": "Local Mode (Supabase nahi hai)"
            }

    except Exception as e:
        return {
            "total_farmers": 0,
            "total_queries": 0,
            "status": f"Error: {e}"
        }

# ================================
# LOCAL SAVE (Backup — Supabase na ho tab)
# ================================
def save_local(filename: str, data: dict):
    try:
        existing = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                existing = json.load(f)

        existing.append(data)

        with open(filename, 'w') as f:
            json.dump(existing, f, indent=2)

        print(f"✅ Locally saved to {filename}")

    except Exception as e:
        print(f"Local save error: {e}")

def get_local_farmer(filename: str, phone: str) -> dict:
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                farmers = json.load(f)
            for farmer in farmers:
                if farmer.get("phone") == phone:
                    return farmer
        return None
    except Exception as e:
        return None

def get_local_history(filename: str, phone: str) -> list:
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                queries = json.load(f)
            return [q for q in queries
                    if q.get("farmer_phone") == phone][:5]
        return []
    except Exception as e:
        return []
