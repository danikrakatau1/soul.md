import sys
sys.path.insert(0, "/home/agentuser/.local/lib/python3.12/site-packages")
from hyperbrowser import Hyperbrowser

client = Hyperbrowser(api_key="hb_cdfc571755daac8231b0c1812ec4")
try:
    res = client.web.fetch({"url": "https://muse.ai"})
    print("Web fetch success! Content snippet:", res.content[:200] if hasattr(res, 'content') else res)
except Exception as e:
    print("Web fetch error:", e)
