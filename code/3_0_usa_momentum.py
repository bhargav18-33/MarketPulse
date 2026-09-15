import numpy as np
import pandas as pd
import yfinance as yf
import math as m
import sys
from datetime import datetime, timedelta
import ipywidgets as widgets
from IPython.display import display

print("PICK AN END DATE (2021-06-22) [must be a Saturday or Sunday, e.g., 2024-01-27],:")
print("Use the date [05-07 of month Feb,May,Aug,Nov] &[21-22 of month Mar,Jun,Sep,Dec ] ,:")
end_date_input = widgets.DatePicker(
  description='START DATE',
  disabled=False
)
display(end_date_input)

STEP_W   = 7
STEP_D   = 4

NDX_RMA_period = 3
NDX_EMA_span   = 19

RSI_period_W = [12, 15, 17]
RSI_period_D = [16, 19, 23]
multipliers  = [0.35, 0.45, 0.20]

RSI_period_rel  = [14, 19]
multipliers_rel = [0.53, 0.47]
RSI_filter      = [-10 , 87, 60 , 89]

ROC_period       = [4, 16]
ROC_filter       = [45, 90]

CAGR_period      = [55, 89]
CAGR_multipliers = [0.35, 0.65]
CAGR_EMA         = 23
CAGR_filter      = 150

DIS_period      = [23, 47]
DIS_multipliers = [0.57, 0.43]
DIS_filter      = 60

DIST_EMA        = 21
Streak_filter   = 70

RS_period_W = [13, 17, 22]
RS_multipliers = [0.33, 0.42, 0.25]

rank_filters = [121, 121, 121, 121 ,121]
rank_weights = [.10, 0.1,  0.1, 0.1 ,0.1]

ATH_period      = [67 , 67 , 67]
ATH_multipliers = [0.85, 0.85, 0.85]
R_ATH_period    = [25,25]


w_high = 0.54
w_low = 0.46


EMA_window_size = 3
RMA_window_size = 2
RUN_OK = False

BENCHMARK = "^NDX"
STOCKS = [
           "NVDA","AAPL","GOOG","MSFT","AMZN","META","AVGO","TSLA","WMT","ASML","MU","COST","NFLX","PLTR","AMD","CSCO","AMAT","LRCX","TMUS","INTC","LIN","PEP","AMGN","KLAC","GILD","TXN","ISRG","SHOP","APP",
            "ADI","HON","QCOM","BKNG","PDD","PANW","INTU","CEG","VRTX","ADBE","CMCSA","CME","SBUX","SNY","CRWD","EQIX","MELI","ADP","MAR","WDC","SNPS","ABNB","CTAS","CDNS","REGN","STX","DASH","ORLY","CSX",
            "MNST","MDLZ","HOOD","NTES","AEP","ROST","WBD","MRVL","PCAR","FTNT","BKR","ADSK","COIN","FAST","NXPI","MPWR","XEL","FANG","EA","EXC","IDXX","TRI","TER","HBANM","MSTR","LITE","CCEP","AXON","ARGX",
            "ODFL","FITB","PYPL","DDOG","ALNY","EBAY","ESLT","BIDU","RKLB","TTWO","WDAY","KDP","ERIC","ROP","JD","MCHP","CPRT","HBANP","ASTS","PAYX","GEHC","KMB","VOD","ACGL","FISV","TCOM","RYAAY","ONC","SYM",
            "SATS","CTSH","INSM","UAL","EXPE","IBKR","TW","VRSK","CHTR","ULTA","KHC","WTW","AGNCN","AGNCO","FTAI","AGNCL","NTRA","AGNCM","AGNCP","BIIB","STLD","DXCM","GFS","NTRS","TSCO","RPRX","ZS","CINF","EXE",
            "LPLA","FOXA","CASY","SOFI","BNTX","ON","RGLD","FLEX","FITBI","FCNCA","DLTR","WWD","ZM","FOX","FITBP","CHRW","VRSN","TEAM","MDB","JBHT","ROIV","MRNA","UTHR","CRDO","SBAC","FSLR","CSGP","PFG",
            "NTAP","FUTU","TROW","RVMD","EXAS","ILMN","PTC","LULU","INCY","SMCI","EVRG","ENTG","RIVN","CG","LNT","SSNC","LI","CHKP","FITBO","GMAB","AFRM","MTSI","TPG","PODD","HOLX","BPYPM","VTRS","TRMB",
            "GRAB","BPYPP","CDW","FFIV","HTHT","NDSN","COO","VNOM","PAA","BPYPO","MKSI","WMG","EWBC","LECO","NWS","SLMBP","ASND","AKAM","KTOS","REG","ROKU","BPYPN","TTD","KSPI","OKTA","VLYPP","LAMR","VLYPO",
            "GLPI","NVMI","GEN","ARCC","HST","COKE","DPZ","NWSA","TSEM","HAS","IREN","MEDP","LOGI","NBIX","BBIO","DKNG","ALGN","LSCC","ERIE","IONS","TIGO","FIVE","STRL","DRS","GH","AGNC","JKHY","ENSG","RGC",
            "BSY","AEIS","BMRN","SMMT","TXRH","APA","JAZZ","ZBRA","ZG","CELH","Z","AMKR","CFLT","AVAV","WYNN","EXEL","NTNX","BILI","SAIA","TTMI","XP","ENLT","MDGL","SEIC","RMBS","ONBPO","ONBPP","PPC","DOCU",
            "WTFC","SITM","IDCC","IBRX","HSIC","TTEK","MASI","UMBF","ICLR","ONB","ARWR","GLXY","MANH","TECH","BPOP","AUR","PRAX","ZION","SWKS","CGNX","IESC","PCVX","COLB","AXSM","VICR","FCFS","LFUS","SMTC",
            "LKQ","POOL","PEGA","FRHC","HALO","NUVL","MIDD","APLD","BOKF","AAL","LBRDK","NXST","LBRDA","CYTK","GSAT","GDS","NICE","KRYS","AAOI","SIRI","CBSH","AAON","CAMT","MORN","CPB","DOX","ACGLO","QRVO","MTCH",
            "SFM","VIAV","SANM","ROAD","RGEN","GGAL","VLY","FSV","CRUS","APPF","MBLY","HQY","AUGO","KYMR"]

