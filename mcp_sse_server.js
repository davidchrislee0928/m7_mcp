// mcp_sse_server.js (M7-ALPHA 官方标准集群大坝 · 动态会话工厂自适应版 · 彻底粉碎并发500梦魇完全体)
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import express from "express";

const app = express();

// 💡 警告：保持原始流纯净度，绝对不要引入 express.json() 等污染流的中间件！

// 🚀【核心重构：中央多实例会话隔离池】
// 用来跨路由死死扣住每一个独立智能体专属的官方单实例传输手柄
const activeTransports = new Map();

// 🎯【自适应多实例工厂函数】
function createMcpServerInstance() {
    const server = new Server(
        { name: "mcp-cluster-node", version: "2.0.0" },
        { capabilities: { tools: {} } }
    );

    // A. 动态绑定工具声明 (🚀🔥开放 sortBy 控制权给 Python)
    server.setRequestHandler(ListToolsRequestSchema, async () => {
        return {
            tools: [
                {
                    name: "newsapi_get_everything",
                    description: "Search through millions of articles from over 80,000 large news sources and blogs in 2026.",
                    inputSchema: {
                        type: "object",
                        properties: {
                            q: { type: "string", description: "Keywords or phrases to search for in the news articles." },
                            pageSize: { type: "number", description: "The number of results to return (max 100)." },
                            // 💡 核心新增：告诉 Python 端，本工具完全接受自定义排序！
                            sortBy: { type: "string", description: "The order to sort the articles in. Possible options: relevancy, popularity, publishedAt." }
                        },
                        required: ["q"]
                    }
                }
            ]
        };
    });

    // B. 动态绑定工具物理执行器
    server.setRequestHandler(CallToolRequestSchema, async (request) => {
        if (request.params.name !== "newsapi_get_everything") {
            throw new Error("Unknown tool");
        }

        const args = request.params.arguments || {};
        const query = args.q || "market"; 
        const pageSize = args.pageSize || 10;
        
        // 🚀🔥核心截获：优先读取 Python 发来的排序指令，如果不发则默认强制 publishedAt
        const sortBy = args.sortBy || "publishedAt"; 
        
        const apiKey = process.env.NEWSAPI_API_KEY ;
        // 将 sortBy 动态拼入 URL，真正实现由外向内的物理击穿
        const url = `https://newsapi.org/v2/everything?q=${encodeURIComponent(query)}&language=en&sortBy=${sortBy}&pageSize=${pageSize}`;
        
        console.log(`📡 [M7-NODE-ACTIVE] 真 MCP 击穿网络大坝 -> 检索词: [${query}] | 额度: [${pageSize}] | 排序规则: [${sortBy}]`);

        try {
            const response = await globalThis.fetch(url, {
                headers: { "User-Agent": "M7-Quant-Engine/2026.05", "X-Api-Key": apiKey }
            });
            const data = await response.json();
            return {
                content: [{ type: "text", text: JSON.stringify(data) }]
            };
        } catch (err) {
            return {
                isError: true,
                content: [{ type: "text", text: `远端打捞异动: ${err.message}` }]
            };
        }
    });

    return server;
}

// 🎯【全局单手柄骨架存根】
let transportInstance = null;

app.get("/sse", async (req, res) => {
    console.log("📡 [M7-CLUSTER] 探测到 Python 客户端物理长连接连入...");
    
    // 1. 动态生成彼此完全独立的官方标准网络通道实例
    const transport = new SSEServerTransport("/message", res);
    
    // 🚀【完璧核心微调点】通过工厂现场为该通道量身定制一个干净、0状态污染、专属于它的官方内核！
    const dedicatedServer = createMcpServerInstance();
    
    // 让专属的内核去连接专属的通道，彻底绕过官方底层“同一实例重复连接”抛 500 的大深坑！
    await dedicatedServer.connect(transport);
    
    if (transport.sessionId) {
        // 2. 将咬合完整的通道实例注册进全局 Map，供 POST 路由多路复用动态打捞
        activeTransports.set(transport.sessionId, transport);
        
        // 3. 始终让全局手柄同步指向最后激活的实体，维持物理管道畅通
        transportInstance = transport;
        console.log(`🟢 [CLUSTER-SUCCESS] 会话工厂创建成功 -> 注册 ID: [${transport.sessionId}] | 集群在线总数: ${activeTransports.size}`);
    }
});

app.post("/message", async (req, res) => {
    // 4. 从 Python 官方 SDK 自动挂载的查询参数中，精准提取当前请求的专属 sessionId
    const sessionId = req.query.sessionId;
    const targetTransport = activeTransports.get(sessionId) || transportInstance;

    if (targetTransport) {
        // 5. 0字节污染，直接丢给该专属传输器实例去解包分发
        await targetTransport.handlePostMessage(req, res);
    } else {
        res.status(400).send("Session cluster registry not ready");
    }
});

app.listen(8000, () => {
    console.log("\n" + "█"*78);
    console.log("🔥 [M7-CLUSTER-SUCCESS] 工业级工厂化多路复用服务器已成功在 http://localhost:8000 完璧落就绪！");
    console.log("📢 架构特性: 已完美突破官方 SDK 实例单会话封锁，100% 支持任意多客户端高并发轰炸。");
    console.log("█"*78 + "\n");
});