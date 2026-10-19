import os
import subprocess
import sys

def setup_netrc(email, token_or_password):
    netrc_path = os.path.expanduser("~/.netrc")
    netrc_content = f"machine surge.sh\n  login {email}\n  password {token_or_password}\n"
    
    # Append or write
    mode = "a" if os.path.exists(netrc_path) else "w"
    with open(netrc_path, mode) as f:
        f.write(netrc_content)
    os.chmod(netrc_path, 0o600)
    print("[+] Credentials written to ~/.netrc successfully.")

def deploy():
    project_path = "/home/agentuser/muse/web_checker"
    print(f"[*] Deploying {project_path} to Surge...")
    
    # Run surge non-interactively using the netrc credentials
    cmd = ["npx", "surge", project_path, "card-syntax-checker.surge.sh"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

if __name__ == "__main__":
    # If user wants to pass email & token/password via env or prompt
    email = os.environ.get("SURGE_EMAIL")
    token = os.environ.get("SURGE_PASSWORD")
    
    if email and token:
        setup_netrc(email, token)
        deploy()
    else:
        print("[-] Please set SURGE_EMAIL and SURGE_PASSWORD environment variables to deploy automatically.")
        print("Example: export SURGE_EMAIL='your@email.com' && export SURGE_PASSWORD='your_password_or_token'")
