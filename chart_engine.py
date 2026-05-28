# chart_engine.py (M7-ALPHA 四轴一体真联动·死封拉扯空白·终极修复版)
import os
import datetime
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
CACHE_DIR = os.path.join(PROJECT_ROOT, "data_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def load_m7_stock_data_10y_cache(ticker_str: str) -> pd.DataFrame:
    """10年期自适应 Parquet 仓储中心"""
    cache_file = os.path.join(CACHE_DIR, f"{ticker_str}_10y.parquet")
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    if os.path.exists(cache_file):
        file_modify_time = os.path.getmtime(cache_file)
        file_modify_date = datetime.date.fromtimestamp(file_modify_time).strftime("%Y-%m-%d")
        
        if file_modify_date == today_str:
            try:
                df_local = pd.read_parquet(cache_file)
                if not df_local.empty:
                    return df_local
            except Exception as read_err:
                print(f"⚠️ 本地 Parquet 解析异动: {read_err}")
        else:
            print(f"⏳ [M7-PARQUET-STALE] 历史缓存到期，开盘更新中...")
    else:
        print(f"📡 [M7-PARQUET-MISS] 正在全量打捞 10 年美股二进制因子...")

    try:
        # 下载数据
        df_net = yf.download(ticker_str, period="10y", interval="1d", auto_adjust=True)
        if df_net.empty: return pd.DataFrame()
        
        # 🚀 关键微调：彻底剔除所有 NaN 行（周末/节假日）
        df_net = df_net.dropna(how='all')
        
        if isinstance(df_net.columns, pd.MultiIndex):
            df_net.columns = df_net.columns.get_level_values(0)
        df_net.to_parquet(cache_file, engine="pyarrow")
        return df_net
    except Exception as net_err:
        print(f"❌ 10y 数据网关异常: {net_err}")
        return pd.DataFrame()


def generate_m7_clean_charts(ticker_str: str, kline_period: str):
    """
    通过把 rangebreaks 锁死到全量连动轴中，100% 杜绝 Plotly 底层拉扯出多余垂直空白。
    """
    df_raw = load_m7_stock_data_10y_cache(ticker_str)
    if df_raw.empty:
        return None
        
    df = df_raw.copy()
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    try:
        if kline_period == "周K":
            df = df.resample('W').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
            }).dropna()
        elif kline_period == "月K":
            df = df.resample('ME').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
            }).dropna()
    except Exception as resample_err:
        print(f"重采样聚合异动: {resample_err}")
        df = df_raw.copy()

    if df.empty or len(df) < 2:
        return None

    try:
        # 技术指标计算
        ma_window = 20 if len(df) > 20 else 5
        df['MA20'] = df['Close'].rolling(window=ma_window).mean()
        df['STD20'] = df['Close'].rolling(window=ma_window).std()
        df['Upper'] = df['MA20'] + (df['STD20'] * 2)
        df['Lower'] = df['MA20'] - (df['STD20'] * 2)
        
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['Hist'] = df['MACD'] - df['Signal']
        
        low_min = df['Low'].rolling(window=9).min()
        high_max = df['High'].rolling(window=9).max()
        rsv = ((df['Close'] - low_min) / (high_max - low_min) * 100).fillna(50)
        df['K'] = rsv.ewm(com=2, adjust=False).mean()
        df['D'] = df['K'].ewm(com=2, adjust=False).mean()
        df['J'] = 3 * df['K'] - 2 * df['D']

        last_date = df.index[-1]
        six_months_ago = last_date - pd.DateOffset(months=6)
        start_bound = six_months_ago.strftime("%Y-%m-%d")
        end_bound = last_date.strftime("%Y-%m-%d")

        # 完美垂直咬合
        fig = make_subplots(
            rows=4, cols=1, 
            shared_xaxes=True,          
            vertical_spacing=0.02,     
            row_heights=[0.58, 0.12, 0.15, 0.15], 
            row_titles=("价格", "成交量", "MACD", "KDJ")
        )

        # 1. 价格区
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name=f"K线({kline_period})", showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Upper'], mode='lines', line=dict(color='rgba(41, 182, 246, 0.4)', width=1), showlegend=False, hoverinfo='skip'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Lower'], mode='lines', name='布林通道 (±2σ)', line=dict(color='rgba(41, 182, 246, 0.4)', width=1), fill='tonexty', fillcolor='rgba(41, 182, 246, 0.06)', showlegend=True), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], mode='lines', name='均线 (MA20)', line=dict(color='#FFD54F', width=1.8, dash='dash'), showlegend=True), row=1, col=1)
        
        # 2. 成交量
        colors = ['red' if row['Close'] >= row['Open'] else 'green' for _, row in df.iterrows()]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="成交量", marker_color=colors, showlegend=False), row=2, col=1)

        # 3. MACD
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD', line=dict(color='#00E5FF', width=1.2), showlegend=False), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], mode='lines', name='Signal', line=dict(color='orange', width=1.2), showlegend=False), row=3, col=1)
        hist_colors = ['red' if val >= 0 else 'green' for val in df['Hist']]
        fig.add_trace(go.Bar(x=df.index, y=df['Hist'], name='Hist', marker_color=hist_colors, showlegend=False), row=3, col=1)

        # 4. KDJ
        fig.add_trace(go.Scatter(x=df.index, y=df['K'], mode='lines', name='K', line=dict(color='white', width=1.2), showlegend=False), row=4, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['D'], mode='lines', name='D', line=dict(color='yellow', width=1.2), showlegend=False), row=4, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['J'], mode='lines', name='J', line=dict(color='#E040FB', width=1.5), showlegend=False), row=4, col=1)
        fig.add_shape(type="line", x0=df.index[0], y0=80, x1=df.index[-1], y1=80, line=dict(color="rgba(255,255,255,0.15)", width=1, dash="dot"), row=4, col=1)
        fig.add_shape(type="line", x0=df.index[0], y0=20, x1=df.index[-1], y1=20, line=dict(color="rgba(255,255,255,0.15)", width=1, dash="dot"), row=4, col=1)

