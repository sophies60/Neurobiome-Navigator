from py2neo import Graph, NodeMatcher
import os
from typing import Dict, List, Optional
import pandas as pd

# Fetch connection details from environment variables
neo4j_host = os.getenv('NEO4J_HOST', 'localhost')
neo4j_port = os.getenv('NEO4J_PORT', '7687')
neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
neo4j_password = os.getenv('NEO4J_PASSWORD', 'synhodo123')

# Build the bolt URL
bolt_url = f'bolt://{neo4j_host}:{neo4j_port}'

class GraphQueries:
    def __init__(self):
        """Initialize Neo4j connection"""
        self.graph = Graph(
            bolt_url,
            auth=(neo4j_user, neo4j_password),
            secure=False,
            verify=False
        )

    def get_all_diseases(self) -> pd.DataFrame:
        """Get all diseases with their CUIs"""
        query = """
        MATCH (d:Disease)
        RETURN DISTINCT d.cui as cui, d.name as name
        ORDER BY d.name
        """
        return self.graph.run(query).to_data_frame()

    def get_disease_by_property(self, properties: Dict[str, str]) -> Optional[Dict]:
        """Get disease information by property"""
        query = """
        MATCH (d:Disease)
        WHERE d.{property} = $value
        RETURN 
            d.name as name, 
            d.official_name as official_name, 
            d.cui as cui, 
            d.tui as tui, 
            d.snomedct_concept as snomedct_concept, 
            d.definition as definition, 
            d.synonyms as synonyms
        """.format(property=list(properties.keys())[0])
        
        result = self.graph.run(query, value=list(properties.values())[0]).data()
        return result[0] if result else None

    def get_disease_food_relations(self, cui: str) -> pd.DataFrame:
        """Get food-disease relations through microbes"""
        query = """
        MATCH (f:Food)-[fm:STRENGTH]->(m:Microbe)-[md:STRENGTH]->(d:Disease)
        WHERE d.cui = $cui
        RETURN 
            f.name as food_name,
            f.synonyms as food_synonyms,
            m.name as microbe_name,
            m.synonyms as microbe_synonyms,
            d.name as disease_name,
            fm.strength as food_microbe_strength,
            md.strength as microbe_disease_strength,
            CASE 
                WHEN fm.strength > 0 AND md.strength > 0 THEN 'positive'
                WHEN fm.strength < 0 AND md.strength < 0 THEN 'positive'
                ELSE 'negative'
            END as derived_relation
        """
        result = self.graph.run(query, cui=cui).to_data_frame()
        
        # Clean up data
        result = result.dropna(subset=["food_microbe_strength", "microbe_disease_strength"])
        
        # Calculate food_disease_strength
        result['food_disease_strength'] = abs(result['food_microbe_strength']) + \
            abs(result['microbe_disease_strength']) * (
                1 if result['derived_relation'] == 'positive' else -1
            )
        
        return result

    def get_relationship_paths(self, disease_cui: str, food_name: str) -> dict:
        """Get relationship paths between disease and food"""
        query = """
        MATCH p = (d:Disease {cui: $disease_cui})-[*1..3]-(f:Food {name: $food_name})
        RETURN 
            collect(DISTINCT nodes(p)) as allNodes,
            collect(DISTINCT relationships(p)) as allRels
        """
        result = self.graph.run(query, disease_cui=disease_cui, food_name=food_name).data()
        return result[0] if result else {}
