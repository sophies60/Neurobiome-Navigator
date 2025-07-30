import streamlit as st

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

            h1, h2 {
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
    st.markdown('<div class="nav-card minerva">🔍 MINERVA Dashboard</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Close left-col

    # RIGHT COLUMN
    st.markdown('<div class="right-col">', unsafe_allow_html=True)
    
    # Personal Snapshot Card
    st.markdown("""
        <style>
        .fun-snapshot {
            background: linear-gradient(135deg, #ffecb3 0%, #ffe4e1 100%);
            padding: 2rem;
            border-radius: 30px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="fun-snapshot">', unsafe_allow_html=True)
    st.write("""
        <h2>Personal Health Snapshot</h2>
        <p>Get personalized insights about your health and how it relates to Parkinson's disease.</p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Close right-col
    st.markdown('</div>', unsafe_allow_html=True)  # Close main-container
