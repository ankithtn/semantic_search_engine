from groq import Groq
from typing import List
import time

from ..models.search import SearchResult
from ..config.settings import settings

class LLMService:
    """Service for handling LLM-based answer generation using Groq API"""
    
    def __init__(self):
        """Initialize Groq client"""
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment variables")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        print(f"LLm Service initialized with model: {self.model}")

    def generate_answer(
        self,
        query: str,
        papers: List[SearchResult],
        max_papers: int = 5
    ) -> dict:
        """
        Generate an AI answer based on retrieved papers

        Args:
            query: User's search query/question
            papers: List of retrieved SearchResult objects
            max_papers: Maximum number of papers to include in context
        
        Returns:
            dict with 'answer', 'model', 'tokens_used', 'generation_time'
        """
        start_time = time.time()

        try:
            # Build context from papers
            context = self._build_context(papers[:max_papers])

            # create the prompt
            prompt = self._create_prompt(query, context, len(papers[:max_papers]))

            # Call groq API
            response = self.client.chat.completions.create(
                model = self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful medical research assistant. Your task is to answer questions based on provided research papers. Always cite sources using [1], [2], etc. Be accurate and concise."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=settings.GROQ_MAX_TOKENS,
                top_p=1,
                stream=False
            )

            generation_time = time.time() - start_time

            # Extract answer
            answer = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0

            print(f"Generated answer in {generation_time: 2f}s using {tokens_used} tokens")

            return {
                "answer": answer,
                "model": self.model,
                "tokens_used": tokens_used,
                "generation_time": round(generation_time, 3)
            }
        
        except Exception as e:
            print(f"LLM generation errro: {e}")
            # Return a fallback message instead of crashing
            return {
                "answer": f"I apologize, but I encountered an error generating an answer: {str(e)}. Please try rephrasing your question or contact suppor if the issue persists.",
                "model": self.model,
                "tokens_used": 0,
                "generation_time": round(time.time() - start_time, 3),
                "error": str(e)
            }
        
    def _build_context(self, papers: List[SearchResult]) -> str:
        """
        Format papers into context string for LLM
        
        Args:
            papers: List of SearchResult objects
        
        Returns:
            Formatted context string
        """
        context_parts = []

        for i, paper in enumerate(papers, 1):
            # Truncate abstract if too long (first 600 chars)
            abstract = paper.abstract[:600] + "..." if len(paper.abstract) > 600 else paper.abstract

            paper_text = f"""[{i}] Title: {paper.title}
Journal: {paper.journal or 'N/A'} ({paper.year or 'N/A'})
PMID: {paper.pmid or 'N/A'}
Abstract: {abstract}
Relevance Score: {paper.score:.3f if paper.score else 'N/A'}
"""
            context_parts.append(paper_text)
        
        return "\n---\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str, num_papers: int) -> str:
        """
        Create the prompt for the LLM
        
        Args:
            query: User's question
            context: Formatted papers context
            num_papers: Number of papers included
        
        Returns:
            Complete prompt string
        """
        prompt = f"""You are analyzing medical research papers to answer a question. Below are{num_papers} relevant research papers retrieved from a database. 

USER QUESTION: {query}

RESEARCH PAPERS:
{context}

INSTRUCTIONS:
1. Answer the question based ONLY on the information provided in these papers
2. Use inline citations like [1], [2], [3] to reference specific papers
3. If multiple papers support a point, cite all of them: [1][2]
4. Be concise but comprehensive
5. If the papers don't contain enough information to fully answer the question, acknowledge this
6. Structure your answer clearly with key points
7. Do NOT make up information not present in the papers

Please provide your answer now:"""
        return prompt

    def test_connection(self) -> bool:
        """
        Test if Groq API is accessible
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )
            print(" Groq API connection successful")
            return True
        except Exception as e:
            print(f" Groq API connection failed: {e}")
            return False

# Global instance (will be initialized when app starts)
llm_service = None

def initialize_llm_service():
    """Initialize the global LLM service instance"""
    global llm_service
    try:
        llm_service = LLMService()
        llm_service.test_connection()
        return llm_service
    except Exception as e:
        print(f"Failed to initialize LLM service: {e}")
        print(" Running without LLm capabilities")
        return None

def get_llm_service():
    """Get the global LLM service instance"""
    return llm_service
