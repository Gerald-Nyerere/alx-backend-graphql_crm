from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """Logs a heartbeat message and optionally checks GraphQL hello endpoint."""
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_file = "/tmp/crm_heartbeat_log.txt"

    with open(log_file, "a") as f:
        f.write(f"{timestamp} CRM is alive\n")

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql("{ hello }")
        result = client.execute(query)
        hello_response = result.get("hello", "No response")

        with open(log_file, "a") as f:
            f.write(f"{timestamp} GraphQL hello response: {hello_response}\n")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} GraphQL hello check error: {e}\n")