TICKERS = [BENCHMARK] + STOCKS
end_date = end_date_input.value
start_date  = (end_date - timedelta(days=1500)).strftime('%Y-%m-%d')
_raw = yf.download(TICKERS, start=start_date, end=end_date , auto_adjust=True)
_close = _raw["Close"][TICKERS]

_close.index.name = "Date"

tickers = [c for c in _close.columns if c != "NDX"]


# --- data access: pull one ticker's Close for a date range ---
def fetch_adjusted_close(ticker, start_date, end_date):
    if ticker not in _close.columns:
        raise ValueError(f"No data for {ticker}")

    df = _close[[ticker]].loc[pd.to_datetime(start_date): pd.to_datetime(end_date)]
    df = df.rename(columns={ticker: "Close"})
    if df["Close"].dropna().empty:
        raise ValueError(f"No data for {ticker}")
    return df


def build_price_series(stock, benchmark=None, mode="RAW"):
    if mode == "RAW":
        return stock[["Close"]].rename(columns={"Close": "Price"})

    if mode == "RELATIVE":
        if benchmark is None:
            raise ValueError("Benchmark required for RELATIVE mode")
        merged = stock.merge(benchmark, left_index=True, right_index=True, how="inner")
        merged["Price"] = merged["Close_x"] / merged["Close_y"]
        return merged[["Price"]]

    raise ValueError("Invalid price mode")


def _sample_dates(index, step):
    return index[::-1][::step][::-1]


def resample_W(price_df):
    dates = _sample_dates(price_df.index, STEP_W)
    closed_w = price_df["Price"].loc[dates]
    return pd.DataFrame({"W_Closed": closed_w}).reset_index()


def resample_D(price_df):
    dates = _sample_dates(price_df.index, STEP_D)
    closed_d = price_df["Price"].loc[dates]
    return pd.DataFrame({"D_Closed": closed_d}).reset_index()


##FUNCTIONS###

def compute_rsi_series(series, period):
    delta = series.diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    return 100 - (100 / (1 + avg_gain / avg_loss))


def compute_weighted_rsi(price_df, price_col, rsi_periods, multipliers):
    if len(rsi_periods) != len(multipliers):
        raise ValueError("RSI periods and multipliers must have the same length")

    combined = pd.Series(0.0, index=price_df.index)
    for period, weight in zip(rsi_periods, multipliers):
        combined += weight * compute_rsi_series(price_df[price_col], period)
    return combined


