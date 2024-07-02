from pages import render_page


LOGS_ELEM_TEMPLATE = '''
    <div class="log-elem">
        {log_name}
    </div>
'''

def render_logs_page(logs: list[str]) -> str:
    log_elems = ''.join(LOGS_ELEM_TEMPLATE.format(log_name=log_name) for log_name in logs)
    return render_page(log_elems)