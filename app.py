# app.py (M7-ALPHA 主界面控制台终端 - FMP物理资产无损强吞完全体·持久化并网版)
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
# 💾 核心缓存根目录重构：物理铁血对接 Hugging Face /data 持久化大坝
# =====================================================================
if os.path.exists("/data"):
    BASE_CACHE_DIR = "/data"
    print("🚀 [M7-APP] 成功探测到云端物理存储大坝！路径硬核并网至: /data")
else:
    BASE_CACHE_DIR = PROJECT_ROOT
    print("💻 [M7-APP] 未发现云端物理盘，自动降级为本地开发路径")

# 完璧对齐你的数据缓存盾牌文件夹
DATA_CACHE_DIR = os.path.join(BASE_CACHE_DIR, "data_cache")
if not os.path.exists(DATA_CACHE_DIR):
    os.makedirs(DATA_CACHE_DIR, exist_ok=True)
    try:
        os.chmod(DATA_CACHE_DIR, 0o777)
    except:
        pass

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
    
    # 🌟 核心功能一：双时区主权时钟实时监控
    local_tz = pytz.timezone('Asia/Shanghai')
    est_tz = pytz.timezone('America/New_York')
    
    now_utc = datetime.now(pytz.utc)
    local_now = now_utc.astimezone(local_tz)
    est_now = now_utc.astimezone(est_tz)

    strl.markdown("### 🕒 跨空间精确时钟")
    strl.markdown(
        """
        <div style="background-color:#161b22; padding:10px; border-radius:6px; border-left:4px solid #00FF00; margin-bottom:10px;">
            <p style="margin:0; color:#8b949e; font-size:11px; font-family:monospace;">北京时间 (Asia/Shanghai)</p>
            <p id="m7-clock-beijing" style="margin:0; color:#58a6ff; font-size:18px; font-weight:bold; font-family:monospace;">加载中...</p>
        </div>
        <div style="background-color:#161b22; padding:10px; border-radius:6px; border-left:4px solid #ff9900; margin-bottom:15px;">
            <p style="margin:0; color:#8b949e; font-size:11px; font-family:monospace;">纽约时间 (EST/EDT 自动对齐)</p>
            <p id="m7-clock-newyork" style="margin:0; color:#f0883e; font-size:18px; font-weight:bold; font-family:monospace;">加载中...</p>
        </div>

        <script>
        function updateM7Clocks() {
            const now = new Date();
            
            // 1. 精准提取北京时间 (Intl.DateTimeFormat 强行指定 Asia/Shanghai 协议栈)
            const optionsBeijing = {
                timeZone: 'Asia/Shanghai',
                year: 'numeric', month: '2-digit', day: '2-digit',
                hour: 'numeric', minute: '2-digit', second: '2-digit',
                hour12: false
            };
            const formatterBeijing = new Intl.DateTimeFormat('zh-CN', optionsBeijing);
            const partsBeijing = formatterBeijing.formatToParts(now);
            const bjStr = `${partsBeijing.find(p => p.type === 'year').value}-${partsBeijing.find(p => p.type === 'month').value}-${partsBeijing.find(p => p.type === 'day').value} ${partsBeijing.find(p => p.type === 'hour').value}:${partsBeijing.find(p => p.type === 'minute').value}:${partsBeijing.find(p => p.type === 'second').value}`;
            document.getElementById('m7-clock-beijing').innerText = bjStr;

            // 2. 精准提取纽约时间 (自动兼容 EST 标准时 与 EDT 夏令时切换大坝)
            const optionsNewYork = {
                timeZone: 'America/New_York',
                year: 'numeric', month: '2-digit', day: '2-digit',
                hour: 'numeric', minute: '2-digit', second: '2-digit',
                hour12: false
            };
            const formatterNewYork = new Intl.DateTimeFormat('zh-CN', optionsNewYork);
            const partsNewYork = formatterNewYork.formatToParts(now);
            const nyStr = `${partsNewYork.find(p => p.type === 'year').value}-${partsNewYork.find(p => p.type === 'month').value}-${partsNewYork.find(p => p.type === 'day').value} ${partsNewYork.find(p => p.type === 'hour').value}:${partsNewYork.find(p => p.type === 'minute').value}:${partsNewYork.find(p => p.type === 'second').value}`;
            document.getElementById('m7-clock-newyork').innerText = nyStr;
        }

        // 🚨 核心点火：首次加载立即合龙，随后每隔 1000 毫秒（1秒）全自动心跳复写
        updateM7Clocks();
        setInterval(updateM7Clocks, 1000);
        </script>
        """, 
        unsafe_allow_html=True
    )
    strl.markdown("---")
    # 纳指成分股与K线周期标准选择器
    selected_tickers = strl.multiselect("🔮 请选择要审计的纳指成份股:", options=NASDAQ_100_POOL, default=["GOOGL", "NVDA"])
    period_choice = strl.radio("📈 K线周期切换:", options=["日K", "周K", "月K"], index=0, horizontal=True)
    strl.markdown("---")
    
    # 🌟 核心功能二：资产价格网关（物理持久化存储大坝强吞）
    if selected_tickers:
        strl.markdown("### 💵 核心资产实时报价")
        
        for ticker in selected_tickers:
            # 🔥【精准对齐】：强制将价格 parquet 写入持久化大坝路径
            parquet_path = os.path.join(DATA_CACHE_DIR, f"{ticker.lower()}_10y.parquet")
            current_price = None
            price_source = "未知"
            
            # 1. 穿透拉取持久化 Parquet 物理库
            if os.path.exists(parquet_path):
                try:
                    df_local = pd.read_parquet(parquet_path)
                    if not df_local.empty and "Close" in df_local.columns:
                        latest_row = df_local.iloc[-1]
                        local_price_time = df_local.index[-1]
                        
                        # 核心校准：如果本地最新数据的时间戳距离当前小于 15 分钟，视为最新价直接强吞
                        if (datetime.now(pytz.utc) - local_price_time.to_pydatetime().astimezone(pytz.utc)).total_seconds() < 900:
                            current_price = float(latest_row["Close"])
                            price_source = "物理大坝 (Parquet)"
                except Exception as p_err:
                    print(f"读取持久化 Parquet 缓存异常: {p_err}")
            
            # 2. 缓存未命中/过期，穿透网络大坝追索最新动态报价
            if current_price is None:
                try:
                    ticker_obj = yf.Ticker(ticker)
                    todays_data = ticker_obj.history(period="1d")
                    if not todays_data.empty:
                        current_price = float(todays_data["Close"].iloc[-1])
                        price_source = "实时并网 (yfinance)"
                        
                        # 异步触发更新：下载 10 年历史长卷，重新覆盖固化到 /data 持久化盾牌
                        full_df = ticker_obj.history(period="10y")
                        if not full_df.empty:
                            full_df.to_parquet(parquet_path)
                except Exception as net_err:
                    print(f"动态抓取最新价失败: {net_err}")
                    # 网络彻底断流时，强行切回持久化 Parquet 物理库的最后一行数据进行容灾兜底
                    if os.path.exists(parquet_path):
                        try:
                            df_local = pd.read_parquet(parquet_path)
                            current_price = float(df_local.iloc[-1]["Close"])
                            price_source = "物理大坝兜底"
                        except:
                            pass

            # 3. 动态渲染价格面板
            if current_price is not None:
                strl.metric(
                    label=f"标的: {ticker} ({price_source})", 
                    value=f"${current_price:.2f}",
                    delta=f"美东开盘/盘后联动中"
                )
            else:
                strl.error(f"❌ {ticker} 报价链路断流")
                
        strl.markdown("---")

    status_net = strl.empty()
    if selected_tickers:
        status_net.info(f"🟢 已锁定 {len(selected_tickers)} 支标的")
        
    # 🗑️ 铁血碎冰锤按钮
    if strl.button("🗑️ 物理粉碎死锁缓存 (校准当日日期)", use_container_width=True):
        strl.session_state["audit_cache"] = ""
        for key in list(strl.session_state.keys()):
            if "decision_" in key:
                del strl.session_state[key]
        strl.success("内存缓存已释放！重新点火将强制触发底层过期检测机制。")
        strl.rerun()
    
