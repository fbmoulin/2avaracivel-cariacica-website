"""
Asynchronous Chatbot Service for 2ª Vara Cível de Cariacica
Enhanced performance with async OpenAI integration and concurrent processing
"""

import asyncio
import aiohttp
import openai
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import time
from utils.async_handler import async_handler
from models import ChatMessage, db

logger = logging.getLogger('async_chatbot')

class AsyncChatbotService:
    """Asynchronous chatbot service with OpenAI integration"""
    
    def __init__(self):
        self.client = None
        self.conversation_cache = {}
        self.response_cache = {}
        self.max_cache_size = 1000
        self.processing_queue = asyncio.Queue()
        self.is_processing = False
        
    async def initialize(self):
        """Initialize async OpenAI client"""
        try:
            import os
            api_key = os.environ.get('OPENAI_API_KEY')
            if api_key:
                self.client = openai.AsyncOpenAI(api_key=api_key)
                logger.info("Async OpenAI client initialized successfully")
            else:
                logger.warning("OpenAI API key not found")
        except Exception as e:
            logger.error(f"Failed to initialize async OpenAI client: {e}")
    
    async def get_response(self, message: str, conversation_id: Optional[str] = None) -> Dict:
        """Get async chatbot response with caching and optimization"""
        start_time = time.time()
        
        # Check cache first
        cache_key = f"{message}_{conversation_id}"
        if cache_key in self.response_cache:
            cached_response = self.response_cache[cache_key]
            logger.info(f"Cache hit for message: {message[:50]}...")
            return {
                'response': cached_response['response'],
                'cached': True,
                'processing_time': time.time() - start_time,
                'conversation_id': conversation_id
            }
        
        try:
            # Get conversation context
            context = await self._get_conversation_context(conversation_id)
            
            # Prepare messages for OpenAI
            messages = await self._prepare_messages(message, context)
            
            # Get OpenAI response asynchronously
            response = await self._get_openai_response(messages)
            
            # Save to database asynchronously
            await self._save_message_async(message, response, conversation_id)
            
            # Cache the response
            self._cache_response(cache_key, response)
            
            processing_time = time.time() - start_time
            
            return {
                'response': response,
                'cached': False,
                'processing_time': processing_time,
                'conversation_id': conversation_id,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error getting chatbot response: {e}")
            return {
                'response': "Desculpe, estou enfrentando dificuldades técnicas. Tente novamente em alguns momentos.",
                'error': str(e),
                'processing_time': time.time() - start_time,
                'success': False
            }
    
    async def _get_openai_response(self, messages: List[Dict]) -> str:
        """Get response from OpenAI API asynchronously"""
        if not self.client:
            await self.initialize()
        
        if not self.client:
            raise Exception("OpenAI client not available")
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                timeout=30
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _prepare_messages(self, user_message: str, context: List[Dict]) -> List[Dict]:
        """Prepare message array for OpenAI with context"""
        system_message = {
            "role": "system",
            "content": """Você é um assistente virtual da 2ª Vara Cível de Cariacica. 
            Ajude os usuários com informações sobre processos judiciais, agendamentos, 
            serviços do tribunal e questões relacionadas ao direito civil. 
            Seja profissional, útil e forneça informações precisas."""
        }
        
        messages = [system_message]
        
        # Add conversation context
        for ctx in context[-10:]:  # Last 10 messages for context
            messages.append({"role": "user", "content": ctx['user_message']})
            messages.append({"role": "assistant", "content": ctx['bot_response']})
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    async def _get_conversation_context(self, conversation_id: Optional[str]) -> List[Dict]:
        """Get conversation context asynchronously"""
        if not conversation_id:
            return []
        
        # Check cache first
        if conversation_id in self.conversation_cache:
            return self.conversation_cache[conversation_id]
        
        # Get from database asynchronously
        try:
            context = await async_handler.async_database_operation(
                self._fetch_conversation_from_db,
                conversation_id
            )
            
            if context['success']:
                self.conversation_cache[conversation_id] = context['result']
                return context['result']
            else:
                logger.error(f"Failed to fetch conversation context: {context['error']}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching conversation context: {e}")
            return []
    
    def _fetch_conversation_from_db(self, conversation_id: str) -> List[Dict]:
        """Fetch conversation from database (sync operation)"""
        try:
            messages = ChatMessage.query.filter_by(
                conversation_id=conversation_id
            ).order_by(ChatMessage.created_at.desc()).limit(20).all()
            
            return [
                {
                    'user_message': msg.user_message,
                    'bot_response': msg.bot_response,
                    'created_at': msg.created_at.isoformat()
                }
                for msg in reversed(messages)
            ]
        except Exception as e:
            logger.error(f"Database error fetching conversation: {e}")
            return []
    
    async def _save_message_async(self, user_message: str, bot_response: str, conversation_id: Optional[str]):
        """Save chat message to database asynchronously"""
        try:
            await async_handler.async_database_operation(
                self._save_message_to_db,
                user_message,
                bot_response,
                conversation_id
            )
        except Exception as e:
            logger.error(f"Error saving message to database: {e}")
    
    def _save_message_to_db(self, user_message: str, bot_response: str, conversation_id: Optional[str]):
        """Save message to database (sync operation)"""
        try:
            chat_message = ChatMessage(
                user_message=user_message,
                bot_response=bot_response,
                conversation_id=conversation_id or f"conv_{int(time.time())}",
                created_at=datetime.utcnow()
            )
            
            db.session.add(chat_message)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Database error saving message: {e}")
            db.session.rollback()
            raise
    
    def _cache_response(self, cache_key: str, response: str):
        """Cache response with size management"""
        if len(self.response_cache) >= self.max_cache_size:
            # Remove oldest entries
            oldest_keys = list(self.response_cache.keys())[:100]
            for key in oldest_keys:
                del self.response_cache[key]
        
        self.response_cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
    
    async def batch_process_messages(self, messages: List[Dict]) -> List[Dict]:
        """Process multiple messages in parallel"""
        tasks = []
        
        for msg_data in messages:
            task = self.get_response(
                msg_data['message'],
                msg_data.get('conversation_id')
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) else {
                'error': str(result),
                'success': False
            }
            for result in results
        ]
    
    async def get_conversation_summary(self, conversation_id: str) -> Dict:
        """Get async conversation summary"""
        try:
            context = await self._get_conversation_context(conversation_id)
            
            if not context:
                return {'summary': 'Nenhuma conversa encontrada', 'message_count': 0}
            
            # Create summary prompt
            messages_text = "\n".join([
                f"Usuário: {msg['user_message']}\nAssistente: {msg['bot_response']}"
                for msg in context[-10:]
            ])
            
            summary_prompt = f"""Resuma a seguinte conversa em português de forma concisa:

{messages_text}

Resumo:"""
            
            summary = await self._get_openai_response([
                {"role": "user", "content": summary_prompt}
            ])
            
            return {
                'summary': summary,
                'message_count': len(context),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return {
                'summary': 'Erro ao gerar resumo',
                'error': str(e),
                'success': False
            }
    
    async def health_check(self) -> Dict:
        """Async health check for chatbot service"""
        try:
            if not self.client:
                await self.initialize()
            
            # Test with simple message
            start_time = time.time()
            test_response = await self._get_openai_response([
                {"role": "user", "content": "Teste de conectividade"}
            ])
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'openai_available': True,
                'response_time': response_time,
                'cache_size': len(self.response_cache),
                'conversation_cache_size': len(self.conversation_cache)
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'openai_available': False,
                'error': str(e)
            }
    
    async def clear_cache(self):
        """Clear all caches"""
        self.response_cache.clear()
        self.conversation_cache.clear()
        logger.info("Chatbot caches cleared")

# Global async chatbot service
async_chatbot_service = AsyncChatbotService()