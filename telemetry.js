const MAX_POINTS = 60;
const GRAPH_FREQUENCY = 10;
const SPEED_MODE = 'speed';
const POWER_MODE = 'power';
const TEMPERATURE_MODE = 'temperature';
const ASSIST_MODE = 'assist';
const DASH_MODES = [SPEED_MODE, POWER_MODE, TEMPERATURE_MODE, ASSIST_MODE];

const PARAM_DICT = {
    'amper_hours': {'name': 'Amper Hours', 'unit': 'Ah', 'modes': [POWER_MODE]},
    'human_torque': {'name': 'Human Torque', 'unit': 'Nm', 'treshold': 1, 'modes': [POWER_MODE]},
    'human_watts': {'name': 'Human Power', 'unit': 'W', 'modes': [POWER_MODE]},
    'voltage': {'name': 'Voltage', 'unit': 'V', 'modes': [POWER_MODE]},
    'current': {'name': 'Current', 'unit': 'A', 'modes': [POWER_MODE]},
    'pedal_rpm': {'name': 'Pedaling RPM', 'unit': '', 'modes': [ASSIST_MODE]},
    'speed': {'name': 'Speed', 'unit': 'km/h', 'modes': [SPEED_MODE]},
    'motor_temp': {'name': 'Motor Temp', 'unit': 'C', 'modes': [TEMPERATURE_MODE]},
    'cpu_temperature': {'name': 'CPU Temp', 'unit': 'C', 'modes': [TEMPERATURE_MODE]},
    'trip_distance': {'name': 'Distance', 'unit': 'km', 'modes': [SPEED_MODE]},
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
        paramElem.innerHTML = `
            <div>
                <div><span id="${param}"></span> ${paramData.unit}</div>
                <div>${paramData.name}</div>
            </div>
        `
        paramContainer.appendChild(paramElem);
    }
}
function onMessage(event) {
    const data = JSON.parse(event.data);
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
                label: 'speed',
                data: [],
                borderWidth: 1
            },
            {
                label: 'current',
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
    const url = document.getElementById('resetForm').getAttribute('action');
    fetch(url, { method: 'POST'});
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
        document.getElementById('resetForm').addEventListener("submit", resetFormSubmit);
        document.getElementById('next-mode-button').addEventListener("click", changeMode);
        const ctx = document.getElementById('myChart');
        window.counter = 0;
        window.chart = new Chart(ctx, BASE_CHART_DATA);
    }
};
