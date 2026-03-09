// app.js

// Define your API base URL
const API_BASE = "http://127.0.0.1:5000";

// Functions to interact with your API for insights, recipes, and clusters
async function getInsights() {
    console.log("Running getInsights");

    // Call the backend API to generate charts
    const res = await fetch(`${API_BASE}/api/insights`);
    const data = await res.json();  // You can log the data if you want

    console.log("Insights data:", data);  // Optional: log the insights

    // Only set the images after the charts have been generated
    document.getElementById("barChart").src = `${API_BASE}/backend/storage/charts/bar.png`;
    document.getElementById("scatterPlot").src = `${API_BASE}/backend/storage/charts/bar.png`;
    document.getElementById("heatmap").src = `${API_BASE}/backend/storage/charts/bar.png`;
    // document.getElementById("pieChart").src = `${API_BASE}/charts/pie.png`;
}

async function getRecipes() {
    const res = await fetch(`${API_BASE}/api/recipes`);
    const data = await res.json();
    console.log("Recipes:", data);
    alert("Check console for recipes data");
}

async function getClusters() {
    const res = await fetch(`${API_BASE}/api/clusters`);
    const data = await res.json();
    console.log("Clusters:", data);
    alert("Check console for clusters data");
}

// Setup event listeners for the buttons
document.getElementById("insightsBtn").addEventListener("click", getInsights);
document.getElementById("recipesBtn").addEventListener("click", getRecipes);
document.getElementById("clustersBtn").addEventListener("click", getClusters);