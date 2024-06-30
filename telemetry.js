const MAX_POINTS = 60;
const GRAPH_FREQUENCY = 10;
const PARAM_DICT = {
    'amper_hours': {'name': 'Amper Hours', 'unit': 'Ah'},
    'human_torque': {'name': 'Human Torque', 'unit': 'Nm', 'treshold': 1},
    'human_watts': {'name': 'Human Power', 'unit': 'W'},
    'voltage': {'name': 'Voltage', 'unit': 'V'},
    'current': {'name': 'Current', 'unit': 'A'},
    'pedal_rpm': {'name': 'Pedaling RPM', 'unit': ''},
    'speed': {'name': 'Speed', 'unit': 'km/h'},
    'motor_temp': {'name': 'Motor Temp', 'unit': 'C'},
    'cpu_temperature': {'name': 'CPU Temp', 'unit': 'C'},
    'trip_distance': {'name': 'Distance', 'unit': 'km'},
    'mode': {'name': 'Mode', 'unit': ''},
    'is_brake_pressed': {'name': 'Brake Pressed', 'unit': ''},
}

function onMessage(event) {
    const data = JSON.parse(event.data);
    const chart = window.chart;
    window.counter++;

    const paramContainer = document.getElementById("telemetry-params")
    paramContainer.innerHTML = "";
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
        if (paramData) {
            const paramElem = document.createElement('div');
	    const treshold = paramData.treshold || 0;
	    let value = data[key] > treshold ? data[key] : 0;
            if (typeof value === 'number') {
	        value = value.toFixed(2);
	    }
            paramElem.innerHTML = `
                <div>
                    <div><span id="${key}">${value}</span> ${paramData.unit}</div>
                    <div>${paramData.name}</div>
                </div>
            `
            paramContainer.appendChild(paramElem);
        }
    }
    document.getElementById('log_duration').innerText = data['log_duration'];
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
            {
                label: 'voltage',
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
window.onload = () => {
    initializeConnection();
    document.getElementById('resetForm').addEventListener("submit", resetFormSubmit);
    const ctx = document.getElementById('myChart');
    window.counter = 0;
    window.chart = new Chart(ctx, BASE_CHART_DATA);
};
