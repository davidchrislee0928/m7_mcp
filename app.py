# app.py (M7-ALPHA 主界面控制台终端 - 2026核心天幕·两排响应式·双时区自愈完全体)
import streamlit as strl
import os
import sys
import json
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

# =====================================================================
# 💾 核心缓存根目录：物理铁血对接 Hugging Face /data 持久化大坝
# =====================================================================
if os.path.exists("/data"):
    BASE_CACHE_DIR = "/data"
else:
    BASE_CACHE_DIR = PROJECT_ROOT

DATA_CACHE_DIR = os.path.join(BASE_CACHE_DIR, "data_cache")
os.makedirs(DATA_CACHE_DIR, exist_ok=True)

# 📋 NASDAQ 100 成分股标准备选池
NASDAQ_100_POOL = sorted(list(set([
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA", "AVGO", "PEP",
    "COST", "CSCO", "NFLX", "AMD", "CMCSA", "TMUS", "ADBE", "TXN", "INTC", "HON",
    "AMGN", "QCOM", "INTU", "SBUX", "ISRG", "MDLZ", "GILD", "BKNG", "AMAT", "ADI",
    "ADP", "VRTX", "REGN", "PYPL", "FISV", "LRCX", "MU", "PANW", "SNPS", "CDNS"
])))

# 🎨 STREAMLIT UI 紧凑样式装配
strl.set_page_config(page_title="M7-ALPHA 量化多智能体终端", page_icon="📊", layout="wide")

# =====================================================================
# 🚀🔥【布局提权自愈】：大标题区与时钟区分裂 (彻底根除异步“同步中”死锁)
# =====================================================================
# =====================================================================
# 🚀🔥【布局提权自愈】：大标题区与时钟区分裂 (符合2026新规 · 纯前端毫秒级自驱动秒跳时钟)
# =====================================================================
# =====================================================================
# 🚀🔥【布局提权自愈】：大标题区与时钟区分裂 (彻底粉碎“加载中”沙盒异步执行死锁)
# =====================================================================
# =====================================================================
# 🚀🔥【布局提权自愈】：大标题区与时钟区分裂 (彻底粉碎 Iframe 沙盒隔离导致的“正在同步”死锁)
# =====================================================================
# =====================================================================
# 🚀🔥【布局提权自愈】：大标题区与时钟区分裂 (符合2026新规 · 原生 HTML 标签自点火秒跳时钟)
# =====================================================================
# =====================================================================
# 🚀🔥【布局提权自愈】：大标题区与时钟区分裂 (纯 Python 内存画布硬灌技术 · 100% 秒级实时更新走字)
# =====================================================================
# =====================================================================
# 🚀🔥【布局提权自愈】：大标题区与时钟区分裂 (彻底攻克静止不点跳死锁 · 纯前端高频脉冲时钟完全体)
# =====================================================================
# =====================================================================
# 🚀🔥【布局提权自愈】：大标题区与时钟区分裂 (2026全新 st.fragment 局部动能流 · 纯 Python 毫秒级自驱动秒跳完全体)
# =====================================================================
# =====================================================================
# 🚀🔥【布局提权自愈】：大标题区与时钟区分裂 (WebSocket 动能硬清洗 · 纯 Python 毫秒级自驱动真点跳完全体)
# =====================================================================
title_col, clock_col = strl.columns([5, 5]) # 微调比例，给双时区大数留足横向物理空间

with title_col:
    strl.markdown("# 📊 M7-ALPHA 美国宏观经济指标")

with clock_col:
    # 🌟 终极自愈防线：将时钟完全剥离为无 HTML 杂质的纯净 Fragment 局部渲染原子
    # 强制锁死 1 秒脉冲，通过官方原生的 WebSocket 通道每秒直接洗牌前台数字，彻底粉碎缓存死锁！
    @strl.fragment(run_every=1)
    def render_m7_absolute_live_clocks():
        try:
            # 穿透时区底层抓取当前微秒级时间大数
            now_bj = datetime.now(pytz.timezone('Asia/Shanghai'))
            now_ny = datetime.now(pytz.timezone('America/New_York'))
            
            bj_date = now_bj.strftime("%Y-%m-%d")
            bj_time = now_bj.strftime("%H:%M:%S")
            
            ny_date = now_ny.strftime("%Y-%m-%d")
            ny_time = now_ny.strftime("%H:%M:%S")
        except Exception:
            bj_date, bj_time = "同步中...", "00:00:00"
            ny_date, ny_time = "同步中...", "00:00:00"

        # 🚀 现场搓出两个并排的原生高敏 Metric 画布
        sub_c1, sub_c2 = strl.columns(2)
        
        # 利用原生 metric 的硬擦除机制，每秒直接物理干翻前台显示，达成完全不需要任何点击的自驱动秒跳！
        with sub_c1:
            strl.metric(label="🟢 北京时间 (SHANGHAI)", value=bj_time, delta=bj_date, delta_color="off")
        with sub_c2:
            strl.metric(label="🟠 纽约时间 (NEW YORK)", value=ny_time, delta=ny_date, delta_color="off")

    # 🚀 物理现场点火拉起，全自动高频空转
    render_m7_absolute_live_clocks()
