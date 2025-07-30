from __future__ import annotations
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field, ConfigDict
from dotenv import load_dotenv
from rich.markdown import Markdown
from rich.console import Console
from rich.live import Live
import asyncio
import os

from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai import Agent, RunContext
from minerva import MINERVA

load_dotenv()

# ========== Define dependencies ==========
@dataclass
class MINERVADependencies:
    """Dependencies for the MINERVA agent."""
    minerva_client: MINERVA

# ========== Helper function to get model configuration ==========
def get_model():
    """Configure and return the LLM model to use."""
    model_choice = os.getenv('MODEL_CHOICE', 'gpt-4')
    api_key = os.getenv('OPENAI_API_KEY')
    return OpenAIModel(model_choice, provider=OpenAIProvider(api_key=api_key))

# ========== Create the MINERVA agent ==========
minerva_agent = Agent(
    get_model(),
    system_prompt="""You are a medical research assistant specializing in Parkinson's disease and oral-gut-brain axis.
    You have access to:
    - Neo4j knowledge graph containing:
      * Parkinson's disease research
      * Gut microbiome studies
      * Impulse control disorder information
      * Treatment and management strategies
    - Research papers on the latest scientific findings
    
    When answering questions:
    1. First search the knowledge graph for structured information
    2. If needed, query research papers for deeper insights
    3. Provide clear, factual answers with supporting evidence
    4. Format responses in Markdown with:
       * Clear headings
       * Bullet points for key findings
       * Proper citations when using research paper information
    
    Important guidelines:
    - Always prioritize knowledge graph information when available
    - Use research papers to supplement or provide deeper insights
    - Present medical information in a professional, evidence-based manner
    - Be honest if you cannot find the information needed
    """,
    deps_type=MINERVADependencies
)

# ========== Define result models ==========
class Neo4jResult(BaseModel):
    """Model representing a Neo4j query result."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    labels: List[str] = Field(description="Labels of the nodes")
    properties: Dict[str, Any] = Field(description="Properties of the nodes")
    relationships: List[Dict[str, Any]] = Field(description="Relationships between nodes")

class ResearchPaperResult(BaseModel):
    """Model representing a research paper query result."""
    context: str = Field(description="Context from relevant papers")
    insights: str = Field(description="Generated insights from the context")

# ========== Neo4j query tool ==========
@minerva_agent.tool
async def query_neo4j(ctx: RunContext[MINERVADependencies], query: str, parameters: Dict = None) -> List[Neo4jResult]:
    """Query the Neo4j knowledge graph with the given Cypher query.
    
    Args:
        ctx: The run context containing dependencies
        query: The Cypher query to execute
        parameters: Optional parameters for the query
        
    Returns:
        A list of formatted Neo4j results
    """
    try:
        # Execute the query
        results = ctx.deps.minerva_client.query_neo4j(query, parameters)
        
        # Format results
        formatted_results = []
        for _, row in results.iterrows():
            result = Neo4jResult(
                labels=row.get('labels', []),
                properties=row.get('properties', {}),
                relationships=row.get('relationships', [])
            )
            formatted_results.append(result)
        
        return formatted_results
    except Exception as e:
        print(f"Error querying Neo4j: {str(e)}")
        raise

# ========== Research paper query tool ==========
@minerva_agent.tool
async def query_research_papers(ctx: RunContext[MINERVADependencies], question: str) -> ResearchPaperResult:
    """Query research papers for deeper insights.
    
    Args:
        ctx: The run context containing dependencies
        question: The research question to investigate
        
    Returns:
        A formatted research paper result with context and insights
    """
    try:
        # Get insights from research papers
        insights = ctx.deps.minerva_client.query_papers(question)
        
        return ResearchPaperResult(
            context="",  # Context is handled internally by MINERVA
            insights=insights
        )
    except Exception as e:
        print(f"Error querying research papers: {str(e)}")
        raise

# ========== Food-disease relationship query tool ==========
@minerva_agent.tool
async def query_food_relationships(ctx: RunContext[MINERVADependencies], disease_name: str = "Parkinson's Disease") -> Dict:
    """Query food-disease relationships through microbiome analysis.
    
    Args:
        ctx: The run context containing dependencies
        disease_name: The name of the disease to query (default: "Parkinson's Disease")
        
    Returns:
        A dictionary containing food-disease relationships and insights
    """
    try:
        # First, get the disease CUI
        disease_query = """
        MATCH (d:Disease)
        WHERE toLower(d.name) CONTAINS toLower($disease_name)
        RETURN d.cui as cui, d.name as name
        LIMIT 1
        """
        disease_result = ctx.deps.minerva_client.query_neo4j(disease_query, {"disease_name": disease_name})
        
        if disease_result.empty:
            return {"error": f"No disease found matching '{disease_name}'"}
            
        disease_cui = disease_result.iloc[0]['cui']
        disease_name = disease_result.iloc[0]['name']
        
        # Get food-disease relationships
        food_relations = ctx.deps.minerva_client.get_disease_food_relations(disease_cui)
        
        if food_relations.empty:
            return {
                "disease": disease_name,
                "message": f"No food relationships found for {disease_name}.",
                "relationships": []
            }
            
        # Format the results
        relationships = []
        for _, row in food_relations.iterrows():
            relationships.append({
                "food": row['food_name'],
                "microbe": row['microbe_name'],
                "food_microbe_strength": float(row['food_microbe_strength']),
                "microbe_disease_strength": float(row['microbe_disease_strength']),
                "derived_relation": row['derived_relation']
            })
        
        return {
            "disease": disease_name,
            "message": f"Found {len(relationships)} food relationships for {disease_name}.",
            "relationships": relationships
        }
        
    except Exception as e:
        print(f"Error querying food relationships: {str(e)}")
        return {"error": f"An error occurred while querying food relationships: {str(e)}"}

# ========== Main execution function ==========
async def main():
    """Run the MINERVA agent with user queries."""
    print("MINERVA Agent - Medical Research Assistant")
    print("Enter 'exit' to quit the program.")

    # Initialize MINERVA
    minerva_client = MINERVA()
    
    console = Console()
    messages = []
    
    try:
        while True:
            # Get user input
            user_input = input("\n[You] ")
            
            # Check if user wants to exit
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("Goodbye!")
                break
            
            try:
                # Process the user input and output the response
                print("\n[Assistant]")
                with Live('', console=console, vertical_overflow='visible') as live:
                    # Pass the MINERVA client as a dependency
                    deps = MINERVADependencies(minerva_client=minerva_client)
                    
                    async with minerva_agent.run_stream(
                        user_input, message_history=messages, deps=deps
                    ) as result:
                        curr_message = ""
                        async for message in result.stream_text(delta=True):
                            curr_message += message
                            live.update(Markdown(curr_message))
                    
                    # Add the new messages to the chat history
                    messages.extend(result.all_messages())
                
            except Exception as e:
                print(f"\n[Error] An error occurred: {str(e)}")
    finally:
        print("\nMINERVA agent closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        raise