# ...（前文保持不变）

        fig.update_layout(
            height=850, 
            template="plotly_dark",
            margin=dict(t=55, b=20, l=55, r=45), 
            showlegend=True,
            hovermode="x unified",
            # 🚀 核心修改：将 X 轴强制设为 'category' 类型
            # 这会把 X 轴当成离散标签，所有柱子会像士兵列队一样紧密排列，绝无空隙
            xaxis=dict(
                type='category',
                showgrid=False,
                rangeslider=dict(visible=False),
                # 自定义标签：只显示特定数量的刻度，防止标签堆叠
                tickmode='auto',
                nticks=10
            )
        )
        
        # 移除原先所有与 rangebreaks 和 date 类型相关的配置
        # 彻底让它按照“类别”顺序平铺，不再识别时间日历
        # 🚀 🚀 🚀 【全联轴强韧防线】：必须在 update_xaxes 阶段把 matches 和 rangebreaks 锁死到全部 Row 上！
        # 彻底掐死因为单轴 rangebreaks 变形导致主图下沉腾出多余空白的恶性 bug
        fig.update_xaxes(
            range=[start_bound, end_bound], 
            type="date", 
            rangeslider_visible=False,
            matches='x',  # 👈 强制让所有子图的时间信号锁在同一个物理发讯轴上
            rangebreaks=[dict(bounds=["sat", "mon"])] if kline_period == "日K" else None
        )
        
        # 单独为首选主轴装载按钮
        fig.update_xaxes(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m(默)", step="month", stepmode="backward"), 
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=5, label="5y", step="year", stepmode="backward"),
                    dict(step="all", label="Max")
                ]),
                bgcolor="rgba(45, 45, 45, 0.9)", activecolor="#29B6F6", font=dict(size=11, color="white"),
                y=1.01, x=0.00  
            ),
            row=1, col=1
        )

        fig.update_yaxes(autorange=True, fixedrange=False, exponentformat="none", tickformat=",", row=1, col=1)
        fig.update_yaxes(autorange=True, fixedrange=False, row=2, col=1)
        fig.update_yaxes(autorange=True, fixedrange=False, row=3, col=1)
        fig.update_yaxes(range=[-10, 110], fixedrange=False, row=4, col=1) 

        return fig
    except Exception as e:
        print(f"[{ticker_str}] 核心看板渲染中断: {e}")
        return None