def compute_Rate_of_Change(price, periods, prefix="ROC"):
    out = pd.DataFrame(index=price.index)
    for s in periods:
        out[f"{prefix}_{s}"] = price.div(price.shift(s)).sub(1) * 100
    return out


def compute_rma(series, period):
    return series.ewm(alpha=1/period, adjust=False).mean()


def compute_rma_ratios(rma_series, shifts):
    out = pd.DataFrame(index=rma_series.index)
    for s in shifts:
        out[f"RS_{s}"] = rma_series / rma_series.shift(s)
    return out

def compute_weighted_cagr(price_df, price_col, cagr_periods, multipliers, bars_per_year=33):
    if len(cagr_periods) != len(multipliers):
        raise ValueError("CAGR periods and multipliers must have the same length")

    combined = pd.Series(0.0, index=price_df.index)
    for period, weight in zip(cagr_periods, multipliers):
        shifted = price_df[price_col].shift(period)
        cagr = (price_df[price_col] / shifted) ** (bars_per_year/ period) - 1
        combined += weight * cagr

    combined = compute_rma(combined, RMA_window_size)
    return combined * 100

def compute_price_distance(price_df, price_col, spans, multipliers):
    if len(spans) != len(multipliers):
        raise ValueError("Spans and multipliers must have the same length")

    series   = price_df[price_col]
    combined = pd.Series(0.0, index=price_df.index)

    for span, weight in zip(spans, multipliers):
        ema = series.ewm(span=span, adjust=False).mean()
        combined += weight *((series / ema) - 1)

    return combined * 100

def compute_relative_strength(raw_df, benchmark_df, price_col, rs_periods, rs_multipliers, rma_period, rma_rs_window, ema_rs_span):
    if len(rs_periods) != len(rs_multipliers):
        raise ValueError("RS periods and multipliers must have the same length")

    raw_df["RMA_W"] = compute_rma(raw_df[price_col], rma_period)
    raw_df = raw_df.join(compute_rma_ratios(raw_df["RMA_W"], rs_periods))

    total_rs = pd.Series(0.0, index=raw_df.index)
    for period, weight in zip(rs_periods, rs_multipliers):
        raw_df[f"Final_RS_{period}"] = raw_df[f"RS_{period}"] / benchmark_df[f"RS_{period}"]
        total_rs += raw_df[f"Final_RS_{period}"] * weight

    raw_df["Total_RS"] = total_rs
    raw_df["RMA_RS"]   = raw_df["Total_RS"].rolling(rma_rs_window).mean()
    raw_df["EMA_RS"]   = raw_df["Total_RS"].ewm(span=ema_rs_span, adjust=False).mean()
    return raw_df


def compute_streak_above(series, reference):
    above  = series > reference
    reset  = (~above).cumsum()
    streak = above.groupby(reset).cumcount() + 1
    return streak.where(above, 0)

def latest(df):
    return df.sort_values("Date").groupby("Ticker").tail(1).set_index("Ticker")

