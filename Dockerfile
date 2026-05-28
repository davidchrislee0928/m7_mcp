# 1. 使用官方兼顾 Python 和 Node.js 的标准底层镜像
FROM nikolaik/python-nodejs:python3.10-nodejs20

WORKDIR /app

# 2. 物理同步 Node.js 环境依赖
COPY package*.json ./
RUN npm ci --only=production

# 3. 物理同步 Python 环境依赖（支持你的 uv.lock 或 requirements.txt）
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 4. 将全量工程源码拷入虚拟机
COPY . .

# 5. 建立本地 Parquet 与财报持久化数据盾牌目录
RUN mkdir -p data_cache && chmod -R 777 data_cache

# 6. 开启双服务并网端口（Streamlit 默认 7860）
EXPOSE 7860

# 7. 终极点火：在后台同时拉起 Node.js MCP 服务和 Streamlit 前端
CMD node mcp_sse_server.js & streamlit run app.py --server.port=7860 --server.address=0.0.0.0