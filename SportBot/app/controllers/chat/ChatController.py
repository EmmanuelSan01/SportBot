from typing import List, Optional, Dict
import pymysql
from app.database import get_sync_connection
from app.models.chat.ChatModel import ChatCreate, ChatUpdate, ChatResponse
from app.services.agent import AgentService
from app.services.data_sync import DataSyncService

class ChatController:
    
    def __init__(self):
        self.agent_service = AgentService()
        self.data_sync_service = DataSyncService()
    
    async def process_message(self, message: str, user_id: Optional[int] = None) -> Dict:
        """Process message using RAG instead of direct SQL queries"""
        try:
            # Use RAG to process the query
            response = await self.agent_service.process_query(message, user_id)
            
            # Store conversation in database if user_id provided
            if user_id:
                await self._store_conversation(user_id, message, response.get("reply", ""))
            
            return {
                "status": "success",
                "message": "Consulta procesada exitosamente",
                "data": {
                    "reply": response.get("reply", ""),
                    "sources": response.get("sources", []),
                    "relevance_score": response.get("relevance_score", 0.0),
                    "context_used": response.get("context_used", [])
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error procesando mensaje: {str(e)}",
                "data": {
                    "reply": "Lo siento, ocurrió un error procesando tu consulta. Por favor intenta nuevamente.",
                    "sources": [],
                    "relevance_score": 0.0
                }
            }
    
    async def _store_conversation(self, user_id: int, user_message: str, bot_response: str):
        """Store conversation in database for persistence"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                # Update or create chat record
                sql_check = "SELECT id FROM chat WHERE usuarioId = %s ORDER BY fechaCreacion DESC LIMIT 1"
                cursor.execute(sql_check, (user_id,))
                chat_record = cursor.fetchone()
                
                if chat_record:
                    # Update existing chat
                    sql_update = """
                    UPDATE chat 
                    SET ultimoMensaje = %s, totalMensajes = totalMensajes + 1 
                    WHERE id = %s
                    """
                    cursor.execute(sql_update, (user_message, chat_record['id']))
                else:
                    # Create new chat
                    sql_insert = """
                    INSERT INTO chat (usuarioId, chatId, ultimoMensaje, totalMensajes) 
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql_insert, (user_id, f"chat_{user_id}", user_message, 1))
                
                connection.commit()
                
        finally:
            connection.close()
    
    @staticmethod
    def create_chat(chat: ChatCreate) -> ChatResponse:
        """Create a new chat"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO chat (usuarioId, chatId, ultimoMensaje, totalMensajes) 
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    chat.usuarioId, chat.chatId, chat.ultimoMensaje, chat.totalMensajes
                ))
                connection.commit()
                
                chat_id = cursor.lastrowid
                return ChatController.get_chat_by_id(chat_id)
        finally:
            connection.close()
    
    @staticmethod
    def get_all_chats() -> List[ChatResponse]:
        """Get all chats"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM chat ORDER BY fechaCreacion DESC"
                cursor.execute(sql)
                result = cursor.fetchall()
                return [ChatResponse(**row) for row in result]
        finally:
            connection.close()
    
    @staticmethod
    def get_chat_by_id(chat_id: int) -> Optional[ChatResponse]:
        """Get chat by ID"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM chat WHERE id = %s"
                cursor.execute(sql, (chat_id,))
                result = cursor.fetchone()
                return ChatResponse(**result) if result else None
        finally:
            connection.close()
    
    @staticmethod
    def get_chats_by_usuario(usuario_id: int) -> List[ChatResponse]:
        """Get chats by usuario"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM chat WHERE usuarioId = %s ORDER BY fechaCreacion DESC"
                cursor.execute(sql, (usuario_id,))
                result = cursor.fetchall()
                return [ChatResponse(**row) for row in result]
        finally:
            connection.close()
    
    @staticmethod
    def update_chat(chat_id: int, chat: ChatUpdate) -> Optional[ChatResponse]:
        """Update chat"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                update_fields = []
                values = []
                
                if chat.ultimoMensaje is not None:
                    update_fields.append("ultimoMensaje = %s")
                    values.append(chat.ultimoMensaje)
                
                if chat.totalMensajes is not None:
                    update_fields.append("totalMensajes = %s")
                    values.append(chat.totalMensajes)
                
                if not update_fields:
                    return ChatController.get_chat_by_id(chat_id)
                
                values.append(chat_id)
                sql = f"UPDATE chat SET {', '.join(update_fields)} WHERE id = %s"
                cursor.execute(sql, values)
                connection.commit()
                
                return ChatController.get_chat_by_id(chat_id)
        finally:
            connection.close()
    
    @staticmethod
    def delete_chat(chat_id: int) -> bool:
        """Delete chat"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM chat WHERE id = %s"
                cursor.execute(sql, (chat_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()