# =====================================================================
with strl.sidebar:
    strl.title("⚙️ 纳斯达克100股票选择")
    strl.caption("架构层: 工业级单画布四轴强联动合龙内核")
    strl.markdown("---")
    
    selected_tickers = strl.multiselect("🔮 请选择要审计的纳指成份股:", options=NASDAQ_100_POOL, default=["GOOGL", "NVDA"])
    period_choice = strl.radio("📈 K线周期切换:", options=["日K", "周K", "月K"], index=0, horizontal=True)
    strl.markdown("---")
    
    if selected_tickers:
        strl.markdown("### 💵 核心资产实时报价")
        for ticker in selected_tickers:
            parquet_path = os.path.join(DATA_CACHE_DIR, f"{ticker.lower()}_10y.parquet")
            df_stock = None
            
            if os.path.exists(parquet_path):
                try: df_stock = pd.read_parquet(parquet_path)
                except: pass
            
            if df_stock is None or df_stock.empty or (datetime.now(pytz.utc) - df_stock.index[-1].to_pydatetime().astimezone(pytz.utc)).total_seconds() > 900:
                try:
                    ticker_obj = yf.Ticker(ticker)
                    full_df = ticker_obj.history(period="10y")
                    if not full_df.empty:
                        full_df.to_parquet(parquet_path)
                        df_stock = full_df
                except Exception as net_err:
                    print(f"动态同步个股 {ticker} 失败: {net_err}")

            if df_stock is not None and not df_stock.empty and "Close" in df_stock.columns:
                try:
                    clean_prices = df_stock["Close"].dropna().values.flatten()
                    if len(clean_prices) >= 2:
                        curr_p = float(clean_prices[-1])
                        prev_p = float(clean_prices[-2])
                        p_change = curr_p - prev_p
                        p_pct = (p_change / prev_p) * 100
                        
                        if p_change > 0:
                            p_delta_str = f"▲ ${p_change:+.2f} ({p_pct:+.2f}%)"
                        elif p_change < 0:
                            p_delta_str = f"▼ ${p_change:+.2f} ({p_pct:+.2f}%)"
                        else:
                            p_delta_str = f"— $0.00 (0.00%)"
                        
                        strl.metric(label=f"标的: {ticker}", value=f"${curr_p:.2f}", delta=p_delta_str)
                    else:
                        strl.metric(label=f"标的: {ticker}", value=f"${clean_prices[-1]:.2f}", delta="对比数据不足")
                except:
                    strl.error(f"❌ {ticker} 矩阵解算中断")
            else:
                strl.error(f"❌ {ticker} 报价链路断流")
        strl.markdown("---")

    status_net = strl.empty()
    if selected_tickers:
        status_net.info(f"🟢 已锁定 {len(selected_tickers)} 支标的")
        
    if strl.button("🗑️ 物理粉碎死锁缓存 (校准当日日期)", use_container_width=True):
        strl.session_state["audit_cache"] = ""
        for key in list(strl.session_state.keys()):
            if "decision_" in key: del strl.session_state[key]
        strl.success("内存缓存已释放！")
        strl.rerun()

# =====================================================================
# 🚀🔥【大布局重组】：自适应两排响应式大天幕墙
# =====================================================================
global_cached_macro = {}
try:
    macro_data = macro_engine.get_macro_indicators()
    global_cached_macro = macro_data 
