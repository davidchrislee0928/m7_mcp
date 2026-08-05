# decision_engine.py (M7-ALPHA Central Quant Strategic Decision Engine - Multi-Factor Synthesis)
import os
import json
import random
import sys
import pandas as pd
import numpy as np
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

print("⚙️ [M7-TRACE-BOOT] Loading M7 Decision Brain dynamic factor computation environment...")
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
    print("❌ [M7-FATAL] Chief Auditor Circuit Breaker: No valid GOOGLE_API_KEY found in configuration!")
    sys.exit(1)


def generate_m7_weekly_decision(ticker, period_choice, macro_data, audit_text, stock_news, geo_news, time_prompt, urgent_intel=""):
    """
    🚀 M7 Strategic Decision Engine: Integrates live prices, macro factors, 
    technical indicators, fundamental audits, and urgent intelligence catalysts.
    """
    print(f"🧠 [M7-DECISION-ENGINE] Dynamically computing technical indicators for [{ticker}] from local Parquet cache...")
    
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

                target_row = df.iloc[-1]
                for i in range(1, min(len(df) + 1, 15)):
                    row_candidate = df.iloc[-i]
                    if not pd.isna(row_candidate.get("Computed_MA20")) and float(row_candidate.get("Computed_MA20")) != 0.0:
                        target_row = row_candidate
                        break

                latest_market_metrics = {
                    "Latest_Close_Price": round(float(target_row.get("Close", 0)), 2),
                    "5_Day_MA": round(float(target_row.get("Computed_MA5", 0)), 2),
                    "20_Day_MA": round(float(target_row.get("Computed_MA20", 0)), 2),
                    "Bollinger_Upper": round(float(target_row.get("Computed_Boll_Upper", 0)), 2),
                    "Bollinger_Mid": round(float(target_row.get("Computed_Boll_Mid", 0)), 2),
                    "Bollinger_Lower": round(float(target_row.get("Computed_Boll_Lower", 0)), 2),
                    "MACD_State": "Bullish momentum above zero line" if float(target_row.get("Computed_MACD", 0)) >= 0 else "Bearish correction below zero line"
                }
    except Exception as e: 
        print(f"❌ Error computing dynamic technical metrics: {e}")

    broad_market_metrics = {}
    index_map = {"S&P 500 Index": "gspc", "Dow Jones Industrial": "dji", "NASDAQ Composite": "ixic"}
    for idx_name, idx_file in index_map.items():
        try:
            idx_parquet_path = os.path.join(DATA_CACHE_DIR, f"{idx_file}_10y.parquet")
            if os.path.exists(idx_parquet_path):
                df_idx = pd.read_parquet(idx_parquet_path)
                if not df_idx.empty:
                    close_series = df_idx["Close"].dropna().values.flatten() if "Close" in df_idx.columns else df_idx.iloc[:, df_idx.columns.get_level_values(-1) == 'Close'].dropna().values.flatten()
                    if len(close_series) >= 2:
                        broad_market_metrics[idx_name] = {
                            "Latest_Index_Level": f"{close_series[-1]:,.2f}",
                            "Daily_Percentage_Change": f"{((close_series[-1] - close_series[-2]) / close_series[-2]) * 100:+.2f}%",
                            "Market_Sentiment": "Bullish Resonance" if close_series[-1] > close_series[-2] else "Bearish Pressure"
                        }
        except: 
            pass

    gemini_key = random.choice(active_google_keys)
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.1, google_api_key=gemini_key)

    stock_news_summary = "\n".join([f"- [Ticker Catalyst] {n.get('title')}: {n.get('summary')[:250]}" for n in stock_news])
    geo_news_summary = "\n".join([f"- [Geopolitical Radar] {n.get('title')}: {n.get('summary')[:250]}" for n in geo_news])

    prompt_context = f"""
    You are the Chief Quantitative Strategist and Fundamental Analyst at M7-ALPHA Capital. Generate an executive-grade trading decision report for ticker [{ticker}] for the upcoming trading week.

    【🔴 MANDATORY ANALYSIS RULES】:
    1. ⚡⚡【DATA SOURCE 5: URGENT EXECUTIVE INTELLIGENCE】:
       This input contains real-time catalysts entered directly by executive leadership. If it mentions events such as "10% pre-market crash" or "private placement dilution", you MUST treat it as the HIGHEST PRIORITY SHORT-TERM CATALYST across all sections (especially Risk Control and Trading Strategy) to counter historical fundamental lag!
    2. 【DATA SOURCE 4: FUNDAMENTAL AUDIT REPORT】:
       Treat this as the structural baseline. Synthesize the long-term fundamental anchor from Source 4 with the short-term high-volatility impulse from Source 5.
    3. 【TECHNICAL & MACRO ALIGNMENT】:
       Combine the Macro Snapshot with exact Technical Data (Close Price, Moving Averages, Bollinger Bands) to derive precise resistance and support levels.
    4. 🚫 【NO LATEX / MATH FORMATTING】:
       DO NOT wrap prose sentences or text in LaTeX math characters (like $...$ or $$...$$). Write plain text and dollar figures directly as plain numbers (e.g., write "$18.22B" or "10%").
    5. 🚫 【NO HALLUCINATIONS】:
       If any historical data point is unavailable, report 'N/A' directly. Never fabricate historical financials.

    【CURRENT TIMEFRAME VIEW】: {period_choice}
    
    【DATA SOURCE 1: LIVE BENCHMARK EXECUTION PRICE】
    {time_prompt}
    
    【DATA SOURCE 2: U.S. MAJOR INDICES MACRO SNAPSHOT】
    {json.dumps(broad_market_metrics, ensure_ascii=False, indent=2)}
    
    【DATA SOURCE 3: REAL-TIME TECHNICAL INDICATORS (PARQUET ENGINE)】
    {json.dumps(latest_market_metrics, ensure_ascii=False, indent=2)}
    
    【DATA SOURCE 4: PERSISTENT FUNDAMENTAL AUDIT REPORT (STRUCTURAL BASELINE)】
    {audit_text if audit_text else "No cached fundamental report available."}
    
    【DATA SOURCE 5: 📢 URGENT EXECUTIVE INTELLIGENCE STREAM (HIGHEST PRIORITY IMPULSE)】
    ➡️ 【URGENT FACTOR】: {urgent_intel if urgent_intel else "Market conditions calm. No custom urgent intelligence entered by executive leadership. Proceeding with standard multi-factor synthesis."}
    
    【DATA SOURCE 6: M7 HIGH-SENSITIVITY NEWS RADAR】
    * Ticker News Feed:
    {stock_news_summary}
    * Geopolitical Intelligence:
    {geo_news_summary}
    
    Please output a comprehensive, structured quantitative trading report using EXACTLY the following 4 section headings in Markdown:
    
    ### 1️⃣ 【Executive Direction & Multi-Factor Evidence Matrix】
    ### 2️⃣ 【Technical Indicator State & Key Target Price Levels】
    ### 3️⃣ 【Weekly Outlook Rating & Multi-Factor Convergence Logic】
    ### 4️⃣ 【Actionable Trading Strategy & Risk Management Plan】
    """

    try:
        message = HumanMessage(content=prompt_context)
        ai_message = llm.invoke([message])
        
        # 1️⃣ 提取纯文本 content（安全处理 str 和 list 多种返回类型）
        raw_content = ai_message.content
        if isinstance(raw_content, list):
            fragments = []
            for block in raw_content:
                if isinstance(block, dict) and 'text' in block:
                    fragments.append(str(block['text']))
                else:
                    fragments.append(str(block))
            clean_res = "".join(fragments)
        else:
            clean_res = str(raw_content)

        # 2️⃣ 彻底斩断 LaTeX 字体斜体粘连 BUG：
        # 将被 $ ... $ 包裹的长文本，或单独的美元符号全部进行转义或替换，
        # 确保 Streamlit 把它当成纯文本/Markdown 渲染，绝不触发 KaTeX 公式引擎！
        import re
        
        # 物理剥离包裹长英文句子的单美元符号 (如 $200B Anthropic...$ -> 200B Anthropic...)
        clean_res = re.sub(r'\$([^\$\n]{2,})\$', r'\1', clean_res)
        
        # 消除 Note: 被 * ... * 强行包裹造成的全段斜体
        clean_res = re.sub(r'\*(Note:[^*]+)\*', r'\1', clean_res)
        
        # 将剩下的单个美元符号（如 $200B）转义为 \$，防止 Streamlit 前端误判
        clean_res = clean_res.replace('$', '\\$')
        
        return clean_res

    except Exception as err:
        return f"❌ [M7-DECISION-FATAL] Strategic decision matrix execution failed: {str(err)}"