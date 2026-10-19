with open("/home/agentuser/muse/muke.py", "r", encoding="utf-8") as f:
    text = f.read()

# Remove duplicate definitions if any
while text.count("HB_API_KEY = ") > 1:
    # Keep only the first one
    first_idx = text.find("HB_API_KEY = ")
    second_idx = text.find("HB_API_KEY = ", first_idx + 13)
    # Remove the second block or clean up
    # Let us do a clean rewrite instead of complex string slicing
    break

# Let us do a clean generation of muke.py from backup
