const MAX_POINTS = 60;
const GRAPH_FREQUENCY = 10;
const SPEED_MODE = 'speed_mode';
const POWER_MODE = 'power_mode';
const TEMPERATURE_MODE = 'temperature_mode';
const ASSIST_MODE = 'assist_mode';
const ODO_MODE = 'odo_mode';
const DASH_MODES = [ASSIST_MODE, POWER_MODE, ODO_MODE];

const PARAM_DICT = {
    'amper_hours': {'name': 'Amper Hours', 'unit': 'Ah', 'modes': [ODO_MODE]},
    'human_torque': {'name': 'Human Torque', 'unit': 'Nm', 'treshold': 1, 'modes': []},
    'human_watts': {'name': 'Human Power', 'unit': 'W', 'modes': [ASSIST_MODE]},
    'voltage': {'name': 'Voltage', 'unit': 'V', 'modes': [POWER_MODE]},
    'current': {'name': 'Current', 'unit': 'A', 'modes': [POWER_MODE]},
    'motor_power': {'name': 'Motor Power', 'unit': 'W', 'modes': [ASSIST_MODE]},
    'pedal_rpm': {'name': 'Pedaling RPM', 'unit': '', 'modes': [ASSIST_MODE, SPEED_MODE]},
    'speed': {'name': 'Speed', 'unit': 'km/h', 'modes': [SPEED_MODE, ASSIST_MODE]},
    'motor_temp': {'name': 'Motor Temp', 'unit': 'C', 'modes': [TEMPERATURE_MODE, POWER_MODE]},
    'cpu_temperature': {'name': 'CPU Temp', 'unit': 'C', 'modes': [TEMPERATURE_MODE, POWER_MODE]},
    'trip_distance': {'name': 'Distance', 'unit': 'km', 'modes': [ODO_MODE]},
    'mode': {'name': 'Mode', 'unit': '', 'modes': []},
    'is_brake_pressed': {'name': 'Brake Pressed', 'unit': '', 'modes': []},
}

function initParamContainers() {
    const paramContainer = document.getElementById("telemetry-params")
    paramContainer.innerHTML = "";
    for (param in PARAM_DICT) {
        const paramData = PARAM_DICT[param];
        if (!paramData.modes.includes(DASH_MODES[window.currentDashMode])) {
            continue
        }
        const paramElem = document.createElement('div');
        paramElem.className = 'param-container';
        paramElem.innerHTML = `
            <div><span id="${param}"></span> ${paramData.unit}</div>
            <div>${paramData.name}</div>
        `
        paramContainer.appendChild(paramElem);
    }
}
function onMessage(event) {
    const data = JSON.parse(event.data);
    data['motor_power'] = data['voltage'] * data['current'];
    const chart = window.chart;
    window.counter++;

    const paramContainer = document.getElementById("telemetry-params")
    for (const key in data) {
        if (window.counter % GRAPH_FREQUENCY === 0) {
            for (const ds of chart.data.datasets) {
                if (ds.label === key) {
                    if (ds.data.length > MAX_POINTS) {
                        ds.data.shift();
                    }
                    ds.data.push(data[key]);
                }
            }
        }
        const paramData = PARAM_DICT[key];
        const valueElem = document.getElementById(key);
        if (paramData && valueElem) {
	        const treshold = paramData.treshold || 0;
	        let value = data[key] > treshold ? data[key] : 0;
            if (typeof value === 'number') {
	            value = value.toFixed(2);
	        }
            valueElem.innerText = value;
        }
    }
    document.getElementById('log_duration').innerText = data['log_duration'].toFixed(1);
    document.getElementById('log_file').innerText = data['log_file'];
    if (window.counter % GRAPH_FREQUENCY === 0) {
        if (chart.data.labels.length > MAX_POINTS) {
            chart.data.labels.shift();
        }
        chart.data.labels.push(window.counter / 10);
        chart.update();
    }
}

function initializeConnection() {
    const socket = new WebSocket(`ws://${window.location.host}/ws`);
    socket.onmessage = onMessage
}

const BASE_CHART_DATA = {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                label: 'human_watts',
                data: [],
                borderWidth: 1
            },
            {
                label: 'motor_power',
                data: [],
                borderWidth: 1
            },
        ]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
}

resetFormSubmit = (event) => {
    event.preventDefault();
    fetch('/reset_log', { method: 'POST'});
}

changeMode = (event) => {
    event.preventDefault();
    window.currentDashMode += 1;
    if (window.currentDashMode >= DASH_MODES.length) {
        window.currentDashMode = 0;
    }
    initParamContainers();
}
window.onload = () => {
    const paramContainer = document.getElementById("telemetry-params");
    window.currentDashMode = 0;
    if (paramContainer) {
        initializeConnection();
        initParamContainers();
        document.getElementById('reset-log-button').addEventListener("click", resetFormSubmit);
        document.getElementById('next-mode-button').addEventListener("click", changeMode);
        const ctx = document.getElementById('myChart');
        window.counter = 0;
        window.chart = new Chart(ctx, BASE_CHART_DATA);
    }
};
