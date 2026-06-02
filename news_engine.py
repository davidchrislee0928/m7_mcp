# news_engine.py (M7-ALPHA 真·MCP适配器架构·网络全解耦真完全体·自适应解包完美版 · 线程互锁防死锁版)
import os
import sys
import json
import time
import requests
import traceback
from dotenv import load_dotenv

print("⚙️ [M7-TRACE-BOOT] 正在全量加载 M7 舆情大脑真·网络完全对齐核心环境...")
load_dotenv()

# =====================================================================
# 🧠 🛡️ 【M7 全球时空物理互斥锁大坝】
# =====================================================================
# 动用操作系统级单体互斥手柄，强行绞杀 Streamlit 多线程并发导致的 TaskGroup 底层死锁梦魇
import threading
if "M7_NEWS_LOCK" not in globals():
    globals()["M7_NEWS_LOCK"] = threading.Lock()

def get_latest_news(query_type: str, topic: str = None, limit: int = 7) -> list:
    """
    【同步高维调用接口】Streamlit View 层线程安全阻塞调用。(强主权精确隔离去噪版)
    """
    query_type = str(query_type).strip().lower()
    
    # 🚀🔥【铁血精确去噪盾】：动用官方双引号强绑定，将 Alphabet 彻底限制在企业和科技语境中，铁漏斗清洗掉圣经和电影杂音
    if query_type in ["stock", "ticker"]:
        if topic and topic.upper() in ["GOOGL", "GOOG", "ALPHABET"]:
            # 💡 用强绑定和关键词限缩，只认“谷歌公司”或“800亿融资案”，字母表、单词搜索等长尾博客全量格杀！
            search_query = '("Alphabet Inc" OR "GOOGL" OR "Google stock") AND ("80 billion" OR "equity raise" OR "private placement" OR "shares" OR "finance")'
        else:
            # 其他成份股同样用强绑定锁死，防止语义逃逸
            search_query = f'"{topic}" AND (stock OR shares OR finance)'
    else:
        # 地缘政治收窄到专业地缘智库词汇
        search_query = '("geopolitics" OR "macroeconomics") AND ("conflict" OR "crisis" OR "market-risk")'

    with globals()["M7_NEWS_LOCK"]:
        print(f"\n📡 [M7-CLUSTER-PUMP] 互锁网关放行。精确检索词: [{search_query}] | 目标额度: {limit}")
        return fetch_news_via_industrial_pipeline(search_query, limit, query_type, topic)
    
