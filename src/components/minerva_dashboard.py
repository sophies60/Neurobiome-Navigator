import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minerva import MINERVA

def create_minerva_dashboard():
    """Create the MINERVA dashboard"""
    st.title("MINERVA Dashboard")
    
    # Initialize MINERVA client
    minerva = MINERVA()
    
    # Load research papers
    try:
        minerva.load_research_papers("research_papers")
        st.success("Research papers loaded successfully")
    except Exception as e:
        st.error(f"Error loading research papers: {str(e)}")
    
    # Add diagnostic information
    st.subheader("Database Information")
    
    # Get schema information
    labels, rels, samples = minerva.get_schema()
    
    if labels is not None:
        st.write("### Labels in Database:")
        st.dataframe(labels)
        
        st.write("### Relationship Types:")
        st.dataframe(rels)
        
        st.write("### Sample Node Counts:")
        st.dataframe(samples)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Microbiome Analysis", "Risk Factors", "Statistics"])
    
    with tab1:
        st.header("Microbiome-PD Relationships")
        
        # Get Parkinson's Disease information
        try:
            pd_info = minerva.get_microbiome_info()
            if pd_info is not None and not pd_info.empty:
                st.write("### Parkinson's Disease Information:")
                st.dataframe(pd_info)
            else:
                st.write("No Parkinson's Disease information found in the database.")
        except Exception as e:
            st.error(f"Error querying Parkinson's Disease information: {str(e)}")

        # Get risk factors
        try:
            risk_factors = minerva.get_risk_factors()
            if risk_factors is not None and not risk_factors.empty:
                st.write("### Risk Factors:")
                st.dataframe(risk_factors)
            else:
                st.write("No risk factors found in the database.")
        except Exception as e:
            st.error(f"Error querying risk factors: {str(e)}")
        # Get all diseases using MINERVA's method
        try:
            all_diseases = minerva.get_all_diseases()
            if all_diseases.empty:
                st.warning("No diseases found in the database.")
                return
                
            # Create a dropdown selector for diseases
            selected_disease = st.selectbox(
                "Select a disease to analyze:",
                all_diseases['name'].tolist()
            )
            
            # Get disease-food relations using MINERVA's method
            try:
                disease_cui = all_diseases[all_diseases['name'] == selected_disease]['cui'].iloc[0]
                results = minerva.get_disease_food_relations(disease_cui)
                
                if not results.empty:
                    # Display table
                    st.subheader(f"Top Foods Associated with {selected_disease}")
                    st.dataframe(results)
                    
                    # Create visualization
                    fig = px.scatter(
                        results,
                        x='food_microbe_strength',
                        y='microbe_disease_strength',
                        color='derived_relation',
                        size='food_disease_strength',
                        hover_data=['food_name', 'microbe_name'],
                        title=f'Food-Microbe-{selected_disease} Relationships'
                    )
                    st.plotly_chart(fig)
                else:
                    st.warning(f"No data found for {selected_disease}.")
            except Exception as e:
                st.error(f"Error querying disease-food relations: {str(e)}")
        except Exception as e:
            st.error(f"Error fetching diseases: {str(e)}")
        
        if not results.empty:
            # Display table
            st.subheader("Top Microbes Associated with Parkinson's")
            st.dataframe(results)
            
            # Create bar chart
            fig = px.bar(
                results,
                x='strength',
                y='microbe',
                orientation='h',
                title='Microbe Strength Relationship with Parkinson\'s Disease',
                labels={'strength': 'Relationship Strength', 'microbe': 'Microbe'}
            )
            st.plotly_chart(fig)
        else:
            st.warning("No data found. Please check Neo4j connection.")
            
            # Show sample data for Microbe and Disease labels
            st.write("### Sample Microbe Data:")
            microbe_data = minerva.get_sample_data('Microbe', 3)
            if not microbe_data.empty:
                st.dataframe(microbe_data)
            
            st.write("### Sample Disease Data:")
            disease_data = minerva.get_sample_data('Disease', 3)
            if not disease_data.empty:
                st.dataframe(disease_data)
    
    with tab2:
        st.header("Risk Factors Analysis")
        
        # Get risk factors using MINERVA's method
        try:
            risk_factors = minerva.get_risk_factors()
            if not risk_factors.empty:
                st.subheader("Risk Factors for Parkinson's Disease")
                st.dataframe(risk_factors)
            else:
                st.warning("No risk factors found in the database.")
        except Exception as e:
            st.error(f"Error querying risk factors: {str(e)}")
        
        if not risk_factors.empty:
            # Create pie chart
            fig = px.pie(
                risk_factors,
                names='factor_type',
                title='Distribution of Risk Factor Types'
            )
            st.plotly_chart(fig)
        
    with tab3:
        st.header("Statistics")
        
        # Count queries
        microbe_count_query = """
        MATCH (m:Microbe)-[:STRENGTH]-(d:Disease)
        WHERE d.name = 'Parkinson\'s Disease'
        RETURN COUNT(DISTINCT m) as microbe_count
        """
        
        paper_count_query = """
        MATCH (m:Microbe)-[r:STRENGTH]-(d:Disease)
        WHERE d.name = 'Parkinson\'s Disease'
        RETURN count(DISTINCT r.pmid) AS paper_count
        """
        
        microbe_count = minerva.query(microbe_count_query)
        paper_count = minerva.query(paper_count_query)
        
        if not microbe_count.empty and not paper_count.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Number of Microbes", microbe_count.iloc[0]['microbe_count'])
            
            with col2:
                st.metric("Number of Research Papers", paper_count.iloc[0]['paper_count'])

if __name__ == "__main__":
    create_minerva_dashboard()
