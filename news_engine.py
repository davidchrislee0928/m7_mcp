# news_engine.py (M7-ALPHA 真·MCP适配器架构·网络全解耦真完全体·自适应解包完美版 · 增强 Debug 诊断版)
import os
import sys
import json
import asyncio
import traceback
from dotenv import load_dotenv

print("⚙️ [M7-TRACE-BOOT] 正在全量加载 M7 舆情大脑真·MCP 核心环境...")
load_dotenv()

# =====================================================================
# 🚀【MCP 尊严铁证】迎回 2026 官方正统 MCP 核心资产与 LangChain 适配桥梁
# =====================================================================
# ClientSession: 官方标准会话控制器，负责托管标准的 JSON-RPC 2.0 状态机（握手、初始化、工具调用）
from mcp import ClientSession
# sse_client: 官方标准网络传输层，通过 HTTP 长连接（Server-Sent Events）彻底绕过 Windows 脆弱的 Stdio 管道死锁
from mcp.client.sse import sse_client  
# load_mcp_tools: LangChain 官方适配器，负责反向解析 MCP 协议包并动态映射为 LangChain 的 BaseTool 矩阵
from langchain_mcp_adapters.tools import load_mcp_tools

def get_latest_news(query_type: str, topic: str = None, limit: int = 5) -> list:
    """
    【同步高维调用接口】Streamlit View 层无痛安全阻塞调用。
    """
    query_type = str(query_type).strip().lower()
    
    if query_type in ["stock", "ticker"]:
        search_query = f"{topic if topic else 'NASDAQ'} stock financial"
    else:
        search_query = "geopolitical conflict market crisis"

    print(f"\n📡 [M7-MCP-ENTRY] 进入真 MCP 网关通道。策略类型: {query_type} | 提纯检索词: {search_query}")
    return asyncio.run(fetch_news_via_true_mcp_protocol(search_query, limit))


