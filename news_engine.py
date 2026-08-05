# news_engine.py (M7-ALPHA 真·MCP适配器架构·动态 NASDAQ 100 主权词矩阵同步版)
import os
import sys
import json
import asyncio
import re
import requests
import traceback
from bs4 import BeautifulSoup
from dotenv import load_dotenv

print("\n" + "█"*60)
print("⚙️ [M7-TRACE-BOOT] 正在全量加载 M7 舆情大脑真·MCP 核心环境...")
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, ".env"))
load_dotenv()

RAW_ENV_KEY = os.environ.get("NEWSAPI_API_KEY")
if RAW_ENV_KEY is None:
    print("🚨 [M7-DEBUG-KEY] 核心警报：系统环境变量中完全找不到 NEWSAPI_API_KEY！")
    ENV_KEY_CLEAN = ""
else:
    ENV_KEY_CLEAN = RAW_ENV_KEY.strip('"' + "'").strip()
    print(f"🟢 [M7-ENV-SUCCESS] Python 侧 Key 资产清洗封盘成功: [{ENV_KEY_CLEAN[:5]}***] (长度: {len(ENV_KEY_CLEAN)})")
print("█"*60 + "\n")

from mcp import ClientSession
from mcp.client.sse import sse_client  
from langchain_mcp_adapters.tools import load_mcp_tools

# =====================================================================
# 🌐 动态 NASDAQ 100 成分股打捞与别名构建矩阵 (对齐 app.py)
# =====================================================================
def get_dynamic_nasdaq_100_map() -> dict:
    """
    抓取 Slickcharts 最新 NASDAQ 100 列表并构建（Ticker -> 公司名/别名检索表达式）字典
    """
    nasdaq_map = {}
    blacklist = []  # 保持黑名单为空，包含 SPCX 等所有公开标的
    
    url = "https://www.slickcharts.com/nasdaq100"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            rows = soup.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 3:
                    comp_name = cols[1].text.strip()
                    symbol = cols[2].text.strip().upper()
                    
                    if symbol and symbol not in blacklist and (symbol.isalpha() or "-" in symbol):
                        clean_name = re.sub(r'\b(Inc\.?|Corp\.?|Corporation|Ltd\.?|Co\.?|Class A|Class C|Common Stock)\b', '', comp_name, flags=re.I).strip()
                        if clean_name and clean_name != symbol:
                            nasdaq_map[symbol] = f'("{symbol}" OR "{clean_name}" OR "{comp_name}")'
                        else:
                            nasdaq_map[symbol] = f'("{symbol}")'
    except Exception as e:
        print(f"⚠️ [M7-LOG-WARN] Slickcharts 动态映射打捞超时，启用高权重静态兜底: {e}")

    # 🚀 核心权重与 SPCX (SpaceX) 专属别名保护规则
    core_overrides = {
        "SPCX": '("SPCX" OR "SpaceX" OR "Space Exploration Technologies" OR "Starlink" OR "Elon Musk")',
        "GOOGL": '("GOOGL" OR "Alphabet" OR "Google")',
        "GOOG": '("GOOG" OR "Alphabet" OR "Google")',
        "NVDA": '("NVDA" OR "NVIDIA" OR "Jensen Huang")',
        "AAPL": '("AAPL" OR "Apple Inc" OR "iPhone" OR "Tim Cook")',
        "MSFT": '("MSFT" OR "Microsoft" OR "Satya Nadella")',
        "AMZN": '("AMZN" OR "Amazon" OR "Jeff Bezos")',
        "META": '("META" OR "Meta Platforms" OR "Mark Zuckerberg" OR "Facebook")',
        "TSLA": '("TSLA" OR "Tesla" OR "Elon Musk" OR "Gigafactory")',
        "INTC": '("INTC" OR "Intel" OR "Pat Gelsinger")',
        "AMD": '("AMD" OR "Advanced Micro Devices" OR "Lisa Su")',
    }
    nasdaq_map.update(core_overrides)
    return nasdaq_map

def get_latest_news(query_type: str, topic: str = None, limit: int = 7) -> list:
    """
    【同步高维调用接口】Streamlit View 层无痛安全阻塞调用。
    """
    query_type = str(query_type).strip().lower()
    
    if query_type in ["stock", "ticker"] and topic:
        ticker = str(topic).strip().upper()
        
        # 🎯 动态获取与 app.py 对齐的全量成分股映射矩阵
        nasdaq_company_map = get_dynamic_nasdaq_100_map()
        company_lock = nasdaq_company_map.get(ticker, f'("{ticker}")')
        
        search_query = f'{company_lock} AND (financing OR funding OR "pre-market" OR breaking OR earnings OR "private placement" OR dilution OR slump OR crash)'
        
    elif query_type in ["stock", "ticker"] and not topic:
        search_query = 'breaking AND (NASDAQ OR "stock market" OR financial)'
    else:
        search_query = 'geopolitics AND (conflict OR shock OR risk OR energy OR breaking)'

    print(f"\n📡 [M7-MCP-ENTRY] 进入真 MCP 网关通道。策略类型: {query_type} | 动态成分股死锁检索词: [{search_query}]")
    return asyncio.run(fetch_news_via_true_mcp_protocol(search_query, limit, query_type, topic))

