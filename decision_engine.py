# decision_engine.py (M7-ALPHA Central Quant Strategic Decision Engine - Multi-Factor Synthesis & Anti-HTML Leak)
import os
import json
import random
import sys
import re
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
    🚀 M7 Strategic Decision Engine: Integrates live prices, FRED macro factors, 
    technical indicators, fundamental audits, deep news catalysts, and urgent intelligence.
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

    # 🌐【结构化解包】格式化 FRED 美联储 & 核心宏观多因子清单
    macro_formatted_lines = []
    if isinstance(macro_data, dict):
        for m_key, m_val in macro_data.items():
            if isinstance(m_val, dict):
                v_str = m_val.get("val", "N/A")
                p_str = m_val.get("prev", "N/A")
                d_str = f" [Release: {m_val.get('date')}]" if m_val.get('date') else ""
                macro_formatted_lines.append(f"- **{m_key}**: Current={v_str} | Prev={p_str}{d_str}")
            else:
                macro_formatted_lines.append(f"- **{m_key}**: {m_val}")
    macro_full_str = "\n".join(macro_formatted_lines) if macro_formatted_lines else "No detailed FRED macro factors available."

    gemini_key = random.choice(active_google_keys)
    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.1, google_api_key=gemini_key)

    stock_news_summary = "\n".join([
        f"- [News Catalyst #{i+1}] Title: {n.get('title', 'N/A')} | Content: {n.get('summary', n.get('description', ''))[:500]}" 
        for i, n in enumerate(stock_news)
    ]) if stock_news else "No specific stock news retrieved."

    geo_news_summary = "\n".join([
        f"- [Geopolitical Intel #{i+1}] Title: {n.get('title', 'N/A')} | Content: {n.get('summary', '')[:400]}" 
        for i, n in enumerate(geo_news)
    ]) if geo_news else "No specific geopolitical news retrieved."

    # =====================================================================
    # 🎯 全量定型 System Prompt 模板 (严禁 HTML 裸露与技术逻辑错位)
    # =====================================================================
    prompt_context = f"""
    You are the Chief Quantitative Strategist and Fundamental Analyst at M7-ALPHA Capital. Generate an executive-grade trading decision report for ticker [{ticker}] for the upcoming trading week.

    【🔴 MANDATORY ANALYSIS & FORMATTING RULES】:
    1. ⚡⚡【DATA SOURCE 5: URGENT EXECUTIVE INTELLIGENCE】:
       This input contains real-time catalysts entered directly by executive leadership. If it mentions events such as "10% pre-market crash" or "private placement dilution", you MUST treat it as the HIGHEST PRIORITY SHORT-TERM CATALYST across all sections (especially Risk Control and Trading Strategy) to counter historical fundamental lag!

    2. 🏛️【DATA SOURCE 2: FULL-SPECTRUM FRED MACRO & FED LIQUIDITY FACTORS (MANDATORY)】:
       You MUST explicitly integrate Fed Funds Rate, Unemployment Rate, Non-Farm Payrolls, Core CPI YoY, PPI (YoY/MoM), 10Y Treasury Yield, and US Dollar Index into your macro analysis. Explain how interest rates, labor market tightness, and inflation sticky points impact the discount rate and valuation baseline for [{ticker}].

    3. 📐【TECHNICAL MA ALIGNMENT & PRICE LEVEL STRICT ORDER (NEVER INVERT)】:
       - **Bullish Golden Cross Setup**: In a Bullish/Overweight stance, 5-Day MA MUST be HIGHER than 20-Day MA (e.g., 5-Day MA @ $121.50 > 20-Day MA @ $114.60). Entry Zone should build above or near 5-Day MA, and Stop-Loss MUST be placed SAFELY BELOW 20-Day MA (the lower, stronger support)! NEVER claim 20-Day MA is higher than 5-Day MA in a bullish alignment!
       - **Price Ordering Strict Sanity Rule**:
         * For LONG/BULLISH: Stop-Loss < Entry Zone < Primary Take-Profit Target < Upside Acceleration Trigger.
         * For SHORT/BEARISH: Primary Take-Profit Target < Entry Zone < Stop-Loss < Downside Acceleration Trigger.

    4. 🚫 【ABSOLUTE NO HTML TAGS & ZERO LATEX RULE (CRITICAL)】:
       - DO NOT EVER output raw HTML code or CSS inline tags (such as `<span style="...">`, `<div>`, `</span>`, etc.) inside the generated report body!
       - Write sentiment labels in PLAIN TEXT with standard brackets and standard text emojis ONLY (e.g., write `[Sentiment: BEARISH 🔴]` or `[Sentiment: BULLISH 🟢]`).
       - DO NOT use LaTeX syntax like `\\text{{...}}`, `\\frac{{...}}`, or LaTeX delimiters (`$`). Write plain text numbers and standard dollar signs!

    5. 📰【DATA SOURCE 6: HIGH-WEIGHT NEWS CATALYST EXTRACTION】:
       DO NOT summarize all news into a single generic sentence! In Section 3, you MUST explicitly extract 2 to 4 SPECIFIC high-impact catalysts from Data Source 6, label their sentiment using pure text (e.g., `[Sentiment: HIGH VOLATILITY / BEARISH 🔴]`), and detail their direct price implications.

    6. 🎯【DIRECTIONAL & TRADE PARAMETER STRICT CONSISTENCY】:
       Your trade execution parameters MUST strictly align with the Executive Direction:
       - If Executive Direction is BULLISH or OVERWEIGHT: Tactical Entry Zone must be a buy level, Take-Profit must be ABOVE Entry, Stop-Loss must be BELOW Entry.
       - If Executive Direction is BEARISH or UNDERWEIGHT: DO NOT provide a long buy setup! State clearly that this is a risk-mitigation / position reduction stance, or provide short/hedging parameters where Take-Profit is BELOW Entry and Stop-Loss is ABOVE Entry.

    7. ⚖️【REWARD-TO-RISK RATIO & PURE TEXT CALCULATION】:
       Use EXCLUSIVELY the term "Reward-to-Risk Ratio" (DO NOT write "Risk-Reward Ratio"). 
       Calculate it strictly as: Reward / Risk = (Take Profit - Entry) / (Entry - Stop Loss) [for Long] or (Entry - Take Profit) / (Stop Loss - Entry) [for Short].
       * Output the calculation purely in plain text, e.g.: 
         `Reward-to-Risk Ratio: 2.5:1 (Reward: $26.50 / Risk: $10.60)`

    8. 📊【SECTION 1 MULTI-FACTOR EVIDENCE MATRIX STRICT TEMPLATE】:
       Section 1 MUST contain a clean Markdown Table with EXACTLY 3 columns (`Factor Module`, `Data Input & Values`, `Impact on Valuation & Trend Signal`). DO NOT output pseudo-code boxes, ASCII block diagrams, or text lists for the matrix.

    ------------------------------------------------------------------
    【INPUT FACTOR DATASETS】

    【CURRENT TIMEFRAME VIEW】: {period_choice}
    
    【DATA SOURCE 1: LIVE BENCHMARK EXECUTION PRICE】
    {time_prompt}
    
    【DATA SOURCE 2: U.S. MAJOR INDICES & FULL-SPECTRUM FRED MACRO FACTORS】
    * U.S. Major Stock Market Benchmarks:
    {json.dumps(broad_market_metrics, ensure_ascii=False, indent=2)}
    
    * Federal Reserve & Core Macro Economic Indicators (FRED API):
    {macro_full_str}
    
    【DATA SOURCE 3: REAL-TIME TECHNICAL INDICATORS (PARQUET ENGINE)】
    {json.dumps(latest_market_metrics, ensure_ascii=False, indent=2)}
    
    【DATA SOURCE 4: PERSISTENT FUNDAMENTAL AUDIT REPORT (STRUCTURAL BASELINE)】
    {audit_text if audit_text else "No cached fundamental report available."}
    
    【DATA SOURCE 5: 📢 URGENT EXECUTIVE INTELLIGENCE STREAM (HIGHEST PRIORITY IMPULSE)】
    ➡️ 【URGENT FACTOR】: {urgent_intel if urgent_intel else "Market conditions calm. No custom urgent intelligence entered by executive leadership. Proceeding with standard multi-factor synthesis."}
    
    【DATA SOURCE 6: M7 HIGH-SENSITIVITY NEWS RADAR】
    * Ticker-Specific Catalysts (Up to 7 items):
    {stock_news_summary}
    
    * Geopolitical & Macro Risk Feed:
    {geo_news_summary}
    ------------------------------------------------------------------

    Please output a comprehensive, structured quantitative trading report using EXACTLY the following 4 section headings in Markdown:
    
    ### 1️⃣ 【Executive Direction & Multi-Factor Evidence Matrix】
    - **Executive Direction**: [BULLISH / BEARISH / NEUTRAL / OVERWEIGHT / UNDERWEIGHT]
    - **Primary Execution Benchmark**: [Current Execution Price]
    - **Timeframe**: [Daily / 1-Week Tactical Window]

    #### Multi-Factor Evidence Matrix
    | Factor Module | Data Input & Values | Impact on Valuation & Trend Signal |
    | :--- | :--- | :--- |
    | **Fed & Macro Regime** | [Summarize Fed Rate, CPI, PPI, NFP, Unemployment, Yields] | [Analysis signal] |
    | **Market Beta Sentiment** | [Summarize S&P 500, NASDAQ, Dow Jones] | [Analysis signal] |
    | **Fundamental Anchor** | [Summarize Earnings, Revenue, Margins, and Audit Assessment] | [Analysis signal] |
    | **Real-Time Catalysts & News** | [Summarize Key News Catalysts & Urgent Intel] | [Analysis signal] |

    ### 2️⃣ 【Technical Indicator State & Key Target Price Levels】
    - **Technical Structure Overview**: [Moving Average alignment and Bollinger Band status]
    - **Key Resistance Levels**: [Resistance 1, Resistance 2]
    - **Key Support Levels**: [Support 1, Support 2]

    ### 3️⃣ 【Weekly Outlook Rating & Multi-Factor Convergence Logic】
    - **Macro & Fed Liquidity Alignment**: [Deep analysis on Fed Rate, Inflation, Labor Data]
    - **Fundamental & Earnings Confluence**: [Synthesis of fundamental report & health assessment]
    - **News & Geopolitical Catalyst Impact**: 
      * **Key High-Impact News Drivers**: [Explicitly cite 2 to 4 specific news events from Data Source 6 and analyze their direct price/sentiment impact on {ticker}. Use pure text brackets like [Sentiment: BEARISH 🔴]!]
      * **Geopolitical & Sentiment Alignment**: [Explicitly state market sentiment e.g., EXTREME EUPHORIA / RISK-ON or FEAR / RISK-OFF]

    ### 4️⃣ 【Actionable Trading Strategy & Risk Management Plan】
    - **Recommended Asset Allocation**: [e.g., Overweight (5.0% to 7.0%) or Underweight (1.0% to 2.0% defensive allocation)]
    - **Sentiment-Driven Risk Regime**: [必须明确给出情绪定位与风控建议，例如: RISK-ON / HIGH CATALYST VOLATILITY (FOMO 追高风险高，建议分步挂单入场 — avoid market orders at market open; build positions via tiered limit orders between 5-Day and 20-Day moving averages to mitigate earnings-implied volatility spikes) 或 RISK-OFF / EXTREME FEAR (极度恐慌，宽止损防洗盘)]
    - **Trade Execution Parameters**:
      * **Tactical Entry Zone**: [Exact Entry Price or Range. Ensure it aligns correctly with MAs e.g., Layered limit orders between 20-Day MA and 5-Day MA]
      * **Primary Take-Profit Target**: [Exact Target Price]
      * **Strict Stop-Loss Level**: [Exact Stop-Loss Price. MUST be positioned safely below the LOWER/STRONGER MA support line for Long!]
    - **Reward-to-Risk Ratio**: [Calculated precisely as (Target - Entry) / (Entry - Stop Loss), e.g., 2.5:1 (Reward: $26.50 / Risk: $10.60)]
    - **Dynamic Contingency Triggers**:
      * **Upside Acceleration Trigger**: [e.g., A daily close above $X opens secondary momentum toward $Y]
      * **Downside Invalidation Trigger**: [e.g., A breach below $Z invalidates the stance]
    """

    try:
        message = HumanMessage(content=prompt_context)
        ai_message = llm.invoke([message])
        
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

        # =====================================================================
        # 🧹【多重安全正则清理】彻底剥离任何残留的 HTML 标签与 LaTeX 破坏符
        # =====================================================================
        # 1. 移除伪代码块标识
        clean_res = re.sub(r'```[a-zA-Z]*\n', '', clean_res)
        clean_res = clean_res.replace('```', '')
        
        # 2. 彻底撕毁大模型可能误吐出的 HTML 标签（如 <span style="...">...</span> 或 <div>）
        clean_res = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', clean_res, flags=re.IGNORECASE)
        clean_res = re.sub(r'</?[a-zA-Z][^>]*>', '', clean_res)
        
        # 3. 剥离 \text{...} 和 \frac{...}{...} LaTeX 算式裸露
        clean_res = re.sub(r'\\text\{([^}]+)\}', r'\1', clean_res)
        clean_res = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1 / \2', clean_res)
        
        # 4. 消除多余的反斜杠（如 \140.00 -> 140.00）
        clean_res = re.sub(r'\\([0-9]+)', r'\1', clean_res)
        
        # 5. 剥离包裹在句中多余的单美元符号（$200B -> 200B）
        clean_res = re.sub(r'\$([^\$\n]{2,})\$', r'\1', clean_res)
        clean_res = re.sub(r'\*(Note:[^*]+)\*', r'\1', clean_res)
        
        # 6. 最后统一进行美元符号转义，防止 Streamlit 前端将 $ 误识别为 LaTeX 渲染标识符
        clean_res = clean_res.replace('$', '\\$')
        
        return clean_res

    except Exception as err:
        return f"❌ [M7-DECISION-FATAL] Strategic decision matrix execution failed: {str(err)}"