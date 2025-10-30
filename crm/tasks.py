import datetime
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

@shared_task
def generate_crm_report():
    """Fetch CRM data from GraphQL and log summary."""
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql/",
        verify=False,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
        query {
            allCustomers {
                totalCount
            }
            allOrders {
                totalCount
                edges {
                    node {
                        totalAmount
                    }
                }
            }
        }
    """)

    log_path = "/tmp/crm_report_log.txt"

    try:
        response = client.execute(query)
        total_customers = response['allCustomers']['totalCount']
        total_orders = response['allOrders']['totalCount']
        total_revenue = sum(
            float(edge['node']['totalAmount'])
            for edge in response['allOrders']['edges']
        )

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_line = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n"

        with open(log_path, "a") as f:
            f.write(report_line)

        print("CRM report generated successfully.")
    except Exception as e:
        with open(log_path, "a") as f:
            f.write(f"{datetime.datetime.now()} - Error: {str(e)}\n")
        print("Failed to generate CRM report:", str(e))
