# app.py (M7-ALPHA 主界面控制台终端 - 顶层宏观天幕墙·三大股指并网完全体版)
import streamlit as strl
import os
import sys
import json
from datetime import datetime
import pytz
import pandas as pd
import yfinance as yf
import streamlit.components.v1 as components

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
# ⚙️ 控制中心侧边栏 - 双时区终端时钟与 Parquet 价格自愈网关
# =====================================================================
with strl.sidebar:
    strl.title("⚙️ 控制中心")
    strl.caption("架构层: 工业级单画布四轴强联动合龙内核")
    strl.markdown("---")
    
    # 🌟 跨空间铁血动态主权时钟 (标准安全网关并网·全自动秒级点跳版)
    strl.markdown("### 🕒 跨空间铁血时钟")
    components.html(
        """
        <div style="background-color:#161b22; padding:10px; border-radius:6px; border-left:4px solid #00FF00; margin-bottom:10px; font-family:monospace;">
            <p style="margin:0 0 4px 0; color:#8b949e; font-size:11px;">北京时间 (Asia/Shanghai)</p>
            <p id="m7-clock-beijing" style="margin:0; color:#58a6ff; font-size:18px; font-weight:bold;">同步中...</p>
        </div>
        <div style="background-color:#161b22; padding:10px; border-radius:6px; border-left:4px solid #ff9900; margin-bottom:15px; font-family:monospace;">
            <p style="margin:0 0 4px 0; color:#8b949e; font-size:11px;">纽约时间 (EST/EDT 自动对齐)</p>
            <p id="m7-clock-newyork" style="margin:0; color:#f0883e; font-size:18px; font-weight:bold;">同步中...</p>
        </div>

        <script>
        function updateM7Clocks() {
            const now = new Date();
            const optionsBeijing = {timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit', hour: 'numeric', minute: '2-digit', second: '2-digit', hour12: false};
            const formatterBeijing = new Intl.DateTimeFormat('zh-CN', optionsBeijing);
            const partsBeijing = formatterBeijing.formatToParts(now);
            const bjStr = `${partsBeijing.find(p => p.type === 'year').value}-${partsBeijing.find(p => p.type === 'month').value}-${partsBeijing.find(p => p.type === 'day').value} ${partsBeijing.find(p => p.type === 'hour').value}:${partsBeijing.find(p => p.type === 'minute').value}:${partsBeijing.find(p => p.type === 'second').value}`;
            document.getElementById('m7-clock-beijing').innerText = bjStr;

            const optionsNewYork = {timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit', hour: 'numeric', minute: '2-digit', second: '2-digit', hour12: false};
            const formatterNewYork = new Intl.DateTimeFormat('zh-CN', optionsNewYork);
            const partsNewYork = formatterNewYork.formatToParts(now);
            const nyStr = `${partsNewYork.find(p => p.type === 'year').value}-${partsNewYork.find(p => p.type === 'month').value}-${partsNewYork.find(p => p.type === 'day').value} ${partsNewYork.find(p => p.type === 'hour').value}:${partsNewYork.find(p => p.type === 'minute').value}:${partsNewYork.find(p => p.type === 'second').value}`;
            document.getElementById('m7-clock-newyork').innerText = nyStr;
        }
        updateM7Clocks();
        setInterval(updateM7Clocks, 1000);
        </script>
        <style>body { margin: 0; background-color: transparent; overflow: hidden; }</style>
        """,
        height=145,
    )
    strl.markdown("---")

    selected_tickers = strl.multiselect("🔮 请选择要审计的纳指成份股:", options=NASDAQ_100_POOL, default=["GOOGL", "NVDA"])
    period_choice = strl.radio("📈 K线周期切换:", options=["日K", "周K", "月K"], index=0, horizontal=True)
    strl.markdown("---")
    
    if selected_tickers:
        strl.markdown("### 💵 核心资产实时报价")
        for ticker in selected_tickers:
            parquet_path = os.path.join(DATA_CACHE_DIR, f"{ticker.lower()}_10y.parquet")
            current_price = None
            price_source = "未知"
            
            if os.path.exists(parquet_path):
                try:
                    df_local = pd.read_parquet(parquet_path)
                    if not df_local.empty and "Close" in df_local.columns:
                        if (datetime.now(pytz.utc) - df_local.index[-1].to_pydatetime().astimezone(pytz.utc)).total_seconds() < 900:
                            current_price = float(df_local.iloc[-1]["Close"])
                            price_source = "物理大坝 (Parquet)"
                except Exception as p_err:
                    print(f"读取本地 Parquet 缓存异常: {p_err}")
            
            if current_price is None:
                try:
                    ticker_obj = yf.Ticker(ticker)
                    todays_data = ticker_obj.history(period="1d")
                    if not todays_data.empty:
                        current_price = float(todays_data["Close"].iloc[-1])
                        price_source = "实时并网 (yfinance)"
                        full_df = ticker_obj.history(period="10y")
                        if not full_df.empty:
                            full_df.to_parquet(parquet_path)
                except Exception as net_err:
                    print(f"动态抓取最新价失败: {net_err}")
                    if os.path.exists(parquet_path):
                        try:
                            df_local = pd.read_parquet(parquet_path)
                            current_price = float(df_local.iloc[-1]["Close"])
                            price_source = "物理大坝兜底"
                        except: pass

            if current_price is not None:
                strl.metric(label=f"标的: {ticker} ({price_source})", value=f"${current_price:.2f}", delta=f"美东盘面联动中")
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
# 🚀🔥【工业级全新裂变】：宏观天空看盘墙 (物理提权到三大标签页上方)
# =====================================================================
strl.markdown("## 📊 实时宏观经济与美国三大股指核心墙")

