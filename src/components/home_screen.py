import streamlit as st
from .survey import SurveyManager, get_survey_summary, show_survey

def create_home_screen():
    """Create the home screen with navigation cards"""
    # --- Custom Styling ---
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Playfair+Display&family=Inter&display=swap');

            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
                background-color: #fefefe;
            }

            h1, h2, h3 {
                font-family: 'Playfair Display', serif;
            }

            .main-container {
                display: flex;
                justify-content: center;
                align-items: flex-start;
                padding: 2rem;
                gap: 3rem;
            }

            .left-col {
                flex: 2;
            }

            .right-col {
                flex: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 1rem;
                background-color: #f4faff;
                border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }

            .snapshot-img {
                width: 100px;
                height: 100px;
            }

            .nav-card {
                padding: 1rem 1.5rem;
                border-radius: 12px;
                margin-bottom: 1rem;
                font-size: 1.1rem;
                font-weight: 500;
                box-shadow: 0 2px 6px rgba(0,0,0,0.04);
                display: flex;
                align-items: center;
                justify-content: space-between;
                cursor: default;
            }

            .gut { background-color: #fff3e0; }
            .impulse { background-color: #ede7f6; }
            .oral { background-color: #e0f7fa; }
            .minerva { background-color: #e8f5e9; }

            .powered-by {
                text-align: right;
                font-size: 0.9rem;
                color: #888;
                margin-bottom: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- Header ---
    st.markdown('<div class="powered-by">Powered by <a href="https://github.com/MGH-LMIC/MINERVA" target="_blank">MINERVA</a></div>', unsafe_allow_html=True)
    st.markdown("<h1>Neurobiome Navigator</h1>", unsafe_allow_html=True)
    
    # --- Introduction ---
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%); 
                padding: 1.5rem; 
                border-radius: 12px; 
                margin: 1.5rem 0;
                border-left: 5px solid #6c63ff;'>
        <h2 style='color: #2d3748; margin-top: 0;'>Understanding Parkinson's Disease & The Microbiome Connection</h2>
        <p style='font-size: 1.1rem; line-height: 1.6; color: #4a5568;'>
            Parkinson's Disease (PD) is a complex condition that affects both movement and challenging non-motor aspects, 
            including Impulse Control Disorders (ICDs). Emerging research highlights the significant influence of your 
            body's microbial communities, known as microbiomes, specifically those in your oral cavity and gut, which 
            are intricately linked to PD risk, symptom progression, and even the presence of ICDs.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- Layout ---
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # LEFT COLUMN
    st.markdown('<div class="left-col">', unsafe_allow_html=True)

    st.markdown("## Welcome to Neurobiome Navigator")
    st.write("Explore the connections between your microbiome and Parkinson’s disease.")

    # Navigation cards (non-clickable, since navigation is in the sidebar now)
    st.markdown('<div class="nav-card gut">🦠 Gut Insight Navigator</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-card impulse">🧠 Impulse Control Spotlight</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-card oral">🦷 Oral Health & PD Connection</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Close left-col

    # RIGHT COLUMN
    st.markdown('<div class="right-col">', unsafe_allow_html=True)
    
    # --- Personal Snapshot Card ---
    st.markdown("### 🎯 Personal Snapshot")
        max-width: 600px;
        width: 100%;
        font-family: 'Arial', sans-serif;
        overflow: hidden; /* Ensures child elements respect the border radius */
    }
    .card-section {
        background: #f9f9ff;
        padding: 1.25rem 1.5rem;
        margin: 0;
        border-bottom: 1px solid #eee;
    }
    .card-section:last-child {
        border-bottom: none; /* Remove border from last section */
    }
    .card-title {
        color: #6c63ff;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .card-text {
        color: #555;
        line-height: 1.5;
        font-size: 0.95rem;
        text-align: center;
    }
    .quick-tip {
        background: #f0f7ff;
        padding: 1rem 1.5rem;
        border-left: 4px solid #6c63ff;
        margin: 0;
    }
    .quick-tip-title {
        color: #6c63ff;
        font-weight: 600;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Card Container and Header
    st.markdown("""
    <div class="snapshot-card">
        <div style="padding: 1.5rem 1.5rem 1.25rem; text-align: center; border-bottom: 1px solid #eee;">
            <h2 style="color: #6c63ff; margin: 0;">✨ Your Health Snapshot</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Survey Summary Section
    survey_summary = get_survey_summary()
    st.markdown(f"""
    <div class="card-section">
        <div class="card-title">📋 Survey Summary</div>
        <div class="card-text">
            {survey_summary}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Dietary Tips Section
    st.markdown("""
    <div class="card-section">
        <div class="card-title">🍎 Dietary Tips</div>
        <div class="card-text">
            <b>Try:</b> Add berries for antioxidants<br>
            <b>Remember:</b> Stay hydrated daily
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Oral Health Section
    st.markdown("""
    <div class="card-section">
        <div class="card-title">🦷 Oral Health</div>
        <div class="card-text">
            <b>Next checkup:</b> In 3 months
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Tip Section
    st.markdown("""
    <div class="quick-tip">
        <div class="quick-tip-title">💡 Quick Tip</div>
        <div class="card-text" style="margin-top: 0.5rem;">
            10-min walk after meals helps digestion
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    # Show survey form in an expander
    with st.expander("✏️ Update My Health Survey", expanded=False):
        show_survey()
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close right-col
    st.markdown('</div>', unsafe_allow_html=True)  # Close main-container
