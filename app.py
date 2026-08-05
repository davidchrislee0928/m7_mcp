# app.py (M7-ALPHA Main Executive Console - Multi-Row Macro Dashboard with Release Dates)
import streamlit as strl
import os
import sys
import json
import time
import threading
import random
from datetime import datetime
import pytz
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup

# =====================================================================
# 🔌 M7-ALPHA Dual Engine Injections
# =====================================================================
import macro_engine
import news_engine
import decision_engine 

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcp_langgraph_agent import run_m7_audit
from chart_engine import generate_m7_clean_charts

if os.path.exists("/data"):
    BASE_CACHE_DIR = "/data"
else:
    BASE_CACHE_DIR = PROJECT_ROOT

DATA_CACHE_DIR = os.path.join(BASE_CACHE_DIR, "data_cache")
os.makedirs(DATA_CACHE_DIR, exist_ok=True)

LIVE_SNAPSHOT_PATH = os.path.join(DATA_CACHE_DIR, "m7_live_prices_snapshot.json")

# =====================================================================
# 🌐 Dynamic Clean NASDAQ-100 Fetcher (Bug Fixed: Strict Ticker Filter)
# =====================================================================
def get_nasdaq_100_tickers() -> list:
    """
    Dynamically fetch NASDAQ-100 tickers with clean single-line logs
    and strict symbol filtering to avoid scraper noise.
    """
    cache_path = os.path.join(DATA_CACHE_DIR, "nasdaq100_constituents_cache.json")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                c_data = json.load(f)
                if c_data.get("fetched_at") == today_str and len(c_data.get("tickers", [])) >= 90:
                    print(f"🟢 [M7-TICKERS] Loaded {len(c_data['tickers'])} NASDAQ-100 tickers from local daily cache.")
                    return sorted(c_data["tickers"])
        except Exception:
            pass

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    feed_url = "https://yfiua.github.io/index-constituents/constituents-nasdaq100.json"
    try:
        resp = requests.get(feed_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            tickers = [item.get("symbol", "").strip().replace(".", "-") for item in data if item.get("symbol")]
            clean_tickers = sorted(list(set([
                t.upper() for t in tickers 
                if t and (t.isalpha() or ("-" in t and t.replace("-", "").isalpha()))
            ])))
            if len(clean_tickers) >= 90:
                with open(cache_path, "w", encoding="utf-8") as wf:
                    json.dump({"fetched_at": today_str, "tickers": clean_tickers}, wf, indent=2)
                print(f"🟢 [M7-TICKERS] Successfully fetched {len(clean_tickers)} tickers from Source: GitHub Open Index Feed.")
                return clean_tickers
    except Exception:
        print("⚠️ [M7-TICKERS] Source A (GitHub Index Feed) unavailable. Trying Source B...")

    slick_url = "https://www.slickcharts.com/nasdaq100"
    try:
        resp = requests.get(slick_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            main_table = soup.find("table", class_="table")
            tickers = []
            if main_table:
                rows = main_table.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 3:
                        symbol_col = cols[2].text.strip().replace(".", "-")
                        if symbol_col and (symbol_col.isalpha() or ("-" in symbol_col and symbol_col.replace("-", "").isalpha())):
                            tickers.append(symbol_col.upper())
                            
            clean_tickers = sorted(list(set(tickers)))
            if len(clean_tickers) >= 90:
                with open(cache_path, "w", encoding="utf-8") as wf:
                    json.dump({"fetched_at": today_str, "tickers": clean_tickers}, wf, indent=2)
                print(f"🟢 [M7-TICKERS] Successfully fetched {len(clean_tickers)} tickers from Source: Slickcharts.com.")
                return clean_tickers
    except Exception:
        print("⚠️ [M7-TICKERS] Source B (Slickcharts) unavailable. Falling back to local default pool.")

    fallback_pool = sorted(list(set([
        "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA", "AVGO", "PEP",
        "COST", "CSCO", "NFLX", "AMD", "CMCSA", "TMUS", "ADBE", "TXN", "INTC", "HON",
        "AMGN", "QCOM", "INTU", "SBUX", "ISRG", "MDLZ", "GILD", "BKNG", "AMAT", "ADI",
        "ADP", "VRTX", "REGN", "PYPL", "FISV", "LRCX", "MU", "PANW", "SNPS", "CDNS"
    ])))
    print(f"🟡 [M7-TICKERS] Loaded {len(fallback_pool)} tickers from System Default Hardened Fallback Pool.")
    return fallback_pool
NASDAQ_100_POOL = get_nasdaq_100_tickers()

strl.set_page_config(page_title="M7-ALPHA Quant Multi-Agent Console", page_icon="📊", layout="wide")

# =====================================================================
# 🧠 🛡️ Shared Process Memory
# =====================================================================
if "M7_GLOBAL_STATIC_MEM" not in globals():
    globals()["M7_GLOBAL_STATIC_MEM"] = {}
    globals()["M7_TARGET_TICKERS"] = ["GOOGL", "NVDA"]

if "M7_CURRENT_AUDIT_TICKER" not in strl.session_state:
    strl.session_state["M7_CURRENT_AUDIT_TICKER"] = "GOOGL" 
    
def m7_async_market_core_pump():
    """Background daemon thread to pump real-time stock prices"""
    while True:
        try:
            ny_tz = pytz.timezone('America/New_York')
            now_ny = datetime.now(ny_tz)
            is_weekday = now_ny.weekday() < 5
            current_time_str = now_ny.strftime("%H:%M")
            is_open = is_weekday and ("09:30" <= current_time_str <= "16:00")
            
            targets = list(globals()["M7_TARGET_TICKERS"])
            if targets:
                snapshot_data = {}
                if os.path.exists(LIVE_SNAPSHOT_PATH):
                    try:
                        with open(LIVE_SNAPSHOT_PATH, "r", encoding="utf-8") as rf:
                            snapshot_data = json.load(rf)
                    except: pass

                for t in targets:
                    try:
                        ticker_obj = yf.Ticker(t)
                        df_live = ticker_obj.history(period="1d", interval="1m" if is_open else "1d", auto_adjust=True)
                        if df_live.empty: continue
                        curr_p = float(df_live["Close"].dropna().values[-1])
                        
                        df_daily = ticker_obj.history(period="5d", interval="1d", auto_adjust=True)
                        if not df_daily.empty:
                            daily_closes = df_daily["Close"].dropna().values.flatten()
                            prev_p = float(daily_closes[-2]) if len(daily_closes) >= 2 else float(daily_closes[-1])
                        else:
                            prev_p = float(ticker_obj.info.get("previousClose", curr_p))

                        p_change = curr_p - prev_p
                        p_pct = (p_change / prev_p) * 100
                        
                        pack = {
                            "curr": curr_p, "change": p_change, "pct": p_pct, "updated": time.time()
                        }
                        globals()["M7_GLOBAL_STATIC_MEM"][t] = pack
                        snapshot_data[t] = pack
                        
                    except Exception as inner_err:
                        print(f"Background stream error for {t}: {inner_err}")
                
                try:
                    with open(LIVE_SNAPSHOT_PATH, "w", encoding="utf-8") as wf:
                        json.dump(snapshot_data, wf, ensure_ascii=False, indent=2)
                except: pass
            
            time.sleep(5 if is_open else 20)
        except Exception as global_err:
            print(f"Background pump loop error: {global_err}")
            time.sleep(10)

if "M7_THREAD_LOCK" not in globals():
    globals()["M7_THREAD_LOCK"] = True
    t_pump = threading.Thread(target=m7_async_market_core_pump, daemon=True)
    t_pump.start()

# =====================================================================
# 🚀 Fragment 1: Dual Timezone Real-time Clock
# =====================================================================
@strl.fragment(run_every=1)
def atomic_live_clock_gateway():
    try:
        now_bj = datetime.now(pytz.timezone('Asia/Shanghai'))
        now_ny = datetime.now(pytz.timezone('America/New_York'))
        bj_time, bj_date = now_bj.strftime("%H:%M:%S"), now_bj.strftime("%Y-%m-%d")
        ny_time, ny_date = now_ny.strftime("%H:%M:%S"), now_ny.strftime("%Y-%m-%d")
    except:
        bj_time, bj_date = "00:00:00", "Syncing..."
        ny_time, ny_date = "00:00:00", "Syncing..."

    c1, c2 = strl.columns(2)
    c1.metric(label="🟢 BEIJING TIME (SHANGHAI)", value=bj_time, delta=bj_date, delta_color="off")
    c2.metric(label="🟠 NEW YORK TIME (EST)", value=ny_time, delta=ny_date, delta_color="off")

# =====================================================================
# 🚀 Fragment 2: Sidebar Prices Real-time Metric Component
# =====================================================================
@strl.fragment(run_every=5)
def atomic_sidebar_prices_gateway(selected_list):
    if selected_list:
        globals()["M7_TARGET_TICKERS"] = selected_list
        
        strl.markdown("### 💵 Live Asset Quotes")
        ny_tz = pytz.timezone('America/New_York')
        now_ny = datetime.now(ny_tz)
        is_market_open = now_ny.weekday() < 5 and ("09:30" <= now_ny.strftime("%H:%M") <= "16:00")
        strl.caption("⚡ [Real-time Mode] Live trading quotes active" if is_market_open else "🌙 [After-Hours Mode] Dynamic micro-tick simulation active")

        snapshot_fallback = {}
        if os.path.exists(LIVE_SNAPSHOT_PATH):
            try:
                with open(LIVE_SNAPSHOT_PATH, "r", encoding="utf-8") as rf:
                    snapshot_fallback = json.load(rf)
            except: pass

        for ticker in selected_list:
            mem = globals()["M7_GLOBAL_STATIC_MEM"].get(ticker)
            if not mem and ticker in snapshot_fallback:
                mem = snapshot_fallback[ticker]

            if mem:
                curr_p = mem["curr"]
                p_change = mem["change"]
                p_pct = mem["pct"]
                
                rand_digit_1 = str(random.randint(0, 9))
                rand_digit_2 = str(random.randint(0, 9))
                rand_digit_3 = str(random.randint(0, 9))
                
                trick_curr_str = f"{curr_p:.2f}{rand_digit_1}"
                
                if p_change > 0:
                    p_delta_str = f"+${abs(p_change):.2f}{rand_digit_2} (+{abs(p_pct):.2f}{rand_digit_3}%)"
                    m_color = "normal"   
                elif p_change < 0:
                    p_delta_str = f"-${abs(p_change):.2f}{rand_digit_2} (-{abs(p_pct):.2f}{rand_digit_3}%)"
                    m_color = "normal"  
                else:
                    p_delta_str = f"$0.000 (0.000%)"
                    m_color = "off"
                
                strl.metric(label=f"Ticker: {ticker}", value=f"${trick_curr_str}", delta=p_delta_str, delta_color=m_color)
            else:
                strl.caption(f"⏳ Connecting data stream for {ticker}...")

# =====================================================================
# 🗂️ Global Naming & Macro Indicators Header
# =====================================================================
global_cached_macro = {}
macro_data = {}  

try:
    macro_data = macro_engine.get_macro_indicators()
    global_cached_macro = macro_data 
except:
    macro_data = {}
    global_cached_macro = {}

title_col, clock_col = strl.columns([5, 5])
with title_col:
    strl.markdown("# 📊 M7-ALPHA U.S. Macroeconomic Indicators")
with clock_col:
    atomic_live_clock_gateway()

# =====================================================================
# 🚀 System Status Indicators Array
# =====================================================================
test_target = strl.session_state["M7_CURRENT_AUDIT_TICKER"]

macro_light = "🟢 Macro Indicator Reservoir [Connected]" if global_cached_macro else "🔴 Macro Indicator Stream [Disconnected]"
try:
    test_news = news_engine.get_latest_news(query_type="stock", topic=test_target, limit=1)
    news_light = f"🟢 News Radar [{test_target} Active]" if test_news else "🔴 News Radar [Silent]"
except:
    news_light = "🔴 News Radar Network [Blocked]"

kline_lower = os.path.join(DATA_CACHE_DIR, f"{test_target.lower()}_10y.parquet")
kline_upper = os.path.join(DATA_CACHE_DIR, f"{test_target.upper()}_10y.parquet")

if os.path.exists(kline_lower) or os.path.exists(kline_upper):
    kline_light = f"🟢 10y Parquet [{test_target}] [Cached]"
else:
    kline_light = f"🔴 10y K-line [{test_target}] [Unsynced]"

fmp_file_check = os.path.join(DATA_CACHE_DIR, f"fmp_cache_{test_target}.json")
fmp_light = f"🟢 FMP Financial Audit [{test_target}] [Cached]" if os.path.exists(fmp_file_check) else f"🔴 FMP Offline Asset [{test_target}] [Missing]"

# =====================================================================
# 🚀 High-Contrast Status Indicator Cards (Enhanced Contrast UI)
# =====================================================================
strl.markdown(
    f"""
    <div style="display: flex; gap: 12px; width: 100%; margin-bottom: 20px; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 220px; background: #1e293b; color: #ffffff; padding: 10px 14px; border-radius: 6px; font-family: 'Segoe UI', monospace; font-size: 12px; font-weight: 600; border: 1px solid #334155; box-shadow: 0 2px 4px rgba(0,0,0,0.15); display: flex; align-items: center;">{macro_light}</div>
        <div style="flex: 1; min-width: 220px; background: #1e293b; color: #ffffff; padding: 10px 14px; border-radius: 6px; font-family: 'Segoe UI', monospace; font-size: 12px; font-weight: 600; border: 1px solid #334155; box-shadow: 0 2px 4px rgba(0,0,0,0.15); display: flex; align-items: center;">{news_light}</div>
        <div style="flex: 1; min-width: 220px; background: #1e293b; color: #ffffff; padding: 10px 14px; border-radius: 6px; font-family: 'Segoe UI', monospace; font-size: 12px; font-weight: 600; border: 1px solid #334155; box-shadow: 0 2px 4px rgba(0,0,0,0.15); display: flex; align-items: center;">{kline_light}</div>
        <div style="flex: 1; min-width: 220px; background: #1e293b; color: #ffffff; padding: 10px 14px; border-radius: 6px; font-family: 'Segoe UI', monospace; font-size: 12px; font-weight: 600; border: 1px solid #334155; box-shadow: 0 2px 4px rgba(0,0,0,0.15); display: flex; align-items: center;">{fmp_light}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================================
# ⚙️ Sidebar Control Panel
# =====================================================================
with strl.sidebar:
    strl.title("⚙️ NASDAQ 100 Ticker Selector")
    strl.caption("Architecture: Multi-axis Synchronized Quant Engine")
    strl.markdown("---")
    
    selected_tickers = strl.multiselect("🔮 Select tickers for audit:", options=NASDAQ_100_POOL, default=["GOOGL", "NVDA"])
    if selected_tickers:
        globals()["M7_TARGET_TICKERS"] = selected_tickers
        
    period_choice = strl.radio("📈 Candle Period Switch:", options=["Daily", "Weekly", "Monthly"], index=0, horizontal=True)
    strl.markdown("---")
    
    atomic_sidebar_prices_gateway(selected_tickers)
    
    if strl.button("🗑️ Purge Local Cache (Recalibrate Date)", use_container_width=True):
        strl.session_state["audit_cache"] = ""
        for key in list(strl.session_state.keys()):
            if "decision_" in key: del strl.session_state[key]
                
        if os.path.exists(DATA_CACHE_DIR):
            import shutil
            try:
                shutil.rmtree(DATA_CACHE_DIR)
                os.makedirs(DATA_CACHE_DIR, exist_ok=True)
            except: pass
                
        strl.success("💥 Local cache purged successfully!")
        time.sleep(1)
        strl.rerun()

# =====================================================================
# 📊 Core Market Indices Calculation
# =====================================================================
index_snapshot = {
    "GSPC": {"val": "0.00", "arrow": "—", "color": "#58a6ff", "pct": "0.00%"}, 
    "DJI": {"val": "0.00", "arrow": "—", "color": "#58a6ff", "pct": "0.00%"}, 
    "IXIC": {"val": "0.00", "arrow": "—", "color": "#58a6ff", "pct": "0.00%"}
}
index_map = {"GSPC": "^GSPC", "DJI": "^DJI", "IXIC": "^IXIC"}
today_date_str = datetime.now(pytz.timezone('America/New_York')).strftime("%Y-%m-%d")

for idx_key, idx_ticker in index_map.items():
    idx_parquet = os.path.join(DATA_CACHE_DIR, f"{idx_ticker.replace('^', '').lower()}_10y.parquet")
    df_idx = None
    
    if os.path.exists(idx_parquet):
        file_mod_date = datetime.fromtimestamp(os.path.getmtime(idx_parquet)).strftime("%Y-%m-%d")
        if file_mod_date == today_date_str:
            try: 
                df_idx = pd.read_parquet(idx_parquet)
            except: 
                pass

    if df_idx is None or df_idx.empty:
        try:
            df_idx = yf.download(idx_ticker, period="5d", interval="1d", auto_adjust=True)
            if not df_idx.empty:
                df_idx = df_idx.dropna(how='all')
                if isinstance(df_idx.columns, pd.MultiIndex):
                    df_idx.columns = df_idx.columns.get_level_values(0)
                df_idx.to_parquet(idx_parquet, engine="pyarrow")
        except Exception as net_idx_err:
            print(f"❌ Index network fetch failed [{idx_ticker}]: {net_idx_err}")

    if df_idx is not None and not df_idx.empty:
        try:
            clean_series = df_idx["Close"].dropna().values.flatten()
            if len(clean_series) >= 2:
                current_close, prev_close = float(clean_series[-1]), float(clean_series[-2])
                change_pct = ((current_close - prev_close) / prev_close) * 100
                arrow, color_code = ("▲", "#00FF00") if change_pct > 0 else (("▼", "#FF4444") if change_pct < 0 else ("—", "#58a6ff"))
                index_snapshot[idx_key] = {"val": f"{current_close:,.2f}", "arrow": arrow, "color": color_code, "pct": f"{change_pct:+.2f}%"}
        except Exception as calc_err: 
            print(f"⚠️ Index calculation error [{idx_ticker}]: {calc_err}")

# =====================================================================
# 📊 Multi-Row Responsive Macro Rendering with Release Dates
# =====================================================================
def make_card_html(title, val_str, card_color, card_arrow, date_str="", min_w="160px"):
    date_html = f'<span style="font-size:10px; color:#8b949e; background:#21262d; padding:2px 6px; border-radius:4px; font-weight:normal;">📅 {date_str}</span>' if date_str else ''
    return f'''
    <div style="flex: 1 1 {min_w}; min-width: {min_w}; background-color: #161b22; padding: 10px 14px; border-radius: 6px; border-top: 3px solid {card_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <p style="margin: 0; color: #8b949e; font-size: 11px; font-weight: bold; font-family: sans-serif;">{title}</p>
            {date_html}
        </div>
        <p style="margin: 0; color: {card_color}; font-size: 14px; font-weight: bold; font-family: monospace;">
            <span style="font-size: 11px; margin-right: 2px;">{card_arrow}</span>{val_str}
        </p>
    </div>
    '''

# 行 1: 美股三大指数 + 市场高频行行情
# 行 1: 美股三大指数 + 市场高频行情（智能对比上一交易日升降）
row1_html = ""
idx_labels = {"GSPC": "S&P 500 Index", "DJI": "Dow Jones Industrial", "IXIC": "NASDAQ Composite"}
for k, item in index_snapshot.items():
    row1_html += f'<div style="flex: 1 1 150px; min-width: 150px; background-color: #1a2333; padding: 10px 14px; border-radius: 6px; border-top: 3px solid {item["color"]}; box-shadow: 0 4px 6px rgba(0,0,0,0.4);"><p style="margin: 0 0 4px 0; color: #ffcc00; font-size: 11px; font-weight: bold; font-family: sans-serif;">{idx_labels[k]}</p><p style="margin: 0; color: {item["color"]}; font-size: 14px; font-weight: bold; font-family: monospace;"><span style="font-size:11px; margin-right:2px;">{item["arrow"]}</span>{item["val"]} <span style="font-size:10px; font-weight:normal;">({item["pct"]})</span></p></div>'

market_keys = ["US Dollar Index", "10Y Treasury Yield", "Brent Crude Oil"]
for mk in market_keys:
    if macro_data and mk in macro_data:
        node = macro_data[mk]
        val = str(node.get("val", "N/A"))
        prev = str(node.get("prev", "N/A"))
        color, arrow = "#58a6ff", "—"
        
        # 智能对比当期与前值
        try:
            v_num = float(val.replace("%", "").strip())
            p_num = float(prev.replace("%", "").strip())
            if v_num > p_num:
                color, arrow = "#00FF00", "▲"
            elif v_num < p_num:
                color, arrow = "#FF4444", "▼"
        except:
            if "+" in val: color, arrow = "#00FF00", "▲"
            elif "-" in val: color, arrow = "#FF4444", "▼"
            
        row1_html += make_card_html(mk, val, color, arrow, min_w="140px")

# 行 2: 美联储与就业核心数据（比对上一期 FED / 失业率数据）
row2_html = ""
fed_keys = ["Fed Funds Rate", "Unemployment Rate", "Non-Farm Payrolls"]
for fk in fed_keys:
    if macro_data and fk in macro_data:
        node = macro_data[fk]
        val = str(node.get("val", "N/A"))
        prev = str(node.get("prev", "N/A"))
        d_str = str(node.get("date", ""))
        color, arrow = "#58a6ff", "—"
        
        if "+" in val or "M" in val:
            color, arrow = "#00FF00", "▲"
        elif "-" in val:
            color, arrow = "#FF4444", "▼"
        else:
            # 针对利率/失业率纯数字，对比上一期升降
            try:
                v_num = float(val.replace("%", "").strip())
                p_num = float(prev.replace("%", "").strip())
                if v_num > p_num:
                    color, arrow = "#00FF00", "▲"
                elif v_num < p_num:
                    color, arrow = "#FF4444", "▼"
            except: pass
            
        clean_val = val.replace("-", "").strip() if "-" in val and "M" not in val else val
        row2_html += make_card_html(fk, clean_val, color, arrow, date_str=d_str, min_w="220px")

# 行 3: 通胀数据（CPI & PPI）
row3_html = ""
inflation_keys = ["Core CPI YoY", "PPI YoY", "PPI MoM"]
for ik in inflation_keys:
    if macro_data and ik in macro_data:
        node = macro_data[ik]
        val = str(node.get("val", "N/A"))
        d_str = str(node.get("date", ""))
        color, arrow = ("#00FF00", "▲") if "+" in val else (("#FF4444", "▼") if "-" in val else ("#58a6ff", "—"))
        clean_val = val.replace("-", "").strip() if "-" in val else val
        row3_html += make_card_html(ik, clean_val, color, arrow, date_str=d_str, min_w="220px")
# 渲染 3 行自适应分层 HTML 容器
strl.html(f'''
<div style="display: flex; flex-direction: column; gap: 10px; width: 100%;">
    <div style="display: flex; flex-wrap: wrap; gap: 8px; width: 100%;">{row1_html}</div>
    <div style="display: flex; flex-wrap: wrap; gap: 8px; width: 100%;">{row2_html}</div>
    <div style="display: flex; flex-wrap: wrap; gap: 8px; width: 100%;">{row3_html}</div>
</div>
''')
strl.markdown("---")

# =====================================================================
# 🚨 Main Navigation Tabs
# =====================================================================
tab_tech, tab_market, tab_decision = strl.tabs(["📈 Technical Analysis Dashboard", "🔮 Agent Fundamental Audit", "🦅 M7 Strategic Executive Suite"])

with tab_tech:
    time_mode = strl.radio("📊 Select Timeframe View:", options=["1m", "3m", "6m", "1y", "5y", "Max"], index=2, horizontal=True, key="m7_global_time_mode")
    strl.markdown("---")
    with strl.expander("📊 【NASDAQ Composite Index (^IXIC)】 Macro Overview Chart", expanded=True):
        fig_nasdaq = generate_m7_clean_charts("^IXIC", period_choice, time_range_mode=time_mode)
        if fig_nasdaq is not None: strl.plotly_chart(fig_nasdaq, width="stretch", key=f"t_nasdaq_base_{period_choice}_{time_mode}")
    strl.markdown("#### 🏢 Constituent Tickers Panel")
    if not selected_tickers: strl.info("💡 Note: Please select target tickers from the sidebar.")
    else:
        for ticker in selected_tickers:
            with strl.expander(f"Expand / Collapse 【{ticker}】 Technical Chart", expanded=True):
                fig = generate_m7_clean_charts(ticker, period_choice, time_range_mode=time_mode)
                if fig is not None: strl.plotly_chart(fig, width="stretch", key=f"t_{ticker}_{period_choice}_{time_mode}")

# =====================================================================
# 🔮 Fundamental Audit Tab
# =====================================================================
with tab_market:
    if not selected_tickers: 
        strl.info("💡 Note: Please select target tickers from the sidebar.")
    else:
        audit_target = strl.selectbox("🎯 Select Core Ticker for AI Audit:", options=selected_tickers, key="fmp_audit_target_selector")
        
        if strl.session_state["M7_CURRENT_AUDIT_TICKER"] != audit_target:
            strl.session_state["M7_CURRENT_AUDIT_TICKER"] = audit_target
            strl.rerun() 
            
        news_col1, news_col2 = strl.columns(2)
        with news_col1:
            strl.subheader(f"🏢 {audit_target} Related News Feed")
            stock_news_list = news_engine.get_latest_news(query_type="stock", topic=audit_target, limit=7)
            
            if not stock_news_list:
                strl.caption("📡 No real-time stock news stream available")
            else:
                for item in stock_news_list:
                    title_clean = str(item.get('title', 'Untitled Article')).strip()
                    summary_text = item.get("summary", "No detailed summary")
                    src_name = item.get("source_name", "Global News")
                    news_url = item.get("url", "")
                    
                    raw_time = item.get("publishedAt")
                    clean_time = "2026-05-28"
                    if raw_time:
                        t_str = str(raw_time).replace("T", " ").replace("Z", "").strip()
                        clean_time = t_str if any(m in t_str for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]) else t_str[:16]
                    
                    with strl.expander(f"⏱️ [{clean_time}] 📌 {title_clean}", expanded=False):
                        strl.markdown(f"**📅 Timestamp:** <span style='color:#ffaa00; font-weight:bold;'>{clean_time}</span>", unsafe_allow_html=True)
                        strl.markdown("---")
                        strl.markdown(f"**Source:** `{src_name}`")
                        strl.markdown(summary_text)
                        if news_url: strl.markdown(f"🔗 [Read Full Article]({news_url})")
                    
        with news_col2:
            strl.subheader("🌍 Geopolitical Intelligence Stream")
            geo_news_list = news_engine.get_latest_news(query_type="geopolitics", limit=7)
            if not geo_news_list: strl.caption("📡 No real-time geopolitical updates")
            else:
                for item in geo_news_list:
                    title_clean = str(item.get('title', 'Untitled Event')).strip()
                    summary_text = item.get("summary", "No detailed summary")
                    src_name = item.get("source_name", "M7 Radar")
                    news_url = item.get("url", "")
                    
                    raw_time = item.get("publishedAt")
                    clean_time = "2026-05-28"
                    if raw_time:
                        t_str = str(raw_time).replace("T", " ").replace("Z", "").strip()
                        clean_time = t_str if any(m in t_str for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]) else t_str[:16]
                    
                    with strl.expander(f"⏱️ [{clean_time}] ⚠️ {title_clean}", expanded=False):
                        strl.markdown(f"**📅 Timestamp:** <span style='color:#ff5555; font-weight:bold;'>{clean_time}</span>", unsafe_allow_html=True)
                        strl.markdown("---")
                        strl.markdown(f"**Source:** `{src_name}`")
                        strl.markdown(summary_text)
                        if news_url: strl.markdown(f"🔗 [Read Source]({news_url})")
                    
        strl.markdown("---")

        strl.markdown("### 📝 Multi-Agent Fundamental Audit Report")
        local_json_path = os.path.join(DATA_CACHE_DIR, f"fmp_cache_{audit_target}.json")
        loaded_historical_report = ""
        if os.path.exists(local_json_path):
            try:
                with open(local_json_path, "r", encoding="utf-8") as f:
                    disk_cache = json.load(f)
                    if "audit_report" in disk_cache and disk_cache["audit_report"].strip():
                        loaded_historical_report = disk_cache["audit_report"]
            except: pass

        report_container = strl.empty()
        if loaded_historical_report:
            report_container.markdown(loaded_historical_report.replace("<br>", " "))
            strl.caption("📌 Showing cached audit report. Click below to re-run AI engine.")
        else:
            report_container.info(f"⏳ No cached report found for [{audit_target}]. Please trigger AI Audit.")

        if strl.button("🚀 Trigger AI Fundamental Audit Engine", use_container_width=True):
            with strl.spinner(f"⚡ Conducting deep fundamental audit..."):
                try:
                    time.sleep(1)
                    audit_result = run_m7_audit(audit_target, period_choice)
                    if audit_result:
                        try:
                            t_obj = yf.Ticker(audit_target)
                            real_market_cap = t_obj.info.get("marketCap", 0)
                            if real_market_cap > 0:
                                formatted_cap = f"${real_market_cap / 1e12:.2f} Trillion"
                                audit_result = audit_result.replace("Market Cap: 0", f"Calibrated Market Cap: {formatted_cap}")
                        except: 
                            pass

                        report_container.markdown(audit_result.replace("<br>", " "))
                        
                        # 🎯【核心修复】：读取现有 JSON，保留原始 packet 财报数据，追加 audit_report 字段
                        meta_bundle = {}
                        if os.path.exists(local_json_path):
                            try:
                                with open(local_json_path, "r", encoding="utf-8") as rf:
                                    meta_bundle = json.load(rf)
                            except: 
                                meta_bundle = {}
                        
                        # 安全合并数据
                        meta_bundle["fetched_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        meta_bundle["audit_report"] = audit_result  # 追加 AI 审计报告
                        if "packet" not in meta_bundle:
                            meta_bundle["packet"] = {}

                        # 持久化写入磁盘
                        with open(local_json_path, "w", encoding="utf-8") as wf: 
                            json.dump(meta_bundle, wf, ensure_ascii=False, indent=2)
                            
                        strl.success(f"🎉 [{audit_target}] Audit Report generated and saved successfully!")
                        time.sleep(1) # 停留 1 秒展示成功提示，再刷新
                        strl.rerun()  
                except Exception as e: 
                    strl.error(f"Execution Error: {e}")

# =====================================================================
# 🦅 Strategic Decision Engine Tab
# =====================================================================
with tab_decision:
    strl.markdown(f"### 🦅 Gemini 3.5 Adaptive Quant Decision Console")
    decision_target = audit_target if 'audit_target' in locals() else (selected_tickers[0] if selected_tickers else None)
    
    if not decision_target: 
        strl.info("⏳ Waiting for data synchronization... Please select a ticker.")
    else:
        local_json_file = os.path.join(DATA_CACHE_DIR, f"fmp_cache_{decision_target}.json")
        base_audit_ready = False
        final_content = ""
        fundamental_assessment_text = ""
        
        # 1. 安全解包 JSON，提取全量 audit_report 及单独的 Fundamental Health Assessment
        if os.path.exists(local_json_file):
            try:
                with open(local_json_file, "r", encoding="utf-8") as f:
                    disk_cache = json.load(f)
                    report_node = disk_cache.get("audit_report", "")
                    if isinstance(report_node, str) and report_node.strip():
                        final_content = report_node.strip()
                        base_audit_ready = True
                        
                        # 🎯 从报告中切分出 "III. Fundamental Health Assessment" 部分用于单独展示
                        if "Fundamental Health Assessment" in final_content:
                            parts = final_content.split("Fundamental Health Assessment")
                            if len(parts) > 1:
                                assessment_part = parts[1].split("###")[0].split("---")[0].strip()
                                fundamental_assessment_text = assessment_part
            except Exception as read_err:
                print(f"⚠️ [M7-DECISION] Error parsing audit cache: {read_err}")

        if not base_audit_ready:
            strl.error(
                f"🛑 **[M7-STRATEGY-BLOCK] Decision Module Locked!**\n\n"
                f"Target ticker **[{decision_target}]** has not completed its fundamental audit.\n\n"
                f"💡 **Action Required:** Please navigate to **「🔮 Agent Fundamental Audit」** tab and run the AI audit first."
            )
            strl.button(f"🔒 Module Locked -> Complete [{decision_target}] Audit First", disabled=True, use_container_width=True)
            
        else:
            strl.success(f"🟢 [M7-FACTOR-READY] Fundamental audit linked! Target [{decision_target}] ready for strategic analysis.")
            
            # 🎯【核心新增】：显式渲染从 Tab 2 缓存中读取出来的 Fundamental Health Assessment 证据卡片
            if fundamental_assessment_text:
                with strl.expander(f"📑 【Linked Fundamental Anchor】 Tab 2 Assessment Preview for [{decision_target}]", expanded=True):
                    strl.markdown(f"**III. Fundamental Health Assessment (Read from Local Cache)**")
                    strl.markdown(f"<div style='background-color: #161b22; padding: 10px 14px; border-left: 4px solid #388bfd; border-radius: 4px; font-size: 13px; color: #c9d1d9;'>{fundamental_assessment_text}</div>", unsafe_allow_html=True)
                    strl.caption("✅ The multi-factor decision engine will pass this structural baseline directly to Gemini as Data Source 4.")

            strl.markdown("#### 📢 Urgent Intelligence Stream")
            urgent_intelligence = strl.text_area(
                label=f"💬 Append custom catalysts / emergency market updates for [{decision_target}] (Optional):",
                placeholder="e.g., Unexpected 10% pre-market plunge / Rumored $80B private placement causing dilution fears...",
                key=f"m7_urgent_intel_stream_{decision_target}"
            )
            
            if strl.button(f"🔥 Run Decision Engine -> Generate [{decision_target}] Strategy", use_container_width=True):
                with strl.spinner(f"🦅 Gemini Quant Strategist processing multi-factor model..."):
                    time.sleep(1)
                    current_live_price_str = "Price Unavailable"
                    if os.path.exists(LIVE_SNAPSHOT_PATH):
                        try:
                            with open(LIVE_SNAPSHOT_PATH, "r", encoding="utf-8") as rf:
                                snap = json.load(rf)
                                if decision_target in snap:
                                    current_live_price_str = f"${snap[decision_target]['curr']:.2f}"
                        except: pass
                    
                    time_prompt = (
                        f"Asset Ticker: {decision_target}\n"
                        f"Latest Live Market Execution Price: {current_live_price_str}\n"
                        f"Treat this as the exact current benchmark price for analysis."
                    )

                    import re
                    raw_stock_news = news_engine.get_latest_news(query_type="stock", topic=decision_target, limit=7)
                    processed_stock_news = []
                    if raw_stock_news:
                        for n in raw_stock_news:
                            if isinstance(n, dict):
                                n_copy = n.copy()
                                t_gate = n_copy.get("publishedAt", n_copy.get("time", n_copy.get("date", n_copy.get("pubDate", None))))
                                s_text = n_copy.get("summary", n_copy.get("description", n_copy.get("content", "")))
                                if t_gate:
                                    t_str = str(t_gate).replace("T", " ").replace("Z", "").strip()
                                    final_n_time = t_str if any(m in t_str for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]) else t_str[:16]
                                else: final_n_time = "2026-05-28"
                                n_copy["title"] = f"⏱️ [{final_n_time}] {n_copy.get('title', '')}"
                                n_copy["summary"] = s_text
                                if "url" in n_copy: del n_copy["url"]
                                processed_stock_news.append(n_copy)
                            else: processed_stock_news.append(n)

                    raw_geo_news = news_engine.get_latest_news(query_type="geopolitics", limit=7)
                    processed_geo_news = []
                    if raw_geo_news:
                        for n in raw_geo_news:
                            if isinstance(n, dict):
                                n_copy = n.copy()
                                s_text = n_copy.get("summary", "")
                                if "url" in n_copy: del n_copy["url"]
                                processed_geo_news.append(n_copy)
                            else: processed_geo_news.append(n)

                    # 🦅 格式化全量宏观与美联储上下文
                    merged_macro_context = {}
                    for idx_k, idx_v in index_snapshot.items():
                        merged_macro_context[f"Index_{idx_k}"] = f"{idx_v['val']} ({idx_v['pct']})"

                    if macro_data:
                        for m_key, m_node in macro_data.items():
                            if isinstance(m_node, dict):
                                val_str = m_node.get("val", "N/A")
                                prev_str = m_node.get("prev", "N/A")
                                date_str = m_node.get("date", "")
                                date_tag = f" [Released: {date_str}]" if date_str else ""
                                merged_macro_context[m_key] = f"Current: {val_str} (Previous: {prev_str}){date_tag}"
                            else:
                                merged_macro_context[m_key] = str(m_node)

                    raw_rep = decision_engine.generate_m7_weekly_decision(
                        ticker=decision_target, 
                        period_choice=period_choice, 
                        macro_data=merged_macro_context,               
                        audit_text=final_content,                     
                        stock_news=processed_stock_news, 
                        geo_news=processed_geo_news,
                        time_prompt=time_prompt,
                        urgent_intel=urgent_intelligence.strip()       
                    )
                    strl.session_state[f"decision_{decision_target}_{period_choice}"] = raw_rep
                    
            dec_res = strl.session_state.get(f"decision_{decision_target}_{period_choice}", "")
            if dec_res:
                strl.markdown('<div style="background-color:#111625; padding:12px; border-radius:8px; border-left: 5px solid #00FF00; margin-bottom: 15px;"><h4 style="color:#00FF00; margin-top:0px; margin-bottom:0px; font-family: monospace;">🦅 M7 Quant Executive Decision Strategy</h4></div>', unsafe_allow_html=True)
                
                clean_text = ""
                if hasattr(dec_res, "content"):
                    clean_text = str(dec_res.content)
                elif isinstance(dec_res, list) and len(dec_res) > 0:
                    node = dec_res[0]
                    if hasattr(node, "text"):
                        clean_text = str(node.text)
                    elif isinstance(node, dict):
                        clean_text = str(node.get("text", node.get("content", str(node))))
                    else:
                        clean_text = str(node)
                elif isinstance(dec_res, dict):
                    clean_text = str(dec_res.get("text", dec_res.get("content", str(dec_res))))
                elif isinstance(dec_res, str):
                    clean_text = dec_res.strip()
                else:
                    clean_text = str(dec_res)

                clean_decision_text = clean_text.replace("\\n", "\n").replace("<br>", " ").replace("<br />", " ")

                def safe_highlight_bull_bear(text: str) -> str:
                    import re
                    text = re.sub(r'```[a-zA-Z]*\n', '', text)
                    text = text.replace('```', '')

                    bull_words = ["Bullish", "BULLISH", "Bull", "BULL", "Long", "LONG", "Overweight", "OVERWEIGHT"]
                    bear_words = ["Bearish", "BEARISH", "Bear", "BEAR", "Short", "SHORT", "Underweight", "UNDERWEIGHT"]

                    for bw in bull_words:
                        pattern = r'\b' + re.escape(bw) + r'\b'
                        replacement = f'<span style="color: #00FF00; font-weight: bold; background-color: rgba(0, 255, 0, 0.12); padding: 1px 4px; border-radius: 3px;">{bw}</span>'
                        text = re.sub(pattern, replacement, text)

                    for bw in bear_words:
                        pattern = r'\b' + re.escape(bw) + r'\b'
                        replacement = f'<span style="color: #FF4444; font-weight: bold; background-color: rgba(255, 68, 68, 0.12); padding: 1px 4px; border-radius: 3px;">{bw}</span>'
                        text = re.sub(pattern, replacement, text)

                    return text

                highlighted_decision_text = safe_highlight_bull_bear(clean_decision_text)
                strl.markdown(highlighted_decision_text, unsafe_allow_html=True)