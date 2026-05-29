# decision_engine.py (M7-ALPHA 中央高维量化决策引擎 · 内存动态量化因子生成完全体·持久化并网版)
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

# =====================================================================
# 📌 【铁血多 Key 轮流化缘池】（高精清洗并网版）
# =====================================================================
API_KEY_POOL = [
    os.environ.get("GOOGLE_API_KEY1"),
    os.environ.get("GOOGLE_API_KEY2"),
    os.environ.get("GOOGLE_API_KEY3"),
    os.environ.get("GOOGLE_API_KEY4"),
    os.environ.get("GOOGLE_API_KEY"), 
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


def generate_m7_weekly_decision(ticker, period_choice, macro_data, audit_text, stock_news, geo_news):
    print(f"🧠 [M7-DECISION-ENGINE] 正在从本地 Parquet 动态计算 [{ticker}] 均线与布林带矩阵...")
    
    # 确定物理大坝共享数据中心路径
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    if os.path.exists("/data"):
        BASE_CACHE_DIR = "/data"
    else:
        BASE_CACHE_DIR = PROJECT_ROOT
    DATA_CACHE_DIR = os.path.join(BASE_CACHE_DIR, "data_cache")

    # 1. ⚙️【个股核心因子现场量化算力并网】
    latest_market_metrics = {}
    try:
        parquet_path = os.path.join(DATA_CACHE_DIR, f"{ticker.lower()}_10y.parquet")
        if os.path.exists(parquet_path):
            df = pd.read_parquet(parquet_path)
            if not df.empty:
                df.columns = [c.capitalize() for c in df.columns]
                if "Date" in df.columns:
                    df = df.sort_values("Date")
                
                df["Computed_MA5"] = df["Close"].rolling(window=5).mean()
                df["Computed_MA20"] = df["Close"].rolling(window=20).mean()
                df["Computed_Boll_Mid"] = df["Computed_MA20"]
                df["Computed_Std"] = df["Close"].rolling(window=20).std()
                df["Computed_Boll_Upper"] = df["Computed_Boll_Mid"] + (df["Computed_Std"] * 2)
                df["Computed_Boll_Lower"] = df["Computed_Boll_Mid"] - (df["Computed_Std"] * 2)
                
                ema12 = df["Close"].ewm(span=12, adjust=False).mean()
                ema26 = df["Close"].ewm(span=26, adjust=False).mean()
                df["Computed_MACD"] = ema12 - ema26

                target_row = None
                for i in range(1, min(len(df) + 1, 15)):
                    row_candidate = df.iloc[-i]
                    if not pd.isna(row_candidate.get("Computed_MA20")) and float(row_candidate.get("Computed_MA20")) != 0.0:
                        target_row = row_candidate
                        break
                if target_row is None:
                    target_row = df.iloc[-1]

                latest_market_metrics = {
                    "最新实际收盘价": round(float(target_row.get("Close", 0)), 2),
                    "5_day_MA(5日均线)": round(float(target_row.get("Computed_MA5", 0)), 2),
                    "20_day_MA(20日均线)": round(float(target_row.get("Computed_MA20", 0)), 2),
                    "布林带上轨(Boll_Upper)": round(float(target_row.get("Computed_Boll_Upper", 0)), 2),
                    "布林带中轨(Boll_Mid)": round(float(target_row.get("Computed_Boll_Mid", 0)), 2),
                    "布林带下轨(Boll_Lower)": round(float(target_row.get("Computed_Boll_Lower", 0)), 2),
                    "MACD物理状态": "零轴上方多头放量形态" if float(target_row.get("Computed_MACD", 0)) >= 0 else "零轴下方空头修正形态"
                }
        else:
            print(f"⚠️ [DECISION-WARN] 本地未定位到资产盘 {parquet_path}")
    except Exception as e:
        print(f"❌ 动态内存个股因子因子解算崩溃: {e}")

    # 2. 🌍【2026战略新增】：大盘主权气象因子数据大清洗捕捞
    broad_market_metrics = {}
    index_map = {"标普500 (S&P 500)": "gspc", "道琼斯 (Dow 30)": "dji", "纳斯达克 (Nasdaq)": "ixic"}
    
    print("📡 [M7-DECISION-broad] 正在穿透持久化数据大坝合龙三大股指决策因子...")
    for idx_name, idx_file in index_map.items():
        try:
            idx_parquet_path = os.path.join(DATA_CACHE_DIR, f"{idx_file}_10y.parquet")
            if os.path.exists(idx_parquet_path):
                df_idx = pd.read_parquet(idx_parquet_path)
                if not df_idx.empty:
                    # 洗净由于未收盘导致的 NaN 结尾行，提取最末尾两个真实价格
                    if "Close" in df_idx.columns:
                        close_series = df_idx["Close"].dropna().values.flatten()
                    else:
                        # 容灾处理 yfinance 多列结构
                        close_series = df_idx.iloc[:, df_idx.columns.get_level_values(-1) == 'Close'].dropna().values.flatten()
                    
                    if len(close_series) >= 2:
                        curr_close = float(close_series[-1])
                        prev_close = float(close_series[-2])
                        idx_change_pct = ((curr_close - prev_close) / prev_close) * 100
                        
                        broad_market_metrics[idx_name] = {
                            "当前最新指数点位": f"{curr_close:,.2f}",
                            "前一日历史收盘": f"{prev_close:,.2f}",
                            "大盘日内动态涨跌幅": f"{idx_change_pct:+.2f}%",
                            "宏观大盘多空情绪": "绿色多头共振" if idx_change_pct > 0 else "红色空头承压"
                        }
        except Exception as idx_err:
            print(f"⚠️ 吞噬大盘因子 [{idx_name}] 异动: {idx_err}")

    # 3. 🧠 Gemini 3.5 深度量化全解包研报投递 (五维一体铁血 Prompt 矩阵)
    gemini_key = random.choice(active_google_keys)
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0.1,
        google_api_key=gemini_key
    )

    stock_news_summary = "\n".join([f"- [个股信源] {n.get('title')}: {n.get('summary')[:300]}" for n in stock_news])
    geo_news_summary = "\n".join([f"- [地缘政治] {n.get('title')}: {n.get('summary')[:300]}" for n in geo_news])

    prompt_context = f"""
    您是 M7-ALPHA 量化主权基金的首席战略宏观与基本面联审专家。请对标的 [{ticker}] 执行未来一周的高规格专业操盘研报输出。
    
    【🔴 铁血深度审计硬核指令】：
    你的分析过程必须在对应的模块里，显式地提及并深度解读以下输入因子（决不能省略）：
    1. 必须提及并综合研判【最新大盘主权气象因子】，将个股与标普500、纳斯达克大盘的多空情绪进行强弱共振推演（判断个股是强于大盘还是随波逐流）。
    2. 必须提及【最新个股实盘 Parquet 数据】中真实的股价、均线、布林带具体数值，严格根据这些非零的实盘数字执行阻力位/支撑位推演。
    3. 必须提及【宏观经济基本面】中的核心因子（如美国最新非农就业、CPI、PPI中最新的数据特征，以及当前的利率环境与避险资产动态）。
    4. 必须提及【个股基本面审计长卷 / FMP 离线库】中真实的财报数据（例如营收增幅、净利润增长或核心主营业务等具体亮点）。
    5. 必须结合【M7 高敏双翼舆情雷达】中具体的个股及地缘新闻标题与快照内文进行逻辑合流。
    
    【当前战略看盘周期】: {period_choice}
    
    【数据源一：美国三大主权股指大盘气象快照 (保真因子大坝)】
    {json.dumps(broad_market_metrics, ensure_ascii=False, indent=2)}
    
    【数据源二：最新个股实盘 Parquet 技术面动态解算快照】
    {json.dumps(latest_market_metrics, ensure_ascii=False, indent=2)}
    
    【数据源三：实时宏观经济核心指标面板】
    {json.dumps(macro_data, ensure_ascii=False, indent=2)}
    
    【数据源四：本地落盘的 FMP 核心基本面/财务审计长卷】
    {audit_text if audit_text else "暂无持久化财务数据。"}
    
    【数据源五：M7 双流网络高敏新闻舆情雷达】
    * 个股关联前沿电报:
    {stock_news_summary}
    * 全球地缘政治动向:
    {geo_news_summary}
    
    请严格基于上述五维一体的数据，执行高保真逻辑推演，输出必须包含以下四大结构完整的硬核模块（不要缩写，要把数据和逻辑平铺展开）：
    
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