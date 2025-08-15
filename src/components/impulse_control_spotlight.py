import streamlit as st
from minerva import MINERVA
from agent import minerva_agent, MINERVADependencies
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .survey import SurveyManager, SurveyType
import time, asyncio
from metrics import span, log_csv, now_iso 

# Dictionary of microbiome descriptions
MICROBIOME_DESCRIPTIONS = {
    "Methanobrevibacter": "In Parkinson's Disease (PD) patients exhibiting Impulse Control Disorders (ICDs), the genus Methanobrevibacter has been found to be significantly enriched in the gut microbiota compared to non-impulsive PD patients. This enrichment of Methanobrevibacter in the impulsive group was robust, withstanding correction for multiple testing. Network analysis further revealed a strong positive correlation between Methanobrevibacter and Cloacibacillus within the impulsive group, forming a distinct microbial cluster. While the precise mechanism linking Methanobrevibacter to ICDs in PD is still under investigation, its altered abundance suggests a potential involvement of gut microbiota in the pathophysiology of impulsive behaviors in PD.",
    "Intestinimonas butyriciproducens": "This species was the only species that remained significantly enriched in the gut microbiota of Parkinson's Disease (PD) patients with Impulse Control Disorders (ICDs) after rigorous statistical correction. Intestinimonas butyriciproducens is recognized as a butyrate-producing bacterium. Butyrate, a short-chain fatty acid (SCFA), is known to influence brain function and behavior by modulating neuroinflammation, blood-brain barrier integrity, and neurotransmitter production. The observed altered abundance of this bacterium suggests a potential link between gut microbial metabolism, particularly SCFA production, and impulsive behaviors in PD. Butyrate has been implicated in regulating levels of GABA and serotonin, both of which play crucial roles in impulse control and emotional regulation, thus highlighting a possible pathway through which Intestinimonas butyriciproducens may contribute to ICDs in PD."
}