# 1. 物理调用宏观与指数引擎打捞数据
global_cached_macro = {}
try:
    # 基础宏观数据打捞
    macro_data = macro_engine.get_macro_indicators()
    global_cached_macro = macro_data 
except Exception as err:
    strl.error(f"宏观组件异动: {err}")
    macro_data = {}

# 2. 【2026硬核追加】：美国三大股指高并发实时提取与缓存并网机制
index_snapshot = {"标普500 (S&P 500)": "N/A", "道琼斯 (Dow 30)": "N/A", "纳斯达克 (Nasdaq)": "N/A"}
index_map = {"标普500 (S&P 500)": "^GSPC", "道琼斯 (Dow 30)": "^DJI", "纳斯达克 (Nasdaq)": "^IXIC"}

for idx_name, idx_ticker in index_map.items():
    idx_parquet = os.path.join(DATA_CACHE_DIR, f"{idx_ticker.replace('^', '').lower()}_10y.parquet")
    cached_val = None
    
    # 优先从持久化 Parquet 吞噬 15 分钟内新资产
    if os.path.exists(idx_parquet):
        try:
            df_idx = pd.read_parquet(idx_parquet)
            if not df_idx.empty and (datetime.now(pytz.utc) - df_idx.index[-1].to_pydatetime().astimezone(pytz.utc)).total_seconds() < 900:
                cached_val = float(df_idx.iloc[-1]["Close"])
        except: pass
        
    if cached_val is None:
        try:
            t_obj = yf.Ticker(idx_ticker)
            h_data = t_obj.history(period="1d")
            if not h_data.empty:
                cached_val = float(h_data["Close"].iloc[-1])
                # 异步同步10年数据沉入大坝
                full_idx_df = t_obj.history(period="10y")
                if not full_idx_df.empty: full_idx_df.to_parquet(idx_parquet)
        except Exception as e:
            if os.path.exists(idx_parquet):
                try: cached_val = float(pd.read_parquet(idx_parquet).iloc[-1]["Close"])
                except: pass
                
    if cached_val is not None:
        index_snapshot[idx_name] = f"{cached_val:,.2f}"

