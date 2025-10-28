import streamlit as st
import random
import math
import numpy as np
import matplotlib.pyplot as plt
import colorsys
import pandas as pd
import os
import io

# ==========================================
# 1. CSV Palette File Management
# ==========================================

PALETTE_FILE = "palette.csv"

def initialize_palette_csv():
    """Create default palette file if missing."""
    if not os.path.exists(PALETTE_FILE):
        df = pd.DataFrame([
            {"name": "sky", "r": 0.4, "g": 0.7, "b": 1.0},
            {"name": "sun", "r": 1.0, "g": 0.8, "b": 0.2},
            {"name": "forest", "r": 0.2, "g": 0.6, "b": 0.3}
        ])
        df.to_csv(PALETTE_FILE, index=False)
        print("✅ Created default palette.csv")

def read_palette():
    if not os.path.exists(PALETTE_FILE):
        initialize_palette_csv()
    try:
        df = pd.read_csv(PALETTE_FILE)
        if not all(col in df.columns for col in ["name", "r", "g", "b"]):
            initialize_palette_csv()
            return pd.read_csv(PALETTE_FILE)
        return df
    except Exception:
        initialize_palette_csv()
        return pd.read_csv(PALETTE_FILE)

def save_palette(df):
    df.to_csv(PALETTE_FILE, index=False)

def load_csv_palette():
    df = read_palette()
    return [(float(r.r), float(r.g), float(r.b)) for r in df.itertuples()]

# ==========================================
# 2. Generative Poster Logic
# ==========================================

def blob(center=(0.5, 0.5), r=0.4, points=400, wobble=0.15):
    angles = np.linspace(0, 2 * math.pi, points)
    radii = r * (1 + wobble * (np.random.rand(points) - 0.5))
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return x, y

def make_palette(k=6, mode="pastel", base_h=0.6):
    if mode == "csv":
        return load_csv_palette()

    cols = []
    for _ in range(k):
        if mode == "pastel":
            h, s, v = random.random(), random.uniform(0.15, 0.35), random.uniform(0.9, 1.0)
        elif mode == "vivid":
            h, s, v = random.random(), random.uniform(0.8, 1.0), random.uniform(0.8, 1.0)
        elif mode == "mono":
            h = (base_h + random.uniform(-0.05, 0.05)) % 1.0
            s, v = random.uniform(0.2, 0.8), random.uniform(0.5, 1.0)
        else:
            h, s, v = random.random(), random.uniform(0.3, 1.0), random.uniform(0.5, 1.0)
        cols.append(colorsys.hsv_to_rgb(h, s, v))
    return cols

def draw_single_blob(ax, center, radius, color, alpha, wobble):
    x, y = blob(center=center, r=radius, wobble=wobble)
    ax.fill(x, y, color=color, alpha=alpha, edgecolor='none')

def redraw_poster(ax, n_layers, wobble_val, palette_mode, seed_val):
    random.seed(seed_val)
    np.random.seed(seed_val)
    ax.clear()
    ax.set_facecolor((0.97, 0.97, 0.97))
    ax.axis("off")

    palette = make_palette(6, mode=palette_mode)
    if not palette:
        palette = [(0.5, 0.5, 0.5)]

    for _ in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.1, 0.4)
        alpha = random.uniform(0.1, 0.5)
        color = random.choice(palette)
        draw_single_blob(ax, (cx, cy), rr, color, alpha, wobble_val)

    ax.text(0.05, 0.95, f"Poster • {palette_mode}", transform=ax.transAxes,
            fontsize=14, weight="bold", color="black")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

# ==========================================
# 3. Streamlit UI
# ==========================================

st.set_page_config(page_title="Interactive Generative Poster", layout="wide")
st.title("🎨 Streamlit Generative Poster (with CSV Palette)")

# Palette management
st.sidebar.header("🎨 Manage Palette (palette.csv)")
initialize_palette_csv()
palette_df = read_palette()

st.sidebar.write("Current Palette:")
st.sidebar.dataframe(palette_df, use_container_width=True)

# Add new color
with st.sidebar.expander("➕ Add New Color"):
    new_name = st.text_input("Color Name")
    new_r = st.slider("R (0.0–1.0)", 0.0, 1.0, 0.5)
    new_g = st.slider("G (0.0–1.0)", 0.0, 1.0, 0.5)
    new_b = st.slider("B (0.0–1.0)", 0.0, 1.0, 0.5)
    if st.button("Add Color"):
        if new_name:
            if new_name in palette_df["name"].values:
                st.warning("Color name already exists.")
            else:
                palette_df = pd.concat([
                    palette_df,
                    pd.DataFrame([{"name": new_name, "r": new_r, "g": new_g, "b": new_b}])
                ], ignore_index=True)
                save_palette(palette_df)
                st.success(f"Added color '{new_name}' ✅")
        else:
            st.error("Please provide a color name.")

# Delete color
with st.sidebar.expander("❌ Delete Color"):
    if not palette_df.empty:
        del_name = st.selectbox("Select color to delete", palette_df["name"].tolist())
        if st.button("Delete Selected Color"):
            palette_df = palette_df[palette_df["name"] != del_name]
            save_palette(palette_df)
            st.success(f"Deleted '{del_name}' ✅")
    else:
        st.info("No colors available to delete.")

# ==========================================
# Poster Controls
# ==========================================

st.sidebar.header("⚙️ Poster Settings")

palette_mode = st.sidebar.selectbox("Palette Mode", ["csv", "pastel", "vivid", "mono", "random"])
n_layers = st.sidebar.slider("Number of Layers", 3, 50, 8)
wobble_val = st.sidebar.slider("Wobble Intensity", 0.01, 0.5, 0.15)
seed_val = st.sidebar.number_input("Seed (for randomness)", 0, 9999, 0)

# ==========================================
# Generate Poster
# ==========================================

if st.button("🎨 Generate Poster"):
    fig, ax = plt.subplots(figsize=(7, 10))
    redraw_poster(ax, n_layers, wobble_val, palette_mode, seed_val)
    st.pyplot(fig)

    # Download button
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)
    st.download_button(
        "💾 Download Poster",
        data=buf,
        file_name=f"poster_{palette_mode}.png",
        mime="image/png"
    )

st.markdown("---")
st.caption("Built with Streamlit • Real-time editable palette (palette.csv) and generative art engine 🎨")
