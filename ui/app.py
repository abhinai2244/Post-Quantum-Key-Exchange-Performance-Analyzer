import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import math
import sys
import os
import io

# ── Ensure src modules can be imported ──────────────────────────────────────
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.classical.rsa import classical_factorization
from src.classical.symmetric import classical_symmetric_search
from src.quantum.shor import build_shor_circuit
from src.quantum.grover import build_grover_circuit
from src.quantum.noise import get_noise_model
from src.quantum.simulator import simulate_circuit
from src.analyzer.scaling import (
    classical_factorization_scaling,
    shor_scaling,
    classical_search_scaling,
    grover_scaling,
)
from src.analyzer.metrics import parse_simulation_metrics, generate_noise_comparison
from src.analyzer.comparison import (
    generate_algorithm_comparison,
    generate_threat_timeline,
    generate_speedup_factors,
    generate_security_gauge_data,
)

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                        PAGE CONFIG & THEME                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝
st.set_page_config(
    page_title="Post-Quantum Key Exchange Performance Analyzer",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject Premium Dark Glassmorphism CSS ───────────────────────────────────
st.markdown("""
<style>
/* ── Import premium font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Root & Body ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 25%, #1b263b 50%, #0d1b2a 75%, #0a0a1a 100%);
    background-attachment: fixed;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: rgba(13, 27, 42, 0.95) !important;
    border-right: 1px solid rgba(0, 255, 255, 0.15);
}

section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e0e0e0 !important;
}

/* ── Glass Card ── */
.glass-card {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(0, 255, 255, 0.12);
    border-radius: 16px;
    padding: 24px;
    margin: 12px 0;
    transition: all 0.3s ease;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.glass-card:hover {
    border-color: rgba(0, 255, 255, 0.35);
    box-shadow: 0 8px 32px rgba(0, 255, 255, 0.08);
    transform: translateY(-2px);
}

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, rgba(0,255,255,0.1) 0%, rgba(139,92,246,0.1) 50%, rgba(236,72,153,0.1) 100%);
    border: 1px solid rgba(0, 255, 255, 0.2);
    border-radius: 20px;
    padding: 40px;
    text-align: center;
    margin-bottom: 30px;
    position: relative;
    overflow: hidden;
}

.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: conic-gradient(from 0deg, transparent, rgba(0,255,255,0.05), transparent 30%);
    animation: hero-spin 6s linear infinite;
}

@keyframes hero-spin {
    100% { transform: rotate(360deg); }
}

.hero-title {
    font-size: 2.6rem;
    font-weight: 900;
    background: linear-gradient(135deg, #00ffff, #8b5cf6, #ec4899, #00ffff);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradient-shift 4s ease infinite;
    position: relative;
    z-index: 1;
    margin: 0 0 10px 0;
    line-height: 1.2;
}

@keyframes gradient-shift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

.hero-subtitle {
    font-size: 1.05rem;
    color: rgba(224, 224, 224, 0.8);
    max-width: 800px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
    line-height: 1.6;
}

/* ── KPI Metric Card ── */
.kpi-card {
    background: rgba(255,255,255, 0.03);
    border: 1px solid rgba(0,255,255,0.15);
    border-radius: 14px;
    padding: 20px 16px;
    text-align: center;
    transition: all 0.3s ease;
}

.kpi-card:hover {
    border-color: rgba(0,255,255,0.4);
    box-shadow: 0 0 20px rgba(0,255,255,0.1);
}

.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    margin: 4px 0;
    line-height: 1.1;
}

.kpi-label {
    font-size: 0.8rem;
    color: rgba(224,224,224,0.55);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 6px;
}

/* ── Section Header ── */
.section-header {
    font-size: 1.6rem;
    font-weight: 700;
    color: #e0e0e0;
    margin: 30px 0 10px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(0,255,255,0.2);
}

/* ── Status badges ── */
.badge-safe {
    background: rgba(34,197,94,0.15);
    color: #22c55e;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
    border: 1px solid rgba(34,197,94,0.3);
    display: inline-block;
}

.badge-broken {
    background: rgba(239,68,68,0.15);
    color: #ef4444;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
    border: 1px solid rgba(239,68,68,0.3);
    display: inline-block;
}

.badge-warn {
    background: rgba(245,158,11,0.15);
    color: #f59e0b;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
    border: 1px solid rgba(245,158,11,0.3);
    display: inline-block;
}

/* ── Tab styling ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(255,255,255,0.02);
    border-radius: 12px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: rgba(224,224,224,0.6);
    font-weight: 500;
}

.stTabs [aria-selected="true"] {
    background: rgba(0,255,255,0.1) !important;
    color: #00ffff !important;
    border-bottom: 2px solid #00ffff !important;
}

/* ── Plotly chart backgrounds ── */
.js-plotly-plot .plotly .main-svg {
    border-radius: 12px;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(0,255,255,0.1) !important;
}

/* ── Hide streamlit branding ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Plotly dark template ────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#e0e0e0"),
    margin=dict(l=40, r=40, t=50, b=40),
)

NEON_COLORS = ["#00ffff", "#8b5cf6", "#ec4899", "#22c55e", "#f59e0b", "#06b6d4"]

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                          HERO BANNER                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">⚛️ Post-Quantum Key Exchange<br>Performance Analyzer</div>
    <div class="hero-subtitle">
        A quantum simulation framework using Qiskit Aer that evaluates how Shor's &amp; Grover's algorithms
        break classical cryptography — and proves why lattice-based &amp; hash-based post-quantum schemes remain secure.
    </div>
</div>
""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                          SIDEBAR                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝
st.sidebar.markdown("## ⚙️ Quantum Configuration")
st.sidebar.markdown("---")

noise_enabled = st.sidebar.checkbox("🔊 Enable NISQ Noise Model", value=False)
if noise_enabled:
    noise_type = st.sidebar.selectbox(
        "Noise Channel",
        ["depolarizing", "bit_flip", "phase_flip"],
        help="Type of quantum error channel to apply to all gates.",
    )
    noise_level = st.sidebar.slider(
        "Error Probability (Per Gate)", 0.0, 0.1, 0.01, step=0.005
    )
    noise_model = get_noise_model(noise_level, noise_type)
    st.sidebar.warning(f"Noise: {noise_type} @ p={noise_level}")
else:
    noise_model = None
    st.sidebar.success("✨ Ideal Simulation (Zero Noise)")

shots = st.sidebar.slider("Simulation Shots", 128, 4096, 1024, step=128)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align:center; color: rgba(224,224,224,0.4); font-size: 0.75rem; padding-top: 10px;">
    Built with Qiskit Aer · Streamlit · Plotly<br>
    Post-Quantum Cryptography Research
</div>
""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                            TABS                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📖 How It Works",
    "🎯 Live Attack Simulation",
    "📉 NISQ Noise Analysis",
    "📊 Performance & Scaling",
    "🛡️ Post-Quantum Security Shield",
    "⏳ Quantum Threat Timeline",
    "🔬 Interactive Lab",
])


# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — HOW IT WORKS (Educational Step-by-Step)
# ═══════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">🧠 Understanding the Quantum Threat to Cryptography</div>', unsafe_allow_html=True)

    # Step-by-step flow
    steps = [
        ("🔐", "1. Classical Key Exchange",
         "RSA and Diffie-Hellman generate key pairs using **prime factorization** and **discrete logarithms**. "
         "These problems are computationally hard for classical computers — requiring sub-exponential to exponential time."),
        ("⚡", "2. Quantum Attacks Emerge",
         "**Shor's Algorithm (1994)** factors integers in **polynomial time** O(n³) on a quantum computer. "
         "**Grover's Algorithm (1996)** provides a **quadratic speedup** O(√N) for brute-force search. "
         "Together, they shatter the mathematical hardness that protects classical cryptography."),
        ("💥", "3. Classical Crypto Breaks",
         "With a sufficiently powerful quantum computer, RSA-2048 could be broken in hours instead of billions of years. "
         "Symmetric keys like AES-128 lose half their effective security bits. The entire PKI infrastructure is at risk."),
        ("🛡️", "4. Post-Quantum Cryptography (PQC)",
         "**Lattice-based** schemes (CRYSTALS-Kyber, Dilithium) rely on the **Learning With Errors** problem — "
         "exponentially hard for both classical AND quantum computers. **Hash-based** signatures (SPHINCS+) "
         "rely on cryptographic hash functions, immune to Shor's algorithm."),
        ("✅", "5. NIST Standardization (2024)",
         "NIST has officially standardized three PQC algorithms: **FIPS 203** (ML-KEM/Kyber), "
         "**FIPS 204** (ML-DSA/Dilithium), and **FIPS 205** (SLH-DSA/SPHINCS+). "
         "The global migration to quantum-safe cryptography has begun."),
    ]

    for icon, title, desc in steps:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size:2rem; margin-bottom:8px;">{icon}</div>
            <div style="font-size:1.15rem; font-weight:700; color:#00ffff; margin-bottom:8px;">{title}</div>
            <div style="color:rgba(224,224,224,0.8); line-height:1.7;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    # Visual flow diagram
    st.markdown('<div class="section-header">🔄 Attack Flow Visualization</div>', unsafe_allow_html=True)

    flow_fig = go.Figure()
    flow_steps = ["Key\nGeneration", "Public Key\nExchange", "Quantum\nAttack", "Key\nBroken!", "PQC\nSolution"]
    colors = ["#06b6d4", "#8b5cf6", "#ef4444", "#ef4444", "#22c55e"]
    x_pos = list(range(len(flow_steps)))

    for i, (step, color) in enumerate(zip(flow_steps, colors)):
        flow_fig.add_trace(go.Scatter(
            x=[i], y=[0], mode="markers+text",
            marker=dict(size=60, color=color, line=dict(width=2, color="white"), opacity=0.9),
            text=[step], textposition="bottom center",
            textfont=dict(size=11, color="#e0e0e0"),
            hoverinfo="skip", showlegend=False,
        ))
        if i < len(flow_steps) - 1:
            arrow_color = "#ef4444" if i >= 2 else "#00ffff"
            flow_fig.add_annotation(
                x=i + 0.55, y=0, ax=i + 0.15, ay=0,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=2,
                arrowcolor=arrow_color,
            )

    flow_fig.update_layout(
        **PLOTLY_LAYOUT,
        title="Classical Crypto → Quantum Attack → Post-Quantum Defense",
        xaxis=dict(visible=False, range=[-0.5, 4.5]),
        yaxis=dict(visible=False, range=[-0.8, 0.5]),
        height=250,
    )
    st.plotly_chart(flow_fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — LIVE ATTACK SIMULATION
# ═══════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">⚡ Quantum Attack Simulation Lab</div>', unsafe_allow_html=True)

    attack_type = st.radio(
        "Select Attack Algorithm:",
        ["🔓 Shor's Algorithm (Factoring RSA)", "🔍 Grover's Algorithm (Key Search)"],
        horizontal=True,
    )

    if "Shor" in attack_type:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("#### 🎛️ Circuit Parameters")
            n_value = st.selectbox("N to factor:", [15, 21], help="Toy integers for demonstration")
            if n_value == 15:
                a_value = st.selectbox("Coprime 'a':", [2, 7, 8, 11, 13], index=1)
            else:
                a_value = st.selectbox("Coprime 'a':", [2, 5, 8, 11], index=0)

            run_shor = st.button("⚡ Execute Shor's Attack", type="primary", use_container_width=True)

        with col2:
            st.markdown("#### 📐 Classical Baseline")
            factor1, factor2, c_time, c_iters = classical_factorization(n_value)
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Classical Factorization of N={n_value}</div>
                <div class="kpi-value" style="color:#f59e0b;">{factor1} × {factor2}</div>
                <div class="kpi-label">{c_iters} iterations · {c_time:.6f}s</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        if run_shor:
            with st.spinner("🔨 Building quantum circuit & simulating..."):
                qc = build_shor_circuit(n_value, a_value)
                results = simulate_circuit(qc, noise_model, shots)

            st.success("✅ Shor's Simulation Complete!")

            # ── KPI Row ─────────────────────────────────────
            m = results['metrics']
            k1, k2, k3, k4 = st.columns(4)
            kpi_data = [
                (k1, "Qubits", str(m['qubits_required']), "#00ffff"),
                (k2, "Circuit Depth", str(m['depth']), "#8b5cf6"),
                (k3, "Total Gates", str(m['total_gates']), "#ec4899"),
                (k4, "Sim Time", f"{m['execution_time_seconds']:.3f}s", "#22c55e"),
            ]
            for col, label, val, color in kpi_data:
                with col:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-value" style="color:{color};">{val}</div>
                        <div class="kpi-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # ── Circuit Diagram ──────────────────────────────
            st.markdown('<div class="section-header">🔬 Quantum Circuit Diagram</div>', unsafe_allow_html=True)
            try:
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                
                # Qiskit's qc.draw('mpl') creates its own figure. 
                # We should capture that figure instead of creating our own subplots which causes overlapping.
                fig_circuit = qc.draw('mpl', style={
                    "backgroundcolor": "#0a0a1a",
                    "textcolor": "#e0e0e0",
                    "linecolor": "#00ffff",
                    "gatefacecolor": "#1b263b",
                    "gatetextcolor": "#e0e0e0",
                    "barrierfacecolor": "#8b5cf6",
                    "fontsize": 10,
                    "subfontsize": 8,
                })
                fig_circuit.patch.set_facecolor('#0a0a1a')
                # ensure it isn't cropped
                fig_circuit.tight_layout()
                st.pyplot(fig_circuit, bbox_inches='tight')
                plt.close(fig_circuit)
            except Exception as e:
                st.info(f"Circuit diagram rendering: using text fallback. ({e})")
                st.code(qc.draw('text'), language=None)

            # ── Measurement Probabilities ────────────────────
            st.markdown('<div class="section-header">📊 Measurement Outcomes</div>', unsafe_allow_html=True)
            probs = results['probabilities']
            sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:15]
            df_probs = pd.DataFrame(sorted_probs, columns=['State', 'Probability'])

            fig_probs = px.bar(
                df_probs, x='State', y='Probability',
                color='Probability',
                color_continuous_scale=["#0a0a1a", "#00ffff", "#8b5cf6"],
                title="Top 15 Measurement Outcomes",
            )
            fig_probs.update_layout(**PLOTLY_LAYOUT, height=400, coloraxis_showscale=False)
            fig_probs.update_traces(marker_line_width=0)
            st.plotly_chart(fig_probs, use_container_width=True)

    else:  # Grover's Algorithm
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("#### 🎛️ Search Parameters")
            num_qubits = st.slider("Qubits (Search Space = 2^N):", 2, 5, 3)
            search_space = 2 ** num_qubits
            default_target = format(search_space - 1, f'0{num_qubits}b')
            target_state = st.text_input(f"Target State ({num_qubits}-bit binary):", default_target)

            valid_target = len(target_state) == num_qubits and all(c in '01' for c in target_state)
            if not valid_target:
                st.error(f"Enter a valid {num_qubits}-bit binary string.")
            else:
                optimal_iters = int(math.pi / 4 * math.sqrt(search_space))
                iters = st.slider("Grover Iterations:", 1, 10, optimal_iters)
                run_grover = st.button("🔍 Execute Grover's Search", type="primary", use_container_width=True)

        with col2:
            if valid_target:
                target_int = int(target_state, 2)
                st.markdown("#### 📐 Classical Baseline")
                found, c_time, c_iters = classical_symmetric_search(target_int, num_qubits)
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Classical Brute-Force Search</div>
                    <div class="kpi-value" style="color:#f59e0b;">{c_iters} iters</div>
                    <div class="kpi-label">vs Grover's {optimal_iters if valid_target else '?'} iters (optimal)</div>
                    <div class="kpi-label">Search space: {search_space} states</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        if valid_target and 'run_grover' in dir() and run_grover:
            with st.spinner("🔨 Building Grover circuit & simulating..."):
                qc = build_grover_circuit(num_qubits, target_state, iters)
                results = simulate_circuit(qc, noise_model, shots)

            st.success("✅ Grover's Simulation Complete!")

            # KPI cards
            m = results['metrics']
            k1, k2, k3, k4 = st.columns(4)
            kpi_items = [
                (k1, "Qubits", str(m['qubits_required']), "#00ffff"),
                (k2, "Depth", str(m['depth']), "#8b5cf6"),
                (k3, "Gates", str(m['total_gates']), "#ec4899"),
                (k4, "Time", f"{m['execution_time_seconds']:.3f}s", "#22c55e"),
            ]
            for col, label, val, color in kpi_items:
                with col:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-value" style="color:{color};">{val}</div>
                        <div class="kpi-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Circuit diagram
            st.markdown('<div class="section-header">🔬 Quantum Circuit Diagram</div>', unsafe_allow_html=True)
            try:
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                
                # Qiskit's qc.draw('mpl') creates its own figure.
                fig_circuit = qc.draw('mpl', style={
                    "backgroundcolor": "#0a0a1a",
                    "textcolor": "#e0e0e0",
                    "linecolor": "#00ffff",
                    "gatefacecolor": "#1b263b",
                    "gatetextcolor": "#e0e0e0",
                    "barrierfacecolor": "#8b5cf6",
                    "fontsize": 10,
                    "subfontsize": 8,
                })
                fig_circuit.patch.set_facecolor('#0a0a1a')
                fig_circuit.tight_layout()
                st.pyplot(fig_circuit, bbox_inches='tight')
                plt.close(fig_circuit)
            except Exception as e:
                st.info(f"Circuit diagram rendering: using text fallback. ({e})")
                st.code(qc.draw('text'), language=None)

            # Measurement Probabilities — highlight target
            st.markdown('<div class="section-header">📊 State Probabilities</div>', unsafe_allow_html=True)
            probs = results['probabilities']
            df_probs = pd.DataFrame(probs.items(), columns=['State', 'Probability'])
            df_probs['Is Target'] = df_probs['State'].apply(lambda s: '🎯 Target' if s == target_state else 'Other')
            df_probs = df_probs.sort_values('Probability', ascending=False)

            fig_grover = px.bar(
                df_probs, x='State', y='Probability', color='Is Target',
                color_discrete_map={'🎯 Target': '#22c55e', 'Other': 'rgba(0,255,255,0.3)'},
                title=f"Grover's Search — Target: |{target_state}⟩",
            )
            fig_grover.update_layout(**PLOTLY_LAYOUT, height=400)
            st.plotly_chart(fig_grover, use_container_width=True)

            target_prob = probs.get(target_state, 0)
            if target_prob > 0.5:
                st.success(f"🎯 Target state |{target_state}⟩ found with **{target_prob:.1%}** probability — Grover's amplification works!")
            else:
                st.warning(f"Target probability is {target_prob:.1%}. Try adjusting the iteration count closer to the optimal value ({optimal_iters}).")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — NISQ NOISE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">🌡️ NISQ Noise Impact Analysis</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <div style="color:rgba(224,224,224,0.85); line-height:1.7;">
            Current quantum computers operate in the <b style="color:#f59e0b;">NISQ era</b>
            (Noisy Intermediate-Scale Quantum). Every gate operation introduces errors.
            As circuit depth grows, noise accumulates and <b style="color:#ef4444;">destroys quantum advantage</b>.
            This analysis shows exactly how noise degrades Grover's attack success rate.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_noise1, col_noise2 = st.columns(2)

    with col_noise1:
        st.markdown("#### Single Noise Channel Sweep")
        if st.button("▶️ Run Noise Degradation Analysis", type="primary", use_container_width=True):
            with st.spinner("Simulating Grover across noise levels..."):
                noise_levels = [0.0, 0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.1]
                target = "101"
                qc = build_grover_circuit(3, target)

                for nt in ["depolarizing", "bit_flip", "phase_flip"]:
                    success_rates = []
                    for nl in noise_levels:
                        nm = get_noise_model(nl, nt)
                        res = simulate_circuit(qc, nm, shots=1024)
                        success_rates.append(res['probabilities'].get(target, 0.0))

                    if nt == "depolarizing":
                        dep_data = success_rates
                    elif nt == "bit_flip":
                        bit_data = success_rates
                    else:
                        phase_data = success_rates

                fig_noise = go.Figure()
                fig_noise.add_trace(go.Scatter(
                    x=noise_levels, y=dep_data, mode='lines+markers',
                    name='Depolarizing', line=dict(color='#00ffff', width=3),
                    marker=dict(size=8),
                ))
                fig_noise.add_trace(go.Scatter(
                    x=noise_levels, y=bit_data, mode='lines+markers',
                    name='Bit Flip', line=dict(color='#8b5cf6', width=3),
                    marker=dict(size=8),
                ))
                fig_noise.add_trace(go.Scatter(
                    x=noise_levels, y=phase_data, mode='lines+markers',
                    name='Phase Flip', line=dict(color='#ec4899', width=3),
                    marker=dict(size=8),
                ))
                fig_noise.add_hline(
                    y=1/8, line_dash="dash", line_color="#ef4444",
                    annotation_text="Random Guessing (1/8)",
                    annotation_font_color="#ef4444",
                )
                fig_noise.update_layout(
                    **PLOTLY_LAYOUT,
                    title="Grover Success Rate vs Noise (3-qubit, target=|101⟩)",
                    xaxis_title="Error Probability (Per Gate)",
                    yaxis_title="Success Probability",
                    height=450,
                    legend=dict(x=0.7, y=0.95),
                )
                st.plotly_chart(fig_noise, use_container_width=True)

    with col_noise2:
        st.markdown("#### 3D Noise Heatmap")
        if st.button("▶️ Generate 3D Noise Surface", type="primary", use_container_width=True):
            with st.spinner("Running multi-qubit noise sweep (this may take ~30s)..."):
                from src.analyzer.comparison import generate_noise_heatmap_data
                df_heat = generate_noise_heatmap_data(
                    noise_types=["depolarizing"],
                    noise_levels=[0.0, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1],
                    qubit_counts=[2, 3, 4, 5],
                )

            # Pivot for surface plot
            pivot = df_heat.pivot_table(
                values='Success Probability',
                index='Qubits',
                columns='Noise Level',
                aggfunc='mean',
            )

            fig_3d = go.Figure(data=[go.Surface(
                z=pivot.values,
                x=pivot.columns.tolist(),
                y=pivot.index.tolist(),
                colorscale=[[0, '#ef4444'], [0.5, '#f59e0b'], [1, '#22c55e']],
                opacity=0.9,
            )])
            fig_3d.update_layout(
                **PLOTLY_LAYOUT,
                title="Success Probability Surface (Depolarizing Noise)",
                scene=dict(
                    xaxis_title="Noise Level",
                    yaxis_title="Qubits",
                    zaxis_title="P(success)",
                    bgcolor="rgba(0,0,0,0)",
                ),
                height=500,
            )
            st.plotly_chart(fig_3d, use_container_width=True)

    st.info("📌 **Key Insight:** As noise increases beyond ~3%, the success probability drops to random guessing. "
            "This proves that real quantum attacks require **fault-tolerant quantum computers** with error correction — technology still years away.")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 — PERFORMANCE & SCALING
# ═══════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">📈 Asymptotic Scaling & Quantum Speedup</div>', unsafe_allow_html=True)

    # ── Speedup Metrics KPI ─────────────────────────────────────────────
    speedup_bits = [32, 64, 128, 256, 512, 1024, 2048]
    df_speedup = generate_speedup_factors(speedup_bits)

    st.markdown("#### 🚀 Quantum Speedup Factors (vs Classical)")
    sc1, sc2, sc3, sc4 = st.columns(4)
    # Pick representative values at different key sizes
    representative = df_speedup[df_speedup['Key Size (bits)'].isin([64, 256, 1024, 2048])]

    for col, (_, row) in zip([sc1, sc2, sc3, sc4], representative.iterrows()):
        bits = int(row['Key Size (bits)'])
        factor_log = row['Factorization Speedup (log10)']
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{bits}-bit RSA</div>
                <div class="kpi-value" style="color:#00ffff;">10<sup>{factor_log:.0f}</sup>×</div>
                <div class="kpi-label">Shor's Speedup</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Side-by-side scaling charts ─────────────────────────────────────
    col_scale1, col_scale2 = st.columns(2)

    with col_scale1:
        st.markdown("#### Asymmetric Crypto (RSA Factorization)")
        bits = list(range(10, 80, 3))
        class_scale = classical_factorization_scaling(bits)
        quant_scale = shor_scaling(bits)

        fig_rsa = go.Figure()
        fig_rsa.add_trace(go.Scatter(
            x=bits, y=np.log10(class_scale),
            mode='lines', name='Classical (GNFS)',
            line=dict(color='#ef4444', width=3),
            fill='tozeroy', fillcolor='rgba(239,68,68,0.1)',
        ))
        fig_rsa.add_trace(go.Scatter(
            x=bits, y=np.log10(quant_scale),
            mode='lines', name="Shor's (Quantum)",
            line=dict(color='#22c55e', width=3),
            fill='tozeroy', fillcolor='rgba(34,197,94,0.1)',
        ))
        fig_rsa.update_layout(
            **PLOTLY_LAYOUT,
            title="RSA Factorization Complexity (Log₁₀)",
            xaxis_title="Key Size (bits)", yaxis_title="Operations (Log₁₀ scale)",
            height=420,
            legend=dict(x=0.02, y=0.98),
        )
        st.plotly_chart(fig_rsa, use_container_width=True)

    with col_scale2:
        st.markdown("#### Symmetric Crypto (AES Key Search)")
        bits = list(range(10, 50, 2))
        c_search = classical_search_scaling(bits)
        q_search = grover_scaling(bits)

        fig_aes = go.Figure()
        fig_aes.add_trace(go.Scatter(
            x=bits, y=np.log10(c_search),
            mode='lines', name='Classical (Brute Force)',
            line=dict(color='#ef4444', width=3),
            fill='tozeroy', fillcolor='rgba(239,68,68,0.1)',
        ))
        fig_aes.add_trace(go.Scatter(
            x=bits, y=np.log10(q_search),
            mode='lines', name="Grover's (Quantum)",
            line=dict(color='#22c55e', width=3),
            fill='tozeroy', fillcolor='rgba(34,197,94,0.1)',
        ))
        fig_aes.update_layout(
            **PLOTLY_LAYOUT,
            title="Symmetric Key Search Complexity (Log₁₀)",
            xaxis_title="Key Size (bits)", yaxis_title="Operations (Log₁₀ scale)",
            height=420,
            legend=dict(x=0.02, y=0.98),
        )
        st.plotly_chart(fig_aes, use_container_width=True)

    # ── Animated Scaling Race ────────────────────────────────────────────
    st.markdown('<div class="section-header">🏁 Animated Complexity Race</div>', unsafe_allow_html=True)

    anim_bits = list(range(10, 70, 2))
    anim_class = classical_factorization_scaling(anim_bits)
    anim_quant = shor_scaling(anim_bits)

    frames_data = []
    for i in range(1, len(anim_bits) + 1):
        for j in range(i):
            frames_data.append({
                'Key Size': anim_bits[j],
                'Operations (Log₁₀)': math.log10(max(anim_class[j], 1)),
                'Algorithm': 'Classical (GNFS)',
                'Frame': anim_bits[i - 1],
            })
            frames_data.append({
                'Key Size': anim_bits[j],
                'Operations (Log₁₀)': math.log10(max(anim_quant[j], 1)),
                'Algorithm': "Shor's (Quantum)",
                'Frame': anim_bits[i - 1],
            })

    df_anim = pd.DataFrame(frames_data)
    fig_race = px.line(
        df_anim, x='Key Size', y='Operations (Log₁₀)',
        color='Algorithm', animation_frame='Frame',
        color_discrete_map={'Classical (GNFS)': '#ef4444', "Shor's (Quantum)": '#22c55e'},
        title="Watch the Exponential Gap Grow",
    )
    fig_race.update_layout(**PLOTLY_LAYOUT, height=450)
    st.plotly_chart(fig_race, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 5 — POST-QUANTUM SECURITY SHIELD
# ═══════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">🛡️ Post-Quantum Algorithm Security Comparison</div>', unsafe_allow_html=True)

    # ── Radar Chart ──────────────────────────────────────────────────────
    df_radar = generate_algorithm_comparison()
    dimensions = ["Key Size Efficiency", "Classical Security", "Quantum Resistance", "Performance Speed", "Standardization Maturity"]

    fig_radar = go.Figure()
    for i, (_, row) in enumerate(df_radar.iterrows()):
        values = [row[d] for d in dimensions]
        values.append(values[0])  # close the polygon
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=dimensions + [dimensions[0]],
            fill='toself',
            name=row['Algorithm'],
            line=dict(color=NEON_COLORS[i % len(NEON_COLORS)], width=2),
            opacity=0.7,
        ))

    fig_radar.update_layout(
        **PLOTLY_LAYOUT,
        title="Algorithm Capability Radar (0-100 Scale)",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        ),
        height=550,
        legend=dict(x=1.05, y=1),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── Security Gauge Cards ─────────────────────────────────────────────
    st.markdown('<div class="section-header">🔒 Effective Security Strength</div>', unsafe_allow_html=True)

    gauge_data = generate_security_gauge_data()
    cols = st.columns(3)
    for i, entry in enumerate(gauge_data):
        with cols[i % 3]:
            classical_bits = entry['Classical Security (bits)']
            quantum_bits = entry['Quantum Security (bits)']
            color = entry['Color']
            status = entry['Status']

            if '❌' in status:
                badge_class = 'badge-broken'
            elif '⚠️' in status:
                badge_class = 'badge-warn'
            else:
                badge_class = 'badge-safe'

            st.markdown(f"""
            <div class="glass-card" style="text-align:center; border-color: {color}33;">
                <div style="font-weight:700; color:{color}; font-size:1.1rem; margin-bottom:8px;">{entry['Algorithm']}</div>
                <div style="color:rgba(224,224,224,0.5); font-size:0.8rem; margin-bottom:12px;">{entry['Type']}</div>
                <div style="display:flex; justify-content:space-around; margin-bottom:12px;">
                    <div>
                        <div style="font-size:1.8rem; font-weight:800; color:#e0e0e0;">{classical_bits}</div>
                        <div style="font-size:0.7rem; color:rgba(224,224,224,0.5);">CLASSICAL BITS</div>
                    </div>
                    <div>
                        <div style="font-size:1.8rem; font-weight:800; color:{color};">{quantum_bits}</div>
                        <div style="font-size:0.7rem; color:rgba(224,224,224,0.5);">QUANTUM BITS</div>
                    </div>
                </div>
                <div class="{badge_class}">{status}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Why PQC Works ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🧮 Why Post-Quantum Crypto Resists Quantum Attacks</div>', unsafe_allow_html=True)

    col_pq1, col_pq2 = st.columns(2)
    with col_pq1:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size:1.3rem; font-weight:700; color:#06b6d4; margin-bottom:10px;">
                🔷 Lattice-Based (Kyber / Dilithium)
            </div>
            <div style="color:rgba(224,224,224,0.8); line-height:1.7;">
                Built on the <b>Learning With Errors (LWE)</b> problem and the <b>Shortest Vector Problem (SVP)</b>
                in high-dimensional lattices.
                <br><br>
                <b style="color:#22c55e;">Why Quantum-Safe:</b> No known quantum algorithm (including Shor's) can efficiently
                solve lattice problems. Complexity remains <b>exponential</b> against both classical and quantum computers.
                <br><br>
                <b>NIST Standards:</b> FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_pq2:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size:1.3rem; font-weight:700; color:#ec4899; margin-bottom:10px;">
                🔶 Hash-Based (SPHINCS+)
            </div>
            <div style="color:rgba(224,224,224,0.8); line-height:1.7;">
                Security relies solely on the <b>cryptographic hash function</b> (e.g., SHA-3).
                <br><br>
                <b style="color:#22c55e;">Why Quantum-Safe:</b> While Grover's can reverse hashes in O(√N),
                <b>doubling the hash output size</b> (256→512 bits) completely eliminates the quantum advantage.
                No polynomial-time quantum algorithm applies to hash functions.
                <br><br>
                <b>NIST Standard:</b> FIPS 205 (SLH-DSA)
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 6 — QUANTUM THREAT TIMELINE
# ═══════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-header">⏳ The Race Between Quantum Computing & Cryptography</div>', unsafe_allow_html=True)

    df_timeline = generate_threat_timeline()

    category_colors = {
        "Classical Crypto": "#06b6d4",
        "Quantum Threat": "#ef4444",
        "Quantum Milestone": "#f59e0b",
        "Post-Quantum": "#22c55e",
    }

    fig_timeline = go.Figure()

    for cat, color in category_colors.items():
        subset = df_timeline[df_timeline['Category'] == cat]
        fig_timeline.add_trace(go.Scatter(
            x=subset['Year'],
            y=[cat] * len(subset),
            mode='markers+text',
            name=cat,
            marker=dict(size=18, color=color, line=dict(width=2, color='white'), symbol='diamond'),
            text=subset['Event'],
            textposition='top center',
            textfont=dict(size=10, color=color),
            hovertext=subset['Description'],
            hoverinfo='text',
        ))

    fig_timeline.update_layout(
        **PLOTLY_LAYOUT,
        title="Cryptography & Quantum Computing Timeline (1976 — 2025)",
        xaxis=dict(
            title="Year",
            dtick=5,
            range=[1974, 2027],
            gridcolor="rgba(255,255,255,0.05)",
        ),
        yaxis=dict(
            title="",
            categoryorder='array',
            categoryarray=list(category_colors.keys()),
            gridcolor="rgba(255,255,255,0.05)",
        ),
        height=500,
        legend=dict(x=0.01, y=-0.15, orientation='h'),
        hoverlabel=dict(
            bgcolor="rgba(10,10,26,0.95)",
            bordercolor="rgba(0,255,255,0.3)",
            font_size=12,
        ),
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

    # Milestone cards
    st.markdown('<div class="section-header">📍 Key Milestones</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, (_, row) in enumerate(df_timeline.iterrows()):
        color = category_colors.get(row['Category'], '#00ffff')
        with cols[i % 3]:
            st.markdown(f"""
            <div class="glass-card" style="border-color: {color}33; min-height: 160px;">
                <div style="font-size:0.75rem; color:{color}; font-weight:600; letter-spacing:1px;">{row['Year']} · {row['Category'].upper()}</div>
                <div style="font-size:1.05rem; font-weight:700; color:#e0e0e0; margin:6px 0;">{row['Event']}</div>
                <div style="font-size:0.85rem; color:rgba(224,224,224,0.65); line-height:1.5;">{row['Description']}</div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 7 — INTERACTIVE LAB
# ═══════════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown('<div class="section-header">🔬 Interactive Cryptography Lab</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <div style="color:rgba(224,224,224,0.85); line-height:1.7;">
            <b style="color:#00ffff;">Try it yourself!</b> Enter a composite number below and watch it get
            factored by classical trial division vs. Shor's quantum algorithm. See the quantum advantage in real-time.
        </div>
    </div>
    """, unsafe_allow_html=True)

    lab_col1, lab_col2 = st.columns(2)

    with lab_col1:
        st.markdown("#### 🔢 Classical Factorization Explorer")
        user_n = st.number_input("Enter a composite number to factor:", min_value=4, max_value=100000, value=91, step=1)
        if st.button("⚡ Factor It!", type="primary", use_container_width=True):
            f1, f2, t, iters = classical_factorization(int(user_n))
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;">
                <div class="kpi-label">Factorization Result</div>
                <div class="kpi-value" style="color:#00ffff;">{int(user_n)} = {f1} × {f2}</div>
                <div style="margin-top:12px;">
                    <span class="kpi-label">Iterations: {iters}</span> ·
                    <span class="kpi-label">Time: {t:.6f}s</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Show how Shor's would compare (theoretical)
            bits = int(math.log2(max(user_n, 2))) + 1
            shor_ops = bits ** 3
            classical_ops = max(iters, 1)
            if classical_ops > shor_ops:
                st.markdown(f"""
                <div class="glass-card" style="border-color: rgba(34,197,94,0.3); text-align:center;">
                    <div style="color:#22c55e; font-weight:700; font-size:1.1rem;">
                        Shor's Theoretical Advantage
                    </div>
                    <div style="color:rgba(224,224,224,0.7); margin-top:8px;">
                        Classical: ~{classical_ops} operations<br>
                        Shor's: ~{shor_ops} operations ({bits}-bit number → O(n³))<br>
                        <b style="color:#00ffff;">Speedup: {classical_ops / shor_ops:.1f}×</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with lab_col2:
        st.markdown("#### 📊 Scaling Projection for Your Number")

        if st.button("📈 Show Scaling Projection", use_container_width=True):
            user_bits = int(math.log2(max(user_n, 2))) + 1
            proj_bits = list(range(user_bits, user_bits + 40, 2))
            proj_class = classical_factorization_scaling(proj_bits)
            proj_quant = shor_scaling(proj_bits)

            fig_proj = go.Figure()
            fig_proj.add_trace(go.Scatter(
                x=proj_bits, y=np.log10(proj_class),
                mode='lines+markers', name='Classical (GNFS)',
                line=dict(color='#ef4444', width=3), marker=dict(size=6),
                fill='tozeroy', fillcolor='rgba(239,68,68,0.08)',
            ))
            fig_proj.add_trace(go.Scatter(
                x=proj_bits, y=np.log10(proj_quant),
                mode='lines+markers', name="Shor's Algorithm",
                line=dict(color='#22c55e', width=3), marker=dict(size=6),
                fill='tozeroy', fillcolor='rgba(34,197,94,0.08)',
            ))
            fig_proj.add_vline(
                x=user_bits, line_dash="dash", line_color="#00ffff",
                annotation_text=f"Your number ({int(user_n)})",
                annotation_font_color="#00ffff",
            )
            fig_proj.update_layout(
                **PLOTLY_LAYOUT,
                title=f"Scaling Projection Starting from {user_bits}-bit Numbers",
                xaxis_title="Key Size (bits)", yaxis_title="Operations (Log₁₀)",
                height=450,
            )
            st.plotly_chart(fig_proj, use_container_width=True)

    # ── RSA Key Demo ─────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🔑 RSA Key Pair Generator</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-card">
        <div style="color:rgba(224,224,224,0.85); line-height:1.7;">
            Generate a toy RSA keypair to see the mathematical structure that Shor's algorithm exploits.
            Pick two small primes and watch the key generation process.
        </div>
    </div>
    """, unsafe_allow_html=True)

    rsa_col1, rsa_col2 = st.columns(2)
    with rsa_col1:
        p = st.number_input("Prime p:", min_value=2, max_value=997, value=61)
        q = st.number_input("Prime q:", min_value=2, max_value=997, value=53)

    with rsa_col2:
        if st.button("🔑 Generate RSA Keypair", type="primary", use_container_width=True):
            from src.classical.rsa import is_prime, generate_keypair
            if not is_prime(int(p)):
                st.error(f"{int(p)} is not prime!")
            elif not is_prime(int(q)):
                st.error(f"{int(q)} is not prime!")
            elif p == q:
                st.error("p and q must be different!")
            else:
                public, private = generate_keypair(int(p), int(q))
                n = int(p) * int(q)
                st.markdown(f"""
                <div class="glass-card" style="border-color: rgba(0,255,255,0.3);">
                    <div style="text-align:center; margin-bottom:16px;">
                        <div class="kpi-label">RSA Modulus (N = p × q)</div>
                        <div class="kpi-value" style="color:#00ffff;">{n}</div>
                    </div>
                    <div style="display:flex; justify-content:space-around;">
                        <div style="text-align:center;">
                            <div style="font-size:0.8rem; color:rgba(224,224,224,0.5);">PUBLIC KEY (e, N)</div>
                            <div style="font-size:1.1rem; font-weight:600; color:#22c55e;">({public[0]}, {public[1]})</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:0.8rem; color:rgba(224,224,224,0.5);">PRIVATE KEY (d, N)</div>
                            <div style="font-size:1.1rem; font-weight:600; color:#ef4444;">({private[0]}, {private[1]})</div>
                        </div>
                    </div>
                    <div style="text-align:center; margin-top:12px; color:rgba(224,224,224,0.5); font-size:0.8rem;">
                        ⚠️ Shor's algorithm can recover p={int(p)} and q={int(q)} from N={n} in polynomial time
                    </div>
                </div>
                """, unsafe_allow_html=True)
