from constants import SCRIPT_CONTENT, STYLES_CONTENT



PAGE_TEMPLATE = f"""
<!DOCTYPE html>
<html>
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
    <body>
        <div id="telemetry-params">
        </div>
        <div>
            Log file:&nbsp;
            <span id="log_file">
            </span>
        </div>
        <div>
            Duration:&nbsp;
            <span id="log_duration">
            </span>
            &nbsp;Seconds
            <form action="/reset_log" id="resetForm">
                <input name="submit" type="submit" value="Reset log file">
            </form>
        </div>

        <div style="width: 100%; height: 400px;">
            <canvas id="myChart"></canvas>
        </div>
    </body>
</html>
"""
