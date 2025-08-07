import streamlit as st

def create_sample_snapshots():
    """Create a page with sample snapshots of different PD patient profiles"""
    st.title("Sample Patient Snapshots")
    st.write("""
    Explore these realistic patient snapshots to understand how the app provides personalized insights and recommendations.
    Each snapshot reflects a different stage and experience of Parkinson's disease.
    """)

    # Base styles with unique background colors for each card
    card_styles = ["""
    <style>
    .snapshot-card-1 {
        background: linear-gradient(135deg, #e3f2ff, #bbdefb);
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 2rem auto;
        max-width: 600px;
        width: 100%;
        font-family: 'Arial', sans-serif;
        overflow: hidden;
    }
    """,
    """
    <style>
    .snapshot-card-2 {
        background: linear-gradient(135deg, #fff8e1, #ffe0b2);
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 2rem auto;
        max-width: 600px;
        width: 100%;
        font-family: 'Arial', sans-serif;
        overflow: hidden;
    }
    """,
    """
    <style>
    .snapshot-card-3 {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 2rem auto;
        max-width: 600px;
        width: 100%;
        font-family: 'Arial', sans-serif;
        overflow: hidden;
    }
    </style>
    """]

    # Shared card styles
    shared_styles = """
    <style>
    .card-section {
        background: #f9f9ff;
        padding: 1.25rem 1.5rem;
        margin: 0;
        border-bottom: 1px solid #eee;
    }
    .card-section:last-child {
        border-bottom: none;
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
    .bio-section {
        padding: 1.5rem;
        text-align: center;
    }
    
    .bio-1 {
        background: #bbdefb !important;
        border-bottom: 1px solid #90caf9 !important;
    }
    
    .bio-2 {
        background: #ffe0b2 !important;
        border-bottom: 1px solid #ffcc80 !important;
    }
    
    .bio-3 {
        background: #ffcdd2 !important;
        border-bottom: 1px solid #ef9a9a !important;
    }
    .bio-name {
        font-size: 1.5rem;
        color: #4a4a9c;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .bio-details {
        color: #666;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    .bio-status {
        display: inline-block;
        background: #6c63ff;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    </style>
    """

    st.markdown(shared_styles, unsafe_allow_html=True)

    def render_card(card_num, name, age, duration, symptoms, status, oral_health, impulse_control, tips, dietary_tip, oral_health_tip, quick_tip):
        st.markdown(card_styles[card_num-1], unsafe_allow_html=True)
        
        st.markdown(f'<div class="snapshot-card-{card_num}">', unsafe_allow_html=True)
        
        # Bio Section
        st.markdown(f'''
        <div class="bio-section bio-{card_num}">
            <div class="bio-name">{name}</div>
            <div class="bio-details">
                {age} years • PD for {duration} • {symptoms}
            </div>
            <div class="bio-status">{status}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Survey Summary Section
        st.markdown(f'''
        <div class='card-section'>
            <div class='card-title'>Survey Summary</div>
            <div style='display: flex; justify-content: center; gap: 2rem; margin-top: 1rem;'>
                <div style='text-align: center; padding: 0 1rem;'>
                    <div style='font-weight: 600; color: #3a3a3a; margin-bottom: 0.5rem;'>🦷 Oral Health</div>
                    <div style='font-size: 0.9rem; color: #444;'>{oral_health}</div>
                </div>
                <div style='width: 1px; background-color: #eee;'></div>
                <div style='text-align: center; padding: 0 1rem;'>
                    <div style='font-weight: 600; color: #3a3a3a; margin-bottom: 0.5rem;'>🧠 Impulse Control</div>
                    <div style='font-size: 0.9rem; color: #444;'>{impulse_control}</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Dietary Tips Section
        st.markdown(f'''
        <div class="card-section">
            <div class="card-title">🍎 Dietary Tips</div>
            <div class="card-text">
                {dietary_tip}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Oral Health Section
        st.markdown(f'''
        <div class="card-section">
            <div class="card-title">🦷 Oral Health</div>
            <div class="card-text">
                <b>Tip:</b> {oral_health_tip}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Quick Tip Section
        st.markdown(f'''
        <div class="card-section">
            <div class="card-title">💡 Quick Tip</div>
            <div class="card-text">
                {quick_tip}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Example Card 1 - Newly Diagnosed
    render_card(
        card_num=1,
        name="Sarah Johnson",
        age=52,
        duration="6 months",
        symptoms="Occasional hand tremor, mild stiffness",
        status="Mild PD",
        oral_health="Maintains regular dental routine",
        impulse_control="No significant concerns",
        dietary_tip="<b>Try:</b> Adding walnuts to your morning oatmeal for healthy fats<br><b>Remember:</b> Drinking water throughout the day helps with digestion",
        oral_health_tip="Brushing before breakfast protects your enamel from acidic foods.",
        quick_tip="Taking short walks after meals can help with digestion and mood.",
        tips=[]
    )

    # Example Card 2 - Moderate PD
    render_card(
        card_num=2,
        name="Michael Chen",
        age=65,
        duration="5 years",
        symptoms="Noticeable tremor, slower movements, some balance changes",
        status="Moderate PD",
        oral_health="Experiences dry mouth, uses special toothpaste",
        impulse_control="Occasional impulsive shopping, working on strategies",
        dietary_tip="<b>Try:</b> Adding turmeric to meals for its anti-inflammatory properties<br><b>Remember:</b> Eating protein with carbs helps maintain energy levels",
        oral_health_tip="Chewing sugar-free gum can help stimulate saliva flow.",
        quick_tip="Gentle stretching in the morning can help with flexibility and movement.",
        tips=[]
    )

    # Example Card 3 - Advanced PD
    render_card(
        card_num=3,
        name="Robert Williams",
        age=72,
        duration="12 years",
        symptoms="Significant movement challenges, requires more time for daily activities",
        status="Advanced PD",
        oral_health="Uses electric toothbrush and special flossers",
        impulse_control="Uses spending limits and family support",
        dietary_tip="<b>Try:</b> Nutrient-rich smoothies with Greek yogurt and berries<br><b>Remember:</b> Smaller, more frequent meals can be easier to manage",
        oral_health_tip="Using a straw for acidic drinks helps protect tooth enamel.",
        quick_tip="Using a pill organizer with alarms helps for staying on schedule with medications.",
        tips=[]
    )