# 3. 完美的纯前端全宽无损 Flex 卡片流渲染大天幕（彻底融合三大股指）
if macro_data:
    macro_html_tiles = ""
    
    # 首先通铺美国三大大盘股指（高亮金黄色左边框，展现统治地位）
    for name, val in index_snapshot.items():
        macro_html_tiles += f"""
        <div style="flex: 1; min-width: 220px; background-color: #1a2333; padding: 12px 16px; border-radius: 6px; border-top: 3px solid #ffcc00; margin: 6px; box-shadow: 0 4px 6px rgba(0,0,0,0.4);">
            <p style="margin: 0 0 6px 0; color: #ffcc00; font-size: 11px; font-weight: bold; font-family: sans-serif;">🇺🇸 {name}</p>
            <p style="margin: 0; color: #ffffff; font-size: 20px; font-weight: bold; font-family: monospace;">{val}</p>
        </div>
        """
        
    # 其次无缝追加原有的宏观基础指标矩阵
    for name, val in macro_data.items():
        if "新增" in str(val) or "+" in str(val): tile_border_color = "#00FF00"
        elif "符合" in str(val) or "控" in str(val): tile_border_color = "#f0883e"
        else: tile_border_color = "#58a6ff"
        
        macro_html_tiles += f"""
        <div style="flex: 1; min-width: 180px; background-color: #161b22; padding: 12px 16px; border-radius: 6px; border-top: 3px solid {tile_border_color}; margin: 6px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <p style="margin: 0 0 6px 0; color: #8b949e; font-size: 11px; font-weight: bold; font-family: sans-serif;">{name}</p>
            <p style="margin: 0; color: #ffffff; font-size: 17px; font-weight: bold; font-family: monospace; white-space: normal; word-break: break-all;">{val}</p>
        </div>
        """
    
    # 轰出天幕全画布
    strl.markdown(f'<div style="display: flex; flex-wrap: wrap; justify-content: space-between; width: 100%; margin-bottom: 15px;">{macro_html_tiles}</div>', unsafe_allow_html=True)
else:
    strl.warning("⚠️ 动态宏观资产天幕正在等待网关物理唤醒...")

strl.markdown("---")

# =====================================================================
# 🚨 降维并网：三大核心标签页点火发射
# =====================================================================
tab_tech, tab_market, tab_decision = strl.tabs(["📈 动态技术面多显大屏", "🔮 智能体基本面审计长卷", "🦅 M7 主权决策战略操作仓"])

global_cached_stock_news = []
global_cached_geo_news = []

# =====================================================================
# 📈 标签页 1：动态技术面多显大屏 (首发纳指大盘 K 线图)
# =====================================================================
with tab_tech:
    # 🌟 核心突破二：在自选股前，无条件强力铺开纳斯达克综合大盘走势图
    with strl.expander("📊 【🌍 纳斯达克大盘基准面指数】 核心大周期K线图", expanded=True):
        # 调用大盘代码 ^IXIC 绘制标准图表
        fig_nasdaq = generate_m7_clean_charts("^IXIC", period_choice)
        if fig_nasdaq is not None:
            strl.plotly_chart(fig_nasdaq, use_container_width=True, key=f"t_nasdaq_base_{period_choice}")
            
    strl.markdown("#### 🏢 标的成份股技术面板")
    if not selected_tickers:
        strl.info("💡 提示：请在左侧控制中心选择标的。")
    else:
        for ticker in selected_tickers:
            with strl.expander(f"展开/收起 【{ticker}】 技术面看板", expanded=True):
                fig = generate_m7_clean_charts(ticker, period_choice)
                if fig is not None:
                    strl.plotly_chart(fig, use_container_width=True, key=f"t_{ticker}_{period_choice}")


