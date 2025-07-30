import streamlit as st

def create_sample_snapshots():
    """Create a page with sample snapshots of different PD patient profiles"""
    st.title("Sample Patient Snapshots")
    st.write("""
    Explore these realistic patient snapshots to understand how the app provides personalized insights and recommendations.
    Each snapshot reflects a different stage and experience of Parkinson’s disease.
    """)

    st.markdown("""
    <style>
    .snapshot-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 2rem;
        margin-top: 2rem;
    }

    .snapshot-card {
        background: linear-gradient(135deg, #f4faff, #e3f2fd);
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        width: 300px;
        padding: 1.5rem;
        font-family: 'Helvetica Neue', sans-serif;
        color: #333;
        position: relative;
        transition: transform 0.2s ease;
    }

    .snapshot-card:hover {
        transform: translateY(-5px);
    }

    .snapshot-title {
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #0077b6;
    }

    .snapshot-badge {
        font-size: 0.85rem;
        padding: 0.3rem 0.6rem;
        border-radius: 12px;
        color: #fff;
        background: #4ecdc4;
        display: inline-block;
        margin-bottom: 0.75rem;
    }

    .snapshot-section {
        background-color: #ffffffcc;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }

    .snapshot-section h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
        color: #444;
    }

    .snapshot-section p {
        font-size: 0.9rem;
        margin: 0;
    }

    .snapshot-tips {
        font-size: 0.85rem;
        margin-top: 0.5rem;
        padding-left: 1rem;
    }

    .snapshot-tips li {
        margin-bottom: 0.4rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="snapshot-grid">', unsafe_allow_html=True)

    def render_card(name, age, duration, symptoms, status, sections, tips):
        st.markdown('<div class="snapshot-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="snapshot-title">{name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="snapshot-badge">{status}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="snapshot-section"><h4>Patient Info</h4><p>Age: {age} • PD Duration: {duration} • Symptoms: {symptoms}</p></div>', unsafe_allow_html=True)

        for title, content in sections:
            st.markdown(f'<div class="snapshot-section"><h4>{title}</h4><p>{content}</p></div>', unsafe_allow_html=True)

        if tips:
            st.markdown('<div class="snapshot-section"><h4>Quick Tips</h4><ul class="snapshot-tips">', unsafe_allow_html=True)
            for tip in tips:
                st.markdown(f'<li>{tip}</li>', unsafe_allow_html=True)
            st.markdown('</ul></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Example cards
    render_card(
        name="Sarah - Early Stage PD",
        age=58,
        duration="2 years",
        symptoms="Mild tremor, occasional stiffness",
        status="Good",
        sections=[
            ("Microbiome", "Balanced diet with some processed foods. Could improve fiber intake."),
            ("Impulse Control", "Minimal symptoms. Last check-in: 2 days ago."),
            ("Oral Health", "Excellent dental hygiene. Last check-up: 3 months ago."),
            ("Food of the Day", "Quinoa Salad with Avocado")
        ],
        tips=[
            "Increase fiber intake gradually",
            "Stay hydrated throughout the day",
            "Regular dental check-ups",
            "Monitor tremor patterns"
        ]
    )

    render_card(
        name="Michael - Advanced PD",
        age=65,
        duration="8 years",
        symptoms="Severe tremor, dyskinesia, GI issues",
        status="Needs Attention",
        sections=[
            ("Microbiome", "Low fiber intake. Microbiome diversity is low."),
            ("Impulse Control", "Moderate symptoms. Last check-in: 1 day ago."),
            ("Oral Health", "Some dental issues. Last check-up: 2 months ago."),
            ("Food of the Day", "Soft Mashed Sweet Potatoes")
        ],
        tips=[
            "Focus on soft, easy-to-digest foods",
            "Increase fiber intake slowly",
            "Monitor GI symptoms closely",
            "Regular medication reviews"
        ]
    )

    st.markdown('</div>', unsafe_allow_html=True)

create_sample_snapshots()
