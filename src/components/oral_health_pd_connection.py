import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from minerva import MINERVA
from agent import minerva_agent, MINERVADependencies
import asyncio
from .survey import SurveyManager, SurveyType

MICROBIOME_DESCRIPTIONS = {
    "Streptobacillaceae": (
        "The family Streptobacillaceae, which includes species like *Streptococcus mutans* and *Streptococcus anginosus*, "
        "shows elevated abundance in the oral cavity of Parkinson's Disease (PD) patients. *Streptococcus mitis*, a common "
        "commensal, participates in biofilm formation, but an overgrowth of pathogenic species like *S. mutans* is linked to "
        "oral diseases such as periodontitis and caries. Streptococcus has been implicated in systemic conditions including "
        "irritable bowel disease and aortic aneurysms, and may act as a contaminant in microbiome analyses. Its presence has "
        "been observed in both oral and gut microbiomes in alcohol dependence studies, suggesting potential oral-gut-brain interactions."
    ),
    "Lactobacillaceae": (
        "Frequently cited as abundant in the oral microbiota of PD patients, the Lactobacillaceae family includes *Lactobacillus reuteri*, "
        "which has been linked to increased alpha-synuclein release in the enteric nervous system. *L. reuteri* is significantly elevated in PD "
        "patients and positively correlated with slowed movement. Though detected in both gut and blood microbiomes, its presence in blood is rare and "
        "may reflect contamination. Lactobacillus has also been associated with oxidative phosphorylation and increased intestinal permeability."
    ),
    "Prevotellaceae": (
        "This family, including *Prevotella intermedia*, *P. histicola*, and *P. melaninogenica*, is often found in greater abundance in the oral cavity "
        "of PD patients. Interestingly, this increase is sometimes accompanied by a decrease in gut Prevotella, which is linked to impaired mucin production "
        "and leaky gut. While common in the oral microbiome, Prevotellaceae may become pathogenic and contribute to systemic inflammation. Their elevated oral "
        "presence in PD may stem from poor oral hygiene due to motor and cognitive symptoms."
    ),
    "Veillonellaceae": (
        "*Veillonella parvula*, a member of the Veillonellaceae family, is found in higher abundance in the oral microbiota of PD patients. Typically a commensal, "
        "its elevated presence in PD may indicate a pathological role. In animal studies, *V. parvula* has been shown to exacerbate PD by promoting T-helper 1 (Th1) "
        "cell infiltration, suggesting a pro-inflammatory mechanism of action."
    ),
    "Porphyromonas gingivalis": (
        "A key pathogen in oral diseases like periodontitis, *P. gingivalis* is implicated in systemic inflammation and neurodegeneration in PD. Its gingipain enzymes "
        "degrade neuronal proteins and compromise the blood-brain barrier. Two proposed mechanisms of action include: (1) bloodstream entry triggering beta-amyloid production "
        "and neuroinflammation; (2) gut colonization leading to dysbiosis, inflammation, and α-synuclein accumulation that travels via the vagus nerve. *P. gingivalis* is also "
        "linked to Alzheimer's Disease, cancer, and cardiovascular diseases, highlighting its systemic pathogenic potential."
    )
}


