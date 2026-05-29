# app.py (M7-ALPHA 主界面控制台终端 - 前收盘价真基准校准·完全体版)
import streamlit as strl
import os
import sys
import json
import time
import threading
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

NASDAQ_100_POOL = sorted(list(set([
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA", "AVGO", "PEP",
    "COST", "CSCO", "NFLX", "AMD", "CMCSA", "TMUS", "ADBE", "TXN", "INTC", "HON",
    "AMGN", "QCOM", "INTU", "SBUX", "ISRG", "MDLZ", "GILD", "BKNG", "AMAT", "ADI",
    "ADP", "VRTX", "REGN", "PYPL", "FISV", "LRCX", "MU", "PANW", "SNPS", "CDNS"
])))

strl.set_page_config(page_title="M7-ALPHA 量化多智能体终端", page_icon="📊", layout="wide")

# =====================================================================
# 🧠 🛡️ 【全局共享进程内存大坝】：前收盘价硬核咬合加固
# =====================================================================
if "M7_GLOBAL_STATIC_MEM" not in globals():
    globals()["M7_GLOBAL_STATIC_MEM"] = {}
    globals()["M7_TARGET_TICKERS"] = ["GOOGL", "NVDA"]

def m7_async_market_core_pump():
    """独立于 Streamlit 主进程之外的操作系统级守护线程
    昨收价双轨解算引擎，完美对齐真实行情走势"""
    while True:
        try:
            ny_tz = pytz.timezone('America/New_York')
            now_ny = datetime.now(ny_tz)
            is_weekday = now_ny.weekday() < 5
            current_time_str = now_ny.strftime("%H:%M")
            is_open = is_weekday and ("09:30" <= current_time_str <= "16:00")
            
            targets = list(globals()["M7_TARGET_TICKERS"])
            if targets:
                for t in targets:
                    try:
                        ticker_obj = yf.Ticker(t)
                        
                        # 🚀 轨一：拉取最新鲜的实时价格
                        df_live = ticker_obj.history(period="1d", interval="1m" if is_open else "1d", auto_adjust=True)
                        if df_live.empty:
                            continue
                        curr_p = float(df_live["Close"].dropna().values[-1])
                        
                        # 🚀 轨二：极速解算标准历史日线，物理提取【真正的昨收价】
                        # 为了对抗节假日与深夜除权，直接拉取5天日K，倒数第二根K线必是昨收价
                        df_daily = ticker_obj.history(period="5d", interval="1d", auto_adjust=True)
                        if not df_daily.empty:
                            daily_closes = df_daily["Close"].dropna().values.flatten()
                            
                            if is_open:
                                # 🟢 如果在开盘时段：最新一条日K可能包含今天，所以上一条 [-2] 是昨收
                                prev_p = float(daily_closes[-2]) if len(daily_closes) >= 2 else float(daily_closes[-1])
                            else:
                                # 🌙 如果在休盘时段：最新一条日K已经是收盘价了，前一日则是 [-2]
                                prev_p = float(daily_closes[-2]) if len(daily_closes) >= 2 else float(daily_closes[-1])
                        else:
                            # 灾备三级兜底：从 Info 字典里直接化缘 previousClose
                            prev_p = float(ticker_obj.info.get("previousClose", curr_p))

                        # 高精度执行主权看盘涨跌解算
                        p_change = curr_p - prev_p
                        p_pct = (p_change / prev_p) * 100
                        
                        # 100% 纯净数据推入全局内存大坝
                        globals()["M7_GLOBAL_STATIC_MEM"][t] = {
                            "curr": curr_p, "change": p_change, "pct": p_pct, "updated": time.time()
                        }
                    except Exception as inner_err:
                        print(f"后台双轨打捞 {t} 异常: {inner_err}")
            
            time.sleep(10 if is_open else 30)
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
# 🚀🔥【原子提权 Fragment 二】：昨收基准级·10s零转圈股价原子
# =====================================================================
@strl.fragment(run_every=5)
def atomic_sidebar_prices_gateway(selected_list):
    if selected_list:
        globals()["M7_TARGET_TICKERS"] = selected_list
        
        strl.markdown("### 💵 核心资产实时报价")
        ny_tz = pytz.timezone('America/New_York')
        now_ny = datetime.now(ny_tz)
        is_market_open = now_ny.weekday() < 5 and ("09:30" <= now_ny.strftime("%H:%M") <= "16:00")
        strl.caption("⚡ [昨收基准对齐] 侧边栏报价已锁死 10s 级异步无感点跳" if is_market_open else "🌙 美股休盘时段 · 维持最新历史快照")

        for ticker in selected_list:
            mem = globals()["M7_GLOBAL_STATIC_MEM"].get(ticker)
            
            if mem:
                curr_p = mem["curr"]
                p_change = mem["change"]
                p_pct = mem["pct"]
                
                # 🛡️ 物理提权：清理多余前置箭头符号，避免和 st.metric 底层图标打架
                # 显式控制：上涨正常绿（normal），下跌反转红（inverse）
                if p_change > 0:
                    p_delta_str = f"${p_change:+.2f} ({p_pct:+.2f}%)"
                    m_color = "normal"   
                elif p_change < 0:
                    p_delta_str = f"${p_change:.2f} ({p_pct:+.2f}%)"
                    m_color = "inverse"  
                else:
                    p_delta_str = f"$0.00 (0.00%)"
                    m_color = "off"
                
                strl.metric(label=f"标的: {ticker}", value=f"${curr_p:.2f}", delta=p_delta_str, delta_color=m_color)
            else:
                parquet_path = os.path.join(DATA_CACHE_DIR, f"{ticker.lower()}_10y.parquet")
                if os.path.exists(parquet_path):
                    try:
                        df_old = pd.read_parquet(parquet_path)
                        val = float(df_old["Close"].dropna().values[-1])
                        strl.metric(label=f"标的: {ticker}", value=f"${val:.2f}", delta="📡 大坝同步中...", delta_color="off")
                    except:
                        strl.caption(f"⏳ {ticker} 正在执行点火并网...")
                else:
                    strl.caption(f"⏳ {ticker} 正在执行点火并网...")