async def fetch_news_via_true_mcp_protocol(search_query: str, limit: int, query_type: str, topic: str = None) -> list:
    news_items = []
    mcp_server_url = "http://localhost:8000/sse" 
    raw_results = []
    
    try:
        async with sse_client(mcp_server_url) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                langchain_tools = await load_mcp_tools(session)
                search_tool = next((t for t in langchain_tools if "everything" in t.name or "search" in t.name), None)
                if not search_tool:
                    raise RuntimeError("❌ 关键性阻断：远端 Node.js 节点上未感知到有效的检索工具声明！")
                    
                print(f"🔥 [M7-MCP-EXECUTE] 正式激活真 MCP 工具跨系统穿透打击 -> 检索词: [{search_query}]")
                
                tool_result = await search_tool.ainvoke({
                    "q": search_query, 
                    "pageSize": max(limit * 3, 25),
                    "apiKey": ENV_KEY_CLEAN
                })
                
                json_str = ""
                if isinstance(tool_result, str): json_str = tool_result
                elif isinstance(tool_result, dict): json_str = json.dumps(tool_result)
                elif hasattr(tool_result, "content"): json_str = str(tool_result.content)
                elif isinstance(tool_result, list) and len(tool_result) > 0:
                    first_node = tool_result[0]
                    json_str = first_node.text if hasattr(first_node, "text") else (first_node.get("text", json.dumps(first_node)) if isinstance(first_node, dict) else str(first_node))
                
                if json_str:
                    parsed_data = json.loads(json_str)
                    if isinstance(parsed_data, dict) and parsed_data.get("status") == "error":
                        print(f"❌ [M7-MCP-REMOTE-ERR] Node 侧透传的 NewsAPI 官方报错!! 原因: {parsed_data.get('message')}")
                    if isinstance(parsed_data, dict):
                        raw_results = parsed_data.get("articles", [])
                    elif isinstance(parsed_data, list):
                        raw_results = parsed_data
                        
                print(f"📊 [DEBUG-DATA-FLOW] MCP 协议通道处理完毕，成功获取原始文章数: {len(raw_results)}")

    except Exception as mcp_fatal_err:
        print("\n" + "🛑"*15 + " M7-MCP 物理链路崩溃深度诊断堆栈 " + "🛑"*15)
        traceback.print_exc()
        print("🛑"*45 + "\n")
        
        return [{
            "title": f"🚨 [M7-MCP 物理故障大坝拦截]: {type(mcp_fatal_err).__name__}",
            "summary": f"**报告长官：MCP 核心链路点火失败。** <br/><br/>**物理报错原因:** `{mcp_fatal_err}`",
            "source_name": "M7-Kernel-Error",
            "url": "",
            "publishedAt": "CORE-BREAKDOWN"
        }]

    # =====================================================================
    # 🧼 第三层：主权数据过滤清洗漏斗
    # =====================================================================
    seen_titles = set()
    priority_pool = []  # 🚀 主权置顶池
    normal_pool = []    # 正常时间线池
    
    match_keywords = []
    if query_type in ["stock", "ticker"] and topic:
        t_upper = str(topic).strip().upper()
        match_keywords.append(t_upper)
        
        # 针对 SPCX 及核心大股增加特异性别名映射
        if t_upper == "SPCX": match_keywords.extend(["SPACEX", "STARLINK"])
        elif t_upper in ["GOOGL", "GOOG", "ALPHABET"]: match_keywords.extend(["GOOGLE", "ALPHABET"])
        elif t_upper in ["NVDA", "NVIDIA"]: match_keywords.extend(["NVIDIA", "JENSEN"])
        elif t_upper in ["AAPL", "APPLE"]: match_keywords.extend(["APPLE", "IPHONE"])
        elif t_upper in ["MSFT", "MICROSOFT"]: match_keywords.append("MICROSOFT")
        elif t_upper in ["AMZN", "AMAZON"]: match_keywords.append("AMAZON")
        elif t_upper in ["INTC", "INTEL"]: match_keywords.append("INTEL")
        elif t_upper in ["AMD"]: match_keywords.append("AMD")
        else:
            friendly_name = t_upper.title()
            if len(friendly_name) > 2: match_keywords.append(friendly_name)

    # 分流打捞清洗
    for item in raw_results:
        title = item.get("title")
        if title == "[Removed]" or not title: 
            continue
        
        title_clean = str(title).strip()
        if title_clean in seen_titles: 
            continue
        
        summary = str(item.get("description") or item.get("content") or "").strip()
        if not summary or summary == "None" or len(summary) < 10:
            summary = "未检索到细分摘要明细，请点击原文链接查看详情。"
        
        link = item.get("url", "")
        source_name = item.get("source", {}).get("name", "Global Financial")
        published_at = item.get("publishedAt", "2026-06-02 12:00")
        
        seen_titles.add(title_clean)
        
        news_packet = {
            "title": title_clean,
            "summary": summary, 
            "source_name": source_name,
            "url": link,  
            "publishedAt": published_at
        }
        
        title_upper = title_clean.upper()
        is_target_headline = any(kw in title_upper for kw in match_keywords) if match_keywords else False
        
        if is_target_headline:
            priority_pool.append(news_packet)
        else:
            normal_pool.append(news_packet)
            
    # 大坝并网组装
    if priority_pool:
        news_items.append(priority_pool.pop(0))
        print(f"🎯 [M7-FILTER-ACTIVE] 成功捕获并置顶主权标题头条: {news_items[0]['title'][:40]}...")
        
    remaining_pool = priority_pool + normal_pool
    for item in remaining_pool:
        if len(news_items) >= limit: 
            break
        news_items.append(item)
        
    print(f"🎉 [M7-SUCCESS] 最终向 Streamlit 输出真实舆情条数: {len(news_items)} (动态主权锁定完成)\n")
    return news_items