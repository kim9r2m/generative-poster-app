import streamlit as st
import random
import math
import numpy as np
import matplotlib.pyplot as plt

# ------------------------
# Helper functions
# ------------------------
def random_palette(k=5):
    """Return k random pastel-like colors"""
    return [(random.random(), random.random(), random.random()) for _ in range(k)]

def blob(center=(0.5, 0.5), r=0.3, points=200, wobble=0.15):
    """Generate a wobbly closed shape"""
    angles = np.linspace(0, 2*math.pi, points)
    radii = r * (1 + wobble*(np.random.rand(points)-0.5))
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return x, y

# ------------------------
# Streamlit App
# ------------------------
st.set_page_config(page_title="Generative Poster", layout="wide")

st.title("🎨 Generative Poster Art")
st.write("This app generates a unique generative poster each time you click **Generate**.")

# Sidebar controls
st.sidebar.header("🛠️ Controls")
n_layers = st.sidebar.slider("Number of Layers", 3, 15, 8)
num_colors = st.sidebar.slider("Number of Colors in Palette", 3, 10, 6)
min_radius = st.sidebar.slider("Minimum Radius", 0.1, 0.4, 0.15)
max_radius = st.sidebar.slider("Maximum Radius", 0.2, 0.6, 0.45)
min_wobble = st.sidebar.slider("Min Wobble", 0.01, 0.3, 0.05)
max_wobble = st.sidebar.slider("Max Wobble", 0.05, 0.4, 0.25)
button = st.sidebar.button("🎨 Generate Poster")

# Generate on button click
if button:
    random.seed()  # Different art each run
    plt.figure(figsize=(7, 10))
    plt.axis('off')
    plt.gca().set_facecolor((0.98, 0.98, 0.97))

    palette = random_palette(num_colors)

    for i in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(min_radius, max_radius)
        x, y = blob(center=(cx, cy), r=rr, wobble=random.uniform(min_wobble, max_wobble))
        color = random.choice(palette)
        alpha = random.uniform(0.25, 0.6)
        plt.fill(x, y, color=color, alpha=alpha, edgecolor=(0,0,0,0))

    # Labels
    plt.text(0.05, 0.95, "Generative Poster", fontsize=18, weight='bold', transform=plt.gca().transAxes)
    plt.text(0.05, 0.91, "Week 2 • Arts & Advanced Big Data", fontsize=11, transform=plt.gca().transAxes)

    plt.xlim(0, 1)
    plt.ylim(0, 1)

    st.pyplot(plt)
else:
    st.info("👈 Adjust parameters and click **Generate Poster** to see your art!")

