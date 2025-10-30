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


def update_low_stock():
    """Executes UpdateLowStockProducts mutation and logs results."""
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql/",  # Adjust if running on another host or port
        verify=False,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)

    mutation = gql("""
        mutation {
            updateLowStockProducts {
                updatedProducts {
                    id
                    name
                    stock
                }
                message
            }
        }
    """)

    log_file = "/tmp/low_stock_updates_log.txt"
    try:
        response = client.execute(mutation)
        updated_products = response["updateLowStockProducts"]["updatedProducts"]
        message = response["updateLowStockProducts"]["message"]

        with open(log_file, "a") as f:
            f.write(f"\n[{datetime.datetime.now()}] {message}\n")
            for p in updated_products:
                f.write(f" - {p['name']}: new stock = {p['stock']}\n")

        print("✅ Low-stock products updated successfully.")
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"\n[{datetime.datetime.now()}] ❌ Error: {str(e)}\n")
        print("❌ Cron job failed:", str(e))