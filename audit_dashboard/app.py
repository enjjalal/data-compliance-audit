import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Data Compliance Audit Dashboard",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "outputs"

# Load data
@st.cache_data
def load_data():
    try:
        violations = pd.read_csv(DATA_DIR / "violations.csv")
        pii_scan = pd.read_csv(DATA_DIR / "pii_scan.csv")
        enhanced_violations = pd.read_csv(DATA_DIR / "enhanced_violations.csv")
        
        with open(DATA_DIR / "violations_history.json", 'r') as f:
            violations_history = json.load(f)
            
        return {
            'violations': violations,
            'pii_scan': pii_scan,
            'enhanced_violations': enhanced_violations,
            'violations_history': violations_history
        }
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def display_metrics(data):
    if data is None:
        return
        
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total PII Findings", len(data['pii_scan']))
    
    with col2:
        st.metric("Active Violations", len(data['violations']))
        
    with col3:
        st.metric("High Risk Findings", 
                 len(data['pii_scan'][data['pii_scan']['confidence'] > 0.7]))

def plot_violations_by_type(data):
    if data is None:
        return
        
    fig = px.bar(
        data['violations']['violation_type'].value_counts().reset_index(),
        x='index',
        y='violation_type',
        labels={'index': 'Violation Type', 'violation_type': 'Count'},
        title='Violations by Type'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_pii_distribution(data):
    if data is None:
        return
        
    pii_dist = data['pii_scan']['pii_type'].value_counts().reset_index()
    fig = px.pie(
        pii_dist,
        values='pii_type',
        names='index',
        title='PII Type Distribution'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_violation_trend(data):
    if not data or 'violations_history' not in data:
        return
        
    history = data['violations_history']
    dates = [datetime.fromisoformat(d) for d in history.keys()]
    counts = list(history.values())
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, 
        y=counts,
        mode='lines+markers',
        name='Violations'
    ))
    
    fig.update_layout(
        title='Violation Trend Over Time',
        xaxis_title='Date',
        yaxis_title='Number of Violations'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.title("🔒 Data Compliance Audit Dashboard")
    st.markdown("### Monitor and analyze data compliance across your organization")
    
    # Load data
    data = load_data()
    
    # Display metrics
    st.markdown("### Key Metrics")
    display_metrics(data)
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        plot_violations_by_type(data)
    
    with col2:
        plot_pii_distribution(data)
    
    st.markdown("### Violation Trend")
    plot_violation_trend(data)
    
    # Raw data tabs
    st.markdown("### Detailed Data")
    tab1, tab2, tab3 = st.tabs(["PII Scan Results", "Active Violations", "Enhanced Violations"])
    
    with tab1:
        st.dataframe(data['pii_scan'] if data is not None else pd.DataFrame())
    
    with tab2:
        st.dataframe(data['violations'] if data is not None else pd.DataFrame())
    
    with tab3:
        st.dataframe(data['enhanced_violations'] if data is not None else pd.DataFrame())
    
    # Add some styling
    st.markdown("""
    <style>
    .stMetricLabel { font-size: 1rem; }
    .stMetricValue { font-size: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
