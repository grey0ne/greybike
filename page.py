PARAM_DICT = {
    'amper_hours': {'name': 'Amper Hours', 'unit': 'Ah'},
    'human_torque': {'name': 'Human Torque', 'unit': 'Nm'},
    'human_watts': {'name': 'Human Power', 'unit': 'W'},
    'voltage': {'name': 'Voltage', 'unit': 'V'},
    'current': {'name': 'Current', 'unit': 'A'},
    'rpm': {'name': 'Pedaling RPM', 'unit': ''},
    'speed': {'name': 'Speed', 'unit': 'km/h'},
    'motor_temp': {'name': 'Motor Temp', 'unit': '°C'},
    'distance': {'name': 'Distance', 'unit': 'km'},
    'mode': {'name': 'Mode', 'unit': ''},
    'is_brake_pressed': {'name': 'Brake Pressed', 'unit': ''},
}
PARAM_ELEMS = '\n'.join([f'<div><div><span id="{key}"></span> {param["unit"]}</div><div>{param["name"]}</div></div>' for key, param in PARAM_DICT.items()])

with open('telemetry.js') as js_file:
    SCRIPT = js_file.read()

""

STYLES = """
    .telemetry-params {
        display: flex;
        flex-wrap: wrap;
    }
    .telemetry-params > div {
        width: 30%;
        font-size: 32px;
        text-align: center;
        margin: 10px;
    }
    .telemetry-params span {
        font-size: 48px;
    }
"""

PAGE_TEMPLATE = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>Greybike Telemetry</title>
        <style>
            {STYLES}
        </style>
        <script>
            {SCRIPT}
        </script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="telemetry-params">
            {PARAM_ELEMS}
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

        <div style="width: 800px; height: 400px;">
            <canvas id="myChart"></canvas>
        </div>
    </body>
</html>
"""
