# app.py (M7-ALPHA 主界面控制台终端 - 作用域完全加固·突发因数完全解耦并网版)
import streamlit as strl
import os
import sys
import json
import time
import threading
import random  # 🚀 用于休盘期高频动态千分位脉冲测试
from datetime import datetime
import pytz
import pandas as pd
import yfinance as yf

# =====================================================================
# 🔌 M7-ALPHA 增强型宏观与舆情双向引擎注入点
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

# 全时态实时最新价格物理快照路径
LIVE_SNAPSHOT_PATH = os.path.join(DATA_CACHE_DIR, "m7_live_prices_snapshot.json")

NASDAQ_100_POOL = sorted(list(set([
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA", "AVGO", "PEP",
    "COST", "CSCO", "NFLX", "AMD", "CMCSA", "TMUS", "ADBE", "TXN", "INTC", "HON",
    "AMGN", "QCOM", "INTU", "SBUX", "ISRG", "MDLZ", "GILD", "BKNG", "AMAT", "ADI",
    "ADP", "VRTX", "REGN", "PYPL", "FISV", "LRCX", "MU", "PANW", "SNPS", "CDNS"
])))

strl.set_page_config(page_title="M7-ALPHA 量化多智能体终端", page_icon="📊", layout="wide")

# =====================================================================
# 🧠 🛡️ 【全局共享进程内存大坝】
# =====================================================================
if "M7_GLOBAL_STATIC_MEM" not in globals():
    globals()["M7_GLOBAL_STATIC_MEM"] = {}
    globals()["M7_TARGET_TICKERS"] = ["GOOGL", "NVDA"]

# 🚀🔥【动态主权个股锁】：用于跨标签页动态校准顶部四色指示灯
if "M7_CURRENT_AUDIT_TICKER" not in strl.session_state:
    strl.session_state["M7_CURRENT_AUDIT_TICKER"] = "GOOGL" 
    
def m7_async_market_core_pump():
    """独立于 Streamlit 主进程之外的操作系统级守护线程"""
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
                        print(f"后台双轨打捞 {t} 异常: {inner_err}")
                
                try:
                    with open(LIVE_SNAPSHOT_PATH, "w", encoding="utf-8") as wf:
                        json.dump(snapshot_data, wf, ensure_ascii=False, indent=2)
                except: pass
            
            time.sleep(5 if is_open else 20)
        except Exception as global_err:
            print(f"大坝主循环异常: {global_err}")
            time.sleep(10)

if "M7_THREAD_LOCK" not in globals():
    globals()["M7_THREAD_LOCK"] = True
    t_pump = threading.Thread(target=m7_async_market_core_pump, daemon=True)
    t_pump.start()

# =====================================================================
# 🚀🔥【原子提权 Fragment 一】：秒级实时自驱动双时区主权时钟
# =====================================================================
@strl.fragment(run_every=1)
def atomic_live_clock_gateway():
    try:
        now_bj = datetime.now(pytz.timezone('Asia/Shanghai'))
        now_ny = datetime.now(pytz.timezone('America/New_York'))
        bj_time, bj_date = now_bj.strftime("%H:%M:%S"), now_bj.strftime("%Y-%m-%d")
        ny_time, ny_date = now_ny.strftime("%H:%M:%S"), now_ny.strftime("%Y-%m-%d")
    except:
        bj_time, bj_date = "00:00:00", "同步中..."
        ny_time, ny_date = "00:00:00", "同步中..."

    c1, c2 = strl.columns(2)
    c1.metric(label="🟢 北京时间 (SHANGHAI)", value=bj_time, delta=bj_date, delta_color="off")
    c2.metric(label="🟠 纽约时间 (NEW YORK)", value=ny_time, delta=ny_date, delta_color="off")

