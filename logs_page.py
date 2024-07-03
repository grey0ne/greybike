from pages import render_page


LOGS_ELEM_TEMPLATE = '''
    <div class="log-elem">
        {log_name}
    </div>
'''

LOGS_PAGE_TEMPLATE = '''
    <div id="logs-page">
        <div>
            <a href="/">Back</a>
        </div>
        <div>
            {log_elems}
        </div>
    </div>

'''

def render_logs_page(logs: list[str]) -> str:
    log_elems = ''.join(LOGS_ELEM_TEMPLATE.format(log_name=log_name) for log_name in logs)
    return render_page(LOGS_PAGE_TEMPLATE.format(log_elems=log_elems))