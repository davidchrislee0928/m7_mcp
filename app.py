# app.py (M7-ALPHA 主界面控制台终端 - 顶层宏观天幕墙·三大股指·跨空间时钟一体化完全体)
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
# 🚀🔥【布局提权改版一】：大标题区与时钟区分裂，时钟强行置于右上角
# =====================================================================
title_col, clock_col = strl.columns([6, 4])

with title_col:
    strl.markdown("# 📊 M7-ALPHA 美国宏观经济指标")

with clock_col:
    # 将铁血时钟独立在右上角拉起一个微型画布，秒级点跳，绝不挤占指标墙空间
    components.html(
        """
        <div style="display: flex; gap: 8px; justify-content: flex-end; font-family: monospace;">
            <div style="background-color:#161b22; padding: 6px 12px; border-radius: 4px; border-left: 3px solid #00FF00; min-width: 165px;">
                <p style="margin:0; color:#8b949e; font-size:10px;">北京时间 (SHANGHAI)</p>
                <p id="top-clock-bj" style="margin:0; color:#58a6ff; font-size:13px; font-weight:bold;">同步中...</p>
            </div>
            <div style="background-color:#161b22; padding: 6px 12px; border-radius: 4px; border-left: 3px solid #ff9900; min-width: 165px;">
                <p style="margin:0; color:#8b949e; font-size:10px;">纽约时间 (NEW YORK)</p>
                <p id="top-clock-ny" style="margin:0; color:#f0883e; font-size:13px; font-weight:bold;">同步中...</p>
            </div>
        </div>
        <script>
        function updateTopClocks() {
            const now = new Date();
            const optBJ = {timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit', hour: 'numeric', minute: '2-digit', second: '2-digit', hour12: false};
            const partsBJ = new Intl.DateTimeFormat('zh-CN', optBJ).formatToParts(now);
            document.getElementById('top-clock-bj').innerText = partsBJ.find(p => p.type === 'year').value + '-' + partsBJ.find(p => p.type === 'month').value + '-' + partsBJ.find(p => p.type === 'day').value + ' ' + partsBJ.find(p => p.type === 'hour').value + ':' + partsBJ.find(p => p.type === 'minute').value + ':' + partsBJ.find(p => p.type === 'second').value;

            const optNY = {timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit', hour: 'numeric', minute: '2-digit', second: '2-digit', hour12: false};
            const partsNY = new Intl.DateTimeFormat('zh-CN', optNY).formatToParts(now);
            document.getElementById('top-clock-ny').innerText = partsNY.find(p => p.type === 'year').value + '-' + partsNY.find(p => p.type === 'month').value + '-' + partsNY.find(p => p.type === 'day').value + ' ' + partsNY.find(p => p.type === 'hour').value + ':' + partsNY.find(p => p.type === 'minute').value + ':' + partsNY.find(p => p.type === 'second').value;
        }
        updateTopClocks();
        setInterval(updateTopClocks, 1000);
        </script>
        <style>body { margin: 0; background-color: transparent; overflow: hidden; }</style>
        """,
        height=45,
    )

# =====================================================================
# ⚙️ 控制中心侧边栏 - 自选股锁定与资产价格网关
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
            
            # 优先从物理大坝捞取历史序列
            if os.path.exists(parquet_path):
                try:
                    df_stock = pd.read_parquet(parquet_path)
                except: pass
            
            # 增量自愈网关：无缓存或缓存过期则重新拉取10年数据
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
                    # 深度清洗序列末端，排除当日未收盘导致最新行为 NaN 的情况
                    clean_prices = df_stock["Close"].dropna().values.flatten()
                    if len(clean_prices) >= 2:
                        curr_p = float(clean_prices[-1])
                        prev_p = float(clean_prices[-2])
                        p_change = curr_p - prev_p
                        p_pct = (p_change / prev_p) * 100
                        
                        # 铁血大数准则：走高亮绿，走低亮红
                        if p_change > 0:
                            p_delta_str = f"▲ ${p_change:+.2f} ({p_pct:+.2f}%)"
                        elif p_change < 0:
                            p_delta_str = f"▼ ${p_change:+.2f} ({p_pct:+.2f}%)"
                        else:
                            p_delta_str = f"— $0.00 (0.00%)"
                        
                        strl.metric(
                            label=f"标的: {ticker}", 
                            value=f"${curr_p:.2f}", 
                            delta=p_delta_str,
                            delta_color="normal" # 自动匹配 Streamlit 默认的自愈正绿负红，若要极端自定义可写独立 HTML
                        )
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
# 🚀🔥【大布局重组二】：纯净红绿物理大天幕 (100% 贯彻：高绿低红铁律，绝不遗漏非农/CPI/PPI)
# =====================================================================
# 1. 调用两日对比型宏观核心资产
global_cached_macro = {}
try:
    macro_data = macro_engine.get_macro_indicators()
    global_cached_macro = macro_data 
