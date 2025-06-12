"""
Optimized content service with intelligent caching and data management
High-performance content delivery with automatic cache invalidation
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from functools import wraps
import os

logger = logging.getLogger(__name__)


class ContentCache:
    """Intelligent content caching with TTL and dependency tracking"""
    
    def __init__(self):
        self.cache = {}
        self.dependencies = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached content with expiration check"""
        if key in self.cache:
            entry = self.cache[key]
            if entry['expires_at'] > datetime.utcnow():
                self.hits += 1
                return entry['data']
            else:
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, key: str, data: Any, ttl: int = 3600, dependencies: List[str] = None):
        """Cache content with TTL and dependency tracking"""
        self.cache[key] = {
            'data': data,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(seconds=ttl)
        }
        
        if dependencies:
            self.dependencies[key] = dependencies
    
    def invalidate(self, dependency: str):
        """Invalidate all cache entries that depend on a file"""
        keys_to_remove = []
        for key, deps in self.dependencies.items():
            if dependency in deps:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            self.cache.pop(key, None)
            self.dependencies.pop(key, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            'entries': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }


def cached_content(ttl: int = 3600, dependencies: List[str] = None):
    """Decorator for caching content loading functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # Try cache first
            cached_result = content_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Load fresh data
            try:
                result = func(*args, **kwargs)
                content_cache.set(cache_key, result, ttl, dependencies)
                return result
            except Exception as e:
                logger.error(f"Content loading failed for {func.__name__}: {e}")
                return None
        return wrapper
    return decorator


class OptimizedContentService:
    """High-performance content service with intelligent caching"""
    
    def __init__(self):
        self.data_path = 'data'
        self.cache = ContentCache()
        self.file_watchers = {}
    
    def _load_json_file(self, filename: str) -> Optional[Dict]:
        """Load JSON file with error handling"""
        try:
            filepath = os.path.join(self.data_path, filename)
            if not os.path.exists(filepath):
                logger.warning(f"File not found: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}")
            return None
    
    def _check_file_modified(self, filename: str) -> bool:
        """Check if file has been modified since last load"""
        try:
            filepath = os.path.join(self.data_path, filename)
            if not os.path.exists(filepath):
                return False
            
            current_mtime = os.path.getmtime(filepath)
            last_mtime = self.file_watchers.get(filename, 0)
            
            if current_mtime > last_mtime:
                self.file_watchers[filename] = current_mtime
                self.cache.invalidate(filename)
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking file modification for {filename}: {e}")
            return False
    
    @cached_content(ttl=1800, dependencies=['faq.json'])
    def get_faq_data(self) -> Dict[str, Any]:
        """Get FAQ data with intelligent caching"""
        self._check_file_modified('faq.json')
        
        faq_data = self._load_json_file('faq.json')
        if not faq_data:
            return self._get_default_faq()
        
        # Process and optimize FAQ data
        processed_faq = {}
        for category, questions in faq_data.items():
            processed_faq[category] = []
            for i, question in enumerate(questions):
                processed_faq[category].append({
                    'id': f"{category}_{i}",
                    'pergunta': question.get('pergunta', ''),
                    'resposta': question.get('resposta', ''),
                    'categoria': category,
                    'keywords': self._extract_keywords(question.get('pergunta', ''))
                })
        
        return processed_faq
    
    @cached_content(ttl=900, dependencies=['news.json'])
    def get_news_data(self) -> List[Dict[str, Any]]:
        """Get news data with caching and processing"""
        self._check_file_modified('news.json')
        
        news_data = self._load_json_file('news.json')
        if not news_data:
            return self._get_default_news()
        
        # Process news items
        processed_news = []
        for item in news_data.get('noticias', []):
            processed_item = {
                'id': len(processed_news) + 1,
                'titulo': item.get('titulo', ''),
                'resumo': item.get('resumo', ''),
                'conteudo': item.get('conteudo', ''),
                'data_publicacao': item.get('data_publicacao', datetime.utcnow().isoformat()),
                'ativo': item.get('ativo', True),
                'categoria': item.get('categoria', 'geral')
            }
            
            if processed_item['ativo']:
                processed_news.append(processed_item)
        
        # Sort by publication date (newest first)
        processed_news.sort(key=lambda x: x['data_publicacao'], reverse=True)
        
        return processed_news
    
    @cached_content(ttl=3600, dependencies=['services.json'])
    def get_services_data(self) -> Dict[str, Any]:
        """Get services data with caching"""
        self._check_file_modified('services.json')
        
        services_data = self._load_json_file('services.json')
        if not services_data:
            return self._get_default_services()
        
        return services_data
    
    @cached_content(ttl=1800)
    def get_homepage_content(self) -> Dict[str, Any]:
        """Get optimized homepage content"""
        try:
            # Combine multiple data sources
            content = {
                'services_highlight': self._get_services_highlight(),
                'recent_news': self.get_news_data()[:3],  # Latest 3 news
                'quick_stats': self._get_quick_stats(),
                'featured_service': self._get_featured_service()
            }
            
            return content
        except Exception as e:
            logger.error(f"Failed to load homepage content: {e}")
            return self._get_default_homepage()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for search optimization"""
        import re
        
        # Simple keyword extraction
        words = re.findall(r'\b\w{4,}\b', text.lower())
        # Remove common words
        stop_words = {'para', 'como', 'onde', 'quando', 'qual', 'quais', 'processo', 'vara', 'civil'}
        keywords = [word for word in words if word not in stop_words]
        
        return list(set(keywords))[:10]  # Unique keywords, max 10
    
    def _get_services_highlight(self) -> List[Dict[str, Any]]:
        """Get highlighted services for homepage"""
        return [
            {
                'title': 'Consulta Processual',
                'description': 'Consulte o andamento do seu processo',
                'icon': 'consulta_processual.png',
                'url': '/servicos/consulta-processual',
                'popular': True
            },
            {
                'title': 'Agendamento',
                'description': 'Agende seu atendimento presencial ou virtual',
                'icon': 'agendamento.png',
                'url': '/servicos/agendamento',
                'popular': True
            },
            {
                'title': 'Audiências',
                'description': 'Informações sobre audiências e tutoriais',
                'icon': 'balcao_virtual.png',
                'url': '/servicos/audiencias',
                'popular': False
            },
            {
                'title': 'Certidões',
                'description': 'Solicite certidões e documentos',
                'icon': 'documentos.png',
                'url': '/servicos/certidoes',
                'popular': False
            }
        ]
    
    def _get_quick_stats(self) -> Dict[str, Any]:
        """Get quick statistics for homepage"""
        try:
            from services.database_service_optimized import db_service
            stats = db_service.get_consultation_stats(days=30)
            
            return {
                'consultas_mes': stats.get('total_consultations', 0),
                'processos_unicos': stats.get('unique_processes', 0),
                'media_diaria': stats.get('total_consultations', 0) // 30,
                'disponibilidade': '99.9%'
            }
        except Exception as e:
            logger.warning(f"Could not load stats: {e}")
            return {
                'consultas_mes': 0,
                'processos_unicos': 0,
                'media_diaria': 0,
                'disponibilidade': '99.9%'
            }
    
    def _get_featured_service(self) -> Dict[str, Any]:
        """Get featured service for homepage"""
        return {
            'title': 'Audiências Virtuais',
            'description': 'Participe de audiências online com tutorial completo do Zoom',
            'image': 'tutorial_zoom_audio_pt.gif',
            'url': '/servicos/audiencias',
            'new': True
        }
    
    def _get_default_faq(self) -> Dict[str, Any]:
        """Default FAQ data when file is not available"""
        return {
            'Geral': [
                {
                    'pergunta': 'Qual o horário de funcionamento?',
                    'resposta': 'Segunda a sexta-feira das 12h às 18h.'
                },
                {
                    'pergunta': 'Onde fica localizada a vara?',
                    'resposta': 'Rua Expedito Garcia, s/n, Centro, Cariacica - ES.'
                }
            ]
        }
    
    def _get_default_news(self) -> List[Dict[str, Any]]:
        """Default news data when file is not available"""
        return [
            {
                'id': 1,
                'titulo': 'Funcionamento Normal',
                'resumo': 'A 2ª Vara Cível funciona normalmente.',
                'conteudo': 'Informamos que a 2ª Vara Cível de Cariacica mantém funcionamento normal.',
                'data_publicacao': datetime.utcnow().isoformat(),
                'ativo': True,
                'categoria': 'informativo'
            }
        ]
    
    def _get_default_services(self) -> Dict[str, Any]:
        """Default services data when file is not available"""
        return {
            'servicos': [
                'Consulta Processual',
                'Agendamento',
                'Audiências',
                'Certidões'
            ]
        }
    
    def _get_default_homepage(self) -> Dict[str, Any]:
        """Default homepage content when loading fails"""
        return {
            'services_highlight': self._get_services_highlight(),
            'recent_news': [],
            'quick_stats': {
                'consultas_mes': 0,
                'processos_unicos': 0,
                'media_diaria': 0,
                'disponibilidade': '99.9%'
            },
            'featured_service': self._get_featured_service()
        }
    
    def search_content(self, query: str, content_type: str = 'all') -> List[Dict[str, Any]]:
        """Search across all content with relevance scoring"""
        results = []
        query_lower = query.lower()
        
        if content_type in ['all', 'faq']:
            faq_data = self.get_faq_data()
            for category, questions in faq_data.items():
                for question in questions:
                    score = 0
                    # Check title match
                    if query_lower in question['pergunta'].lower():
                        score += 10
                    # Check content match
                    if query_lower in question['resposta'].lower():
                        score += 5
                    # Check keywords
                    for keyword in question.get('keywords', []):
                        if query_lower in keyword:
                            score += 3
                    
                    if score > 0:
                        results.append({
                            'type': 'faq',
                            'title': question['pergunta'],
                            'content': question['resposta'][:200],
                            'url': f"/faq#{question['id']}",
                            'score': score,
                            'category': category
                        })
        
        if content_type in ['all', 'news']:
            news_data = self.get_news_data()
            for news_item in news_data:
                score = 0
                if query_lower in news_item['titulo'].lower():
                    score += 15
                if query_lower in news_item['resumo'].lower():
                    score += 8
                if query_lower in news_item['conteudo'].lower():
                    score += 3
                
                if score > 0:
                    results.append({
                        'type': 'news',
                        'title': news_item['titulo'],
                        'content': news_item['resumo'],
                        'url': f"/noticias#{news_item['id']}",
                        'score': score,
                        'date': news_item['data_publicacao']
                    })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:20]  # Return top 20 results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get content cache statistics"""
        return self.cache.get_stats()
    
    def clear_cache(self) -> bool:
        """Clear all cached content"""
        try:
            self.cache.cache.clear()
            self.cache.dependencies.clear()
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False


# Global content service instance
content_cache = ContentCache()
content_service = OptimizedContentService()


# Convenience functions for backward compatibility
def get_faq_data():
    """Get FAQ data"""
    return content_service.get_faq_data()


def get_news_data():
    """Get news data"""
    return content_service.get_news_data()


def get_homepage_content():
    """Get homepage content"""
    return content_service.get_homepage_content()