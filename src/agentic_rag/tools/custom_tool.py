import os
import requests
from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field, ConfigDict
from markitdown import MarkItDown
from chonkie import SemanticChunker
from qdrant_client import QdrantClient
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class FireCrawlWebSearchTool(BaseTool):
    """
    A tool to perform web searches using the FireCrawl API.
    """
    name: str = "FireCrawlWebSearchTool"
    description: str = "Search the web using FireCrawl API."
    api_key: str = Field(default_factory=lambda: os.getenv('FIRECRAWL_API_KEY', 'YOUR_FIRECRAWL_API_KEY'),)
    base_url: str = "https://api.firecrawl.dev/v1/search"
    
    def __init__(self, **kwargs):
        # Pydantic-compatible initialization
        super().__init__(**kwargs)

        if not self.api_key:
            raise ValueError("FireCrawl API key is required.")

        

    def search(self, query: str, limit: int = 1):
        """
        Perform a web search using the FireCrawl API.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": query,
            "limit": limit
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Parse and return search results
            return [
                {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", "")
                }
                for result in data.get("data", [])
            ]
        except requests.exceptions.RequestException as e:
            print(f"Web search error: {e}")
            return []

    def _run(self, query: str):
        """
        Perform a web search and return results.
        """
        return self.search(query)
 
class DocumentSearchToolInput(BaseModel):
    """Input schema for DocumentSearchTool."""
    query: str = Field(..., description="Query to search the document.")

class DocumentSearchTool(BaseTool):
    name: str = "DocumentSearchTool"
    description: str = "Search the document for the given query."
    args_schema: Type[BaseModel] = DocumentSearchToolInput
    
    model_config = ConfigDict(extra="allow")
    
    def __init__(self, file_path: str):
        """Initialize the searcher with a PDF file path and set up the Qdrant collection."""
        super().__init__()
        self.file_path = file_path
        self.collection_name = "demo_collection"
        self.client = QdrantClient(":memory:")  # For small experiments
        self._process_document()

    def _extract_text(self) -> str:
        """Extract raw text from PDF using MarkItDown."""
        try:
            md = MarkItDown()
            result = md.convert(self.file_path)
            return result.text_content
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def _create_chunks(self, raw_text: str) -> list:
        """Create semantic chunks from raw text."""
        chunker = SemanticChunker(
            embedding_model="minishlab/potion-base-8M",
            threshold=0.5,
            chunk_size=512,
            min_sentences=1
        )
        return chunker.chunk(raw_text)

    def _process_document(self):
        """Process the document and add chunks to Qdrant collection."""
        raw_text = self._extract_text()
        chunks = self._create_chunks(raw_text)
        
        docs = [chunk.text for chunk in chunks]
        metadata = [{"source": os.path.basename(self.file_path)} for _ in range(len(chunks))]
        ids = list(range(len(chunks)))

        self.client.add(
            collection_name="demo_collection",
            documents=docs,
            metadata=metadata,
            ids=ids
        )
        
    def _run(self, query: str) -> list:
        """Search the document with a query string."""
        relevant_chunks = self.client.query(
            collection_name="demo_collection",
            query_text=query
        )
        docs = [chunk.document for chunk in relevant_chunks]
        separator = "\n___\n"
        return separator.join(docs)


    def search_with_fallback(self, web_tool, query: str) -> dict:
        """
        Search the document and fallback to web search if no relevant results are found.
        """
        # Step 1: Search the document
        try:
            document_results = self._run(query)  # Assuming _run handles document search
            if document_results and document_results != "No results found in the document.":
                # Check if the results are relevant to the query
                relevant_results = [
                    result for result in document_results.split("\n___\n") if query.lower() in result.lower()
                ]
                if relevant_results:
                    print("Search results found in document.")
                    return {"source": "document", "results": relevant_results}
                else:
                    print("No relevant results found in document. Falling back to web search...")
        except Exception as e:
            print(f"Error during document search: {e}")

        # Step 2: Fallback to web search
        print("No relevant results found in document. Falling back to web search...")
        try:
            web_results = web_tool.search(query)  # Assuming web_tool.search is well-implemented
            if web_results and len(web_results) > 0:
                print("Search results found on the web.")
                # Format web results for consistency
                formatted_web_results = []
                for result in web_results:
                    # Ensure the result contains the required fields
                    if "title" in result and "url" in result and "description" in result:
                        formatted_web_results.append({
                            "title": result["title"],
                            "link": result["url"],
                            "snippet": result["description"]
                        })
                    else:
                        print(f"Skipping invalid result: {result}")
                return {"source": "web", "results": formatted_web_results}
            else:
                print("No results found in web search.")
                return {"source": "none", "results": ["No results found for your query."]}
        except Exception as e:
            print(f"Error during web search: {e}")
            return {"source": "none", "results": ["An error occurred during the web search."]}


        # Test the implementation
def test_document_searcher():
    # Test file path
    pdf_path = "/agentic_rag/knowledge/Smart Wardrobe_ipd paper.pdf"
    
    # Create instance
    searcher = DocumentSearchTool(file_path=pdf_path)
    
    # Test search
    result = searcher.search(pdf_path, "What is the purpose of DSpy?")
    print("Search Results:", result)


if __name__ == "__main__":
    test_document_searcher()
