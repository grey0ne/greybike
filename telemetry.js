const MAX_POINTS = 60;
const GRAPH_FREQUENCY = 10;

const socket = new WebSocket(`ws://${window.location.host}/ws`);

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const chart = window.chart;
    window.counter++;
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
        const elem = document.getElementById(key)
        if (elem) {
            elem.innerHTML = data[key];
        }
    }
    if (window.counter % GRAPH_FREQUENCY === 0) {
        if (chart.data.labels.length > MAX_POINTS) {
            chart.data.labels.shift();
        }
        chart.data.labels.push(window.counter / 10);
        chart.update();
    }
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

window.onload = () => {
    const ctx = document.getElementById('myChart');
    window.counter = 0;
    window.chart = new Chart(ctx, BASE_CHART_DATA);
};