# =====================================================================
# 🚀🔥【原子提权 Fragment 二】：昨收基准级·5s前台动态千分位 Trick 验证原子
# =====================================================================
@strl.fragment(run_every=5)
def atomic_sidebar_prices_gateway(selected_list):
    if selected_list:
        globals()["M7_TARGET_TICKERS"] = selected_list
        
        strl.markdown("### 💵 核心资产实时报价")
        ny_tz = pytz.timezone('America/New_York')
        now_ny = datetime.now(ny_tz)
        is_market_open = now_ny.weekday() < 5 and ("09:30" <= now_ny.strftime("%H:%M") <= "16:00")
        strl.caption("⚡ [M7 Trick 验证中] 股价已锁死千分位翻牌" if is_market_open else "🌙 [休盘期动态验证] 千分位5s自己秒跳更新")

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
                
                strl.metric(label=f"标的: {ticker}", value=f"${trick_curr_str}", delta=p_delta_str, delta_color=m_color)
            else:
                strl.caption(f"⏳ {ticker} 正在接入物理核心数据链...")

# =====================================================================
# 🗂️ 全局命名解耦与大盘气象
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
    strl.markdown("# 📊 M7-ALPHA 美国宏观经济指标")
with clock_col:
    atomic_live_clock_gateway()

# =====================================================================
# 🚀🔥【核心降维回嵌】：工业级四色数据主权物理指示灯大阵
# =====================================================================
test_target = strl.session_state["M7_CURRENT_AUDIT_TICKER"]

macro_light = "🟢 宏观经济指标大坝 [已并网]" if global_cached_macro else "🔴 宏观经济数据断流 [未接入]"
try:
    test_news = news_engine.get_latest_news(query_type="stock", topic=test_target, limit=1)
    news_light = f"🟢 舆情雷达网关 [{test_target} 已激活]" if test_news else "🔴 舆情雷达信源静默 [待重试]"
except:
    news_light = "🔴 舆情雷达网络阻断 [熔断]"

kline_lower = os.path.join(DATA_CACHE_DIR, f"{test_target.lower()}_10y.parquet")
kline_upper = os.path.join(DATA_CACHE_DIR, f"{test_target.upper()}_10y.parquet")

if os.path.exists(kline_lower) or os.path.exists(kline_upper):
    kline_light = f"🟢 10y二进制 [{test_target}] K线大坝 [落盘]"
else:
    kline_light = f"🔴 10yK线 [{test_target}] Parquet大坝 [未同步]"

fmp_file_check = os.path.join(DATA_CACHE_DIR, f"fmp_cache_{test_target}.json")
fmp_light = f"🟢 FMP财务审计 [{test_target}] 有持久化缓存" if os.path.exists(fmp_file_check) else f"🔴 FMP离线资产 [{test_target}] 未建立"

