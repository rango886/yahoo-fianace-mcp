import json
from typing import Literal, Optional

import pandas as pd
from requests import Session
from yfinance import Ticker

def _dataframe_to_json(data) -> str:
    """Converts various data types (DataFrame, Series, dict, list) to a JSON string."""
    if isinstance(data, (pd.DataFrame, pd.Series)):
        # Use orient='split' for better structure, handle dates
        return data.to_json(orient="split", date_format="iso")
    elif isinstance(data, (dict, list)):
        # Use json.dumps for dicts and lists, handle potential non-serializable types
        return json.dumps(data, default=str)
    else:
        # Fallback for other types, attempt default string conversion
        return json.dumps(str(data))

class YahooFinance:
    def __init__(self, session: Session | None = None, verify: bool = True) -> None:
        self.session = session or Session()
        self.session.verify = verify

    def get_current_stock_price(self, symbol: str) -> str:
        """Get the current stock price based on stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
        """
        try:
            stock = Ticker(ticker=symbol).info
            current_price = stock.get(
                "regularMarketPrice", stock.get("currentPrice")
            )
            if current_price is not None:
                return f"{current_price:.4f}"
            else:
                # Attempt to get previous close if market price is unavailable
                prev_close = stock.get("previousClose")
                if prev_close is not None:
                    return f"{prev_close:.4f} (Previous Close)"
                else:
                    return f"Couldn't fetch current or previous price for {symbol}"
        except Exception as e:
            return f"Error fetching price for {symbol}: {e}"

    def get_stock_price_by_date(self, symbol: str, date: str) -> str:
        """Get the stock closing price for a given stock symbol on a specific date.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
            date (str): The date in YYYY-MM-DD format.
        """
        try:
            stock = Ticker(ticker=symbol)
            # Fetch slightly more data to handle potential non-trading days
            price_data = stock.history(start=date, end=pd.to_datetime(date) + pd.Timedelta(days=1))
            if not price_data.empty:
                return f"{price_data.iloc[0]['Close']:.4f}"
            else:
                return f"No price data found for {symbol} on or immediately after {date}."
        except Exception as e:
            return f"Error fetching price for {symbol} on {date}: {e}"

    def get_stock_price_date_range(
        self, symbol: str, start_date: str, end_date: str
    ) -> str:
        """Get the closing stock prices for a given date range for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
            start_date (str): The start date in YYYY-MM-DD format.
            end_date (str): The end date in YYYY-MM-DD format.
        """
        try:
            stock = Ticker(ticker=symbol)
            prices = stock.history(start=start_date, end=end_date)
            if prices.empty:
                return f"No price data found for {symbol} between {start_date} and {end_date}."
            return _dataframe_to_json(prices['Close'])
        except Exception as e:
            return f"Error fetching price range for {symbol}: {e}"

    def get_historical_stock_prices(
        self,
        symbol: str,
        period: Literal[
            "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
        ] = "1mo",
        interval: Literal[
            "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"
        ] = "1d",
    ) -> str:
        """Get historical stock prices (OHLCV) for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
            period (str): The period for historical data. Defaults to "1mo".
                    Valid periods: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
            interval (str): The interval between data points. Defaults to "1d".
                    Valid intervals: "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"
                    Note: Intraday data (<1d) availability depends on the period. 1m is typically available for the last 7 days.
        """
        try:
            stock = Ticker(ticker=symbol)
            prices = stock.history(period=period, interval=interval)
            if prices.empty:
                 return f"No historical data found for {symbol} with period={period}, interval={interval}."
            # Return OHLCV data
            return _dataframe_to_json(prices[['Open', 'High', 'Low', 'Close', 'Volume']])
        except Exception as e:
            return f"Error fetching historical prices for {symbol}: {e}"

    def get_dividends(self, symbol: str) -> str:
        """Get dividends for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
        """
        try:
            stock = Ticker(ticker=symbol)
            dividends = stock.dividends
            if dividends.empty:
                return f"No dividend data found for {symbol}."
            return _dataframe_to_json(dividends)
        except Exception as e:
            return f"Error fetching dividends for {symbol}: {e}"

    def get_income_statement(
        self, symbol: str, freq: Literal["yearly", "quarterly", "trailing"] = "yearly"
    ) -> str:
        """Get income statement for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
            freq (str): At what frequency to get income statement. Defaults to "yearly".
                    Valid frequencies: "yearly", "quarterly", "trailing" (Trailing Twelve Months)
        """
        try:
            stock = Ticker(ticker=symbol)
            # Note: 'trailing' might not be directly supported by get_income_stmt, yfinance handles TTM differently.
            # Using income_stmt property might be more reliable. freq='quarterly' for quarterly.
            if freq == "quarterly":
                 data = stock.quarterly_income_stmt
            else: # Default to yearly
                 data = stock.income_stmt

            if isinstance(data, pd.DataFrame) and not data.empty:
                return _dataframe_to_json(data)
            elif isinstance(data, pd.DataFrame) and data.empty:
                 return f"No {freq} income statement data found for {symbol}."
            else:
                 return f"Unexpected data type received for income statement: {type(data)}"
        except Exception as e:
            return f"Error fetching {freq} income statement for {symbol}: {e}"

    def get_cashflow(
        self, symbol: str, freq: Literal["yearly", "quarterly", "trailing"] = "yearly"
    ) -> str:
        """Get cashflow statement for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
            freq (str): At what frequency to get cashflow statements. Defaults to "yearly".
                    Valid frequencies: "yearly", "quarterly", "trailing" (Trailing Twelve Months)
        """
        try:
            stock = Ticker(ticker=symbol)
            if freq == "quarterly":
                data = stock.quarterly_cashflow
            # elif freq == "trailing": # yfinance might calculate TTM separately or via properties
            #     data = stock.ttm_cashflow # Check if this property exists/works reliably
            else: # Default to yearly
                data = stock.cashflow

            if isinstance(data, pd.DataFrame) and not data.empty:
                return _dataframe_to_json(data)
            elif isinstance(data, pd.DataFrame) and data.empty:
                 return f"No {freq} cashflow data found for {symbol}."
            else:
                 return f"Unexpected data type received for cashflow: {type(data)}"
        except Exception as e:
            return f"Error fetching {freq} cashflow for {symbol}: {e}"

    def get_earning_dates(self, symbol: str, limit: int = 12) -> str:
        """Get earning dates (past and upcoming).

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
            limit (int): Max amount of upcoming and recent earnings dates to return. Default 12.
        """
        try:
            stock = Ticker(ticker=symbol)
            # get_earnings_dates is deprecated, use calendar or earnings_dates instead
            # earning_dates = stock.get_earnings_dates(limit=limit) # Deprecated
            earning_dates = stock.earnings_dates

            if isinstance(earning_dates, pd.DataFrame) and not earning_dates.empty:
                 earning_dates = earning_dates.reset_index() # Flatten MultiIndex if present
                 earning_dates['Earnings Date'] = earning_dates['Earnings Date'].dt.strftime('%Y-%m-%d') # Format date
                 return _dataframe_to_json(earning_dates.head(limit)) # Apply limit after fetching
            elif isinstance(earning_dates, pd.DataFrame) and earning_dates.empty:
                 # Try calendar as fallback
                 calendar_info = stock.calendar
                 if calendar_info is not None and 'Earnings Date' in calendar_info.index:
                     # Format calendar output if needed
                     return _dataframe_to_json(calendar_info)
                 else:
                    return f"No earnings dates found for {symbol} via earnings_dates or calendar."
            else:
                return f"Unexpected data type received for earnings dates: {type(earning_dates)}"
        except Exception as e:
             return f"Error fetching earning dates for {symbol}: {e}"

    def get_news(self, symbol: str) -> str:
        """Get recent news for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
        """
        try:
            stock = Ticker(ticker=symbol)
            news = stock.news
            if not news:
                return f"No recent news found for {symbol}."
            # The news format is typically a list of dictionaries, already JSON-friendly
            return _dataframe_to_json(news)
        except Exception as e:
            return f"Error fetching news for {symbol}: {e}"

    # --- Newly Added Methods ---

    def get_balance_sheet(
        self, symbol: str, freq: Literal["yearly", "quarterly"] = "yearly"
    ) -> str:
        """Get balance sheet for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
            freq (str): At what frequency to get the balance sheet. Defaults to "yearly".
                    Valid frequencies: "yearly", "quarterly"
        """
        try:
            stock = Ticker(ticker=symbol)
            if freq == "quarterly":
                data = stock.quarterly_balance_sheet
            else: # Default to yearly
                data = stock.balance_sheet

            if isinstance(data, pd.DataFrame) and not data.empty:
                return _dataframe_to_json(data)
            elif isinstance(data, pd.DataFrame) and data.empty:
                 return f"No {freq} balance sheet data found for {symbol}."
            else:
                 return f"Unexpected data type received for balance sheet: {type(data)}"
        except Exception as e:
            return f"Error fetching {freq} balance sheet for {symbol}: {e}"

    def get_company_info(self, symbol: str) -> str:
        """Get comprehensive company information for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
        """
        try:
            stock = Ticker(ticker=symbol)
            info_data = stock.info
            if not info_data:
                # Fallback to fast_info if info is empty
                info_data = stock.fast_info
                if not info_data:
                   return f"Could not retrieve company info or fast_info for {symbol}."

            # info_data is a dict, directly serializable
            return _dataframe_to_json(info_data)
        except Exception as e:
            return f"Error fetching company info for {symbol}: {e}"

    def get_splits(self, symbol: str) -> str:
        """Get stock split history for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
        """
        try:
            stock = Ticker(ticker=symbol)
            splits = stock.splits
            if splits.empty:
                return f"No stock split data found for {symbol}."
            return _dataframe_to_json(splits)
        except Exception as e:
            return f"Error fetching splits for {symbol}: {e}"

    def get_recommendations(self, symbol: str) -> str:
        """Get analyst recommendations history for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
        """
        try:
            stock = Ticker(ticker=symbol)
            recommendations = stock.recommendations
            if recommendations is None or (isinstance(recommendations, pd.DataFrame) and recommendations.empty):
                return f"No recommendation data found for {symbol}."
            # Handle potential None or empty DataFrame
            return _dataframe_to_json(recommendations if recommendations is not None else pd.DataFrame())
        except Exception as e:
            return f"Error fetching recommendations for {symbol}: {e}"

    def get_analyst_price_targets(self, symbol: str) -> str:
        """Get analyst price targets for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
        """
        try:
            stock = Ticker(ticker=symbol)
            targets = stock.analyst_price_target
            if targets is None or (isinstance(targets, pd.DataFrame) and targets.empty):
                 return f"No analyst price target data found for {symbol}."
            return _dataframe_to_json(targets if targets is not None else pd.DataFrame())
        except Exception as e:
            return f"Error fetching analyst price targets for {symbol}: {e}"

    def get_major_holders(self, symbol: str) -> str:
        """Get major holders information for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
        """
        try:
            stock = Ticker(ticker=symbol)
            holders = stock.major_holders
            if holders is None or holders.empty:
                return f"No major holders data found for {symbol}."
            return _dataframe_to_json(holders)
        except Exception as e:
            return f"Error fetching major holders for {symbol}: {e}"

    def get_institutional_holders(self, symbol: str) -> str:
        """Get institutional holders information for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
        """
        try:
            stock = Ticker(ticker=symbol)
            holders = stock.institutional_holders
            if holders is None or holders.empty:
                return f"No institutional holders data found for {symbol}."
            return _dataframe_to_json(holders)
        except Exception as e:
            return f"Error fetching institutional holders for {symbol}: {e}"

    def get_mutualfund_holders(self, symbol: str) -> str:
        """Get mutual fund holders information for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
        """
        try:
            stock = Ticker(ticker=symbol)
            holders = stock.mutualfund_holders
            if holders is None or holders.empty:
                return f"No mutual fund holders data found for {symbol}."
            return _dataframe_to_json(holders)
        except Exception as e:
            return f"Error fetching mutual fund holders for {symbol}: {e}"

    def get_option_expiration_dates(self, symbol: str) -> str:
        """Get available option expiration dates for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
        """
        try:
            stock = Ticker(ticker=symbol)
            expirations = stock.options
            if not expirations:
                return f"No option expiration dates found for {symbol}."
            # expirations is a tuple of strings
            return _dataframe_to_json(list(expirations))
        except Exception as e:
            return f"Error fetching option expiration dates for {symbol}: {e}"

    def get_option_chain(self, symbol: str, date: str) -> str:
        """Get the full option chain (calls and puts) for a specific expiration date.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
            date (str): The expiration date in YYYY-MM-DD format. Get available dates from get_option_expiration_dates.
        """
        try:
            stock = Ticker(ticker=symbol)
            # Validate date format if needed, though yfinance might handle it
            if date not in stock.options:
                return f"Invalid or unavailable expiration date: {date}. Use get_option_expiration_dates to see available dates."
            chain = stock.option_chain(date)
            # chain object has .calls and .puts DataFrames
            result = {
                "calls": json.loads(_dataframe_to_json(chain.calls)), # Convert DataFrame JSON string back to dict
                "puts": json.loads(_dataframe_to_json(chain.puts))    # Convert DataFrame JSON string back to dict
            }
            return _dataframe_to_json(result)
        except Exception as e:
            return f"Error fetching option chain for {symbol} on {date}: {e}"

    def get_sustainability(self, symbol: str) -> str:
        """Get sustainability (ESG) scores for a given stock symbol.

        Args:
            symbol (str): Stock symbol in Yahoo Finance format.
        """
        try:
            stock = Ticker(ticker=symbol)
            sustainability = stock.sustainability
            if sustainability is None or sustainability.empty:
                return f"No sustainability (ESG) data found for {symbol}."
            return _dataframe_to_json(sustainability)
        except Exception as e:
            return f"Error fetching sustainability data for {symbol}: {e}"
        
if __name__ == "__main__":
    yahoo_client = YahooFinance()
    symbol = "AAPL"
    r = yahoo_client.get_current_stock_price(symbol=symbol)
    print(r)