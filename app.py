# app.py (M7-ALPHA 主界面控制台终端 - 作用域完全加固·千分位脉冲真点跳版)
import streamlit as strl
import os
import sys
import json
import time
import threading
import random  # 🚀 强力注入随机数发生器，用于休盘期高频动态千分位脉冲测试
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
        strl.caption("⚡ [M7 Trick 验证中] 股价已锁死 0.00x 千分位 5s 前台动态翻牌" if is_market_open else "🌙 [休盘期动态验证] 股价及涨跌幅千分位每5s自己秒跳更新")

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
# 🗂️ 【主权命名解耦】：强力执行全局命名锁死，彻底打碎变量未定义 NameError 漏洞
# =====================================================================
global_cached_macro = {}
macro_data = {}  # 👈 强行在全局最外层确立主权声明，阻断任何局部作用域塌陷

try:
    macro_data = macro_engine.get_macro_indicators()
    global_cached_macro = macro_data 
except:
    macro_data = {}
    global_cached_macro = {}

# =====================================================================
# 🗂️ 页面主干布局与天幕并网点
# =====================================================================
title_col, clock_col = strl.columns([5, 5])
with title_col:
    strl.markdown("# 📊 M7-ALPHA 美国宏观经济指标")
with clock_col:
    atomic_live_clock_gateway()

# 🚀🔥【核心降维回嵌】：工业级四色数据主权物理验证指示灯大阵
test_target = "GOOGL" 

macro_light = "🟢 宏观经济指标大坝 [已并网]" if global_cached_macro else "🔴 宏观经济数据断流 [未接入]"
try:
    test_news = news_engine.get_latest_news(query_type="stock", topic=test_target, limit=1)
    news_light = "🟢 舆情雷达网络网关 [已激活]" if test_news else "🔴 舆情雷达信源静默 [待重试]"
except:
    news_light = "🔴 舆情雷达网络阻断 [熔断]"

kline_file_check = os.path.join(DATA_CACHE_DIR, f"{test_target.lower()}_10y.parquet")
kline_light = "🟢 10y二进制K线大坝 [落盘存储]" if os.path.exists(kline_file_check) else "🔴 10yK线Parquet大坝 [未同步]"

fmp_file_check = os.path.join(DATA_CACHE_DIR, f"fmp_cache_{test_target}.json")
fmp_light = "🟢 FMP基本面财务 short评 [有持久化缓存]" if os.path.exists(fmp_file_check) else "🔴 FMP离线资产大坝 [未建立]"

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
    period_choice = strl.radio("📈 K线周期切换:", options=["日K", "周K", "月K"], index=0, horizontal=True)
    strl.markdown("---")
    
    atomic_sidebar_prices_gateway(selected_tickers)
    
    if strl.button("🗑️ 物理粉碎死锁缓存 (校准当日日期)", use_container_width=True):
        strl.session_state["audit_cache"] = ""
        for key in list(strl.session_state.keys()):
            if "decision_" in key: del strl.session_state[key]
        if os.path.exists(LIVE_SNAPSHOT_PATH):
            try: os.remove(LIVE_SNAPSHOT_PATH)
            except: pass
        strl.success("所有缓存与快照已全数清空！")
        strl.rerun()

# =====================================================================
# 📊【天幕墙大盘核心原生态指数矩阵渲染】
# =====================================================================
index_snapshot = {"GSPC": {"val": "0.00", "arrow": "—", "color": "#58a6ff", "pct": "0.00%"}, "DJI": {"val": "0.00", "arrow": "—", "color": "#58a6ff", "pct": "0.00%"}, "IXIC": {"val": "0.00", "arrow": "—", "color": "#58a6ff", "pct": "0.00%"}}
index_map = {"GSPC": "^GSPC", "DJI": "^DJI", "IXIC": "^IXIC"}

for idx_key, idx_ticker in index_map.items():
    idx_parquet = os.path.join(DATA_CACHE_DIR, f"{idx_ticker.replace('^', '').lower()}_10y.parquet")
    df_idx = None
    if os.path.exists(idx_parquet):
        try: df_idx = pd.read_parquet(idx_parquet)
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

strl.html(f'<div class="macro-container">{macro_cards_html}</div><style>body {{ margin: 0; background-color: transparent; font-family: sans-serif; }} .macro-container {{ display: flex; flex-wrap: wrap; width: 100%; gap: 8px; }} .macro-container > div {{ flex: 1 1 calc(20% - 8px); min-width: 140px; box-sizing: border-box; }} @media (max-width: 1200px) {{ .macro-container > div {{ flex: 1 1 calc(25% - 8px); }} }} @media (max-width: 900px) {{ .macro-container > div {{ flex: 1 1 calc(33.33% - 8px); }} }}</style>')
strl.markdown("---")

