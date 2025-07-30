import streamlit as st
import pandas as pd
import plotly.express as px
from minerva import MINERVA
from components.graph_queries import GraphQueries
import plotly.graph_objects as go

# Dictionary of microbiome descriptions
MICROBIOME_DESCRIPTIONS = {
    "Lachnospiraceae": "This bacterial family is consistently found in lower abundances in the gut microbiota of Parkinson's Disease (PD) patients compared to healthy controls. A decreased abundance of Lachnospiraceae has been positively correlated with increased disease severity, including postural instability, gait disturbances, and cognitive impairment in PD patients. It is also categorized as an 'anti-inflammatory' bacterium, and its reduced presence in PD cohorts is thought to contribute to pro-inflammatory gut dysbiosis observed in the condition.",
    "Faecalibacterium": "In individuals with Parkinson's Disease (PD), Faecalibacterium is typically observed at lower abundances in the gut microbiota compared to healthy individuals. A decreased presence of this beneficial bacterium has been linked to increased PD disease severity. Faecalibacterium is considered an 'anti-inflammatory' bacterium and is among the short-chain fatty acid (SCFA)-producing genera whose reduced levels are associated with accelerated disease progression in early PD.",
    "Blautia": "Blautia is a genus found in lower abundances in the gut microbiota of Parkinson's Disease (PD) patients when compared to healthy individuals. Its decreased presence is associated with greater disease severity in PD. Blautia is classified as an 'anti-inflammatory' bacterium, and its reduction in PD patients contributes to the pro-inflammatory gut dysbiosis observed in the condition. Furthermore, it is a short-chain fatty acid (SCFA)-producing genus whose diminished levels are linked to accelerated disease progression in early PD.",
    "Prevotella": "The relationship of Prevotella with Parkinson's Disease (PD) appears to vary depending on the body site. In the gut microbiota of PD patients, Prevotella is generally found in lower abundances, with its deficiency correlating with impaired mucin production, increased gut permeability, and disease progression. Hydrogen-generating Prevotella has also been negatively correlated with disease severity in PD. In contrast, in the oral cavity of PD patients, the family Prevotellaceae, including species like P. intermedia, P. histicola, and P. melaninogenica, is frequently cited for its higher abundance. This increased oral presence, which contrasts with its decrease in the gut, may be linked to opportunistic pathogens due to oral hygiene deficiencies associated with PD's motor and non-motor symptoms. Porphyromonas gingivalis, a notable member of this family, is implicated in promoting systemic inflammation, disrupting the blood-brain barrier via secreted gingipains, and potentially contributing to neurodegenerative processes and cognitive decline in PD. While Prevotella has been observed in human blood and gut microbiomes, it was only significantly correlated between the two in the PTSD cohort in one study, and not in PD.",
    "Enterobacteriaceae": "Enterobacteriaceae is a bacterial family found in higher abundances in the gut microbiota of Parkinson's Disease (PD) patients compared to healthy controls. Its increased presence has been consistently linked to higher disease severity in PD, showing positive correlations with postural instability, gait disturbances, and overall PD duration.",
    "Bifidobacterium": "While the sources do not directly link Bifidobacterium to changes in PD incidence, it is recognized as a beneficial bacterium within the gut microbiota. Preclinical studies indicate that probiotic strains such as Bifidobacterium breve demonstrate neuroprotective effects in Parkinson's Disease (PD) mouse models by enhancing intestinal barrier integrity and alleviating pathological progression. This suggests a potential role for Bifidobacterium in therapeutic strategies aimed at modulating the gut microbiota in PD.",
    "Akkermansia": "Akkermansia is a genus found in higher abundances in the gut microbiota of Parkinson's Disease (PD) patients. This mucin-degrading genus has been linked to accelerated disease progression in early PD. Studies further indicate that an increase in Akkermansia can contribute to heightened intestinal permeability, which may expose neurons to oxidative conditions that favor the aggregation of alpha-synuclein, a hallmark of PD pathology.",
    "Lactobacillus": "Lactobacillus exhibits a complex association with Parkinson's Disease (PD). In the gut microbiota of PD patients, certain species of Lactobacillus have been reported to be present in higher abundances. Specifically, Lactobacillus reuteri, found in the mouth and gut, has been suggested to increase the release of alpha-synuclein in the enteric nervous system, and its elevation in PD patients is positively correlated with slowed movement. However, particular probiotic strains of Lactobacillus, such as Lactobacillus plantarum DP189 and PS128, have demonstrated beneficial effects in PD models, including suppressing oxidative stress, restoring microbial diversity, decreasing alpha-syn aggregation, alleviating motor deficits, and improving quality of life in PD patients. Although Lactobacillus has been observed in human blood and in irritable bowel disease, its detection in the blood of PD cases in one study was attributed to contamination or individual factors due to very low read counts.",
    "Enterococcus": "Enterococcus is a genus observed in higher abundances in the gut microbiota of Parkinson's Disease (PD) patients. Beyond the gut, Enterococcus has been reported in the human gut microbiome and is associated with the potential for translocation into the bloodstream, which could lead to bacteremia. In the context of a study correlating gut and blood microbiomes across neuropsychiatric disorders, Enterococcus was found to be present in both environments in the Schizophrenia cohort, but its abundance between the two sites was not significantly correlated.",
    "Desulfovibrio": "Desulfovibrio is a genus that, in the context of Parkinson's Disease (PD) mouse models, was found to have its abundance decreased following fecal microbiota transplantation (FMT) treatment. This suggests that Desulfovibrio may have been present in elevated or undesirable levels in the PD model before the intervention, indicating a potential association with the disease state that FMT aims to alleviate."
}