# ═══════════════════════════════════════════════════════════════
# run_pipeline — everything from Block 1–3, callable for any date
# ═══════════════════════════════════════════════════════════════
def run_pipeline(as_of_date):
    start = (as_of_date - timedelta(days=1000)).strftime('%Y-%m-%d')

    # --- BENCHMARK ---
    ndx_close = fetch_adjusted_close(BENCHMARK, start, as_of_date)
    ndx_price = build_price_series(ndx_close, mode="RAW")

    ndx_w = resample_W(ndx_price)
    ndx_d = resample_D(ndx_price)

    ndx_d["RMA_D"] = compute_rma(ndx_d["D_Closed"], NDX_RMA_period)
    ndx_d["EMA_D"] = ndx_d["D_Closed"].ewm(span=NDX_EMA_span, adjust=False).mean()

    ndx_w["RMA_W"] = compute_rma(ndx_w["W_Closed"], NDX_RMA_period)
    ndx_w = ndx_w.join(compute_rma_ratios(ndx_w["RMA_W"], RS_period_W))

    bull_regime = ndx_d["RMA_D"].iloc[-1] >= ndx_d["EMA_D"].iloc[-1]

    factor_values   = {}
    raw_W_all, rel_W_all, raw_D_all, rel_D_all = [], [], [], []
    final_RSI_W_all, final_RSI_D_all = [], []

    # --- TICKER LOOP ---
    for ticker in tickers:
        try:
            stock = fetch_adjusted_close(ticker, start, as_of_date)
            if len(stock["Close"].dropna()) < 600:
                continue

            raw_price = build_price_series(stock, mode="RAW")
            rel_price = build_price_series(stock, ndx_close, mode="RELATIVE")

            raw_W = resample_W(raw_price)
            raw_D = resample_D(raw_price)
            rel_W = resample_W(rel_price)
            rel_D = resample_D(rel_price)

            # RSI — W
            raw_W["RSI_COMBINED"] = compute_weighted_rsi(raw_W, "W_Closed", RSI_period_W, multipliers)
            rel_W["RSI_COMBINED"] = compute_weighted_rsi(rel_W, "W_Closed", RSI_period_rel, multipliers_rel)

            final_RSI_W = pd.DataFrame(index=raw_W.index)
            final_RSI_W["RSI_W"] = raw_W["RSI_COMBINED"] * w_high + rel_W["RSI_COMBINED"] * w_low
            raw_W["RMA_RSI_W"] = compute_rma(raw_W["RSI_COMBINED"], RMA_window_size)
            final_RSI_W["RMA_RSI_W_FINAL"] = compute_rma(final_RSI_W["RSI_W"], RMA_window_size)
            final_RSI_W["EMA_RSI_W_FINAL"] = final_RSI_W["RSI_W"].ewm(span=11, adjust=False).mean()

            # RSI — D
            raw_D["RSI_COMBINED"] = compute_weighted_rsi(raw_D, "D_Closed", RSI_period_D, multipliers)
            rel_D["RSI_COMBINED"] = compute_weighted_rsi(rel_D, "D_Closed", RSI_period_rel, multipliers_rel)

            final_RSI_D = pd.DataFrame(index=raw_D.index)
            final_RSI_D["RSI_D"] = raw_D["RSI_COMBINED"] * w_high + rel_D["RSI_COMBINED"] * w_low
            final_RSI_D["RMA_RSI_D"] = compute_rma(final_RSI_D["RSI_D"], RMA_window_size)

            final_RSI_W["Date"] = raw_W["Date"]
            final_RSI_D["Date"] = raw_D["Date"]

            # ROC
            raw_D = raw_D.join(compute_Rate_of_Change(raw_D["D_Closed"], ROC_period))

            # CAGR
            raw_D["CAGR"] = compute_weighted_cagr(raw_D, "D_Closed", CAGR_period, CAGR_multipliers)
            raw_D["CAGR_EMA_line"] = raw_D["CAGR"].ewm(span=CAGR_EMA, adjust=False).mean()

            # DIS / STREAK
            rel_D["DIS"] = compute_price_distance(rel_D, "D_Closed", DIS_period, DIS_multipliers)
            rel_D["EMA"] = rel_D["D_Closed"].ewm(span=DIST_EMA, adjust=False).mean()
            rel_D["Streak"] = compute_streak_above(rel_D["D_Closed"], rel_D["EMA"])

            # RELATIVE STRENGTH
            raw_W = compute_relative_strength(raw_W, ndx_w, "W_Closed", RS_period_W, RS_multipliers,
                    rma_period=3, rma_rs_window=RMA_window_size, ema_rs_span=11)

            # ATH SIGNALS (close-only)
            raw_W["High"] = (raw_W["W_Closed"] >= raw_W["W_Closed"].rolling(ATH_period[0], min_periods=ATH_period[0]).max() * ATH_multipliers[0]).astype(int)
            rel_W["High"] = (compute_rma(rel_W["W_Closed"], 3) >= compute_rma(rel_W["W_Closed"], 3).rolling(ATH_period[1], min_periods=ATH_period[1]).max() * ATH_multipliers[1]).astype(int)
            raw_D["CAGR_High"] = (raw_D["CAGR"] >= raw_D["CAGR"].rolling(ATH_period[2], min_periods=ATH_period[2]).max() * ATH_multipliers[2]).astype(int)
            final_RSI_W["High"] = (final_RSI_W["RMA_RSI_W_FINAL"] >= final_RSI_W["RMA_RSI_W_FINAL"].rolling(R_ATH_period[0], min_periods=R_ATH_period[0]).max() * 0.9).astype(int)

            factor_values[ticker] = {
                "Close"    : raw_W["W_Closed"].iloc[-1],
                "RSI_D"    : final_RSI_D["RMA_RSI_D"].iloc[-1],
                "RSI_FW"   : final_RSI_W["RMA_RSI_W_FINAL"].iloc[-1],
                "RSI_FEW"  : final_RSI_W["EMA_RSI_W_FINAL"].iloc[-1],
                "RSI_W"    : raw_W["RMA_RSI_W"].iloc[-1],
                "RSI_ATH"  : final_RSI_W["High"].iloc[-1],
                "RS_SHORT" : raw_W[f"Final_RS_{RS_period_W[0]}"].iloc[-1],
                "RS_MID"   : raw_W[f"Final_RS_{RS_period_W[1]}"].iloc[-1],
                "RS_LONG"  : raw_W[f"Final_RS_{RS_period_W[2]}"].iloc[-1],
                "ROC_LONG" : raw_D[f"ROC_{ROC_period[1]}"].iloc[-1],
                "ROC_DIFF" : raw_D[f"ROC_{ROC_period[1]}"].iloc[-1] - raw_D[f"ROC_{ROC_period[1]}"].shift(11).iloc[-1],
                "DIS_RANK" : rel_D["DIS"].iloc[-1],
                "DIS_DIFF" : rel_D["DIS"].iloc[-1] - rel_D["DIS"].shift(7).iloc[-1],
                "CAGR"     : raw_D["CAGR"].iloc[-1],
                "CAGR_High": raw_D["CAGR_High"].iloc[-1]
            }

            for df, bucket in ((raw_W, raw_W_all), (rel_W, rel_W_all),
                   (final_RSI_W, final_RSI_W_all), (final_RSI_D, final_RSI_D_all),
                   (rel_D, rel_D_all), (raw_D, raw_D_all)):
                  tmp = df.copy()
                  tmp["Ticker"] = ticker
                  bucket.append(tmp)

        except Exception:
            continue

    if not raw_W_all:
        return None   # no tickers survived at all — bear regime or empty universe

    D_raw       = pd.concat(raw_D_all,       ignore_index=True)
    D_rel       = pd.concat(rel_D_all,       ignore_index=True)
    W_raw       = pd.concat(raw_W_all,       ignore_index=True)
    W_rel       = pd.concat(rel_W_all,       ignore_index=True)
    W_final_RSI = pd.concat(final_RSI_W_all, ignore_index=True)
    D_final_RSI = pd.concat(final_RSI_D_all, ignore_index=True)

    latest_W      = latest(W_raw)
    latest_W_R    = latest(W_rel)
    latest_RSI_W  = latest(W_final_RSI)
    latest_RSI_D  = latest(D_final_RSI)
    latest_D_rel  = latest(D_rel)
    latest_D_raw  = latest(D_raw)

    universe_idx = latest_W.index
    common_pass = (
        (latest_W["High"]          == 1) &
        (latest_W_R["High"]        == 1) &
        (latest_D_raw["CAGR_High"] == 1) &
        (latest_W["W_Closed"]      >= 5)
    ).reindex(universe_idx).fillna(False)

    idx = common_pass[common_pass].index

    latest_df   = pd.DataFrame.from_dict(factor_values, orient="index").loc[idx]
    factor_cols = latest_df.columns.drop(["Close", "DIS_DIFF", "ROC_DIFF", "RSI_ATH", "CAGR_High"])
    latest_rank = latest_df[factor_cols].rank(method="min", ascending=False)

    latest_rank["Final_RSI_Rank"] = ((latest_rank["RSI_D"] * 0.45 + latest_rank["RSI_FW"] * 0.55) * 0.53) + (latest_rank["RSI_W"] * 0.47)
    adj_rsi = pd.Series(0, index=latest_rank.index)
    adj_rsi[latest_df["RSI_ATH"] == 1] -= 3
    latest_rank["Final_RSI_Rank"] = (latest_rank["Final_RSI_Rank"] + adj_rsi).clip(lower=1)

    latest_rank["Final_RS_Rank"] = (
        latest_rank["RS_SHORT"] * RS_multipliers[0] +
        latest_rank["RS_MID"]   * RS_multipliers[1] +
        latest_rank["RS_LONG"]  * RS_multipliers[2]
    )

    adj_roc = pd.Series(0, index=latest_rank.index)
    adj_roc[latest_df["ROC_DIFF"] <= -7] += 3
    adj_roc[(latest_df["ROC_DIFF"] >= 10) & (latest_rank["ROC_LONG"] >= 15)] -= 3
    latest_rank["Final_ROC_Rank"] = (latest_rank["ROC_LONG"] + adj_roc).clip(lower=1)

    adj_dis = pd.Series(0, index=latest_rank.index)
    adj_dis[latest_df["DIS_DIFF"] <= -8] += 3
    adj_dis[(latest_df["DIS_DIFF"] >= 10) & (latest_rank["DIS_RANK"] >= 15)] -= 3
    latest_rank["Final_DIS_Rank"] = (latest_rank["DIS_RANK"] + adj_dis).clip(lower=1)

    latest_rank["Final_CAGR_Rank"] = latest_rank["CAGR"]

    return {
        "latest_W": latest_W, "latest_W_R": latest_W_R,
        "latest_RSI_W": latest_RSI_W, "latest_RSI_D": latest_RSI_D,
        "latest_D_rel": latest_D_rel, "latest_D_raw": latest_D_raw,
        "latest_df": latest_df, "latest_rank": latest_rank,
        "idx": idx, "bull_regime": bull_regime,
    }

