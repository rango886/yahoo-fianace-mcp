import sys
import json
import traceback
from typing import Any, Dict, Optional, Literal

from mcp.server.fastmcp import FastMCP
from src.tool import YahooFinance

SERVER_NAME = "yahoo_finance_engine"
SERVER_VERSION = "0.3.0" # Bump version for major refactor

# Initialize FastMCP server
mcp = FastMCP(SERVER_NAME,port=7080)

# Initialize the YahooFinance client once
try:
    yahoo_client = YahooFinance()
    print(f"[{SERVER_NAME} Info] YahooFinance client initialized successfully.", file=sys.stderr)
except Exception as init_e:
    print(f"[{SERVER_NAME} Error] Failed to initialize YahooFinance client: {init_e}", file=sys.stderr)
    # If client fails to init, maybe exit or define tools that return errors?
    # For now, let it proceed, but tool calls will likely fail.
    yahoo_client = None # Indicate client is unavailable

# Helper function for error handling within tools
def _handle_tool_error(command_name: str, params: Dict[str, Any], e: Exception) -> Dict[str, Any]:
    error_trace = traceback.format_exc()
    error_msg = f"Error executing command '{command_name}' with params {params}: {e}"
    print(f"[{SERVER_NAME} Error] {error_msg}\n{error_trace}", file=sys.stderr)
    return {"error": f"Server error during '{command_name}': {e}", "code": -32000}

# --- Define MCP Tools for each YahooFinance method --- (Error handling added)

@mcp.tool()
def get_current_stock_price(symbol: str) -> str | Dict[str, Any]:
    """Get the current stock price based on stock symbol.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format (e.g., 'AAPL').
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_current_stock_price(symbol=symbol)
    except Exception as e:
        return _handle_tool_error("get_current_stock_price", {"symbol": symbol}, e)

@mcp.tool()
def get_stock_price_by_date(symbol: str, date: str) -> str | Dict[str, Any]:
    """Get the stock closing price for a given stock symbol on a specific date.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
        date (str): The date in YYYY-MM-DD format.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_stock_price_by_date(symbol=symbol, date=date)
    except Exception as e:
        return _handle_tool_error("get_stock_price_by_date", {"symbol": symbol, "date": date}, e)

@mcp.tool()
def get_stock_price_date_range(symbol: str, start_date: str, end_date: str) -> str | Dict[str, Any]:
    """Get the closing stock prices for a given date range for a given stock symbol.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
        start_date (str): The start date in YYYY-MM-DD format.
        end_date (str): The end date in YYYY-MM-DD format.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_stock_price_date_range(symbol=symbol, start_date=start_date, end_date=end_date)
    except Exception as e:
        return _handle_tool_error("get_stock_price_date_range", {"symbol": symbol, "start_date": start_date, "end_date": end_date}, e)

@mcp.tool()
def get_historical_stock_prices(
    symbol: str,
    period: Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"] = "1mo",
    interval: Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"] = "1d",
) -> str | Dict[str, Any]:
    """Get historical stock prices (OHLCV) for a given stock symbol.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
        period (str): The period for historical data. Defaults to "1mo". Valid: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max".
        interval (str): The interval between data points. Defaults to "1d". Valid: "1m", "2m", ..., "1d", "5d", "1wk", "1mo", "3mo". Intraday data availability depends on period.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_historical_stock_prices(symbol=symbol, period=period, interval=interval)
    except Exception as e:
        return _handle_tool_error("get_historical_stock_prices", {"symbol": symbol, "period": period, "interval": interval}, e)

@mcp.tool()
def get_dividends(symbol: str) -> str | Dict[str, Any]:
    """Get dividends history for a given stock symbol.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_dividends(symbol=symbol)
    except Exception as e:
        return _handle_tool_error("get_dividends", {"symbol": symbol}, e)

@mcp.tool()
def get_income_statement(symbol: str, freq: Literal["yearly", "quarterly"] = "yearly") -> str | Dict[str, Any]:
    """Get income statement for a given stock symbol.
       Note: 'trailing' frequency might not be reliably supported by the underlying library.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
        freq (str): Frequency ("yearly", "quarterly"). Defaults to "yearly".
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        # Note: Passing 'trailing' might cause issues based on src/tool.py comments
        # Consider validating freq here or rely on underlying method's error handling.
        actual_freq = freq if freq in ["yearly", "quarterly"] else "yearly"
        return yahoo_client.get_income_statement(symbol=symbol, freq=actual_freq)
    except Exception as e:
        return _handle_tool_error("get_income_statement", {"symbol": symbol, "freq": freq}, e)

@mcp.tool()
def get_cashflow(symbol: str, freq: Literal["yearly", "quarterly"] = "yearly") -> str | Dict[str, Any]:
    """Get cashflow statement for a given stock symbol.
       Note: 'trailing' frequency might not be reliably supported by the underlying library.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
        freq (str): Frequency ("yearly", "quarterly"). Defaults to "yearly".
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        actual_freq = freq if freq in ["yearly", "quarterly"] else "yearly"
        return yahoo_client.get_cashflow(symbol=symbol, freq=actual_freq)
    except Exception as e:
        return _handle_tool_error("get_cashflow", {"symbol": symbol, "freq": freq}, e)

@mcp.tool()
def get_earning_dates(symbol: str, limit: int = 12) -> str | Dict[str, Any]:
    """Get earning dates (past and upcoming) for a given stock symbol.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
        limit (int): Max amount of upcoming and recent earnings dates to return. Default 12.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_earning_dates(symbol=symbol, limit=limit)
    except Exception as e:
        return _handle_tool_error("get_earning_dates", {"symbol": symbol, "limit": limit}, e)

