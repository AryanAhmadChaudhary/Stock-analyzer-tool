from fastmcp import FastMCP
from analysis import analyze_stock

mcp = FastMCP("this is my tool for stock analysis")


@mcp.tool()
def stock_analysis(ticker: str, period="6mo"):
    return analyze_stock(ticker,period)

if __name__ == "__main__":
    mcp.run()