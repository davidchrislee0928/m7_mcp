// mcp_sse_server.js (M7-ALPHA 动态会话工厂自适应版 · 彻底粉碎并发500梦魇完全体 · 密钥参数透传动态并网版)
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import express from "express";

const app = express();

// 用来跨路由死死扣住每一个独立智能体专属的官方单实例传输手柄
const activeTransports = new Map();

// 🎯【自适应多实例工厂函数】
function createMcpServerInstance() {
    const server = new Server(
        { name: "mcp-cluster-node", version: "2.0.0" },
        { capabilities: { tools: {} } }
    );

    // A. 动态绑定工具声明
    server.setRequestHandler(ListToolsRequestSchema, async () => {
        return {
            tools: [
                {
                    name: "newsapi_get_everything",
                    description: "Search through millions of articles via NewsAPI in 2026.",
                    inputSchema: {
                        type: "object",
                        properties: {
                            q: { type: "string", description: "Keywords or phrases to search for." },
                            pageSize: { type: "number", description: "The number of results to return." },
                            apiKey: { type: "string", description: "M7 Dynamic injected NewsAPI Key Asset." } // 🚀 显式声明动态并网密钥因数
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
        
        // 🚀【铁血合龙点】：优先从 Python 高维投喂的参数中精准捞取洗净的密钥，其次兜底本地环境，彻底断绝环境变量跨进程丢失阴影！
        const apiKey = args.apiKey || process.env.NEWSAPI_API_KEY;
        
        // 🚀【M7 终极时效微调点】：既然 Python 已经用双引号锁死了主权个股，这里果断换装 publishedAt
        // 确保 NewsAPI 吐出来的每一条高资产因数全部是“此时此刻、美东盘前、当下最新”的滚烫头条！
        const url = `https://newsapi.org/v2/everything?q=${encodeURIComponent(query)}&language=en&sortBy=publishedAt&pageSize=${pageSize}`;
        
        console.log(`📡 [M7-NODE-ACTIVE] 真 MCP 击穿网络大坝 -> 检索词: [${query}] | 密钥状态: [${apiKey ? '🟢 已动态并网(' + apiKey.substring(0,4) + ')' : '🔴 空资产'}]`);

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

let transportInstance = null;

app.get("/sse", async (req, res) => {
    console.log("📡 [M7-CLUSTER] 探测到 Python 客户端物理长连接连入...");
    const transport = new SSEServerTransport("/message", res);
    const dedicatedServer = createMcpServerInstance();
    await dedicatedServer.connect(transport);
    
    if (transport.sessionId) {
        activeTransports.set(transport.sessionId, transport);
        transportInstance = transport;
        console.log(`🟢 [CLUSTER-SUCCESS] 会话工厂创建成功 -> 注册 ID: [${transport.sessionId}] | 集群在线总数: ${activeTransports.size}`);
    }
});

app.post("/message", async (req, res) => {
    const sessionId = req.query.sessionId;
    const targetTransport = activeTransports.get(sessionId) || transportInstance;

    if (targetTransport) {
        await targetTransport.handlePostMessage(req, res);
    } else {
        res.status(400).send("Session cluster registry not ready");
    }
});

app.listen(8000, () => {
    console.log("\n" + "█"*78);
    console.log("🔥 [M7-CLUSTER-SUCCESS] 工业级工厂化多路复用服务器已成功就绪！");
    console.log("█"*78 + "\n");
});