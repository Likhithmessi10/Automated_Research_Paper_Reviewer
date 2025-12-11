# frontend.py
import streamlit as st
import pandas as pd
import os
import tempfile
import plotly.graph_objects as go
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
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS FOR MODERN STYLING ---
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding-top: 2rem;
    }
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 { color: white; font-size: 3rem; font-weight: 700; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .main-header p { color: rgba(255,255,255,0.95); font-size: 1.1rem; margin-top: 0.5rem; }
    .metric-card { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #667eea; transition: transform 0.2s; }
    .metric-card:hover { transform: translateY(-5px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
    .upload-section { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 2rem; border-radius: 15px; text-align: center; margin: 2rem 0; }
    .info-box { background: #e8f4f8; border-left: 4px solid #3498db; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
    .feedback-item { padding: 1rem; margin: 0.5rem 0; border-radius: 10px; border-left: 4px solid; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stProgress > div > div > div > div { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); }
    .stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.75rem 2rem; border-radius: 25px; font-weight: 600; transition: all 0.3s; }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("""
    <div class="main-header">
        <h1>📝 PaperLens</h1>
        <p>Advanced AI-Powered Research Paper Analysis & Review System</p>
    </div>
""", unsafe_allow_html=True)

# --- Controls in sidebar ---
with st.sidebar:
    st.header("AI Options")
    rewrite_toggle = st.checkbox("Rewrite insights with Ollama (recommended)", value=True)
    model_choice = st.selectbox(
        "Ollama model (local)",
        options=["llama3.1:8b", "mistral:7b", "phi3", "llama3:latest"],
        index=0,
        help="Choose a locally installed Ollama model for rewriting."
    )
    st.markdown("---")
    st.markdown("⚙️ Advanced")
    auto_reject_thresh = st.slider("Auto-reject plagiarism threshold (%)", 0, 100, 40)
    st.caption("If plagiarism % > threshold then final verdict becomes REJECT (plagiarism).")

# --- FEATURE HIGHLIGHTS ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("**🎯 Instant Analysis**")
    st.caption("Get results in seconds")
with col2:
    st.markdown("**🔍 Deep Insights**")
    st.caption("Comprehensive evaluation")
with col3:
    st.markdown("**📊 Clear Metrics**")
    st.caption("Quantified assessments")
with col4:
    st.markdown("**💡 Actionable Tips**")
    st.caption("Improvement suggestions")

st.markdown("<br>", unsafe_allow_html=True)

# --- FILE UPLOAD SECTION ---
st.markdown("""
    <div class="upload-section">
        <h3>🚀 Upload Your Research Paper</h3>
        <p>Drop your PDF file below to begin the intelligent review process</p>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type="pdf",
    help="Supported format: PDF | Max file size: 200MB",
    label_visibility="collapsed"
)

if uploaded_file is not None:
    # File meta
    file_details = st.expander("📄 File Details", expanded=False)
    with file_details:
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Filename:** {uploaded_file.name}")
            st.write(f"**File size:** {uploaded_file.size / 1024:.2f} KB")
        with c2:
            st.write(f"**File type:** {uploaded_file.type}")

    # Progress UI
    progress_bar = st.progress(0)
    status_text = st.empty()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        pdf_path = tmp_file.name

    try:
        status_text.text("🔍 Extracting content...")
        progress_bar.progress(20)
        time.sleep(0.2)

        status_text.text("🧠 Analyzing with heuristic patterns...")
        progress_bar.progress(45)
        time.sleep(0.2)

        # Run the review logic (pass rewrite flag & model choice)
        status_text.text("🤖 Running AI rewriting (if enabled)...")
        progress_bar.progress(65)
        with st.spinner("Processing paper (this may take a few seconds)..."):
            review_results = review_pdf(pdf_path, rewrite=rewrite_toggle, ollama_model=model_choice)

        status_text.text("✅ Analysis complete!")
        progress_bar.progress(100)
        time.sleep(0.3)
        progress_bar.empty()
        status_text.empty()

        # --- RESULTS DASHBOARD ---
        st.markdown("---")
        st.markdown("## 📊 Analysis Results")

        # Top metrics row: Verdict | Confidence | Score | Insights
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        # Verdict panel
        with col1:
            verdict = review_results.get("verdict", "REVIEW FAILED")
            if "ACCEPT" in verdict:
                verdict_color = "#10b981"
                verdict_emoji = "✅"
                verdict_bg = "#d1fae5"
            elif "WEAK" in verdict:
                verdict_color = "#f59e0b"
                verdict_emoji = "⚠️"
                verdict_bg = "#fef3c7"
            else:
                verdict_color = "#ef4444"
                verdict_emoji = "❌"
                verdict_bg = "#fee2e2"

            st.markdown(f"""
                <div style='
                    padding: 2rem;
                    border-radius: 15px;
                    background: {verdict_bg};
                    border: 2px solid {verdict_color};
                    text-align: center;
                '>
                    <div style='font-size: 3rem;'>{verdict_emoji}</div>
                    <h2 style='color: {verdict_color}; margin: 0.5rem 0;'>{verdict}</h2>
                    <p style='color: #6b7280; margin: 0;'>Final Decision</p>
                </div>
            """, unsafe_allow_html=True)

        # Confidence
        with col2:
            confidence = round(review_results.get("confidence", 0.0) * 100)
            st.metric(label="🎯 Confidence", value=f"{confidence}%", delta=f"{confidence - 50}%" if confidence > 50 else None)

        # Score
        with col3:
            raw_score = round(review_results.get("final_score", 0.0), 2)
            st.metric(label="📈 Score", value=f"{raw_score}", delta=f"+{raw_score}" if raw_score > 0 else None)

        # Insights count
        with col4:
            total_feedback = (
                len(review_results.get("strengths", [])) +
                len(review_results.get("weaknesses", [])) +
                len(review_results.get("improvements", []))
            )
            st.metric(label="💬 Insights", value=total_feedback)

        # --- Plagiarism row (full width) ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🧬 Plagiarism Analysis")
        plag = review_results.get("plagiarism_percent", 0)
        orig = review_results.get("originality_percent", max(0, 100 - int(plag)))
        risk = review_results.get("plagiarism_risk", "UNAVAILABLE")

        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            st.metric("Plagiarism", f"{plag}%")
        with c2:
            st.metric("Originality", f"{orig}%")
        with c3:
            if isinstance(risk, str):
                risk_u = risk.upper()
            else:
                risk_u = str(risk).upper()
            if risk_u == "LOW":
                st.success("🟢 Low Plagiarism Risk")
            elif risk_u == "MEDIUM":
                st.warning("🟡 Medium Plagiarism Risk")
            elif risk_u == "HIGH":
                st.error("🔴 High Plagiarism Risk")
            else:
                st.info(f"⚪ Plagiarism Check: {risk_u}")

        # --- SCORE VISUALIZATION ---
        st.markdown("<br>", unsafe_allow_html=True)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=confidence,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Confidence Level", 'font': {'size': 20}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': verdict_color},
                'steps': [
                    {'range': [0, 33], 'color': '#fee2e2'},
                    {'range': [33, 66], 'color': '#fef3c7'},
                    {'range': [66, 100], 'color': '#d1fae5'}
                ],
            }
        ))
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

        # --- DETAILED FEEDBACK (Side-by-side Original vs Rewritten) ---
        st.markdown("---")
        st.markdown("## 📋 Detailed Feedback (Original vs AI-Rewritten)")

        # Prepare lists from results (safe defaults)
        orig_strengths = review_results.get("strengths", [])
        orig_weaknesses = review_results.get("weaknesses", [])
        orig_improvements = review_results.get("improvements", [])

        rewritten_strengths = review_results.get("rewritten_strengths", orig_strengths)
        rewritten_weaknesses = review_results.get("rewritten_weaknesses", orig_weaknesses)
        rewritten_improvements = review_results.get("rewritten_improvements", orig_improvements)

        # For each category we create tabs with two sub-tabs: Original / Rewritten
        tab1, tab2, tab3 = st.tabs(["✅ Strengths", "❌ Weaknesses", "💡 Improvements"])

        # Strengths tab
        with tab1:
            st.markdown(f"**Found {len(orig_strengths)} strength sentences.**")
            s_tab1, s_tab2 = st.tabs(["Original Extracted", "AI-Rewritten"])
            with s_tab1:
                if orig_strengths:
                    for i, s in enumerate(orig_strengths, 1):
                        st.markdown(f"<div class='feedback-item' style='border-left-color:#10b981;'>"
                                    f"<strong style='color:#10b981;'>Orig {i}.</strong> {s}</div>", unsafe_allow_html=True)
                else:
                    st.info("No strengths detected.")
            with s_tab2:
                if rewritten_strengths:
                    for i, s in enumerate(rewritten_strengths, 1):
                        st.markdown(f"<div class='feedback-item' style='border-left-color:#065f46;'>"
                                    f"<strong style='color:#065f46;'>AI {i}.</strong> {s}</div>", unsafe_allow_html=True)
                else:
                    st.info("No rewritten strengths available.")

        # Weaknesses tab
        with tab2:
            st.markdown(f"**Found {len(orig_weaknesses)} weakness sentences.**")
            w_tab1, w_tab2 = st.tabs(["Original Extracted", "AI-Rewritten"])
            with w_tab1:
                if orig_weaknesses:
                    for i, w in enumerate(orig_weaknesses, 1):
                        st.markdown(f"<div class='feedback-item' style='border-left-color:#ef4444;'>"
                                    f"<strong style='color:#ef4444;'>Orig {i}.</strong> {w}</div>", unsafe_allow_html=True)
                else:
                    st.info("No weaknesses detected.")
            with w_tab2:
                if rewritten_weaknesses:
                    for i, w in enumerate(rewritten_weaknesses, 1):
                        st.markdown(f"<div class='feedback-item' style='border-left-color:#b91c1c;'>"
                                    f"<strong style='color:#b91c1c;'>AI {i}.</strong> {w}</div>", unsafe_allow_html=True)
                else:
                    st.info("No rewritten weaknesses available.")

        # Improvements tab
        with tab3:
            st.markdown(f"**Found {len(orig_improvements)} improvement suggestions.**")
            m_tab1, m_tab2 = st.tabs(["Original Extracted", "AI-Rewritten"])
            with m_tab1:
                if orig_improvements:
                    for i, m in enumerate(orig_improvements, 1):
                        st.markdown(f"<div class='feedback-item' style='border-left-color:#f59e0b;'>"
                                    f"<strong style='color:#f59e0b;'>Orig {i}.</strong> {m}</div>", unsafe_allow_html=True)
                else:
                    st.info("No improvements detected.")
            with m_tab2:
                if rewritten_improvements:
                    for i, m in enumerate(rewritten_improvements, 1):
                        st.markdown(f"<div class='feedback-item' style='border-left-color:#92400e;'>"
                                    f"<strong style='color:#92400e;'>AI {i}.</strong> {m}</div>", unsafe_allow_html=True)
                else:
                    st.info("No rewritten improvements available.")

        # --- EXPORT OPTIONS (Original & Rewritten) ---
        st.markdown("---")
        st.markdown("## 💾 Export Results")

        # Build text reports
        def build_text_report(filename_label, strengths_list, weaknesses_list, improvements_list, verdict_label, confidence_val, score_val):
            tz = time.strftime("%Y-%m-%d %H:%M:%S")
            report_text = f"PAPERLENS ANALYSIS REPORT\n{'='*60}\n\n"
            report_text += f"FILE: {filename_label}\nVERDICT: {verdict_label}\nCONFIDENCE: {confidence_val}%\nRAW SCORE: {score_val}\nTIMESTAMP: {tz}\n\n"
            report_text += f"STRENGTHS ({len(strengths_list)}):\n"
            report_text += "\n".join([f"{i+1}. {s}" for i, s in enumerate(strengths_list)]) + "\n\n"
            report_text += f"WEAKNESSES ({len(weaknesses_list)}):\n"
            report_text += "\n".join([f"{i+1}. {w}" for i, w in enumerate(weaknesses_list)]) + "\n\n"
            report_text += f"IMPROVEMENTS ({len(improvements_list)}):\n"
            report_text += "\n".join([f"{i+1}. {m}" for i, m in enumerate(improvements_list)]) + "\n\n"
            report_text += "="*60 + "\nGenerated by PaperLens\n"
            return report_text

        left_col, right_col = st.columns(2)
        with left_col:
            # Download original text report
            orig_report = build_text_report(uploaded_file.name, orig_strengths, orig_weaknesses, orig_improvements, verdict, confidence, raw_score)
            st.download_button("📄 Download Original Text Report", data=orig_report, file_name=f"paperlens_original_{uploaded_file.name}.txt", mime="text/plain")
            # CSV of original
            csv_orig = pd.DataFrame({
                "Type": (["Strength"] * len(orig_strengths)) + (["Weakness"] * len(orig_weaknesses)) + (["Improvement"] * len(orig_improvements)),
                "Feedback": orig_strengths + orig_weaknesses + orig_improvements
            })
            st.download_button("📊 Download Original CSV", data=csv_orig.to_csv(index=False), file_name=f"paperlens_original_{uploaded_file.name}.csv", mime="text/csv")
        with right_col:
            # Download rewritten text report
            rew_report = build_text_report(uploaded_file.name, rewritten_strengths, rewritten_weaknesses, rewritten_improvements, verdict, confidence, raw_score)
            st.download_button("📄 Download AI-Rewritten Text Report", data=rew_report, file_name=f"paperlens_rewritten_{uploaded_file.name}.txt", mime="text/plain")
            # CSV of rewritten
            csv_rew = pd.DataFrame({
                "Type": (["Strength"] * len(rewritten_strengths)) + (["Weakness"] * len(rewritten_weaknesses)) + (["Improvement"] * len(rewritten_improvements)),
                "Feedback": rewritten_strengths + rewritten_weaknesses + rewritten_improvements
            })
            st.download_button("📊 Download AI-Rewritten CSV", data=csv_rew.to_csv(index=False), file_name=f"paperlens_rewritten_{uploaded_file.name}.csv", mime="text/csv")

    except Exception as e:
        st.error(f"❌ An error occurred during analysis: {e}")
        st.exception(e)

    finally:
        try:
            os.remove(pdf_path)
        except Exception:
            pass

else:
    # --- INITIAL STATE ---
    st.markdown("""
        <div class="info-box">
            <h4>👋 Welcome to PaperLens!</h4>
            <p>Get started by uploading a research paper PDF above. Our AI-powered system will analyze your paper and provide:</p>
            <ul>
                <li>✅ Comprehensive strength identification</li>
                <li>❌ Potential weakness detection</li>
                <li>💡 Actionable improvement suggestions</li>
                <li>📊 Quantified confidence metrics</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📚 How It Works")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**1️⃣ Upload**\n\nSelect your research paper PDF from your device")
    with c2:
        st.markdown("**2️⃣ Analyze**\n\nOur system reviews the content using advanced heuristics")
    with c3:
        st.markdown("**3️⃣ Review**\n\nGet detailed feedback and export your results")

# --- FOOTER ---
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #6b7280; padding: 2rem 0;'>
        <p>Built with ❤️ using Streamlit | PaperLens v3.0</p>
        <p style='font-size: 0.9rem;'>Powered by heuristic analysis patterns and Ollama for content polishing</p>
    </div>
""", unsafe_allow_html=True)
