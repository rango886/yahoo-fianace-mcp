# Yahoo Finance MCP Server

This project provides a Model Context Protocol (MCP) server that exposes various functions from the `yfinance` library as individual tools. This allows an MCP client (like Claude Desktop) to query Yahoo Finance data.

## Prerequisites

*   **Python:** Ensure you have Python installed (Python 3.8+ recommended).
*   **uv:** This project uses `uv` for environment and package management. If you don't have it, install it following the instructions here: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:a05031113/yahoo-fianace-mcp.git
    cd yahoo-finance # Or your repository directory name
    ```

2.  **Create a virtual environment:**
    It's highly recommended to use a virtual environment. Create one using `uv`:
    ```bash
    uv venv
    ```
    This will create a `.venv` directory.

3.  **Activate the virtual environment:**
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```
    *   On Windows (Git Bash/WSL):
        ```bash
        source .venv/Scripts/activate
        ```
    *   On Windows (Command Prompt/PowerShell):
        ```bash
        .venv\Scripts\activate
        ```
    You should see `(.venv)` at the beginning of your terminal prompt.

4.  **Install dependencies:**
    Install the required Python packages using `uv`:
    ```bash
    uv pip install -r requirements.txt
    ```

## Running the Server

This server communicates via standard input/output (stdio) as expected by MCP. To run the server, simply execute the `main.py` script using the Python interpreter from your activated virtual environment:

```bash
python main.py
```

The server will start and print log messages to standard error (`stderr`), waiting for JSON-RPC requests on standard input (`stdin`).

You would typically configure your MCP client (e.g., in its settings JSON file) to run this command:

```json
{
  "mcpServers": {
    "yahoo_finance_engine": {
      "command": "/path/to/your/yahoo-finance/.venv/bin/python", // Adjust path accordingly
      "args": [
        "/path/to/your/yahoo-finance/main.py" // Adjust path accordingly
      ]
    }
    // ... other servers
  }
}
```

The MCP client will then manage starting and communicating with this server process.

## Available Tools

The server exposes the public methods of the `YahooFinance` class (defined in `src/tool.py`) as individual MCP tools. These include (but are not limited to):

*   `get_current_stock_price(symbol: str)`
*   `get_stock_price_by_date(symbol: str, date: str)`
*   `get_stock_price_date_range(symbol: str, start_date: str, end_date: str)`
*   `get_historical_stock_prices(symbol: str, period: str = "1mo", interval: str = "1d")`
*   `get_dividends(symbol: str)`
*   `get_income_statement(symbol: str, freq: str = "yearly")`
*   `get_cashflow(symbol: str, freq: str = "yearly")`
*   `get_balance_sheet(symbol: str, freq: str = "yearly")`
*   `get_earning_dates(symbol: str, limit: int = 12)`
*   `get_news(symbol: str)`
*   `get_company_info(symbol: str)`
*   `get_splits(symbol: str)`
*   `get_recommendations(symbol: str)`
*   `get_analyst_price_targets(symbol: str)`
*   `get_major_holders(symbol: str)`
*   `get_institutional_holders(symbol: str)`
*   `get_mutualfund_holders(symbol: str)`
*   `get_option_expiration_dates(symbol: str)`
*   `get_option_chain(symbol: str, date: str)`
*   `get_sustainability(symbol: str)`

Refer to the docstrings within `main.py` or `src/tool.py` for details on each tool's parameters.  

Certified by MCP Review. https://mcpreview.com/mcp-servers/a05031113/yahoo-fianace-mcp