# macro_engine.py (M7-ALPHA Macro Storage - Enhanced with Publication Dates)
import os
import json
import datetime
import requests
import traceback
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

if os.path.exists("/data"):
    BASE_CACHE_DIR = "/data"
    print("🚀 [M7-MACRO] Cloud storage persistent disk detected! Binding macro factor path to: /data")
else:
    BASE_CACHE_DIR = PROJECT_ROOT
    print("💻 [M7-MACRO] No cloud disk detected. Falling back to local development path.")

CACHE_DIR = os.path.join(BASE_CACHE_DIR, "data_cache")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        os.chmod(CACHE_DIR, 0o777)
    except:
        pass


def fetch_fred_series_with_dates(series_id: str, api_key: str, limit: int = 14) -> list:
    """
    Fetch observations along with release dates directly from FRED API.
    Returns list of dicts: [{"val": float, "date": "YYYY-MM-DD"}, ...]
    """
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json&sort_order=desc&limit={limit}"
    try:
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            obs = res.json().get("observations", [])
            valid_obs = []
            for o in obs:
                val_str = o.get("value")
                if val_str and val_str != ".":
                    valid_obs.append({
                        "val": float(val_str),
                        "date": o.get("date", "")[:7]  # 提取 YYYY-MM
                    })
            return valid_obs
    except Exception as e:
        print(f"⚠️ [M7-MACRO-FRED] Failed to fetch FRED series [{series_id}]: {e}")
    return []