except Exception as err:
    strl.error(f"宏观组件异动: {err}")
    macro_data = {}

# 2. 彻底堵死美国三大股指休盘 NaN 空白漏洞（多日长卷深度清洗降维法）
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
        try:
            df_idx = pd.read_parquet(idx_parquet)
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
                
                if change_pct > 0:
                    arrow, color_code = "▲", "#00FF00"
                elif change_pct < 0:
                    arrow, color_code = "▼", "#FF4444"
                else:
                    arrow, color_code = "—", "#58a6ff"

                index_snapshot[idx_key] = {
                    "val": f"{current_close:,.2f}",
                    "arrow": arrow,
                    "color": color_code,
                    "pct": f"{change_pct:+.2f}%"
                }
        except: pass

# 3. 🛡️ 【大屏视觉合龙】：全矩阵动态融合高频走势与静态宏观，100% 严密还原
macro_cards_html = ""

# A. 首先并排轰入三大指数卡片
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

# B. 其次无损并网全部宏观要素（包含高频对比与非农/CPI/PPI等静态要素）
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
                # 针对非农、CPI、PPI等静态披露指标进行铁血高亮渲染
                card_arrow = "📢"
                if "新增" in display_val or "+" in display_val or "涨" in display_val:
                    card_color = "#00FF00"  # 只要是增长、增加等趋势，直观亮绿
                elif "降" in display_val or "-" in display_val:
                    card_color = "#FF4444"  # 只要是下降趋势，直观亮红
                else:
                    card_color = "#f0883e"  # 维持稳定或符合预期亮金
            elif val != "N/A" and prev != "N/A":
                # 针对高频动态要素（美元指数、原油、美债）执行物理涨跌大数对比
                try:
                    num_curr = float(val.replace("%", "").strip())
                    num_prev = float(prev.replace("%", "").strip())
                    
                    if num_curr > num_prev:
                        card_color = "#00FF00"
                        card_arrow = "▲"
                    elif num_curr < num_prev:
                        card_color = "#FF4444"
                        card_arrow = "▼"
                except:
                    pass
        else:
            display_val = str(node)

        macro_cards_html += f"""
        <div style="flex: 1; min-width: 140px; background-color: #161b22; padding: 8px 12px; border-radius: 6px; border-top: 3px solid {card_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <p style="margin: 0 0 4px 0; color: #8b949e; font-size: 11px; font-weight: bold; font-family: sans-serif; white-space: nowrap;">{name}</p>
            <p style="margin: 0; color: {card_color}; font-size: 13px; font-weight: bold; font-family: monospace; white-space: normal; word-break: break-all; line-height: 1.2;">
                <span style="font-size: 10px; margin-right: 2px;">{card_arrow}</span>{display_val}
            </p>
        </div>
        """

# 4. 一键打入全画幅横向弹性自适应大天幕
# 4. 一键打入全画幅横向自适应两排/多排响应式天幕墙
components.html(
    f"""
    <div class="macro-container">
        {macro_cards_html}
    </div>
    <style>
        body {{ 
            margin: 0; 
            background-color: transparent; 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        .macro-container {{
            display: flex; 
            flex-wrap: wrap;       /* 🚀 核心突破点：允许自动弹性换行 */
            justify-content: flex-start; 
            width: 100%; 
            gap: 8px;              /* 紧凑网格间距 */
        }}
        /* 🎨 动态响应式卡片网格拓扑 */
        .macro-container > div {{
            flex: 1 1 calc(20% - 8px); /* 🟢 默认在宽屏下尽量一行放 5 个左右，9个指标自然均匀分成完美的 2 排 */
            min-width: 150px;          /* 🛡️ 限制单卡片极限卡口，防止挤压变形 */
            box-sizing: border-box;
        }}
        
        /* 📱 针对窄屏、竖屏、分屏或小浏览器的媒体查询自适应自愈 */
        @media (max-width: 1200px) {{
            .macro-container > div {{
                flex: 1 1 calc(25% - 8px); /* 中等屏幕一行 4 个 */
            }}
        }}
        @media (max-width: 900px) {{
            .macro-container > div {{
                flex: 1 1 calc(33.33% - 8px); /* 小屏幕、竖屏下一行 3 个 */
            }}
        }}
        @media (max-width: 600px) {{
            .macro-container > div {{
                flex: 1 1 calc(50% - 8px); /* 极端窄屏下一行 2 个 */
            }}
        }}
    </style>
    """,
    height=150, # 🚀 物理提权高度：从 68px 扩容到 150px，给换行预留充裕的垂直伸缩空间，彻底防止内容被截断
)

