import streamlit as st
import pandas as pd
import json
import os
import time
from match_engine import evaluate_bidder_against_rules

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Tender IQ Evaluator",
    layout="wide",
    page_icon="⚖️",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
    }
    
    /* Leaderboard styling */
    .leaderboard-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    .leaderboard-header h2 {
        margin: 0;
        color: #1e293b;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .badge-pass {
        background: #dcfce7;
        color: #166534;
    }
    
    .badge-fail {
        background: #fee2e2;
        color: #991b1b;
    }
    
    .badge-flagged {
        background: #fef3c7;
        color: #92400e;
    }
    
    /* Rule card styling */
    .rule-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
    }
    
    .rule-card-pass {
        border-left-color: #22c55e;
        background: linear-gradient(90deg, rgba(34,197,94,0.05) 0%, white 100%);
    }
    
    .rule-card-fail {
        border-left-color: #ef4444;
        background: linear-gradient(90deg, rgba(239,68,68,0.05) 0%, white 100%);
    }
    
    .rule-card-flagged {
        border-left-color: #f59e0b;
        background: linear-gradient(90deg, rgba(245,158,11,0.05) 0%, white 100%);
    }
    
    .rule-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.75rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .score-pill {
        background: #f1f5f9;
        padding: 0.25rem 0.75rem;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 700;
        color: #475569;
    }
    
    .rule-detail {
        margin-bottom: 0.75rem;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .rule-detail:last-child {
        border-bottom: none;
        margin-bottom: 0;
    }
    
    .rule-detail-label {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 0.25rem;
    }
    
    .rule-detail-value {
        color: #334155;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .evidence-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 0.75rem;
    }
    
    .evidence-box p {
        margin: 0;
        color: #1e40af;
        font-style: italic;
    }
    
    /* Demo banner */
    .demo-banner {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #fbbf24;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .demo-banner-icon {
        font-size: 2rem;
    }
    
    .demo-banner-text {
        flex: 1;
    }
    
    .demo-banner-title {
        font-weight: 600;
        color: #92400e;
        margin-bottom: 0.25rem;
    }
    
    .demo-banner-desc {
        color: #a16207;
        font-size: 0.9rem;
    }
    
    /* Section divider */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 2.5rem 0;
    }
    
    /* Bidder tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #f8fafc;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Progress indicator */
    .progress-ring {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #f8fafc;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Button enhancements */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border-radius: 12px;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>⚖️ Tender IQ</h1>
    <p>AI-Powered Procurement Evaluation • Automated Compliance Scoring • Multi-Bidder Ranking</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR: Document Uploads ---
with st.sidebar:
    st.markdown("### 📁 Document Upload")
    st.markdown("---")
    
    st.markdown("**Step 1: Tender Document**")
    tender_file = st.file_uploader(
        "Upload the tender/RFP with requirements",
        type="pdf",
        key="tender",
        help="Upload the official tender document containing all mandatory specifications"
    )
    
    if tender_file:
        st.success(f"✓ {tender_file.name}", icon="📋")
    
    st.markdown("")
    st.markdown("**Step 2: Bidder Submissions**")
    
    if 'bidder_list' not in st.session_state:
        st.session_state['bidder_list'] = []

    new_bidders = st.file_uploader(
        "Upload one or more bid proposals",
        type="pdf",
        accept_multiple_files=True,
        key="bidders",
        help="Upload PDF submissions from bidders to evaluate against tender requirements"
    )

    if new_bidders:
        for file in new_bidders:
            if file.name not in [f.name for f in st.session_state['bidder_list']]:
                st.session_state['bidder_list'].append(file)

    if st.session_state['bidder_list']:
        st.markdown("")
        st.markdown(f"**📄 {len(st.session_state['bidder_list'])} Bidder(s) Ready:**")
        
        for f in st.session_state['bidder_list']:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.caption(f"• {f.name}")
        
        st.markdown("")
        if st.button("🗑️ Clear All Bidders", use_container_width=True):
            st.session_state['bidder_list'] = []
            st.rerun()

    # --- ACTION BUTTON ---
    st.markdown("---")
    
    if tender_file and len(st.session_state['bidder_list']) > 0:
        with open("temp_tender.pdf", "wb") as f:
            f.write(tender_file.getbuffer())
        
        st.markdown("### 🚀 Ready to Evaluate")
        st.info(f"**{len(st.session_state['bidder_list'])}** bidder(s) will be evaluated against the tender requirements.", icon="✅")
        
        if st.button("▶️ Run Evaluation", type="primary", use_container_width=True):
            all_bidders_data = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, b_file in enumerate(st.session_state['bidder_list']):
                bidder_name = b_file.name
                temp_bid_path = f"temp_bid_{idx}.pdf"
                with open(temp_bid_path, "wb") as f:
                    f.write(b_file.getbuffer())
                
                progress = (idx + 1) / len(st.session_state['bidder_list'])
                progress_bar.progress(progress)
                status_text.text(f"Analyzing {bidder_name}...")
                
                result_str = evaluate_bidder_against_rules("temp_tender.pdf", temp_bid_path)
                try:
                    eval_results = json.loads(result_str).get('evaluation_results', [])
                except json.JSONDecodeError:
                    st.error("AI returned malformed data. Please try again.")
                    eval_results = []
                
                time.sleep(2)
                if os.path.exists(temp_bid_path):
                    os.remove(temp_bid_path)
                
                total_score = sum(r.get('score', 0) for r in eval_results)
                total_rules = len(eval_results)
                max_score = total_rules * 5
                
                all_bidders_data.append({
                    "Bidder": bidder_name,
                    "Total Rules": total_rules,
                    "Total Score": f"{total_score} / {max_score}",
                    "Raw Score": total_score,
                    "Max Score": max_score,
                    "Details": eval_results
                })
            
            progress_bar.empty()
            status_text.empty()
            
            if os.path.exists("temp_tender.pdf"):
                os.remove("temp_tender.pdf")
            
            st.session_state['leaderboard'] = sorted(all_bidders_data, key=lambda x: x["Raw Score"], reverse=True)
            st.session_state['is_demo'] = False
            st.rerun()
    
    # --- DEMO SECTION ---
    st.markdown("---")
    st.markdown("### 🧪 Try the Demo")
    st.caption("No files? See the AI in action with sample documents.")
    
    if st.button("🎯 One-Click Demo", use_container_width=True):
        if not os.path.exists("sample_tender.pdf") or not os.path.exists("sample_bid.pdf"):
            st.error("Demo files missing! Add 'sample_tender.pdf' and 'sample_bid.pdf' to your project.")
        else:
            with st.spinner("Running AI evaluation..."):
                result_str = evaluate_bidder_against_rules("sample_tender.pdf", "sample_bid.pdf")
                try:
                    eval_results = json.loads(result_str).get('evaluation_results', [])
                    if not eval_results:
                        st.warning("No rules found. The PDF might be empty or too large.")
                except json.JSONDecodeError:
                    st.error("AI returned malformed data. The API might have timed out.")
                    eval_results = []
                
                total_score = sum(r.get('score', 0) for r in eval_results)
                total_rules = len(eval_results)
                max_score = total_rules * 5 if total_rules > 0 else 0
                
                st.session_state['leaderboard'] = [{
                    "Bidder": "sample_bid.pdf",
                    "Total Rules": total_rules,
                    "Total Score": f"{total_score} / {max_score}",
                    "Raw Score": total_score,
                    "Max Score": max_score,
                    "Details": eval_results
                }]
                st.session_state['is_demo'] = True
                st.rerun()

# --- MAIN DASHBOARD ---
if 'leaderboard' in st.session_state and len(st.session_state['leaderboard']) > 0:
    
    # --- DEMO BANNER ---
    if st.session_state.get('is_demo', False):
        st.markdown("""
        <div class="demo-banner">
            <div class="demo-banner-icon">🔬</div>
            <div class="demo-banner-text">
                <div class="demo-banner-title">Demo Mode Active</div>
                <div class="demo-banner-desc">You're viewing results from sample documents. Download them below to verify the AI's analysis.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            with open("sample_tender.pdf", "rb") as pdf_file:
                st.download_button(
                    "📥 Download Tender PDF",
                    data=pdf_file,
                    file_name="sample_tender.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        with col2:
            with open("sample_bid.pdf", "rb") as pdf_file:
                st.download_button(
                    "📥 Download Bid PDF",
                    data=pdf_file,
                    file_name="sample_bid.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # --- SUMMARY METRICS ---
    leader = st.session_state['leaderboard'][0]
    total_bidders = len(st.session_state['leaderboard'])
    avg_score = sum(b['Raw Score'] for b in st.session_state['leaderboard']) / total_bidders
    
    st.markdown("### 📊 Evaluation Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_bidders}</div>
            <div class="metric-label">Bidders Evaluated</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{leader['Total Rules']}</div>
            <div class="metric-label">Requirements Checked</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        top_pct = int((leader['Raw Score'] / leader['Max Score']) * 100) if leader['Max Score'] > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{top_pct}%</div>
            <div class="metric-label">Top Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_pct = int((avg_score / leader['Max Score']) * 100) if leader['Max Score'] > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_pct}%</div>
            <div class="metric-label">Average Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # --- LEADERBOARD ---
    st.markdown("### 🏆 Bidder Rankings")
    
    with st.expander(f"ℹ️ **Scoring Methodology** — {leader['Max Score']} points possible", expanded=False):
        st.markdown(f"""
        The AI extracted **{leader['Total Rules']} mandatory specifications** from the tender document.
        Each requirement is scored on a 0-5 scale based on compliance evidence found in the bid submission.
        """)
        
        st.markdown("**Evaluated Requirements:**")
        cols = st.columns(2)
        for idx, rule in enumerate(leader['Details']):
            with cols[idx % 2]:
                st.markdown(f"• {rule.get('rule_name', 'Unnamed Rule')} *(5 pts)*")
    
    st.markdown("")
    
    # Build ranking dataframe
    ranking_data = []
    for rank, bidder in enumerate(st.session_state['leaderboard']):
        score_pct = int((bidder['Raw Score'] / bidder['Max Score']) * 100) if bidder['Max Score'] > 0 else 0
        row = {
            "🏅 Rank": rank + 1,
            "Bidder": bidder["Bidder"],
            "Score": bidder["Total Score"],
            "Compliance": f"{score_pct}%"
        }
        for rule in bidder["Details"]:
            row[rule.get("rule_name", "Rule")] = f"{rule.get('score', 0)}/5"
        ranking_data.append(row)
    
    df = pd.DataFrame(ranking_data)
    
    # Style the dataframe
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "🏅 Rank": st.column_config.NumberColumn(width="small"),
            "Bidder": st.column_config.TextColumn(width="medium"),
            "Score": st.column_config.TextColumn(width="small"),
            "Compliance": st.column_config.TextColumn(width="small"),
        }
    )
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # --- DETAILED BREAKDOWNS ---
    st.markdown("### 📋 Detailed Analysis")
    
    tabs = st.tabs([f"{'🥇' if i==0 else '🥈' if i==1 else '🥉' if i==2 else '📄'} {b['Bidder']}" for i, b in enumerate(st.session_state['leaderboard'])])
    
    for i, tab in enumerate(tabs):
        with tab:
            bidder = st.session_state['leaderboard'][i]
            
            # Bidder summary header
            score_pct = int((bidder['Raw Score'] / bidder['Max Score']) * 100) if bidder['Max Score'] > 0 else 0
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"#### {bidder['Bidder']}")
            with col2:
                st.metric("Final Score", bidder['Total Score'])
            with col3:
                st.metric("Compliance Rate", f"{score_pct}%")
            
            st.markdown("")
            
            # Pass/Fail/Flag summary
            passes = sum(1 for r in bidder['Details'] if r.get('status') == 'Pass')
            fails = sum(1 for r in bidder['Details'] if r.get('status') == 'Fail')
            flags = len(bidder['Details']) - passes - fails
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<span class='status-badge badge-pass'>✓ {passes} Passed</span>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<span class='status-badge badge-fail'>✗ {fails} Failed</span>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<span class='status-badge badge-flagged'>⚠ {flags} Flagged</span>", unsafe_allow_html=True)
            
            st.markdown("")
            st.markdown("---")
            
            # Individual rule cards
            for result in bidder["Details"]:
                status = result.get('status', 'Flagged')
                score = result.get('score', 0)
                
                if status == 'Pass':
                    card_class = "rule-card-pass"
                    icon = "✅"
                elif status == 'Fail':
                    card_class = "rule-card-fail"
                    icon = "❌"
                else:
                    card_class = "rule-card-flagged"
                    icon = "⚠️"
                
                with st.container():
                    st.markdown(f"""
                    <div class="rule-card {card_class}">
                        <div class="rule-title">
                            <span>{icon} {result.get('rule_name', 'Rule')}</span>
                            <span class="score-pill">{score}/5</span>
                        </div>
                        <div class="rule-detail">
                            <div class="rule-detail-label">🎯 Tender Requires</div>
                            <div class="rule-detail-value">{result.get('tender_requirement', 'N/A')}</div>
                        </div>
                        <div class="rule-detail">
                            <div class="rule-detail-label">📝 Bidder Provided</div>
                            <div class="rule-detail-value">{result.get('bidder_submission', 'Not explicitly mentioned in document.')}</div>
                        </div>
                        <div class="rule-detail">
                            <div class="rule-detail-label">🧠 AI Reasoning</div>
                            <div class="rule-detail-value"><em>{result.get('reasoning', 'No reasoning provided.')}</em></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Evidence quote in native Streamlit for better interactivity
                    quote = result.get('exact_quote', '')
                    if quote and quote.lower() not in ["n/a", "not found", "not found in document"]:
                        st.info(f"🔎 **Evidence from Document:**\n\n> *\"{quote}\"*")
                    
                    st.markdown("")

else:
    # --- EMPTY STATE ---
    st.markdown("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; background: #f8fafc; border-radius: 16px; border: 2px dashed #e2e8f0;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📤</div>
            <h3 style="color: #475569; margin-bottom: 0.5rem;">No Evaluations Yet</h3>
            <p style="color: #94a3b8;">Upload a tender document and bidder submissions in the sidebar to get started, or try the <strong>One-Click Demo</strong>.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("")
    
    # Feature highlights
    st.markdown("### ✨ What Tender IQ Does")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔍</div>
            <h4 style="color: #334155;">Auto-Extract Requirements</h4>
            <p style="color: #64748b; font-size: 0.9rem;">AI reads your tender document and identifies all mandatory specifications automatically.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⚖️</div>
            <h4 style="color: #334155;">Score Compliance</h4>
            <p style="color: #64748b; font-size: 0.9rem;">Each bidder is evaluated against every requirement with transparent scoring and reasoning.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🏆</div>
            <h4 style="color: #334155;">Rank & Compare</h4>
            <p style="color: #64748b; font-size: 0.9rem;">Get an instant leaderboard with side-by-side comparison of all bidders.</p>
        </div>
        """, unsafe_allow_html=True)