def create_gut_insight_navigator():
    """
    Create the Gut Insight Navigator page that shows relationships between gut microbes and Parkinson's disease.
    """
    st.title("Gut Insight Navigator")
    
    # Initialize GraphQueries and MINERVA
    querier = GraphQueries()
    minerva = MINERVA()
    
    # Load papers if not already loaded
    if not hasattr(minerva, 'research_embeddings'):
        with st.spinner('Loading research papers...'):
            minerva.load_research_papers("research_papers")
    
    # Introductory context 
    st.markdown("""Your gut is home to a vast community of tiny living things, the gut microbiome, which constantly communicates with your brain through a vital "gut microbiota-gut-brain axis". In Parkinson's Disease (PD), an imbalance in these gut microbes, called "gut dysbiosis," is strongly linked to how the disease starts and progresses, affecting symptoms, duration, and severity. This imbalance can contribute to PD by causing a "leaky gut" (increased intestinal permeability), leading to widespread inflammation (including in the brain), encouraging the clumping of alpha-synuclein (α-syn) protein, increasing oxidative stress, and reducing the production of important brain chemicals (neurotransmitters) like dopamine and serotonin. Because of these strong connections, targeting the gut microbiome through approaches like Fecal Microbiota Transplantation (FMT), which aims to restore a healthy balance, is being explored as a promising new therapy for PD.""")

    # Create tabs first to ensure they're available throughout the function
    tab1, tab2, tab3 = st.tabs(["Microbiome Insights", "Dietary Insights", "Research Insights"])

    # Content for tab1 (Microbiome Insights)
    with tab1:
        st.header("Microbiome Insights")
        
        # List of specific microbiomes related to gut and Parkinson's disease
        specific_microbiomes = [
            "Lachnospiraceae",
            "Faecalibacterium",
            "Blautia",
            "Prevotella",
            "Enterobacteriaceae",
            "Bifidobacterium",
            "Akkermansia",
            "Lactobacillus",
            "Enterococcus",
            "Desulfovibrio"
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

        # Microbiome selection
        st.markdown("""
        <h3>Select up to 4 microbiomes to analyze:</h3>
        """, unsafe_allow_html=True)
        
        # Create columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
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


                
    
    # Content for tab2 (Dietary Insights)
    with tab2:
        st.header("Dietary Insights")
        st.markdown("""
        This section shows the top foods that may influence Parkinson's Disease risk through their effects on gut microbiota.
        """)
        
        # Initialize default values
        disease_food_relations = pd.DataFrame()
        connection_error = False
        
        # Test database connection
        try:
            # Test the connection first
            test_query = "MATCH (n) RETURN count(n) AS count LIMIT 1"
            querier.graph.run(test_query).to_data_frame()
        except Exception as e:
            st.error("⚠️ Could not connect to the knowledge graph database.")
            st.warning("Please ensure the Neo4j database is running and properly configured.")
            connection_error = True
        
        # Only proceed with queries if connection is successful
        if not connection_error:
            try:
                # Use Parkinson's disease CUI
                parkinsons_cui = "C0030567"
                
                # Get disease-food relations for Parkinson's disease
                disease_food_relations = querier.get_disease_food_relations(parkinsons_cui)
                
                if disease_food_relations is not None and not disease_food_relations.empty:
                    # Calculate food-disease strength
                    disease_food_relations["food_disease_strength"] = (
                        disease_food_relations["food_microbe_strength"].abs() +
                        disease_food_relations["microbe_disease_strength"].abs()
                    ) * disease_food_relations["derived_relation"].apply(lambda x: 1 if x=="positive" else -1)
                    
                    # Group by food name and calculate total strength
                    food_strengths = disease_food_relations.groupby("food_name").agg({
                        "food_disease_strength": "sum"
                    }).reset_index()
                
                    # Get top protective and risk foods (top 5 each)
                    protective_foods = food_strengths[food_strengths["food_disease_strength"] < 0]\
                        .sort_values("food_disease_strength", ascending=True)\
                        .head(5)
                    risk_foods = food_strengths[food_strengths["food_disease_strength"] > 0]\
                        .sort_values("food_disease_strength", ascending=False)\
                        .head(5)
                    
                    # Display in two columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 🛡️ Top 5 Protective Foods")
                        if not protective_foods.empty:
                            for _, row in protective_foods.iterrows():
                                food = row['food_name']
                                strength = abs(row['food_disease_strength'])
                                st.markdown(f"""
                                <div style='margin-bottom: 15px; padding: 10px; background-color: #e6f7e6; border-radius: 5px;'>
                                    <strong>{food}</strong><br>
                                    <small>Protective Strength: {strength:.2f}</small>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No protective foods found.")
                    
                    with col2:
                        st.markdown("### ⚠️ Top 5 Risk Foods")
                        if not risk_foods.empty:
                            for _, row in risk_foods.iterrows():
                                food = row['food_name']
                                strength = row['food_disease_strength']
                                st.markdown(f"""
                                <div style='margin-bottom: 15px; padding: 10px; background-color: #ffebee; border-radius: 5px;'>
                                    <strong>{food}</strong><br>
                                    <small>Risk Strength: {strength:.2f}</small>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No risk foods found.")
                    
                    # Add a divider
                    st.markdown("---")
                    
                    # Show detailed view for selected food
                    st.markdown("### 🔍 Food Details")
                    
                    # Create a dropdown to select a food
                    all_foods = disease_food_relations["food_name"].unique().tolist()
                    selected_food = st.selectbox("Select a food to view detailed relationships:", [""] + all_foods)
                    
                    if selected_food:
                        # Get all microbe relationships for the selected food
                        food_relations = disease_food_relations[disease_food_relations["food_name"] == selected_food]
                        
                        # Calculate total strength for this food
                        total_strength = food_relations["food_disease_strength"].sum()
                        relation_type = "Protective" if total_strength < 0 else "Risk"
                        
                        # Display summary
                        st.markdown(f"""
                        <div style='padding: 15px; background-color: #f5f5f5; border-radius: 5px; margin-bottom: 20px;'>
                            <h4>{selected_food}</h4>
                            <p><strong>Overall Effect:</strong> {relation_type} (Strength: {abs(total_strength):.2f})</p>
                            <p><strong>Mechanism:</strong> This food influences {len(food_relations)} different microbes associated with Parkinson's Disease.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display detailed microbe relationships
                        st.markdown("#### Microbe Relationships")
                        
                        # Create a table with microbe relationships
                        microbe_data = []
                        for _, row in food_relations.iterrows():
                            microbe_data.append({
                                "Microbe": row["microbe_name"],
                                "Food-Microbe Strength": row["food_microbe_strength"],
                                "Microbe-Disease Strength": row["microbe_disease_strength"],
                                "Relationship Type": row["derived_relation"].capitalize()
                            })
                        
                        # Display the table
                        st.table(pd.DataFrame(microbe_data))
                else:
                    st.info("No food relationships found for Parkinson's Disease.")
                    
            except Exception as e:
                st.error(f"Error loading dietary insights: {str(e)}")
                st.exception(e)
        
        # Always show general recommendations
        st.markdown("---")
        st.subheader("General Dietary Recommendations for Parkinson's Disease")
        st.info("""
        While we couldn't connect to the detailed database, here are some evidence-based dietary recommendations:
        
        **Protective Foods:**
        - Omega-3 rich foods (fatty fish, flaxseeds, walnuts, chia seeds)
        - Antioxidant-rich fruits and vegetables (berries, leafy greens, bell peppers)
        - Whole grains (oats, quinoa, brown rice)
        - Nuts and seeds (almonds, walnuts, chia seeds)
        - Green tea and turmeric for their anti-inflammatory properties
        
        **Foods to Limit:**
        - Processed foods high in sugar and unhealthy fats
        - Excessive red meat consumption
        - Dairy products (some studies suggest a potential link)
        - Foods high in advanced glycation end products (AGEs)
        
        **General Tips:**
        - Stay hydrated throughout the day
        - Eat smaller, more frequent meals if experiencing appetite changes
        - Consider working with a dietitian for personalized advice
        - Monitor how different foods affect your symptoms
        """)
        
    with tab3:
        st.header("Research Insights")
        
        # Add user query section
        st.subheader("Ask a Question")
        user_query = st.text_input("Enter your question about gut microbiome and Parkinson's disease:")
        
        if st.button("Get Answer"):
            if user_query:
                with st.spinner('Getting answer...'):
                    answer = minerva.query_papers(user_query)
                st.markdown(answer)