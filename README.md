# 📊 M7-ALPHA 量化多智能体主权控制仓 (M7-ALPHA Quantum Multi-Agent Terminal)

![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge)
![Node.js](https://img.shields.io/badge/Gateway-Node.js_20-339933?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/Core-LangGraph_&_Gemini_3.5-4285F4?style=for-the-badge)
![License](https://img.shields.io/badge/Security-Level_4_Compliant-00FF00?style=for-the-badge)

M7-ALPHA 是一个工业级、全画布四轴强联动、多语言并网的多智能体量化看盘与财务审计控制台。系统采用 **Python 状态机大脑** 与 **Node.js MCP 高并发异步网关** 混合驱动架构，完美打通了 FMP (Financial Modeling Prep) 财务底层资产与实时全球高频金融/舆情流，为纳斯达克 100 成分股提供跨空间的终极主权决策建议。

---

## ⚡ 核心架构体系

本工程由两大铁血硬核引擎并网联动：
1. **上层决策大脑 (`app.py` & `mcp_langgraph_agent.py`)**：基于 Streamlit 框架构建的全宽动态看板。集成 LangGraph 状态机与满血 Gemini 3.5 核心阵列，执行多维基本面全量脱水提纯。
2. **底层异步网关 (`mcp_sse_server.js`)**：基于 Node.js Express 框架构建的标准 Model Context Protocol (MCP) 高并发会话工场，用来跨路由锁住独立智能体专属的官方单实例传输手柄。

---

## ✨ 核心工业级功能点

* **🕒 跨空间铁血时钟**：侧边栏原生 HTML Flex 纵向通铺卡片，实时秒级同步北京时间与美东时间（EST/EDT 自动换算），彻底告别物理截断。
* **💵 Parquet 价格自愈网关**：高频标的价格优先强吞本地 `data_cache/*.parquet` 物理盾牌，针对 15 分钟时差自动触发 yfinance 网络穿透追索并异步全量覆写，兼顾毫秒级冷启动与实盘保真。
* **📈 宏观因子防死锁重刷**：`macro_engine.py` 实现天级物理固化缓存与高频标的一维 NumPy 降维打捞，自带 `N/A` 脏数据热冲刷洗盘机制，在前端采用全宽弹性卡片流无损平铺。
* **🛡️ 铁血风控隔離**：完美的 `.gitignore` 动态大坝设计，物理隔离 `node_modules/`、`.env` 生产环境密钥及数 GB 的冷热财报缓存资产。

---

## 📂 项目模块账本

```text
├── app.py                      # Streamlit 工业级全画布前端主控台
├── mcp_langgraph_agent.py      # LangGraph 财务状态机逻辑与多 Key 轮询阵列
├── macro_engine.py             # 全球宏观核心因子（美元、美债、原油）降维打捞中心
├── chart_engine.py             # 四轴一体真联动 Plotly 纯净高级清洗图表渲染器
├── decision_engine.py          # Gemini 3.5 首席战略家高维自适应跨空间决策大脑
├── mcp_sse_server.js           # Node.js MCP 官方标准集群大坝（Express 架构）
├── requirements.txt            # Python 全量依赖环境高精地图
├── package.json                # Node.js 环境及 MCP SDK 依赖声明
└── Dockerfile                  # 用于云端虚拟机虚拟机一键点火上云的容器配置文件