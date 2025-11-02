## tv_crypto_listener.py
# Requisitos: pip install tradingview_ta requests flask

import os, time, requests
from tradingview_ta import TA_Handler, Interval
from keep_alive import keep_alive

# ===== MANTENER ACTIVO EN RENDER =====
keep_alive()

# ===== CONFIGURA AQUÍ =====
TOKEN = os.getenv("TOKEN")  # ✅ token seguro desde variables de entorno
EXCHANGE = "BINANCE"
SCREENER = "crypto"
SUPPORTED = {"BTC", "ETH", "SOL", "XRP", "DOGE", "LTC", "BNB", "ADA"}
# ==========================

TIMEFRAMES = {
    "1H": Interval.INTERVAL_1_HOUR,
    "4H": Interval.INTERVAL_4_HOURS,
    "1D": Interval.INTERVAL_1_DAY
}

REC_EMOJI = {
    "STRONG_BUY": "🟢🟢🟢",
    "BUY": "🟢",
    "NEUTRAL": "🟡",
    "SELL": "🔴",
    "STRONG_SELL": "🔴🔴🔴",
    "UNKNOWN": "⚪"
}

API_URL = lambda: f"https://api.telegram.org/bot{TOKEN}"

# ======== ANÁLISIS TÉCNICO ========

def get_analysis(symbol, interval):
    h = TA_Handler(symbol=f"{symbol}USDT", exchange=EXCHANGE, screener=SCREENER, interval=interval)
    a = h.get_analysis()
    ind = a.indicators
    def val(k, nd=2):
        v = ind.get(k)
        if v is None: return None
        try: return round(float(v), nd)
        except: return None
    return {
        "price": val("close"),
        "rec": a.summary.get("RECOMMENDATION", "UNKNOWN"),
        "rsi": val("RSI"),
        "ao": val("AO", 4),
        "adx": val("ADX"),
        "ema20": val("EMA20"),
        "ema50": val("EMA50"),
        "ema200": val("EMA200"),
        "macd": val("MACD.macd", 4),
        "macds": val("MACD.signal", 4),
        "macdh": val("MACD.hist", 4)
    }

def trend_text(d):
    e20,e50,e200,adx = d["ema20"],d["ema50"],d["ema200"],d["adx"]
    strong = " 💪" if (adx and adx>=25) else ""
    if all(x is not None for x in (e20,e50,e200)):
        if e20>e50>e200: return f"🔺 Alcista{strong}"
        elif e20<e50<e200: return f"🔻 Bajista{strong}"
        else: return f"↔️ Lateral{strong}"
    return "·"

def macd_info(d):
    m,s,h = d["macd"], d["macds"], d["macdh"]
    cross="·"
    if m is not None and s is not None:
        if m>s: cross="🟢 Cruce alcista"
        elif m<s: cross="🔴 Cruce bajista"
    return m,s,h,cross

def interpret_signal(d):
    score,reasons=0,[]
    rec=(d["rec"] or "").upper()
    if rec in("STRONG_BUY","BUY"): score+=1; reasons.append("TV=BUY")
    elif rec in("STRONG_SELL","SELL"): score-=1; reasons.append("TV=SELL")

    rsi=d["rsi"]
    if rsi is not None:
        if rsi<35: score+=1; reasons.append("RSI bajo")
        elif rsi>65: score-=1; reasons.append("RSI alto")

    ao=d["ao"]
    if ao is not None:
        if ao>0: score+=1; reasons.append("AO>0")
        elif ao<0: score-=1; reasons.append("AO<0")

    e20,e50,e200=d["ema20"],d["ema50"],d["ema200"]
    if all(x is not None for x in (e20,e50,e200)):
        if e20>e50>e200: score+=1; reasons.append("EMA alcista")
        elif e20<e50<e200: score-=1; reasons.append("EMA bajista")

    m,s,_,_=macd_info(d)
    if m is not None and s is not None:
        if m>s: score+=1; reasons.append("MACD>Señal")
        elif m<s: score-=1; reasons.append("MACD<Señal")

    if score>=2: sig="🟢 COMPRAR"
    elif score<=-2: sig="🔴 VENDER"
    else: sig="🟡 NEUTRAL"
    return sig, ", ".join(reasons) if reasons else "—"

