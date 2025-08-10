import os

from agents.tool import HostedMCPTool
from dotenv import load_dotenv

load_dotenv()

tavily_search_tool = HostedMCPTool(
    {
        "type": "mcp",
        "server_label": "tavily",
        "server_url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={os.getenv('TAVILY_API_KEY')}",
        "require_approval": "never",
    }
)
