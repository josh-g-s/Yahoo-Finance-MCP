from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

import yfinance as yf
from typing import List, Any
import json

server = Server("yahoo-finance-mcp")


@server.list_tools()
async def list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name="get-stock-price",
            description="Get current stock price and basic info for a ticker symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, MSFT, TSLA)",
                    },
                },
                "required": ["ticker"],
            },
        ),
        types.Tool(
            name="get-stock-history",
            description="Get historical stock price data",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol",
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)",
                        "default": "1mo",
                    },
                },
                "required": ["ticker"],
            },
        ),
        types.Tool(
            name="get-stock-info",
            description="Get detailed company information for a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol",
                    },
                },
                "required": ["ticker"],
            },
        ),
        types.Tool(
            name="get-financials",
            description="Get financial statements (income statement, balance sheet, cash flow)",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol",
                    },
                    "statement_type": {
                        "type": "string",
                        "description": "Type of financial statement: income, balance, cashflow",
                        "enum": ["income", "balance", "cashflow"],
                        "default": "income",
                    },
                },
                "required": ["ticker"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[types.TextContent]:
    try:
        if name == "get-stock-price":
            ticker = arguments.get("ticker")
            stock = yf.Ticker(ticker)
            info = stock.info

            result = {
                "ticker": ticker,
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "previous_close": info.get("previousClose"),
                "open": info.get("open") or info.get("regularMarketOpen"),
                "day_high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
                "day_low": info.get("dayLow") or info.get("regularMarketDayLow"),
                "volume": info.get("volume") or info.get("regularMarketVolume"),
                "market_cap": info.get("marketCap"),
                "currency": info.get("currency"),
            }

            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get-stock-history":
            ticker = arguments.get("ticker")
            period = arguments.get("period", "1mo")

            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            # Convert DataFrame to dict with date as string
            result = {
                "ticker": ticker,
                "period": period,
                "data": hist.reset_index().to_dict(orient="records"),
            }

            # Convert timestamps to strings for JSON serialization
            for record in result["data"]:
                if "Date" in record:
                    record["Date"] = str(record["Date"])

            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get-stock-info":
            ticker = arguments.get("ticker")
            stock = yf.Ticker(ticker)
            info = stock.info

            # Select key information fields
            result = {
                "ticker": ticker,
                "name": info.get("longName") or info.get("shortName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "description": info.get("longBusinessSummary"),
                "website": info.get("website"),
                "employees": info.get("fullTimeEmployees"),
                "city": info.get("city"),
                "state": info.get("state"),
                "country": info.get("country"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "dividend_yield": info.get("dividendYield"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
            }

            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get-financials":
            ticker = arguments.get("ticker")
            statement_type = arguments.get("statement_type", "income")

            stock = yf.Ticker(ticker)

            if statement_type == "income":
                financials = stock.financials
            elif statement_type == "balance":
                financials = stock.balance_sheet
            elif statement_type == "cashflow":
                financials = stock.cashflow
            else:
                return [types.TextContent(type="text", text=f"Invalid statement type: {statement_type}")]

            # Convert DataFrame to dict
            result = {
                "ticker": ticker,
                "statement_type": statement_type,
                "data": financials.to_dict() if not financials.empty else {},
            }

            # Convert any timestamps to strings
            for key, value in result["data"].items():
                result["data"][key] = {str(k): v for k, v in value.items()}

            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="yahoo-finance-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
