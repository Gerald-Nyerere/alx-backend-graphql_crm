#!/bin/bash

LOG_FILE="/tmp/customer_cleanup_log.txt"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

cd "$(dirname "$0")/../.." || exit 1

DELETED_COUNT=$(python3 manage.py shell <<EOF
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

one_year_ago = timezone.now() - timedelta(days=365)
deleted, _ = Customer.objects.filter(order__date__lt=one_year_ago).distinct().delete()
print(deleted)
EOF
)


echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> "$LOG_FILE"
