#!/usr/bin/env python3
"""
股票持仓市值查询工具
用法: python3 portfolio_tracker.py
"""

import json
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError
import time

# 持仓配置
HOLDINGS = {
    "TSLA": 94.38,
    "MSFT": 126,
    "NVDA": 260,
    "GOOG": 235,
}

CASH = 44067

def get_stock_price(symbol):
    """获取实时股价"""
    time.sleep(0.5)  # 延迟避免频率限制
    
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            result = data["chart"]["result"][0]
            meta = result["meta"]
            price = meta.get("regularMarketPrice", meta.get("previousClose", 0))
            prev_close = meta.get("previousClose", meta.get("chartPreviousClose", price))
            change = price - prev_close if prev_close else 0
            change_pct = (change / prev_close) * 100 if prev_close else 0
            return {
                "price": price,
                "change": change,
                "change_pct": change_pct,
                "currency": meta.get("currency", "USD")
            }
    except Exception as e:
        return {"error": str(e)}

def format_money(value):
    """格式化金额"""
    return f"${value:,.2f}"

def main():
    print("=" * 60)
    print("📊 股票持仓市值查询")
    print("=" * 60)
    print()
    
    stock_data = []
    total_stocks_value = 0
    
    for symbol, shares in HOLDINGS.items():
        print(f"查询 {symbol}...", end=" ", flush=True)
        data = get_stock_price(symbol)
        
        if "error" in data:
            print(f"❌ 错误: {data['error']}")
            continue
        
        price = data["price"]
        market_value = price * shares
        total_stocks_value += market_value
        
        stock_data.append({
            "symbol": symbol,
            "shares": shares,
            "price": price,
            "market_value": market_value,
            "change": data["change"],
            "change_pct": data["change_pct"]
        })
        
        change_emoji = "📈" if data["change"] >= 0 else "📉"
        print(f"${price:,.2f}")
        print(f"   持股: {shares} 股")
        print(f"   市值: {format_money(market_value)}")
        print(f"   涨跌: {change_emoji} ${data['change']:+.2f} ({data['change_pct']:+.2f}%)")
        print()
    
    total_assets = total_stocks_value + CASH
    
    print("-" * 60)
    print(f"💰 股票总市值: {format_money(total_stocks_value)}")
    print(f"💵 现金:        {format_money(CASH)}")
    print(f"📊 总资产:      {format_money(total_assets)}")
    print()
    
    # 计算并显示占比
    print("-" * 60)
    print("📈 持仓占比:")
    print("-" * 60)
    for stock in stock_data:
        pct_of_stocks = (stock["market_value"] / total_stocks_value * 100) if total_stocks_value else 0
        pct_of_total = (stock["market_value"] / total_assets * 100) if total_assets else 0
        print(f"  {stock['symbol']}: 占股票 {pct_of_stocks:.1f}% | 占总资产 {pct_of_total:.1f}%")
    
    cash_pct = (CASH / total_assets * 100) if total_assets else 0
    print(f"  现金:          占总资产 {cash_pct:.1f}%")
    print("=" * 60)

if __name__ == "__main__":
    main()