except Exception as err:
    strl.error(f"宏观组件异动: {err}")
    macro_data = {}

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
    if df_idx is None or df_idx.empty or (datetime.now(pytz.utc) - df_idx.index[-1].to_pydatetime().astimezone(pytz.utc)).total_seconds() > 900:
        try:
            t_obj = yf.Ticker(idx_ticker)
            full_idx_df = t_obj.history(period="10y")
            if not full_idx_df.empty:
                full_idx_df.to_parquet(idx_parquet)
                df_idx = full_idx_df
        except: pass

    if df_idx is not None and not df_idx.empty:
        try:
            clean_series = df_idx["Close"].dropna().values.flatten()
            if len(clean_series) >= 2:
                current_close = float(clean_series[-1])
                prev_close = float(clean_series[-2])
                change_pct = ((current_close - prev_close) / prev_close) * 100
                if change_pct > 0: arrow, color_code = "▲", "#00FF00"
                elif change_pct < 0: arrow, color_code = "▼", "#FF4444"
                else: arrow, color_code = "—", "#58a6ff"
                index_snapshot[idx_key] = {"val": f"{current_close:,.2f}", "arrow": arrow, "color": color_code, "pct": f"{change_pct:+.2f}%"}
        except: pass

macro_cards_html = ""
idx_labels = {"GSPC": "S&P 500 (标普大盘)", "DJI": "DOW 30 (道指工业)", "IXIC": "NASDAQ (纳指综合)"}
for k, item in index_snapshot.items():
    macro_cards_html += f"""
    <div style="flex: 1; min-width: 140px; background-color: #1a2333; padding: 8px 12px; border-radius: 6px; border-top: 3px solid {item['color']}; box-shadow: 0 4px 6px rgba(0,0,0,0.4);">
        <p style="margin: 0 0 4px 0; color: #ffcc00; font-size: 11px; font-weight: bold; font-family: sans-serif; white-space: nowrap;">{idx_labels[k]}</p>
        <p style="margin: 0; color: {item['color']}; font-size: 14px; font-weight: bold; font-family: monospace; white-space: nowrap;">
            <span style="font-size:10px; margin-right:2px;">{item['arrow']}</span>{item['val']} <span style="font-size:9px; font-weight:normal;">({item['pct']})</span>
        </p>
    </div>
    """

if macro_data:
    for name, node in macro_data.items():
        card_color = "#58a6ff"
        card_arrow = "—"
        display_val = "N/A"
        if isinstance(node, dict):
            val = node.get("val", "N/A")
            prev = node.get("prev", "N/A")
            display_val = str(val)
            if prev == "STATIC":
                card_arrow = "📢"
                if "新增" in display_val or "+" in display_val or "涨" in display_val: card_color = "#00FF00"
                elif "降" in display_val or "-" in display_val: card_color = "#FF4444"
                else: card_color = "#f0883e"
            elif val != "N/A" and prev != "N/A":
                try:
                    num_curr = float(val.replace("%", "").strip())
                    num_prev = float(prev.replace("%", "").strip())
                    if num_curr > num_prev: card_color = "#00FF00"; card_arrow = "▲"
                    elif num_curr < num_prev: card_color = "#FF4444"; card_arrow = "▼"
                except: pass
        else: display_val = str(node)

        macro_cards_html += f"""
        <div style="flex: 1; min-width: 140px; background-color: #161b22; padding: 8px 12px; border-radius: 6px; border-top: 3px solid {card_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <p style="margin: 0 0 4px 0; color: #8b949e; font-size: 11px; font-weight: bold; font-family: sans-serif; white-space: nowrap;">{name}</p>
            <p style="margin: 0; color: {card_color}; font-size: 13px; font-weight: bold; font-family: monospace; white-space: normal; word-break: break-all; line-height: 1.2;">
                <span style="font-size: 10px; margin-right: 2px;">{card_arrow}</span>{display_val}
            </p>
        </div>
        """

# 采用 2026 新规两排自适应 Flexbox 容器网关横向通铺
strl.html(
    f"""
    <div class="macro-container">
        {macro_cards_html}
    </div>
    <style>
        body {{ margin: 0; background-color: transparent; font-family: sans-serif; }}
        .macro-container {{ display: flex; flex-wrap: wrap; width: 100%; gap: 8px; }}
        .macro-container > div {{ flex: 1 1 calc(20% - 8px); min-width: 140px; box-sizing: border-box; }}
        @media (max-width: 1200px) {{ .macro-container > div {{ flex: 1 1 calc(25% - 8px); }} }}
        @media (max-width: 900px) {{ .macro-container > div {{ flex: 1 1 calc(33.33% - 8px); }} }}
    </style>
    """
)