# STEP 1 — run TODAY

end_date = end_date_input.value
today = run_pipeline(end_date)

if today is None or not today["bull_regime"]:
    print("Market is not investment friendly (Bear Regime), or no data. Exiting.")
else:

    # STEP 2 — find TWO historical dates, snapped to available days

    all_dates = _close.index

    target_1mo = pd.to_datetime(end_date) - timedelta(days=40)
    target_2mo = pd.to_datetime(end_date) - timedelta(days=70)

    hist_date_1mo = all_dates[all_dates <= target_1mo].max()
    hist_date_2mo = all_dates[all_dates <= target_2mo].max()


    # STEP 3 — run the pipeline for BOTH historical dates

    hist_1mo = run_pipeline(hist_date_1mo)
    hist_2mo = run_pipeline(hist_date_2mo)

    TOP_N = 20
    factor_cols = {
        "RSI": "Final_RSI_Rank", "RS": "Final_RS_Rank", "ROC": "Final_ROC_Rank",
        "DIS": "Final_DIS_Rank", "CAGR": "Final_CAGR_Rank",
    }

    def median_gain_by_factor(hist_result, now_price):
        past_price = hist_result["latest_W"]["W_Closed"]
        gains = {}
        for name, col in factor_cols.items():
            top_tickers = hist_result["latest_rank"][col].nsmallest(TOP_N).index
            gain = (now_price.reindex(top_tickers) / past_price.reindex(top_tickers) - 1).dropna()
            gains[name] = gain.median()
        return pd.Series(gains)

    now_price = today["latest_W"]["W_Closed"]

    gain_1mo = median_gain_by_factor(hist_1mo, now_price)
    gain_2mo = median_gain_by_factor(hist_2mo, now_price)



    # STEP 4 — rank factors WITHIN each window (1 = best),

    rank_1mo = gain_1mo.rank(ascending=False)
    rank_2mo = gain_2mo.rank(ascending=False)

    blended_rank = 0.60 * rank_1mo + 0.40 * rank_2mo
    blended_rank = blended_rank.sort_values()

    # STEP 5 — top 3 by blended rank get the bonus schedule

    bonus_schedule = [0.19, 0.17, 0.14]
    bonus = {name: 0.0 for name in factor_cols}
    for i, name in enumerate(blended_rank.index[:3]):
        bonus[name] = bonus_schedule[i]

    dynamic_rank_weights = [0.10 + bonus["RSI"], 0.10 + bonus["RS"], 0.10 + bonus["ROC"],
                             0.10 + bonus["DIS"], 0.10 + bonus["CAGR"]]


    # STEP 6 — apply to TODAY's ranking

    latest_rank = today["latest_rank"]
    latest_rank["Final_Rank"] = (
        latest_rank["Final_RSI_Rank"]  * dynamic_rank_weights[0] +
        latest_rank["Final_RS_Rank"]   * dynamic_rank_weights[1] +
        latest_rank["Final_ROC_Rank"]  * dynamic_rank_weights[2] +
        latest_rank["Final_DIS_Rank"]  * dynamic_rank_weights[3] +
        latest_rank["Final_CAGR_Rank"] * dynamic_rank_weights[4]
    )

