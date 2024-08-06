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
    <link rel="icon" type="image/png" href="/favicon-16.png" sizes="16x16">
    <link rel="icon" type="image/png" href="/favicon-32.png" sizes="32x32">
    <link rel="icon" type="image/png" href="/favicon-96.png" sizes="96x96">
    <link rel="apple-touch-icon" sizes="76x76" href="/touch-icon-76.png">
    <style>
        {STYLES_CONTENT}
    </style>
    <script>
        {SCRIPT_CONTENT}
    </script>
    <script src="/chart.js"></script>
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

