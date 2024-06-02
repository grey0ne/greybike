const socket = new WebSocket(`ws://${window.location.host}/ws`);
socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const chart = window.chart;
    window.counter++;
    for (const key in data) {
        if (window.counter % 10 === 0) {
            for (const ds of chart.data.datasets) {
                if (ds.label === key) {
                    ds.data.push(data[key]);
                }
            }
        }
        const elem = document.getElementById(key)
        if (elem) {
            elem.innerHTML = data[key];
        }
    }
    if (window.counter % 10 === 0) {
        chart.data.labels.push(window.counter);
        chart.update();
    }
} 

window.onload = () => {
    const ctx = document.getElementById('myChart');
    window.counter = 0;
    window.chart = new Chart(ctx, {
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
    });
};