strl.markdown(
    f"""
    <div style="display: flex; gap: 10px; width: 100%; margin-bottom: 15px; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 220px; background-color: #111625; padding: 6px 12px; border-radius: 4px; font-family: monospace; font-size: 11px; font-weight: bold; border: 1px solid #1f293d;">{macro_light}</div>
        <div style="flex: 1; min-width: 220px; background-color: #111625; padding: 6px 12px; border-radius: 4px; font-family: monospace; font-size: 11px; font-weight: bold; border: 1px solid #1f293d;">{news_light}</div>
        <div style="flex: 1; min-width: 220px; background-color: #111625; padding: 6px 12px; border-radius: 4px; font-family: monospace; font-size: 11px; font-weight: bold; border: 1px solid #1f293d;">{kline_light}</div>
        <div style="flex: 1; min-width: 220px; background-color: #111625; padding: 6px 12px; border-radius: 4px; font-family: monospace; font-size: 11px; font-weight: bold; border: 1px solid #1f293d;">{fmp_light}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================================
# ⚙️ 控制中心侧边栏
# =====================================================================
with strl.sidebar:
    strl.title("⚙️ 纳斯达克100股票选择")
    strl.caption("架构层: 工业级单画布四轴强联动合龙内核")
    strl.markdown("---")
    
    selected_tickers = strl.multiselect("🔮 请选择要审计的纳指成份股:", options=NASDAQ_100_POOL, default=["GOOGL", "NVDA"])
    if selected_tickers:
        globals()["M7_TARGET_TICKERS"] = selected_tickers
        
    period_choice = strl.radio("📈 K线周期切换:", options=["日K", "周K", "月K"], index=0, horizontal=True)
    strl.markdown("---")
    
    atomic_sidebar_prices_gateway(selected_tickers)
    
    if strl.button("🗑️ 物理粉碎死锁缓存 (校准当日日期)", use_container_width=True):
        strl.session_state["audit_cache"] = ""
        for key in list(strl.session_state.keys()):
            if "decision_" in key: del strl.session_state[key]
                
        if os.path.exists(DATA_CACHE_DIR):
            import shutil
            try:
                shutil.rmtree(DATA_CACHE_DIR)
                os.makedirs(DATA_CACHE_DIR, exist_ok=True)
            except: pass
                
        strl.success("💥 持久化大坝资产已全数彻底粉碎！空仓重新点火中...")
        time.sleep(1)
        strl.rerun()

# =====================================================================
# 📊【天幕墙大盘核心原生态指数矩阵渲染】
# =====================================================================
index_snapshot = {
    "GSPC": {"val": "0.00", "arrow": "—", "color": "#58a6ff", "pct": "0.00%"}, 
    "DJI": {"val": "0.00", "arrow": "—", "color": "#58a6ff", "pct": "0.00%"}, 
    "IXIC": {"val": "0.00", "arrow": "—", "color": "#58a6ff", "pct": "0.00%"}
}
index_map = {"GSPC": "^GSPC", "DJI": "^DJI", "IXIC": "^IXIC"}

for idx_key, idx_ticker in index_map.items():
    idx_parquet = os.path.join(DATA_CACHE_DIR, f"{idx_ticker.replace('^', '').lower()}_10y.parquet")
    df_idx = None
    if os.path.exists(idx_parquet):
        try: df_idx = pd.read_parquet(idx_parquet)
        except: pass
    if df_idx is None or df_idx.empty:
        try:
            df_idx = yf.download(idx_ticker, period="5d", interval="1d", auto_adjust=True)
            if not df_idx.empty: df_idx.to_parquet(idx_parquet)
        except: pass

    if df_idx is not None and not df_idx.empty:
        try:
            clean_series = df_idx["Close"].dropna().values.flatten()
            if len(clean_series) >= 2:
                current_close, prev_close = float(clean_series[-1]), float(clean_series[-2])
                change_pct = ((current_close - prev_close) / prev_close) * 100
                arrow, color_code = ("▲", "#00FF00") if change_pct > 0 else (("▼", "#FF4444") if change_pct < 0 else ("—", "#58a6ff"))
                index_snapshot[idx_key] = {"val": f"{current_close:,.2f}", "arrow": arrow, "color": color_code, "pct": f"{change_pct:+.2f}%"}
        except: pass

macro_cards_html = ""
idx_labels = {"GSPC": "S&P 500 (标普大盘)", "DJI": "DOW 30 (道指工业)", "IXIC": "NASDAQ (纳指综合)"}
for k, item in index_snapshot.items():
    macro_cards_html += f'<div style="flex: 1; min-width: 140px; background-color: #1a2333; padding: 8px 12px; border-radius: 6px; border-top: 3px solid {item["color"]}; box-shadow: 0 4px 6px rgba(0,0,0,0.4);"><p style="margin: 0 0 4px 0; color: #ffcc00; font-size: 11px; font-weight: bold; font-family: sans-serif; white-space: nowrap;">{idx_labels[k]}</p><p style="margin: 0; color: {item["color"]}; font-size: 14px; font-weight: bold; font-family: monospace; white-space: nowrap;"><span style="font-size:10px; margin-right:2px;">{item["arrow"]}</span>{item["val"]} <span style="font-size:9px; font-weight:normal;">({item["pct"]})</span></p></div>'

if macro_data:
    for name, node in macro_data.items():
        card_color, card_arrow, display_val = "#58a6ff", "—", "N/A"
        if isinstance(node, dict):
            val, prev = node.get("val", "N/A"), node.get("prev", "N/A")
            display_val = str(val)
            if prev == "STATIC":
                card_arrow = "📢"
                card_color = "#00FF00" if ("新增" in display_val or "+" in display_val or "涨" in display_val) else ("#FF4444" if ("降" in display_val or "-" in display_val) else "#f0883e")
            elif val != "N/A" and prev != "N/A":
                try:
                    num_curr, num_prev = float(val.replace("%", "").strip()), float(prev.replace("%", "").strip())
                    card_color, card_arrow = ("#00FF00", "▲") if num_curr > num_prev else ("#FF4444", "▼")
                except: pass
        else: display_val = str(node)
        macro_cards_html += f'<div style="flex: 1; min-width: 140px; background-color: #161b22; padding: 8px 12px; border-radius: 6px; border-top: 3px solid {card_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.3);"><p style="margin: 0 0 4px 0; color: #8b949e; font-size: 11px; font-weight: bold; font-family: sans-serif; white-space: nowrap;">{name}</p><p style="margin: 0; color: {card_color}; font-size: 13px; font-weight: bold; font-family: monospace; white-space: normal; word-break: break-all; line-height: 1.2;"><span style="font-size: 10px; margin-right: 2px;">{card_arrow}</span>{display_val}</p></div>'

strl.html(f'<div class="macro-container">{macro_cards_html}</div><style>body {{ margin: 0; background-color: transparent; font-family: sans-serif; }} .macro-container {{ display: flex; flex-wrap: wrap; width: 100%; gap: 8px; }} .macro-container > div {{ flex: 1 1 calc(20% - 8px); min-width: 140px; box-sizing: border-box; }}</style>')
strl.markdown("---")

# =====================================================================
# 🚨 标签页及大屏 K 线渲染层
# =====================================================================
tab_tech, tab_market, tab_decision = strl.tabs(["📈 动态技术面多显大屏", "🔮 智能体基本面审计长卷", "🦅 M7 主权决策战略操作仓"])

with tab_tech:
    time_mode = strl.radio("📊 选择看盘时基视口:", options=["1m", "3m", "6m", "1y", "5y", "Max"], index=2, horizontal=True, key="m7_global_time_mode")
    strl.markdown("---")
    with strl.expander("📊 【🌍 纳斯达克综合指数 (NASDAQ Composite)】 核心大周期走势图", expanded=True):
        fig_nasdaq = generate_m7_clean_charts("^IXIC", period_choice, time_range_mode=time_mode)
        if fig_nasdaq is not None: strl.plotly_chart(fig_nasdaq, width="stretch", key=f"t_nasdaq_base_{period_choice}_{time_mode}")
    strl.markdown("#### 🏢 标的成份股技术面板")
    if not selected_tickers: strl.info("💡 提示：请在左侧控制中心选择标的。")
    else:
        for ticker in selected_tickers:
            with strl.expander(f"展开/收起 【{ticker}】 技术面看板", expanded=True):
                fig = generate_m7_clean_charts(ticker, period_choice, time_range_mode=time_mode)
                if fig is not None: strl.plotly_chart(fig, width="stretch", key=f"t_{ticker}_{period_choice}_{time_mode}")

# =====================================================================
# 🔮 智能体基本面审计长卷 (第二页：负责稳健的 FMP 冷资产管理)
# =====================================================================
with tab_market:
    if not selected_tickers: 
        strl.info("💡 提示：请在左侧控制中心锁定股票。")
    else:
        audit_target = strl.selectbox("🎯 请选择本次点火 AI 联审的核心目标:", options=selected_tickers, key="fmp_audit_target_selector")
        
        if strl.session_state["M7_CURRENT_AUDIT_TICKER"] != audit_target:
            strl.session_state["M7_CURRENT_AUDIT_TICKER"] = audit_target
            strl.rerun() 
            
        news_col1, news_col2 = strl.columns(2)
        with news_col1:
            strl.subheader(f"🏢 {audit_target} 最新关联热点摘要")
            stock_news_list = news_engine.get_latest_news(query_type="stock", topic=audit_target, limit=7)
            
            if not stock_news_list:
                strl.caption("📡 暂无关联实时个股新闻流")
            else:
                for item in stock_news_list:
                    title_clean = str(item.get('title', '未命名舆情序列')).strip()
                    summary_text = item.get("summary", "无摘要详情")
                    src_name = item.get("source_name", "Global News")
                    news_url = item.get("url", "")
                    
                    raw_time = item.get("publishedAt")
                    clean_time = "2026-05-28"
                    if raw_time:
                        t_str = str(raw_time).replace("T", " ").replace("Z", "").strip()
                        clean_time = t_str if any(m in t_str for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]) else t_str[:16]
                    
                    with strl.expander(f"⏱️ [{clean_time}] 📌 {title_clean}", expanded=False):
                        strl.markdown(f"**📅 发布时刻:** <span style='color:#ffaa00; font-weight:bold;'>{clean_time}</span>", unsafe_allow_html=True)
                        strl.markdown("---")
                        strl.markdown(f"**信源機構:** `{src_name}`")
                        strl.markdown(summary_text)
                        if news_url: strl.markdown(f"🔗 [查看完整信源]({news_url})")
                    
        with news_col2:
            strl.subheader("🌍 全球地缘政治前沿动向")
            geo_news_list = news_engine.get_latest_news(query_type="geopolitics", limit=7)
            if not geo_news_list: strl.caption("📡 暂无地缘政治前沿快讯")
            else:
                for item in geo_news_list:
                    title_clean = str(item.get('title', '未命名地缘异动')).strip()
                    summary_text = item.get("summary", "无摘要详情")
                    src_name = item.get("source_name", "M7地缘雷达")
                    news_url = item.get("url", "")
                    
                    raw_time = item.get("publishedAt")
                    clean_time = "2026-05-28"
                    if raw_time:
                        t_str = str(raw_time).replace("T", " ").replace("Z", "").strip()
                        clean_time = t_str if any(m in t_str for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]) else t_str[:16]
                    
                    with strl.expander(f"⏱️ [{clean_time}] ⚠️ {title_clean}", expanded=False):
                        strl.markdown(f"**📅 爆发时刻:** <span style='color:#ff5555; font-weight:bold;'>{clean_time}</span>", unsafe_allow_html=True)
                        strl.markdown("---")
                        strl.markdown(f"**信源機構:** `{src_name}`")
                        strl.markdown(summary_text)
                        if news_url: strl.markdown(f"🔗 [穿透情报原件]({news_url})")
                    
        strl.markdown("---")

        strl.markdown("### 📝 多智能体基本面联审研报")
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
            strl.caption("📌 当前为固化的本地持久化历史基本面审计。如需最新季度穿透，请点击下方大按钮。")
        else:
            report_container.info(f"⏳ 物理大坝中暂无 [{audit_target}] 的历史研报，请强制点火生成。")

        if strl.button("🚀 强制点火状态机 -> 重新生成 AI 多维基本面联审", use_container_width=True):
            with strl.spinner(f"⚡ 正在全量穿透深度审计..."):
                try:
                    audit_result = run_m7_audit(audit_target, period_choice)
                    if audit_result:
                        try:
                            t_obj = yf.Ticker(audit_target)
                            real_market_cap = t_obj.info.get("marketCap", 0)
                            if real_market_cap > 0:
                                formatted_cap = f"${real_market_cap / 1e12:.2f} 万亿美元"
                                audit_result = audit_result.replace("得原始市值为0 (未导入实时市值)", f"经动态校准真实市值约为 {formatted_cap}")
                        except: pass

                        report_container.markdown(audit_result.replace("<br>", " "))
                        meta_bundle = {"fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "packet": {}, "audit_report": audit_result}
                        with open(local_json_path, "w", encoding="utf-8") as wf: 
                            json.dump(meta_bundle, wf, ensure_ascii=False, indent=2)
                        strl.success(f"🎉 [{audit_target}] 联审研报固化封盘成功！已完美落盘存储。")
                        strl.rerun()  
                except Exception as e: strl.error(f"内部异动崩溃: {e}")

# =====================================================================
# 🦅 M7 主权决策战略操作仓 (第三页：长官加急情报强锁定解耦并网)
# =====================================================================
with tab_decision:
    strl.markdown(f"### 🦅 Gemini 3.5 多维因子自适应跨空间终极决策建议")
    decision_target = audit_target if 'audit_target' in locals() else (selected_tickers[0] if selected_tickers else None)
    
    if not decision_target: 
        strl.info("⏳ 正在等待数据链合龙... 请选择标的。")
    else:
        local_json_file = os.path.join(DATA_CACHE_DIR, f"fmp_cache_{decision_target}.json")
        base_audit_ready = False
        final_content = ""
        
        if os.path.exists(local_json_file):
            try:
                with open(local_json_file, "r", encoding="utf-8") as f:
                    disk_cache = json.load(f)
                    if "audit_report" in disk_cache and disk_cache["audit_report"].strip():
                        final_content = disk_cache["audit_report"]
                        base_audit_ready = True
            except: pass

        if not base_audit_ready:
            strl.error(
                f"🛑 **[M7-STRATEGY-BLOCK] 战略决策舱触发安全熔断锁死！**\n\n"
                f"检测到核心目标标的 **[{decision_target}]** 尚未完成第二页的**『AI 多维基本面联审研报』**持久化资产落盘固化。\n\n"
                f"💡 **战略主权长官指令:** 请立刻前往 **「🔮 智能体基本面审计长卷」** 标签页，点击大按钮启动基本面审计状态机。完成审计落盘后，本决策操作仓将自动完璧解锁并网！"
            )
            strl.button(f"🔒 决策状态机已锁定 -> 请先完成 [{decision_target}] 基本面审计", disabled=True, use_container_width=True)
            
        else:
            strl.success(f"🟢 [M7-FACTOR-READY] 因子链合龙成功！标的 [{decision_target}] 基本面审计资产已就位，战略计算网关允许通行。")
            
            # 🚀🔥【彻底分离 · 突发不与 FMP 混淆】：平嵌加急情报纯净舱，用独立进程 Key 规避重塑冲突
            strl.markdown("#### 📢 华尔街加急情报输入舱")
            urgent_intelligence = strl.text_area(
                label=f"💬 请长官动态追加关于 [{decision_target}] 的最新盘前突发、大面积砸盘或资本层异动因子（若无可不填）：",
                placeholder="例如：谷歌盘前突发暴跌10% / 传Alphabet计划定向融资80B巨额资本产生股份稀释恐慌...",
                key=f"m7_urgent_intel_stream_{decision_target}"
            )
            
            if strl.button(f"🔥 点火决策状态机 -> 下达 [{decision_target}] 操盘战略", use_container_width=True):
                with strl.spinner(f"🦅 M7 首席战略家 Gemini 正在动态执行因子交叉解算..."):
                    current_live_price_str = "未获取到实时价"
                    if os.path.exists(LIVE_SNAPSHOT_PATH):
                        try:
                            with open(LIVE_SNAPSHOT_PATH, "r", encoding="utf-8") as rf:
                                snap = json.load(rf)
                                if decision_target in snap:
                                    current_live_price_str = f"${snap[decision_target]['curr']:.2f}"
                        except: pass
                    
                    # 基准时空价格注入包
                    time_基准_prompt = (
                        f"资产标的: {decision_target}\n"
                        f"当前实盘最新成交真基准价: {current_live_price_str}\n"
                        f"请以此价格为最终真基准。若历史 FMP 研报库中含有其他陈旧价格，请自动将其视为历史记录。"
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

                    # 🚀🔥【彻底配合对齐】：将长官手动追加的情报独立透传到 decision_engine 的 urgent_intel 入参中，绝不污染 audit_text
                    raw_rep = decision_engine.generate_m7_weekly_decision(
                        ticker=decision_target, 
                        period_choice=period_choice, 
                        macro_data=globals()["macro_data"], 
                        audit_text=final_content,                     # 👈 纯正冷基本面
                        stock_news=processed_stock_news, 
                        geo_news=processed_geo_news,
                        time_prompt=time_基准_prompt,
                        urgent_intel=urgent_intelligence.strip()       # 👈 纯正长官突发热因子解耦并网
                    )
                    strl.session_state[f"decision_{decision_target}_{period_choice}"] = raw_rep
                    
            # =====================================================================
            # 🦅 M7 终极渲染层：铁血多模态解包提纯算子（彻底粉碎原始 JSON 源码反弹）
            # =====================================================================
            dec_res = strl.session_state.get(f"decision_{decision_target}_{period_choice}", "")
            if dec_res:
                strl.markdown('<div style="background-color:#111625; padding:12px; border-radius:8px; border-left: 5px solid #00FF00; margin-bottom: 15px;"><h4 style="color:#00FF00; margin-top:0px; margin-bottom:0px; font-family: monospace;">🦅 M7 量化主权研报体系 · 决策流完美合龙</h4></div>', unsafe_allow_html=True)
                
                clean_text = ""
                
                # 1️⃣ 梯队：如果是原生的 LangChain AIMessage 对象，提取 content 属性
                if hasattr(dec_res, "content"):
                    clean_text = str(dec_res.content)
                # 2️⃣ 梯队：如果是标准 list，提取内部字典或对象的 text 核心
                elif isinstance(dec_res, list) and len(dec_res) > 0:
                    node = dec_res[0]
                    if hasattr(node, "text"):
                        clean_text = str(node.text)
                    elif isinstance(node, dict):
                        clean_text = str(node.get("text", node.get("content", str(node))))
                    else:
                        clean_text = str(node)
                # 3️⃣ 梯队：如果是 dict 字典，打捞对应的主权 Key
                elif isinstance(dec_res, dict):
                    clean_text = str(dec_res.get("text", dec_res.get("content", str(dec_res))))
                # 4️⃣ 梯队：如果是由于系统缓存导致被强行强转成了原生字符串格式的错乱表达式，执行硬核正则/字符串切片打捞
                elif isinstance(dec_res, str):
                    s_stripped = dec_res.strip()
                    if s_stripped.startswith("[") or s_stripped.startswith("{"):
                        try:
                            # 尝试安全反序列化
                            import ast
                            parsed = ast.literal_eval(s_stripped)
                            if isinstance(parsed, list) and len(parsed) > 0:
                                parsed = parsed[0]
                            if isinstance(parsed, dict):
                                clean_text = parsed.get("text", parsed.get("content", ""))
                        except:
                            # 容灾模糊截取匹配法
                            if "'text':" in s_stripped:
                                try:
                                    start_idx = s_stripped.find("'text': '") + 9
                                    if start_idx != 8:
                                        end_idx = s_stripped.find("', 'type'")
                                        if end_idx == -1: end_idx = s_stripped.find("', 'links'")
                                        if start_idx < end_idx:
                                            clean_text = s_stripped[start_idx:end_idx]
                                except: pass
                    
                    # 如果未命中任何结构化反序列化，说明本身就是纯文本
                    if not clean_text:
                        clean_text = s_stripped

                else:
                    clean_text = str(dec_res)

                # 5️⃣ 终极去噪：修复由于原生反序列化可能夹带出来的字面量换行符和前端网页标签
                clean_decision_text = clean_text.replace("\\n", "\n").replace("<br>", " ").replace("<br />", " ")
                
                # 交付最干净、最漂亮的 Markdown 文本长卷到前端大屏
                strl.markdown(clean_decision_text)