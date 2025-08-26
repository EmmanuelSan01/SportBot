import logging
from typing import List, Dict, Any, Optional
import asyncio

from app.config import Config
from app.services.qdrant import QdrantService
from app.services.embedding import EmbeddingService
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# ==============================
# Clase 1: Agente Hardcoded
# ==============================
class TaekwondoAgent:
    
    # Agente especializado en productos de Taekwondo 
    
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
        
        # Prompt especializado exclusivamente en productos de Taekwondo
        
        return """
## IDENTIDAD - BaekhoBot: Especialista en Productos de Taekwondo 🛍️

Eres **BaekhoBot**, el asistente comercial más especializado en **PRODUCTOS DE TAEKWONDO** del mundo. Tu único enfoque es ser el experto definitivo en equipamiento, gear y accesorios para practicantes de Taekwondo.

**Tu expertise se centra EXCLUSIVAMENTE en:**
- 🥋 **PRODUCTOS**: Doboks, cinturones, protecciones, accesorios
- 💰 **COMERCIAL**: Precios, promociones, comparaciones, recomendaciones
- 📏 **ESPECIFICACIONES**: Tallas, materiales, durabilidad, uso apropiado
- 🛒 **ASESORÍA DE COMPRA**: Qué comprar según nivel, edad, presupuesto

**CATÁLOGO DE PRODUCTOS ESPECIALIZADO 🛍️**

=====================
🥋 DOBOKS (UNIFORMES)
=====================

(...)

==================
🏅 CINTURONES (TI)
==================

(...)

=========================
🛡️ PROTECCIONES COMPLETAS
=========================

(...)

===========================
🥊 EQUIPOS DE ENTRENAMIENTO
===========================

(...)

==================================
PROMOCIONES Y SISTEMA COMERCIAL 💰
==================================

(...)

=========================
CALENDARIO DE PROMOCIONES
=========================

(...)

===================================
ASESORÍA ESPECIALIZADA POR PERFIL 🎯
===================================

(...)

=========
POR EDAD:
=========

(...)

==================================
ESTILO DE COMUNICACIÓN COMERCIAL 🗣️
==================================

(...)

=========================
PROTOCOLO DE RESPUESTAS 📋
=========================

(...)
        """.strip()
    
    def _get_product_knowledge(self) -> Dict[str, Any]:
        
        # Base de conocimiento especializada en productos
        
        return {
            "doboks": {
                
            },
            "protecciones": {
                
            },
            "cinturones": {
                
            },
            "accesorios": {
                
            },
            "promociones_activas": {
                
            }
        }
    
    def _detect_user_intent(self, message: str) -> Dict[str, Any]:
        
        # Detecta intenciones comerciales y de productos específicamente
        
        message_lower = message.lower()
        
        intents = {
            
        }
        
        detected_intents = []
        confidence = 0
        
        for intent, keywords in intents.items():
            matches = sum(1 for keyword in keywords if keyword in message_lower)
            if matches > 0:
                detected_intents.append(intent)
                confidence += matches
        
        return {
            "primary_intent": detected_intents[0] if detected_intents else "general",
            "all_intents": detected_intents,
            "confidence": confidence / len(message.split()) if message.split() else 0,
            "message_type": self._classify_message_type(message_lower)
        }
    
    def _classify_message_type(self, message: str) -> str:
        
        # Clasifica mensajes para respuestas comerciales apropiadas
        
        if any(word in message for word in ["?", "que", "como", "donde", "cuando", "cuanto"]):
            return "question"
        elif any(word in message for word in ["quiero", "necesito", "busco", "me interesa"]):
            return "purchase_intent"
        elif any(word in message for word in ["gracias", "perfecto", "excelente", "genial"]):
            return "positive_feedback"
        elif any(word in message for word in ["caro", "costoso", "barato", "economic"]):
            return "price_concern"
        else:
            return "general_inquiry"
    
    async def process_message(
        self, 
        message: str, 
        user_info: Dict[str, Any] = None, 
        context: Optional[str] = None,
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        
        # Procesa mensajes con enfoque exclusivo en productos
        
        try:
            # Analizar intención comercial
            intent_analysis = self._detect_user_intent(message)
            
            # Construir prompt comercial especializado
            commercial_prompt = self._build_commercial_prompt(
                message, user_info, intent_analysis
            )
            
            # Procesar con LLM o usar respuestas especializadas
            if self.primary_provider == "openai" and self.openai_client:
                response = await self._process_with_openai(commercial_prompt, intent_analysis)
            else:
                response = self._get_product_focused_fallback(message, intent_analysis)
            # Post-procesar para enfoque comercial
            return self._post_process_commercial_response(response, intent_analysis)
                
        except Exception as e:
            logger.error(f"Error procesando consulta comercial: {str(e)}")
            return self._get_commercial_error_response()
    
    def _build_commercial_prompt(
        self, 
        message: str, 
        user_info: Dict[str, Any] = None,
        intent_analysis: Dict[str, Any] = None
    ) -> str:
        
        prompt_parts = []
        
        # Contexto comercial
        prompt_parts.append("CONSULTA COMERCIAL DE PRODUCTOS DE TAEKWONDO")
        
        if intent_analysis:
            prompt_parts.append(f"INTENCIÓN: {intent_analysis['primary_intent']}")
            prompt_parts.append(f"TIPO: {intent_analysis['message_type']}")
        
        # Información del cliente para personalizar recomendaciones
        if user_info:
            prompt_parts.append(f"CLIENTE: {user_info.get('first_name', 'Usuario')}")
        
        # Mensaje del cliente
        prompt_parts.append(f"CONSULTA: {message}")
        
        # Instrucciones específicas según intención
        commercial_instructions = {
            
        }
        
        primary_intent = intent_analysis.get('primary_intent') if intent_analysis else None
        if primary_intent in commercial_instructions:
            prompt_parts.append(commercial_instructions[primary_intent])
        
        prompt_parts.append("\nIMPORTANTE: Incluye precios, promociones aplicables y alternativas para diferentes presupuestos.")
        
        return "\n".join(prompt_parts)
    
    async def _process_with_openai(self, prompt: str, intent_analysis: Dict[str, Any] = None) -> str:
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",   
                messages=messages,
                max_tokens=800,
                temperature=0.4,
                top_p=0.9,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
        
        except asyncio.TimeoutError:
            raise Exception("Timeout al procesar consulta comercial")
        except Exception as e:
            logger.error(f"Error con OpenAI en consulta comercial: {str(e)}")
            raise e
    
    def _get_product_focused_fallback(self, message: str, intent_analysis: Dict[str, Any]) -> str:
        
        # Respuestas fallback especializadas en productos únicamente
        
        primary_intent = intent_analysis.get('primary_intent', 'general')
        message_lower = message.lower()
        
        if primary_intent == "greeting":
            return """🛍️ ¡Hola! Soy **BaekhoBot**, tu especialista personal en productos de Taekwondo.

(...)
¿Qué necesitas para tu práctica de Taekwondo? 🤔"""
        
        elif primary_intent == "dobok_inquiry":
            return """🥋 **DOBOKS DISPONIBLES - CATÁLOGO COMPLETO**

(...)
¿Cuál es tu nivel y qué tipo de uso le darás? Te recomiendo la opción perfecta. 🎯"""
        
        elif primary_intent == "protection_inquiry":
            return """🛡️ **PROTECCIONES COMPLETAS - GUÍA ESPECIALIZADA**

(...)
¿Para qué tipo de entrenamiento necesitas protección? 🤔"""
        
        elif primary_intent == "price_inquiry":
            return """💰 **GUÍA COMPLETA DE PRECIOS - TAEKWONDO GEAR**

(...)
¿Cuál es tu presupuesto aproximado? Te armo la mejor combinación. 🎯"""
        
        elif primary_intent == "promotion_inquiry":
            return """🎉 **PROMOCIONES ESPECIALES ACTIVAS**

(...)
¿Cuál promoción te interesa más? 🛒"""
        
        elif primary_intent == "recommendation":
            return """🎯 **RECOMENDACIONES PERSONALIZADAS**

(...)
¡Cuéntame más detalles y te doy la recomendación perfecta! 📋"""
        
        elif primary_intent == "size_inquiry":
            return """📏 **GUÍA COMPLETA DE TALLAS - TODAS LAS CATEGORÍAS**

(...)
¿Necesitas ayuda midiendo alguna talla específica? 📋"""
        
        elif primary_intent == "beginner_gear":
            return """🌱 **PACK COMPLETO PARA PRINCIPIANTES**

(...)
¿Cuántos años tienes y cuál es tu presupuesto inicial? Te armo el pack perfecto. 🎒"""
        
        elif primary_intent == "competition_gear":
            return """🏆 **EQUIPAMIENTO PARA COMPETICIÓN OFICIAL**

(...)
¿En qué nivel vas a competir? Te armo el paquete exacto que necesitas. 🥇"""

        else:
            return """🛍️ ¡Hola! Soy **BaekhoBot**, tu especialista en productos de Taekwondo.

(...)"""
    
    def _post_process_commercial_response(self, response: str, intent_analysis: Dict[str, Any]) -> str:
        
        # Post-proceso de respuestas para mantener enfoque comercial
        
        # Asegurar emojis comerciales apropiados
        if not any(emoji in response for emoji in ["🛍️", "💰", "🎯", "📏", "🎉"]):
            response = "🛍️ " + response
        
        # Añadir llamadas a la acción comerciales
        commercial_ctas = {
            
        }
        
        primary_intent = intent_analysis.get('primary_intent', 'general')
        if primary_intent in commercial_ctas and len(response) < 1200:
            response += commercial_ctas[primary_intent]
        
        return response.strip()
    
    def _get_commercial_error_response(self) -> str:
        
        # Respuesta de error manteniendo enfoque comercial
        
        return """🛍️ ¡Ups! Pequeño problema técnico en nuestro sistema de productos...

¡Intenta tu consulta de nuevo en unos segundos! Estoy ansioso por ayudarte a encontrar el equipamiento perfecto. 🎒✨"""
    
    def get_model_info(self) -> dict:
        
        # Información del modelo enfocada en capacidades comerciales
        
        return {
            "provider": self.primary_provider,
            "available": self.is_available(),
            "openai_configured": bool(self.openai_client),
            "model": "gpt-4o-mini" if self.primary_provider == "openai" else "unknown",
            "commercial_capabilities": {
            
            },
            
            "price_ranges": {
            
            }
        }
    
    def is_available(self) -> bool:
        return self.primary_provider is not None
    
    async def get_product_recommendations(self, user_query: str, user_level: str = "", budget: str = "") -> str:
        
        # Recomendaciones de productos específicas basadas en parámetros comerciales
        
        recommendation_prompt = f"""
(...)
        """
        
        return await self.process_message(recommendation_prompt)
    
    async def compare_products(self, product_type: str, comparison_criteria: str = "price") -> str:
        
        # Comparación detallada entre productos similares
        
        comparison_prompt = f"""
(...)
        """
        return await self.process_message(comparison_prompt)

# ==============================
# Clase 2: Agente RAG (Qdrant)
# ==============================

class AgentService:
    def __init__(self):
        # ... (other initializations) ...
        self.qdrant_service = QdrantService()
        self.embedding_service = EmbeddingService()
        self.openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

    async def process_query(self, query: str, user_id: str, context: Optional[Dict] = None) -> str:
        """
        Procesa una consulta del usuario usando RAG (Qdrant + embeddings)
        """
        try:
            query_embedding = await self.embedding_service.generate_embedding(query)

            # Remove 'await' here because search_similar() returns a list, not a coroutine.
            relevant_docs = self.qdrant_service.search_similar(
                query_embedding,
                limit=5
            )

            context_text = self._build_context(relevant_docs, context)

            response = await self._generate_response(query, context_text, user_id)

            return response

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return None

    def _build_context(self, relevant_docs: List[Dict], additional_context: Optional[Dict] = None) -> str:
        context_parts = []

        if relevant_docs:
            context_parts.append("📦 Información de productos relevantes de la base de datos:")
            for doc in relevant_docs:
                payload = doc.get("payload", {})
                context_parts.append(f"- {payload.get('nombre', 'N/A')}: {payload.get('descripcion', 'N/A')}")
                context_parts.append(f"  💰 Precio: {payload.get('precio', 'N/A')}")
                context_parts.append(f"  📂 Categoría: {payload.get('categoria', 'N/A')}")

        if additional_context:
            context_parts.append("\nℹ️ Información adicional:")
            for key, value in additional_context.items():
                context_parts.append(f"- {key}: {value}")

        return "\n".join(context_parts)

    async def _generate_response(self, query: str, context: str, user_id: str) -> str:
        system_prompt = """
        (...)
        """

        user_prompt = f"""
        Consulta: {query}

        Contexto disponible:
        {context}
        """

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=600,
                temperature=0.5
            )

            return {
                "reply": response.choices[0].message.content.strip(),
                "sources": [], # You can populate this with relevant info from context
                "relevance_score": 0.0 # You can calculate this based on the search
            }

        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {str(e)}")
            return None

    async def get_product_recommendations(self, category: str, budget: Optional[float] = None) -> List[Dict]:
        try:
            search_query = f"productos de {category}"
            if budget:
                search_query += f" con precio menor a {budget}"

            query_embedding = await self.embedding_service.generate_embedding(search_query)

            results = await self.qdrant_service.search_similar(
                query_embedding,
                limit=10,
                collection_name="productos"
            )

            recommendations = []
            for result in results:
                payload = result.get("payload", {})
                precio = payload.get("precio", 0)

                if budget is None or precio <= budget:
                    recommendations.append({
                        "id": payload.get("id"),
                        "nombre": payload.get("nombre"),
                        "descripcion": payload.get("descripcion"),
                        "precio": precio,
                        "categoria": payload.get("categoria"),
                        "score": result.get("score", 0),
                    })

            return recommendations[:5]

        except Exception as e:
            logger.error(f"Error getting product recommendations: {str(e)}")
            return []


# ==============================
# Clase 3: Orquestador
# ==============================

class BaekhoAgent:
    """
    Orquesta entre el agente RAG (dinámico) y el agente hardcoded (fallback).
    """
    def __init__(self):
        self.rag_agent = AgentService()
        self.hardcoded_agent = TaekwondoAgent()

    async def process_message(self, message: str, user_info: Dict[str, Any] = None) -> str:
        # 1️⃣ Intentamos primero con RAG (Qdrant)
        response = await self.rag_agent.process_query(message, user_info.get("id", "anonimo"))

        # 2️⃣ Si RAG no devuelve nada, usamos fallback hardcoded
        if not response:
            logger.info("⚠️ Usando fallback hardcoded de TaekwondoAgent")
            response = await self.hardcoded_agent.process_message(message, user_info)

        return response

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "rag_available": True,
            "fallback_available": self.hardcoded_agent.is_available(),
            "models": {
                "rag": "gpt-4o-mini + Qdrant",
                "hardcoded": "gpt-4o-mini (catálogo estático)"
            }
        }
