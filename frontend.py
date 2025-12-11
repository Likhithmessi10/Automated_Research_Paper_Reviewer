import streamlit as st
import pandas as pd
import os
import tempfile
import plotly.graph_objects as go
import plotly.express as px
import time

# ------------------------------------------------------------------
# Import the core review logic from your file
# ------------------------------------------------------------------
try:
    from review_model import review_pdf, generate_final_report
    from review_model import STRENGTH_PATTERNS, WEAKNESS_PATTERNS, IMPROVEMENT_PATTERNS
except ImportError:
    st.error("Could not find 'review_model.py'. Please ensure it is in the same directory.")
    st.stop()
except Exception as e:
    st.error(f"Error loading dependencies or functions from 'review_model.py': {e}")
    st.stop()

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="PaperLens - AI Research Paper Reviewer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ENHANCED CUSTOM CSS ---
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        padding-top: 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Animated Header */
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
        background-size: 50px 50px;
        animation: grid-animation 20s linear infinite;
    }
    
    @keyframes grid-animation {
        0% { transform: translate(0, 0); }
        100% { transform: translate(50px, 50px); }
    }
    
    .main-header h1 {
        color: white;
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.95);
        font-size: 1.2rem;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        text-align: center;
        height: 100%;
        border: 2px solid transparent;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    /* Upload Section */
    .upload-section {
        background: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        border: 3px dashed #667eea;
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: #764ba2;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border-left: 5px solid #667eea;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Verdict Card */
    .verdict-card {
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        border: 3px solid;
    }
    
    .verdict-card:hover {
        transform: scale(1.02);
    }
    
    .verdict-emoji {
        font-size: 4rem;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* Feedback Items */
    .feedback-item {
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 15px;
        border-left: 5px solid;
        background: white;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .feedback-item:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.12);
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #e8f4f8 0%, #d1f2eb 100%);
        border-left: 5px solid #3498db;
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 3px 10px rgba(52, 152, 219, 0.1);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        animation: progress-animation 1s ease-in-out;
    }
    
    @keyframes progress-animation {
        0% { width: 0%; }
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.85rem 2.5rem;
        border-radius: 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 0.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1);
    }
    
    /* Section Headers */
    h2, h3 {
        color: #2d3748;
        font-weight: 700;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Animation for cards appearing */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animated-card {
        animation: fadeInUp 0.6s ease-out;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("""
    <div class="main-header">
        <h1>📝 PaperLens</h1>
        <p>Advanced AI-Powered Research Paper Analysis & Review System</p>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    
    with st.expander("🤖 AI Settings", expanded=True):
        rewrite_toggle = st.toggle("Enable AI Rewriting", value=True, 
                                   help="Use Ollama to enhance and polish the feedback")
        model_choice = st.selectbox(
            "Select Ollama Model",
            options=["llama3.1:8b", "mistral:7b", "phi3", "llama3:latest"],
            index=0,
            help="Choose your locally installed Ollama model"
        )
    
    with st.expander("🎯 Quality Thresholds", expanded=False):
        auto_reject_thresh = st.slider(
            "Plagiarism Rejection Threshold",
            min_value=0,
            max_value=100,
            value=40,
            help="Papers exceeding this plagiarism % will be auto-rejected"
        )
        st.caption(f"Current: {auto_reject_thresh}% threshold")
    
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    if 'total_reviews' not in st.session_state:
        st.session_state.total_reviews = 0
    st.metric("Papers Reviewed", st.session_state.total_reviews)
    
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <p style='color: white; font-size: 0.9rem;'>
                💡 Need help?<br>
                Check our documentation
            </p>
        </div>
    """, unsafe_allow_html=True)

# --- FEATURE HIGHLIGHTS ---
st.markdown("### ✨ Why Choose PaperLens?")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">⚡</span>
            <h4>Lightning Fast</h4>
            <p>Get comprehensive results in seconds</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🔬</span>
            <h4>Deep Analysis</h4>
            <p>Multi-layered evaluation system</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📈</span>
            <h4>Clear Metrics</h4>
            <p>Quantified quality scores</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">💡</span>
            <h4>Actionable</h4>
            <p>Specific improvement tips</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- FILE UPLOAD SECTION ---
st.markdown("""
    <div class="upload-section">
        <h2>🚀 Upload Your Research Paper</h2>
        <p style='font-size: 1.1rem; color: #64748b; margin-top: 0.5rem;'>
            Drag and drop your PDF or click to browse
        </p>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type="pdf",
    help="Supported format: PDF | Max file size: 200MB",
    label_visibility="collapsed"
)

if uploaded_file is not None:
    # Increment review counter
    st.session_state.total_reviews += 1
    
    # File Details in Expandable Card
    with st.expander("📄 File Information", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**📎 Filename**  \n{uploaded_file.name}")
        with col2:
            st.markdown(f"**💾 File Size**  \n{uploaded_file.size / 1024:.2f} KB")
        with col3:
            st.markdown(f"**📋 Type**  \n{uploaded_file.type}")

    # Animated Progress Section
    st.markdown("---")
    progress_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        progress_message = st.empty()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        pdf_path = tmp_file.name

    try:
        # Progress Animation
        stages = [
            (20, "🔍 Extracting content from PDF...", 0.5),
            (40, "🧠 Analyzing with heuristic patterns...", 0.7),
            (60, "🤖 Running Expert AI Analysis...", 1.0),
            (80, "📊 Generating comprehensive report...", 0.5),
        ]
        
        for progress, message, delay in stages:
            status_text.markdown(f"### {message}")
            progress_bar.progress(progress)
            time.sleep(delay)
        
        # Run the review logic
        with st.spinner("🔬 Deep analysis in progress..."):
            review_results = review_pdf(pdf_path, rewrite=rewrite_toggle, ollama_model=model_choice)

        status_text.markdown("### ✅ Analysis Complete!")
        progress_bar.progress(100)
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()

        # --- RESULTS DASHBOARD ---
        st.markdown("---")
        st.markdown("## 🎯 Analysis Results")

        # Verdict Section - Full Width
        verdict = review_results.get("verdict", "REVIEW FAILED")
        if "ACCEPT" in verdict:
            verdict_color = "#10b981"
            verdict_emoji = "✅"
            verdict_bg = "#d1fae5"
            verdict_border = "#10b981"
        elif "WEAK" in verdict:
            verdict_color = "#f59e0b"
            verdict_emoji = "⚠️"
            verdict_bg = "#fef3c7"
            verdict_border = "#f59e0b"
        else:
            verdict_color = "#ef4444"
            verdict_emoji = "❌"
            verdict_bg = "#fee2e2"
            verdict_border = "#ef4444"

        st.markdown(f"""
            <div class="verdict-card animated-card" style='
                background: {verdict_bg};
                border-color: {verdict_border};
            '>
                <div class="verdict-emoji">{verdict_emoji}</div>
                <h1 style='color: {verdict_color}; margin: 1rem 0; font-size: 2.5rem;'>{verdict}</h1>
                <p style='color: #64748b; font-size: 1.2rem; margin: 0;'>Final Decision</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Metrics Row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            confidence = round(review_results.get("confidence", 0.0) * 100)
            st.markdown("""
                <div class="metric-card animated-card">
                    <h3 style='color: #667eea; margin: 0;'>🎯 Confidence</h3>
                    <p style='font-size: 2.5rem; font-weight: 700; margin: 0.5rem 0; color: #2d3748;'>{}</p>
                    <p style='color: #64748b; margin: 0;'>Reliability Score</p>
                </div>
            """.format(f"{confidence}%"), unsafe_allow_html=True)

        with col2:
            raw_score = round(review_results.get("final_score", 0.0), 2)
            st.markdown("""
                <div class="metric-card animated-card">
                    <h3 style='color: #667eea; margin: 0;'>📈 Quality Score</h3>
                    <p style='font-size: 2.5rem; font-weight: 700; margin: 0.5rem 0; color: #2d3748;'>{}</p>
                    <p style='color: #64748b; margin: 0;'>Overall Rating</p>
                </div>
            """.format(f"{raw_score}"), unsafe_allow_html=True)

        with col3:
            total_feedback = (
                len(review_results.get("strengths", [])) +
                len(review_results.get("weaknesses", [])) +
                len(review_results.get("improvements", []))
            )
            st.markdown("""
                <div class="metric-card animated-card">
                    <h3 style='color: #667eea; margin: 0;'>💬 Total Insights</h3>
                    <p style='font-size: 2.5rem; font-weight: 700; margin: 0.5rem 0; color: #2d3748;'>{}</p>
                    <p style='color: #64748b; margin: 0;'>Feedback Points</p>
                </div>
            """.format(total_feedback), unsafe_allow_html=True)

        with col4:
            plag = review_results.get("plagiarism_percent", 0)
            plag_color = "#10b981" if plag < 20 else "#f59e0b" if plag < 40 else "#ef4444"
            st.markdown("""
                <div class="metric-card animated-card">
                    <h3 style='color: #667eea; margin: 0;'>🧬 Originality</h3>
                    <p style='font-size: 2.5rem; font-weight: 700; margin: 0.5rem 0; color: {};'>{}</p>
                    <p style='color: #64748b; margin: 0;'>Plagiarism Check</p>
                </div>
            """.format(plag_color, f"{plag}%"), unsafe_allow_html=True)

        # --- PLAGIARISM DETAILED ANALYSIS ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🧬 Plagiarism & Originality Analysis")
        
        plag = review_results.get("plagiarism_percent", 0)
        orig = review_results.get("originality_percent", max(0, 100 - int(plag)))
        risk = review_results.get("plagiarism_risk", "UNAVAILABLE")

        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig_plag = go.Figure(go.Indicator(
                mode="gauge+number",
                value=plag,
                title={'text': "Plagiarism", 'font': {'size': 18}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#ef4444"},
                    'steps': [
                        {'range': [0, 20], 'color': '#d1fae5'},
                        {'range': [20, 40], 'color': '#fef3c7'},
                        {'range': [40, 100], 'color': '#fee2e2'}
                    ],
                }
            ))
            fig_plag.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_plag, use_container_width=True)

        with col2:
            fig_orig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=orig,
                title={'text': "Originality", 'font': {'size': 18}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#10b981"},
                    'steps': [
                        {'range': [0, 60], 'color': '#fee2e2'},
                        {'range': [60, 80], 'color': '#fef3c7'},
                        {'range': [80, 100], 'color': '#d1fae5'}
                    ],
                }
            ))
            fig_orig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_orig, use_container_width=True)

        with col3:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if isinstance(risk, str):
                risk_u = risk.upper()
            else:
                risk_u = str(risk).upper()
            
            if risk_u == "LOW":
                st.success("### 🟢 Low Risk")
                st.markdown("The paper shows good originality")
            elif risk_u == "MEDIUM":
                st.warning("### 🟡 Medium Risk")
                st.markdown("Some sections may need review")
            elif risk_u == "HIGH":
                st.error("### 🔴 High Risk")
                st.markdown("Significant plagiarism detected")
            else:
                st.info(f"### ⚪ {risk_u}")

        # --- CONFIDENCE VISUALIZATION ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📊 Confidence Level Breakdown")
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=confidence,
            delta={'reference': 70, 'increasing': {'color': "#10b981"}},
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Confidence", 'font': {'size': 24}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "darkblue"},
                'bar': {'color': verdict_color, 'thickness': 0.75},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 33], 'color': '#fee2e2'},
                    {'range': [33, 66], 'color': '#fef3c7'},
                    {'range': [66, 100], 'color': '#d1fae5'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", font={'size': 14})
        st.plotly_chart(fig, use_container_width=True)

        # --- EXPERT AI REVIEW (V2) ---
        st.markdown("---")
        st.markdown("## 🧠 Expert AI Review Dashboard")
        
        card = review_results.get("final_card", {})
        
        if card:
            # Scorecard
            col1, col2, col3, col4 = st.columns(4)
            
            scores = [
                ("Originality", card.get('originality', '-'), "🎨"),
                ("Methodology", card.get('methodology', '-'), "🔬"),
                ("Clarity", card.get('clarity', '-'), "📖"),
                ("Impact", card.get('recommendation', 'N/A'), "⭐")
            ]
            
            for col, (label, value, icon) in zip([col1, col2, col3, col4], scores):
                with col:
                    if label == "Impact":
                        st.markdown(f"""
                            <div class="metric-card">
                                <div style='font-size: 2rem;'>{icon}</div>
                                <h4 style='color: #667eea; margin: 0.5rem 0;'>{label}</h4>
                                <p style='font-size: 1.5rem; font-weight: 700; color: {verdict_color};'>{value}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div style='font-size: 2rem;'>{icon}</div>
                                <h4 style='color: #667eea; margin: 0.5rem 0;'>{label}</h4>
                                <p style='font-size: 2rem; font-weight: 700; color: #2d3748;'>{value}/10</p>
                            </div>
                        """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.info(f"**💭 Expert Opinion:** {card.get('reason', 'No specific reason provided.')}")
        else:
            st.warning("⚠️ Expert AI Scorecard unavailable. Please check your Ollama connection.")

        # --- SECTION ANALYSIS ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📑 Deep Section Analysis")
        
        col_a, col_b = st.columns(2)

        with col_a:
            m_rev = review_results.get("methodology_review")
            if m_rev:
                st.markdown("""
                    <div class="metric-card">
                        <h3 style='color: #667eea;'>🛠 Methodology Review</h3>
                """, unsafe_allow_html=True)
                st.write(f"**Summary:** {m_rev.get('summary', 'N/A')}")
                score_m = m_rev.get('score', '-')
                st.metric("Section Quality", f"{score_m}/10")
                if m_rev.get("weaknesses"):
                    st.markdown("**⚠️ Areas of Concern:**")
                    for w in m_rev.get("weaknesses", []):
                        st.markdown(f"- {w}")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No methodology analysis available")

        with col_b:
            r_rev = review_results.get("results_review")
            if r_rev:
                st.markdown("""
                    <div class="metric-card">
                        <h3 style='color: #667eea;'>📈 Results Review</h3>
                """, unsafe_allow_html=True)
                st.write(f"**Summary:** {r_rev.get('summary', 'N/A')}")
                score_r = r_rev.get('score', '-')
                st.metric("Section Quality", f"{score_r}/10")
                if r_rev.get("weaknesses"):
                    st.markdown("**⚠️ Areas of Concern:**")
                    for w in r_rev.get("weaknesses", []):
                        st.markdown(f"- {w}")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No results analysis available")

        # --- DETAILED FEEDBACK ---
        st.markdown("---")
        st.markdown("## 📋 Detailed Feedback Insights")

        orig_strengths = review_results.get("strengths", [])
        orig_weaknesses = review_results.get("weaknesses", [])
        orig_improvements = review_results.get("improvements", [])

        rewritten_strengths = review_results.get("rewritten_strengths", orig_strengths)
        rewritten_weaknesses = review_results.get("rewritten_weaknesses", orig_weaknesses)
        rewritten_improvements = review_results.get("rewritten_improvements", orig_improvements)

        tab1, tab2, tab3 = st.tabs(["✅ Strengths", "❌ Weaknesses", "💡 Improvements"])

        with tab1:
            s_tab1, s_tab2 = st.tabs(["📝 Original", "🤖 AI-Enhanced"])
            with s_tab1:
                if orig_strengths:
                    for i, s in enumerate(orig_strengths, 1):
                        st.markdown(f"""
                            <div class='feedback-item' style='border-left-color:#10b981;'>
                                <strong style='color:#10b981; font-size: 1.1rem;'>✓ Strength {i}</strong>
                                <p style='margin: 0.5rem 0 0 0; color: #2d3748;'>{s}</p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No strengths detected in the analysis.")
            
            with s_tab2:
                if rewritten_strengths:
                    for i, s in enumerate(rewritten_strengths, 1):
                        st.markdown(f"""
                            <div class='feedback-item' style='border-left-color:#065f46; background: linear-gradient(90deg, #ecfdf5 0%, white 100%);'>
                                <strong style='color:#065f46; font-size: 1.1rem;'>🤖 AI Enhanced {i}</strong>
                                <p style='margin: 0.5rem 0 0 0; color: #2d3748;'>{s}</p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No AI-enhanced strengths available.")

        with tab2:
            w_tab1, w_tab2 = st.tabs(["📝 Original", "🤖 AI-Enhanced"])
            with w_tab1:
                if orig_weaknesses:
                    for i, w in enumerate(orig_weaknesses, 1):
                        st.markdown(f"""
                            <div class='feedback-item' style='border-left-color:#ef4444;'>
                                <strong style='color:#ef4444; font-size: 1.1rem;'>⚠ Weakness {i}</strong>
                                <p style='margin: 0.5rem 0 0 0; color: #2d3748;'>{w}</p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No weaknesses detected in the analysis.")
            
            with w_tab2:
                if rewritten_weaknesses:
                    for i, w in enumerate(rewritten_weaknesses, 1):
                        st.markdown(f"""
                            <div class='feedback-item' style='border-left-color:#b91c1c; background: linear-gradient(90deg, #fef2f2 0%, white 100%);'>
                                <strong style='color:#b91c1c; font-size: 1.1rem;'>🤖 AI Enhanced {i}</strong>
                                <p style='margin: 0.5rem 0 0 0; color: #2d3748;'>{w}</p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No AI-enhanced weaknesses available.")

        with tab3:
            m_tab1, m_tab2 = st.tabs(["📝 Original", "🤖 AI-Enhanced"])
            with m_tab1:
                if orig_improvements:
                    for i, m in enumerate(orig_improvements, 1):
                        st.markdown(f"""
                            <div class='feedback-item' style='border-left-color:#f59e0b;'>
                                <strong style='color:#f59e0b; font-size: 1.1rem;'>💡 Suggestion {i}</strong>
                                <p style='margin: 0.5rem 0 0 0; color: #2d3748;'>{m}</p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No improvement suggestions detected.")
            
            with m_tab2:
                if rewritten_improvements:
                    for i, m in enumerate(rewritten_improvements, 1):
                        st.markdown(f"""
                            <div class='feedback-item' style='border-left-color:#92400e; background: linear-gradient(90deg, #fffbeb 0%, white 100%);'>
                                <strong style='color:#92400e; font-size: 1.1rem;'>🤖 AI Enhanced {i}</strong>
                                <p style='margin: 0.5rem 0 0 0; color: #2d3748;'>{m}</p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No AI-enhanced improvements available.")

        # --- EXPORT SECTION ---
        st.markdown("---")
        st.markdown("## 💾 Export Your Analysis")

        def build_text_report(filename_label, strengths_list, weaknesses_list, improvements_list, verdict_label, confidence_val, score_val, v2_data=None):
            tz = time.strftime("%Y-%m-%d %H:%M:%S")
            report_text = f"""
╔═══════════════════════════════════════════════════════════════════╗
║                PAPERLENS ANALYSIS REPORT                          ║
╚═══════════════════════════════════════════════════════════════════╝

FILE: {filename_label}
VERDICT: {verdict_label}
CONFIDENCE: {confidence_val}%
QUALITY SCORE: {score_val}
TIMESTAMP: {tz}

"""
            if v2_data:
                report_text += f"""
{'='*70}
EXPERT AI ASSESSMENT
{'='*70}
Recommendation: {v2_data.get('recommendation', 'N/A')}
Originality Score: {v2_data.get('originality', 'N/A')}/10
Methodology Score: {v2_data.get('methodology', 'N/A')}/10
Clarity Score: {v2_data.get('clarity', 'N/A')}/10

Reasoning: {v2_data.get('reason', 'N/A')}

"""

            report_text += f"""
{'='*70}
STRENGTHS IDENTIFIED ({len(strengths_list)})
{'='*70}
"""
            report_text += "\n".join([f"{i+1}. {s}" for i, s in enumerate(strengths_list)])
            
            report_text += f"""

{'='*70}
WEAKNESSES IDENTIFIED ({len(weaknesses_list)})
{'='*70}
"""
            report_text += "\n".join([f"{i+1}. {w}" for i, w in enumerate(weaknesses_list)])
            
            report_text += f"""

{'='*70}
IMPROVEMENT SUGGESTIONS ({len(improvements_list)})
{'='*70}
"""
            report_text += "\n".join([f"{i+1}. {m}" for i, m in enumerate(improvements_list)])
            
            report_text += f"""

{'='*70}
Generated by PaperLens v3.0 - AI Research Paper Reviewer
https://paperlens.ai
{'='*70}
"""
            return report_text

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📝 Original Analysis")
            orig_report = build_text_report(
                uploaded_file.name, orig_strengths, orig_weaknesses, 
                orig_improvements, verdict, confidence, raw_score, card
            )
            st.download_button(
                "📄 Download Text Report",
                data=orig_report,
                file_name=f"paperlens_original_{uploaded_file.name}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            csv_orig = pd.DataFrame({
                "Category": (["Strength"] * len(orig_strengths)) + 
                           (["Weakness"] * len(orig_weaknesses)) + 
                           (["Improvement"] * len(orig_improvements)),
                "Feedback": orig_strengths + orig_weaknesses + orig_improvements,
                "Source": ["Original"] * (len(orig_strengths) + len(orig_weaknesses) + len(orig_improvements))
            })
            st.download_button(
                "📊 Download CSV Report",
                data=csv_orig.to_csv(index=False),
                file_name=f"paperlens_original_{uploaded_file.name}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            st.markdown("### 🤖 AI-Enhanced Analysis")
            rew_report = build_text_report(
                uploaded_file.name, rewritten_strengths, rewritten_weaknesses, 
                rewritten_improvements, verdict, confidence, raw_score, card
            )
            st.download_button(
                "📄 Download Text Report",
                data=rew_report,
                file_name=f"paperlens_ai_enhanced_{uploaded_file.name}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            csv_rew = pd.DataFrame({
                "Category": (["Strength"] * len(rewritten_strengths)) + 
                           (["Weakness"] * len(rewritten_weaknesses)) + 
                           (["Improvement"] * len(rewritten_improvements)),
                "Feedback": rewritten_strengths + rewritten_weaknesses + rewritten_improvements,
                "Source": ["AI-Enhanced"] * (len(rewritten_strengths) + len(rewritten_weaknesses) + len(rewritten_improvements))
            })
            st.download_button(
                "📊 Download CSV Report",
                data=csv_rew.to_csv(index=False),
                file_name=f"paperlens_ai_enhanced_{uploaded_file.name}.csv",
                mime="text/csv",
                use_container_width=True
            )

        # Success message
        st.success("✅ Analysis complete! Your reports are ready for download.")

    except Exception as e:
        st.error(f"❌ An error occurred during analysis")
        with st.expander("🔍 View Error Details"):
            st.exception(e)

    finally:
        try:
            os.remove(pdf_path)
        except Exception:
            pass

else:
    # --- WELCOME SCREEN ---
    st.markdown("""
        <div class="info-box animated-card">
            <h3>👋 Welcome to PaperLens!</h3>
            <p style='font-size: 1.1rem; line-height: 1.6;'>
                Transform your research paper review process with our cutting-edge AI analysis system. 
                Upload your PDF and receive comprehensive, actionable feedback in seconds.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 What You'll Get")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <h4 style='color: #667eea;'>✅ Comprehensive Strengths Analysis</h4>
                <p>Identify what makes your paper stand out</p>
                <ul>
                    <li>Novel contributions detection</li>
                    <li>Methodological excellence</li>
                    <li>Clear presentation highlights</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="metric-card">
                <h4 style='color: #667eea;'>💡 Actionable Improvements</h4>
                <p>Specific suggestions to enhance quality</p>
                <ul>
                    <li>Structure optimization</li>
                    <li>Clarity enhancements</li>
                    <li>Impact maximization</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <h4 style='color: #667eea;'>❌ Critical Weakness Detection</h4>
                <p>Uncover potential issues before submission</p>
                <ul>
                    <li>Methodology gaps</li>
                    <li>Logic inconsistencies</li>
                    <li>Missing components</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="metric-card">
                <h4 style='color: #667eea;'>📊 Quantified Quality Metrics</h4>
                <p>Data-driven assessment scores</p>
                <ul>
                    <li>Confidence levels</li>
                    <li>Plagiarism detection</li>
                    <li>Originality scoring</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🚀 How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style='text-align: center; padding: 2rem; background: white; border-radius: 15px; box-shadow: 0 3px 10px rgba(0,0,0,0.08);'>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>📤</div>
                <h4 style='color: #667eea;'>1. Upload</h4>
                <p>Simply drag and drop your research paper PDF</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style='text-align: center; padding: 2rem; background: white; border-radius: 15px; box-shadow: 0 3px 10px rgba(0,0,0,0.08);'>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>🔬</div>
                <h4 style='color: #667eea;'>2. Analyze</h4>
                <p>Our AI performs multi-layer deep analysis</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style='text-align: center; padding: 2rem; background: white; border-radius: 15px; box-shadow: 0 3px 10px rgba(0,0,0,0.08);'>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>📥</div>
                <h4 style='color: #667eea;'>3. Export</h4>
                <p>Download detailed reports in multiple formats</p>
            </div>
        """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h4 style='color: #667eea;'>Built with ❤️ for Researchers</h4>
        <p style='color: #64748b; font-size: 1rem;'>
            PaperLens v3.0 | Powered by Advanced AI & Ollama<br>
            Making research review intelligent, fast, and comprehensive
        </p>
        <div style='margin-top: 1rem;'>
            <span style='margin: 0 0.5rem; color: #667eea;'>📧 Contact</span>
            <span style='margin: 0 0.5rem; color: #667eea;'>📖 Docs</span>
            <span style='margin: 0 0.5rem; color: #667eea;'>💬 Support</span>
        </div>
    </div>
""", unsafe_allow_html=True)