for label, result in [("Today", today), ("1 month ago", hist_1mo), ("2 months ago", hist_2mo)]:
    total_evaluated = len(result["latest_W"])
    passed = len(result["idx"])
    pct = 100 * passed / total_evaluated if total_evaluated else 0
    print(f"{label:<14}: {passed:>4} / {total_evaluated:<4} passed common_filter ({pct:.1f}%)")

# BLOCK 5 — REMAINING FILTERS, REPORT, FINAL OUTPUT

latest_W     = today["latest_W"]
latest_W_R   = today["latest_W_R"]
latest_RSI_W = today["latest_RSI_W"]
latest_RSI_D = today["latest_RSI_D"]
latest_D_rel = today["latest_D_rel"]
latest_D_raw = today["latest_D_raw"]
latest_df    = today["latest_df"]
idx          = today["idx"]

final_output = pd.DataFrame({"Final_Rank": latest_rank["Final_Rank"]})

# --- RSI filter ---
latest_combined = latest_W.join(
    latest_RSI_W[["High", "RMA_RSI_W_FINAL","EMA_RSI_W_FINAL"]],
    rsuffix="_weighted", how="inner"
).join(
    latest_RSI_D[["RMA_RSI_D"]], how="inner"
)

rsi_filter = (
    (latest_df["RSI_ATH"].reindex(latest_combined.index) == 1) &
    (latest_combined["RMA_RSI_W_FINAL"] >= RSI_filter[2]) &
    (latest_combined["RMA_RSI_D"]       <= RSI_filter[3]) &
    (
        (latest_combined["RMA_RSI_W_FINAL"] < 75) |
        (latest_combined["RMA_RSI_W_FINAL"] > latest_combined["EMA_RSI_W_FINAL"])
    )
).reindex(idx).fillna(False)

