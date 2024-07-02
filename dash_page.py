from pages import render_page

DASH_PAGE_HTML = render_page(
"""
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
"""
)
