# decision_engine.py (M7-ALPHA 中央高维量化决策引擎 · 内存动态量化因子生成完全体 · 突发高敏因数剥离提权版)
import os
import json
import random
import sys
import pandas as pd
import numpy as np
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

print("⚙️ [M7-TRACE-BOOT] 正在加载 M7 决策大脑动态因子解算环境...")
load_dotenv()

API_KEY_POOL = [
    os.environ.get("GOOGLE_API_KEY1"),
    os.environ.get("GOOGLE_API_KEY2"),
    os.environ.get("GOOGLE_API_KEY3"),
    os.environ.get("GOOGLE_API_KEY4"),
    os.environ.get("GOOGLE_API_KEY5"), 
]

active_google_keys = []
for k in API_KEY_POOL:
    if k:
        clean_k = str(k).strip().replace('"', '').replace("'", "")
        if clean_k and clean_k.upper() != "NONE" and clean_k != "":
            active_google_keys.append(clean_k)

if not active_google_keys:
    print("❌ [M7-FATAL] 铁血审计长官熔断：未在环境配置文件中发现任何可用的 GOOGLE_API_KEY！")
    sys.exit(1)


def generate_m7_weekly_decision(ticker, period_choice, macro_data, audit_text, stock_news, geo_news, time_prompt, urgent_intel=""):
    """
    🚀【M7 高规格重构对齐】：增设 time_prompt 与 urgent_intel 独立形参，
    实现冷、热基本面数据空间全方位剥离与独立解析
    """
    print(f"🧠 [M7-DECISION-ENGINE] 正在从本地 Parquet 动态计算 [{ticker}] 均线与布林带矩阵...")
    
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    BASE_CACHE_DIR = "/data" if os.path.exists("/data") else PROJECT_ROOT
    DATA_CACHE_DIR = os.path.join(BASE_CACHE_DIR, "data_cache")

    latest_market_metrics = {}
    try:
        parquet_path = os.path.join(DATA_CACHE_DIR, f"{ticker.lower()}_10y.parquet")
        if os.path.exists(parquet_path):
            df = pd.read_parquet(parquet_path)
            if not df.empty:
                df.columns = [c.capitalize() for c in df.columns]
                if "Date" in df.columns: df = df.sort_values("Date")
                
                df["Computed_MA5"] = df["Close"].rolling(window=5).mean()
                df["Computed_MA20"] = df["Close"].rolling(window=20).mean()
                df["Computed_Boll_Mid"] = df["Computed_MA20"]
                df["Computed_Std"] = df["Close"].rolling(window=20).std()
                df["Computed_Boll_Upper"] = df["Computed_Boll_Mid"] + (df["Computed_Std"] * 2)
                df["Computed_Boll_Lower"] = df["Computed_Boll_Mid"] - (df["Computed_Std"] * 2)
                
                ema12 = df["Close"].ewm(span=12, adjust=False).mean()
                ema26 = df["Close"].ewm(span=26, adjust=False).mean()
                df["Computed_MACD"] = ema12 - ema26

                target_row = df.iloc[-1]
                for i in range(1, min(len(df) + 1, 15)):
                    row_candidate = df.iloc[-i]
                    if not pd.isna(row_candidate.get("Computed_MA20")) and float(row_candidate.get("Computed_MA20")) != 0.0:
                        target_row = row_candidate
                        break

                latest_market_metrics = {
                    "最新实际收盘价": round(float(target_row.get("Close", 0)), 2),
                    "5_day_MA(5日均线)": round(float(target_row.get("Computed_MA5", 0)), 2),
                    "20_day_MA(20日均线)": round(float(target_row.get("Computed_MA20", 0)), 2),
                    "布林带上轨(Boll_Upper)": round(float(target_row.get("Computed_Boll_Upper", 0)), 2),
                    "布林带中轨(Boll_Mid)": round(float(target_row.get("Computed_Boll_Mid", 0)), 2),
                    "布林带下轨(Boll_Lower)": round(float(target_row.get("Computed_Boll_Lower", 0)), 2),
                    "MACD物理状态": "零轴上方多头放量形态" if float(target_row.get("Computed_MACD", 0)) >= 0 else "零轴下方空头修正形态"
                }
    except Exception as e: print(f"❌ 动态个股技术面计算崩溃: {e}")

    broad_market_metrics = {}
    index_map = {"标普500 (S&P 500)": "gspc", "道琼斯 (Dow 30)": "dji", "纳斯达克 (Nasdaq)": "ixic"}
    for idx_name, idx_file in index_map.items():
        try:
            idx_parquet_path = os.path.join(DATA_CACHE_DIR, f"{idx_file}_10y.parquet")
            if os.path.exists(idx_parquet_path):
                df_idx = pd.read_parquet(idx_parquet_path)
                if not df_idx.empty:
                    close_series = df_idx["Close"].dropna().values.flatten() if "Close" in df_idx.columns else df_idx.iloc[:, df_idx.columns.get_level_values(-1) == 'Close'].dropna().values.flatten()
                    if len(close_series) >= 2:
                        broad_market_metrics[idx_name] = {
                            "当前最新指数点位": f"{close_series[-1]:,.2f}",
                            "大盘日内动态涨跌幅": f"{((close_series[-1] - close_series[-2]) / close_series[-2]) * 100:+.2f}%",
                            "宏观大盘多空情绪": "绿色多头共振" if close_series[-1] > close_series[-2] else "红色空头承压"
                        }
        except: pass

    gemini_key = random.choice(active_google_keys)
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.1, google_api_key=gemini_key)

    stock_news_summary = "\n".join([f"- [个股舆情] {n.get('title')}: {n.get('summary')[:250]}" for n in stock_news])
    geo_news_summary = "\n".join([f"- [地缘前沿] {n.get('title')}: {n.get('summary')[:250]}" for n in geo_news])

    # 🚀🔥【提示词矩阵高维剥离解耦大阵】
    # 将 urgent_intel 与 audit_text 划归彼此完全隔离的数据源，强行对突发加急大新闻赋予最高级别逻辑指导权！
    prompt_context = f"""
    您是 M7-ALPHA 量化主权基金的首席战略宏观与基本面联审专家。请对标的 [{ticker}] 执行未来一周的高规格专业操盘研报输出。
    
    【🔴 铁血深度审计最高主权要求】：
    你的分析过程必须在对应的模块里，显式地提及并深度解读以下输入因子（决不能省略）：
    1. ⚡⚡【长官单独加急注入的突发最高权时空情报（数据源五）】：
       此条为长官手工捕获的最新最火爆盘前、资本突发情报。如果其中提及类似“盘前大跌10%”、“80B定向融资稀释”等重磅突发事实，必须在四大模块（尤其是风险及实盘策略）中将其作为【全网一号突发变量因子】优先并网计算，对冲陈旧基本面带来的认知断层！
    2. 必须提及【数据源四】本地落盘的 FMP 核心财务库，将其视作长期底座，与数据源五的短期剧烈波动进行“长周期面+短周期点”的综合跨维度因子共振推演。
    3. 严格结合大盘气象快照、Parquet 技术面实际数据（股价、均线、布林带具体数值），解算出精准的阻力位与支撑位。
    
    【当前看盘时基视口】: {period_choice}
    
    【数据源一：最新时钟基准时空价格核】
    {time_prompt}
    
    【数据源二：美国三大主权股指大盘气象快照】
    {json.dumps(broad_market_metrics, ensure_ascii=False, indent=2)}
    
    【数据源三：最新个股实盘 Parquet 技术面动态解算快照】
    {json.dumps(latest_market_metrics, ensure_ascii=False, indent=2)}
    
    【数据源四：本地落盘固化的 FMP 核心财务审计长卷（长期底座）】
    {audit_text if audit_text else "暂无持久化财务冷数据。"}
    
    【数据源五：📢 长官独占加急通道注入的实盘突发头条因子（短期最高热变量）】
    ➡️ 【突发事实】: {urgent_intel if urgent_intel else "【当前市场平静，无长官加急手动录入情报，一切基于常规多维数据流进行平稳解算。】"}
    
    【数据源六：M7 双翼高敏舆情雷达网】
    * 个股前沿快讯摘要:
    {stock_news_summary}
    * 全球地缘政治动向:
    {geo_news_summary}
    
    请严格基于上述完全解耦、无冲突的数据大坝，输出包含以下四大硬核结构的专业操盘研报（要把数据和逻辑平铺展开，拒绝任何含糊的泛化分析）：
    
    ### 1️⃣ 【核心决策方向与全维数据引证矩阵】
    ### 2️⃣ 【技术面物理状态与核心价格推演】
    ### 3️⃣ 【未来一周涨势评级与多维因子共振逻辑】
    ### 4️⃣ 【实盘防卷操作策略与全方位风控预案】
    """

    try:
        message = HumanMessage(content=prompt_context)
        ai_message = llm.invoke([message])
        return ai_message.content
    except Exception as err:
        return f"❌ [M7-DECISION-FATAL] 策略矩阵撞墙: {str(err)}"