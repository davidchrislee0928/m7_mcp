# macro_engine.py (M7-ALPHA Macro Multi-Factor Storage Center - English Edition)
import os
import json
import datetime
import requests
import traceback
import yfinance as yf

# =====================================================================
# 💾 Dynamic persistence path binding for /data directory
# =====================================================================
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

if os.path.exists("/data"):
    BASE_CACHE_DIR = "/data"
    print("🚀 [M7-MACRO] Cloud storage persistent disk detected! Binding macro factor path to: /data")
else:
    BASE_CACHE_DIR = PROJECT_ROOT
    print("💻 [M7-MACRO] No cloud disk detected. Falling back to local development path.")

# Cache directory aligned with system isolation
CACHE_DIR = os.path.join(BASE_CACHE_DIR, "data_cache")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        os.chmod(CACHE_DIR, 0o777)
    except:
        pass


def get_macro_indicators() -> dict:
    """
    Fetch and cache global core macroeconomic factors.
    24-hour daily cache: Reads directly from local JSON cache within 24 hours to prevent API rate limiting.
    Structure: Returns both latest value (val) and previous value (prev) for front-end rendering.
    """
    cache_file = os.path.join(CACHE_DIR, "m7_macro_capsule.json")
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    # 🛡️ Cache hit defense
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_bundle = json.load(f)
            if cache_bundle.get("fetched_at") == today_str:
                cached_data = cache_bundle.get("data", {})
                # Validate schema integrity
                if cached_data.get("US Dollar Index", {}).get("val", "N/A") != "N/A":
                    print(f"🟢 [M7-MACRO] Cache hit: Successfully loaded local macro capsule. Cache Date: {today_str}")
                    return cached_data
        except Exception as cache_err:
            print(f"⚠️ [M7-MACRO] Cache parsing error: {cache_err}. Forcing network fetch...")

    print("📡 [M7-MACRO] Offline cache expired or missing. Fetching global macro factors via live gateway...")
    
    # Initialize standard macro benchmark snapshot
    macro_snapshot = {
        "US Dollar Index": {"val": "N/A", "prev": "N/A"},
        "10Y Treasury Yield": {"val": "N/A", "prev": "N/A"},
        "Brent Crude Oil": {"val": "N/A", "prev": "N/A"},
        "Non-Farm Payrolls": {"val": "+253K (Prev: 165K)", "prev": "STATIC"},  
        "Core CPI YoY": {"val": "3.6% (In Line)", "prev": "STATIC"},
        "PPI MoM": {"val": "+0.2% (Controlled)", "prev": "STATIC"}
    }
    
    # High-frequency real-time market target mapping
    market_map = {
        "US Dollar Index": "DX-Y.NYB",
        "10Y Treasury Yield": "^TNX",
        "Brent Crude Oil": "BZ=F"
    }
    
    for key, ticker in market_map.items():
        try:
            # Download 5-day historical data to avoid weekend/holiday NaN truncation
            df = yf.download(ticker, period="5d", interval="1d", auto_adjust=True, group_by='ticker')
            if not df.empty:
                if 'Close' in df.columns:
                    close_series = df['Close']
                else:
                    close_series = df.iloc[:, df.columns.get_level_values(-1) == 'Close']
                
                raw_values = close_series.dropna().values.flatten()
                if len(raw_values) >= 2:
                    current_val = float(raw_values[-1])
                    previous_val = float(raw_values[-2])
                    
                    # Format Treasury Yield as percentage; keep 2 decimals for others
                    if key == "10Y Treasury Yield":
                        macro_snapshot[key] = {
                            "val": f"{current_val:.3f}%",
                            "prev": f"{previous_val:.3f}%"
                        }
                    else:
                        macro_snapshot[key] = {
                            "val": f"{current_val:.2f}",
                            "prev": f"{previous_val:.2f}"
                        }
                elif len(raw_values) == 1:
                    macro_snapshot[key] = {"val": f"{float(raw_values[0]):.2f}", "prev": "N/A"}
                else:
                    print(f"⚠️ [M7-MACRO] Target [{key}] close price series is empty.")
        except Exception as yf_err:
            print(f"❌ [M7-MACRO] Error fetching [{key}] from Yahoo Finance: {yf_err}")
            traceback.print_exc()

    # 3. Save persistent cache to disk
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"fetched_at": today_str, "data": macro_snapshot}, f, ensure_ascii=False, indent=2)
        print("💾 [M7-MACRO] Global macro benchmark data successfully saved to persistent disk.")
    except Exception as save_err:
        print(f"⚠️ [M7-MACRO] Error saving macro cache file: {save_err}")
        
    return macro_snapshot

if __name__ == "__main__":
    print("\n🔥 [M7-TEST] Initiating standalone test run...")
    res = get_macro_indicators()
    print("\n" + "█"*30 + " M7 MACRO EXTRACT RESULT " + "█"*30)
    print(json.dumps(res, indent=4, ensure_ascii=False))
    print("█"*85)