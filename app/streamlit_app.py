import streamlit as st
import os
import sys
import time
import pandas as pd
from datetime import datetime
import uuid

# Add 'src' folder to system path safely
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(base_dir, 'src'))

try:
    from predict import predict_message, load_models
    from heuristics import analyze_heuristics
    from gmail_service import GmailService
except ImportError as e:
    st.error(f"Error: Could not import source modules: {str(e)}")
    st.stop()

FASTAPI_URL = os.environ.get("FASTAPI_URL", None)

# -----------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------
st.set_page_config(
    page_title="Digital Sentinel Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------
# CUSTOM INJECTIONS (SAAS THEME)
# -----------------------------------------
st.markdown("""
<style>
    :root {
        --bg-color: #0c0e15;
        --card-bg: rgba(22, 27, 40, 0.7);
        --border-color: rgba(255, 255, 255, 0.1);
        --accent-blue: #00e5ff;
        --accent-red: #ff3366;
        --accent-green: #00e676;
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', 'Manrope', -apple-system, sans-serif !important;
        background-color: var(--bg-color) !important;
        color: var(--text-main);
    }
    
    /* Hide top header line */
    header {visibility: hidden;}

    /* Sidebar theme */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid var(--border-color);
    }
    
    /* Metrics / Cards Glassmorphism */
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 800;
    }
    .glass-card {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    .glass-header {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 12px;
        color: var(--accent-blue);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Tag Styling */
    .severity-High { background-color: rgba(255,51,102,0.2); color: #ff3366; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold;}
    .severity-Medium { background-color: rgba(255,170,0,0.2); color: #ffaa00; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold;}
    .severity-Low { background-color: rgba(0,229,255,0.2); color: #00e5ff; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold;}

    /* Security Flag Styling */
    .flag-PASS { color: var(--accent-green); font-weight: bold;}
    .flag-FAIL { color: var(--accent-red); font-weight: bold;}
    .flag-SOFTFAIL { color: #ffaa00; font-weight: bold;}

    /* Custom Text Area */
    .stTextArea textarea {
        background-color: rgba(0,0,0,0.3) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-main) !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #00e5ff 0%, #0077ff 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 229, 255, 0.3);
        transition: all 0.3s ease;
        font-weight: 600;
        width: 100%;
        border-radius: 8px;
    }
    .stButton>button:hover {
        box-shadow: 0 6px 20px rgba(0, 229, 255, 0.5);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------
# LOAD AI MODELS
# -----------------------------------------
@st.cache_resource(show_spinner=False)
def init_ai():
    try:
        load_models()
        return True
    except FileNotFoundError:
        return False

models_loaded = init_ai()

# -----------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------
with st.sidebar:
    st.markdown("## 🛡️ Digital Sentinel")
    st.markdown("---")
    menu = st.radio("Navigation", ["Dashboard", "Live Inbox Sync", "Analytics", "Settings", "Threats"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("<p style='color: gray; font-size: 0.8rem;'>System Status: 🟢 Online</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: gray; font-size: 0.8rem;'>Model Ver: MN-Bayes v2.1</p>", unsafe_allow_html=True)

# -----------------------------------------
# HEADER SECTION
# -----------------------------------------
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("Cyberspace Threat Analysis")
    st.caption(f"Active Module: `{menu.upper()}` | Timestamp: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC`")

with col_head2:
    st.write("") # spacing
    st.write("")
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button("Confirm Spam", key="btn_spam")
    with btn_col2:
        st.button("False Positive", key="btn_fp")

st.markdown("---")

# -----------------------------------------
# MAIN VIEWS
# -----------------------------------------

if menu == "Dashboard":
    
    col_left, col_right = st.columns([5, 4])

    # Initialize session state for prediction
    if 'analyzed' not in st.session_state:
        st.session_state.analyzed = False
        st.session_state.results = {}
        st.session_state.heuristics = {}

    with col_left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='glass-header'>FORENSIC EMAIL INSPECTION PANEL</div>", unsafe_allow_html=True)
        
        sender_col, rec_col = st.columns(2)
        with sender_col:
            sender_info = st.text_input("Sender Address", value="unknown@example.com")
        with rec_col:
            rec_info = st.text_input("Recipient Address", value="admin@company.local")
            
        subject_line = st.text_input("Subject Line", value="URGENT: Account Locked - Verify Immediately")
        
        raw_content = st.text_area(
            "Raw Email Payload",
            height=300,
            value="Dear User,\n\nYour account has been suspended due to abnormal activity. You must verify your details immediately to prevent permanent termination of your account.\n\nClick the link below to verify:\nhttp://verify-account-security-update24.xyz/login\n\nFailure to do so will result in a $50 penalty fee.\n\nThank you,\nSecurity Team"
        )
        
        if st.button("RUN FORENSIC ANALYSIS", use_container_width=True):
            if not raw_content.strip():
                st.warning("Payload cannot be empty.")
            else:
                with st.spinner("Executing Deep Neural Inspection..."):
                    time.sleep(0.8) # simulate loading
                    full_text = f"{subject_line}\n{raw_content}"
                    
                    if FASTAPI_URL:
                        try:
                            # Use REST Backend (Render.com)
                            import requests
                            response = requests.post(f"{FASTAPI_URL}/predict", json={"text": full_text})
                            if response.status_code == 200:
                                data = response.json()
                                result = {
                                    "is_spam": data["is_spam"],
                                    "score": data["confidence_score"],
                                    "label": data["label"]
                                }
                                heu_result = data["heuristics"]
                            else:
                                st.error("REST Backend returned an error.")
                        except Exception as req_err:
                            st.error(f"Failed to connect to backend: {req_err}")
                            st.stop()
                    else:
                        # Use local ML loaded state
                        result = predict_message(full_text)
                        heu_result = analyze_heuristics(full_text)
                    
                    st.session_state.analyzed = True
                    st.session_state.results = result
                    st.session_state.heuristics = heu_result
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


    with col_right:
        if st.session_state.analyzed:
            res = st.session_state.results
            heu = st.session_state.heuristics
            
            is_spam = res["is_spam"]
            score = res["score"]
            
            # 1. AI Analysis Panel
            card_color = "rgba(255, 51, 102, 0.15)" if is_spam else "rgba(0, 230, 118, 0.15)"
            border_color = "var(--accent-red)" if is_spam else "var(--accent-green)"
            verdict_text = "CRITICAL THREAT (SPAM)" if is_spam else "SECURE (HAM)"
            verdict_color = "var(--accent-red)" if is_spam else "var(--accent-green)"
            
            st.markdown(f"""
            <div class='glass-card' style='background: {card_color}; border-color: {border_color};'>
                <div class='glass-header'>AI VERDICT</div>
                <h2 style='color: {verdict_color}; margin: 0; font-weight: 800; font-size: 2rem;'>{verdict_text}</h2>
                <p style='color: var(--text-muted); margin-bottom: 15px;'>Machine Learning Pipeline Output</p>
                <div style='background: rgba(0,0,0,0.4); border-radius: 8px; padding: 15px;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
                        <span>Threat Probability</span>
                        <span style='font-weight: bold; color: white;'>{score}%</span>
                    </div>
                    <div style='width: 100%; background: #333; border-radius: 4px; height: 10px;'>
                        <div style='width: {score}%; background: {verdict_color}; height: 10px; border-radius: 4px;'></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 2. Rule Engine Section
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<div class='glass-header'>TRIGGERED NLP HEURISTICS</div>", unsafe_allow_html=True)
            
            if len(heu["rules"]) == 0:
                st.markdown("<p style='color: var(--accent-green);'>✅ No abnormal heuristics detected.</p>", unsafe_allow_html=True)
            else:
                for rule in heu["rules"]:
                    st.markdown(f"""
                    <div style='border-left: 3px solid #555; padding-left: 10px; margin-bottom: 12px;'>
                        <div style='margin-bottom: 4px;'><span class='severity-{rule["severity"]}'>{rule["severity"].upper()}</span> <strong style='color: white; margin-left: 5px;'>{rule["rule"]}</strong></div>
                        <div style='color: var(--text-muted); font-size: 0.9rem;'>{rule["desc"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # 3. Technical Flags Section
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<div class='glass-header'>TECHNICAL SECURITY PROTOCOLS</div>", unsafe_allow_html=True)
            
            flags = heu["flags"]
            for proto, data in flags.items():
                status_class = f"flag-{data['status']}"
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding: 8px 0;'>
                    <span style='font-weight: 600;'>{proto} Check:</span>
                    <div style='text-align: right;'>
                        <span class='{status_class}'>{data['status']}</span>
                        <div style='font-size: 0.75rem; color: var(--text-muted);'>{data['desc']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)

        else:
            # Placeholder before analysis
            st.markdown("""
            <div class='glass-card' style='text-align: center; padding: 60px 20px; border: 1px dashed var(--border-color);'>
                <div style='font-size: 3rem; margin-bottom: 15px;'>📡</div>
                <h3 style='color: var(--text-muted);'>AWAITING DATA STREAM</h3>
                <p style='color: #666;'>Initialize forensic analysis on the left panel to generate a threat report.</p>
            </div>
            """, unsafe_allow_html=True)

elif menu == "Live Inbox Sync":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='glass-header'>REAL-TIME GMAIL INTEGRATION (OAUTH2)</div>", unsafe_allow_html=True)
    
    st.write("Authenticate with Google to pull the latest emails from your INBOX and run them through our Live Threat Detection.")
    
    max_emails = st.slider("Number of emails to fetch", 1, 25, 5)
    
    if st.button("SYNCHRONIZE AND ANALYZE INBOX", type="primary"):
        with st.spinner("Connecting to Google SMTP... please authenticate if prompted."):
            try:
                g_service = GmailService()
                emails = g_service.fetch_latest_emails(max_results=max_emails)
                
                if not emails:
                    st.info("Inbox is empty or no emails fetched.")
                else:
                    results_data = []
                    for mail in emails:
                        full_text = f"{mail['subject']}\n{mail['body']}"
                        
                        if FASTAPI_URL:
                            import requests
                            res = requests.post(f"{FASTAPI_URL}/predict", json={"text": full_text}).json()
                            verdict = {"is_spam": res["is_spam"], "score": res["confidence_score"]}
                        else:
                            verdict = predict_message(full_text)
                        
                        results_data.append({
                            "Sender": mail['sender'],
                            "Subject": mail['subject'],
                            "Threat Status": "🚨 SPAM" if verdict['is_spam'] else "✅ HAM",
                            "Confidence": f"{verdict['score']}%"
                        })
                    
                    st.success(f"Successfully processed {len(emails)} live emails.")
                    
                    df = pd.DataFrame(results_data)
                    st.dataframe(df, use_container_width=True)
                    
            except FileNotFoundError:
                st.error("Missing `credentials.json` in the root folder. Please ensure OAuth credentials are in place.")
            except Exception as e:
                st.error(f"Live Sync Encountered an Error: {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info(f"Module '{menu}' is currently offline in this environment.")
