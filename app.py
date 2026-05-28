# app.py (M7-ALPHA 主界面控制台终端 - FMP物理资产无损强吞完全体)
import streamlit as strl
import os
import sys
import json

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
# ⚙️ 控制中心侧边栏 - 双时区时钟与 Parquet 价格并网网关
# =====================================================================
# =====================================================================
# ⚙️ 控制中心侧边栏 - 双时区终端时钟与 Parquet 价格自愈网关
# =====================================================================
with strl.sidebar:
    strl.title("⚙️ 控制中心")
    strl.caption("架构层: 工业级单画布四轴强联动合龙内核")
    strl.markdown("---")
    
    # 🌟 核心功能一：双时区主权时钟实时监控（全宽通铺，彻底解决 ... 截断与时区报错问题）
    from datetime import datetime
    import pytz

    # 精准定义时区
    local_tz = pytz.timezone('Asia/Shanghai')
    est_tz = pytz.timezone('America/New_York')
    
    # 获取带有时区感知的基础 UTC 时间
    now_utc = datetime.now(pytz.utc)
    
    # 🔥 【精准修复点】：100% 使用标准 astimezone() 进行安全时区转换
    local_now = now_utc.astimezone(local_tz)
    est_now = now_utc.astimezone(est_tz)

    strl.markdown("### 🕒 跨空间铁血时钟")
    strl.markdown(
        f"""
        <div style="background-color:#161b22; padding:10px; border-radius:6px; border-left:4px solid #00FF00; margin-bottom:10px;">
            <p style="margin:0; color:#8b949e; font-size:11px; font-family:monospace;">北京时间 (Asia/Shanghai)</p>
            <p style="margin:0; color:#58a6ff; font-size:18px; font-weight:bold; font-family:monospace;">{local_now.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <div style="background-color:#161b22; padding:10px; border-radius:6px; border-left:4px solid #ff9900; margin-bottom:15px;">
            <p style="margin:0; color:#8b949e; font-size:11px; font-family:monospace;">纽约时间 (EST/EDT 自动对齐)</p>
            <p style="margin:0; color:#f0883e; font-size:18px; font-weight:bold; font-family:monospace;">{est_now.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    strl.markdown("---")

    # 纳指成分股与K线周期标准选择器
    selected_tickers = strl.multiselect("🔮 请选择要审计的纳指成份股:", options=NASDAQ_100_POOL, default=["GOOGL", "NVDA"])
    period_choice = strl.radio("📈 K线周期切换:", options=["日K", "周K", "月K"], index=0, horizontal=True)
    strl.markdown("---")
    
    # 🌟 核心功能二：资产价格网关（Parquet 物理缓存强吞与动态追加覆写）
    if selected_tickers:
        strl.markdown("### 💵 核心资产实时报价")
        import pandas as pd
        import yfinance as yf
        
        # 建立并校准数据缓存目录
        DATA_CACHE_DIR = os.path.join(PROJECT_ROOT, "data_cache")
        os.makedirs(DATA_CACHE_DIR, exist_ok=True)
        
        for ticker in selected_tickers:
            parquet_path = os.path.join(DATA_CACHE_DIR, f"{ticker.lower()}_10y.parquet")
            current_price = None
            price_source = "未知"
            
            # 1. 穿透拉取本地 Parquet 物理库
            if os.path.exists(parquet_path):
                try:
                    df_local = pd.read_parquet(parquet_path)
                    if not df_local.empty and "Close" in df_local.columns:
                        latest_row = df_local.iloc[-1]
                        local_price_time = df_local.index[-1]
                        
                        # 核心校准：如果本地最新数据的时间戳距离当前小于 15 分钟，视为最新价直接强吞
                        if (datetime.now(pytz.utc) - local_price_time.to_pydatetime().astimezone(pytz.utc)).total_seconds() < 900:
                            current_price = float(latest_row["Close"])
                            price_source = "物理缓存 (Parquet)"
                except Exception as p_err:
                    print(f"读取本地 Parquet 缓存异常: {p_err}")
            
            # 2. 缓存未命中/过期，穿透网络大坝追索最新动态报价
            if current_price is None:
                try:
                    ticker_obj = yf.Ticker(ticker)
                    todays_data = ticker_obj.history(period="1d")
                    if not todays_data.empty:
                        current_price = float(todays_data["Close"].iloc[-1])
                        price_source = "实时并网 (yfinance)"
                        
                        # 🔥 异步触发更新：下载 10 年历史长卷，重新覆盖固化本地 Parquet 盾牌
                        full_df = ticker_obj.history(period="10y")
                        if not full_df.empty:
                            full_df.to_parquet(parquet_path)
                except Exception as net_err:
                    print(f"动态抓取最新价失败: {net_err}")
                    # 网络彻底断流时，强行切回 Parquet 物理库的最后一行数据进行容灾兜底
                    if os.path.exists(parquet_path):
                        try:
                            df_local = pd.read_parquet(parquet_path)
                            current_price = float(df_local.iloc[-1]["Close"])
                            price_source = "本地兜底 (Parquet)"
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
        
        # 1. 物理调用原有引擎打捞数据（底层完好保留，不破坏天级缓存与 N/A 自愈机制）
        try:
            macro_data = macro_engine.get_macro_indicators()
            global_cached_macro = macro_data 
        except Exception as err:
            strl.error(f"宏观组件异常: {err}")
            macro_data = {}
            
        # 💡【核心微调点】：放弃 st.columns，改用工业级全宽动态卡片流，确保长文本无损一吐到底
        if macro_data:
            macro_html_tiles = ""
            for name, val in macro_data.items():
                # 根据指标属性，动态匹配高亮边框线颜色
                if "新增" in str(val) or "+" in str(val):
                    tile_border_color = "#00FF00"  # 绿色
                elif "符合" in str(val) or "控" in str(val):
                    tile_border_color = "#f0883e"  # 橙色
                else:
                    tile_border_color = "#58a6ff"  # 蓝色
                
                # 每一个指标组装为一个独立的弹性 Tile 卡片
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
            
            # 使用 Flex 弹性伸缩布局包裹所有卡片，当侧边栏收缩或分屏时，数据会自动转为多行显示，绝对不带省略号
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
        
        # =====================================================================
        # 🎯【以下你原本的代码逻辑原封不动，包括 selectbox、缓存打捞及状态机点火】
        # =====================================================================
        audit_target = strl.selectbox("🎯 请选择本次点火 AI 联审的核心目标:", options=selected_tickers)
        
        report_container = strl.empty()
        
        local_json_path = os.path.join(PROJECT_ROOT, f"fmp_cache_{audit_target}.json")
        has_local_json = os.path.exists(local_json_path)
        
        if "audit_cache" not in strl.session_state:
            strl.session_state["audit_cache"] = ""

        if not strl.session_state["audit_cache"] and has_local_json:
            try:
                with open(local_json_path, "r", encoding="utf-8") as f:
                    local_data = json.load(f)
                    raw_text = local_data.get("audit_report", json.dumps(local_data, ensure_ascii=False))
                    strl.session_state["audit_cache"] = f"💡 [M7-FMP-DOCK] 已成功识别并打捞本地持久化核心资产：\n\n{raw_text[:1200]}..."
            except Exception as e:
                print(f"读取本地 FMP JSON 异常: {e}")

        if strl.session_state["audit_cache"]:
            report_container.markdown(strl.session_state["audit_cache"])
        else:
            report_container.markdown(f"> 锁定战略主攻目标: **{audit_target}**。本地暂无物理库，点击下方按钮激活状态机。")

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
# 🦅 标签页 3：M7 主权决策战略操作仓 (100% 完整物理穿透吞噬逻辑，不卡死)
# =====================================================================
with tab_decision:
    strl.markdown(f"### 🦅 Gemini 3.5 多维因子自适应跨空间终极决策建议")
    
    decision_target = audit_target if 'audit_target' in locals() else (selected_tickers[0] if selected_tickers else None)
    
    if not decision_target:
        strl.info("⏳ 正在等待数据链合龙... 请确保在左侧控制中心至少选择了一支股票。")
    else:
        # 🚀【核心防护】：硬核检测同级目录下是否存在 fmp_cache_{ticker}.json
        local_json_file = os.path.join(PROJECT_ROOT, f"fmp_cache_{decision_target}.json")
        is_fundamental_ready = bool(strl.session_state.get("audit_cache")) or os.path.exists(local_json_file)

        # 动态状态通关灯排布
        d_col1, d_col2, d_col3, d_col4 = strl.columns(4)
        d_col1.markdown(f"🎯 核心标的: **{decision_target}**")
        d_col2.markdown(f"📈 宏观因子墙: <span style='color:#00FF00;'>🟢 已就绪</span>", unsafe_allow_html=True)
        
        if is_fundamental_ready:
            d_col3.markdown(f"📝 FMP基本面: <span style='color:#00FF00; font-weight:bold;'>🟢 已读取本地物理缓存</span>", unsafe_allow_html=True)
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
                
                # 【物理穿透自愈核心】：如果变量丢失，无条件穿透去强吞本地的 fmp_cache_{ticker}.json 财报原始数据
                if not final_audit_content or "💡" not in final_audit_content:
                    if os.path.exists(local_json_file):
                        try:
                            with open(local_json_file, "r", encoding="utf-8") as f:
                                local_json_data = json.load(f)
                                if isinstance(local_json_data, dict) and "audit_report" in local_json_data:
                                    final_audit_content = local_json_data["audit_report"]
                                else:
                                    final_audit_content = json.dumps(local_json_data, ensure_ascii=False, indent=2)
                                
                                # 回填内存
                                strl.session_state["audit_cache"] = f"💡 [M7-EMERGENCY-DOCK] 成功吞噬本地 FMP 原始财报数据"
                        except Exception as file_err:
                            final_audit_content = f"强吞本地 FMP 资产发生异常: {str(file_err)}"

                # 💡【核心修复点】：动态获取每次点击按钮时的绝对真实时间
                from datetime import datetime
                current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S (UTC+8)")
                
                # 组装强指令前缀，强行约束大模型的报告生成行为
                time_anchor_instruction = (
                    f"【M7系统高优先级时钟注入】\n"
                    f"当前最新的绝对操作时间为: {current_time_str}。\n"
                    f"请你在最终输出的战略研报头部的『发布时间』一栏中，必须精确填写这个时间（{current_time_str}）。"
                    f"严禁参考或沿用任何历史缓存或原始财报文件中的旧日期作为报告发布日期！\n"
                    f"==================================================\n\n"
                )
                
                # 将时间指针随财报上下文一同注入大脑
                final_audit_content_with_time = time_anchor_instruction + final_audit_content

                # 提取引擎兜底参数
                macro_input = global_cached_macro if global_cached_macro else macro_engine.get_macro_indicators()
                stock_news_input = global_cached_stock_news if global_cached_stock_news else news_engine.get_latest_news(query_type="stock", topic=decision_target, limit=5)
                geo_news_input = global_cached_geo_news if global_cached_geo_news else news_engine.get_latest_news(query_type="geopolitics", limit=5)
                
                # 🚀 降维投递至决策大脑组件
                raw_decision_report = decision_engine.generate_m7_weekly_decision(
                    ticker=decision_target,
                    period_choice=period_choice,
                    macro_data=macro_input,
                    audit_text=final_audit_content_with_time, # 带有当前最新时间锚点的数据流
                    stock_news=stock_news_input,
                    geo_news=geo_news_input
                )
                strl.session_state[decision_cache_key] = raw_decision_report
                
        # =====================================================================
        # 🏁 纯净 Markdown 清洗渲染器（规避 Langchain/JSON 串打印乱码）
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