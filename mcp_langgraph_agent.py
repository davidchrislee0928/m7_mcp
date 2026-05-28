# mcp_langgraph_agent.py (FMP直连·4大Key阵列轮询·Pro-Latest硬核换脑·全断点日志肉眼追踪版)
import os
import sys
import time
import json
import random
import datetime
import requests
import traceback  
from dotenv import load_dotenv

load_dotenv()

print("\n" + "█"*40 + " 🖥️ M7 QUANT ENGINE INITIALIZATION " + "█"*40)

# 📌 1. FMP 环境密钥硬风控
FMP_API_KEY = os.environ.get("FMP_API_KEY")
if not FMP_API_KEY:
    print("❌ [M7-FATAL] 审计长官熔断：未在环境配置文件(.env)中发现 [FMP_API_KEY]！")
    sys.exit(1)
print(f"🟢 [M7-INIT] 成功加载 FMP 财务网关密钥: [...{FMP_API_KEY[-6:] if len(FMP_API_KEY)>6 else 'VALID'}]")

# 📌 2. 恢复【铁血多 Key 轮流化缘池】
# =====================================================================
# 📌 2. 铁血多 Key 轮流化缘池（高精清洗并网版）
# =====================================================================
API_KEY_POOL = [
    os.environ.get("GOOGLE_API_KEY1"),
    os.environ.get("GOOGLE_API_KEY2"),
    os.environ.get("GOOGLE_API_KEY3"),
    os.environ.get("GOOGLE_API_KEY4"),
    os.environ.get("GOOGLE_API_KEY"), 
]

# 🔥 铁血强洗：不仅过滤 None，还要剔除空字符串、前后空格、以及任何带引号的脏文本
active_google_keys = []
for k in API_KEY_POOL:
    if k:
        clean_k = str(k).strip().replace('"', '').replace("'", "")
        # 强制剔除常见的云端死锁空值占位符
        if clean_k and clean_k.upper() != "NONE" and clean_k != "":
            active_google_keys.append(clean_k)

if not active_google_keys:
    print("❌ [M7-FATAL] 审计长官熔断：未在环境配置文件中发现任何有效的 GOOGLE_API_KEY！")
    sys.exit(1)

print(f"🟢 [M7-INIT] 成功激活 Gemini 大脑轮询阵列。当前去噪后的有效密钥弹药量: {len(active_google_keys)} 发。")

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

CACHE_DIR = os.path.dirname(os.path.abspath(__file__))

# =====================================================================
# ⚙️ 核心一阶数据打捞：对齐 FMP 官方 2026 最新标准 Query 参数通道
# =====================================================================
def get_company_info_fmp(symbol: str) -> list:
    url = f"https://financialmodelingprep.com/stable/profile?symbol={symbol.upper()}&apikey={FMP_API_KEY}"
    print(f"📡 [M7-LOG-HTTP] 正在物理请求 FMP 公司简况端点 URL: {url.split('apikey=')[0]}apikey=***")
    try:
        res = requests.get(url, timeout=12)
        print(f"📡 [M7-LOG-HTTP] 公司简况端点返回状态码: {res.status_code}")
        if res.status_code == 200:
            res_json = res.json()
            print(f"📡 [M7-LOG-HTTP] 成功打捞公司简况，记录数: {len(res_json)}")
            return res_json
        return []
    except Exception as e:
        print(f"❌ [M7-LOG-ERROR] FMP公司简介网络异动: {e}")
        return []

def get_income_statement_fmp(symbol: str) -> list:
    url = f"https://financialmodelingprep.com/stable/income-statement?symbol={symbol.upper()}&period=quarter&limit=5&apikey={FMP_API_KEY}"
    print(f"📡 [M7-LOG-HTTP] 正在物理请求 FMP 5季度利润表端点 URL: {url.split('apikey=')[0]}apikey=***")
    try:
        res = requests.get(url, timeout=12)
        print(f"📡 [M7-LOG-HTTP] 利润表端点返回状态码: {res.status_code}")
        if res.status_code == 200:
            res_json = res.json()
            print(f"📡 [M7-LOG-HTTP] 成功打捞季度利润表，记录数: {len(res_json)}")
            return res_json
        return []
    except Exception as e:
        print(f"❌ [M7-LOG-ERROR] FMP利润表网络异动: {e}")
        return []


