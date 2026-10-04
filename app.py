from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from datetime import datetime, timezone
from pathlib import Path

app = FastAPI(title="Robô IA V2 — Paper Trading")

DEFAULT_TICKERS = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BOVA11.SA"]

def indicators(df):
    x = df.copy()
    if isinstance(x.columns, pd.MultiIndex):
        x.columns = x.columns.get_level_values(0)
    x = x.rename(columns=str.lower)
    x["ret1"] = x["close"].pct_change()
    x["sma20"] = x["close"].rolling(20).mean()
    x["sma60"] = x["close"].rolling(60).mean()
    x["mom20"] = x["close"].pct_change(20)
    delta = x["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    x["rsi"] = 100 - 100/(1+rs)
    x["vol20"] = x["ret1"].rolling(20).std()
    x["target"] = (x["close"].shift(-1) > x["close"]).astype(int)
    return x.dropna()

def analyze(ticker):
    hist = yf.download(
        ticker, period="2y", interval="1d",
        auto_adjust=True, progress=False, threads=False
    )
    if hist is None or hist.empty:
        raise RuntimeError(f"Sem dados para {ticker}")

    x = indicators(hist)
    feats = ["rsi","vol20","mom20"]
    x["gap"] = x["sma20"]/x["sma60"] - 1
    feats2 = ["rsi","vol20","mom20","gap"]

    # Separação temporal: treino no passado, teste no período posterior.
    split = int(len(x) * 0.75)
    train = x.iloc[:split]
    test = x.iloc[split:].copy()

    model = LogisticRegression(max_iter=2000)
    model.fit(train[feats2], train["target"])
    test["prob_up"] = model.predict_proba(test[feats2])[:,1]

    latest = x.iloc[-1].copy()
    p = float(model.predict_proba(x.iloc[[-1]][feats2])[:,1][0])
    price = float(latest["close"])
    trend = float(latest["sma20"] / latest["sma60"] - 1)

    # Sinal demonstrativo: IA + filtro de tendência + RSI.
    if p >= 0.70:
    signal = "COMPRA"
    elif p <= 0.30:
    signal = "VENDA"
    else:signal = "NEUTRO"

    # Métrica de teste simples, sem transformar isso em promessa de retorno.
    test_pred = (test["prob_up"] >= 0.5).astype(int)
    accuracy = float((test_pred == test["target"]).mean())

    return {
        "ticker": ticker,
        "price": price,
        "signal": signal,
        "confidence": round((p if signal == "COMPRA" else 1-p if signal == "VENDA" else max(p,1-p))*100, 1),
        "rsi": round(float(latest["rsi"]), 2),
        "trend": round(trend*100, 2),
        "volatility": round(float(latest["vol20"])*100, 2),
        "test_accuracy": round(accuracy*100, 1),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    html = Path("index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)

@app.get("/api/market")
def market(tickers: str = ",".join(DEFAULT_TICKERS)):
    symbols = [x.strip().upper() for x in tickers.split(",") if x.strip()]
    symbols = symbols[:8]
    results, errors = [], []
    for ticker in symbols:
        try:
            results.append(analyze(ticker))
        except Exception as e:
            errors.append({"ticker": ticker, "error": str(e)})
    return JSONResponse({
        "source": "Yahoo Finance via yfinance",
        "note": "Dados podem ter atraso e não constituem feed profissional de execução.",
        "results": results,
        "errors": errors,
        "updated_at": datetime.now(timezone.utc).isoformat()
    })