# --- ROC filter ---
roc_filter = (
    (latest_D_raw[f"ROC_{ROC_period[0]}"] < ROC_filter[0]) &
    (latest_D_raw[f"ROC_{ROC_period[1]}"] < ROC_filter[1])
).reindex(idx).fillna(False)

# --- CAGR filter ---
cagr_filter = (
    (latest_D_raw["CAGR"] > latest_D_raw["CAGR_EMA_line"]) &
    (latest_D_raw["CAGR"] < CAGR_filter)
).reindex(idx).fillna(False)

# --- DIS filter ---
dis_filter = (
    (latest_D_rel["DIS"]    < DIS_filter) &
    (latest_D_rel["Streak"] < Streak_filter)
).reindex(idx).fillna(False)

# --- RS filter ---
rs_filter = (
    latest_W["RMA_RS"] >= latest_W["EMA_RS"] * 0.88
).reindex(idx).fillna(False)

# --- RANK filter (5 components, using rank_filters thresholds) ---
rank_filter = (
    (latest_rank["Final_RSI_Rank"]  <= rank_filters[0]) &
    (latest_rank["Final_RS_Rank"]   <= rank_filters[1]) &
    (latest_rank["Final_ROC_Rank"]  <= rank_filters[2]) &
    (latest_rank["Final_DIS_Rank"]  <= rank_filters[3]) &
    (latest_rank["Final_CAGR_Rank"] <= rank_filters[4])
).reindex(idx).fillna(False)

# --- REPORT ---
filters = {
    "rsi"  : rsi_filter,
    "roc"  : roc_filter,
    "cagr" : cagr_filter,
    "dis"  : dis_filter,
    "rs"   : rs_filter,
    "rank" : rank_filter,
}
filter_detail = pd.DataFrame(filters)
filter_detail["ALL"]        = filter_detail.all(axis=1)
filter_detail["Final_Rank"] = final_output["Final_Rank"]

print(filter_detail.drop(columns="Final_Rank").sum().to_frame("Passed"))

# --- FINAL OUTPUT ---
final_Stocks = final_output[filter_detail["ALL"]].sort_values("Final_Rank").head(30)
print(final_Stocks)

final_report = filter_detail.reset_index().rename(columns={"index": "Ticker"}).sort_values("Final_Rank")
final_report.to_csv("filter_report.csv", index=False)
final_Stocks.reset_index().rename(columns={"index": "Ticker"}).to_csv("final_Stocks.csv", index=False)
