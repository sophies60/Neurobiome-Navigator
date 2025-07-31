import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from minerva import MINERVA
from components.graph_queries import GraphQueries
import plotly.graph_objects as go
from streamlit_agraph import agraph, Node, Edge, Config

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
            st.markdown("<p style='color: #4a5568; margin-bottom: 10px; font-size: 0.95rem;'>Select from the most influential microbiomes linked to Parkinson's Disease:</p>", unsafe_allow_html=True)
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
        st.header("🍽️ Dietary Insights")
        
        # Main description
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
        This section shows how different foods may influence Parkinson's Disease risk through their effects on gut bacteria.
        </div>
        """, unsafe_allow_html=True)
        
        # Create two columns for the info boxes
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("🔍 Understanding Food Types", expanded=True):
                st.markdown("""
                <div style="background-color: #e8f5e9; padding: 12px; border-radius: 8px; border-left: 4px solid #4caf50;">
                <h4 style="margin-top: 0; color: #2e7d32;">🛡️ Protective Foods</h4>
                <p style="margin-bottom: 0;">Promote beneficial microbes or inhibit harmful ones associated with Parkinson's.</p>
                </div>
                <div style="margin-top: 10px; background-color: #ffebee; padding: 12px; border-radius: 8px; border-left: 4px solid #f44336;">
                <h4 style="margin-top: 0; color: #c62828;">⚠️ Risk Foods</h4>
                <p style="margin-bottom: 0;">May promote microbes linked to Parkinson's or reduce beneficial ones.</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            with st.expander("📊 Understanding Strength Values", expanded=True):
                st.markdown("""
                <div style="background-color: #e3f2fd; padding: 12px; border-radius: 8px; border-left: 4px solid #2196f3;">
                <p style="margin: 5px 0;"><b>Negative Values (🛡️):</b> More protective</p>
                <p style="margin: 5px 0;"><b>Positive Values (⚠️):</b> More risky</p>
                <p style="margin: 5px 0 0 0;"><small>Higher absolute value = stronger relationship</small></p>
                </div>
                """, unsafe_allow_html=True)
        
        # Add a visual indicator
        st.markdown("""
        <div style="display: flex; justify-content: space-between; margin: 10px 0 20px 0; padding: 0 20px;">
            <div style="text-align: center;">
                <div style="font-size: 24px;">🛡️</div>
                <div>More Protective</div>
            </div>
            <div style="flex-grow: 1; margin: 15px 10px 0; height: 6px; background: linear-gradient(90deg, #4caf50, #f44336); border-radius: 3px;"></div>
            <div style="text-align: center;">
                <div style="font-size: 24px;">⚠️</div>
                <div>More Risky</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
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
            return disease_food_relations, connection_error

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
                    
                    # Display foods in two columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 🛡️ Top 5 Protective Foods")
                        if not protective_foods.empty:
                            for _, row in protective_foods.iterrows():
                                food = row['food_name']
                                strength = abs(row['food_disease_strength'])
                                if st.button(f"{food} (Strength: {strength:.2f})", 
                                           key=f"protect_{food}",
                                           help=f"Click to see details about {food}"):
                                    st.session_state.selected_food = food
                        else:
                            st.info("No protective foods found.")
                    
                    with col2:
                        st.markdown("### ⚠️ Top 5 Risk Foods")
                        if not risk_foods.empty:
                            for _, row in risk_foods.iterrows():
                                food = row['food_name']
                                strength = abs(row['food_disease_strength'])
                                if st.button(f"{food} (Strength: {strength:.2f})",
                                           key=f"risk_{food}",
                                           help=f"Click to see details about {food}"):
                                    st.session_state.selected_food = food
                        else:
                            st.info("No risk foods found.")
                    
                    # Add a divider
                    st.markdown("---")
                    
                    # Display knowledge graph when a food is selected
                    if 'selected_food' in st.session_state and st.session_state.selected_food:
                        selected_food = st.session_state.selected_food
                        food_relations = disease_food_relations[
                            disease_food_relations["food_name"] == selected_food
                        ]
                        
                        if not food_relations.empty:
                            st.markdown(f"""
                            <h2 style='text-align: center; color: #4B0082; background: linear-gradient(90deg, #FF6B6B, #4ECDC4); 
                            padding: 10px; border-radius: 10px;'>
                                🍽️ {selected_food} - Microbiome Relationship
                            </h2>
                            """, unsafe_allow_html=True)
                            
                            # Create interactive knowledge graph
                            # Calculate if the food is protective overall
                            if not food_relations.empty:
                                # Define top protective and risk foods
                                protective_foods = [
                                    'dietary fiber',
                                    'cultured milk products',
                                    'yogurt',
                                    'adult high protein high fiber formula',
                                    'almond nut'
                                ]
                                
                                risk_foods = [
                                    'nitrogen',
                                    'saturated fats',
                                    'red meats',
                                    'raw foods',
                                    'meat'
                                ]
                                
                                # Count positive and negative relations for the description
                                positive_relations = (food_relations['derived_relation'] == 'positive').sum()
                                total_relations = len(food_relations)
                                
                                # Determine if food is in our known lists (case insensitive)
                                food_lower = selected_food.lower()
                                is_protective = any(food in food_lower for food in protective_foods)
                                is_risk = any(food in food_lower for food in risk_foods)
                                
                                # If not in either list, use the calculated score as fallback
                                if not is_protective and not is_risk and total_relations > 0:
                                    food_relations['combined_strength'] = (
                                        food_relations['food_microbe_strength'] * 
                                        food_relations['microbe_disease_strength']
                                    )
                                    positive_score = food_relations[food_relations['derived_relation'] == 'positive']['combined_strength'].sum()
                                    negative_score = abs(food_relations[food_relations['derived_relation'] == 'negative']['combined_strength'].sum())
                                    is_protective = positive_score >= (negative_score * 0.7)
                                
                                # Special case for known protective foods
                                known_protective_foods = [
                                    'dietary fiber', 'fiber', 'whole grain', 'olive oil', 
                                    'berries', 'leafy greens', 'fermented foods', 'probiotics'
                                ]
                                
                                # If the food name contains any known protective terms, prioritize that
                                if any(food.lower() in selected_food.lower() for food in known_protective_foods):
                                    is_protective = True
                                
                                # Create a colorful description
                                protection_text = "protective against" if is_protective else "a potential risk factor for"
                                protection_color = "#4CAF50" if is_protective else "#F44336"
                                
                                # Food description with emoji and styling
                                st.markdown(f"""
                                <div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px; 
                                border-left: 5px solid {protection_color}; margin: 15px 0;'>
                                    <h4 style='color: {protection_color}; margin-top: 0;'>
                                        {'🛡️' if is_protective else '⚠️'} 
                                        {selected_food} appears to be {protection_text} Parkinson's Disease
                                    </h4>
                                    <p>
                                        Based on the analysis of {total_relations} microbe relationships, 
                                        {selected_food} has {positive_relations} ({positive_relations/total_relations:.0%}) 
                                        positive associations with gut microbes that influence Parkinson's Disease.
                                    </p>
                                </div>
                                
                                <div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin: 15px 0; border-left: 5px solid #4CAF50;'>
                                    <h4 style='color: #4CAF50; margin-top: 0;'>🛡️ Protective Foods</h4>
                                    <p>Promote beneficial microbes or inhibit harmful ones associated with Parkinson's.</p>
                                </div>
                                
                                <div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin: 15px 0; border-left: 5px solid #F44336;'>
                                    <h4 style='color: #F44336; margin-top: 0;'>⚠️ Risk Foods</h4>
                                    <p>May promote microbes linked to Parkinson's or reduce beneficial ones.</p>
                                </div>
                                
                                <div style='background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin: 15px 0;'>
                                    <h4 style='color: #1976D2; margin-top: 0;'>📊 Understanding Strength Values</h4>
                                    <ul style='margin-bottom: 0;'>
                                        <li><strong>Negative Values (🛡️)</strong>: More protective</li>
                                        <li><strong>Positive Values (⚠️)</strong>: More risky</li>
                                        <li><strong>Higher absolute value</strong> = stronger relationship</li>
                                    </ul>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown(f"<h4 style='text-align: center; margin-top: 20px;'>Microbial Relationships for {selected_food}</h4>", unsafe_allow_html=True)
                            
                            # Hardcoded CUI for Parkinson's Disease from UMLS
                            PARKINSONS_CUI = "C0030567"
                            
                            # Query to find the selected food and its directly connected microbiomes
                            query = """
                            // Find the food by name (case insensitive partial match)
                            MATCH (f:Food)
                            WHERE toLower(f.official_name) CONTAINS toLower($food_name) 
                               OR toLower(f.name) CONTAINS toLower($food_name)
                            
                            // Find all directly connected microbiomes (1 hop)
                            MATCH (f)-[r]-(m:Microbe)
                            RETURN 
                                f.name as food_name,
                                f.official_name as food_official_name,
                                collect(DISTINCT {
                                    microbe: m.name,
                                    microbe_id: m.id,
                                    relationship: type(r),
                                    strength: r.strength_raw
                                }) as microbiomes
                            """
                            
                            try:
                                # Execute the query
                                graph_queries = GraphQueries()
                                
                                # Run the query to get food and its microbiomes
                                with st.spinner('Loading food-microbiome relationships...'):
                                    result = graph_queries.graph.run(query, 
                                                                   food_name=selected_food).data()
                                    
                                    if not result or not result[0].get('microbiomes'):
                                        st.warning(f"No microbiome data found for {selected_food}")
                                        # No need for return here, as the outer function continues.
                                        # The rest of the inner try block will be skipped.
                                    else:
                                        # Removed the Food-Microbiome Relationships text
                                        
                                        microbe_data = []
                                        for _, row in food_relations.iterrows():
                                            # Get strength values and determine relation type based on sign
                                            food_strength = row.get("food_microbe_strength", 0)
                                            disease_strength = row.get("microbe_disease_strength", 0)
                                            
                                            microbe_data.append({
                                                "Microbe": row.get("microbe_name", "N/A"),
                                                "Food-Microbe Strength": f"{food_strength:.2f}",
                                                "Microbe-Disease Strength": f"{disease_strength:.2f}",
                                                "Overall Derived Relation": "Positive" if row.get("derived_relation") == "positive" else "Negative"
                                            })
                                        
                                        # Display microbe data in a table
                                        st.dataframe(microbe_data, use_container_width=True)
                            except Exception as e:
                                st.error(f"An error occurred while loading microbe data: {e}")
                            
                            # Add a small space after the table
                            st.markdown("\n")

                else:
                    st.info("No disease-food relations found for Parkinson's disease.")
                    
                    # Add a divider
                    st.markdown("---")
                    
                    # Show detailed view for selected food
                    st.markdown("### 🔍 Food Details")
                    
                    # Create a dropdown to select a food
                    try:
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
                            try:
                                microbe_data = []
                                for _, row in food_relations.iterrows():
                                    microbe_data.append({
                                        "Microbe": row.get("microbe_name", "N/A"),
                                        "Food-Microbe Strength": f"{row.get('food_microbe_strength', 0):.2f}" if 'food_microbe_strength' in row else "N/A",
                                        "Microbe-Disease Strength": f"{row.get('microbe_disease_strength', 0):.2f}" if 'microbe_disease_strength' in row else "N/A",
                                        "Relationship Type": row.get("derived_relation", "N/A").capitalize()
                                    })
                                
                                # Display the table if we have data
                                if microbe_data:
                                    st.dataframe(pd.DataFrame(microbe_data), use_container_width=True)
                                    
                                    # Show detailed microbe information
                                    st.markdown("#### Detailed Microbe Information")
                                    for _, row in food_relations.iterrows():
                                        try:
                                            st.markdown(f"**Microbe:** {row.get('microbe_name', 'N/A')}")
                                            
                                            # Safely get food relation data
                                            food_rel = row.get('food_microbe_relation', 'No relation data')
                                            food_str = f"{row.get('food_microbe_strength', 0):.2f}" if 'food_microbe_strength' in row else 'N/A'
                                            st.markdown(f"**Food Relation:** {food_rel} (Strength: {food_str})")
                                            
                                            # Safely get disease relation data
                                            disease_rel = row.get('microbe_disease_relation', 'No relation data')
                                            disease_str = f"{row.get('microbe_disease_strength', 0):.2f}" if 'microbe_disease_strength' in row else 'N/A'
                                            st.markdown(f"**Disease Relation:** {disease_rel} (Strength: {disease_str})")
                                            
                                            # Safely get derived relation
                                            derived = row.get('derived_relation', 'No derived relation data')
                                            st.markdown(f"**Overall Derived Relation:** {derived}")
                                            st.markdown("---")
                                        except Exception as e:
                                            st.error(f"Error displaying detailed microbe data: {str(e)}")
                                            st.exception(e)
                                            st.markdown("---")
                                else:
                                    st.warning("No microbe relationship data available for the selected food.")
                            except Exception as e:
                                st.error(f"Error creating microbe relationship table: {str(e)}")
                                st.exception(e)
                    except Exception as e:
                        st.error(f"An error occurred while loading food details: {str(e)}")
                        st.exception(e)
            except Exception as e:
                st.error(f"An error occurred while fetching dietary insights: {e}")
            
            # Research-Based Dietary Summary
            st.markdown("---")
            st.markdown("## 🎯 Dietary Recommendations Summary")
            
            st.markdown("""
            <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #6c63ff; line-height: 1.6;'>
            <p>For optimal gut health and potential Parkinson's Disease management, focus on a <b>whole food, plant-based diet</b> rich in fiber, antioxidants, and healthy fats. Include plenty of colorful fruits, vegetables, whole grains, and omega-3 sources like fatty fish and flaxseeds. Fermented foods like yogurt and kefir can support a healthy gut microbiome. Limit processed foods, red meats, and added sugars, which may promote inflammation and disrupt gut bacteria balance. A Mediterranean-style eating pattern has shown particular promise in research for supporting brain health.</p>
            <p style='margin: 10px 0 0 0; font-size: 0.9em; color: #555;'><i>Note: Individual responses may vary. Consult with a healthcare provider for personalized dietary advice.</i></p>
            </div>
            """, unsafe_allow_html=True)
  
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