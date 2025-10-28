import streamlit as st
import random
import math
import numpy as np
import matplotlib.pyplot as plt
import colorsys
from matplotlib.patches import Polygon
import io

# ------------------------------------------
# 1. Palette Functions (Now More Distinct)
# ------------------------------------------

def random_palette_pastel(k=5):
    """Soft pastel tones: low saturation, high brightness."""
    return [colorsys.hsv_to_rgb(random.random(), random.uniform(0.2, 0.4), random.uniform(0.9, 1.0)) for _ in range(k)]

def random_palette_vivid(k=5):
    """Strong vivid tones: high saturation, full brightness."""
    return [colorsys.hsv_to_rgb(random.random(), random.uniform(0.8, 1.0), random.uniform(0.9, 1.0)) for _ in range(k)]

def random_palette_mono(k=5):
    """Single hue, multiple brightness levels."""
    base_hue = random.random()
    return [colorsys.hsv_to_rgb(base_hue, random.uniform(0.3, 0.6), 0.3 + i / k * 0.7) for i in range(k)]

def random_palette_noisetouch(k=5):
    """Unpredictable color mixing with random noise."""
    return [(abs(random.gauss(0.5, 0.3)), abs(random.gauss(0.5, 0.3)), abs(random.gauss(0.5, 0.3))) for _ in range(k)]

def get_palette(style, k=5):
    """Return color palette by style."""
    if style == "Pastel":
        return random_palette_pastel(k)
    elif style == "Vivid":
        return random_palette_vivid(k)
    elif style == "Mono":
        return random_palette_mono(k)
    elif style == "NoiseTouch":
        return random_palette_noisetouch(k)
    else:
        return random_palette_vivid(k)

# ------------------------------------------
# 2. Blob & Lighting Functions
# ------------------------------------------

def blob(center=(0.5, 0.5), r=0.3, points=500, wobble=0.15):
    """Generate coordinates for a wobbly closed blob."""
    angles = np.linspace(0, 2 * math.pi, points)
    radii = r * (1 + wobble * (np.random.rand(points) - 0.5))
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return x, y

def get_lighting_effect_color(color_rgb, blob_center, light_source):
    """Add subtle lighting effect based on distance from the light source."""
    dist = math.sqrt((light_source[0] - blob_center[0]) ** 2 + (light_source[1] - blob_center[1]) ** 2)
    brightness_factor = 1.0 - (dist * 0.05)
    h, s, v = colorsys.rgb_to_hsv(*color_rgb)
    v = max(0, min(1, v * brightness_factor))
    return colorsys.hsv_to_rgb(h, s, v)

def draw_gradient_blob(ax, x, y, base_color, alpha, edge_color):
    """Draw a soft gradient blob."""
    patch = Polygon(np.column_stack([x, y]), facecolor='none', edgecolor='none')
    ax.add_patch(patch)
    h, s, v = colorsys.rgb_to_hsv(*base_color)
    lighter = colorsys.hsv_to_rgb(h, s * 0.3, min(1.0, v * 1.25))

    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))
    extent = [x.min(), x.max(), y.min(), y.max()]

    cmap = plt.cm.colors.LinearSegmentedColormap.from_list("grad", [base_color, lighter])
    im = ax.imshow(gradient, aspect='auto', extent=extent, origin='lower', cmap=cmap, alpha=alpha)
    im.set_clip_path(patch)

    # Draw edge if selected
    if edge_color is not None:
        ax.plot(x, y, color=edge_color, linewidth=1.5, alpha=0.8)

def draw_blob_with_all_effects(ax, palette, light_source, wobble, edge_color):
    """Draw one blob with shadow, lighting, and gradient."""
    cx, cy = random.random(), random.random()
    rr = random.uniform(0.1, 0.4 - cy * 0.25)
    alpha = 0.85 - (cy * 0.4)
    x, y = blob(center=(cx, cy), r=rr, wobble=wobble)

    # Soft shadow
    for i in range(5, 0, -1):
        offset = i * 0.0015
        alpha_shadow = 0.06 * (i / 5)
        ax.fill(x + offset, y - offset, color=(0, 0, 0, alpha_shadow), edgecolor='none')

    # Color + lighting
    base = random.choice(palette)
    final_color = get_lighting_effect_color(base, (cx, cy), light_source)
    draw_gradient_blob(ax, x, y, final_color, alpha, edge_color)

# ------------------------------------------
# 3. Poster Generator
# ------------------------------------------

def generate_3d_poster(num_layers, num_colors, wobble, light_x, light_y,
                       edge_color, palette_style, seed):
    """Generate the full 3D generative poster."""
    if seed != 0:
        random.seed(seed)
        np.random.seed(seed)

    light_source = (light_x, light_y)
    fig, ax = plt.subplots(figsize=(7, 10))
    fig.patch.set_facecolor((0.98, 0.98, 0.98))
    ax.axis("off")

    palette = get_palette(palette_style, num_colors)

    for _ in range(num_layers):
        draw_blob_with_all_effects(ax, palette, light_source, wobble, edge_color)

    ax.text(0.05, 0.95, "3D Illusion Poster", fontsize=18, weight='bold',
            transform=ax.transAxes, color='white')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    return fig

# ------------------------------------------
# 4. Streamlit UI
# ------------------------------------------

st.set_page_config(page_title="3D Generative Poster", layout="wide")
st.title("✨ Interactive 3D Generative Poster")
st.write("Generate a poster with **distinct palette styles, lighting, gradient, and shadow effects.**")

# Sidebar controls
st.sidebar.header("🎨 Poster Settings")

palette_style = st.sidebar.selectbox("Palette Style", ["Pastel", "Vivid", "Mono", "NoiseTouch"])
num_layers = st.sidebar.slider("Number of Layers", 1, 50, 20)
num_colors = st.sidebar.slider("Palette Size", 2, 15, 6)
wobble = st.sidebar.slider("Wobble Intensity", 0.01, 1.0, 0.15)
light_x = st.sidebar.slider("Light Source X", 0.0, 1.0, 0.1)
light_y = st.sidebar.slider("Light Source Y", 0.0, 1.0, 0.9)
seed = st.sidebar.number_input("Random Seed", 0, 9999, 0)

# Edge color control
edge_mode = st.sidebar.radio("Edge Mode", ["Use Color", "No Edge"])
if edge_mode == "Use Color":
    edge_color = st.sidebar.color_picker("Edge Color", "#FFFFFF")
else:
    edge_color = None

# Generate button
generate = st.button("🎨 Generate Poster")

if generate:
    with st.spinner("Rendering poster..."):
        fig = generate_3d_poster(num_layers, num_colors, wobble, light_x, light_y, edge_color, palette_style, seed)
        st.pyplot(fig)

        # Download
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        buf.seek(0)
        st.download_button(
            label="💾 Download Poster",
            data=buf,
            file_name=f"3D_Poster_{palette_style}.png",
            mime="image/png"
        )

st.markdown("---")
st.caption("Created with Streamlit • Includes Pastel, Vivid, Mono, and NoiseTouch palettes 🌈 + optional edge color.")
