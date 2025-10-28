import streamlit as st
import random
import math
import numpy as np
import matplotlib.pyplot as plt
import colorsys
from matplotlib.patches import Polygon
from streamlit_drawable_canvas import st_canvas
import io

# ------------------------------------------
# 1. Core Generative & Lighting Functions
# ------------------------------------------

def random_palette(k=5):
    """Generate a bright vivid palette."""
    palette = []
    for _ in range(k):
        hue = random.random()
        saturation = random.uniform(0.8, 0.9)
        value = random.uniform(0.7, 0.8)
        palette.append(colorsys.hsv_to_rgb(hue, saturation, value))
    return palette

def blob(center=(0.5, 0.5), r=0.3, points=500, wobble=0.15):
    """Generate coordinates for an irregular closed blob."""
    angles = np.linspace(0, 2 * math.pi, points)
    radii = r * (1 + wobble * (np.random.rand(points) - 0.5))
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return x, y

def get_lighting_effect_color(color_rgb, blob_center, light_source):
    """Apply simple lighting: adjust brightness by distance from the light source."""
    dist = math.sqrt((light_source[0] - blob_center[0])**2 + (light_source[1] - blob_center[1])**2)
    brightness_factor = 1.0 - (dist * 0.05)
    h, s, v = colorsys.rgb_to_hsv(*color_rgb)
    new_v = max(0, min(1, v * brightness_factor))
    return colorsys.hsv_to_rgb(h, s, new_v)

def draw_gradient_blob(ax, x, y, base_color, alpha):
    """Draw a soft gradient-filled blob."""
    patch = Polygon(np.column_stack([x, y]), facecolor='none', edgecolor='none')
    ax.add_patch(patch)
    h, s, v = colorsys.rgb_to_hsv(*base_color)
    lighter_color = colorsys.hsv_to_rgb(h, s * 0.2, min(1.0, v * 1.2))

    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))
    extent = [x.min(), x.max(), y.min(), y.max()]

    cmap = plt.cm.colors.LinearSegmentedColormap.from_list("grad", [base_color, lighter_color])
    im = ax.imshow(gradient, aspect='auto', extent=extent, origin='lower', cmap=cmap, alpha=alpha)
    im.set_clip_path(patch)

def draw_blob_with_all_effects(ax, palette, light_source, cx=None, cy=None):
    """Draw one blob with shadow, lighting, and gradient effects."""
    cx = random.random() if cx is None else cx
    cy = random.random() if cy is None else cy

    max_radius = 0.4 - (cy * 0.25)
    rr = random.uniform(0.1, max_radius)
    alpha = 0.8 - (cy * 0.4)
    wobble = random.uniform(0.8, 0.9)
    x, y = blob(center=(cx, cy), r=rr, wobble=wobble)

    # Draw soft shadow
    shadow_layers = 5
    shadow_offset_step = 0.0015
    shadow_base_alpha = 0.06
    for i in range(shadow_layers, 0, -1):
        offset = i * shadow_offset_step
        current_alpha = shadow_base_alpha * (i / shadow_layers)
        shadow_color = (0, 0, 0, current_alpha)
        ax.fill(x + offset, y - offset, color=shadow_color, edgecolor='none')

    # Lighting + gradient fill
    original_color = random.choice(palette)
    final_color = get_lighting_effect_color(original_color, (cx, cy), light_source)
    draw_gradient_blob(ax, x, y, final_color, alpha)

def generate_3d_poster(num_layers=6, num_colors=6, wobble=0.15, light_x=0.1, light_y=0.9, seed=None, clicks=None):
    """Main function to generate the 3D poster."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    light_source = (light_x, light_y)
    fig, ax = plt.subplots(figsize=(7, 10))
    fig.patch.set_facecolor((0.98, 0.98, 0.98))
    ax.axis('off')

    palette = random_palette(num_colors)

    for _ in range(num_layers):
        draw_blob_with_all_effects(ax, palette, light_source)

    # Add blobs from user clicks
    if clicks:
        for (cx, cy) in clicks:
            draw_blob_with_all_effects(ax, palette, light_source, cx=cx, cy=cy)

    ax.text(0.05, 0.95, "3D Illusion Poster", fontsize=18, weight='bold',
            transform=ax.transAxes, color='white')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    return fig

# ------------------------------------------
# 2. Streamlit UI
# ------------------------------------------

st.set_page_config(page_title="3D Generative Poster", layout="wide")
st.title("✨ Interactive 3D Generative Poster")
st.write("Draw new blobs interactively and apply lighting, gradient, and shadow effects.")

# Sidebar controls
st.sidebar.header("⚙️ Poster Settings")
num_layers = st.sidebar.slider("Number of Layers", 1, 50, 20)
num_colors = st.sidebar.slider("Palette Size", 2, 15, 6)
light_x = st.sidebar.slider("Light Source X", 0.0, 1.0, 0.1)
light_y = st.sidebar.slider("Light Source Y", 0.0, 1.0, 0.9)
seed = st.sidebar.number_input("Random Seed", 0, 9999, 0)
st.sidebar.write("Click below poster to add new blobs!")

# Initialize click storage
if "clicks" not in st.session_state:
    st.session_state.clicks = []

# Interactive Canvas for Click Capture
canvas_result = st_canvas(
    fill_color="rgba(255,255,255,0)",  # Transparent fill
    stroke_width=0,
    stroke_color="#000000",
    background_color="#fafafa",
    update_streamlit=True,
    height=400,
    width=400,
    drawing_mode="point",
    key="canvas",
)

# Capture click coordinates
if canvas_result.json_data is not None:
    objects = canvas_result.json_data.get("objects", [])
    for obj in objects:
        cx = obj["left"] / 400  # Normalize X to 0–1 range
        cy = 1 - obj["top"] / 400  # Normalize Y (invert Y-axis)
        if (cx, cy) not in st.session_state.clicks:
            st.session_state.clicks.append((cx, cy))

# Buttons
col1, col2, col3 = st.columns(3)
with col1:
    generate = st.button("🎨 Generate Poster")
with col2:
    clear_clicks = st.button("🧹 Clear Clicks")
with col3:
    reset_all = st.button("♻️ Reset Poster")

if clear_clicks:
    st.session_state.clicks = []

if reset_all:
    st.session_state.clicks = []
    seed = None

# Generate the poster
if generate or st.session_state.clicks:
    fig = generate_3d_poster(
        num_layers, num_colors, 0.15, light_x, light_y, seed, clicks=st.session_state.clicks
    )
    st.pyplot(fig)

    # Download button
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)
    st.download_button(
        label="💾 Download Poster",
        data=buf,
        file_name="3D_Generative_Poster.png",
        mime="image/png"
    )

st.markdown("---")
st.caption("Interactive 3D Generative Poster • Add blobs by clicking below.")

