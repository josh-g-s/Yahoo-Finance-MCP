# Yahoo Finance MCP Server

A lightweight MCP server for accessing Yahoo Finance data. No persistent service required - the server runs only when needed.

## Features

- **get-stock-price**: Get current stock price and basic trading information
- **get-stock-history**: Get historical price data for various time periods
- **get-stock-info**: Get detailed company information
- **get-financials**: Get financial statements (income, balance sheet, cash flow)

## Installation

```bash
pip install -e .
```

## Usage

The server uses stdio for communication (no HTTP server needed). Configure it in your MCP client:

```json
{
  "mcpServers": {
    "yahoo-finance": {
      "command": "python",
      "args": ["-m", "yahoo_finance_mcp"]
    }
  }
}
```

Or if installed globally:

```json
{
  "mcpServers": {
    "yahoo-finance": {
      "command": "yahoo-finance-mcp"
    }
  }
}
```

## Examples

- Get Apple stock price: `get-stock-price` with `{"ticker": "AAPL"}`
- Get Tesla's last 6 months: `get-stock-history` with `{"ticker": "TSLA", "period": "6mo"}`
- Get Microsoft info: `get-stock-info` with `{"ticker": "MSFT"}`
- Get Amazon financials: `get-financials` with `{"ticker": "AMZN", "statement_type": "income"}`