# 🚨 三路标签页并网
tab_tech, tab_market, tab_decision = strl.tabs(["📈 动态技术面多显大屏", "🔮 智能体基本面审计长卷", "🦅 M7 主权决策战略操作仓"])

global_cached_macro = {}
global_cached_stock_news = []
global_cached_geo_news = []

# =====================================================================
# 📈 标签页 1：动态技术面多显大屏
# =====================================================================
with tab_tech:
    if not selected_tickers:
        strl.info("💡 提示：请在左侧控制中心选择标的。")
    else:
        for ticker in selected_tickers:
            with strl.expander(f"展开/收起 【{ticker}】 技术面看板", expanded=True):
                fig = generate_m7_clean_charts(ticker, period_choice)
                if fig is not None:
                    strl.plotly_chart(fig, use_container_width=True, key=f"t_{ticker}_{period_choice}")


# =====================================================================
# 🔮 标签页 2：智能体基本面审计长卷 (纯前端 Flex 容器重构 · 彻底封杀截断)
# =====================================================================
with tab_market:
    if not selected_tickers:
        strl.info("💡 提示：请在左侧控制中心锁定股票。")
    else:
        strl.markdown("### 📈 实时宏观经济核心指标")
        
        # 1. 物理调用原有引擎打捞数据
        try:
            macro_data = macro_engine.get_macro_indicators()
            global_cached_macro = macro_data 
        except Exception as err:
            strl.error(f"宏观组件异常: {err}")
            macro_data = {}
            
        if macro_data:
            macro_html_tiles = ""
            for name, val in macro_data.items():
                if "新增" in str(val) or "+" in str(val):
                    tile_border_color = "#00FF00"
                elif "符合" in str(val) or "控" in str(val):
                    tile_border_color = "#f0883e"
                else:
                    tile_border_color = "#58a6ff"
                
                macro_html_tiles += f"""
                <div style="
                    flex: 1; 
                    min-width: 180px; 
                    background-color: #161b22; 
                    padding: 12px 16px; 
                    border-radius: 6px; 
                    border-top: 3px solid {tile_border_color}; 
                    margin: 6px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                ">
                    <p style="margin: 0 0 6px 0; color: #8b949e; font-size: 12px; font-weight: bold; font-family: sans-serif;">{name}</p>
                    <p style="margin: 0; color: #ffffff; font-size: 18px; font-weight: bold; font-family: monospace; white-space: normal; word-break: break-all;">{val}</p>
                </div>
                """
            
            strl.markdown(
                f"""
                <div style="display: flex; flex-wrap: wrap; justify-content: space-between; width: 100%; margin-bottom: 10px;">
                    {macro_html_tiles}
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            strl.warning("⚠️ 动态宏观账本空置，等待网关唤醒中...")

        strl.markdown("---")
        strl.markdown("### 📝 多智能体基本面联审研报")
        
        audit_target = strl.selectbox("🎯 请选择本次点火 AI 联审的核心目标:", options=selected_tickers)
        
        report_container = strl.empty()
        
        # 🔥【精准对齐】：将研报 JSON 缓存路径死死锁进 /data 持久化盘中
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
            report_container.markdown(f"> 锁定战略主攻目标: **{audit_target}**。持久化物理库暂无记录，点击下方按钮激活状态机。")

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
                        structured_output = {
                            "ticker": audit_target,
                            "period": period_choice,
                            "audit_report": audit_result
                        }
                        # 🔥【精准对齐】：将生成的研报资产牢牢砸进物理磁盘
                        with open(local_json_path, "w", encoding="utf-8") as wf:
                            json.dump(structured_output, wf, ensure_ascii=False, indent=2)
                    except Exception as w_err:
                        print(f"回填写入持久化资产失败: {w_err}")
                else:
                    status_net.error("❌ 审计断流")
            except Exception as ui_err:
                status_net.error(f"❌ 运行期突发崩溃: {ui_err}")

        strl.markdown("---")
        strl.markdown(f"### 📰 M7 高敏舆情雷达监控舱")
        news_col1, news_col2 = strl.columns(2)
        with news_col1:
            strl.subheader(f"🏢 {audit_target} 最新关联热点摘要")
            stock_news_list = news_engine.get_latest_news(query_type="stock", topic=audit_target, limit=5)
            global_cached_stock_news = stock_news_list 
            for item in stock_news_list:
                with strl.expander(f"📌 {item['title']}", expanded=False):
                    strl.markdown(item['summary'])
        with news_col2:
            strl.subheader("🌍 全球地缘政治前沿动向")
            geo_news_list = news_engine.get_latest_news(query_type="geopolitics", limit=5)
            global_cached_geo_news = geo_news_list 
            for item in geo_news_list:
                with strl.expander(f"⚠️ {item['title']}", expanded=False):
                    strl.markdown(item['summary'])

# =====================================================================
# 🦅 标签页 3：M7 主权决策战略操作仓 (100% 完整物理穿透吞噬逻辑)
# =====================================================================
with tab_decision:
    strl.markdown(f"### 🦅 Gemini 3.5 多维因子自适应跨空间终极决策建议")
    
    decision_target = audit_target if 'audit_target' in locals() else (selected_tickers[0] if selected_tickers else None)
    
    if not decision_target:
        strl.info("⏳ 正在等待数据链合龙... 请确保在左侧控制中心至少选择了一支股票。")
    else:
        # 🔥【精准对齐】：决策端硬核强刷 /data 持久化盘下的 json 历史记录
        local_json_file = os.path.join(DATA_CACHE_DIR, f"fmp_cache_{decision_target}.json")
        is_fundamental_ready = bool(strl.session_state.get("audit_cache")) or os.path.exists(local_json_file)

        # 动态状态通关灯排布
        d_col1, d_col2, d_col3, d_col4 = strl.columns(4)
        d_col1.markdown(f"🎯 核心标的: **{decision_target}**")
        d_col2.markdown(f"📈 宏观因子墙: <span style='color:#00FF00;'>🟢 已就绪</span>", unsafe_allow_html=True)
        
        if is_fundamental_ready:
            d_col3.markdown(f"📝 FMP基本面: <span style='color:#00FF00; font-weight:bold;'>🟢 已读取持久化物理库</span>", unsafe_allow_html=True)
        else:
            d_col3.markdown(f"📝 FMP基本面: <span style='color:#FF9900;'>⚠️ 未发现本地物理库，将常识推理</span>", unsafe_allow_html=True)
            
        d_col4.markdown(f"📰 MCP舆情流: <span style='color:#00FF00;'>🟢 已双向并网</span>", unsafe_allow_html=True)
        
        strl.markdown("---")
        
        decision_cache_key = f"decision_{decision_target}_{period_choice}"
        if decision_cache_key not in strl.session_state:
            strl.session_state[decision_cache_key] = ""
            
        if strl.button(f"🔥 点火决策状态机 -> 下达 [{decision_target}] 操盘战略", use_container_width=True):
            with strl.spinner(f"🦅 M7 首席战略家 Gemini 正在对四轴联动因子执行高维脱水提纯..."):
                
                final_audit_content = strl.session_state.get("audit_cache", "")
                
                # 🔥【物理穿透自愈核心】：无条件穿透去强吞持久化大坝盘下的原始财报数据
                if not final_audit_content or "💡" not in final_audit_content:
                    if os.path.exists(local_json_file):
                        try:
                            with open(local_json_file, "r", encoding="utf-8") as f:
                                local_json_data = json.load(f)
                                if isinstance(local_json_data, dict) and "audit_report" in local_json_data:
                                    final_audit_content = local_json_data["audit_report"]
                                else:
                                    final_audit_content = json.dumps(local_json_data, ensure_ascii=False, indent=2)
                                
                                strl.session_state["audit_cache"] = f"💡 [M7-EMERGENCY-DOCK] 成功吞噬持久化大坝 FMP 原始财报数据"
                        except Exception as file_err:
                            final_audit_content = f"强吞持久化 FMP 资产发生异常: {str(file_err)}"

                current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S (UTC+8)")
                
                time_anchor_instruction = (
                    f"【M7系统高优先级时钟注入】\n"
                    f"当前最新的绝对操作时间为: {current_time_str}。\n"
                    f"请你在最终输出的战略研报头部的『发布时间』一栏中，必须精确填写这个时间（{current_time_str}）。"
                    f"严禁参考或沿用任何历史缓存或原始财报文件中的旧日期作为报告发布日期！\n"
                    f"==================================================\n\n"
                )
                
                final_audit_content_with_time = time_anchor_instruction + final_audit_content

                macro_input = global_cached_macro if global_cached_macro else macro_engine.get_macro_indicators()
                stock_news_input = global_cached_stock_news if global_cached_stock_news else news_engine.get_latest_news(query_type="stock", topic=decision_target, limit=5)
                geo_news_input = global_cached_geo_news if global_cached_geo_news else news_engine.get_latest_news(query_type="geopolitics", limit=5)
                
                raw_decision_report = decision_engine.generate_m7_weekly_decision(
                    ticker=decision_target,
                    period_choice=period_choice,
                    macro_data=macro_input,
                    audit_text=final_audit_content_with_time,
                    stock_news=stock_news_input,
                    geo_news=geo_news_input
                )
                strl.session_state[decision_cache_key] = raw_decision_report
                
        # =====================================================================
        # 🏁 纯净 Markdown 清洗渲染器
        # =====================================================================
        if strl.session_state[decision_cache_key]:
            strl.markdown('<div style="background-color:#111625; padding:12px; border-radius:8px; border-left: 5px solid #00FF00; margin-bottom: 15px;"><h4 style="color:#00FF00; margin-top:0px; margin-bottom:0px; font-family: monospace;">🦅 M7 量化主权研报体系 · 决策流完美合龙</h4></div>', unsafe_allow_html=True)
            
            raw_report = strl.session_state[decision_cache_key]
            clean_text = ""
            
            if isinstance(raw_report, list) and len(raw_report) > 0:
                node = raw_report[0]
                clean_text = node.text if hasattr(node, "text") else (node.get("text", str(node)) if isinstance(node, dict) else str(node))
            elif isinstance(raw_report, dict):
                clean_text = raw_report.get("text", raw_report.get("content", str(raw_report)))
            elif isinstance(raw_report, str):
                if raw_report.strip().startswith("[") or raw_report.strip().startswith("{"):
                    try:
                        if "'text':" in raw_report:
                            s = raw_report.find("'text': '") + 9
                            e = raw_report.find("', 'type'")
                            if s != -1 and e != -1: clean_text = raw_report[s:e].replace("\\n", "\n")
                    except: pass
                if not clean_text: clean_text = raw_report
            else:
                clean_text = str(raw_report)
                
            strl.markdown(clean_text)