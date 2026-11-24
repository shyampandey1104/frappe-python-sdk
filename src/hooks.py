# Copyright (c) 2026, Shyamkumar Pandey and contributors
# For license information, please see license.txt

app_name = "src"
app_title = "Frappe Python Sdk"
app_publisher = "Shyamkumar Pandey"
app_description = "Frappe Python Sdk - Enterprise Multi-DocType Solution for Frappe & ERPNext"
app_email = "shyampandey1104@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------
app_include_css = "/assets/src/css/src.bundle.css"
app_include_js = "/assets/src/js/src.bundle.js"

# Document Events
# ---------------
doc_events = {
    "Frappe Python Sdk Entry": {
        "validate": "src.services.validator.EnterpriseValidationEngine.validate_compliance_rules",
        "on_submit": "src.services.integration_service.EnterpriseIntegrationService.verify_remote_status"
    }
}

# Scheduled Background Tasks
# --------------------------
scheduler_events = {
    "hourly": [
        "src.tasks.hourly_sync"
    ],
    "daily": [
        "src.tasks.daily_reconciliation"
    ],
    "weekly": [
        "src.tasks.weekly_digest"
    ]
}