async def create_impulse_control_spotlight():
    """Create the Impulse Control Spotlight dashboard"""
    st.title("Impulse Control Spotlight")
    
    # Initialize MINERVA client
    minerva = MINERVA()
    
    # Load papers if not already loaded
    if not hasattr(minerva, 'research_embeddings'):
        with st.spinner('Loading research papers...'):
            minerva.load_research_papers("research_papers")
    
    # Introductory context
    st.markdown("""Impulse Control Disorders (ICDs) are challenging, hard-to-control urges that can affect people with Parkinson's Disease (PD), leading to compulsive behaviors like gambling or shopping. While sometimes linked to PD medications, ICDs can also occur independently, suggesting other biological reasons. New research indicates your gut microbiome—the community of tiny living things in your intestines—might play a key role in ICDs in PD through the gut-brain axis. Studies have found certain gut bacteria like Methanobrevibacter and Intestinimonas butyriciproducens are more abundant in PD patients with impulsive behaviors. These bacteria and their metabolic activities, affecting pathways like nicotinate, nicotinamide, and caffeine metabolism, could influence brain chemicals such as GABA and serotonin, which are crucial for impulse and emotional control. These findings suggest new, non-medication-based ways to understand and potentially manage ICDs by focusing on the gut microbiome.""")

    
    
    # Create tabs first to ensure they're available throughout the function
    tab1, tab2, tab3 = st.tabs(["Microbiome Insights", "ICD Symptoms", "Research Insights"])

    with tab1:
        st.header("Microbiome Insights")
        
        # List of specific microbiomes related to gut and Parkinson's disease
        specific_microbiomes = [
            "Methanobrevibacter",
            "Intestinimonas butyriciproducens"
        ]



        # Display microbe selection
        st.markdown("""
        <style>
        .microbe-info {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        .relation-card {
            background-color: #e8f5e9;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .relation-title {
            color: #1b5e20;
            margin-bottom: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<p style='color: #4a5568; margin-bottom: 10px; font-size: 0.95rem;'>Select from the most influential gut microbiomes linked to Impulse Control Disorders in Parkinson's:</p>", unsafe_allow_html=True)
            selected_microbes = st.multiselect(
                "Select Microbiomes",
                options=list(MICROBIOME_DESCRIPTIONS.keys()),
                default=[list(MICROBIOME_DESCRIPTIONS.keys())[0]],
                max_selections=4
            )
        
        with col2:
            if selected_microbes:
                st.markdown("<h3>Selected Microbiomes</h3>", unsafe_allow_html=True)
                for microbe_name in selected_microbes:
                    st.markdown(f"<div class='microbe-info'>", unsafe_allow_html=True)
                    st.markdown(f"<h5>{microbe_name}</h5>", unsafe_allow_html=True)
                    st.markdown("<p>", unsafe_allow_html=True)
                    st.write(MICROBIOME_DESCRIPTIONS[microbe_name])
                    st.markdown("</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
    
        # Metabolic Pathways Section – Styled for Patient Readability
        expander_style = """
        <style>
        section[data-testid="stExpander"] > div:first-child {
            background-color: #d1ecf1;
            color: #0c5460;
            border: 2px solid #bee5eb;
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease-in-out;
        }
        section[data-testid="stExpander"] > div:first-child span {
            font-size: 22px;
            font-weight: 700;
        }   
        section[data-testid="stExpander"] > div:first-child:hover {
            background-color: #cde2e7;
            border-color: #a8d3dc;
            cursor: pointer;
        }   
        .metabolic-block {
            background-color: #f8f9fa;
            padding: 18px;
            border-radius: 10px;
            margin-bottom: 18px;
            border-left: 5px solid #dc3545;
        }
        .increased-block {
            border-left: 5px solid #28a745;
        }
        .block-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 8px;
            color: #343a40;
        }
        .block-point {
            margin-left: 15px;
            color: #495057;
            font-size:  16px;
        }
        .block-note {
            color: #6c757d;
            font-size: 15px;
            margin-top: 5px;
        }
        </style>
        """
        
        st.markdown(expander_style, unsafe_allow_html=True)

        # ↓ Decreased Pathways
        with st.expander("↓ Metabolic Activity Decreases in Impulsive Parkinson’s Patients"):
            st.markdown("""
        <div class='metabolic-block'>
            <div class='block-title'>1. Brain Chemical Production</div>
            <div class='block-point'>Less activity in amino acids like tryptophan and tyrosine</div>
            <div class='block-note'>These are building blocks for serotonin and dopamine, which help regulate mood and control impulses.</div>
        </div>

        <div class='metabolic-block'>
            <div class='block-title'>2. Energy and Gut Health</div>
            <div class='block-point'>Lower activity in sugar breakdown and butyrate production</div>
            <div class='block-note'>Butyrate is a healthy compound made by gut bacteria that supports brain health and reduces inflammation.</div>
        </div>

        <div class='metabolic-block'>
            <div class='block-title'>3. Vitamin B3 (Niacin) Processing</div>
            <div class='block-point'>Less breakdown of nicotinate and nicotinamide</div>
            <div class='block-note'>These help with brain protection, stress response, and keeping nerve cells healthy.</div>
        </div>

        <div class='metabolic-block'>
            <div class='block-title'>4. Natural Brain Protection</div>
            <div class='block-point'>Lower production of natural detox chemicals (polyketides)</div>
            <div class='block-note'>These may help protect the brain from damage and stress.</div>
        </div>

        <div class='metabolic-block'>
            <div class='block-title'>5. Caffeine Processing</div>
            <div class='block-point'>Slower breakdown of caffeine</div>
            <div class='block-note'>This may affect dopamine, which plays a role in attention and self-control.</div>
        </div>

        <div class='metabolic-block'>
            <div class='block-title'>6. Serotonin Pathway Disruption</div>
            <div class='block-point'>Lower production of indole compounds (from tryptophan)</div>
            <div class='block-note'>These help make serotonin—a key chemical for mood and emotional balance.</div>
        </div>

        <div class='metabolic-block'>
            <div class='block-title'>7. Detox and Waste Breakdown</div>
            <div class='block-point'>Reduced breakdown of environmental toxins (like xylene and dioxin)</div>
            <div class='block-note'>Could mean more stress on the brain and body.</div>
        </div>

        <div style='margin-top: 20px; padding: 15px; background-color: #f1f3f5; border-radius: 10px;'>
            <p style='color: #495057; font-size: 15px;'>
                These changes suggest that people with impulsive behaviors in Parkinson’s may not have fewer gut bacteria overall—but rather different types doing different things. These shifts could affect the brain through the gut-brain connection.
            </p>
        </div>
""", unsafe_allow_html=True)

        # ↑ Increased Pathways
        with st.expander("↑ Metabolic Activity Increases in Impulsive Parkinson’s Patients"):
            st.markdown("""
        <div class='metabolic-block increased-block'>
            <div class='block-title'>1. Nitrogen and Ammonia Processing</div>
            <div class='block-point'>More nitrate breakdown and higher urea cycle activity</div>
            <div class='block-note'>Could lead to changes in how the gut handles nitrogen, which might affect brain health.</div>
        </div>

        <div class='metabolic-block increased-block'>
            <div class='block-title'>2. Fatty Acid Production</div>
            <div class='block-point'>Increased creation of short-chain fatty acids (SCFAs)</div>
            <div class='block-point'>More branched-chain fatty acids made by gut microbes</div>
            <div class='block-note'>SCFAs are helpful in balance—but too much or the wrong kind may impact brain signals or inflammation.</div>
        </div>

        <div style='margin-top: 20px; padding: 15px; background-color: #f1f3f5; border-radius: 10px;'>
            <p style='color: #495057; font-size: 15px;'>
                These increased processes might reflect how the gut’s activity shifts in impulsive individuals—possibly producing too much of certain compounds that affect brain function through the gut-brain connection.
            </p>
        </div>
