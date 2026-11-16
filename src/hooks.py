# Copyright (c) 2026, Shyamkumar Pandey and contributors
# For license information, please see license.txt

app_name = "src"
app_title = "Frappe Python Sdk"
app_publisher = "Shyamkumar Pandey"
app_description = "Frappe Python Sdk for Frappe and ERPNext"
app_email = "shyampandey1104@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------
app_include_css = "/assets/src/css/src.bundle.css"
app_include_js = "/assets/src/js/src.bundle.js"

# Document Events
# ---------------
doc_events = {
    "DocType Event": {
        "on_submit": "src.engine.on_document_submit",
        "on_cancel": "src.engine.on_document_cancel"
    }
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "src.engine.daily_scheduled_sync"
    ]
}
