import streamlit as st
import requests
import pandas as pd
import os

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG & STATE
# ─────────────────────────────────────────────────────────────────────────────
API_BASE = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Equil - Finance Wizard", layout="wide", page_icon="🪄")

# Inject minimal dark mode tweaks to align with the old Enterprise UI
st.markdown("""
<style>
    .stApp { background-color: #020617; color: #f8fafc; }
    .stButton>button { background-color: #10b981; color: white; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #059669; }
</style>
""", unsafe_allow_html=True)

if 'session_id' not in st.session_state:
    st.session_state.session_id = ""
if 'upload_result' not in st.session_state:
    st.session_state.upload_result = None

PERSONAS = {
    "buffett": "Warren Buffett (Value & Compounding)",
    "fire": "F.I.R.E. (Aggressive savings)",
    "kiyosaki": "Robert Kiyosaki (Cashflow focus)",
    "sethi": "Ramit Sethi (Conscious spending)",
    "indian_expert": "Indian Expert (Localized strategy)"
}

# ─────────────────────────────────────────────────────────────────────────────
# API WRAPPERS
# ─────────────────────────────────────────────────────────────────────────────
def upload_files(files, persona):
    url = f"{API_BASE}/api/v1/extract/upload"
    files_to_send = [("files", (f.name, f.getvalue(), f.type)) for f in files]
    data = {"user_preference": persona}
    if st.session_state.session_id:
        data["session_id"] = st.session_state.session_id
        
    try:
        response = requests.post(url, files=files_to_send, data=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Upload failed: {e}")
        return None

def change_advisor(persona, transactions, currency):
    url = f"{API_BASE}/api/v1/extract/advisory/generate"
    payload = {
        "session_id": st.session_state.session_id,
        "persona": persona,
        "transactions": transactions,
        "currency": currency
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to regenerate advisory: {e}")
        return None

def sync_splitwise(api_key, persona):
    url = f"{API_BASE}/api/v1/splitwise/sync"
    payload = {
        "api_key": api_key, 
        "days_back": 30, 
        "user_preference": persona, 
        "session_id": st.session_state.session_id
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Splitwise sync failed: {e}")
        return None

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.title("🪄 Equil")
st.sidebar.markdown("Smart Wealth Management")

st.sidebar.divider()
st.sidebar.subheader("Settings")
selected_persona_key = st.sidebar.selectbox(
    "Select Your Advisor", 
    options=list(PERSONAS.keys()), 
    format_func=lambda x: PERSONAS[x]
)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────────────────────
st.title("Financial Dashboard")

# Document Upload Section
with st.expander("Upload Documents", expanded=st.session_state.upload_result is None):
    uploaded_files = st.file_uploader(
        "Upload Receipts, Bank Statements, or Invoices (PDF/IMG/CSV)", 
        accept_multiple_files=True
    )
    if st.button("Extract & Analyze"):
        if uploaded_files:
            with st.spinner("Extracting text and analyzing financials..."):
                res = upload_files(uploaded_files, selected_persona_key)
                if res:
                    st.session_state.upload_result = res
                    st.session_state.session_id = res.get("session_id", "")
                    st.success("Analysis Complete!")
        else:
            st.warning("Please upload at least one file.")

st.divider()

# Results Section
if st.session_state.upload_result:
    res = st.session_state.upload_result
    analytics = res.get("analytics", {})
    transactions = res.get("data", {}).get("structured_data", {}).get("transactions", [])
    currency = analytics.get("currency", "USD")
    
    # Advisor Change Handler
    current_persona = res.get("persona_routed", selected_persona_key)
    if current_persona != selected_persona_key:
        st.warning(f"You have changed your advisor to **{PERSONAS[selected_persona_key]}**.")
        if st.button("Regenerate Advice Now"):
            with st.spinner(f"Generating new advice from {PERSONAS[selected_persona_key]}..."):
                new_adv = change_advisor(selected_persona_key, transactions, currency)
                if new_adv:
                    st.session_state.upload_result["advisory_report"] = new_adv["advisory_report"]
                    st.session_state.upload_result["persona_routed"] = selected_persona_key
                    st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "🧠 Advisory", "🗂️ Transactions", "🔗 Integrations"])
    
    with tab1:
        st.subheader("Financial Health")
        score = analytics.get("health_score", 0)
        st.metric("Health Score", f"{score}/100")
        
        cats = analytics.get("categories", {})
        if cats:
            st.markdown("### Spending by Category")
            df = pd.DataFrame(list(cats.items()), columns=["Category", "Amount"])
            st.bar_chart(df.set_index("Category"))
            
        anomalies = analytics.get("anomalies", [])
        if anomalies:
            st.markdown("### Anomalies Detected")
            for a in anomalies:
                st.error(a)
                
    with tab2:
        st.subheader("Personalized Guidance")
        st.info(f"Generated by: **{PERSONAS.get(current_persona, current_persona)}**")
        st.markdown(res.get("advisory_report", "No report generated."))
        
    with tab3:
        st.subheader("Structured Data")
        if transactions:
            st.dataframe(pd.DataFrame(transactions))
        else:
            st.write("No transactions parsed.")
            
    with tab4:
        st.subheader("Splitwise Sync")
        sw_key = st.text_input("Splitwise API Key", type="password")
        if st.button("Sync Splitwise Data"):
            if sw_key:
                with st.spinner("Syncing expenses..."):
                    sw_res = sync_splitwise(sw_key, selected_persona_key)
                    if sw_res:
                        st.session_state.upload_result = sw_res
                        st.success("Sync complete! Check the Analytics tab.")
                        st.rerun()
            else:
                st.warning("Enter an API key first.")
