# SENDER_EMAIL = "goyalkhushi3844@gmail.com" 
# SENDER_PASSWORD = "bqcz oxlc uycp syvb"  # Google App Password (16 chars)
import streamlit as st
import pandas as pd
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Topsis Calculator",
    page_icon="⚖️",
    layout="centered" 
)

# --- CUSTOM CSS FOR "CARD" LOOK ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* The Container "Card" */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #ddd;
    }

    /* Input Fields Styling */
    .stTextInput>div>div>input {
        border: 1px solid #ced4da;
        border-radius: 5px;
        color: #495057;
    }

    /* Submit Button Styling (Orange) */
    .stButton>button {
        background-color: #ff9800; /* Orange color */
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: bold;
        width: 100%;
        padding: 10px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #e68900;
        color: white;
        border-color: #e68900;
    }
    
    /* Headers */
    h1 {
        text-align: center;
        color: #333;
        font-family: 'Arial', sans-serif;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- EMAIL LOGIC ---
SENDER_EMAIL = "goyalkhushi3844@gmail.com" 
SENDER_PASSWORD = "bqcz oxlc uycp syvb"  # Google App Password (16 chars)

def send_email(receiver_email, result_file):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "TOPSIS Analysis Results"
    body = "Here are your TOPSIS analysis results."
    msg.attach(MIMEText(body, 'plain'))
    with open(result_file, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={result_file}")
        msg.attach(part)
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.send_message(msg)
    server.quit()

def topsis_algorithm(df, weights, impacts):
    data = df.iloc[:, 1:].values.astype(float)
    
    # Normalize
    norm_data = data / np.sqrt((data**2).sum(axis=0))
    
    # Weight
    weighted_data = norm_data * weights
    
    # Ideal Best & Worst
    ideal_best = []
    ideal_worst = []
    for i in range(len(weights)):
        if impacts[i] == '+':
            ideal_best.append(weighted_data[:, i].max())
            ideal_worst.append(weighted_data[:, i].min())
        else:
            ideal_best.append(weighted_data[:, i].min())
            ideal_worst.append(weighted_data[:, i].max())
            
    # Distance
    dist_best = np.sqrt(((weighted_data - ideal_best)**2).sum(axis=1))
    dist_worst = np.sqrt(((weighted_data - ideal_worst)**2).sum(axis=1))
    
    # Score
    scores = dist_worst / (dist_best + dist_worst)
    
    df['Topsis Score'] = scores
    df['Rank'] = pd.Series(scores).rank(ascending=False)
    return df

# --- MAIN UI ---

st.title("TOPSIS Calculator")

# --- THE FORM CONTAINER ---
with st.container():
    st.markdown("### Input Parameters")
    
    uploaded_file = st.file_uploader("Upload CSV File", type="csv")
    
    col1, col2 = st.columns(2)
    with col1:
        weights_input = st.text_input("Weights", placeholder="1,1,1,1", help="Comma separated numerical weights")
    with col2:
        impacts_input = st.text_input("Impacts", placeholder="+,+,-,+", help="Comma separated impacts (+ or -)")
        
    email_input = st.text_input("Email Id", placeholder="name@example.com")
    
    submit_btn = st.button("Submit")

# --- RESULTS SECTION ---
if submit_btn:
    if uploaded_file and weights_input and impacts_input:
        try:
            df = pd.read_csv(uploaded_file)
            num_cols = df.shape[1] - 1
            
            # Parse inputs
            w_list = [float(x) for x in weights_input.strip(',').split(',')]
            i_list = impacts_input.strip(',').split(',')
            
            if len(w_list) != num_cols or len(i_list) != num_cols:
                st.error(f"❌ Error: Input mismatch. File has {num_cols} numeric columns.")
            else:
                # Calculate
                result_df = topsis_algorithm(df.copy(), w_list, i_list)
                
                # --- VISUAL RESULTS ---
                st.write("---")
                st.markdown("## 🏆 Results")
                
                # 1. Winner Highlight
                best_alt = result_df.loc[result_df['Rank'] == 1].iloc[0,0]
                best_score = result_df.loc[result_df['Rank'] == 1, 'Topsis Score'].values[0]
                
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                metric_col1.metric("🥇 Best Alternative", str(best_alt))
                metric_col2.metric("⭐ Top Score", f"{best_score:.4f}")
                
                # 2. TABS for clean browsing
                tab1, tab2, tab3 = st.tabs(["📄 Data Table", "📊 Bar Chart", "📥 Download"])
                
                with tab1:
                    st.dataframe(result_df.style.background_gradient(subset=['Topsis Score'], cmap="Greens"))
                
                with tab2:
                    st.bar_chart(result_df.set_index(result_df.columns[0])['Topsis Score'])
                    
                with tab3:
                    csv = result_df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Result CSV", csv, "topsis_result.csv", "text/csv")
                
                # Email
                if email_input:
                    result_df.to_csv("temp.csv", index=False)
                    try:
                        send_email(email_input, "temp.csv")
                        st.success(f"✅ Email sent successfully to {email_input}")
                    except Exception as e:
                        st.error(f"Email Error: {e}")
                    
                    if os.path.exists("temp.csv"):
                        os.remove("temp.csv")

        except ValueError:
            st.error("❌ Weights must be numbers.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("⚠️ Please fill all fields.")