async def create_oral_health_pd_connection():
    """Create the Oral Health & PD Connection dashboard"""
    st.title("Oral Health & Parkinson's Disease")
    
    # Initialize MINERVA client
    minerva = MINERVA()
    
    # Load research papers
    try:
        minerva.load_research_papers("research_papers")
    except Exception as e:
        st.error(f"Error loading research papers: {str(e)}")
        st.error("Please ensure the research_papers directory exists and contains PDF files.")
        st.stop()
    
    # Get introductory context using the agent
    st.markdown("""Your mouth, acting as a gateway to your body, hosts a diverse community of microbes. When this balance is disrupted, it leads to oral dysbiosis, a condition increasingly recognized as a risk factor for worsening Parkinson's Disease (PD), though not its direct cause. This imbalance can influence both the onset of PD and the progression of symptoms like cognitive decline. Harmful bacteria, such as Porphyromonas gingivalis, commonly linked to gum disease, can promote widespread inflammation throughout your body and potentially affect your brain by disrupting the blood-brain barrier. Oral bacteria can also travel to your gut via saliva, altering its microbial balance and further influencing the gut-brain axis. Studies in PD patients often show a higher presence of certain oral bacteria like Streptobacillaceae, Lactobacillaceae, and Prevotellaceae, which might be partly due to oral hygiene challenges faced by PD patients. This highlights the importance of good oral hygiene as a potential strategy in managing PD.""")



    # Add description
    st.markdown("""
    Complete the oral health assessment below to receive personalized insights based on your responses.
    """)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Microbiome Insights", "Oral Health Assessment", "Research Insights"])
    
    # Add custom CSS for expanders
    st.markdown("""
    <style>
    /* Base expander style */
    div[data-testid="stExpander"] {
        margin-bottom: 1rem;
    }
    
    /* Expander header */
    div[data-testid="stExpander"] > div[role="button"] {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%) !important;
        border-radius: 8px !important;
        padding: 0.8rem 1.2rem !important;
        margin: 0.5rem 0 !important;
        border: 1px solid #bae6fd !important;
        transition: all 0.2s ease !important;
    }
    
    /* Expander header text */
    div[data-testid="stExpander"] > div[role="button"] > div {
        font-size: 1.2em !important;
        font-weight: 600 !important;
        color: #0369a1 !important;
    }
    
    /* Hover effect */
    div[data-testid="stExpander"] > div[role="button"]:hover {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.1) !important;
    }
    
    /* First expander style */
    div[data-testid="stExpander"]:nth-of-type(1) > div[role="button"] {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%) !important;
        border-color: #86efac !important;
    }
    
    div[data-testid="stExpander"]:nth-of-type(1) > div[role="button"] > div {
        color: #15803d !important;
    }
    
    /* Expander content */
    div[data-testid="stExpander"] > div[data-testid="stExpanderContent"] {
        border: 1px solid #e0f2fe !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        margin: -0.5rem 0 1rem 0 !important;
        padding: 1.2rem !important;
        background-color: #f8fafc !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with tab1:
        st.header("Microbiome Insights")
        
        # List of specific microbiomes related to oral health and Parkinson's disease
        specific_microbiomes = [
            "Streptobacillaceae",
            "Lactobacillaceae",
            "Prevotellaceae",
            "Veillonellaceae",
            "Porphyromonas gingivalis"
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
            st.markdown("<p style='color: #4a5568; margin-bottom: 10px; font-size: 0.95rem;'>Select from the most influential oral microbiomes linked to Parkinson's Disease:</p>", unsafe_allow_html=True)
            selected_microbes = st.multiselect(
                "Select Microbiomes",
                options=specific_microbiomes,
                default=[specific_microbiomes[0]],
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

        # First expander with custom class
        with st.expander("🧠 Mechanisms of Influence"):
            st.markdown("""
            - **Systemic and Neuroinflammation**:  
            Pathogens like *Porphyromonas gingivalis* secrete gingipains that degrade essential neuronal proteins and disrupt the blood-brain barrier (BBB), allowing inflammatory mediators and pathogens to access the brain, exacerbating neuroinflammation.

            - **α-Synuclein Aggregation**:  
            *P. gingivalis* can also enter the gut, inducing dysbiosis and inflammation, which leads to abnormal α-synuclein accumulation. This aggregation may then spread to the brain via the vagus nerve.

            - **Cognitive Decline**:  
            Oral dysbiosis—especially from periodontal disease—can contribute to cognitive decline in neurodegenerative diseases such as Parkinson's and Alzheimer's. This is due to elevated cerebral pro-inflammatory mediators and increased amyloid deposition.
            """)

        # Second expander with custom class
        with st.expander("⚕️ Implications for Parkinson's Disease Management"):
            st.markdown("""
            - These findings suggest that **oral hygiene** and **oral microbiome composition** may play a significant role in the progression of PD.  
            - Regular **periodontal care**, **monitoring of oral microbial profiles**, and **targeted probiotics or anti-inflammatory interventions** might be beneficial.  
            - Future treatment strategies could incorporate **oral microbiome screening** as a non-invasive biomarker for disease monitoring.
            """)
    
    with tab2:
        st.header("Oral Health Symptoms")
        
        st.subheader("Common Oral Symptoms")
        
        # Oral symptoms questions with sliders (0-5 scale)
        bleeding = st.slider("How often do you experience bleeding gums?", 0, 5, 0, help="0 = Never, 5 = Always")
        dry_mouth = st.slider("How often do you experience dry mouth?", 0, 5, 0, help="0 = Never, 5 = Always")
        bad_breath = st.slider("How often do you experience bad breath?", 0, 5, 0, help="0 = Never, 5 = Always")
        tooth_sensitivity = st.slider("How often do you experience tooth sensitivity?", 0, 5, 0, help="0 = Never, 5 = Always")
        mouth_pain = st.slider("How often do you experience mouth pain or discomfort?", 0, 5, 0, help="0 = Never, 5 = Always")
        
        # Only show graph and insights after submission
        if st.button("Submit Survey"):
            with st.spinner('Analyzing your symptoms...'):
                # Store survey responses in a dictionary for easy reference
                survey_responses = {
                    'Bleeding Gums': bleeding,
                    'Dry Mouth': dry_mouth,
                    'Bad Breath': bad_breath,
                    'Tooth Sensitivity': tooth_sensitivity,
                    'Mouth Pain': mouth_pain
                }
                
                # Save responses to session state
                survey_manager = SurveyManager()
                survey_manager.update_responses(SurveyType.ORAL_HEALTH, survey_responses)
                
                # Create a clean DataFrame with the survey responses in the original order
                symptom_order = ['Bleeding Gums', 'Dry Mouth', 'Bad Breath', 'Tooth Sensitivity', 'Mouth Pain']
                symptoms = pd.DataFrame({
                    'Symptom': symptom_order,
                    'Score': [survey_responses[symptom] for symptom in symptom_order]
                })
                
                # Ensure scores are integers
                symptoms['Score'] = symptoms['Score'].astype(int)
                
                st.subheader("Your Oral Health Symptom Profile")
                
                # Create a simple horizontal bar chart
                fig = go.Figure()
                
                # Add bars in the exact order of the symptoms in our DataFrame
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
                
                # Customize the layout
                fig.update_layout(
                    xaxis=dict(
                        title='Severity (0-5)',
                        tickvals=[0, 1, 2, 3, 4, 5],
                        ticktext=['0 (Never)', '1', '2', '3', '4', '5 (Always)'],
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
                        # Force the y-axis categories to be in the exact order of our symptom_order
                        categoryorder='array',
                        categoryarray=symptom_order[::-1]  # Reverse to match the order in the table
                    ),
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=300,
                    margin=dict(l=150, r=20, t=30, b=50),
                    hovermode='closest',
                    showlegend=False,
                    # Ensure bars are grouped by symptom
                    barmode='group'
                )
                
                # Add a title with severity scale explanation
                st.caption("Severity Scale: 0 = Never, 1 = Rarely, 2 = Sometimes, 3 = Often, 4 = Very Often, 5 = Always")
                
                # Display the chart
                st.plotly_chart(fig, use_container_width=True)

                  
                # Get personalized insights based on the survey responses
                st.markdown("### Personalized Insights")
                with st.spinner('Analyzing your responses and researching relevant findings...'):
                    # Get active symptoms (scores > 0) for the query
                    active_symptoms = {k: v for k, v in survey_responses.items() if v > 0}
                    
                    if not active_symptoms:
                        st.info("No significant symptoms reported. This is a positive sign!")
                        return
                        
                    # Create a simple, clear query for the AI agent
                    symptom_text = ", ".join([f"{k.lower()} (score: {v}/5)" for k, v in active_symptoms.items()])
                    
                    query = (
                        f"Based on these Parkinson's symptoms: {symptom_text}. "
                        "Provide a general overview of oral health symptoms in the context of Parkinson's disease. "
                        "Provide 2-3 practical, balanced suggestions. "
                        "Focus on general wellness and common management strategies. "
                        "Avoid clinical language and keep the tone reassuring and clear."
                    )   
                    
                    # Get insights from the AI agent
                    with st.spinner('Getting insights...'):
                        try:
                            # Initialize MINERVADependencies with the minerva client
                            insights = await minerva_agent.run(query, deps=MINERVADependencies(minerva_client=minerva))
                            # Display the insights in a clean format
                            st.markdown("### Suggestions for You")
                            st.markdown(insights.output)
                        except Exception as e:
                            st.error("Sorry, I encountered an error while generating insights. Please try again later.")
                            st.error(str(e))
                

        
    with tab3:
        st.header("Research Insights")
        
        # Add user query section
        st.subheader("Ask a Question")
        user_query = st.text_input("Enter your question about oral microbiomes and Parkinson's disease:")
        
        if st.button("Get Answer"):
            if user_query:
                with st.spinner('Getting answer...'):
                    answer = minerva.query_papers(user_query)
                st.markdown(answer)


if __name__ == "__main__":
    import asyncio
    asyncio.run(create_oral_health_pd_connection())
