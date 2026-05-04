import streamlit as st
import pandas as pd
import json
import os
import time
from match_engine import evaluate_bidder_against_rules

# Set page layout
st.set_page_config(page_title="Tender IQ Evaluator", layout="wide", page_icon="⚖️")
st.title("⚖️ Tender IQ: AI Procurement Evaluator")
st.markdown("Automated multi-bidder ranking and compliance scoring.")

# --- SIDEBAR: Document Uploads ---
st.sidebar.header("1. Upload Documents")
tender_file = st.sidebar.file_uploader("Upload Tender Document (Rules)", type="pdf", key="tender")

# 1. Initialize a memory bank for our bidder files
if 'bidder_list' not in st.session_state:
    st.session_state['bidder_list'] = []

# 2. The Uploader
new_bidders = st.sidebar.file_uploader("Upload Bidder Submissions", type="pdf", accept_multiple_files=True, key="bidders")

# 3. Add new files to memory without duplicates
if new_bidders:
    for file in new_bidders:
        if file.name not in [f.name for f in st.session_state['bidder_list']]:
            st.session_state['bidder_list'].append(file)

# 4. Show the user what they have accumulated
if st.session_state['bidder_list']:
    st.sidebar.markdown("**📄 Accumulated Bidders:**")
    for f in st.session_state['bidder_list']:
        st.sidebar.markdown(f" - {f.name}")
        
    if st.sidebar.button("🗑️ Clear Bidders List"):
        st.session_state['bidder_list'] = []
        st.rerun()

# --- ACTION BUTTON ---
if tender_file and len(st.session_state['bidder_list']) > 0:
    with open("temp_tender.pdf", "wb") as f: f.write(tender_file.getbuffer())
    
    st.sidebar.success(f"Tender and {len(st.session_state['bidder_list'])} Bidder(s) ready!")
    
    if st.sidebar.button("Run Smart Multi-Evaluation", type="primary"):
        all_bidders_data = []
        
        for idx, b_file in enumerate(st.session_state['bidder_list']):
            bidder_name = b_file.name
            temp_bid_path = f"temp_bid_{idx}.pdf"
            
            with open(temp_bid_path, "wb") as f: f.write(b_file.getbuffer())
            
            with st.spinner(f"Analyzing {bidder_name}..."):
                # Call the AI Engine
                result_str = evaluate_bidder_against_rules("temp_tender.pdf", temp_bid_path)
                eval_results = json.loads(result_str).get('evaluation_results', [])
                
                # Protect the free tier limit: pause for 2 seconds between documents
                time.sleep(2)
                
                # Calculate scores
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
        
        # Sort by highest score for the leaderboard
        all_bidders_data = sorted(all_bidders_data, key=lambda x: x["Raw Score"], reverse=True)
        st.session_state['leaderboard'] = all_bidders_data

# --- MAIN DASHBOARD AREA ---
if 'leaderboard' in st.session_state:
    st.markdown("---")
    st.header("🏆 Multi-Bidder Leaderboard")
    
    sample_rules_count = st.session_state['leaderboard'][0]['Total Rules']
    sample_max_score = st.session_state['leaderboard'][0]['Max Score']
    
    # --- INTERACTIVE MATH EXPANDER ---
    with st.expander(f"🧮 **How is this scored? (Maximum Score: {sample_max_score} Points)**", expanded=False):
        st.write(f"The AI automatically extracted **{sample_rules_count} mandatory specifications** from the Tender document. Each specification is graded on a strict 1 to 5 scale.")
        st.markdown("---")
        
        sample_rules = [r.get('rule_name', 'Unnamed Rule') for r in st.session_state['leaderboard'][0]['Details']]
        col1, col2 = st.columns(2)
        for idx, rule in enumerate(sample_rules):
            if idx % 2 == 0:
                col1.markdown(f"- **{rule}** *(Max 5 pts)*")
            else:
                col2.markdown(f"- **{rule}** *(Max 5 pts)*")
                
        st.markdown("---")
        st.markdown(f"**Total Potential Score = {sample_rules_count} rules × 5 points = {sample_max_score} points.**")
    
    # --- THE LEADERBOARD TABLE ---
    ranking_data = []
    for rank, bidder in enumerate(st.session_state['leaderboard']):
        row = {"Rank": rank + 1, "Bidder Name": bidder["Bidder"], "Total Score": bidder["Total Score"]}
        for rule in bidder["Details"]:
            row[rule["rule_name"]] = f"{rule.get('score', 0)}/5"
        ranking_data.append(row)
        
    df = pd.DataFrame(ranking_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # --- SCORING RUBRICS ---
    st.markdown("### ℹ️ Evaluation & Grading Rubrics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Individual Rule Scoring (1-5)**")
        rubric_df = pd.DataFrame({
            "Score": ["5", "4", "3", "2", "1"],
            "Meaning": [
                "Exceeded requirement flawlessly",
                "Passed with standard compliance",
                "Met minimum requirements / Flagged for review",
                "Failed partially / Missing minor elements",
                "Failed completely / Non-compliant"
            ]
        })
        st.table(rubric_df)
        
    with col2:
        st.markdown("**Total Score Grading Scale**")
        total_rubric_df = pd.DataFrame({
            "Final Score": ["90% - 100%", "75% - 89%", "60% - 74%", "Below 60%"],
            "Classification": ["🟢 Tier 1: Exceptional", "🟡 Tier 2: Acceptable", "🟠 Tier 3: High Risk", "🔴 Tier 4: Disqualified"],
            "Recommended Action": [
                "Auto-Shortlist",
                "Proceed with Clarifications",
                "Manual Review Required",
                "Reject Bid"
            ]
        })
        st.table(total_rubric_df)
    
    st.markdown("---")
    st.header("📄 Detailed Bidder Breakdowns")
    
    # --- BIDDER TABS ---
    tabs = st.tabs([b["Bidder"] for b in st.session_state['leaderboard']])
    for i, tab in enumerate(tabs):
        with tab:
            bidder = st.session_state['leaderboard'][i]
            st.subheader(f"Evaluation for {bidder['Bidder']}")
            st.markdown(f"> **Final Score: {bidder['Total Score']}** *(Sum of {bidder['Total Rules']} specifications × 5 points max each)*")
            st.write("") 
            
            for result in bidder["Details"]:
                status = result.get('status', 'Flagged')
                score = result.get('score', 0)
                
                if status == 'Pass': box = st.success; icon = "✅"
                elif status == 'Fail': box = st.error; icon = "❌"
                else: box = st.warning; icon = "⚠️"
                    
                with box(f"{icon} **{result.get('rule_name', 'Rule')}** (Score: {score}/5)"):
                    st.write(f"**Tender Requires:** {result.get('tender_requirement', 'N/A')}")
                    st.write(f"**Bidder Provided:** {result.get('bidder_submission', 'N/A')}")
                    st.markdown(f"**AI Reasoning:** *{result.get('reasoning', 'N/A')}*")