strl.markdown("---")

# =====================================================================
# 🚨 标签页核心并网
# =====================================================================
tab_tech, tab_market, tab_decision = strl.tabs(["📈 动态技术面多显大屏", "🔮 智能体基本面审计长卷", "🦅 M7 主权决策战略操作仓"])

with tab_tech:
    time_mode = strl.radio(
        "📊 核心量化看盘时基视口 (一键切换将由 Python 底层动态提纯 Y 轴高低点边界 · 100% 抽干黑洞留白)",
        options=["1m", "3m", "6m", "1y", "5y", "Max"],
        index=2,
        horizontal=True,
        key="m7_global_time_mode"
    )
    strl.markdown("---")

    with strl.expander("📊 【🌍 纳斯达克综合指数 (NASDAQ Composite)】 核心大周期走势图", expanded=True):
        fig_nasdaq = generate_m7_clean_charts("^IXIC", period_choice, time_range_mode=time_mode)
        if fig_nasdaq is not None:
            strl.plotly_chart(fig_nasdaq, width="stretch", key=f"t_nasdaq_base_{period_choice}_{time_mode}")
            
    strl.markdown("#### 🏢 标的成份股技术面板")
    if not selected_tickers:
        strl.info("💡 提示：请在左侧控制中心选择标的。")
    else:
        for ticker in selected_tickers:
            with strl.expander(f"展开/收起 【{ticker}】 技术面看板", expanded=True):
                fig = generate_m7_clean_charts(ticker, period_choice, time_range_mode=time_mode)
                if fig is not None:
                    strl.plotly_chart(fig, width="stretch", key=f"t_{ticker}_{period_choice}_{time_mode}")

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
                with open(local_json_path, "r", encoding="utf-8") as f:
                    strl.session_state["audit_cache"] = f"💡 [M7-FMP-DOCK] 已成功识别资产大坝库：\n\n{json.load(f).get('audit_report', '')[:1200]}..."
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

# =====================================================================
# 🦅 标签页 3：M7 主权决策战略操作仓 (彻底洗净原始字典杂质完全体版)
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
                raw_rep = decision_engine.generate_m7_weekly_decision(decision_target, period_choice, global_cached_macro, f"【M7时钟注入】\n当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}。\n" + final_content, news_engine.get_latest_news(query_type="stock", topic=decision_target, limit=5), news_engine.get_latest_news(query_type="geopolitics", limit=5))
                strl.session_state[f"decision_{decision_target}_{period_choice}"] = raw_rep
                
        dec_res = strl.session_state.get(f"decision_{decision_target}_{period_choice}", "")
        if dec_res:
            strl.markdown('<div style="background-color:#111625; padding:12px; border-radius:8px; border-left: 5px solid #00FF00; margin-bottom: 15px;"><h4 style="color:#00FF00; margin-top:0px; margin-bottom:0px; font-family: monospace;">🦅 M7 量化主权研报体系 · 决策流完美合龙</h4></div>', unsafe_allow_html=True)
            
            # 🌟 🛡️ 【硬核拓扑清洗网关】：强力剥离任何由于 LangChain 包裹或返回的原始字典/列表外壳
            clean_text = ""
            if isinstance(dec_res, list) and len(dec_res) > 0:
                node = dec_res[0]
                clean_text = node.text if hasattr(node, "text") else (node.get("text", str(node)) if isinstance(node, dict) else str(node))
            elif isinstance(dec_res, dict): 
                clean_text = dec_res.get("text", dec_res.get("content", str(dec_res)))
            elif isinstance(dec_res, str):
                # 容灾：如果 Gemini 返回的纯文本内部包裹了脏的 JSON 字符串转义
                if dec_res.strip().startswith("[") or dec_res.strip().startswith("{"):
                    try:
                        if "'text':" in dec_res:
                            s = dec_res.find("'text': '") + 9
                            e = dec_res.find("', 'type'")
                            if s != -1 and e != -1: clean_text = dec_res[s:e].replace("\\n", "\n")
                    except: pass
                if not clean_text: clean_text = dec_res
            else: 
                clean_text = str(dec_res)
                
            # 完璧输出洗净后的高保真 Markdown 文本
            strl.markdown(clean_text)