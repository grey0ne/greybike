from constants import JS_FILE, STYLES_FILE

with open(JS_FILE) as js_file:
    SCRIPT_CONTENT = js_file.read()


with open(STYLES_FILE) as styles_file:
    STYLES_CONTENT = styles_file.read()

HEAD_HTML = f"""
<head>
    <title>Greybike Telemetry</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=0" />
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-status-bar-style" content="black" />
    <meta name="apple-mobile-web-app-title" content="Telemetry" />
    <link rel="manifest" href="/manifest.json" />
    <style>
        {STYLES_CONTENT}
    </style>
    <script>
        {SCRIPT_CONTENT}
    </script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
"""

def render_page(body: str) -> str:
    return f"""
        <!DOCTYPE html>
        <html>
            {HEAD_HTML}
            <body>
                {body}
            </body>
        </html>
    """