# =====================================================================
# 🔮 标签页 2：智能体基本面审计长卷
# =====================================================================
with tab_market:
    if not selected_tickers:
        strl.info("💡 提示：请在左侧控制中心锁定股票。")
    else:
        strl.markdown("### 📝 多智能体基本面联审研报")
        audit_target = strl.selectbox("🎯 请选择本次点火 AI 联审的核心目标:", options=selected_tickers)
        
        report_container = strl.empty()
        local_json_path = os.path.join(DATA_CACHE_DIR, f"fmp_cache_{audit_target}.json")
        has_local_json = os.path.exists(local_json_path)
        
        if "audit_cache" not in strl.session_state:
            strl.session_state["audit_cache"] = ""

        if not strl.session_state["audit_cache"] and has_local_json:
            try:
                with open(local_json_path, "r", encoding="utf-8") as f:
                    local_data = json.load(f)
                    raw_text = local_data.get("audit_report", json.dumps(local_data, ensure_ascii=False))
                    strl.session_state["audit_cache"] = f"💡 [M7-FMP-DOCK] 已成功识别并打捞持久化物理资产大坝库：\n\n{raw_text[:1200]}..."
            except Exception as e:
                print(f"读取持久化 FMP JSON 异常: {e}")

        if strl.session_state["audit_cache"]:
            report_container.markdown(strl.session_state["audit_cache"])
        else:
            report_container.markdown(f"> 锁定战略主攻目标: **{audit_target}**。持久化物理库暂无记录，请点击点火。")

        if strl.button("🚀 启动 AI 多维基本面联审 (点火状态机)", use_container_width=True):
            status_net.warning(f"🔄 正在唤醒本地子节点，审理 [{audit_target}] 中...")
            report_container.info(f"⏳ **LangGraph 状态机已对 [{audit_target}] 点火**...")
            try:
                audit_result = run_m7_audit(audit_target, period_choice)
                if audit_result:
                    status_net.success(f"🎉 {audit_target} 财务审计圆满合龙！")
                    report_container.markdown(audit_result)
                    strl.session_state["audit_cache"] = audit_result 
                    
                    try:
                        structured_output = {"ticker": audit_target, "period": period_choice, "audit_report": audit_result}
                        with open(local_json_path, "w", encoding="utf-8") as wf:
                            json.dump(structured_output, wf, ensure_ascii=False, indent=2)
                    except Exception as w_err: print(f"回填写入持久化资产失败: {w_err}")
                else:
                    status_net.error("❌ 审计断流")
            except Exception as ui_err: status_net.error(f"❌ 运行期突发崩溃: {ui_err}")

        strl.markdown("---")
        strl.markdown(f"### 📰 M7 高敏舆情雷达监控舱")
        news_col1, news_col2 = strl.columns(2)
        with news_col1:
            strl.subheader(f"🏢 {audit_target} 最新关联热点摘要")
            stock_news_list = news_engine.get_latest_news(query_type="stock", topic=audit_target, limit=5)
            global_cached_stock_news = stock_news_list 
            for item in stock_news_list:
                with strl.expander(f"📌 {item['title']}", expanded=False): strl.markdown(item['summary'])
        with news_col2:
            strl.subheader("🌍 全球地缘政治前沿动向")
            geo_news_list = news_engine.get_latest_news(query_type="geopolitics", limit=5)
            global_cached_geo_news = geo_news_list 
            for item in geo_news_list:
                with strl.expander(f"⚠️ {item['title']}", expanded=False): strl.markdown(item['summary'])

