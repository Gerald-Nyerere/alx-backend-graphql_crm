from datetime import datetime
import requests

def log_crm_heartbeat():
    """Logs a heartbeat message and optionally checks GraphQL hello endpoint."""
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive\n"
    log_file = "/tmp/crm_heartbeat_log.txt"

 
    with open(log_file, "a") as f:
        f.write(log_message)

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.status_code == 200:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL hello response: {response.json()}\n")
        else:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL hello check failed (status {response.status_code})\n")
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} GraphQL hello check error: {e}\n")