# @mcp.tool()
def get_news(symbol: str) -> str | Dict[str, Any]:
    """Get recent news for a given stock symbol.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_news(symbol=symbol)
    except Exception as e:
        return _handle_tool_error("get_news", {"symbol": symbol}, e)

@mcp.tool()
def get_balance_sheet(symbol: str, freq: Literal["yearly", "quarterly"] = "yearly") -> str | Dict[str, Any]:
    """Get balance sheet for a given stock symbol.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
        freq (str): Frequency ("yearly", "quarterly"). Defaults to "yearly".
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_balance_sheet(symbol=symbol, freq=freq)
    except Exception as e:
        return _handle_tool_error("get_balance_sheet", {"symbol": symbol, "freq": freq}, e)

@mcp.tool()
def get_company_info(symbol: str) -> str | Dict[str, Any]:
    """Get comprehensive company information (like sector, employees, summary) for a given stock symbol.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_company_info(symbol=symbol)
    except Exception as e:
        return _handle_tool_error("get_company_info", {"symbol": symbol}, e)

@mcp.tool()
def get_splits(symbol: str) -> str | Dict[str, Any]:
    """Get stock split history for a given stock symbol.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_splits(symbol=symbol)
    except Exception as e:
        return _handle_tool_error("get_splits", {"symbol": symbol}, e)

@mcp.tool()
def get_recommendations(symbol: str) -> str | Dict[str, Any]:
    """Get analyst recommendations history (e.g., Buy, Hold, Sell ratings) for a given stock symbol.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_recommendations(symbol=symbol)
    except Exception as e:
        return _handle_tool_error("get_recommendations", {"symbol": symbol}, e)

@mcp.tool()
def get_analyst_price_targets(symbol: str) -> str | Dict[str, Any]:
    """Get analyst price targets (high, low, mean, median) for a given stock symbol.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_analyst_price_targets(symbol=symbol)
    except Exception as e:
        return _handle_tool_error("get_analyst_price_targets", {"symbol": symbol}, e)

@mcp.tool()
def get_major_holders(symbol: str) -> str | Dict[str, Any]:
    """Get major holders (insiders, institutions percentage) information for a given stock symbol.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_major_holders(symbol=symbol)
    except Exception as e:
        return _handle_tool_error("get_major_holders", {"symbol": symbol}, e)

@mcp.tool()
def get_institutional_holders(symbol: str) -> str | Dict[str, Any]:
    """Get institutional holders (list of institutions holding the stock) information.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_institutional_holders(symbol=symbol)
    except Exception as e:
        return _handle_tool_error("get_institutional_holders", {"symbol": symbol}, e)

@mcp.tool()
def get_mutualfund_holders(symbol: str) -> str | Dict[str, Any]:
    """Get mutual fund holders information for a given stock symbol.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_mutualfund_holders(symbol=symbol)
    except Exception as e:
        return _handle_tool_error("get_mutualfund_holders", {"symbol": symbol}, e)

@mcp.tool()
def get_option_expiration_dates(symbol: str) -> str | Dict[str, Any]:
    """Get available option expiration dates for a given stock symbol.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_option_expiration_dates(symbol=symbol)
    except Exception as e:
        return _handle_tool_error("get_option_expiration_dates", {"symbol": symbol}, e)

@mcp.tool()
def get_option_chain(symbol: str, date: str) -> str | Dict[str, Any]:
    """Get the full option chain (calls and puts) for a specific expiration date.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
        date (str): The expiration date in YYYY-MM-DD format. Get available dates from get_option_expiration_dates.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_option_chain(symbol=symbol, date=date)
    except Exception as e:
        return _handle_tool_error("get_option_chain", {"symbol": symbol, "date": date}, e)

@mcp.tool()
def get_sustainability(symbol: str) -> str | Dict[str, Any]:
    """Get sustainability (ESG scores - Environment, Social, Governance) for a given stock symbol.

    Args:
        symbol (str): Stock symbol in Yahoo Finance format.
    """
    if not yahoo_client: return {"error": "YahooFinance client not initialized", "code": -32001}
    try:
        return yahoo_client.get_sustainability(symbol=symbol)
    except Exception as e:
        return _handle_tool_error("get_sustainability", {"symbol": symbol}, e)


# --- Server Run --- (Keep this part)
if __name__ == "__main__":
    print(f"--- Starting {SERVER_NAME} MCP Server v{SERVER_VERSION} (using FastMCP) ---", file=sys.stderr)
    if yahoo_client is None:
        print(f"[{SERVER_NAME} Critical Error] Yahoo client failed to initialize. Server might not function.", file=sys.stderr)
        # Optionally exit if client init is critical
        # sys.exit(1)

    try:
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"--- Error running MCP server: {e} ---", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    print(f"--- {SERVER_NAME} MCP Server finished ---", file=sys.stderr)
