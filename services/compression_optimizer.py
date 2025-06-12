"""
Advanced Compression and Response Optimization
2ª Vara Cível de Cariacica - Production-grade compression system
"""

import gzip
import zlib
import brotli
from io import BytesIO
from flask import request, current_app
import logging

logger = logging.getLogger(__name__)

class CompressionOptimizer:
    """Advanced compression for HTTP responses"""
    
    def __init__(self, app=None):
        self.app = app
        self.compression_level = 6
        self.min_size = 500  # Minimum response size to compress
        self.compressible_types = {
            'text/html',
            'text/css', 
            'text/javascript',
            'application/javascript',
            'application/json',
            'text/xml',
            'application/xml',
            'text/plain'
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize compression with Flask app"""
        self.app = app
        app.after_request(self.compress_response)
    
    def _should_compress(self, response):
        """Determine if response should be compressed"""
        # Skip if already compressed
        if response.headers.get('Content-Encoding'):
            return False
        
        # Skip if response too small
        if len(response.data) < self.min_size:
            return False
        
        # Check content type
        content_type = response.headers.get('Content-Type', '').split(';')[0]
        if content_type not in self.compressible_types:
            return False
        
        return True
    
    def _get_best_encoding(self):
        """Get best compression encoding based on client support"""
        accept_encoding = request.headers.get('Accept-Encoding', '')
        
        if 'br' in accept_encoding:
            return 'br'
        elif 'gzip' in accept_encoding:
            return 'gzip'
        elif 'deflate' in accept_encoding:
            return 'deflate'
        
        return None
    
    def _compress_brotli(self, data):
        """Compress data using Brotli"""
        try:
            return brotli.compress(data, quality=4)
        except Exception as e:
            logger.warning(f"Brotli compression failed: {e}")
            return None
    
    def _compress_gzip(self, data):
        """Compress data using Gzip"""
        try:
            buffer = BytesIO()
            with gzip.GzipFile(fileobj=buffer, mode='wb', compresslevel=self.compression_level) as f:
                f.write(data)
            return buffer.getvalue()
        except Exception as e:
            logger.warning(f"Gzip compression failed: {e}")
            return None
    
    def _compress_deflate(self, data):
        """Compress data using Deflate"""
        try:
            return zlib.compress(data, self.compression_level)
        except Exception as e:
            logger.warning(f"Deflate compression failed: {e}")
            return None
    
    def compress_response(self, response):
        """Compress HTTP response if beneficial"""
        try:
            if not self._should_compress(response):
                return response
            
            encoding = self._get_best_encoding()
            if not encoding:
                return response
            
            original_size = len(response.data)
            compressed_data = None
            
            if encoding == 'br':
                compressed_data = self._compress_brotli(response.data)
            elif encoding == 'gzip':
                compressed_data = self._compress_gzip(response.data)
            elif encoding == 'deflate':
                compressed_data = self._compress_deflate(response.data)
            
            if compressed_data and len(compressed_data) < original_size:
                response.data = compressed_data
                response.headers['Content-Encoding'] = encoding
                response.headers['Content-Length'] = len(compressed_data)
                response.headers['Vary'] = 'Accept-Encoding'
                
                compression_ratio = (1 - len(compressed_data) / original_size) * 100
                logger.debug(f"Compressed response: {original_size} -> {len(compressed_data)} bytes ({compression_ratio:.1f}% reduction)")
        
        except Exception as e:
            logger.error(f"Compression error: {e}")
        
        return response

class ResponseOptimizer:
    """Optimize HTTP responses for performance"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize response optimization"""
        self.app = app
        app.after_request(self.optimize_headers)
    
    def optimize_headers(self, response):
        """Add performance optimization headers"""
        try:
            # Cache control for static assets
            if request.endpoint and 'static' in request.endpoint:
                response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year
                response.headers['Expires'] = 'Thu, 31 Dec 2025 23:59:59 GMT'
            
            # ETag for content versioning
            if not response.headers.get('ETag') and response.data:
                import hashlib
                etag = hashlib.md5(response.data).hexdigest()[:16]
                response.headers['ETag'] = f'"{etag}"'
            
            # Preload critical resources
            if request.endpoint == 'main.index':
                response.headers['Link'] = (
                    '</static/css/style.css>; rel=preload; as=style, '
                    '</static/js/main.js>; rel=preload; as=script'
                )
            
            # Connection optimization
            response.headers['Connection'] = 'keep-alive'
            
        except Exception as e:
            logger.error(f"Response optimization error: {e}")
        
        return response

class ResourceMinifier:
    """Minify CSS and JavaScript responses"""
    
    def __init__(self):
        self.css_minify_patterns = [
            (r'/\*.*?\*/', ''),  # Remove comments
            (r'\s+', ' '),       # Collapse whitespace
            (r';\s*}', '}'),     # Remove semicolon before }
            (r'{\s+', '{'),      # Remove space after {
            (r';\s+', ';'),      # Remove space after ;
        ]
        
        self.js_minify_patterns = [
            (r'//.*?\n', '\n'),   # Remove single-line comments
            (r'/\*.*?\*/', ''),   # Remove multi-line comments
            (r'\s+', ' '),        # Collapse whitespace
            (r';\s*\n', ';'),     # Remove newlines after semicolon
        ]
    
    def minify_css(self, content):
        """Minify CSS content"""
        try:
            import re
            for pattern, replacement in self.css_minify_patterns:
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            return content.strip()
        except Exception as e:
            logger.warning(f"CSS minification failed: {e}")
            return content
    
    def minify_js(self, content):
        """Minify JavaScript content"""
        try:
            import re
            for pattern, replacement in self.js_minify_patterns:
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            return content.strip()
        except Exception as e:
            logger.warning(f"JS minification failed: {e}")
            return content

compression_optimizer = CompressionOptimizer()
response_optimizer = ResponseOptimizer()
resource_minifier = ResourceMinifier()