def make_block(tf_label,d):
    m,s,h,cross=macd_info(d)
    signal,reasons=interpret_signal(d)
    def f(v): return "-" if v is None else str(v)
    lines=[]
    lines.append(f"{tf_label} 📊")
    lines.append("-"*38)
    lines.append(f"{'Precio':<10}: {f(d['price'])}")
    lines.append(f"{'Recomend.':<10}: {REC_EMOJI.get(d['rec'],'⚪')} {d['rec']}")
    lines.append("-"*38)
    lines.append(f"{'RSI':<10}: {f(d['rsi'])}")
    lines.append(f"{'AO':<10}: {f(d['ao'])}")
    lines.append(f"{'ADX':<10}: {f(d['adx'])}")
    lines.append("-"*38)
    lines.append(f"{'EMA20':<10}: {f(d['ema20'])}")
    lines.append(f"{'EMA50':<10}: {f(d['ema50'])}")
    lines.append(f"{'EMA200':<10}: {f(d['ema200'])}")
    lines.append("-"*38)

# tv_crypto_listener.py
# Requisitos: pip install tradingview_ta requests flask

import os, time, requests
from tradingview_ta import TA_Handler, Interval
from keep_alive import keep_alive

# ===== MANTENER ACTIVO EN RENDER =====
keep_alive()

# ===== CONFIGURA AQUÍ =====
TOKEN = os.getenv("TOKEN")  # ✅ token seguro desde variables de entorno
EXCHANGE = "BINANCE"
SCREENER = "crypto"
SUPPORTED = {"BTC", "ETH", "SOL", "XRP", "DOGE", "LTC", "BNB", "ADA"}
# ==========================

TIMEFRAMES = {
    "1H": Interval.INTERVAL_1_HOUR,
    "4H": Interval.INTERVAL_4_HOURS,
    "1D": Interval.INTERVAL_1_DAY
}

REC_EMOJI = {
    "STRONG_BUY": "🟢🟢🟢",
    "BUY": "🟢",
    "NEUTRAL": "🟡",
    "SELL": "🔴",
    "STRONG_SELL": "🔴🔴🔴",
    "UNKNOWN": "⚪"
}

API_URL = lambda: f"https://api.telegram.org/bot{TOKEN}"

# ======== ANÁLISIS TÉCNICO ========

def get_analysis(symbol, interval):
    h = TA_Handler(symbol=f"{symbol}USDT", exchange=EXCHANGE, screener=SCREENER, interval=interval)
    a = h.get_analysis()
    ind = a.indicators
    def val(k, nd=2):
        v = ind.get(k)
        if v is None: return None
        try: return round(float(v), nd)
        except: return None
    return {
        "price": val("close"),
        "rec": a.summary.get("RECOMMENDATION", "UNKNOWN"),
        "rsi": val("RSI"),
        "ao": val("AO", 4),
        "adx": val("ADX"),
        "ema20": val("EMA20"),
        "ema50": val("EMA50"),
        "ema200": val("EMA200"),
        "macd": val("MACD.macd", 4),
        "macds": val("MACD.signal", 4),
        "macdh": val("MACD.hist", 4)
    }

def trend_text(d):
    e20,e50,e200,adx = d["ema20"],d["ema50"],d["ema200"],d["adx"]
    strong = " 💪" if (adx and adx>=25) else ""
    if all(x is not None for x in (e20,e50,e200)):
        if e20>e50>e200: return f"🔺 Alcista{strong}"
        elif e20<e50<e200: return f"🔻 Bajista{strong}"
        else: return f"↔️ Lateral{strong}"
    return "·"

def macd_info(d):
    m,s,h = d["macd"], d["macds"], d["macdh"]
    cross="·"
    if m is not None and s is not None:
        if m>s: cross="🟢 Cruce alcista"
        elif m<s: cross="🔴 Cruce bajista"
    return m,s,h,cross

def interpret_signal(d):
    score,reasons=0,[]
    rec=(d["rec"] or "").upper()
    if rec in("STRONG_BUY","BUY"): score+=1; reasons.append("TV=BUY")
    elif rec in("STRONG_SELL","SELL"): score-=1; reasons.append("TV=SELL")

    rsi=d["rsi"]
    if rsi is not None:
        if rsi<35: score+=1; reasons.append("RSI bajo")
        elif rsi>65: score-=1; reasons.append("RSI alto")

    ao=d["ao"]
    if ao is not None:
        if ao>0: score+=1; reasons.append("AO>0")
        elif ao<0: score-=1; reasons.append("AO<0")

    e20,e50,e200=d["ema20"],d["ema50"],d["ema200"]
    if all(x is not None for x in (e20,e50,e200)):
        if e20>e50>e200: score+=1; reasons.append("EMA alcista")
        elif e20<e50<e200: score-=1; reasons.append("EMA bajista")

    m,s,_,_=macd_info(d)
    if m is not None and s is not None:
        if m>s: score+=1; reasons.append("MACD>Señal")
        elif m<s: score-=1; reasons.append("MACD<Señal")

    if score>=2: sig="🟢 COMPRAR"
    elif score<=-2: sig="🔴 VENDER"
    else: sig="🟡 NEUTRAL"
    return sig, ", ".join(reasons) if reasons else "—"

