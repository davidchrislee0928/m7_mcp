# mcp_langgraph_agent.py (FMP Gateway · Multi-Key Rotation Pool · Robust Fallback & 429 Anti-Crash Edition)
import os
import sys
import time
import json
import random
import datetime
import requests
import traceback
import pandas as pd  # 👈 核心修复 1：在文件顶部导入 pandas，彻底解决 NameError: name 'pd' is not defined
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

print("\n" + "█"*40 + " 🖥️ M7 QUANT ENGINE INITIALIZATION " + "█"*40)

# 📌 1. FMP Environment Key Gatekeeper
FMP_API_KEY = os.environ.get("FMP_API_KEY")
if not FMP_API_KEY:
    print("❌ [M7-FATAL] Audit Gatekeeper Fusion: [FMP_API_KEY] not found in environment (.env)!")
    sys.exit(1)
print(f"🟢 [M7-INIT] Successfully loaded FMP Financial API Key: [...{FMP_API_KEY[-6:] if len(FMP_API_KEY)>6 else 'VALID'}]")

# 📌 2. Multi-Key Rotation Pool
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
    print("❌ [M7-FATAL] Audit Gatekeeper Fusion: No valid GOOGLE_API_KEY found in configuration!")
    sys.exit(1)

print(f"🟢 [M7-INIT] Successfully activated Gemini rotation pool. Active Key Count: {len(active_google_keys)}.")

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# =====================================================================
# 💾 Persistent Data Path Binding
# =====================================================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

if os.path.exists("/data"):
    BASE_CACHE_DIR = "/data"
    print("🚀 [M7-AGENT] Cloud storage persistent disk detected! Binding agent factor path to: /data")
else:
    BASE_CACHE_DIR = PROJECT_ROOT
    print("💻 [M7-AGENT] No cloud disk detected. Falling back to local development path.")

CACHE_DIR = os.path.join(BASE_CACHE_DIR, "data_cache")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        os.chmod(CACHE_DIR, 0o777)
    except:
        pass

# =====================================================================
# ⚙️ Primary Data Fetcher (FMP API Standard Gateway)
# =====================================================================
def get_company_info_fmp(symbol: str) -> list:
    url = f"https://financialmodelingprep.com/stable/profile?symbol={symbol.upper()}&apikey={FMP_API_KEY}"
    print(f"\n📡 [M7-LOG-HTTP] Requesting FMP Company Profile URL: {url.split('apikey=')[0]}apikey=***")
    try:
        res = requests.get(url, timeout=12)
        print(f"📡 [M7-LOG-HTTP] Company Profile Endpoint Status Code: {res.status_code}")
        if res.status_code == 200:
            res_json = res.json()
            print(f"📡 [M7-LOG-HTTP] Successfully fetched profile, records: {len(res_json)}")
            return res_json
        return []
    except Exception as e:
        print(f"❌ [M7-LOG-ERROR] Network exception fetching FMP Company Profile: {e}")
        return []

def get_income_statement_fmp(symbol: str) -> list:
    url = f"https://financialmodelingprep.com/stable/income-statement?symbol={symbol.upper()}&period=quarter&limit=5&apikey={FMP_API_KEY}"
    print(f"\n📡 [M7-LOG-HTTP] Requesting FMP 5-Quarter Income Statement URL: {url.split('apikey=')[0]}apikey=***")
    try:
        res = requests.get(url, timeout=12)
        print(f"📡 [M7-LOG-HTTP] Income Statement Endpoint Status Code: {res.status_code}")
        if res.status_code == 200:
            res_json = res.json()
            print(f"📡 [M7-LOG-HTTP] Successfully fetched quarterly income statement, records: {len(res_json)}")
            return res_json
        return []
    except Exception as e:
        print(f"❌ [M7-LOG-ERROR] Network exception fetching FMP Income Statement: {e}")
        return []