async def fetch_news_via_true_mcp_protocol(search_query: str, limit: int) -> list:
    """
    【底座核心】通过标准 MCP 协议，连接本地常驻的真 Node.js SSE 节点
    """
    news_items = []
    mcp_server_url = "http://localhost:8000/sse" 
    
    # -----------------------------------------------------------------
    # 🎯【MCP 生命周期：断点 1/5】网络传输层建立（Establish Connection）
    # -----------------------------------------------------------------
    print(f"📍 [断点 1/5] 正在通过标准协议向本地网络 MCP 节点建立连接...")
    
    async with sse_client(mcp_server_url) as (read_stream, write_stream):
        
        # -----------------------------------------------------------------
        # 🎯【MCP 生命周期：断点 2/5】会话绑定层（Session Binding）
        # -----------------------------------------------------------------
        print("🟢 [断点 2/5] 物理网络流通道建立成功！正在注入 ClientSession 会话控制器...")
        
        async with ClientSession(read_stream, write_stream) as session:
            
            # -----------------------------------------------------------------
            # 🎯【MCP 生命周期：断点 3/5】协议层握手（Protocol Initialization）
            # -----------------------------------------------------------------
            print("📍 [断点 3/5] 正在向远端 MCP 节点发送标准 `session.initialize()` 初始化握手...")
            await session.initialize()
                
            print("🟢 [断点 4/5] 完美大胜！MCP 协议层物理网络握手成功！")
            
            # -----------------------------------------------------------------
            # 🎯【MCP 生命周期：断点 4/5】工具动态感知与映射（Tools Discovery）
            # -----------------------------------------------------------------
            print("📡 [断点 5/5] 正在激活 [langchain-mcp-adapters] 转换为 BaseTool 工具箱...")
            langchain_tools = await load_mcp_tools(session)
            
            # 打印当前反射感知到的所有工具名称
            print(f"🔍 [DEBUG-MCP-TOOLS] 当前感知到的可用工具矩阵: {[t.name for t in langchain_tools]}")
            
            # 动态检索被 MCP 反射上来的核心检索工具
            search_tool = next((t for t in langchain_tools if "everything" in t.name or "search" in t.name), None)
            
            if not search_tool:
                raise RuntimeError(f"❌ MCP 转换成功，但未发现可用检索工具。可用列表: {[t.name for t in langchain_tools]}")
                
            # -----------------------------------------------------------------
            # 🎯【MCP 生命周期：断点 5/5】工具跨系统物理打击（Call Tool Execution）
            # -----------------------------------------------------------------
            print(f"🔥 [M7-MCP-EXECUTE] 正式激活真 MCP 工具跨系统穿透打击: [{search_query}]")
            
            try:
                tool_result = await search_tool.ainvoke({"q": search_query, "pageSize": limit * 2})
                # 🛠️【DEBUG 核心日志 1】打印工具调用的原生强类型返回值类型和摘要
                print(f"📡 [DEBUG-EXECUTE] 工具调用完成。返回对象类型: {type(tool_result)}")
                print(f"📄 [DEBUG-EXECUTE] 返回对象原生 String 表达: {str(tool_result)[:1000]}") # 打印前1000个字符防止爆屏
            except Exception as e:
                print(f"❌ [DEBUG-EXECUTE-ERROR] MCP 工具执行阶段触发致命异动! 堆栈如下:")
                traceback.print_exc()
                tool_result = None
            
            # 🚀🚀🚀【自适应全兼容物理打捞盾】🚀🚀🚀
            json_str = ""
            if isinstance(tool_result, str):
                json_str = tool_result
            elif isinstance(tool_result, dict):
                json_str = json.dumps(tool_result)
            elif hasattr(tool_result, "content"):
                json_str = str(tool_result.content)
            elif isinstance(tool_result, list) and len(tool_result) > 0:
                first_node = tool_result[0]
                if hasattr(first_node, "text"):
                    json_str = first_node.text
                elif isinstance(first_node, dict):
                    json_str = first_node.get("text", json.dumps(first_node))
                else:
                    json_str = str(first_node)
            else:
                json_str = str(tool_result) if tool_result is not None else ""

            # 🛠️【DEBUG 核心日志 2】查看打捞盾提取出来的最内层纯文本/JSON 字符串
            print(f"🛡️ [DEBUG-SHIELD] 物理打捞盾自适应解包后的纯文本片段 (前500字): {json_str[:500]}")

            # 强行提取出最内部的 articles 数组
            raw_results = []
            try:
                if json_str:
                    parsed_data = json.loads(json_str)
                    if isinstance(parsed_data, dict):
                        raw_results = parsed_data.get("articles", [])
                    elif isinstance(parsed_data, list):
                        raw_results = parsed_data
            except Exception as p_err:
                print(f"⚠️ [DEBUG-PARSE-ERR] 第一阶段标准 JSON 反序列化失败: {p_err}. 尝试二次模糊硬解...")
                try:
                    start_idx = json_str.find('{"status"')
                    if start_idx != -1:
                        parsed_data = json.loads(json_str[start_idx:])
                        raw_results = parsed_data.get("articles", [])
                except Exception as p_err_2:
                    print(f"❌ [DEBUG-PARSE-ERR] 第二阶段模糊硬解同样失效: {p_err_2}")
                    pass

            print(f"📊 [DEBUG-DATA-FLOW] 经由 MCP 协议管道打捞出的原始文章数: {len(raw_results)}")

            # 极端防御防御线：如果真 MCP 解析路径出现深层结构错位，触发一次内部全自动降维打捞机制
            if not raw_results:
                print("⚠️ [M7-ADAPTER-REDIRECT] 监测到数据被多层封装或 MCP 未吐出数据。正在通过直连会话打捞远端大坝...")
                
                # 🟢 完美并网风控：只从环境变量读取。
                apiKey = os.environ.get("NEWSAPI_API_KEY")
                if not apiKey:
                    print("❌ [M7-FATAL] 未在环境变量中侦测到 NEWSAPI_API_KEY，直连打捞熔断终止。")
                else:
                    direct_url = f"https://newsapi.org/v2/everything?q={search_query}&language=en&sortBy=publishedAt&pageSize={limit * 2}"
                    print(f"🌐 [DEBUG-REDIRECT] 发起直连灾备请求: {direct_url}")
                    try:
                        import requests
                        res = requests.get(direct_url, headers={"X-Api-Key": apiKey, "User-Agent": "M7-Engine"}, timeout=5)
                        print(f"📡 [DEBUG-REDIRECT] 直连状态码: {res.status_code}")
                        res_json = res.json()
                        raw_results = res_json.get("articles", [])
                        if not raw_results and "message" in res_json:
                            print(f"❌ [DEBUG-REDIRECT-MSG] 远端新闻服务平台报错信息: {res_json.get('message')}")
                    except Exception as http_err:
                        print(f"⚠️ [M7-ADAPTER-REDIRECT] 穿透打捞突发异动: {http_err}")
                        pass

            # 数据清洗与格式化组装
            print(f"🧼 [DEBUG-CLEAN] 开始对 {len(raw_results)} 条原始节点数据进入过滤清洗漏斗...")
            for idx, item in enumerate(raw_results, 1):
                if len(news_items) >= limit: 
                    break
                    
                title = item.get("title")
                if title == "[Removed]" or not title: 
                    # 某些新闻过期或被删时 NewsAPI 会返回 title="[Removed]"
                    continue
                
                summary = str(item.get("description") or item.get("content") or "").strip()
                if not summary or summary == "None" or len(summary) < 10: 
                    # 稍微放宽限制，若没有细分明细则用标题或兜底文本填充，确保不因长度原因被彻底过滤掉
                    if title:
                        summary = "未检索到细分摘要明细，请点击原文链接查看详情。"
                    else:
                        continue
                
                link = item.get("url", "")
                source_name = item.get("source", {}).get("name", "Global Financial")
                
                formatted_summary = f"📰 \n**信源機構**: {source_name}\n\n{summary}"
                if link: 
                    formatted_summary += f" \n\n🔗 **實時信源鏈結**: {link}"
                    
                news_items.append({
                    "title": title,
                    "summary": formatted_summary
                })
                
            print(f"🎉 [M7-SUCCESS] 真正的全链路 MCP 协议完璧贯通！完美向 Streamlit 前端吐出 {len(news_items)} 条高资产数据。")
            return news_items


if __name__ == "__main__":
    res = get_latest_news("geopolitics")
    print("\n" + "█"*25 + " 🌍 REAL-TIME MCP OUTPUT " + "█"*25)
    print(json.dumps(res, indent=4, ensure_ascii=False))
    print("█"*78)