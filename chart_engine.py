# chart_engine.py (M7-ALPHA 四轴一体真联动·动态切片物理抽干空白·全周期自愈完全体)
import os
import datetime
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if os.path.exists("/data"):
    BASE_CACHE_DIR = "/data"
else:
    BASE_CACHE_DIR = PROJECT_ROOT

CACHE_DIR = os.path.join(BASE_CACHE_DIR, "data_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def load_m7_stock_data_10y_cache(ticker_str: str) -> pd.DataFrame:
    """10年期自适应 Parquet 仓储中心 - 带硬核纯净数据清洗网关"""
    cache_file = os.path.join(CACHE_DIR, f"{ticker_str}_10y.parquet")
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    df_local = None
    if os.path.exists(cache_file):
        file_modify_time = os.path.getmtime(cache_file)
        file_modify_date = datetime.date.fromtimestamp(file_modify_time).strftime("%Y-%m-%d")
        
        if file_modify_date == today_str:
            try:
                df_local = pd.read_parquet(cache_file)
            except Exception as read_err:
                print(f"⚠️ 本地 Parquet 解析异动: {read_err}")
                
    if df_local is None or df_local.empty:
        try:
            print(f"📡 [M7-DOCK] 正在全量打捞 10 年美股二进制因子: {ticker_str}")
            df_net = yf.download(ticker_str, period="10y", interval="1d", auto_adjust=True)
            if not df_net.empty:
                df_net = df_net.dropna(how='all')
                if isinstance(df_net.columns, pd.MultiIndex):
                    df_net.columns = df_net.columns.get_level_values(0)
                df_net.to_parquet(cache_file, engine="pyarrow")
                df_local = df_net
        except Exception as net_err:
            print(f"❌ 10y 数据网关异常: {net_err}")
            return pd.DataFrame()

    # 🛡️ 数据清洗过滤，砸碎所有序列污染类型
    if df_local is not None and not df_local.empty:
        try:
            df_clean = df_local.copy()
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                if col in df_clean.columns:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0.0).astype(float)
            return df_clean
        except Exception as clean_err:
            print(f"❌ 数据流清洗失败: {clean_err}")
            return df_local
            
    return pd.DataFrame()


def generate_m7_clean_charts(ticker_str: str, kline_period: str, time_range_mode: str = "6m"):
    """
    通过将时间切片逻辑上移至 Python 层动态计算，根据传入的 time_range_mode (1m, 3m, 6m, 1y, 5y, Max)
    强行对齐 Y 轴高低点刻度，100% 斩断并解决跨度缩放产生的巨大空白死锁。
    """
    df_raw = load_m7_stock_data_10y_cache(ticker_str)
    if df_raw.empty:
        return None
        
    df_base = df_raw.copy()
    if not isinstance(df_base.index, pd.DatetimeIndex):
        df_base.index = pd.to_datetime(df_base.index)

    # 🛡️ 稳健的重采样聚合
    try:
        if kline_period == "周K":
            df_base = df_base.resample('W').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
            }).dropna()
        elif kline_period == "月K":
            df_base = df_base.resample('ME').agg({
                'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
            }).dropna()
    except Exception as resample_err:
        print(f"重采样聚合异动: {resample_err}")
        df_base = df_raw.copy()

    if df_base.empty or len(df_base) < 2:
        return None

    try:
        # 技术指标全量动态解算
        ma_window = 20 if len(df_base) > 20 else 5
        df_base['MA20'] = df_base['Close'].rolling(window=ma_window).mean()
        df_base['STD20'] = df_base['Close'].rolling(window=ma_window).std()
        df_base['Upper'] = df_base['MA20'] + (df_base['STD20'] * 2)
        df_base['Lower'] = df_base['MA20'] - (df_base['STD20'] * 2)
        
        exp1 = df_base['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df_base['Close'].ewm(span=26, adjust=False).mean()
        df_base['MACD'] = exp1 - exp2
        df_base['Signal'] = df_base['MACD'].ewm(span=9, adjust=False).mean()
        df_base['Hist'] = df_base['MACD'] - df_base['Signal']
        
        low_min = df_base['Low'].rolling(window=9).min()
        high_max = df_base['High'].rolling(window=9).max()
        rsv = ((df_base['Close'] - low_min) / (high_max - low_min) * 100).fillna(50)
        df_base['K'] = rsv.ewm(com=2, adjust=False).mean()
        df_base['D'] = df_base['K'].ewm(com=2, adjust=False).mean()
        df_base['J'] = 3 * df_base['K'] - 2 * df_base['D']

        # 💡【物理切片提纯】：根据用户在前端选中的时间范围，直接截断 DataFrame 逼迫坐标轴合龙
        last_date = df_base.index[-1]
        if time_range_mode == "1m":
            start_date = last_date - pd.DateOffset(months=1)
        elif time_range_mode == "3m":
            start_date = last_date - pd.DateOffset(months=3)
        elif time_range_mode == "1y":
            start_date = last_date - pd.DateOffset(years=1)
        elif time_range_mode == "5y":
            start_date = last_date - pd.DateOffset(years=5)
        elif time_range_mode == "Max":
            start_date = df_base.index[0]
        else:  # 默认 6m
            start_date = last_date - pd.DateOffset(months=6)

        # 过滤出当前可视窗口内的数据，用于极速动态重组 Y 轴绝对边界
        df_visible = df_base.loc[df_base.index >= start_date]
        if df_visible.empty:
            df_visible = df_base.tail(30) # 灾备兜底
            
        start_init_str = df_visible.index[0].strftime("%Y-%m-%d")
        end_init_str = last_date.strftime("%Y-%m-%d")

        # 计算可视窗口内价格主图的绝对最高和绝对最低点
        max_price = float(df_visible['High'].max()) * 1.03
        min_price = float(df_visible['Low'].min()) * 0.97
        if 'Upper' in df_visible.columns and not df_visible['Upper'].isna().all():
            max_price = max(max_price, float(df_visible['Upper'].max()) * 1.02)
        if 'Lower' in df_visible.columns and not df_visible['Lower'].isna().all():
            min_price = min(min_price, float(df_visible['Lower'].min()) * 0.98)

        # 🚀🔥【终极保固微调点】：废除脆弱的 quantile，采用纯数字真实 max 探测
        # 且强制加入铁血保底线，只要数据小于等于0，无条件给一个一千万的初始看盘坐标轴，绝对不让图表隐身！
        raw_max_vol = float(df_visible['Volume'].max())
        if raw_max_vol > 0:
            max_volume = raw_max_vol * 1.02
        else:
            # 如果5年大盘没有获取到有效的Volume序列，采用10年总数据的均值充当灾备大坝
            alt_max = float(df_base['Volume'].max())
            max_volume = alt_max * 0.50 if alt_max > 0 else 10000000.0

        # 计算可视窗口内 MACD 的动态绝对边界
        max_macd = max(float(df_visible['MACD'].max()), float(df_visible['Hist'].max()), float(df_visible['Signal'].max())) * 1.10
        min_macd = min(float(df_visible['MACD'].min()), float(df_visible['Hist'].min()), float(df_visible['Signal'].min())) * 1.10

        # 100% 紧凑无缝级联动骨架
        fig = make_subplots(
            rows=4, cols=1, 
            shared_xaxes=True,          
            vertical_spacing=0.015,     
            row_heights=[0.58, 0.12, 0.15, 0.15], 
            row_titles=("价格", "成交量", "MACD", "KDJ")
        )

        # 📊 1. 价格主图区
        fig.add_trace(go.Candlestick(x=df_base.index, open=df_base['Open'], high=df_base['High'], low=df_base['Low'], close=df_base['Close'], name=f"K线({kline_period})", showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_base.index, y=df_base['Upper'], mode='lines', line=dict(color='rgba(41, 182, 246, 0.4)', width=1), showlegend=False, hoverinfo='skip'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_base.index, y=df_base['Lower'], mode='lines', name='布林通道 (±2σ)', line=dict(color='rgba(41, 182, 246, 0.4)', width=1), fill='tonexty', fillcolor='rgba(41, 182, 246, 0.06)', showlegend=True), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_base.index, y=df_base['MA20'], mode='lines', name='均线 (MA20)', line=dict(color='#FFD54F', width=1.8, dash='dash'), showlegend=True), row=1, col=1)
        
        # 📊 2. 成交量副图区
        colors = ['#FF4444' if row['Close'] >= row['Open'] else '#00FF00' for _, row in df_base.iterrows()]
        fig.add_trace(go.Bar(x=df_base.index, y=df_base['Volume'], name="成交量", marker_color=colors, showlegend=False), row=2, col=1)

        # 📊 3. MACD 指标区
        fig.add_trace(go.Scatter(x=df_base.index, y=df_base['MACD'], mode='lines', name='MACD', line=dict(color='#00E5FF', width=1.2), showlegend=False), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_base.index, y=df_base['Signal'], mode='lines', name='Signal', line=dict(color='orange', width=1.2), showlegend=False), row=3, col=1)
        hist_colors = ['#FF4444' if val >= 0 else '#00FF00' for val in df_base['Hist']]
        fig.add_trace(go.Bar(x=df_base.index, y=df_base['Hist'], name='Hist', marker_color=hist_colors, showlegend=False), row=3, col=1)

        # 📊 4. KDJ 指标区
        fig.add_trace(go.Scatter(x=df_base.index, y=df_base['K'], mode='lines', name='K', line=dict(color='white', width=1.2), showlegend=False), row=4, col=1)
        fig.add_trace(go.Scatter(x=df_base.index, y=df_base['D'], mode='lines', name='D', line=dict(color='yellow', width=1.2), showlegend=False), row=4, col=1)
        fig.add_trace(go.Scatter(x=df_base.index, y=df_base['J'], mode='lines', name='J', line=dict(color='#E040FB', width=1.5), showlegend=False), row=4, col=1)
        fig.add_shape(type="line", x0=df_base.index[0], y0=80, x1=df_base.index[-1], y1=80, line=dict(color="rgba(255,255,255,0.15)", width=1, dash="dot"), row=4, col=1)
        fig.add_shape(type="line", x0=df_base.index[0], y0=20, x1=df_base.index[-1], y1=20, line=dict(color="rgba(255,255,255,0.15)", width=1, dash="dot"), row=4, col=1)

        fig.update_layout(
            height=780,                
            template="plotly_dark",
            margin=dict(t=15, b=10, l=55, r=45), 
            showlegend=True,
            hovermode="x unified",
            dragmode="zoom",
            uirevision=time_range_mode
        )
        
        # 🚀 强行焊死当前的 X 轴显示视口区间，不使用全局 matches 反向污染
        breaks_config = [dict(bounds=["sat", "mon"])] if kline_period == "日K" else None
        
        for r in range(1, 5):
            fig.update_xaxes(
                range=[start_init_str, end_init_str],
                type="date", 
                rangeslider_visible=False,
                rangebreaks=breaks_config,
                showgrid=False,
                row=r, col=1
            )

        # 🚀 由 Python 直接解算出当前周期内的实际真实边界并强制写入布局！
        # 100% 确保成交量安全计算，全量指标绝对不隐身！
        fig.update_yaxes(range=[min_price, max_price], fixedrange=False, exponentformat="none", tickformat=",", row=1, col=1)
        fig.update_yaxes(range=[0, max_volume], fixedrange=False, row=2, col=1) 
        fig.update_yaxes(range=[min_macd, max_macd], fixedrange=False, row=3, col=1)
        fig.update_yaxes(range=[-5, 105], fixedrange=False, row=4, col=1) 

        return fig
    except Exception as e:
        print(f"[{ticker_str}] 核心看板渲染中断: {e}")
        return None