strl.markdown("---")

# =====================================================================
# 🚨 三大标签页并网分流
# =====================================================================
tab_tech, tab_market, tab_decision = strl.tabs(["📈 动态技术面多显大屏", "🔮 智能体基本面审计长卷", "🦅 M7 主权决策战略操作仓"])

# 下方的标签页内容（tab_tech, tab_market, tab_decision）保持你原本完好无损的逻辑...
# [此处原封不动承接你原本的 tab_tech, tab_market, tab_decision 渲染逻辑代码，不再赘述]
# =====================================================================
# 📈 标签页 1：动态技术面多显大屏 (首发纳指大盘 K 线长卷 - 满血Python动态视口切盘版)
# =====================================================================
with tab_tech:
    # 🚀🔥【核心大并网点一】：在技术大屏最顶端，无缝挂载全大屏最高联动主权的时基切盘纽
    # 它将作为全画布 4 轴自适应的核心逻辑中枢
    time_mode = strl.radio(
        "📊 核心量化看盘时基视口 (一键切换将由 Python 底层动态提纯 Y 轴高低点边界 · 100% 抽干黑洞留白)",
        options=["1m", "3m", "6m", "1y", "5y", "Max"],
        index=2,  # 默认无损锁定在 6m 视口上
        horizontal=True,
        key="m7_global_time_mode"
    )
    strl.markdown("---")

    # 🌟 核心突破二：无条件将纳斯达克综合大盘基准拉到第一位展开冲锋，并注入 time_mode 参数
    with strl.expander("📊 【🌍 纳斯达克综合指数 (NASDAQ Composite)】 核心大周期走势图", expanded=True):
        # 强力传入选中的时基模式
        fig_nasdaq = generate_m7_clean_charts("^IXIC", period_choice, time_range_mode=time_mode)
        if fig_nasdaq is not None:
            strl.plotly_chart(fig_nasdaq, use_container_width=True, key=f"t_nasdaq_base_{period_choice}_{time_mode}")
            
    strl.markdown("#### 🏢 标的成份股技术面板")
    if not selected_tickers:
        strl.info("💡 提示：请在左侧控制中心选择标的。")
    else:
        for ticker in selected_tickers:
            with strl.expander(f"展开/收起 【{ticker}】 技术面看板", expanded=True):
                # 强力传入选中的时基模式，让所有的自选个股（GOOGL, NVDA）全部实现 4 轴动态自愈
                fig = generate_m7_clean_charts(ticker, period_choice, time_range_mode=time_mode)
                if fig is not None:
                    strl.plotly_chart(fig, use_container_width=True, key=f"t_{ticker}_{period_choice}_{time_mode}")
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
                    local_data = json.load(f)
                    strl.session_state["audit_cache"] = f"💡 [M7-FMP-DOCK] 已成功识别并打捞持久化物理资产大坝库：\n\n{local_data.get('audit_report', '')[:1200]}..."
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
            with strl.spinner(f"🦅 M7 首席战略家 Gemini 正在执行高维脱水提纯..."):
                final_content = strl.session_state.get("audit_cache", "")
                if not final_content and os.path.exists(local_json_file):
                    try:
                        with open(local_json_file, "r", encoding="utf-8") as f: final_content = json.load(f).get("audit_report", "")
                    except: pass
                raw_rep = decision_engine.generate_m7_weekly_decision(decision_target, period_choice, global_cached_macro, f"【M7时钟注入】\n当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}。\n" + final_content, news_engine.get_latest_news(query_type="stock", topic=decision_target, limit=5), news_engine.get_latest_news(query_type="geopolitics", limit=5))
                strl.session_state[f"decision_{decision_target}_{period_choice}"] = raw_rep
        dec_res = strl.session_state.get(f"decision_{decision_target}_{period_choice}", "")
        if dec_res: strl.markdown(dec_res)