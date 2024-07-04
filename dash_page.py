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

    <div class="row" style="justify-content:space-around">
        <div>
            <span id="log_file">
            </span>
        </div>
        <div>
            <span id="log_duration">
            </span>
            &nbsp;Seconds
        </div>
    </div>
    <div class="row">
        <button id="reset-log-button" class="default-button row-elem">Reset log file</button>
    </div>
    <div class="row">
        <a href="/logs" class="default-button row-elem">All Logs</a>
    </div>
"""
)
