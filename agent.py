from flask import Flask, request
import subprocess, psutil

# Execute a simple command and return its stdout
def simple_command(command: str):
    result = subprocess.run(command.split(), capture_output=True, text=True)
    return result.returncode, result.stdout


app = Flask(__name__)

# Main Flask route for receiving and sending datas to distant api 
@app.route("/receive", methods=["POST"])
def receive():

    result: dict[str, str] = request.get_json()

    if "command" in result:
        _, command_stdout = simple_command(result["command"])
        return command_stdout, 200

    elif "monitoring" in result:
        if result["monitoring"] != "True":
            return "ko", 500
        
        result: dict[str, str] = {
            "cpu_percent": str(psutil.cpu_percent(interval=1)),
            "ram_usage": str(psutil.virtual_memory().percent)
            }
        
        return result, 200

    return "ko", 500


if __name__ == "__main__":
    app.run(debug=True)