# =====================================================================
# 🦅 标签页 3：M7 主权决策战略操作仓
# =====================================================================
with tab_decision:
    strl.markdown(f"### 🦅 Gemini 3.5 多维因子自适应跨空间终极决策建议")
    decision_target = audit_target if 'audit_target' in locals() else (selected_tickers[0] if selected_tickers else None)
    
    if not decision_target:
        strl.info("⏳ 正在等待数据链合龙... 请选择标的。")
    else:
        local_json_file = os.path.join(DATA_CACHE_DIR, f"fmp_cache_{decision_target}.json")
        is_fundamental_ready = bool(strl.session_state.get("audit_cache")) or os.path.exists(local_json_file)

        d_col1, d_col2, d_col3, d_col4 = strl.columns(4)
        d_col1.markdown(f"🎯 核心标的: **{decision_target}**")
        d_col2.markdown(f"📈 宏观因子墙: <span style='color:#00FF00;'>🟢 已就绪</span>", unsafe_allow_html=True)
        
        if is_fundamental_ready:
            d_col3.markdown(f"📝 FMP基本面: <span style='color:#00FF00; font-weight:bold;'>🟢 已读取持久化物理库</span>", unsafe_allow_html=True)
        else:
            d_col3.markdown(f"📝 FMP基本面: <span style='color:#FF9900;'>⚠️ 未发现本地物理库</span>", unsafe_allow_html=True)
            
        d_col4.markdown(f"📰 MCP舆情流: <span style='color:#00FF00;'>🟢 已双向并网</span>", unsafe_allow_html=True)
        
        strl.markdown("---")
        
        decision_cache_key = f"decision_{decision_target}_{period_choice}"
        if decision_cache_key not in strl.session_state: strl.session_state[decision_cache_key] = ""
            
        if strl.button(f"🔥 点火决策状态机 -> 下达 [{decision_target}] 操盘战略", use_container_width=True):
            with strl.spinner(f"🦅 M7 首席战略家 Gemini 正在执行高维脱水提纯..."):
                final_audit_content = strl.session_state.get("audit_cache", "")
                
                if not final_audit_content or "💡" not in final_audit_content:
                    if os.path.exists(local_json_file):
                        try:
                            with open(local_json_file, "r", encoding="utf-8") as f:
                                local_json_data = json.load(f)
                                final_audit_content = local_json_data.get("audit_report", json.dumps(local_json_data, ensure_ascii=False))
                                strl.session_state["audit_cache"] = f"💡 [M7-EMERGENCY-DOCK] 成功吞噬持久化大坝"
                        except Exception as file_err: final_audit_content = str(file_err)

                current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S (UTC+8)")
                time_anchor_instruction = f"【M7系统高优先级时钟注入】\n当前时间: {current_time_str}。\n==================================================\n\n"
                final_audit_content_with_time = time_anchor_instruction + final_audit_content

                macro_input = global_cached_macro if global_cached_macro else macro_engine.get_macro_indicators()
                stock_news_input = global_cached_stock_news if global_cached_stock_news else news_engine.get_latest_news(query_type="stock", topic=decision_target, limit=5)
                geo_news_input = global_cached_geo_news if global_cached_geo_news else news_engine.get_latest_news(query_type="geopolitics", limit=5)
                
                raw_decision_report = decision_engine.generate_m7_weekly_decision(
                    ticker=decision_target, period_choice=period_choice, macro_data=macro_input,
                    audit_text=final_audit_content_with_time, stock_news=stock_news_input, geo_news=geo_news_input
                )
                strl.session_state[decision_cache_key] = raw_decision_report
                
        if strl.session_state[decision_cache_key]:
            strl.markdown('<div style="background-color:#111625; padding:12px; border-radius:8px; border-left: 5px solid #00FF00; margin-bottom: 15px;"><h4 style="color:#00FF00; margin-top:0px; margin-bottom:0px; font-family: monospace;">🦅 M7 量化主权研报体系 · 决策流完美合龙</h4></div>', unsafe_allow_html=True)
            raw_report = strl.session_state[decision_cache_key]
            clean_text = ""
            
            if isinstance(raw_report, list) and len(raw_report) > 0:
                node = raw_report[0]
                clean_text = node.text if hasattr(node, "text") else (node.get("text", str(node)) if isinstance(node, dict) else str(node))
            elif isinstance(raw_report, dict): clean_text = raw_report.get("text", raw_report.get("content", str(raw_report)))
            elif isinstance(raw_report, str):
                if raw_report.strip().startswith("[") or raw_report.strip().startswith("{"):
                    try:
                        if "'text':" in raw_report:
                            s = raw_report.find("'text': '") + 9
                            e = raw_report.find("', 'type'")
                            if s != -1 and e != -1: clean_text = raw_report[s:e].replace("\\n", "\n")
                    except: pass
                if not clean_text: clean_text = raw_report
            else: clean_text = str(raw_report)
            strl.markdown(clean_text)