# =====================================================================
# 🗂️ 页面主干布局
# =====================================================================
title_col, clock_col = strl.columns([5, 5])
with title_col:
    strl.markdown("# 📊 M7-ALPHA 美国宏观经济指标")
with clock_col:
    atomic_live_clock_gateway()

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
        strl.success("内存缓存已释放！")
        strl.rerun()

# =====================================================================
# 📊【天幕墙大盘核心原生态矩阵渲染】
# =====================================================================
global_cached_macro = {}
try: macro_data = macro_engine.get_macro_indicators(); global_cached_macro = macro_data 
except: macro_data = {}

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
# 🚨 标签页核心大屏
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

with tab_market:
    if not selected_tickers: strl.info("💡 提示：请在左侧控制中心锁定股票。")
    else:
        strl.markdown("### 📝 多智能体基本面联审研报")
        audit_target = strl.selectbox("🎯 请选择本次点火 AI 联审的核心目标:", options=selected_tickers)
        report_container = strl.empty()
        local_json_path = os.path.join(DATA_CACHE_DIR, f"fmp_cache_{audit_target}.json")
        if "audit_cache" not in strl.session_state: strl.session_state["audit_cache"] = ""
        if not strl.session_state["audit_cache"] and os.path.exists(local_json_path):
            try:
                with open(local_json_path, "r", encoding="utf-8") as f: strl.session_state["audit_cache"] = f"💡 [M7-FMP-DOCK] 已成功识别资产大坝库：\n\n{json.load(f).get('audit_report', '')[:1200]}..."
            except: pass
        if strl.session_state["audit_cache"]: report_container.markdown(strl.session_state["audit_cache"])
        if strl.button("🚀 启动 AI 多维基本面联审 (点火状态机)", use_container_width=True):
            try:
                audit_result = run_m7_audit(audit_target, period_choice)
                if audit_result:
                    report_container.markdown(audit_result); strl.session_state["audit_cache"] = audit_result
                    with open(local_json_path, "w", encoding="utf-8") as wf: json.dump({"ticker": audit_target, "period": period_choice, "audit_report": audit_result}, wf, ensure_ascii=False, indent=2)
            except Exception as e: strl.error(f"异常: {e}")
        strl.markdown("---")
        news_col1, news_col2 = strl.columns(2)
        with news_col1:
            strl.subheader(f"🏢 {audit_target} 最新关联热点摘要")
            for item in news_engine.get_latest_news(query_type="stock", topic=audit_target, limit=5):
                with strl.expander(f"📌 {item['title']}", expanded=False): strl.markdown(item['summary'])
        with news_col2:
            strl.subheader("🌍 全球地缘政治前沿动向")
            for item in news_engine.get_latest_news(query_type="geopolitics", limit=5):
                with strl.expander(f"⚠️ {item['title']}", expanded=False): strl.markdown(item['summary'])

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
                raw_rep = decision_engine.generate_m7_weekly_decision(decision_target, period_choice, global_cached_macro, f"【M7时钟注入】\n当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}。\n" + final_content, news_engine.get_latest_news(query_type="stock", topic=decision_target, limit=5), news_engine.get_latest_news(query_type="geopolitics", limit=5))
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
            strl.markdown(clean_text)