import streamlit as st
from model_helper import predict

# ----------------------------------------------------------------------------
# Personal details shown in the sidebar. Fill in your links; empty ones are hidden.
# ----------------------------------------------------------------------------
AUTHOR_NAME = "Sarthak"
LINKEDIN_URL = ""
GITHUB_URL = ""

st.set_page_config(
    page_title="Vehicle Damage Detection",
    page_icon="🚗",
    layout="wide",
)

# ----------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp, .stMarkdown, p, li, label, span, div {
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
}
.stApp { background: #EEF1F4; }
#MainMenu, footer, .stDeployButton { visibility: hidden; }
.block-container { max-width: 1120px; padding-top: 2.4rem; padding-bottom: 3rem; }

.hero-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: clamp(2.3rem, 5.5vw, 3.6rem);
    line-height: 1.04;
    letter-spacing: -0.025em;
    color: #14213D;
    margin: 0 0 0.9rem 0;
}
.hero-sub {
    font-size: 1.08rem;
    line-height: 1.55;
    color: #3B4A63;
    max-width: 38rem;
    margin: 0 0 1.1rem 0;
}
.chip {
    display: inline-block;
    padding: 0.28rem 0.75rem;
    margin: 0 0.4rem 0.4rem 0;
    border: 1px solid #C2CBD7;
    border-radius: 999px;
    background: #FFFFFF;
    color: #14213D;
    font-size: 0.82rem;
    font-weight: 500;
}
.section-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 600;
    font-size: 1.25rem;
    color: #14213D;
    margin: 1.8rem 0 0.6rem 0;
}

