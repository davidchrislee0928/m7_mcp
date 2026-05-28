# agent_nvda.py (M7-ALPHA · 英伟达看盘大脑 · 终端利落平铺版)
import json
from news_engine import get_latest_news

print("\n" + "💚" * 30)
print("💚 [AGENT-NVDA] NVIDIA 个股财报大脑已成功点火启动...")
print("💚 正在通过物理网络层跨系统穿透真 MCP 大坝，打捞路透社/彭博社实盘核心财报...")
print("💚" * 30 + "\n")

# 🚀【高维执行】正式跨系统击穿大坝
res = get_latest_news("stock", topic="NVIDIA")

# 🎯【格式化平铺打印中心】
if isinstance(res, list) and len(res) > 0:
    print("\n" + "█" * 25 + " 📰 NVDA REAL-TIME FINANCIAL REPORT " + "█" * 25)
    
    for idx, news in enumerate(res, 1):
        print(f"\n🔥 [情报序号: {idx:02d}] --------------------------------------------------")
        print(f"📌 核心标题: {news.get('title', '未命名高维快讯')}")
        print(f"📄 深度快照:\n{news.get('summary', '无细分摘要明细')}")
        print("-" * 68)
        
    print("\n" + "█" * 78 + "\n")
else:
    print("\n⚠️ [AGENT-NVDA-WARN] 链路完璧通关，但当前时间节点远端 NewsAPI 未能清洗出符合白名单机构的 NVDA 相关财报数据。")