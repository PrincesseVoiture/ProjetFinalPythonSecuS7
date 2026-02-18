import requests, time, subprocess
import psutil

API_IP = "127.0.0.1"
API_PORT = "5000"
API_URL = f"http://{API_IP}:{API_PORT}"
TOKEN = "secret123"
AGENT_ID = "007"

HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def simple_command(command: str):
    """Exécute une commande cross-platform et retourne (returncode, stdout)."""
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    stdout_clean = (result.stdout + result.stderr).replace('\r\n', '\n')
    return result.returncode, stdout_clean

while True:
    try:
        # envoi stats
        requests.post(
            f"{API_URL}/agent/data",
            headers=HEADERS,
            json={"agent_id": AGENT_ID, "cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent}
        )

        # récupération commande
        response = requests.get(f"{API_URL}/agent/command/{AGENT_ID}", headers=HEADERS).json()

        if response["command"]:
            returncode, stdout = simple_command(response["command"])
            requests.post(
                f"{API_URL}/agent/result",
                headers=HEADERS,
                json={"command_id": response["id"], "output": {"stdout": stdout, "returncode": returncode}}
            )

    except requests.exceptions.ConnectionError:
        print("API unreachable")

    time.sleep(2)