[data-testid="stFileUploaderDropzone"] {
    background: #FFFFFF;
    border: 2px dashed #8E9BAF;
    border-radius: 16px;
    padding: 1.6rem;
}
[data-testid="stFileUploaderDropzone"]:hover { border-color: #14213D; }
[data-testid="stImage"] img {
    border-radius: 16px;
    border: 1px solid #D5DBE3;
}

.report {
    background: #FFFFFF;
    border: 1px solid #D5DBE3;
    border-top: 7px solid var(--accent);
    border-radius: 18px;
    padding: 1.5rem 1.6rem 1.3rem 1.6rem;
}
.report-label { font-size: 0.9rem; color: #5A6A82; margin: 0 0 0.3rem 0; }
.verdict {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: clamp(1.8rem, 3.6vw, 2.5rem);
    line-height: 1.1;
    letter-spacing: -0.02em;
    color: #14213D;
    margin: 0 0 0.5rem 0;
}
.verdict-note {
    display: inline-block;
    padding: 0.25rem 0.7rem;
    border-radius: 8px;
    background: var(--tint);
    color: var(--accent);
    font-weight: 600;
    font-size: 0.92rem;
    margin-bottom: 0.9rem;
}
.report svg { display: block; margin: 0.4rem auto 0.8rem auto; max-width: 190px; width: 100%; height: auto; }
.facts { margin: 0; padding: 0; }
.facts div {
    display: flex;
    justify-content: space-between;
    padding: 0.6rem 0;
    border-top: 1px solid #E3E8EE;
    font-size: 0.95rem;
}
.facts dt { color: #5A6A82; }
.facts dd { margin: 0; font-weight: 600; color: #14213D; }
.empty-note { text-align: center; color: #5A6A82; font-size: 0.95rem; margin: 0 0 0.4rem 0; }

.disclaimer { margin-top: 2.2rem; font-size: 0.85rem; color: #5A6A82; max-width: 44rem; }

[data-testid="stSidebar"] { background: #14213D; }
[data-testid="stSidebar"] * { color: #E4EAF3; }
[data-testid="stSidebar"] a { color: #FFFFFF; text-decoration: underline; }
.side-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 600;
    font-size: 1.15rem;
    margin: 0.2rem 0 0.5rem 0;
}
.side-block { margin: 0 0 1.3rem 0; font-size: 0.93rem; line-height: 1.55; }
.side-block ul { padding-left: 1.1rem; margin: 0.3rem 0 0 0; }
</style>
"""


def render(html: str) -> None:
    """Render an HTML snippet (lines are joined so markdown never sees indentation)."""
    st.markdown(" ".join(line.strip() for line in html.splitlines()), unsafe_allow_html=True)


render(CSS)

# ----------------------------------------------------------------------------
# Presentation helpers (UI only, no model logic here)
# ----------------------------------------------------------------------------
STATUS = {
    "Normal": {
        "color": "#1E8E5A",
        "tint": "#E4F4EB",
        "note": "No damage found",
    },
    "Crushed": {
        "color": "#D96F00",
        "tint": "#FDEEDB",
        "note": "Crush damage found",
    },
    "Breakage": {
        "color": "#C9302F",
        "tint": "#FBE6E6",
        "note": "Breakage found",
    },
}
NEUTRAL = "#9AA7B8"


def car_svg(side=None, color=NEUTRAL) -> str:
    """Top-down car. The front or rear half is tinted with the result colour."""
    zone = ""
    if side == "Front":
        zone = f'<rect x="50" y="14" width="100" height="136" fill="{color}" opacity="0.42" clip-path="url(#body)"/>'
    elif side == "Rear":
        zone = f'<rect x="50" y="150" width="100" height="136" fill="{color}" opacity="0.42" clip-path="url(#body)"/>'
    return f"""
    <svg viewBox="0 0 200 330" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Top view of a car">
      <defs><clipPath id="body"><rect x="50" y="14" width="100" height="272" rx="44"/></clipPath></defs>
      <text x="100" y="12" text-anchor="middle" font-size="13" fill="#5A6A82">Front</text>
      <g transform="translate(0,20)">
        <rect x="36" y="56" width="14" height="46" rx="5" fill="#2A3550"/>
        <rect x="150" y="56" width="14" height="46" rx="5" fill="#2A3550"/>
        <rect x="36" y="196" width="14" height="46" rx="5" fill="#2A3550"/>
        <rect x="150" y="196" width="14" height="46" rx="5" fill="#2A3550"/>
        <rect x="50" y="14" width="100" height="272" rx="44" fill="#FFFFFF" stroke="#14213D" stroke-width="3"/>
        <path d="M66 100 L134 100 L126 136 L74 136 Z" fill="#D5DCE6"/>
        <rect x="72" y="136" width="56" height="62" rx="8" fill="#F3F5F8"/>
        <path d="M74 198 L126 198 L134 224 L66 224 Z" fill="#D5DCE6"/>
        <rect x="62" y="26" width="18" height="7" rx="3" fill="#B7C1CF"/>
        <rect x="120" y="26" width="18" height="7" rx="3" fill="#B7C1CF"/>
        <rect x="62" y="266" width="18" height="7" rx="3" fill="#B7C1CF"/>
        <rect x="120" y="266" width="18" height="7" rx="3" fill="#B7C1CF"/>
        {zone}
      </g>
      <text x="100" y="326" text-anchor="middle" font-size="13" fill="#5A6A82">Rear</text>
    </svg>
    """


def report_card(prediction=None) -> str:
    """Build the inspection result card. With no prediction it shows an empty state."""
    if prediction is None:
        return f"""
        <div class="report" style="--accent:{NEUTRAL}; --tint:#EEF1F4;">
          <p class="report-label">Inspection result</p>
          <p class="empty-note">Upload a photo and the verdict will appear here.</p>
          {car_svg()}
        </div>
        """
    side, condition = prediction.split(" ", 1)
    status = STATUS.get(condition, {"color": NEUTRAL, "tint": "#EEF1F4", "note": condition})
    return f"""
    <div class="report" style="--accent:{status['color']}; --tint:{status['tint']};">
      <p class="report-label">Inspection result</p>
      <p class="verdict">{prediction}</p>
      <span class="verdict-note">{status['note']}</span>
      {car_svg(side, status['color'])}
      <dl class="facts">
        <div><dt>Vehicle area</dt><dd>{side}</dd></div>
        <div><dt>Condition</dt><dd>{condition}</dd></div>
      </dl>
    </div>
    """


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    render(
        """
        <p class="side-title">About this project</p>
        <div class="side-block">
          A computer vision model that looks at a photo of a car and decides whether
          the front or rear is damaged, and how.
        </div>
        <p class="side-title">Model</p>
        <div class="side-block">
          <ul>
            <li>ResNet50 with transfer learning</li>
            <li>Last residual block fine-tuned</li>
            <li>Hyperparameters tuned with Optuna</li>
            <li>About 79% accuracy on the test split</li>
          </ul>
        </div>
        <p class="side-title">Classes it predicts</p>
        <div class="side-block">
          <ul>
            <li>Front: Normal, Crushed, Breakage</li>
            <li>Rear: Normal, Crushed, Breakage</li>
          </ul>
        </div>
        """
    )
    links = []
    if LINKEDIN_URL:
        links.append(f'<a href="{LINKEDIN_URL}" target="_blank">LinkedIn</a>')
    if GITHUB_URL:
        links.append(f'<a href="{GITHUB_URL}" target="_blank">GitHub</a>')
    render(
        f"""
        <p class="side-title">Built by</p>
        <div class="side-block">{AUTHOR_NAME}<br>{'<br>'.join(links)}</div>
        """
    )

# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
render(
    """
    <h1 class="hero-title">Vehicle Damage Detection</h1>
    <p class="hero-sub">
      Upload a photo of a car's front or rear. A fine-tuned deep learning model
      checks it and tells you whether it is normal, crushed or broken.
    </p>
    <span class="chip">PyTorch</span>
    <span class="chip">ResNet50</span>
    <span class="chip">6 damage classes</span>
    <span class="chip">Streamlit</span>
    """
)

# ----------------------------------------------------------------------------
# Main: upload on the left, result on the right
# ----------------------------------------------------------------------------
render('<p class="section-title">Check a vehicle</p>')

left, right = st.columns([1.1, 1], gap="large")
prediction = None

with left:
    uploaded_file = st.file_uploader(
        "Upload a photo of the car",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        image_path = "temp_file.jpg"
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.image(uploaded_file, caption="Photo being analysed", use_container_width=True)
        with st.spinner("Analysing the photo..."):
            try:
                prediction = predict(image_path)
            except Exception as e:
                st.error(f"The model could not process this image. Details: {e}")

with right:
    render(report_card(prediction))

render(
    """
    <p class="disclaimer">
      This is a portfolio project. Predictions come from a single model and can be wrong,
      so they are not a substitute for a professional vehicle inspection.
    </p>
    """
)