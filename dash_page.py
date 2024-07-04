from pages import render_page

DASH_PAGE_HTML = render_page(
"""
    <div id="telemetry-params">
    </div>
    <div class="row">
        <button id="next-mode-button" class="default-button row-elem">Next Mode</button>
    </div>

    <div style="width: 100%;">
        <canvas id="myChart"></canvas>
    </div>

    <div class="row">
            Log file:&nbsp;
            <span id="log_file">
            </span>
    </div>
    <div class="row">
        Duration:&nbsp;
        <span id="log_duration">
        </span>
        &nbsp;Seconds
    </div>
    <div class="row">
        <form action="/reset_log" id="resetForm" class="row-elem" >
            <input name="submit" type="submit" value="Reset log file" class="default-button">
        </form>
    </div>
    <div class="row">
        <a href="/logs" class="default-button row-elem">All Logs</a>
    </div>
"""
)
