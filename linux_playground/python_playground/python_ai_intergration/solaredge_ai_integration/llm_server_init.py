import json
import platform
import shutil
import logging
import subprocess
import time

from linux_playground.utils.path_utils.specific_paths import relative_path
import ollama as ollama_client

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        # logging.FileHandler("geeksforgeeks.log"),
                        logging.StreamHandler()
                    ])



logger.debug("Logger initialized")



class OllamaServer:
    PROC_NAME = "ollama"
    def __init__(self, model: str):
        if not is_ollama_installed(os_name=check_os()):
            logger.error("Ollama is not installed. Please run setup_ollama.py first.")
            raise RuntimeError("Ollama not installed, Install it from the setup_ollama.py script.")
        self.model: str = model
        self.server_process = None

    def start(self):
        # Check if the server is already running under our control
        if self.is_alive():
            logger.debug("Ollama server is already running.")
            return

        # Kill any foreign Ollama processes we don't own
        # owned_pid = self.server_process.pid if self.server_process else None
        kill_existing_process_by_name(name=self.PROC_NAME)

        # Start a fresh Ollama server under our control
        logger.debug(f"Starting Ollama server with model: {self.model}")
        self.server_process = subprocess.Popen(["ollama", "run", self.model], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.debug(f"Ollama server started with PID: {self.server_process.pid}")
        time.sleep(5)  # Wait a moment for the server to start
        if self.is_alive():
            logger.debug("Ollama server is alive after starting.")


    def stop(self):
        # Stop the Ollama server
        logger.debug("Stopping Ollama server")
        # Here you would add the code to stop the server process
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
        # either or either kill whole of the processes with the name "ollama" to ensure it's stopped, or just kill the one we started if we have its PID
        kill_existing_process_by_name(name=self.PROC_NAME)
        logger.debug("Ollama server stopped")


    def is_alive(self) -> bool:
        # Check if the server is alive
        logger.debug("Checking if Ollama server is alive")
        # Here you would add the code to check if the server is running
        if self.server_process:
            logger.debug("Ollama server is alive")
            return True
        logger.debug("Ollama server is not alive")
        return False


class OllamaClient:
    def __init__(self, ollama_url: str, model: str):
        self.ollama_url = ollama_url
        self.model = model
    
    def query(self, prompt: str) -> str:
        response = ollama_client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response["message"]["content"]
        model = response.get("model", "unknown")
        prompt_tokens = response.get("prompt_eval_count", 0)
        completion_tokens = response.get("eval_count", 0)
        logger.debug(f"client received model: {model}")
        logger.debug(f"tokens - prompt: {prompt_tokens}, completion: {completion_tokens}, total: {prompt_tokens + completion_tokens}")
        return content



#### utils ######

def kill_existing_process_by_name(name: str, owned_pid: int | None = None) -> int:
    """Kill any running processes matching the given name that we don't control.

    Args:
        name: Process name to match (case-insensitive substring match).
        owned_pid: PID of a process we own (will be spared).

    Returns:
        Number of processes killed.
    """
    import psutil

    killed = 0
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if proc.info["name"] and name.lower() in proc.info["name"].lower():
                logger.debug(f"  Killing foreign '{name}' process (PID {proc.info['pid']})")
                proc.terminate()
                proc.wait(timeout=5)
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
            logger.warning(f"  Could not kill PID {proc.info['pid']}: {e}")
    if killed:
        logger.debug(f"  Killed {killed} foreign '{name}' process(es)")
    else:
        logger.debug(f"  No foreign '{name}' processes found")
    return killed

def check_os():
    """Step 1: Detect OS."""
    os_name = platform.system()
    logger.debug(f"OS: {os_name} ({platform.platform()})")
    return os_name

def is_ollama_installed(os_name: str) -> bool:
    """Step 2: Check if Ollama binary is installed."""
    # shutil.which checks PATH on both Windows and Linux
    ollama_in_path = shutil.which("ollama")
    if ollama_in_path:
        logger.debug(f"  Found in PATH: {ollama_in_path}")
        return True

    # Windows-specific: check default install location
    if os_name == "Windows":
        import os
        default_path = os.path.join(
            os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe"
        )
        if os.path.isfile(default_path):
            logger.debug(f"  Found at default location: {default_path}")
            return True
    logger.debug("Ollama binary NOT found!")
    logger.debug("Run setup_ollama.py to install it.")
    return False

def load_json_config(config_path: str) -> dict:
    """Load JSON configuration from the given path."""
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            logger.debug(f"Loaded config from {config_path}: {config}")
            return config
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        raise





if __name__ == "__main__":
    # load config `config_llm.json
    # kill_existing_process_by_name("ollama")
    config_llm_path = relative_path("config_llm.json")
    conf = load_json_config(config_llm_path)
    model = conf["model"]
    ollama_url = conf["ollama_url"]
    logger.debug(f"Model: {model}")
    logger.debug(f"Ollama URL: {ollama_url}")
    # Initialize and start the Ollama server
    ollama_server = OllamaServer(model)
    ollama_server.start()
    # Initialize the client
    client = OllamaClient(ollama_url, model)
    # Example query
    prompt = "1 + 1 = ?"
    response = client.query(prompt)
    logger.debug(f"Response: {response}")