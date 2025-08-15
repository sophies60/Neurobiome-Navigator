import pandas as pd
from py2neo import Graph, NodeMatcher
import streamlit as st
from dataclasses import dataclass
import os
import time
from metrics import timer, log_csv, now_iso

# Fetch connection details from environment variables
neo4j_host = os.getenv('NEO4J_HOST', '0.0.0.0')
neo4j_port = os.getenv('NEO4J_PORT', '7687')
neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
neo4j_password = os.getenv('NEO4J_PASSWORD', 'synhodo123')

# Build the bolt URL
bolt_url = f'bolt://{neo4j_host}:{neo4j_port}'


@dataclass
class GraphQueries:
    def __init__(self):
        # Initialize Neo4j connection with explicit settings for local Docker
        self.bolt_url = 'bolt://localhost:7687'  # Direct connection to Docker container
        neo4j_user = 'neo4j'
        neo4j_password = 'synhodo123'
        
        try:
            # Initialize the Neo4j connection
            self.graph = Graph(
                self.bolt_url,
                auth=(neo4j_user, neo4j_password),
                secure=False  # Disable SSL for local connections
            )
            # Test the connection with a simple query
            result = self.graph.run("RETURN 1").data()
            print(f"Successfully connected to Neo4j at {self.bolt_url}")
        except Exception as e:
            error_msg = f"Failed to connect to Neo4j at {self.bolt_url}: {str(e)}"
            print(error_msg)
            if 'st' in globals():
                st.error(error_msg)
            raise

    def _run_timed(self, query: str, params: dict | None = None, label: str = ""):
        t0 = time.perf_counter()
        cursor = self.graph.run(query, **(params or {}))
        data = cursor.data()
        dt_ms = (time.perf_counter() - t0) * 1000

        # Print to terminal
        print(f"[METRIC] neo4j_query_ms={dt_ms:.2f} label={label} rows={len(data)}")

        # Optional CSV
        log_csv({
            "ts": now_iso(),
            "metric": "neo4j_query",
            "label": label,
            "ms": round(dt_ms, 2),
            "rows": len(data)
        })
        return data

    def get_all_diseases(self) -> pd.DataFrame:
        """Get all diseases with their CUIs"""
        query = """
        MATCH (d:Disease)
        RETURN d.name as name, d.cui as cui
        """
        result = self._run_timed(query, label="get_all_diseases")
        return pd.DataFrame(result)

    def get_disease_food_relations(self, disease_cui: str) -> pd.DataFrame:
        """Get food-disease relations through microbes"""
        query = """
        MATCH (f:Food)-[fm:STRENGTH]->(m:Microbe)-[md:STRENGTH]->(d:Disease)
        WHERE d.cui = $disease_cui
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
        result = self._run_timed(query, params={"disease_cui": disease_cui}, label="get_disease_food_relations")
        return pd.DataFrame(result)

    @st.cache_data
    def count_nodes(self, label='Microbe'):
        query = """
        MATCH (m:{})-[:STRENGTH]-(d) 
        RETURN COUNT(DISTINCT m) as count
        """.format(label)
        result = self._run_timed(query, label="count_nodes")
        return result[0]['count']

    @st.cache_data
    def count_papers(self):
        query = """
        MATCH (:Microbe)-[r:NEGATIVE|POSITIVE]->(:Disease)
        RETURN count(DISTINCT r.pmid) AS total_papers
        """
        result = self._run_timed(query, label="count_papers")
        return result[0]['total_papers']

    @st.cache_data
    def count_relationships(self):
        query = """
                MATCH ()-[r:POSITIVE]->()
                RETURN count(r) AS count
                """
        result = self._run_timed(query, label="count_relationships")
        positives = result[0]['count']

        query = """
                MATCH ()-[r:NEGATIVE]->()
                RETURN count(r) AS count
                """
        result = self._run_timed(query, label="count_relationships")
        negatives = result[0]['count']
        total = positives + negatives
        return total


    @st.cache_data
    def get_microbe_by_property(self, dicto):
        query = """
        Match (m:Microbe) where m.{} = '{}'
        return m.name as name, m.official_name as official_name, m.cui as cui, m.rank as rank, m.tax_id as tax_id, m.definition as definition, 
        m.synonyms as synonyms
        """.format(list(dicto.keys())[0], list(dicto.values())[0])

        result = self._run_timed(query, params={"dicto": dicto}, label="get_microbe_by_property")
        return result[0]


    @st.cache_data
    def get_disease_by_property(self, dicto):
        # Escape single quotes in the value
        key = list(dicto.keys())[0]
        value = list(dicto.values())[0].replace("'", "\\'")
        
        query = """
                MATCH (d:Disease) 
                WHERE d.{} = '{}'
                RETURN d.name as name, 
                       d.official_name as official_name, 
                       d.cui as cui, 
                       d.tui as tui, 
                       d.snomedct_concept as snomedct_concept, 
                       d.definition as definition, 
                       d.synonyms as synonyms
                """.format(key, value)

        result = self._run_timed(query, params={"dicto": dicto}, label="get_disease_by_property")
        return result[0] if result else None

    @st.cache_data
    def get_relationship_by_microbe_disease(self, m_dicto, d_dicto):
        query = """
        Match (d:Disease)-[r:{}]-(m:Microbe) 
        WHERE d.{} = '{}' AND m.{} = '{}'
        RETURN r.rel_type as Type, r.title as Title, r.pmid as PMID, r.pmcid as PMCID, r.publication_year as Year, r.impact_factor as ImpactFactor, r.evidence as Evidence
        """.format('POSITIVE', list(d_dicto.keys())[0], list(d_dicto.values())[0],
                   list(m_dicto.keys())[0], list(m_dicto.values())[0])

        result_positive = self._run_timed(query, params={"m_dicto": m_dicto, "d_dicto": d_dicto}, label="get_relationship_by_microbe_disease")

        query = """
            Match (d:Disease)-[r:{}]-(m:Microbe) 
            WHERE d.{} = '{}' AND m.{} = '{}'
            RETURN r.rel_type as Type, r.title as Title, r.pmid as PMID, r.pmcid as PMCID, r.publication_year as Year, r.impact_factor as ImpactFactor, r.evidence as Evidence
                """.format('NEGATIVE', list(d_dicto.keys())[0], list(d_dicto.values())[0],
                           list(m_dicto.keys())[0], list(m_dicto.values())[0])

        result_negative = self._run_timed(query, params={"m_dicto": m_dicto, "d_dicto": d_dicto}, label="get_relationship_by_microbe_disease")

        result = pd.concat([result_negative, result_positive], axis=0)
        return result



    @st.cache_data
    def get_strength_by_microbe_disease(self, m_dicto, d_dicto):
        query = """
                Match (d:Disease)-[r:{}]-(m:Microbe) 
                WHERE d.{} = '{}' AND m.{} = '{}'
                RETURN r.strength_raw as Strength, r.strength_IF as Strength_IF, r.strength_IFQ as Strength_IFQ
                """.format('STRENGTH', list(d_dicto.keys())[0], list(d_dicto.values())[0],
                           list(m_dicto.keys())[0], list(m_dicto.values())[0])

        result = self._run_timed(query, params={"m_dicto": m_dicto, "d_dicto": d_dicto}, label="get_strength_by_microbe_disease")
        return result

    def get_shortest_path_by_microbe_disease(self, m_dicto, d_dicto):
        query = """
                MATCH (m:Microbe),(d:Disease),
                p = shortestPath((m)-[*..15]-(d)) 
                WHERE m.{} = '{}' AND d.{} = '{}'
                RETURN p
                        """.format(list(m_dicto.keys())[0], list(m_dicto.values())[0],
                                   list(d_dicto.keys())[0], list(d_dicto.values())[0])

        result = self._run_timed(query, params={"m_dicto": m_dicto, "d_dicto": d_dicto}, label="get_shortest_path_by_microbe_disease")
        return result

    @st.cache_data
    def get_disease_food_relations(self, cui):
        """
        주어진 Disease cui를 시작점으로, Food → Microbe → Disease 경로를 조회하여,
        Food와 Disease 사이의 파생 관계를 산출합니다.
        
        룰:
          - Food-Microbe 관계와 Microbe-Disease 관계의 strength_raw 값이 모두 0 이상이면 
              (positive + positive) derived_relation은 "positive"
          - 두 값이 모두 0 미만이면 (negative + negative) derived_relation은 "positive"
          - 한 관계가 0 이상이고 다른 관계가 0 미만이면 derived_relation은 "negative"
        """
        query = """
            MATCH (f:`Food`)-[r1:STRENGTH]-(m:Microbe)-[r2:STRENGTH]-(d:Disease)
            WHERE d.cui = '{}'
            RETURN f.official_name AS food_name, 
                   m.name AS microbe_name, 
                   r1.strength_raw AS food_microbe_strength, 
                   r2.strength_raw AS microbe_disease_strength,
                   CASE 
                     WHEN (r1.strength_raw >= 0 AND r2.strength_raw >= 0) OR (r1.strength_raw < 0 AND r2.strength_raw < 0)
                     THEN "positive"
                     ELSE "negative"
                   END AS derived_relation
        """.format(cui)
        result = self._run_timed(query, params={"cui": cui}, label="get_disease_food_relations")
        return result
    
    @st.cache_data
    def find_one_hop_disease_food(self, cui):
        """
        주어진 Disease cui를 시작점으로, 최대 2-hop (Disease → Microbe → Food) 관계를 반환합니다.
        """
        query = """
            MATCH (d:Disease)
            WHERE d.cui = '{}'
            WITH d 
            MATCH p = (d)-[r:STRENGTH|PARENT*..2]-(n)
            WITH p LIMIT 50
            UNWIND relationships(p) AS rel
            WITH startNode(rel) AS source, endNode(rel) AS target, rel as edge
            RETURN 
              source.official_name as source, 
              labels(source)[0] AS source_type,
              CASE WHEN type(edge) = "PARENT" THEN 'PARENT' ELSE toString(edge.strength_raw) END AS relation,
              target.official_name as target,
              labels(target)[0] AS target_type
        """.format(cui)
        result = self._run_timed(query, params={"cui": cui}, label="find_one_hop_disease_food")
        return result

    @st.cache_data
    def get_food_by_property(self, dicto):
        query = """
        MATCH (f:`Food`)
        WHERE f.{} = '{}'
        RETURN f.official_name as official_name, f.tui as tui, f.snomedct_concept as snomedct_concept, 
               f.definition as definition, f.synonyms as synonyms, f.cui as cui, f.name as name
        """.format(list(dicto.keys())[0], list(dicto.values())[0])
        result = self._run_timed(query, params={"dicto": dicto}, label="get_food_by_property")
        if result:
            return result[0]
        else:
            return None

    @st.cache_data
    def get_microbes_with_more_connections_pos_neg(self, n=10):
        query = """
            MATCH (m:Microbe)-[r:STRENGTH]->(:Disease)
            WITH m, count(r) AS strength_count,
                 count(CASE WHEN r.strength_raw >= 0 THEN 1 END) AS strength_positive,
                 count(CASE WHEN r.strength_raw < 0 THEN 1 END) AS strength_negative
            ORDER BY strength_count DESC
            RETURN m.name AS microbe_name, strength_coun    t, strength_positive, strength_negative
            LIMIT {}
        """.format(n)
        result = self._run_timed(query, params={"n": n}, label="get_microbes_with_more_connections_pos_neg")
        return result
    
    @st.cache_data
    def get_all_food(self):
        query = """
        MATCH (f:`Food`)
        RETURN DISTINCT f.cui AS cui, f.name AS name, f.official_name AS official_name
        ORDER BY f.official_name ASC
        """
        result = self._run_timed(query, label="get_all_food")
        return result

    @st.cache_data
    def get_food_relations(self, cui, rel_type='POSITIVE'):
        """
        Food와 Microbe 사이의 관계를 조회합니다.
        rel_type이 POSITIVE이면 strength_raw >= 0인 관계를,
        그렇지 않으면 strength_raw < 0인 관계를 반환합니다.
        """
        if rel_type.upper() == 'POSITIVE':
            query = """
            MATCH (f:`Food`)-[r:STRENGTH]-(m:Microbe)
            WHERE f.cui = '{}' AND r.strength_raw >= 0
            RETURN m.name as microbe_name, f.official_name as food_name, r.strength_raw as strength, f.cui as cui
            """.format(cui)
        else:
            query = """
            MATCH (f:`Food`)-[r:STRENGTH]-(m:Microbe)
            WHERE f.cui = '{}' AND r.strength_raw < 0
            RETURN m.name as microbe_name, f.official_name as food_name, r.strength_raw as strength, f.cui as cui
            """.format(cui)
        result = self._run_timed(query, params={"cui": cui}, label="get_food_relations")
        return result
    
    @st.cache_data
    def find_one_hop_food(self, cui):
        """
        Food/Nutrition 노드를 시작점으로, 최대 2-hop 관계(예: Food→Microbe 및 Microbe→Disease)를 반환합니다.
        """
        query = """
            MATCH (f:`Food`)
            WHERE f.cui = '{}'
            WITH f 
            MATCH p = (f)-[r:STRENGTH|PARENT*..2]-(n)
            WITH p LIMIT 50
            UNWIND relationships(p) AS rel
            WITH startNode(rel) AS source, endNode(rel) AS target, rel as edge
            RETURN 
              source.official_name as source, 
              labels(source)[0] AS source_type,
              CASE WHEN type(edge) = "PARENT" THEN 'PARENT' ELSE toString(edge.strength_raw) END AS relation,
              target.official_name as target,
              labels(target)[0] AS target_type
        """.format(cui)
        result = self._run_timed(query, params={"cui": cui}, label="find_one_hop_food")
        return result

    def get_related_publications_food(self, cui=''):
        """
        Food와 관련된 출판물 정보를 조회합니다.
        Food 노드와 연결된 Microbe와의 관계에서 출판물 정보를 반환합니다.
        """
        query = """
            MATCH (f:`Food`)-[r:POSITIVE|NEGATIVE]-(m:Microbe)
            WHERE f.cui = '{}'
            RETURN r.pmid as pmid, f.official_name as food, r.cui_microbe as microbe, r.rel_type as rel_type,
                   r.publication_year as year, r.journal as journal, r.title as title, r.evidence as evidence
            ORDER BY r.publication_year
            """.format(cui)
        result = self._run_timed(query, params={"cui": cui}, label="get_related_publications_food")
        return result


    @st.cache_data
    def get_microbes_with_more_references_pos_neg(self, n=10):
        query = """
            MATCH (m:Microbe)-[r:NEGATIVE |POSITIVE]->(:Disease)
            WITH m, count(r) AS total_relations, 
                 count(CASE WHEN type(r) = 'NEGATIVE' THEN 1 END) AS negative_count,
                 count(CASE WHEN type(r) = 'POSITIVE' THEN 1 END) AS positive_count
            ORDER BY total_relations DESC
            RETURN m.name AS microbe_name, total_relations, negative_count, positive_count
            LIMIT {}
        """.format(n)
        result = self._run_timed(query, params={"n": n}, label="get_microbes_with_more_references_pos_neg")
        return result

    @st.cache_data
    def get_diseases_with_more_connections_pos_neg(self, n=10):
        query = """
               MATCH (:Microbe)-[r:STRENGTH]->(m:Disease)
            WITH m, count(r) AS strength_count,
                 count(CASE WHEN r.strength_raw >= 0 THEN 1 END) AS strength_positive,
                 count(CASE WHEN r.strength_raw < 0 THEN 1 END) AS strength_negative
            ORDER BY strength_count DESC
            RETURN m.name AS disease_name, strength_count, strength_positive, strength_negative
            LIMIT {}
                """.format(n)
        result = self._run_timed(query, params={"n": n}, label="get_diseases_with_more_connections_pos_neg")
        return result


    @st.cache_data
    def get_diseases_with_more_references_pos_neg(self, n=10):
        query = """
            MATCH (:Microbe)-[r:NEGATIVE |POSITIVE]->(m:Disease)
            WITH m, count(r) AS total_relations, 
                 count(CASE WHEN type(r) = 'NEGATIVE' THEN 1 END) AS negative_count,
                 count(CASE WHEN type(r) = 'POSITIVE' THEN 1 END) AS positive_count
            ORDER BY total_relations DESC
            RETURN m.name AS disease_name, total_relations, negative_count, positive_count
            LIMIT {}
        """.format(n)
        result = self._run_timed(query, params={"n": n}, label="get_diseases_with_more_references_pos_neg")
        return result

    @st.cache_data
    def get_relationships_by_year(self):
        query = """
        MATCH ()-[r:POSITIVE|NEGATIVE]->() 
        RETURN r.publication_year as publication_year, count(r) AS relationship_count
        ORDER BY r.publication_year
        """
        result = self._run_timed(query, label="get_relationships_by_year")
        return result

    @st.cache_data
    def get_publications_by_year(self):
        query = """
        MATCH ()-[r:POSITIVE|NEGATIVE]->() 
        RETURN r.publication_year as publication_year, count(DISTINCT r.pmid) as publications
        ORDER BY r.publication_year
        """
        result = self._run_timed(query, label="get_publications_by_year")
        return result

    @st.cache_data
    def rank_by_positive_strength(self, strength_type='strength_raw', n=10):
        query = """
        MATCH (n1:Microbe)-[r:STRENGTH]-(n2:Disease)
        RETURN n1.name AS Microbe, n2.name AS Disease, r.{} AS Strength
        ORDER BY Strength DESC
        Limit {}
        """.format(strength_type, n)
        result = self._run_timed(query, label="rank_by_positive_strength")
        return pd.DataFrame(result)
    
    @st.cache_data
    def rank_by_negative_strength(self, strength_type='strength_raw', n=10):
        query = """
        MATCH (n1:Microbe)-[r:STRENGTH]-(n2:Disease)
        RETURN n1.name AS Microbe, n2.name AS Disease, r.{} AS Strength
        ORDER BY Strength ASC
        Limit {}
        """.format(strength_type, n)
        result = self._run_timed(query, label="rank_by_negative_strength")
        return pd.DataFrame(result)

    @st.cache_data
    def get_more_relevant_papers(self, n=10):
        query = """
        MATCH ()-[r:POSITIVE|NEGATIVE]->()
        WITH r.pmid AS PMID, count(*) AS Frequency, r.title as Title
        ORDER BY Frequency DESC, r.pmid 
        Limit 10
        RETURN Title, PMID, Frequency 
        """
        result = self._run_timed(query, params={"n": n}, label="get_more_relevant_papers")
        return result

    @st.cache_data
    def get_publications_by_journal(self, n=10):
        query = """
        MATCH (m:Microbe)-[r:NEGATIVE|POSITIVE]->(d:Disease)
        return r.pmid AS PMID, r.journal as Journal
        """
        result = self._run_timed(query, label="get_publications_by_journal")
        df = pd.DataFrame(result)
        df.index = df['PMID']
        df = df[~df.index.duplicated(keep='first')]
        return df['Journal'].value_counts().sort_values(ascending=False).iloc[:n].to_frame('counts')

    @st.cache_data
    def get_all_microbes(self):
        query = """
        MATCH (m:Microbe)-[:STRENGTH]-(:Disease)
        RETURN DISTINCT m.cui AS cui, m.tax_id as tax_id, m.name AS name
        """
        result = self._run_timed(query, label="get_all_microbes")
        df = pd.DataFrame(result)
        return df.sort_values('name', ascending=True)


    @st.cache_data
    def get_all_diseases(self):
        query = """
        MATCH (m:Disease)-[:STRENGTH]-(:Microbe)
        RETURN DISTINCT m.cui AS cui, m.name AS name, m.official_name AS official_name
        """
        result = self._run_timed(query, label="get_all_diseases")
        df = pd.DataFrame(result)
        return df.sort_values('name', ascending=True)

    def find_one_hop_microbe(self, cui):
        query = """
            MATCH (m:Microbe) // Start with the specified Microbe
            WHERE m.cui = '{}'
            // Define the one-hop traversal pattern
            WITH m 
            MATCH p = (m)-[r:STRENGTH|PARENT*..1]-(n) 
            // UNWIND r as rel 
            WITH p LIMIT 50
            UNWIND relationships(p) AS rel   // <-- Use relationships(p) here
            WITH startNode(rel) AS source, endNode(rel) AS target, rel as edge
            
            // Return the desired properties
            RETURN 
              source.name AS source, 
              labels(source)[0] AS source_type, // Get the first label
              CASE WHEN type(edge) = "PARENT" THEN 'PARENT' ELSE edge.strength_raw END AS relation,
              target.name AS target,
                labels(target)[0] AS target_type // Get the first label
        """.format(cui)
        result = self._run_timed(query, label="find_one_hop_microbe")
        return pd.DataFrame(result)

    def find_one_hop_disease(self, cui):
        query = """
            MATCH (m:Disease) // Start with the specified Microbe
            WHERE m.cui = '{}'
            // Define the three-hop traversal pattern
            WITH m 
            MATCH p = (m)-[r:STRENGTH|PARENT*..1]-(n) 
            // UNWIND r as rel 
            WITH p LIMIT 50
            UNWIND relationships(p) AS rel   // <-- Use relationships(p) here
            WITH startNode(rel) AS source, endNode(rel) AS target, rel as edge
            
            // Return the desired properties
            RETURN 
              source.name AS source, 
              labels(source)[0] AS source_type, // Get the first label
              CASE WHEN type(edge) = "PARENT" THEN 'PARENT' ELSE edge.strength_raw END AS relation,
              target.name AS target,
                labels(target)[0] AS target_type // Get the first label
        """.format(cui)
        result = self._run_timed(query, label="find_one_hop_disease")
        return pd.DataFrame(result)

    @st.cache_data
    def get_food_disease_relations(self, cui):
        """
        Food/Nutrition 노드를 시작점으로 Food → Microbe → Disease 경로를 조회하여,
        Food와 Disease 사이의 파생 관계를 반환합니다.
        
        룰:
          - Food-Microbe 관계와 Microbe-Disease 관계의 strength_raw 값이 모두 0 이상이면 (positive + positive)
            또는 모두 0 미만이면 (negative + negative) derived_relation은 "positive"
          - 한 관계가 0 이상이고 다른 관계가 0 미만이면 derived_relation은 "negative"
        """
        query = """
            MATCH (f:`Food`)-[r1:STRENGTH]-(m:Microbe)-[r2:STRENGTH]-(d:Disease)
            WHERE f.cui = '{}'
            RETURN d.official_name AS disease_name, 
                   m.name AS microbe_name, 
                   f.official_name AS food_name,
                   r1.strength_raw AS food_microbe_strength, 
                   r2.strength_raw AS microbe_disease_strength,
                   CASE 
                     WHEN (r1.strength_raw >= 0 AND r2.strength_raw >= 0) OR (r1.strength_raw < 0 AND r2.strength_raw < 0)
                     THEN "positive"
                     ELSE "negative"
                   END AS derived_relation
        """.format(cui)
        result = self._run_timed(query, label="get_food_disease_relations")
        return pd.DataFrame(result)

    def get_microbe_relations(self, cui, rel_type='POSIIVE'):
        if rel_type == 'POSITIVE':
            query = """
            MATCH (m:Microbe)-[r:STRENGTH]-(d:Disease)
            WHERE m.cui = '{}' AND r.strength_raw >= 0
            RETURN m.name as microbe_name, d.name as disease_name, r.strength_raw as strength, d.cui as cui
            """.format(cui)
        else:
            query = """
            MATCH (m:Microbe)-[r:STRENGTH]-(d:Disease)
            WHERE m.cui = '{}' AND r.strength_raw < 0
            RETURN m.name as microbe_name, d.name as disease_name, r.strength_raw as strength, d.cui as cui
            """.format(cui)
        result = self._run_timed(query, label=f"get_microbe_relations_{rel_type.lower()}")
        return pd.DataFrame(result)

    def get_disease_relations(self, cui, rel_type='POSIIVE'):
        if rel_type == 'POSITIVE':
            query = """
            MATCH (m:Microbe)-[r:STRENGTH]-(d:Disease)
            WHERE d.cui = '{}' AND r.strength_raw >= 0
            RETURN d.name as disease_name, m.name as microbe_name, r.strength_raw as strength, m.cui as cui
            """.format(cui)
        else:
            query = """
            MATCH (m:Microbe)-[r:STRENGTH]-(d:Disease)
            WHERE d.cui = '{}' AND r.strength_raw < 0
            RETURN d.name as disease_name, m.name as microbe_name, r.strength_raw as strength, m.cui as cui
            """.format(cui)
        result = self._run_timed(query, label=f"get_disease_relations_{rel_type.lower()}")
        return pd.DataFrame(result)

    def popularity_in_time(self, label='Microbe', cui=''):
        query = """
        MATCH (m:{})-[r:POSITIVE|NEGATIVE]-()
        WHERE m.cui = '{}'
        RETURN r.publication_year as publication_year, count(DISTINCT r.pmid) as publications
        ORDER BY r.publication_year
        """.format(label, cui)
        result = self._run_timed(query, label=f"popularity_in_time_{label.lower()}")
        return pd.DataFrame(result)

    def get_related_publications_microbe(self, cui=''):
        query = """
            MATCH (m:Microbe)-[r:POSITIVE|NEGATIVE]-()
            WHERE m.cui = '{}'
            RETURN r.pmid as pmid, m.name as microbe, r.cui_disease as disease, r.rel_type as rel_type,
             r.publication_year as year, r.journal as journal, r.title as title, r.evidence as evidence
            ORDER BY r.publication_year
            """.format(cui)
        result = self._run_timed(query, label="get_related_publications_microbe")
        return pd.DataFrame(result)

    def get_related_publications_disease(self, cui=''):
        query = """
            MATCH (m:Disease)-[r:POSITIVE|NEGATIVE]-()
            WHERE m.cui = '{}'
            RETURN r.pmid as pmid, m.name as disease, r.cui_microbe as microbe, r.rel_type as rel_type,
             r.publication_year as year, r.journal as journal, r.title as title, r.evidence as evidence
            ORDER BY r.publication_year
            """.format(cui)
        result = self._run_timed(query, label="get_related_publications_disease")
        return pd.DataFrame(result)

if __name__ == '__main__':
    querier = GraphQueries()
    print(querier.get_disease_by_property({'name': 'gondii infection'}))
    print(querier.get_relationship_by_microbe_disease(m_dicto={'name': 'Bacteria'}, d_dicto={'name': 'depression'}))
    print(querier.get_strength_by_microbe_disease(m_dicto={'name': 'Bacteria'}, d_dicto={'name': 'depression'}))
    print(querier.get_shortest_path_by_microbe_disease(m_dicto={'cui': 'C1008539'}, d_dicto={'cui': 'C0040558'}))
    print(querier.rank_by_positive_strength())
    print(querier.rank_by_negative_strength())
    print(querier.get_more_relevant_papers())
    print(querier.count_nodes(label='Microbe'))
    print(querier.count_nodes(label='Disease'))
    print(querier.count_papers())
    print(querier.count_relationships())
    print(querier.get_microbes_with_more_connections_pos_neg(n=10))
    print(querier.get_diseases_with_more_connections_pos_neg(n=10))


    print(querier.get_publications_by_journal(n=10))
    print(querier.get_relationships_by_year())
    print(querier.get_publications_by_year())
    print(querier.get_all_microbes())
    print(querier.get_all_diseases())
    print(querier.get_microbe_by_property({'name': 'Bacteria'}))
    print(querier.find_one_hop_microbe(cui='C0038394'))
    print(querier.get_microbe_relations(cui='C0038394', rel_type='POSITIVE'))
    print(querier.get_microbe_relations(cui='C0038394', rel_type='NEGATIVE'))
    print(querier.popularity_in_time(label='Microbe', cui='C0038394'))
    print(querier.get_related_publications(label='Microbe', cui='C0038394'))

