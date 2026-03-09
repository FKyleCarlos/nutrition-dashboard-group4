# =====================
# Standard library
# =====================
import io
import os
import json

# =====================
# Third-party packages
# =====================
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, jsonify, send_file
from azure.storage.blob import BlobServiceClient

# =====================
# Flask app
# =====================
app = Flask(__name__)

# =====================
# Azure Blob Config
# =====================
CONNECT_STR = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/"
    "K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)
CONTAINER_NAME = "datasets"
BLOB_NAME = "All_Diets.csv"

blob_service_client = BlobServiceClient.from_connection_string(CONNECT_STR)
blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)

# =====================
# Helper function to load dataset
# =====================
def load_dataset():
    csv_bytes = blob_client.download_blob().readall()
    df = pd.read_csv(io.BytesIO(csv_bytes))

    # Fill missing numeric columns
    numeric_cols = ['Protein(g)', 'Carbs(g)', 'Fat(g)']
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

    # Add ratio metrics
    df['Protein_to_Carbs_ratio'] = df['Protein(g)'] / df['Carbs(g)']
    df['Carbs_to_Fat_ratio'] = df['Carbs(g)'] / df['Fat(g)']

    return df

# =====================
# API Endpoints
# =====================

@app.route("/api/insights")
def insights():
    df = load_dataset()
    numeric_cols = ['Protein(g)', 'Carbs(g)', 'Fat(g)']
    avg_macros = df.groupby('Diet_type')[numeric_cols].mean().reset_index()
    return jsonify(avg_macros.to_dict(orient="records"))


@app.route("/api/recipes")
def recipes():
    df = load_dataset()
    top_protein = df.sort_values('Protein(g)', ascending=False).groupby('Diet_type').head(5)
    return jsonify(top_protein[['Diet_type', 'Recipe_name', 'Protein(g)']].to_dict(orient="records"))


@app.route("/api/clusters")
def clusters():
    df = load_dataset()
    # Example: most common cuisine per diet
    common_cuisine = (
        df.groupby('Diet_type')['Cuisine_type']
        .agg(lambda x: x.value_counts().idxmax())
        .reset_index()
        .rename(columns={'Cuisine_type': 'Most_Common_Cuisine'})
    )
    return jsonify(common_cuisine.to_dict(orient="records"))


@app.route("/api/plot/<string:plot_type>")
def plot(plot_type):
    df = load_dataset()
    numeric_cols = ['Protein(g)', 'Carbs(g)', 'Fat(g)']
    avg_macros = df.groupby('Diet_type')[numeric_cols].mean().reset_index()

    img = io.BytesIO()
    plt.figure(figsize=(8, 6))

    if plot_type == "bar":
        sns.barplot(x="Diet_type", y="Protein(g)", data=avg_macros)
        plt.title("Average Protein by Diet Type")
    elif plot_type == "heatmap":
        sns.heatmap(avg_macros.set_index('Diet_type')[numeric_cols], annot=True, fmt=".0f", cmap="coolwarm")
        plt.title("Macronutrient Heatmap by Diet Type")
    elif plot_type == "scatter":
        top_protein = df.sort_values('Protein(g)', ascending=False).groupby('Diet_type').head(5)
        sns.scatterplot(data=top_protein, x='Protein(g)', y='Carbs(g)', hue='Cuisine_type')
        plt.title("Top 5 Protein-Rich Recipes by Cuisine")
    else:
        return jsonify({"error": "Unknown plot type"}), 400

    plt.tight_layout()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    return send_file(img, mimetype='image/png')


# =====================
# Run Flask
# =====================
if __name__ == "__main__":
    app.run(debug=True)
