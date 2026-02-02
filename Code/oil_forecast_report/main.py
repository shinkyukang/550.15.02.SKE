from marketagents.graph.trading_graph import MarketAgentsGraph
from marketagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a custom config
config = DEFAULT_CONFIG.copy()

# Initialize with custom config
ma = MarketAgentsGraph(debug=False, config=config)

# Forward propagate
target_date = "2025-12-05"
_, decision = ma.propagate("Brent crude oil price", target_date)
print("[DECISION]", decision)
