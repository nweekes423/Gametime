#!/bin/bash

# Check if necessary tools are installed
command -v bandit >/dev/null 2>&1 || { echo >&2 "Bandit is not installed. Install it with 'pip install bandit'"; exit 1; }
command -v safety >/dev/null 2>&1 || { echo >&2 "Safety is not installed. Install it with 'pip install safety'"; exit 1; }

# 1. Run Django's built-in security checks
echo "Running Django's built-in security checks..."
python manage.py check --deploy

# 2. Run Bandit to find security issues in the code
echo "Running Bandit security linter..."
bandit -r .

# 3. Run Safety to check for vulnerabilities in dependencies
echo "Checking dependencies with Safety..."
safety check

# 4. OWASP ZAP Scan (optional, requires OWASP ZAP installed and configured)
# echo "Running OWASP ZAP scan..."
# zap-baseline.py -t http://localhost:8000 -r zap_report.html

echo "Security checks completed."

