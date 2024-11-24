document.getElementById("input-form").addEventListener("submit", async function (event) {
  event.preventDefault();

  const latitude = document.getElementById("latitude").value;
  const longitude = document.getElementById("longitude").value;
  const apiKey = "0WZOCxfi4Tbx3";

  await fetchPowerBreakdown(latitude, longitude, apiKey);
});

async function fetchPowerBreakdown(latitude, longitude, apiKey) {
  try {
    const response = await fetch("http://127.0.0.1:5000/fetch_power", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ latitude, longitude, api_key: apiKey }),
    });

    if (!response.ok) throw new Error("Failed to fetch data");

    const data = await response.json();

    if (data.error) {
      alert(data.error);
      return;
    }

    const historicalData = data.history;

    if (!historicalData || historicalData.length === 0) {
      alert("No historical data available.");
      return;
    }

    // Prepare data for the line chart
    const labels = historicalData.map((entry) => new Date(entry.datetime).toLocaleString());
    const sources = {};

    // Collect production values for each source
    historicalData.forEach((entry) => {
      const production = entry.powerProductionBreakdown;

      if (production) {
        Object.entries(production).forEach(([source, value]) => {
          if (!sources[source]) {
            sources[source] = Array(historicalData.length).fill(null);
          }
          sources[source][historicalData.indexOf(entry)] = value ?? 0;
        });
      }
    });

    renderLineChart(labels, sources);

  } catch (error) {
    alert("Error: " + error.message);
  }
}

function renderLineChart(labels, sources) {
  const ctx = document.getElementById("renewableChart").getContext("2d");

  const datasets = Object.entries(sources).map(([source, data]) => ({
    label: source,
    data,
    borderColor: `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 1)`,
    fill: false,
    tension: 0.1,
  }));

  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets,
    },
    options: {
      responsive: true,
      scales: {
        x: {
          title: {
            display: true,
            text: "Time",
          },
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Energy Production (MW)",
          },
        },
      },
    },
  });
}
