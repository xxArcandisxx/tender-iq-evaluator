import streamlit as st
import json
import os
from match_engine import evaluate_bidder_against_rules

# Set page layout
st.set_page_config(page_title="Tender IQ Evaluator", layout="wide", page_icon="⚖️")

st.title("⚖️ Tender IQ: AI Procurement Evaluator")
st.markdown("Automated, transparent compliance checking for government tenders.")

# --- SIDEBAR: Document Uploads ---
st.sidebar.header("1. Upload Documents")
tender_file = st.sidebar.file_uploader("Upload Tender Document (Rules)", type="pdf", key="tender")
bidder_file = st.sidebar.file_uploader("Upload Bidder Submission (Data)", type="pdf", key="bidder")

if tender_file and bidder_file:
    # Save files temporarily for the backend to process
    with open("temp_tender.pdf", "wb") as f: f.write(tender_file.getbuffer())
    with open("temp_bid.pdf", "wb") as f: f.write(bidder_file.getbuffer())
    
    st.sidebar.success("Both documents uploaded successfully!")
    
    # --- ACTION BUTTON ---
    if st.sidebar.button("Run Smart Evaluation", type="primary"):
        with st.spinner("Extracting rules, reading bid, and cross-referencing logic... This takes about 10 seconds."):
            
            # Run the core AI engine
            result_str = evaluate_bidder_against_rules("temp_tender.pdf", "temp_bid.pdf")
            st.session_state['evaluation_results'] = json.loads(result_str).get('evaluation_results', [])

# --- MAIN DASHBOARD AREA ---
if 'evaluation_results' in st.session_state:
    st.markdown("---")
    st.header("📋 Final Evaluation Report")
    
    # Calculate summary metrics
    total = len(st.session_state['evaluation_results'])
    passed = sum(1 for r in st.session_state['evaluation_results'] if r['status'] == 'Pass')
    failed = sum(1 for r in st.session_state['evaluation_results'] if r['status'] == 'Fail')
    flagged = sum(1 for r in st.session_state['evaluation_results'] if r['status'] == 'Flagged')
    
    # Display top-level metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rules Checked", total)
    col2.metric("✅ Passed", passed)
    col3.metric("❌ Failed", failed)
    col4.metric("⚠️ Flagged (Review)", flagged)
    
    st.markdown("### Detailed Breakdown")
    
    # Loop through results and display color-coded cards
    for idx, result in enumerate(st.session_state['evaluation_results']):
        status = result.get('status', 'Flagged')
        
        # Pick the right color block based on the status
        if status == 'Pass':
            box = st.success
            icon = "✅"
        elif status == 'Fail':
            box = st.error
            icon = "❌"
        else:
            box = st.warning
            icon = "⚠️"
            
        with box(f"{icon} **{result.get('rule_name', 'Rule')}** - Status: {status}"):
            st.write(f"**Tender Requires:** {result.get('tender_requirement', 'N/A')}")
            st.write(f"**Bidder Provided:** {result.get('bidder_submission', 'N/A')}")
            st.markdown(f"**AI Reasoning:** *{result.get('reasoning', 'N/A')}*")