# =====================================================================
# 💾 Persistent Local Cache Shield & Hybrid Fetcher
# =====================================================================
def get_m7_financial_packet_with_cache(symbol: str) -> dict:
    symbol = symbol.upper().strip()
    cache_file_path = os.path.join(CACHE_DIR, f"fmp_cache_{symbol}.json")
    
    # 1. 优先读取 24 小时内的本地持久化缓存
    if os.path.exists(cache_file_path):
        try:
            with open(cache_file_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            cache_time_str = cache_data.get("fetched_at", "")
            cache_time = datetime.datetime.strptime(cache_time_str, "%Y-%m-%d %H:%M:%S")
            # 校验缓存里的 income 列表是否非空，防止坏缓存死锁
            if (datetime.datetime.now() - cache_time).days < 1 and cache_data.get("packet", {}).get("income"):
                print(f"💾 [M7-LOG-CACHE] Reading valid cached financial data for [{symbol}].")
                return cache_data["packet"]
        except Exception:
            pass

    print(f"📡 [M7-LOG-GATEWAY] Fetching fresh financial data for [{symbol}]...")
    
    # 2. 从 FMP 抓取
    fmp_profile = get_company_info_fmp(symbol)
    fmp_income = get_income_statement_fmp(symbol)
    
    packet = {
        "profile": fmp_profile,
        "income": fmp_income if isinstance(fmp_income, list) else []
    }

    # 3. 💡 双重保障：如果 FMP 接口报 402 或为空，立刻无缝触发 yfinance 穿透补救
    if not packet["income"]:
        try:
            print(f"⚠️ [M7-LOG-FALLBACK] FMP income empty for [{symbol}]. Triggering yfinance gateway...")
            t_obj = yf.Ticker(symbol)
            
            q_financials = t_obj.quarterly_financials
            if q_financials is not None and not q_financials.empty:
                yf_income_list = []
                for col_date in q_financials.columns[:5]:
                    col_data = q_financials[col_date]
                    date_str = col_date.strftime("%Y-%m-%d") if hasattr(col_date, "strftime") else str(col_date)[:10]
                    
                    # 多名称全兼容字段提取（解决 yfinance 索引名称变动 BUG）
                    def get_val(keys):
                        for k in keys:
                            if k in col_data.index and not pd.isna(col_data[k]):
                                return float(col_data[k])
                        return 0.0

                    rev = get_val(["Total Revenue", "Operating Revenue", "Revenue"])
                    gp = get_val(["Gross Profit"])
                    rd = get_val(["Research And Development", "Research Development"])
                    op_inc = get_val(["Operating Income", "Operating Revenue"])
                    net_inc = get_val(["Net Income", "Net Income Common Stockholders"])
                    
                    yf_income_list.append({
                        "date": date_str,
                        "revenue": rev,
                        "grossProfit": gp,
                        "grossProfitRatio": (gp / rev) if rev > 0 else 0.0,
                        "researchAndDevelopmentExpenses": rd,
                        "operatingIncome": op_inc,
                        "netIncome": net_inc
                    })
                packet["income"] = yf_income_list
                print(f"🟢 [M7-LOG-FALLBACK] Successfully recovered {len(yf_income_list)} quarters via yfinance for [{symbol}].")
        except Exception as yf_err:
            print(f"❌ [M7-LOG-FALLBACK] yfinance fallback failed for [{symbol}]: {yf_err}")

    # 4. 只有数据有效时才落盘固化
    if packet["income"]:
        try:
            meta_bundle = {"fetched_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "packet": packet}
            with open(cache_file_path, "w", encoding="utf-8") as f:
                json.dump(meta_bundle, f, ensure_ascii=False, indent=2)
            print(f"💾 [M7-LOG-CACHE] Updated cache file for [{symbol}].")
        except Exception as e:
            print(f"⚠️ [M7-LOG-CACHE] Error saving cache: {e}")

    return packet


def run_m7_audit(ticker_symbol: str, kline_period: str = "Daily"):
    print("\n" + "⚡"*15 + f" [M7 QUANT ENGINE AUDIT START FOR {ticker_symbol}] " + "⚡"*15)
    
    # 🌟 1. Fetch Raw Packet
    raw_packet = get_m7_financial_packet_with_cache(ticker_symbol)
    
    # 🌟 2. Data Cleaning and Purifying
    purified_packet = {"companyName": "Unknown", "mcap": 0, "quarters": []}
    try:
        if raw_packet.get("profile") and len(raw_packet["profile"]) > 0:
            profile_node = raw_packet["profile"][0]
            purified_packet["companyName"] = profile_node.get("companyName", "Unknown")
            mcap_val = profile_node.get("mktCap", profile_node.get("marketCap", profile_node.get("mcap", 0)))
            purified_packet["mcap"] = mcap_val
            
            print(f"🔍 [M7-DATA-EXPLORER] Extracted Core Market Cap Probe:")
            print(f"   -> Raw mktCap: {profile_node.get('mktCap')}")
            print(f"   -> Raw marketCap: {profile_node.get('marketCap')}")
            print(f"   -> Final Purified Output mcap: {purified_packet['mcap']}")

        if raw_packet.get("income") and isinstance(raw_packet["income"], list):
            for q in raw_packet["income"]:
                purified_packet["quarters"].append({
                    "date": q.get("date"),
                    "revenue": q.get("revenue"),
                    "grossProfit": q.get("grossProfit"),
                    "grossProfitRatio": q.get("grossProfitRatio"),
                    "researchAndDevelopmentExpenses": q.get("researchAndDevelopmentExpenses"),
                    "operatingIncome": q.get("operatingIncome"),
                    "netIncome": q.get("netIncome")
                })
        print(f"\n📊 [M7-LOG-DIAGNOSTIC] Python data purifying complete. Input packet ready for LLM:")
        print(json.dumps(purified_packet, indent=2, ensure_ascii=False))
    except Exception as clean_err:
        print(f"❌ [M7-LOG-DIAGNOSTIC] Error purifying data packet: {clean_err}")

    now_time = datetime.datetime.now()
    current_date = now_time.strftime("%Y-%m-%d")

    # =====================================================================
    # 🧠 English System Instruction Guidelines
    # =====================================================================
    system_instruction = (
        f"# 🧠 M7-ALPHA NASDAQ-100 Fundamental Quant Dashboard\n\n"
        f"## 🪐 Temporal Anchor\n"
        f"Current System Date: **{current_date}**. Selected Timeframe: 【{kline_period}】.\n\n"
        f"## 🛡️ Chief Auditor Core Guidelines\n"
        f"1. **Strict Fiscal Date Lock**: Do NOT invent or alter year/reporting dates. Use exact cutoff dates provided in the data packet.\n"
        f"2. **Numeric Formatting Standard**: Completely ban raw long numbers and scientific notation. Convert all financial figures to human-readable 'Billion USD' ($B) or 'Million USD' ($M) (e.g., $81.62B).\n"
        f"3. **Complete Three-Section Output**: Output Section I, II, and III fully in English.\n"
        f"4. **Ban HTML Line Breaks**: Do NOT insert <br>, <br />, or <br/> tags inside Markdown tables.\n"
        f"5. **STRICTLY BAN LATEX / MATH FORMATTING**: Absolutely DO NOT wrap text sentences inside LaTeX math symbols (like $...$ or $$...$$). Write standard plain text directly!\n"
        f"6. **NO ITALIC FOOTNOTE WRAPPING**: DO NOT wrap entire sentences or 'Note:' paragraphs inside asterisks (e.g., *Note: ...*). Never output italicized paragraphs that cause KaTeX font squeezing bugs!\n"
        f"7. **NO HALLUCINATION ON MISSING METRICS**: If historical quarters are missing, report 'N/A' directly. Never fabricate fake numbers!\n\n"
        f"---\n"        
        f"### I. 🎯 Strategic Positioning: 【{ticker_symbol}】\n"
        f"- Macro Positioning: In a single concise sentence, state the company's calibrated market cap (in Billion/Trillion USD) and its tech sector status.\n"
        f"- Financial Cutoff: Clearly state the cutoff date of the latest financial report in the data packet.\n\n"
        f"### II. 📑 Core Income Statement Quarterly Comparison\n"
        f"Provide a clean, standardized Markdown table displaying the following 6 key financial metrics across 【Prev Quarter 2】, 【Prev Quarter 1】, 【Latest Quarter】, 【QoQ Growth (%)】, and 【YoY Growth (%)】 with absolute mathematical precision:\n"
        f"- Total Revenue\n"
        f"- Gross Profit\n"
        f"- Gross Margin (%)\n"
        f"- R&D Expenses\n"
        f"- Operating Income\n"
        f"- Net Income\n\n"
        f"### III. 🔮 Fundamental Health Assessment (3 Concise Takeaways)\n"
        f"1. Business Moat & Revenue Structure: In one sentence, evaluate whether revenue is healthy and diversified or overly dependent on a single product.\n"
        f"2. Core Anomaly & Cost Pressure: In one sentence, analyze if there are risks in R&D/OPEX expansion or gross margin compression.\n"
        f"3. Institutional Order Flow Sentiment: In one sentence, predict whether major institutional capital is likely in aggressive accumulation or defensive hedging mode."
    )

    user_task = (
        f"Here is the purified financial data packet for 【{ticker_symbol}】:\n"
        f"```json\n{json.dumps(purified_packet)}\n```\n"
        f"Please perform a complete fundamental extraction. Use the 5 quarters of data to identify the corresponding quarter from last year and compute the exact YoY Growth in the final column of the table. Complete Section I, II, and III fully in English before concluding your output."
    )
    
    # 🌟 4. Execute Invoke with Multi-Key Rotation and 429 Retry Mechanism
    response = None
    max_retries = 3

    for attempt in range(max_retries):
        selected_key = random.choice(active_google_keys)
        print(f"\n🎲 [M7-LOG-ROULETTE] Attempt {attempt + 1}/{max_retries} | Selected active Google API Key: [...{selected_key[-6:] if selected_key else 'None'}]")
        
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-3.6-flash",  # 👈 使用配额相对宽裕的模型，降低触发 429 概率
                temperature=0.01,
                google_api_key=selected_key
            )
            print("📡 [M7-LOG-LLM] Sending Invoke command to Gemini Flash pipeline...")
            response = llm.invoke([SystemMessage(content=system_instruction), HumanMessage(content=user_task)])
            print("🟢 [M7-LOG-LLM] Response received! Parsing object structure...")
            break  # 成功调取，跳出重试循环

        except Exception as err:
            err_str = str(err)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                print(f"⚠️ [M7-LOG-429] Triggered rate limit on key [...{selected_key[-6:]}]. Waiting 11 seconds for quota reset...")
                time.sleep(11)
            else:
                print(f"❌ [M7-LOG-ERROR] API call failed on attempt {attempt + 1}: {err}")
                if attempt == max_retries - 1:
                    raise err

    if not response:
        return "❌ [M7-FATAL] All API Keys exhausted or rate-limited. Please try again later."

    # 🌟 5. Parse and Clean LLM Response
    try:
        final_report = ""
        if isinstance(response, AIMessage):
            if isinstance(response.content, list):
                fragments = []
                for idx, block in enumerate(response.content, 1):
                    if isinstance(block, dict) and 'text' in block:
                        fragments.append(block['text'])
                    elif isinstance(block, str):
                        fragments.append(block)
                final_report = "".join(fragments)
            else:
                final_report = str(response.content)
        else:
            final_report = str(response)

        # 🛡️ 1. 物理剥离脏挂件
        for dirty_tag in ["', 'extras':", '", "extras":', "', extras=", '", extras=']:
            if dirty_tag in final_report:
                final_report = final_report.split(dirty_tag)[0]

        # 🚀 2. 【核心排版与 KaTeX 粘连彻底修复算子】
        import re

        # A. 物理斩断被 $ 包裹的一整句/长段英文
        final_report = re.sub(r'\$([^\$\n]+\s+[^\$\n]+)\$', r'\1', final_report)

        # B. 消除 Note: 被 * ... * 或 _ ... _ 强行包裹造成的全段斜体粘连
        final_report = re.sub(r'\*+\s*(Note:[^*]+)\*+', r'\1', final_report)
        final_report = re.sub(r'_\s*(Note:[^_]+)_', r'\1', final_report)

        # C. 精准修复因 KaTeX 遗留导致常见财报指标发生的单词粘连
        sticky_financial_words = {
            "GrossProfit": "Gross Profit",
            "GrossMargin": "Gross Margin",
            "OperatingIncome": "Operating Income",
            "NetIncome": "Net Income",
            "TotalRevenue": "Total Revenue",
            "OperatingLeverage": "Operating Leverage",
            "ResearchAndDevelopment": "Research & Development",
            "operatingleverage": "operating leverage",
            "costpressure": "cost pressure"
        }
        for bad_word, clean_word in sticky_financial_words.items():
            final_report = final_report.replace(bad_word, clean_word)

        # D. 替换字面量换行符
        final_report = final_report.replace("\\n", "\n")

        print("="*40 + " 🏁 M7 QUANT ENGINE AUDIT END " + "="*40 + "\n")
        return final_report
        
    except Exception as e:
        print("\n❌ [M7-LOG-CRASH] Fatal exception in audit engine execution!")
        traceback.print_exc()
        return f"❌ Fundamental AI Audit Engine Execution Error: {e}"

if __name__ == "__main__":
    res = run_m7_audit("CRWD", "Daily")
    print(res)