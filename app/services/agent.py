import logging
from typing import List, Dict, Any, Optional
import asyncio

from app.config import Config
from app.services.qdrant import QdrantService
from app.services.embedding import EmbeddingService
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class TaekwondoAgent:
       
    def __init__(self):
        self.openai_client = None
        
        if Config.OPENAI_API_KEY:
            try:
                self.openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
                self.primary_provider = "openai"
                logger.info("✅ Cliente OpenAI inicializado")
            except Exception as e:
                logger.error(f"Error inicializando OpenAI: {e}")
        else:
            logger.warning("⚠️ No se encontró configuración válida para LLM")
            self.primary_provider = None
        
        self.system_prompt = self._build_system_prompt()
        self.product_knowledge = self._get_product_knowledge()
        
    def _build_system_prompt(self) -> str:        
    
    def _get_product_knowledge(self) -> Dict[str, Any]:        
    
    def _detect_user_intent(self, message: str) -> Dict[str, Any]:
    
    def _classify_message_type(self, message: str) -> str:
                   
    async def process_message(
        self, 
        message: str, 
        user_info: Dict[str, Any] = None, 
        context: Optional[str] = None,
        chat_history: List[Dict[str, str]] = None
    ) -> str:
    
    def _build_commercial_prompt(message, user_info, intent_analysis)
    
    async def _process_with_openai(self, prompt: str, intent_analysis: Dict[str, Any] = None) -> str:

    def _get_product_focused_fallback(self, message: str, intent_analysis: Dict[str, Any]) -> str:
    
    def _post_process_commercial_response(self, response: str, intent_analysis: Dict[str, Any]) -> str:

    def _get_commercial_error_response(self) -> str:
    
    def get_model_info(self) -> dict:
    
    def is_available(self) -> bool:
    
    async def get_product_recommendations(self, user_query: str, user_level: str = "", budget: str = "") -> str:
    
    async def compare_products(self, product_type: str, comparison_criteria: str = "price") -> str:

class AgentService:
    def __init__(self):

    async def process_query(self, query: str, user_id: str, context: Optional[Dict] = None) -> str:

    def _build_context(self, relevant_docs: List[Dict], additional_context: Optional[Dict] = None) -> str:

    async def _generate_response(self, query: str, context: str, user_id: str) -> str:

    async def get_product_recommendations(self, category: str, budget: Optional[float] = None) -> List[Dict]:

class BaekhoAgent:
    def __init__(self):
        self.rag_agent = AgentService()
        self.hardcoded_agent = TaekwondoAgent()

    async def process_message(self, message: str, user_info: Dict[str, Any] = None) -> str:

    def get_model_info(self) -> Dict[str, Any]:
