import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import subprocess
import time

# =====================================================
# CONFIG
# =====================================================

API_KEY = "f46207aae7aa49b0910374f83122f5eb"

TOP_STOCKS = [
    "AAPL","MSFT","TSLA","NVDA","GOOGL",
    "META","AMZN","AMD","NFLX","INTC"
]

st.set_page_config(
    page_title="QuantScope",
    layout="wide"
)

st.title("QuantScope")
st.caption("Live Stock Analytics using C++ Competitive Programming Backend")

# =====================================================
# SIDEBAR CONTROLS
# =====================================================

st.sidebar.header("⚙ Controls")

if "stocks" not in st.session_state:
    st.session_state.stocks = ["AAPL","MSFT","TSLA"]

st.sidebar.header("Controls")

default_options = list(set(TOP_STOCKS + st.session_state.stocks))

selected = st.sidebar.multiselect(
    "Select Stocks",
    default_options,
    default=st.session_state.stocks
)

custom = st.sidebar.text_input("Add Custom Stock")

if st.sidebar.button("Add Stock"):
    if custom.strip():
        sym = custom.strip().upper()

        if sym not in default_options:
            default_options.append(sym)

        if sym not in selected:
            selected.append(sym)

st.session_state.stocks = selected
selected = st.session_state.stocks

# -----------------------------------------------------
# INTERVAL SELECTOR
# -----------------------------------------------------

interval = st.sidebar.selectbox(
    "Select Time Interval (between each data point)",
    [
        "1min",
        "5min",
        "15min",
        "30min",
        "45min",
        "1h",
        "2h",
        "4h",
        "1day",
        "1week",
        "1month"
    ],
    index=0
)

# -----------------------------------------------------
# OUTPUT SIZE
# -----------------------------------------------------

outputsize = st.sidebar.selectbox(
    "Candles / Data Points",
    [30,60,100,200,500,1000],
    index=1
)

refresh = st.sidebar.checkbox("Auto Refresh 15 sec", False)

# =====================================================
# API FETCH
# =====================================================

@st.cache_data(ttl=30)
def get_data(symbol, interval, outputsize):

    try:
        url = (
            f"https://api.twelvedata.com/time_series?"
            f"symbol={symbol}"
            f"&interval={interval}"
            f"&outputsize={outputsize}"
            f"&apikey={API_KEY}"
        )

        r = requests.get(url, timeout=10)
        data = r.json()

        if "values" not in data:
            return None

        df = pd.DataFrame(data["values"])
        df = df.iloc[::-1].reset_index(drop=True)

        for col in ["open","high","low","close"]:
            df[col] = pd.to_numeric(df[col])

        return df

    except:
        return None

# =====================================================
# RUN C++
# =====================================================

def run_cpp(arr):

    inp = str(len(arr)) + "\n" + " ".join(map(str, arr))

    result = subprocess.run(
        ["./cp_engine.exe"],
        input=inp,
        text=True,
        capture_output=True
    )

    lines = result.stdout.strip().split("\n")

    mp = {}

    for line in lines:
        if "=" in line:
            k,v = line.split("=",1)
            mp[k] = v

    return mp

# =====================================================
# LOAD STOCK DATA
# =====================================================

stock_data = {}

for s in selected:
    df = get_data(s, interval, outputsize)
    if df is not None:
        stock_data[s] = df

if len(stock_data) == 0:
    st.error("No valid stock loaded.")
    st.stop()

# =====================================================
# LIVE PRICE CARDS
# =====================================================

st.subheader("Live Prices")

cols = st.columns(len(stock_data))

for i,(name,df) in enumerate(stock_data.items()):

    last_price = round(df["close"].iloc[-1],2)
    chg = round(df["close"].iloc[-1] - df["close"].iloc[0],2)

    cols[i].metric(name,last_price,chg)

# =====================================================
# MULTI STOCK COMPARE
# =====================================================

st.subheader("Compare Stocks")

fig = go.Figure()

for name, df in stock_data.items():

    fig.add_trace(go.Scatter(
        x=list(range(len(df))),
        y=df["close"],
        mode="lines+markers+text",
        name=name,
        text=[name if i == len(df)-1 else "" for i in range(len(df))],
        textposition="top right",
        line=dict(width=3),
        marker=dict(size=5)
    ))

fig.update_layout(
    title=f"Multi Stock Comparison ({interval})",
    height=550,
    xaxis_title="Time Index",
    yaxis_title="Price",
    hovermode="x unified",
    template="plotly_dark",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, width="stretch")

# =====================================================
# RANKING
# =====================================================

st.subheader("Growth Ranking")

rank = []

for name,df in stock_data.items():

    growth = df["close"].iloc[-1] - df["close"].iloc[0]

    rank.append([name, round(growth,2)])

rank = sorted(rank, key=lambda x:x[1], reverse=True)

rank_df = pd.DataFrame(rank, columns=["Stock","Growth"])

st.dataframe(rank_df, width="stretch")

# =====================================================
# CANDLESTICK
# =====================================================

st.subheader("🕯 Candlestick")

cand = st.selectbox(
    "Choose Stock",
    list(stock_data.keys())
)

cdf = stock_data[cand]

fig2 = go.Figure(data=[go.Candlestick(
    x=list(range(len(cdf))),
    open=cdf["open"],
    high=cdf["high"],
    low=cdf["low"],
    close=cdf["close"],
    name=cand
)])

fig2.update_layout(
    title=f"{cand} Candlestick ({interval})",
    height=600,
    xaxis_title="Time Index",
    yaxis_title="Price",
    template="plotly_dark",
    hovermode="x unified"
)

# Add current price label
fig2.add_annotation(
    x=len(cdf)-1,
    y=float(cdf["close"].iloc[-1]),
    text=f"Latest: {round(cdf['close'].iloc[-1],2)}",
    showarrow=True,
    arrowhead=2
)

st.plotly_chart(fig2, width="stretch")

# =====================================================
# C++ ANALYTICS
# =====================================================

st.markdown("## ⚡ C++ Competitive Programming Analytics")

all_results = {}

for name, df in stock_data.items():
    arr = df["close"].tolist()
    all_results[name] = run_cpp(arr)

selected_cp = st.multiselect(
    "Select Stocks to Compare C++ Analytics",
    list(stock_data.keys()),
    default=list(stock_data.keys())[:2]
)

tabs = st.tabs(["📊 Summary Cards", "⚔ Compare Table", "🏆 Winners"])

# =====================================================
# SUMMARY
# =====================================================

with tabs[0]:

    chosen = st.selectbox(
        "Choose Stock for Detailed Analytics",
        selected_cp
    )

    ans = all_results[chosen]

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📈 Average", ans["AVG"])
    c2.metric("💰 Max Profit", ans["MAX_PROFIT"])
    c3.metric("📊 Best MA5", ans["BEST_MA5"])
    c4.metric("📉 Trend", ans["TREND"])

    d1,d2,d3,d4 = st.columns(4)
    d1.metric("🔺 Highest", ans["TOP1"])
    d2.metric("🔻 Lowest", ans["SEG_MIN"])
    d3.metric("🧠 Bit Flips", ans["BIT_FLIPS"])
    d4.metric("🌐 Graph Components", ans["GRAPH_COMPONENTS"])

    e1,e2,e3,e4 = st.columns(4)
    e1.metric("🧩 DSU Clusters", ans["DSU_CLUSTERS"])
    e2.metric("🎯 Buy Day", ans["BUY_DAY"])
    e3.metric("🏁 Sell Day", ans["SELL_DAY"])
    e4.metric("🔢 Unique Prices", ans["UNIQUE_PRICES"])
    
    f1,f2,f3,f4 = st.columns(4)
    f1.metric("BS Index", ans["BS_INDEX"])
    

# =====================================================
# COMPARE TABLE
# =====================================================

with tabs[1]:

    rows = []

    for stock in selected_cp:

        a = all_results[stock]

        rows.append({
            "Stock": stock,
            "Average": float(a["AVG"]),
            "Profit": float(a["MAX_PROFIT"]),
            "MA5": float(a["BEST_MA5"]),
            "Highest": float(a["TOP1"]),
            "Lowest": float(a["SEG_MIN"]),
            "BitFlips": int(a["BIT_FLIPS"]),
            "Clusters": int(a["DSU_CLUSTERS"]),
            "Trend": a["TREND"]
        })

    df = pd.DataFrame(rows)

    max_profit = df["Profit"].max()
    max_avg = df["Average"].max()
    max_high = df["Highest"].max()
    min_low = df["Lowest"].min()

    html = """
    <style>
    table {
        width:100%;
        border-collapse:collapse;
        font-size:18px;
    }
    th, td {
        padding:12px;
        text-align:center;
        border:1px solid #222;
    }
    th {
        background:#111827;
        color:white;
    }
    tr:nth-child(even){
        background:#0f172a;
    }
    tr:nth-child(odd){
        background:#111827;
    }

    .green{
        background:#00ff8855;
        box-shadow:0 0 6px #00ff88;
        font-weight:bold;
    }

    .red{
        background:#ff335555;
        box-shadow:0 0 6px #ff3355;
        font-weight:bold;
    }

    .gold{
        background:#ffd70055;
        box-shadow:0 0 6px gold;
        font-weight:bold;
    }

    </style>

    <table>
    <tr>
    <th>Stock</th>
    <th>Average</th>
    <th>Profit</th>
    <th>MA5</th>
    <th>Highest</th>
    <th>Lowest</th>
    <th>Trend</th>
    </tr>
    """

    for _, row in df.iterrows():

        html += "<tr>"
        html += f"<td>{row['Stock']}</td>"

        avg_cls = "green" if row["Average"] == max_avg else ""
        pro_cls = "green" if row["Profit"] == max_profit else ""
        high_cls = "gold" if row["Highest"] == max_high else ""
        low_cls = "red" if row["Lowest"] == min_low else ""

        html += f"<td class='{avg_cls}'>{row['Average']:.2f}</td>"
        html += f"<td class='{pro_cls}'>{row['Profit']:.2f}</td>"
        html += f"<td>{row['MA5']:.2f}</td>"
        html += f"<td class='{high_cls}'>{row['Highest']:.2f}</td>"
        html += f"<td class='{low_cls}'>{row['Lowest']:.2f}</td>"
        html += f"<td>{row['Trend']}</td>"

        html += "</tr>"

    html += "</table>"

    st.markdown(html, unsafe_allow_html=True)

    st.caption("🟢 Green Glow = Best | 🔴 Red Glow = Lowest | 🟡 Gold Glow = Highest")

# =====================================================
# WINNERS
# =====================================================

with tabs[2]:

    rows = []

    for stock in selected_cp:

        a = all_results[stock]

        rows.append({
            "Stock": stock,
            "Profit": float(a["MAX_PROFIT"]),
            "Average": float(a["AVG"]),
            "Highest": float(a["TOP1"])
        })

    win_df = pd.DataFrame(rows)

    x1,x2,x3 = st.columns(3)

    x1.success("💰 Best Profit: " + win_df.sort_values(
        by="Profit", ascending=False
    ).iloc[0]["Stock"])

    x2.success("📈 Highest Avg: " + win_df.sort_values(
        by="Average", ascending=False
    ).iloc[0]["Stock"])

    x3.success("🚀 Highest Peak: " + win_df.sort_values(
        by="Highest", ascending=False
    ).iloc[0]["Stock"])

# =====================================================
# AUTO REFRESH
# =====================================================

if refresh:
    time.sleep(15)
    st.rerun()