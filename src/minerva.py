from py2neo import Graph, Node, Relationship
import os
from dotenv import load_dotenv
import pandas as pd
from typing import Dict, List, Optional
import json
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
import fitz  # Import PyMuPDF
import json
import numpy as np
from metrics import PerformanceMonitor

class MINERVA:
    def __init__(self, enable_perf_monitoring: bool = True, perf_monitor=None):
        """Initialize Neo4j connection and research paper processing
        
        Args:
            enable_perf_monitoring: Whether to enable performance monitoring
            perf_monitor: Optional external PerformanceMonitor instance
        """
        load_dotenv()
        
        # Initialize performance monitoring
        self.enable_perf_monitoring = enable_perf_monitoring
        if self.enable_perf_monitoring:
            self.perf_monitor = perf_monitor if perf_monitor else PerformanceMonitor()
        
        # Neo4j connection settings
        neo4j_host = os.getenv('NEO4J_HOST', 'localhost')
        neo4j_port = os.getenv('NEO4J_PORT', '7687')
        neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
        neo4j_password = os.getenv('NEO4J_PASSWORD', 'synhodo123')
        
        # Initialize Neo4j connection
        self.graph = Graph(
            f"bolt://{neo4j_host}:{neo4j_port}",
            auth=(neo4j_user, neo4j_password)
        )
        
        # Initialize research paper processing
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        
        # Initialize vector store
        self.vector_store = None
        
    def load_research_papers(self, directory_path: str) -> str:
        """Load and process research papers from a directory."""
        try:
            # Get absolute path to papers directory
            papers_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), directory_path)
            
            # Check if directory exists
            if not os.path.exists(papers_dir):
                raise ValueError(f"Directory not found: {papers_dir}")
                
            # Get all files in directory
            files = os.listdir(papers_dir)
            if not files:
                raise ValueError(f"No files found in directory {papers_dir}")
                
            print(f"Processing files in {papers_dir}")
            documents = []
            
            for filename in files:
                filepath = os.path.join(papers_dir, filename)
                if os.path.isfile(filepath):
                    try:
                        # Try PyPDF2 first
                        try:
                            reader = PdfReader(filepath)
                            text = ""
                            for page in reader.pages:
                                text += page.extract_text()
                            if text:
                                chunks = self.text_splitter.split_text(text)
                                documents.extend(chunks)
                                print(f"Successfully processed {filename} with PyPDF2")
                                continue
                        except Exception:
                            pass
                            
                        # Try PyMuPDF if PyPDF2 fails
                        try:
                            doc = fitz.open(filepath)
                            text = ""
                            for page_num in range(len(doc)):
                                page = doc.load_page(page_num)
                                text += page.get_text()
                            if text:
                                chunks = self.text_splitter.split_text(text)
                                documents.extend(chunks)
                                print(f"Successfully processed {filename} with PyMuPDF")
                                continue
                        except Exception:
                            pass
                            
                        # Try reading as text file if PDF processing fails
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                text = f.read()
                            if text:
                                chunks = self.text_splitter.split_text(text)
                                documents.extend(chunks)
                                print(f"Successfully processed text file: {filename}")
                        except Exception as e:
                            print(f"Failed to process {filename}: {str(e)}")
                            continue
                    except Exception as e:
                        print(f"Failed to process {filename}: {str(e)}")
                        continue
            
            if not documents:
                raise ValueError(f"No readable text files found in directory {papers_dir}")
                
            # Create FAISS index
            self.vector_store = FAISS.from_texts(
                documents,
                self.embeddings
            )
            
            print(f"Successfully loaded {len(documents)} text chunks from research papers")
            return f"Successfully loaded {len(documents)} text chunks from research papers"
            
        except Exception as e:
            print(f"Error loading research papers: {e}")
            raise
    
    def query_papers(self, question: str) -> str:
        """Query research papers using semantic search."""
        if not self.vector_store:
            raise ValueError("No research papers loaded. Please call load_research_papers() first.")
            
        # Get embeddings for query
        query_embedding = self.embeddings.embed_query(question)
        
        # Get similar documents
        docs = self.vector_store.similarity_search_by_vector(
            query_embedding,
            k=3  # Number of similar documents to retrieve
        )
        
        # Format the documents for the LLM
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Create prompt template
        template = """Answer the following question based on the research papers:
        Question: {question}
        Context: {context}
        Answer: """
        
        # Format the prompt
        prompt = template.format(question=question, context=context)
        
        # Get response from LLM
        response = self.llm.invoke(prompt)
        
        return response.content

    def query_neo4j(self, query: str, parameters: dict = None) -> pd.DataFrame:
        """Query Neo4j and return results as DataFrame."""
        try:
            result = self.graph.run(query, parameters).to_data_frame()
            return result
        except Exception as e:
            print(f"Error querying Neo4j: {e}")
            raise

    def get_schema(self) -> tuple:
        """Get schema information from Neo4j."""
        try:
            # Get labels and relationships
            labels_query = """
            CALL db.labels()
            YIELD label
            RETURN DISTINCT label
            ORDER BY label
            """
            labels = self.query_neo4j(labels_query)['label'].tolist()
            
            rels_query = """
            CALL db.relationshipTypes()
            YIELD relationshipType
            RETURN DISTINCT relationshipType
            ORDER BY relationshipType
            """
            rels = self.query_neo4j(rels_query)['relationshipType'].tolist()
            
            # Get sample nodes for each label
            samples_query = """
            MATCH (n)
            RETURN DISTINCT labels(n) AS label, COUNT(n) AS count
            """
            samples = self.query_neo4j(samples_query)
            
            return labels, rels, samples
            
        except Exception as e:
            print(f"Error getting schema: {e}")
            return None, None, None

    def get_sample_data(self, label: str, limit: int = 5) -> pd.DataFrame:
        """Get sample data for a specific label from Neo4j"""
        try:
            query = f"""
            MATCH (n:{label})
            RETURN n
            LIMIT {limit}
            """
            return self.query_neo4j(query)
        except Exception as e:
            print(f"Error getting sample data: {e}")
            return pd.DataFrame()

    def get_all_diseases(self) -> pd.DataFrame:
        """Get all diseases with their CUIs"""
        query = """
        MATCH (d:Disease)
        RETURN d.name as name, d.cui as cui
        """
        return self.query_neo4j(query)

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
        return self.query_neo4j(query, {"disease_cui": disease_cui})

    def get_microbiome_info(self) -> pd.DataFrame:
        """
        Get information about microbiome-PD relationships
        """
        query = """
        MATCH (m:Microbe)-[r:STRENGTH]->(d:Disease)
        WHERE d.name =~ '(?i)Parkinson.*'
        RETURN m.name as microbe_name,
               m.synonyms as microbe_synonyms,
               r.strength as strength,
               d.name as disease_name
        ORDER BY strength DESC
        LIMIT 10
        """
        result = self.query_neo4j(query)
        return result if not result.empty else pd.DataFrame()

    def get_risk_factors(self) -> pd.DataFrame:
        """Get risk factors for Parkinson's Disease"""
        query = """
        MATCH (f:RiskFactor)-[:ASSOCIATED_WITH]->(d:Disease)
        WHERE d.name =~ '(?i)Parkinson.*'
        RETURN f.name as risk_factor,
               f.type as factor_type,
               f.description as description
        ORDER BY f.name
        """
        result = self.query_neo4j(query)
        return result if not result.empty else pd.DataFrame()

    def combined_query(self, neo4j_query: str, paper_query: str, parameters: dict = None) -> dict:
        """
        Execute both Neo4j and paper queries and combine results.
        
        Args:
            neo4j_query: Cypher query for Neo4j database
            paper_query: Question to ask about research papers
            parameters: Optional parameters for Neo4j query
            
        Returns:
            dict: Combined results with 'neo4j' and 'papers' keys
        """
        # Execute Neo4j query
        neo4j_result = self.query_neo4j(neo4j_query, parameters)
        
        # Execute paper query
        paper_result = self.query_papers(paper_query)
        
        # Combine results
        combined_result = {
            'neo4j': neo4j_result,
            'papers': paper_result
        }
        
        return combined_result

# Example usage
if __name__ == "__main__":
    # Initialize MINERVA client (uses environment variables)
    minerva = MINERVA()
    
    # Example query
    query = """
    MATCH (m:Microbe)-[r:STRENGTH]-(d:Disease)
    WHERE d.name = 'Parkinson\'s Disease'
    RETURN m.name as microbe, r.strength as strength
    ORDER BY strength DESC
    LIMIT 10
    """
    
    # Execute query
    results = minerva.query_neo4j(query)
    print("\nMicrobiome-PD Relationships:")
    print(results)
    
    # Example of counting nodes
    count_query = """
    MATCH (m:Microbe)-[:STRENGTH]-(d:Disease)
    RETURN COUNT(DISTINCT m) as count
    """
    count_results = minerva.query_neo4j(count_query)
    print("\nNumber of microbes:")
    print(count_results)