# =====================================================================
# 💾 二阶持久化缓存盾牌
# =====================================================================
def get_m7_financial_packet_with_cache(symbol: str) -> dict:
    symbol = symbol.upper().strip()
    cache_file_path = os.path.join(CACHE_DIR, f"fmp_cache_{symbol}.json")
    
    if os.path.exists(cache_file_path):
        try:
            with open(cache_file_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            cache_time_str = cache_data.get("fetched_at", "")
            cache_time = datetime.datetime.strptime(cache_time_str, "%Y-%m-%d %H:%M:%S")
            time_diff = datetime.datetime.now() - cache_time
            
            if time_diff.days < 1:
                print(f"🟢 [M7-LOG-CACHE] 物理命中本地持久化缓存盾牌！标的: [{symbol}]，本地缓存生成时间为: {cache_time_str}")
                return cache_data["packet"]
        except Exception as e:
            print(f"⚠️ [M7-LOG-CACHE] 读取本地缓存异动: {e}")

    print(f"📡 [M7-LOG-GATEWAY] 缓存未命中/过期，强行穿透物理大坝向 FMP 索要新周期数据...")
    packet = {
        "profile": get_company_info_fmp(symbol),
        "income": get_income_statement_fmp(symbol)
    }
    try:
        meta_bundle = {"fetched_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "packet": packet}
        with open(cache_file_path, "w", encoding="utf-8") as f:
            json.dump(meta_bundle, f, ensure_ascii=False, indent=2)
        print(f"💾 [M7-LOG-CACHE] 5季度核心账目固化封盘成功。本地文件已更新。")
    except Exception as e:
        print(f"⚠️ [M7-LOG-CACHE] 固化本地缓存失败: {e}")
    return packet


def run_m7_audit(ticker_symbol: str, kline_period: str = "日K"):
    print("\n" + "⚡"*15 + f" [M7 QUANT ENGINE POINTCUT START FOR {ticker_symbol}] " + "⚡"*15)
    
    # 🌟 1. 提取原始数据包
    raw_packet = get_m7_financial_packet_with_cache(ticker_symbol)
    
    # 🌟 2. 核心去噪过滤瘦身，并在控制台强力打印数据校验
    purified_packet = {"companyName": "Unknown", "mcap": 0, "quarters": []}
    try:
        # 🟢 修改后的完璧对齐代码
        if raw_packet.get("profile") and len(raw_packet["profile"]) > 0:
            profile_node = raw_packet["profile"][0]
            purified_packet["companyName"] = profile_node.get("companyName", "Unknown")
            
            # 🔥 FMP 官方规范字段是 mktCap，这里进行兼容性打捞
            purified_packet["mcap"] = profile_node.get("mktCap", profile_node.get("mcap", 0))
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
        print(f"📊 [M7-LOG-DIAGNOSTIC] Python清洗完毕。即将投喂给大模型的纯净季度财务节点明细:")
        print(json.dumps(purified_packet, indent=2, ensure_ascii=False))
    except Exception as clean_err:
        print(f"❌ [M7-LOG-DIAGNOSTIC] 提炼数据发生异常: {clean_err}")

    # 🌟 3. 随机抽取化缘密钥
    selected_key = random.choice(active_google_keys)
    print(f"🎲 [M7-LOG-ROULETTE] 阵列抽取活弹密钥通道: [...{selected_key[-6:] if selected_key else 'None'}]")
    
    # 🌟 🌟 🌟 【精准纠偏：修正官方放行真名 gemini-1.5-pro-latest】 🌟 🌟 🌟
    # 解决 404 找不到模型的报错死穴，同时物理抹除 max_tokens 限制，彻底解放生成极限
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash", 
        temperature=0.01,
        google_api_key=selected_key
    )
    
    # 🟢 修改后的动态对齐新代码
    # 获取当前最新的绝对时间
    now_time = datetime.datetime.now()
    current_date_cn = now_time.strftime("%Y年%m月%d日")
    current_date = now_time.strftime("%Y-%m-%d")

    system_instruction = (
        f"# 🧠 M7-ALPHA 纳斯达克100成份股·基本面极简量化看板\n\n"
        f"## 🪐 时空锚定\n"
        f"当前真实时间是：**{current_date_cn}** (系统日期：{current_date})。看盘周期为：【{kline_period}】。\n\n"
        f"## 🛡️ 首席审计官三大硬核铁律\n"
        f"1. **禁止脑补修改年份**：必须如实呈现一句话原始数据中的具体截止日期（例如 NVDA 对应的 2025-10-26, 2026-01-25, 2026-04-26）。严禁虚报财年季度！\n"
        f"2. **数字格式化物理防御**：必须彻底封杀任何科学计数法！100%采用人类操盘手秒懂的『亿美元』本位结算（如 816.15 亿美元，不准写成原始长串数字）。\n"
        f"3. **必须完整一吐到底**：严格按照一、二、三的章节大纲输出，必须把所有指标的环比、同比以及第三部分健康度论断全部完整交卷，绝对不准中途漏掉！\n\n"
        f"---\n"
        f"### 一、 🎯 战略哨所：【{ticker_symbol}】主轴定位\n"
        f"- 宏观定位：一句话指出其当前最新真实市值（以亿美元结算）与科技股核心地位。\n"
        f"- 数据更新：明确标明当前抓取到的最新一份财务数据截止日期。\n\n"
        f"### 二、 📑 核心三季度利润表 (Income Statement) 极简数据硬核对比\n"
        f"请用一个标准的 Markdown 财务大表完整呈现以下6个指标的【历史季度前值2】、【历史季度前值1】、【最新披露季度】、【环比增速】和【同比增速】。要求计算必须绝对精准，格式严整：\n"
        f"- 总营收 (Revenue)\n"
        f"- 毛利润 (Gross Profit)\n"
        f"- 毛利率 (Gross Margin) (用%百分比体现)\n"
        f"- 研发费用 (R&D)\n"
        f"- 营业利润 (Operating Income)\n"
        f"- 净利润 (Net Income)\n\n"
        f"### 三、 🔮 基本面健康度核心三论断 (大白话极限提炼)\n"
        f"1. 护城河现状：用一句话精准阐述营收结构是良性健康还是单核过度依赖。\n"
        f"2. 最核心异动点：用一句话指出研发、运营费用或毛利率是否有爆雷/失速隐患。\n"
        f"3. 下阶段大资金情绪研判：一句话定性下阶段潜在主力会是疯抢还是防守防空。"
    )

    user_task = (
        f"这是我为你准备的【{ticker_symbol}】高纯度财务数据包：\n"
        f"```json\n{json.dumps(purified_packet)}\n```\n"
        f"请立刻对这笔数据包进行全量提炼。利用数据包中的 5 个季度大数，精准找出去年同期的那个季度，算出大表最后一列的『同比增速』。必须完整、不留任何尾巴、一吐到底把第三部分的诊断写完再离场！"
    )
    
    # 🌟 4. 单兵直连点火与正文安全提取
    try:
        print("📡 [M7-LOG-LLM] 3. 正在向满血 Gemini Pro 通道发送 Invoke 指令，全量长卷计算开始...")
        response = llm.invoke([SystemMessage(content=system_instruction), HumanMessage(content=user_task)])
        print("🟢 [M7-LOG-LLM] 4. 大脑计算响应成功！开始解析对象拓扑结构...")
        
        print(f"📋 [M7-LOG-DEBUG] 原始响应类型: {type(response)}")
        if hasattr(response, "response_metadata"):
            print(f"📋 [M7-LOG-DEBUG] 最终截断状态标识(Finish Reason): {response.response_metadata.get('finish_reason')}")
            print(f"📋 [M7-LOG-DEBUG] 全量元数据字典: {response.response_metadata}")
            
        final_report = ""
        if isinstance(response, AIMessage):
            if isinstance(response.content, list):
                print(f"📋 [M7-LOG-DEBUG] 命中的是多形态嵌套列表流，片段总数: {len(response.content)}")
                fragments = []
                for idx, block in enumerate(response.content, 1):
                    print(f"   ├─ 片段 [{idx}] 类型: {type(block)} | 内容缩影: {str(block)[:50]}...")
                    if isinstance(block, dict) and 'text' in block:
                        fragments.append(block['text'])
                    elif isinstance(block, str):
                        fragments.append(block)
                final_report = "".join(fragments)
            else:
                final_report = str(response.content)
        else:
            final_report = str(response)

        print(f"🎉 [M7-LOG-DEBUG] 5. 最终在内存中拼装完毕的纯文本总长度: {len(final_report)} 字")
        print(f"📝 [M7-LOG-DEBUG] 最终文本最末尾50个字缩影透视: {repr(final_report[-50:])}")
        
        # 🛡️ 物理剥离脏挂件
        for dirty_tag in ["', 'extras':", '", "extras":', "', extras=", '", extras=']:
            if dirty_tag in final_report:
                print(f"✂️ [M7-LOG-DEBUG] 斩断残留脏标记: [{dirty_tag}]")
                final_report = final_report.split(dirty_tag)[0]

        final_report = final_report.replace("\\n", "\n")
        print("="*40 + " 🏁 M7 QUANT ENGINE END " + "="*40 + "\n")
        return final_report
        
    except Exception as e:
        print("\n❌ [M7-LOG-CRASH] 核心层突发毁灭性崩溃！！！")
        traceback.print_exc()
        return f"❌ 终端联审发生内部异动崩溃: {e}"

if __name__ == "__main__":
    res = run_m7_audit("NVDA", "日K")
    print(res)