def get_macro_indicators() -> dict:
    cache_file = os.path.join(CACHE_DIR, "m7_macro_capsule.json")
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_bundle = json.load(f)
            if cache_bundle.get("fetched_at") == today_str:
                cached_data = cache_bundle.get("data", {})
                if cached_data.get("US Dollar Index", {}).get("val", "N/A") != "N/A":
                    print(f"🟢 [M7-MACRO] Cache hit: Loaded local macro capsule. Date: {today_str}")
                    return cached_data
        except Exception as cache_err:
            print(f"⚠️ [M7-MACRO] Cache parsing error: {cache_err}. Fetching live...")

    print("📡 [M7-MACRO] Offline cache expired or missing. Fetching global macro factors via live gateway...")
    
    macro_snapshot = {
        "US Dollar Index": {"val": "N/A", "prev": "N/A", "date": ""},
        "10Y Treasury Yield": {"val": "N/A", "prev": "N/A", "date": ""},
        "Brent Crude Oil": {"val": "N/A", "prev": "N/A", "date": ""},
        "Fed Funds Rate": {"val": "N/A", "prev": "N/A", "date": ""},
        "Unemployment Rate": {"val": "N/A", "prev": "N/A", "date": ""},
        "Non-Farm Payrolls": {"val": "N/A", "prev": "N/A", "date": ""},  
        "Core CPI YoY": {"val": "N/A", "prev": "N/A", "date": ""},
        "PPI YoY": {"val": "N/A", "prev": "N/A", "date": ""},
        "PPI MoM": {"val": "N/A", "prev": "N/A", "date": ""}
    }
    
    market_map = {
        "US Dollar Index": "DX-Y.NYB",
        "10Y Treasury Yield": "^TNX",
        "Brent Crude Oil": "BZ=F"
    }
    
    for key, ticker in market_map.items():
        try:
            df = yf.download(ticker, period="5d", interval="1d", auto_adjust=True, group_by='ticker')
            if not df.empty:
                close_series = df['Close'] if 'Close' in df.columns else df.iloc[:, df.columns.get_level_values(-1) == 'Close']
                raw_values = close_series.dropna().values.flatten()
                if len(raw_values) >= 2:
                    current_val = float(raw_values[-1])
                    previous_val = float(raw_values[-2])
                    
                    if key == "10Y Treasury Yield":
                        macro_snapshot[key] = {"val": f"{current_val:.3f}%", "prev": f"{previous_val:.3f}%", "date": "Live"}
                    else:
                        macro_snapshot[key] = {"val": f"{current_val:.2f}", "prev": f"{previous_val:.2f}", "date": "Live"}
        except Exception as yf_err:
            print(f"❌ [M7-MACRO] Error fetching [{key}] from Yahoo Finance: {yf_err}")

    fred_api_key = os.environ.get("FRED_API_KEY")
    print(f"FRED Key detected: {bool(fred_api_key)}")
    if fred_api_key:
        print(f"🔑 [M7-MACRO-FRED] Accessing FRED API with Key...")
        
        # A. Fed Funds Rate
        ffr_obs = fetch_fred_series_with_dates("FEDFUNDS", fred_api_key, limit=2)
        if len(ffr_obs) >= 2:
            macro_snapshot["Fed Funds Rate"] = {
                "val": f"{ffr_obs[0]['val']:.2f}%",
                "prev": f"{ffr_obs[1]['val']:.2f}%",
                "date": ffr_obs[0]['date']
            }

        # B. Unemployment Rate
        unrate_obs = fetch_fred_series_with_dates("UNRATE", fred_api_key, limit=2)
        if len(unrate_obs) >= 2:
            macro_snapshot["Unemployment Rate"] = {
                "val": f"{unrate_obs[0]['val']:.1f}%",
                "prev": f"{unrate_obs[1]['val']:.1f}%",
                "date": unrate_obs[0]['date']
            }

        # C. Core CPI YoY
        cpi_obs = fetch_fred_series_with_dates("CPILFESL", fred_api_key, limit=14)
        if len(cpi_obs) >= 13:
            latest_cpi, prev_year_cpi = cpi_obs[0]['val'], cpi_obs[12]['val']
            prev_month_cpi = cpi_obs[1]['val']
            cpi_yoy = ((latest_cpi - prev_year_cpi) / prev_year_cpi) * 100
            prev_cpi_yoy = ((prev_month_cpi - cpi_obs[13]['val']) / cpi_obs[13]['val']) * 100 if len(cpi_obs) >= 14 else cpi_yoy
            macro_snapshot["Core CPI YoY"] = {
                "val": f"{cpi_yoy:+.1f}%",
                "prev": f"{prev_cpi_yoy:+.1f}%",
                "date": cpi_obs[0]['date']
            }

        # D. Non-Farm Payrolls
        nfp_obs = fetch_fred_series_with_dates("PAYEMS", fred_api_key, limit=3)
        if len(nfp_obs) >= 3:
            total_emp = nfp_obs[0]['val'] / 1000.0
            latest_chg = nfp_obs[0]['val'] - nfp_obs[1]['val']
            prev_chg = nfp_obs[1]['val'] - nfp_obs[2]['val']
            macro_snapshot["Non-Farm Payrolls"] = {
                "val": f"{total_emp:.1f}M ({latest_chg:+.0f}K)",
                "prev": f"Chg Prev: {prev_chg:+.0f}K",
                "date": nfp_obs[0]['date']
            }

        # E. PPI YoY & MoM
        ppi_obs = fetch_fred_series_with_dates("PPIACO", fred_api_key, limit=14)
        if len(ppi_obs) >= 13:
            ppi_mom = ((ppi_obs[0]['val'] - ppi_obs[1]['val']) / ppi_obs[1]['val']) * 100
            ppi_yoy = ((ppi_obs[0]['val'] - ppi_obs[12]['val']) / ppi_obs[12]['val']) * 100
            
            macro_snapshot["PPI MoM"] = {
                "val": f"{ppi_mom:+.1f}%",
                "prev": "N/A",
                "date": ppi_obs[0]['date']
            }
            macro_snapshot["PPI YoY"] = {
                "val": f"{ppi_yoy:+.1f}%",
                "prev": "N/A",
                "date": ppi_obs[0]['date']
            }

    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"fetched_at": today_str, "data": macro_snapshot}, f, ensure_ascii=False, indent=2)
        print("💾 [M7-MACRO] Global macro data saved successfully.")
    except Exception as save_err:
        print(f"⚠️ [M7-MACRO] Error saving cache: {save_err}")
        
    return macro_snapshot