"""
Quick test to verify Ollama is installed, running, and responding.
Run: poetry run python linux_playground/utils/tools/test_ollama.py
"""
import platform
import shutil
import subprocess
import urllib.request
import urllib.error

MODEL = "gemma2:9b"
OLLAMA_URL = "http://localhost:11434"


def check_os():
    """Step 1: Detect OS."""
    os_name = platform.system()
    print(f"  OS: {os_name} ({platform.platform()})")
    return os_name


def check_installed(os_name: str) -> bool:
    """Step 2: Check if Ollama binary is installed."""
    # shutil.which checks PATH on both Windows and Linux
    ollama_in_path = shutil.which("ollama")
    if ollama_in_path:
        print(f"  Found in PATH: {ollama_in_path}")
        return True

    # Windows-specific: check default install location
    if os_name == "Windows":
        import os
        default_path = os.path.join(
            os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe"
        )
        if os.path.isfile(default_path):
            print(f"  Found at default location: {default_path}")
            return True

    print("  Ollama binary NOT found!")
    print("  Run setup_ollama.py to install it.")
    return False


def check_server_alive() -> bool:
    """Step 3: Check if Ollama server is reachable (TCP HTTP on port 11434)."""
    try:
        resp = urllib.request.urlopen(OLLAMA_URL, timeout=5)
        body = resp.read().decode()
        print(f"  Server responded: {body.strip()}")
        return True
    except urllib.error.URLError as e:
        print(f"  Server NOT reachable at {OLLAMA_URL}")
        print(f"  Error: {e.reason}")
        print("  Start it with: ollama serve")
        return False


def check_model_available() -> bool:
    """Step 4: Check if the model is pulled/available locally."""
    try:
        import ollama as ollama_client
        models = ollama_client.list()
        # models.models is a list of Model objects
        model_names = [m.model for m in models.models]
        if any(MODEL in name for name in model_names):
            matched = [n for n in model_names if MODEL in n][0]
            print(f"  Model '{matched}' is available locally")
            return True
        else:
            print(f"  Model '{MODEL}' NOT found locally")
            print(f"  Available models: {model_names or 'none'}")
            print(f"  Pull it with: ollama pull {MODEL}")
            return False
    except Exception as e:
        print(f"  Could not list models: {e}")
        return False


def check_chat() -> bool:
    """Step 5: Send a test prompt and verify we get a response."""
    try:
        import ollama as ollama_client
        response = ollama_client.chat(
            model=MODEL,
            messages=[{"role": "user", "content": "What is 2+2? Answer in one word."}],
        )
        content = response["message"]["content"]
        model_used = response.get("model", "unknown")
        print(f"  Prompt: 'What is 2+2? Answer in one word.'")
        print(f"  Response: {content}")
        print(f"  Model: {model_used}")
        return True
    except Exception as e:
        print(f"  Chat failed: {e}")
        return False


def main():
    print("=" * 50)
    print("  Ollama Health Check")
    print("=" * 50)

    results = {}

    print("\n[1/5] Detecting OS...")
    os_name = check_os()
    results["OS Detection"] = True

    print("\n[2/5] Checking Ollama installation...")
    results["Installed"] = check_installed(os_name)

    print("\n[3/5] Checking Ollama server (TCP port 11434)...")
    results["Server Alive"] = check_server_alive()

    if results["Server Alive"]:
        print(f"\n[4/5] Checking model '{MODEL}'...")
        results["Model Available"] = check_model_available()
    else:
        print(f"\n[4/5] Skipping model check (server not running)")
        results["Model Available"] = False

    if results["Model Available"]:
        print("\n[5/5] Testing chat...")
        results["Chat Works"] = check_chat()
    else:
        print("\n[5/5] Skipping chat test (model not available)")
        results["Chat Works"] = False

    # Summary
    print("\n" + "=" * 50)
    print("  Results")
    print("=" * 50)
    all_passed = True
    for check, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {check}")
        if not passed:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("  All checks passed! Ollama is fully operational.")
    else:
        print("  Some checks failed. See details above.")
    print("=" * 50)


if __name__ == "__main__":
    main()
