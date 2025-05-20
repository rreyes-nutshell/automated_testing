import os
import subprocess
import requests
from utils.logging import debug_log
from dotenv import load_dotenv

# Load .env from instance/ folder
base_dir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(base_dir, "instance", ".env")
if not os.path.exists(env_path):
    env_path = os.path.join(base_dir, "..", "instance", ".env")


def send_to_ollama(prompt: str) -> str:
    debug_log("Entered")
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })
    output = response.json()["response"]
    debug_log("Exited")
    return output

def run_playwright_action(step: str):
    debug_log(f"Running Playwright step: {step}")
    result = subprocess.run(["echo", step], capture_output=True, text=True)
    return result.stdout.strip()
