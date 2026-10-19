import urllib.request
import urllib.error
import json
import os
import time

TOKENS_FILE = "/home/agentuser/muse/dahl_tokens.json"

def load_tokens():
    if os.path.exists(TOKENS_FILE):
        try:
            with open(TOKENS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_tokens(tokens):
    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

def generate_token():
    url = "https://inference.dahl.global/tokens"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Origin": "https://inference.dahl.global",
        "Referer": "https://inference.dahl.global/"
    }
    try:
        req = urllib.request.Request(url, method="POST", headers=headers)
        resp = urllib.request.urlopen(req, data=b"{}")
        if resp.status == 201:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] Failed to generate token: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"[Error] Failed to generate token: {e}")
    return None

def check_token_balance(token):
    url = "https://inference.dahl.global/tokens/current"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("available_tokens", 0)
    except Exception:
        return None

def farm_tokens(count=5, delay=3):
    tokens = load_tokens()
    print(f"[*] Starting token farming. Current saved tokens: {len(tokens)}")
    for i in range(count):
        print(f"[*] Attempting to generate token {i+1}/{count}...")
        res = generate_token()
        if res and "token" in res:
            token_val = res["token"]
            balance = res.get("available_tokens", 100000000)
            tokens.append({"token": token_val, "balance": balance, "created_at": time.time()})
            save_tokens(tokens)
            print(f"[+] Success! Token saved: {token_val[:15]}... Balance: {balance}")
        else:
            print("[-] Rate limited or failed. Waiting before retry...")
        time.sleep(delay)
    print(f"[*] Total tokens saved now: {len(tokens)}")

def list_balances():
    tokens = load_tokens()
    if not tokens:
        print("[-] No tokens saved yet.")
        return
    print(f"[*] Checking balances for {len(tokens)} tokens...")
    valid_tokens = []
    for idx, item in enumerate(tokens):
        t = item["token"]
        bal = check_token_balance(t)
        if bal is not None:
            print(f"[{idx+1}] {t[:15]}... -> Balance: {bal:,} tokens")
            valid_tokens.append({"token": t, "balance": bal, "created_at": item.get("created_at", time.time())})
        else:
            print(f"[{idx+1}] {t[:15]}... -> INVALID / EXPIRED")
    save_tokens(valid_tokens)

def chat_completion(prompt, model="MiniMaxAI/MiniMax-M2.7"):
    tokens = load_tokens()
    if not tokens:
        print("[-] No tokens available. Generating one...")
        res = generate_token()
        if res and "token" in res:
            tokens.append({"token": res["token"], "balance": res.get("available_tokens", 100000000)})
            save_tokens(tokens)
        else:
            print("[-] Failed to get token.")
            return None

    url = "https://inference.dahl.global/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    data = json.dumps(payload).encode("utf-8")

    for idx, item in enumerate(tokens):
        token = item["token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        try:
            req = urllib.request.Request(url, method="POST", headers=headers)
            resp = urllib.request.urlopen(req, data=data)
            result = json.loads(resp.read().decode("utf-8"))
            content = result["choices"][0]["message"]["content"]
            return content
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            print(f"[-] Token {idx+1} error (HTTP {e.code}): {err_body}")
            if e.code == 429:
                print("[*] Rotating to next token...")
                continue
            elif e.code == 401:
                print("[*] Token invalid, skipping...")
                continue
        except Exception as e:
            print(f"[-] Error: {e}")
            continue
    print("[-] All tokens exhausted or failed.")
    return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "farm":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            farm_tokens(count)
        elif cmd == "balance":
            list_balances()
        elif cmd == "chat":
            prompt = sys.argv[2] if len(sys.argv) > 2 else "Halo, siapa kamu?"
            print(chat_completion(prompt))
    else:
        print("Usage: python dahl_manager.py [farm [count] | balance | chat 'prompt']")
