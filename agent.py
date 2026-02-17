import requests, time, subprocess
import psutil

API_IP = "127.0.0.1"
API_PORT = "5000"
API_URL = f"http://{API_IP}:{API_PORT}"
TOKEN = "secret123"
AGENT_ID = "agent01"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

# Execute a simple command and return its stdout
def simple_command(command: str):
    result = subprocess.run(command.split(), capture_output=True, text=True)
    return result.returncode, result.stdout

# Main loop reaching the api server, first send ID and monitoring datas, then if a command was sended,
# running it and send back its stdout
while True:
    try:
        requests.post(
            f"{API_URL}/agent/data",
            headers=HEADERS,
            json={
                "agent_id": AGENT_ID,
                "cpu": psutil.cpu_percent(),
                "ram": psutil.virtual_memory().percent
            }
        )

        response = requests.get(
            f"{API_URL}/agent/command/{AGENT_ID}",
            headers=HEADERS
        ).json()

        if response["command"]:
            output = simple_command(response["command"])

            requests.post(
                f"{API_URL}/agent/result",
                headers=HEADERS,
                json={
                    "command_id": response["id"],
                    "output": output
                }
            )

    except requests.exceptions.ConnectionError as e:
        print ("API unreacheabble")

    time.sleep(0.5)