def make_block(tf_label,d):
    m,s,h,cross=macd_info(d)
    signal,reasons=interpret_signal(d)
    def f(v): return "-" if v is None else str(v)
    lines=[]
    lines.append(f"{tf_label} 📊")
    lines.append("-"*38)
    lines.append(f"{'Precio':<10}: {f(d['price'])}")
    lines.append(f"{'Recomend.':<10}: {REC_EMOJI.get(d['rec'],'⚪')} {d['rec']}")
    lines.append("-"*38)
    lines.append(f"{'RSI':<10}: {f(d['rsi'])}")
    lines.append(f"{'AO':<10}: {f(d['ao'])}")
    lines.append(f"{'ADX':<10}: {f(d['adx'])}")
    lines.append("-"*38)
    lines.append(f"{'EMA20':<10}: {f(d['ema20'])}")
    lines.append(f"{'EMA50':<10}: {f(d['ema50'])}")
    lines.append(f"{'EMA200':<10}: {f(d['ema200'])}")
    lines.append("-"*38)
    lines.append(f"{'MACD':<10}: {f(m)}")
    lines.append(f"{'Señal':<10}: {f(s)}")
    lines.append(f"{'Hist':<10}: {f(h)}")
    lines.append(f"{'Cruce':<10}: {cross}")
    lines.append("-"*38)
    lines.append(f"{'Tendencia':<10}: {trend_text(d)}")
    lines.append(f"{'Señal':<10}: {signal}")
    lines.append(f"{'Bases':<10}: {reasons}")
    return "\n".join(lines), signal, trend_text(d)

def visual_summary(tf_signals, tf_trends):
    def arrow(sig):
        if "COMPRAR" in sig: return "🟢"
        if "VENDER" in sig: return "🔴"
        return "🟡"
    parts=[f"{tf} → {arrow(tf_signals.get(tf,'🟡'))}" for tf in ("1H","4H","1D")]
    line_sig="  •  ".join(parts)
    cats=[]
    for tf in ("1H","4H","1D"):
        t=tf_trends.get(tf,"")
        if "Alcista" in t: cats.append("alcista")
        elif "Bajista" in t: cats.append("bajista")
        elif "Lateral" in t: cats.append("lateral")
    count={k:cats.count(k) for k in ("alcista","bajista","lateral")}
    general=max(count,key=count.get) if any(count.values()) else "lateral"
    if general=="alcista": trend="🔺 Tendencia general: Alcista"
    elif general=="bajista": trend="🔻 Tendencia general: Bajista"
    else: trend="↔️ Tendencia general: Lateral"
    return line_sig,trend

def build_message(symbol, mode="ALL"):
    msg_parts=["```",f"{symbol}/USDT  •  Exchange: {EXCHANGE}","="*38]
    tf_signals,tf_trends={},{}

    tfs = TIMEFRAMES if mode=="ALL" else {mode:TIMEFRAMES[mode]}
    for label,tf in tfs.items():
        d=get_analysis(symbol,tf)
        block,sig,trend=make_block(label,d)
        msg_parts.append(block)
        msg_parts.append("="*38)
        tf_signals[label]=sig
        tf_trends[label]=trend

    if len(tfs)>1:
        line_sig,line_trend=visual_summary(tf_signals,tf_trends)
        msg_parts.append("🔚 RESUMEN:")
        msg_parts.append(line_sig)
        msg_parts.append(line_trend)
    msg_parts.append("```")
    return "\n".join(msg_parts)

# ======== TELEGRAM ========

def send_message(chat_id, text):
    requests.post(f"{API_URL()}/sendMessage", data={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }, timeout=20)

def poll_updates():
    offset=None
    print("🤖 Bot activo. Escribe: BTC | ETH | SOL | XRP | DOGE | LTC | BNB | ADA (+ 1H/4H/1D/ALL)")
    while True:
        try:
            params={"timeout":50}
            if offset: params["offset"]=offset
            resp=requests.get(f"{API_URL()}/getUpdates",params=params,timeout=60).json()
            for upd in resp.get("result",[]):
                offset=upd["update_id"]+1
                msg=upd.get("message",{})
                text=(msg.get("text") or "").strip()
                chat_id=msg["chat"]["id"]
                if not text: continue

                tokens=text.upper().split()
                base=tokens[0]
                if base in SUPPORTED:
                    mode="ALL"
                    if len(tokens)>1 and tokens[1] in ("1H","4H","1D","ALL"):
                        mode=tokens[1]
                    try:
                        message=build_message(base,mode)
                        send_message(chat_id,message)
                    except Exception as e:
                        send_message(chat_id,f"❌ Error: {type(e).__name__}")
        except Exception as e:
            print("Error polling:",e)
            time.sleep(3)

if __name__=="__main__":
    poll_updates()
