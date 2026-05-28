# mcp_gateway.py (M7-ALPHA 纯Python标准FastAPI网关·物理Node一枪爆头·完璧版)
import sys
import os
import asyncio
import glob
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()

os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

app = FastAPI()
process = None
clients = set()
write_queue = asyncio.Queue()

def find_newsapi_js_entry():
    """🚀【物理雷达】自动跨越复杂的 npm 缓存区，死死锁定 NewsAPI MCP 的物理 JS 核心入口"""
    # 动态抓取你在当前系统利用 npx 产生的本地物理缓存目录
    user_profile = os.environ.get("USERPROFILE", "C:\\Users\\default")
    npx_cache_pattern = os.path.join(user_profile, "AppData", "Local", "npm-cache", "_npx", "*", "node_modules", "mcp-server-newsapi", "dist", "index.js")
    matches = glob.glob(npx_cache_pattern)
    
    if matches:
        print(f"🎯 [M7-GATEWAY] 物理雷达精准锁定 NewsAPI 入口: {matches[0]}")
        return matches[0]
        
    # 如果找不到缓存，尝试查找全局安装路径
    global_npm_path = os.path.join(user_profile, "AppData", "Roaming", "npm", "node_modules", "mcp-server-newsapi", "dist", "index.js")
    if os.path.exists(global_npm_path):
        print(f"🎯 [M7-GATEWAY] 物理雷达精准锁定全局 NewsAPI 入口: {global_npm_path}")
        return global_npm_path
        
    return None

async def init_mcp_subprocess():
    global process
    js_entry = find_newsapi_js_entry()
    
    if js_entry:
        # 🟢 最高维真直连：直接用 node 物理程序拉起具体的 js 脚本，0层套娃，彻底粉碎一切 cmd 乱码和 ENOENT！
        process = await asyncio.create_subprocess_exec(
            "node", js_entry,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    else:
        # 🟡 备用防御线：如果路径定制过，直接大范围盲拉全局批处理文件
        print("⚠️ [M7-GATEWAY] 未在标准缓存区搜到 JS 入口，启动二级盲拉方案...")
        process = await asyncio.create_subprocess_exec(
            "cmd.exe", "/c", "mcp-server-newsapi",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
    print(f"🟢 [M7-GATEWAY] 真正的 MCP 状态机驱动完美激活！PID: {process.pid}")
    asyncio.create_task(read_mcp_stdout())
    asyncio.create_task(write_mcp_stdin())

async def read_mcp_stdout():
    global process
    while True:
        try:
            line = await process.stdout.readline()
            if not line:
                break
            data_str = line.decode('utf-8', errors='ignore').strip()
            if data_str:
                # 当你肉眼在黑窗口里看到这行打印，说明后台的 Node 服务器正在疯狂向你吐出真实的真 MCP 协议报文！
                print(f"📥 [MCP-DEEP-FRAME] {data_str}")
                for queue in list(clients):
                    await queue.put(data_str)
        except:
            break

async def write_mcp_stdin():
    global process
    while True:
        try:
            raw_data = await write_queue.get()
            if process and process.stdin and not process.stdin.is_closing():
                process.stdin.write(raw_data + b'\n')
                await process.stdin.drain()
            write_queue.task_done()
        except:
            pass

@app.get("/sse")
async def sse_endpoint():
    async def event_generator():
        queue = asyncio.Queue()
        clients.add(queue)
        try:
            yield "event: endpoint\ndata: /message\n\n"
            while True:
                data = await queue.get()
                yield f"event: message\ndata: {data}\n\n"
        except asyncio.CancelledError:
            clients.remove(queue)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/message")
async def message_endpoint(request: Request):
    raw_data = await request.body()
    await write_queue.put(raw_data)
    return "OK"

@app.on_event("startup")
async def startup_event():
    await init_mcp_subprocess()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")