""", unsafe_allow_html=True)
     

    with tab2:
        st.header("ICD Symptoms")
        
        st.subheader("Impulse Control Disorder Symptoms")
        
        # ICD symptoms questions
        gambling = st.slider("How often do you feel the urge to gamble?", 0, 5, 0, help="0 = Never, 5 = Always")
        shopping = st.slider("How often do you make impulsive purchases?", 0, 5, 0, help="0 = Never, 5 = Always")
        eating = st.slider("How often do you experience binge eating?", 0, 5, 0, help="0 = Never, 5 = Always")
        hypersexuality = st.slider("How often do you experience increased sexual urges?", 0, 5, 0, help="0 = Never, 5 = Always")
        punding = st.slider("How often do you engage in repetitive, purposeless activities?", 0, 5, 0, help="0 = Never, 5 = Always")
        
        # Only show graph and insights after submission
        if st.button("Submit Survey"):
            with st.spinner('Analyzing your symptoms...'):
                # ---- ALL-UP: measure the whole submit flow
                with span("insights_total", page="impulse_control"):

                    # Store survey responses
                    survey_responses = {
                        'Gambling': gambling,
                        'Shopping': shopping,
                        'Eating': eating,
                        'Hypersexuality': hypersexuality,
                        'Punding': punding
                    }

                    # Save to session state
                    survey_manager = SurveyManager()
                    survey_manager.update_responses(SurveyType.IMPULSE_CONTROL, survey_responses)

                    # Build DataFrame
                    symptom_order = ['Punding', 'Hypersexuality', 'Eating', 'Shopping', 'Gambling']
                    symptoms = pd.DataFrame({
                        'Symptom': symptom_order,
                        'Score': [survey_responses[symptom] for symptom in symptom_order]
                    }).astype({'Score': int})

                    st.subheader("Your ICD Symptom Profile")

                    # ---- Chart render timing
                    with span("insights_chart_render", page="impulse_control"):
                        fig = go.Figure()
                        for _, row in symptoms.iterrows():
                            fig.add_trace(go.Bar(
                                x=[row['Score']],
                                y=[row['Symptom']],
                                orientation='h',
                                text=[str(row['Score'])],
                                textposition='auto',
                                marker_color='#1f77b4',
                                showlegend=False
                            ))
                        fig.update_layout(
                            xaxis=dict(
                                title='Severity (0-5)',
                                tickvals=[0, 1, 2, 3, 4, 5],
                                ticktext=['0 (None)', '1', '2', '3', '4', '5 (Severe)'],
                                range=[0, 5],
                                showgrid=True,
                                gridcolor='lightgray',
                                showline=True,
                                linewidth=1,
                                linecolor='lightgray'
                            ),
                            yaxis=dict(
                                title='Symptom',
                                showline=True,
                                linewidth=1,
                                linecolor='lightgray',
                                categoryorder='array',
                                categoryarray=symptom_order[::-1]
                            ),
                            plot_bgcolor='rgba(0,0,0,0)',
                            height=300,
                            margin=dict(l=100, r=20, t=30, b=50),
                            hovermode='closest',
                            showlegend=False,
                            barmode='group'
                        )

                        st.caption("Severity Scale: 0 = None, 1 = Minimal, 2 = Mild, 3 = Moderate, 4 = Severe, 5 = Extreme")
                        st.plotly_chart(fig, use_container_width=True)

            # Personalized insights
            st.markdown("### Personalized Insights")
            with st.spinner('Analyzing your responses and researching relevant findings...'):
                active_symptoms = {k: v for k, v in survey_responses.items() if v > 0}

                if not active_symptoms:
                    st.info("No significant symptoms reported. This is a positive sign!")
                else:
                    symptom_text = ", ".join([f"{k.lower()} (score: {v}/5)" for k, v in active_symptoms.items()])
                    query = (
                        f"Based on these Parkinson's symptoms: {symptom_text}. "
                        "Provide a general overview of impulse control disorders (ICD) in the context of Parkinson's disease. "
                        "Provide 2–3 practical, balanced suggestions. "
                        "Focus on general wellness and common management strategies. "
                        "Avoid clinical language and keep the tone reassuring and clear."
                    )

                    # ---- LLM generation timing (non-streaming)
                    with span("insights_llm_generation", page="impulse_control"):
                        try:
                            insights = await minerva_agent.run(
                                query,
                                deps=MINERVADependencies(minerva_client=minerva)
                            )
                            st.markdown("### Suggestions for You")
                            st.markdown(insights.output)
                        except Exception as e:
                            st.error("Sorry, I encountered an error while generating insights. Please try again later.")
                            st.error(str(e))
        

    with tab3:
        st.header("Research Insights")
        
        # Only query papers when the user submits their query
        user_query = st.text_input("Enter your question about impulse control disorders:")
        if st.button("Get Answer"):
            if user_query:
                with st.spinner('Getting answer...'):
                    answer = minerva.query_papers(user_query)
                st.markdown("### Research Insights")
                st.markdown(answer)