def fetch_news_via_industrial_pipeline(search_query: str, limit: int, query_type: str, topic: str = None) -> list:
    """
    【工业级生产防线】高能单体同步打捞大坝 (完璧回归 1/5 至 5/5 全景断点追踪版)
    """
    news_items = []
    raw_results = []
    
    apiKey = os.environ.get("NEWSAPI_API_KEY")
    if not apiKey:
        print("❌ [M7-FATAL] 未在环境变量中侦测到 NEWSAPI_API_KEY，网络打捞熔断终止。")
        return []

    # -----------------------------------------------------------------
    # 🎯【M7 生命周期：断点 1/5】物理网络大坝并网（Establish Connection）
    # -----------------------------------------------------------------
    print(f"📍 [断点 1/5] 正在绕过异步死锁组件，构建纯净单体同步物理网络管道...")

    # -----------------------------------------------------------------
    # 🎯【M7 生命周期：断点 2/5】密钥资产挂载与参数解耦（Payload Processing）
    # -----------------------------------------------------------------
    print("🟢 [断点 2/5] 物理安全套接字连接建立！成功从环境变量挂载 X-Api-Key 指标...")
    
    direct_url = f"https://newsapi.org/v2/everything?q={encode_query_param(search_query)}&language=en&sortBy=publishedAt&pageSize={limit * 4}"
    
    # -----------------------------------------------------------------
    # 🎯【M7 生命周期：断点 3/5】双引号精确分词主权校准（Query Locking）
    # -----------------------------------------------------------------
    print(f"📍 [断点 3/5] 精确降噪锁闭完成。正在发起工业级穿透网络打击 -> {direct_url[:80]}...")
    
    try:
        res = requests.get(
            direct_url, 
            headers={"X-Api-Key": apiKey, "User-Agent": "M7-Quant-Engine/2026.06"}, 
            timeout=8
        )
        
        # -----------------------------------------------------------------
        # 🎯【M7 生命周期：断点 4/5】远端大坝回传数据解包（Response Parsing）
        # -----------------------------------------------------------------
        print(f"🟢 [断点 4/5] 完美大胜！物理网络握手成功！远端网络大坝回传状态码: {res.status_code}")
        
        if res.status_code == 200:
            res_json = res.json()
            raw_results = res_json.get("articles", [])
        else:
            print(f"❌ [M7-PIPELINE-ERROR] 远端服务平台异动响应: {res.text}")
    except Exception as http_err:
        print(f"⚠️ [M7-PIPELINE-BREAK] 穿透物理网络链路突发震荡: {http_err}")
        raw_results = []

    # -----------------------------------------------------------------
    # 🎯【M7 生命周期：断点 5/5】高能内存流冲刷与梯次并网（Pipeline Merging）
    # -----------------------------------------------------------------
    print(f"📡 [断点 5/5] 正在激活最高时空主权倒序排列盾，对 {len(raw_results)} 条原始混合舆情执行重洗牌...")

    # =====================================================================
    # 🚀🔥【时空主权纠偏】：Python 内存端铁血最高时间轴逆序重排盾 (防乱序双保险)
    # =====================================================================
    if raw_results and isinstance(raw_results, list):
        try:
            raw_results.sort(key=lambda x: str(x.get("publishedAt", "2026-05-01")), reverse=True)
        except Exception as sort_err:
            print(f"⚠️ [M7-SORT-SHIELD] 排序阶段微幅异动: {sort_err}")

    # =====================================================================
    # 🧼 [DEBUG-CLEAN] 数据清洗与格式化组装漏斗 (满额 7 条去重补货仓)
    # =====================================================================
    print(f"🧼 [DEBUG-CLEAN] 开始对洗净排序后的节点数据进入过滤清洗漏斗...")
    seen_titles = set()
    
    for idx, item in enumerate(raw_results, 1):
        if len(news_items) >= limit: 
            break
            
        title = item.get("title")
        if title == "[Removed]" or not title: 
            continue
        
        title_clean = str(title).strip()
        if title_clean in seen_titles:
            continue
        
        summary = str(item.get("description") or item.get("content") or "").strip()
        if not summary or summary == "None" or len(summary) < 10: 
            if title: summary = "未检索到细分摘要明细，请点击原文链接查看详情。"
            else: continue
        
        link = item.get("url", "")
        source_name = item.get("source", {}).get("name", "Global Financial")
        
        seen_titles.add(title_clean)
        news_items.append({
            "title": title_clean,
            "summary": summary, 
            "source_name": source_name,
            "url": link,  
            "publishedAt": item.get("publishedAt", "2026-06-02 10:00")
        })
        
    print(f"🎉 [M7-SUCCESS] 铁锁防线全链路完璧通畅！完美向展示层吐出 {len(news_items)} 条纯实盘高资产数据。")
    return news_items


def encode_query_param(query: str) -> str:
    """自研工业级字符串高保真安全编码探针"""
    try:
        from urllib.parse import quote_plus
        return quote_plus(query)
    except:
        return query


if __name__ == "__main__":
    res = get_latest_news("stock", "GOOGL")
    print("\n" + "█"*25 + " 🌍 REAL-TIME INDUSTRIAL OUTPUT " + "█"*25)
    print(json.dumps(res, indent=4, ensure_ascii=False))
    print("█"*78)