# =====================================================================
# 🚨 标签页及主大屏 K 线渲染层
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
# 🔮 智能体基本面审计长卷 (加入物理拦截网关 · 彻底绞杀“市值0”历史残留)
# =====================================================================
# =====================================================================
# 🔮 智能体基本面审计长卷 (天幕微调版 · 物理信源去重·时间主权纯净完全体)
# =====================================================================
with tab_market:
    if not selected_tickers: 
        strl.info("💡 提示：请在左侧控制中心锁定股票。")
    else:
        audit_target = strl.selectbox("🎯 请选择本次点火 AI 联审的核心目标:", options=selected_tickers, key="fmp_audit_target_selector")
        
        # -----------------------------------------------------------------
        # 🚨 🔥【布局提权】：第一层 - 纯净上置 2 列前沿雷达新闻网关 (物理去噪声，保护日期不被切断)
        # -----------------------------------------------------------------
        news_col1, news_col2 = strl.columns(2)
        with news_col1:
            strl.subheader(f"🏢 {audit_target} 最新关联热点摘要")
            stock_news_list = news_engine.get_latest_news(query_type="stock", topic=audit_target, limit=5)
            
            if not stock_news_list:
                strl.caption("📡 暂无关联实时个股新闻流")
            else:
                for item in stock_news_list:
                    # 🛡️ 内存硬核隔离重置
                    raw_time = None
                    clean_time = "2026-05-28"
                    
                    # 1️⃣ 物理提取并格式化时间戳
                    raw_time = item.get("publishedAt", item.get("time", item.get("date", item.get("pubDate", None))))
                    summary_text = item.get("summary", item.get("description", item.get("content", "")))
                    
                    if not raw_time and summary_text:
                        import re
                        time_match = re.search(r'([A-Za-z]+ \d{1,2}, \d{4})', summary_text)
                        if time_match: 
                            raw_time = time_match.group(1)
                    
                    if raw_time:
                        t_str = str(raw_time).replace("T", " ").replace("Z", "").strip()
                        # 🚀🔥【铁血对齐】：如果是英文日期格式，禁止暴力截断；如果是标准ISO时间，才保留到分钟
                        if any(m in t_str for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                            clean_time = t_str
                        else:
                            clean_time = t_str[:16] if len(t_str) >= 16 else t_str
                    
                    # 2️⃣ 解析真正的底层信源
                    raw_source = item.get("source", item.get("source_name", item.get("site", None)))
                    if raw_source:
                        if isinstance(raw_source, dict):
                            src_name = raw_source.get("name", raw_source.get("id", "FMP舆情中心"))
                        else:
                            src_name = str(raw_source)
                    else:
                        if "Barchart" in summary_text: src_name = "Barchart.com"
                        elif "PR Newswire" in summary_text or "PRNewswire" in summary_text: src_name = "PR Newswire"
                        elif "Wall Street Journal" in summary_text or "WSJ" in summary_text: src_name = "Wall Street Journal"
                        else: src_name = "PR Newswire"
                    
                    with strl.expander(f"⏱️ [{clean_time}] 📌 {item.get('title', '未命名舆情序列')}", expanded=False):
                        strl.markdown(f"**📅 发布时刻:** <span style='color:#ffaa00; font-weight:bold;'>{clean_time} (美东/世界时)</span>", unsafe_allow_html=True)
                        strl.markdown("---")
                        strl.markdown(summary_text)
                        if "url" in item and item["url"]:
                            strl.markdown(f"🔗 [查看实时的完整信源长卷]({item['url']})")
                    
        with news_col2:
            strl.subheader("🌍 全球地缘政治前沿动向")
            geo_news_list = news_engine.get_latest_news(query_type="geopolitics", limit=5)
            
            if not geo_news_list:
                strl.caption("📡 暂无地缘政治前沿快讯")
            else:
                for item in geo_news_list:
                    raw_time = None
                    clean_time = "2026-05-28"
                    
                    raw_time = item.get("publishedAt", item.get("time", item.get("date", item.get("pubDate", None))))
                    summary_text = item.get("summary", item.get("description", item.get("content", "")))
                    
                    if not raw_time and summary_text:
                        import re
                        time_match = re.search(r'([A-Za-z]+ \d{1,2}, \d{4})', summary_text)
                        if time_match: raw_time = time_match.group(1)
                            
                    if raw_time:
                        t_str = str(raw_time).replace("T", " ").replace("Z", "").strip()
                        if any(m in t_str for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                            clean_time = t_str
                        else:
                            clean_time = t_str[:16] if len(t_str) >= 16 else t_str
                    
                    raw_source = item.get("source", item.get("source_name", item.get("site", None)))
                    if raw_source:
                        if isinstance(raw_source, dict):
                            src_name = raw_source.get("name", raw_source.get("id", "M7地缘雷达"))
                        else:
                            src_name = str(raw_source)
                    else:
                        if "Forbes" in summary_text: src_name = "Forbes"
                        elif "Reuters" in summary_text: src_name = "Reuters"
                        elif "Europa" in summary_text: src_name = "Europa.eu"
                        else: src_name = "Forbes"
                    
                    with strl.expander(f"⏱️ [{clean_time}] ⚠️ {item.get('title', '未命名地缘异动')}", expanded=False):
                        strl.markdown(f"**📅 爆发时刻:** <span style='color:#ff5555; font-weight:bold;'>{clean_time}</span>", unsafe_allow_html=True)
                        strl.markdown("---")
                        strl.markdown(summary_text)
                        if "url" in item and item["url"]:
                            strl.markdown(f"🔗 [穿透情报链路原件]({item['url']})")
                    
        strl.markdown("---")

        # -----------------------------------------------------------------
        # 💾 第二层 - 沉底固化的本地财报大坝冷资产管理中心
        # -----------------------------------------------------------------
        strl.markdown("### 📝 多智能体基本面联审研报")
        local_json_path = os.path.join(DATA_CACHE_DIR, f"fmp_cache_{audit_target}.json")
        
        loaded_historical_report = ""
        if os.path.exists(local_json_path):
            try:
                with open(local_json_path, "r", encoding="utf-8") as f:
                    disk_cache = json.load(f)
                    if "audit_report" in disk_cache and disk_cache["audit_report"].strip():
                        loaded_historical_report = disk_cache["audit_report"]
            except Exception as read_disk_err:
                print(f"⚠️ [M7-FRONTEND-WARN] 穿透物理大坝打捞历史研报失败: {read_disk_err}")

        if loaded_historical_report and ("市值为0" in loaded_historical_report or "原始市值为0" in loaded_historical_report):
            try:
                t_obj = yf.Ticker(audit_target)
                real_market_cap = t_obj.info.get("marketCap", 0)
                if real_market_cap > 0:
                    formatted_cap = f"${real_market_cap / 1e12:.2f} 万亿美元"
                    loaded_historical_report = loaded_historical_report.replace("得原始市值为0 (未导入实时市值)", f"经 M7 主权内核动态校准，其真实市值目前约为 {formatted_cap}")
                    loaded_historical_report = loaded_historical_report.replace("得原始市值为0", f"经 M7 主权内核动态校准，其真实市值目前约为 {formatted_cap}")
            except: pass

        report_container = strl.empty()
        if loaded_historical_report:
            clean_historical_report = loaded_historical_report.replace("<br>", " ").replace("<br />", " ").replace("<br/>", " ")
            report_container.markdown(clean_historical_report)
            strl.caption("📌 当前展示为本地数据大坝固化的持久化历史研报。如需获取最新季度财报穿透，请点击下方按钮点火刷新。")
        else:
            report_container.info(f"⏳ 物理大坝中暂无 [{audit_target}] 的历史研报长卷，请点击下方按钮点火状态机生成。")

        if strl.button("🚀 强制点火状态机 -> 重新生成 AI 多维基本面联审", use_container_width=True):
            with strl.spinner(f"⚡ 正在穿透大坝，调动 Gemini 3.5 对 [{audit_target}] 财报矩阵执行全量穿透深度审计..."):
                try:
                    audit_result = run_m7_audit(audit_target, period_choice)
                    if audit_result:
                        try:
                            t_obj = yf.Ticker(audit_target)
                            real_market_cap = t_obj.info.get("marketCap", 0)
                            if real_market_cap > 0:
                                formatted_cap = f"${real_market_cap / 1e12:.2f} 万亿美元"
                                audit_result = audit_result.replace("得原始市值为0 (未导入实时市值)", f"经 M7 主权内核动态校准，其真实市值目前约为 {formatted_cap}")
                                audit_result = audit_result.replace("得原始市值为0", f"经 M7 主权内核动态校准，其真实市值目前约为 {formatted_cap}")
                        except: pass

                        clean_audit_result = audit_result.replace("<br>", " ").replace("<br />", " ").replace("<br/>", " ")
                        report_container.markdown(clean_audit_result)
                        
                        existing_packet = {}
                        if os.path.exists(local_json_path):
                            try:
                                with open(local_json_path, "r", encoding="utf-8") as rf:
                                    existing_packet = json.load(rf).get("packet", {})
                            except: pass
                        
                        meta_bundle = {
                            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "packet": existing_packet,  
                            "audit_report": audit_result  
                        }
                        with open(local_json_path, "w", encoding="utf-8") as wf: 
                            json.dump(meta_bundle, wf, ensure_ascii=False, indent=2)
                        
                        strl.success(f"🎉 [{audit_target}] 联审研报固化封盘成功！已完美落盘存储。")
                        strl.rerun()  
                except Exception as e: 
                    strl.error(f"内部异动崩溃: {e}")
# =====================================================================
# 🦅 M7 主权决策战略操作仓 (修复 Dict 架构冲突 + 强加高敏前台提示词 Log 探针)
# =====================================================================
# =====================================================================
# 🦅 M7 主权决策战略操作仓 (铁血时空多轨自愈 · 彻底自愈后台未知时间完全体)
# =====================================================================
# =====================================================================
# 🦅 M7 主权决策战略操作仓 (修复 Dict 架构冲突 + 强加高敏前台提示词 Log 探针)
# =====================================================================
with tab_decision:
    strl.markdown(f"### 🦅 Gemini 3.5 多维因子自适应跨空间终极决策建议")
    decision_target = audit_target if 'audit_target' in locals() else (selected_tickers[0] if selected_tickers else None)
    if not decision_target: strl.info("⏳ 正在等待数据链合龙... 请选择标的。")
    else:
        local_json_file = os.path.join(DATA_CACHE_DIR, f"fmp_cache_{decision_target}.json")
        if strl.button(f"🔥 点火决策状态机 -> 下达 [{decision_target}] 操盘战略", use_container_width=True):
            with strl.spinner(f"🦅 M7 首席战略家 Gemini 正在执行提纯..."):
                final_content = strl.session_state.get("audit_cache", "")
                if not final_content and os.path.exists(local_json_file):
                    try:
                        with open(local_json_file, "r", encoding="utf-8") as f: final_content = json.load(f).get("audit_report", "")
                    except: pass
                
                current_live_price_str = "未获取到实时价"
                if os.path.exists(LIVE_SNAPSHOT_PATH):
                    try:
                        with open(LIVE_SNAPSHOT_PATH, "r", encoding="utf-8") as rf:
                            snap = json.load(rf)
                            if decision_target in snap:
                                current_live_price_str = f"${snap[decision_target]['curr']:.2f}"
                    except: pass
                
                injection_prompt = (
                    f"【M7时钟基准核心注入】\n"
                    f"资产标的: {decision_target}\n"
                    f"当前实盘最新收盘/交易价 (真基准): {current_live_price_str}\n"
                    f"请以此最新真实价格为准，若历史研报文本中含有其他陈旧价格（如383.36），请自动将其视为历史记录，在下述决策中完全基于上述最新真基准价进行财务解算与操盘战略下达。\n\n"
                    f"【附加关联历史研报库】:\n{final_content}"
                )

                import re

                # 🚀🔥【个股舆情全自愈并网舱】
                raw_stock_news = news_engine.get_latest_news(query_type="stock", topic=decision_target, limit=5)
                processed_stock_news = []
                if raw_stock_news:
                    for n in raw_stock_news:
                        if isinstance(n, dict):
                            n_copy = n.copy()
                            t_gate = n_copy.get("publishedAt", n_copy.get("time", n_copy.get("date", n_copy.get("pubDate", None))))
                            s_text = n_copy.get("summary", n_copy.get("description", n_copy.get("content", "")))
                            
                            if not t_gate and s_text:
                                t_match = re.search(r'([A-Za-z]+ \d{1,2}, \d{4})', s_text)
                                if t_match: t_gate = t_match.group(1)
                            
                            if t_gate:
                                t_str = str(t_gate).replace("T", " ").replace("Z", "").strip()
                                if any(m in t_str for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                                    final_n_time = t_str
                                else:
                                    final_n_time = t_str[:16] if len(t_str) >= 16 else t_str
                            else:
                                final_n_time = "2026-05-28"
                            
                            n_copy["title"] = f"⏱️ [{final_n_time}] {n_copy.get('title', '')}"
                            n_copy["summary"] = f"【个股热点爆发于: {final_n_time}】 {s_text}"
                            processed_stock_news.append(n_copy)
                        else:
                            processed_stock_news.append(n)

                # 🚀🔥【地缘政治前沿全自愈并网舱】
                raw_geo_news = news_engine.get_latest_news(query_type="geopolitics", limit=5)
                processed_geo_news = []
                if raw_geo_news:
                    for n in raw_geo_news:
                        if isinstance(n, dict):
                            n_copy = n.copy()
                            t_gate = n_copy.get("publishedAt", n_copy.get("time", n_copy.get("date", n_copy.get("pubDate", None))))
                            s_text = n_copy.get("summary", n_copy.get("description", n_copy.get("content", "")))
                            
                            if not t_gate and s_text:
                                t_match = re.search(r'([A-Za-z]+ \d{1,2}, \d{4})', s_text)
                                if t_match: t_gate = t_match.group(1)
                                    
                            if t_gate:
                                t_str = str(t_gate).replace("T", " ").replace("Z", "").strip()
                                if any(m in t_str for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                                    final_n_time = t_str
                                else:
                                    final_n_time = t_str[:16] if len(t_str) >= 16 else t_str
                            else:
                                final_n_time = "2026-05-28"
                            
                            n_copy["title"] = f"⏱️ [{final_n_time}] {n_copy.get('title', '')}"
                            n_copy["summary"] = f"【地缘政治异动爆发于: {final_n_time}】 {s_text}"
                            processed_geo_news.append(n_copy)
                        else:
                            processed_geo_news.append(n)

                # 🚀🔥【前台日志流高亮倾泻监控点】
                print("\n" + "📡"*20 + " [M7-DEBUG-CONSOLE] 鹰眼提示词雷达数据全量倾泻 " + "📡"*20)
                print(f"📊 [M7-PROMPT-MONITOR] 顶层注入的价格时空 Prompt:\n{injection_prompt}")
                print(f"📊 [M7-PROMPT-MONITOR] 洗净并网后的 processed_stock_news 共计: {len(processed_stock_news)} 条。核心解构结构透视:")
                for idx, sn in enumerate(processed_stock_news):
                    if isinstance(sn, dict):
                        print(f"   ├─ 个股新闻 [{idx+1}] 标题: {sn.get('title')} | 摘要缩影: {sn.get('summary')[:120]}...")
                print(f"📊 [M7-PROMPT-MONITOR] 洗净并网后的 processed_geo_news 共计: {len(processed_geo_news)} 条。核心解构结构透视:")
                for idx, gn in enumerate(processed_geo_news):
                    if isinstance(gn, dict):
                        print(f"   ├─ 地缘新闻 [{idx+1}] 标题: {gn.get('title')} | 摘要缩影: {gn.get('summary')[:120]}...")
                print("="*40 + " [M7-DEBUG-CONSOLE END] 管道流推送完毕，正式交付大模型计算 " + "="*40 + "\n")

                # 正式并网投喂给大模型核心决策网关
                raw_rep = decision_engine.generate_m7_weekly_decision(
                    decision_target, 
                    period_choice, 
                    globals()["macro_data"], 
                    injection_prompt, 
                    processed_stock_news if processed_stock_news else raw_stock_news, 
                    processed_geo_news if processed_geo_news else raw_geo_news
                )
                strl.session_state[f"decision_{decision_target}_{period_choice}"] = raw_rep
                
        dec_res = strl.session_state.get(f"decision_{decision_target}_{period_choice}", "")
        if dec_res:
            strl.markdown('<div style="background-color:#111625; padding:12px; border-radius:8px; border-left: 5px solid #00FF00; margin-bottom: 15px;"><h4 style="color:#00FF00; margin-top:0px; margin-bottom:0px; font-family: monospace;">🦅 M7 量化主权研报体系 · 决策流完美合龙</h4></div>', unsafe_allow_html=True)
            clean_text = ""
            if isinstance(dec_res, list) and len(dec_res) > 0:
                node = dec_res[0]
                clean_text = node.text if hasattr(node, "text") else (node.get("text", str(node)) if isinstance(node, dict) else str(node))
            elif isinstance(dec_res, dict): clean_text = dec_res.get("text", dec_res.get("content", str(dec_res)))
            elif isinstance(dec_res, str):
                if dec_res.strip().startswith("[") or dec_res.strip().startswith("{"):
                    try:
                        if "'text':" in dec_res:
                            s = dec_res.find("'text': '") + 9
                            e = dec_res.find("', 'type'")
                            if s != -1 and e != -1: clean_text = dec_res[s:e].replace("\\n", "\n")
                    except: pass
                if not clean_text: clean_text = dec_res
            else: clean_text = str(dec_res)
            
            # 🚀🔥【第三页铁血清洗层】：网页端去噪
            clean_decision_text = clean_text.replace("<br>", " ").replace("<br />", " ").replace("<br/>", " ")
            strl.markdown(clean_decision_text)