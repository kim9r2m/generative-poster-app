import streamlit as st
import random
import math
import numpy as np
import matplotlib.pyplot as plt
import colorsys
import io

# --------------------------------------------------------------------------
# 1. Palette Functions
# --------------------------------------------------------------------------

def _random_palette_pastel(k=5):
    """Low saturation, high brightness colors."""
    return [colorsys.hsv_to_rgb(random.random(), random.uniform(0.25, 0.45), random.uniform(0.85, 1.0)) for _ in range(k)]

def _random_palette_vivid(k=5):
    """High saturation and brightness."""
    return [colorsys.hsv_to_rgb(random.random(), random.uniform(0.8, 1.0), random.uniform(0.9, 1.0)) for _ in range(k)]

def _random_palette_muted(k=5):
    """Low saturation, mid brightness."""
    return [colorsys.hsv_to_rgb(random.random(), random.uniform(0.1, 0.3), random.uniform(0.5, 0.7)) for _ in range(k)]

def _random_palette_full_random(k=5):
    """Completely random colors."""
    return [(random.random(), random.random(), random.random()) for _ in range(k)]

# --------------------------------------------------------------------------
# 2. Blob Shape Function
# --------------------------------------------------------------------------

def blob(center=(0.5, 0.5), r=0.3, points=200, wobble=0.15):
    """Generate a wobbly closed shape."""
    angles = np.linspace(0, 2 * math.pi, points)
    radii = r * (1 + wobble * (np.random.rand(points) - 0.5))
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return x, y

# --------------------------------------------------------------------------
# 3. Poster Generation
# --------------------------------------------------------------------------

def generate_poster(style="Pastel", seed=None):
    """Generate a poster in the given style and return the matplotlib figure."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    # Define styles
    if style == "Pastel":
        palette_func = _random_palette_pastel
        n_layers = random.randint(8, 12)
        wobble_range = (0.05, 0.25)
        background_color = (0.98, 0.98, 0.97)
        text_color = "black"
    elif style == "Minimal":
        palette_func = _random_palette_muted
        n_layers = random.randint(3, 5)
        wobble_range = (0.01, 0.05)
        background_color = (0.95, 0.95, 0.95)
        text_color = "#333333"
    elif style == "Vivid":
        palette_func = _random_palette_vivid
        n_layers = random.randint(15, 25)
        wobble_range = (0.1, 0.3)
        background_color = (0.1, 0.1, 0.1)
        text_color = "white"
    elif style == "NoiseTouch":
        palette_func = _random_palette_full_random
        n_layers = random.randint(10, 20)
        wobble_range = (0.3, 0.6)
        background_color = (0.9, 0.9, 0.9)
        text_color = "black"
    else:
        raise ValueError("Unknown style.")

    # Create figure
    fig, ax = plt.subplots(figsize=(7, 10))
    ax.axis("off")
    ax.set_facecolor(background_color)

    # Generate palette
    palette = palette_func(random.randint(5, 7))

    # Draw blobs
    for _ in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.15, 0.45)
        current_wobble = random.uniform(wobble_range[0], wobble_range[1])
        x, y = blob(center=(cx, cy), r=rr, wobble=current_wobble)
        color = random.choice(palette)
        alpha = random.uniform(0.25, 0.7)
        ax.fill(x, y, color=color, alpha=alpha, edgecolor=(0, 0, 0, 0))

    # Text labels
    ax.text(0.05, 0.95, "Generative Poster", fontsize=18, weight="bold",
            transform=ax.transAxes, color=text_color)
    ax.text(0.05, 0.91, "Week 3 • Arts & Advanced Big Data", fontsize=11,
            transform=ax.transAxes, color=text_color)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    return fig

# --------------------------------------------------------------------------
# 4. Streamlit UI
# --------------------------------------------------------------------------

st.set_page_config(page_title="🎨 Generative Poster", layout="wide")

st.title("🎨 Generative Poster Generator")
st.write("Create generative art posters with unique visual styles and download them as PNG.")

# Sidebar Controls
st.sidebar.header("🧩 Controls")
style = st.sidebar.selectbox("Select Poster Style", ["Pastel", "Minimal", "Vivid", "NoiseTouch"])
seed = st.sidebar.number_input("Random Seed (optional)", min_value=0, max_value=9999, value=0)
generate = st.sidebar.button("🎨 Generate Poster")

# Generate poster on button click
if generate:
    with st.spinner(f"Generating '{style}' style poster..."):
        fig = generate_poster(style, seed if seed != 0 else None)
        st.pyplot(fig)

        # Convert plot to PNG for download
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        buf.seek(0)

        st.download_button(
            label="💾 Download Poster as PNG",
            data=buf,
            file_name=f"GenerativePoster_{style}.png",
            mime="image/png"
        )
else:
    st.info("👈 Choose a style and click **Generate Poster** to create your artwork!")

st.markdown("---")
st.caption("Developed with ❤️ using Streamlit and Matplotlib")
