// mcp_sse_server.js (M7-ALPHA 官方标准 SSEServerTransport 工业级真网络节点 · 参数矩阵完美对齐版)
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import express from "express";

const app = express();

const server = new Server(
    { name: "mcp-server-newsapi-pure-sse", version: "1.0.0" },
    { capabilities: { tools: {} } }
);

// 🚀【工具矩阵声明】
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
                        pageSize: { type: "number", description: "The number of results to return (max 100)." }
                    },
                    required: ["q"]
                }
            }
        ]
    };
});

// 🚀【工具执行器：参数解包毫米级校准】
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    if (request.params.name !== "newsapi_get_everything") {
        throw new Error("Unknown tool");
    }

    // 🎯 🎯 🎯【参数完美咬合点】🎯 🎯 🎯
    // 规范解构：框架已经将 arguments 映射到了 params 节点下，直接解构提取真身！
    const args = request.params.arguments || {};
    const query = args.q || "market"; 
    const pageSize = args.pageSize || 10;
    
    const apiKey = process.env.NEWSAPI_API_KEY || "eb243d3af63241518dd1a3c7e7648b77";
    const url = `https://newsapi.org/v2/everything?q=${encodeURIComponent(query)}&language=en&sortBy=publishedAt&pageSize=${pageSize}`;
    
    console.log(`📡 [M7-NODE-ACTIVE] 真 MCP 击穿网络大坝 -> 检索词: [${query}] | 额度: [${pageSize}]`);

    try {
        const response = await globalThis.fetch(url, {
            headers: { "User-Agent": "M7-Quant-Engine/2026.05", "X-Api-Key": apiKey }
        });
        const data = await response.json();
        
        // 返回标准 MCP 文本流结构体
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

let transportInstance = null;

app.get("/sse", async (req, res) => {
    console.log("📡 [M7-NODE-SSE] Python 客户端成功物理接入！正在通过官方协议创建真网络 SSE 广播流...");
    transportInstance = new SSEServerTransport("/message", res);
    await server.connect(transportInstance);
});

app.post("/message", async (req, res) => {
    if (transportInstance) {
        await transportInstance.handlePostMessage(req, res);
    } else {
        res.status(400).send("Session context not ready");
    }
});

app.listen(8000, () => {
    console.log("🔥 [M7-SUCCESS] 真·MCP 官方标准网络服务器已成功在 http://localhost:8000 常驻就绪！");
});