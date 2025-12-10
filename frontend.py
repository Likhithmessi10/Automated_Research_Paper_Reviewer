import streamlit as st
import pandas as pd
import os
import tempfile
import plotly.graph_objects as go

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
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.95);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Upload section */
    .upload-section {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
    }
    
    /* Info boxes */
    .info-box {
        background: #e8f4f8;
        border-left: 4px solid #3498db;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Verdict badge */
    .verdict-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1.2rem;
        margin: 1rem 0;
    }
    
    /* Strength/Weakness items */
    .feedback-item {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
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
    # Display file info
    file_details = st.expander("📄 File Details", expanded=False)
    with file_details:
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Filename:** {uploaded_file.name}")
            st.write(f"**File size:** {uploaded_file.size / 1024:.2f} KB")
        with col2:
            st.write(f"**File type:** {uploaded_file.type}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Progress indicator
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Simulate analysis steps
    status_text.text("🔄 Uploading file...")
    progress_bar.progress(20)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        pdf_path = tmp_file.name

    try:
        status_text.text("🔍 Extracting content...")
        progress_bar.progress(40)
        
        status_text.text("🧠 Analyzing with heuristic patterns...")
        progress_bar.progress(60)
        
        # Run the review logic
        review_results = review_pdf(pdf_path)
        
        status_text.text("✅ Analysis complete!")
        progress_bar.progress(100)
        
        # Clear progress indicators
        import time
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        # --- RESULTS DASHBOARD ---
        st.markdown("---")
        st.markdown("## 📊 Analysis Results")
        
        # Top metrics row
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            verdict = review_results["verdict"]
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

        with col2:
            confidence = round(review_results["confidence"] * 100)
            st.metric(
                label="🎯 Confidence",
                value=f"{confidence}%",
                delta=f"{confidence - 50}%" if confidence > 50 else None
            )
        
        with col3:
            raw_score = round(review_results["final_score"], 2)
            st.metric(
                label="📈 Score",
                value=f"{raw_score}",
                delta=f"+{raw_score}" if raw_score > 0 else None
            )
            st.subheader("🧬 Plagiarism Analysis")

            plag = review_results["plagiarism_percent"]
            orig = review_results["originality_percent"]
            risk = review_results["plagiarism_risk"]

            st.metric("Plagiarism", f"{plag}%")
            st.metric("Originality", f"{orig}%")

            if risk == "LOW":
                st.success("🟢 Low Plagiarism Risk")
            elif risk == "MEDIUM":
                st.warning("🟡 Medium Plagiarism Risk")
            else:
                st.error("🔴 High Plagiarism Risk")
        
        with col4:
            total_feedback = (
                len(review_results["strengths"]) +
                len(review_results["weaknesses"]) +
                len(review_results["improvements"])
            )
            st.metric(
                label="💬 Insights",
                value=total_feedback
            )
        
        # --- SCORE VISUALIZATION ---
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Create gauge chart for confidence
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=confidence,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Confidence Level", 'font': {'size': 24}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
                'bar': {'color': verdict_color},
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
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font={'color': "darkgray", 'family': "Arial"}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # --- DETAILED FEEDBACK ---
        st.markdown("---")
        st.markdown("## 📋 Detailed Feedback")
        
        # Create tabs for different feedback types
        tab1, tab2, tab3 = st.tabs(["✅ Strengths", "❌ Weaknesses", "💡 Improvements"])
        
        with tab1:
            if review_results["strengths"]:
                st.markdown(f"**Found {len(review_results['strengths'])} strengths in your paper**")
                for idx, strength in enumerate(review_results["strengths"][:10], 1):
                    st.markdown(f"""
                        <div class="feedback-item" style="border-left-color: #10b981;">
                            <strong style="color: #10b981;">Strength {idx}</strong><br>
                            {strength}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No significant strengths detected based on heuristic patterns.")
        
        with tab2:
            if review_results["weaknesses"]:
                st.markdown(f"**Found {len(review_results['weaknesses'])} weaknesses to address**")
                for idx, weakness in enumerate(review_results["weaknesses"][:10], 1):
                    st.markdown(f"""
                        <div class="feedback-item" style="border-left-color: #ef4444;">
                            <strong style="color: #ef4444;">Weakness {idx}</strong><br>
                            {weakness}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No major weaknesses detected based on heuristic patterns.")
        
        with tab3:
            if review_results["improvements"]:
                st.markdown(f"**Found {len(review_results['improvements'])} improvement suggestions**")
                for idx, improvement in enumerate(review_results["improvements"][:10], 1):
                    st.markdown(f"""
                        <div class="feedback-item" style="border-left-color: #f59e0b;">
                            <strong style="color: #f59e0b;">Suggestion {idx}</strong><br>
                            {improvement}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No major improvements suggested based on heuristic patterns.")
        
        # --- SUMMARY STATISTICS ---
        st.markdown("---")
        st.markdown("## 📊 Summary Statistics")
        
        summary_data = {
            "Category": ["Strengths", "Weaknesses", "Improvements", "Total Insights"],
            "Count": [
                len(review_results["strengths"]),
                len(review_results["weaknesses"]),
                len(review_results["improvements"]),
                total_feedback
            ]
        }
        
        st.dataframe(
            pd.DataFrame(summary_data),
            use_container_width=True,
            hide_index=True
        )
        
        # --- TECHNICAL DETAILS ---
        with st.expander("🔬 Technical Details & Raw Data"):
            st.markdown("### Heuristic Patterns Used")
            
            pattern_info = pd.DataFrame({
                "Type": ["Strength Patterns", "Weakness Patterns", "Improvement Patterns"],
                "Count": [
                    len(STRENGTH_PATTERNS),
                    len(WEAKNESS_PATTERNS),
                    len(IMPROVEMENT_PATTERNS)
                ],
                "Examples": [
                    ", ".join(STRENGTH_PATTERNS[:3]) + "...",
                    ", ".join(WEAKNESS_PATTERNS[:3]) + "...",
                    ", ".join(IMPROVEMENT_PATTERNS[:3]) + "..."
                ]
            })
            
            st.dataframe(pattern_info, use_container_width=True, hide_index=True)
            
            st.markdown("### Raw Report Output")
            st.code(review_results["report"], language='text')
        
        # --- EXPORT OPTIONS ---
        st.markdown("---")
        st.markdown("## 💾 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Create downloadable report
            report_text = f"""
PAPERLENS ANALYSIS REPORT
{'='*50}

FILE: {uploaded_file.name}
VERDICT: {verdict}
CONFIDENCE: {confidence}%
RAW SCORE: {raw_score}

STRENGTHS ({len(review_results["strengths"])}):
{chr(10).join(f"{i}. {s}" for i, s in enumerate(review_results["strengths"], 1))}

WEAKNESSES ({len(review_results["weaknesses"])}):
{chr(10).join(f"{i}. {w}" for i, w in enumerate(review_results["weaknesses"], 1))}

IMPROVEMENTS ({len(review_results["improvements"])}):
{chr(10).join(f"{i}. {imp}" for i, imp in enumerate(review_results["improvements"], 1))}

{'='*50}
Generated by PaperLens
"""
            
            st.download_button(
                label="📄 Download Text Report",
                data=report_text,
                file_name=f"paperlens_report_{uploaded_file.name}.txt",
                mime="text/plain"
            )
        
        with col2:
            # Create CSV export
            csv_data = pd.DataFrame({
                "Type": (
                    ["Strength"] * len(review_results["strengths"]) +
                    ["Weakness"] * len(review_results["weaknesses"]) +
                    ["Improvement"] * len(review_results["improvements"])
                ),
                "Feedback": (
                    review_results["strengths"] +
                    review_results["weaknesses"] +
                    review_results["improvements"]
                )
            })
            
            st.download_button(
                label="📊 Download CSV Data",
                data=csv_data.to_csv(index=False),
                file_name=f"paperlens_data_{uploaded_file.name}.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"❌ An error occurred during analysis: {e}")
        st.exception(e)
    
    finally:
        os.remove(pdf_path)

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
    
    # Sample papers section
    st.markdown("### 📚 How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            **1️⃣ Upload**
            
            Select your research paper PDF from your device
        """)
    
    with col2:
        st.markdown("""
            **2️⃣ Analyze**
            
            Our system reviews the content using advanced heuristics
        """)
    
    with col3:
        st.markdown("""
            **3️⃣ Review**
            
            Get detailed feedback and export your results
        """)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #6b7280; padding: 2rem 0;'>
        <p>Built with ❤️ using Streamlit | PaperLens v2.0</p>
        <p style='font-size: 0.9rem;'>Powered by heuristic analysis patterns for research paper evaluation</p>
    </div>
""", unsafe_allow_html=True)