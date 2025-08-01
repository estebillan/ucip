"""
Web scraping service for the Universal Consultant Intelligence Platform.

Provides intelligent web scraping for business signals, company information,
news articles, and industry data using Beautiful Soup and aiohttp.
"""

import asyncio
import re
import time
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import aiohttp
import structlog
from bs4 import BeautifulSoup
from pydantic import BaseModel

from backend.core.config import settings
from backend.core.logging import performance_logger
from backend.utils.exceptions import raise_external_service_error

logger = structlog.get_logger(__name__)


class ScrapedContent(BaseModel):
    """Scraped content model."""
    
    url: str
    title: str
    content: str
    metadata: Dict[str, any]
    signals: List[Dict[str, any]]
    scraped_at: float
    processing_time: float


class ScrapingTarget(BaseModel):
    """Scraping target configuration."""
    
    url: str
    target_type: str  # 'company_page', 'news_article', 'press_release', 'industry_report'
    selectors: Dict[str, str]  # CSS selectors for content extraction
    signal_keywords: List[str]
    max_depth: int = 1
    follow_links: bool = False


class WebScrapingService:
    """Advanced web scraping service with signal detection."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            'User-Agent': 'Universal Consultant Intelligence Platform/1.0 (+https://consultant-platform.com/bot)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.max_concurrent = 10
        self.delay_between_requests = 1.0
        
        # Signal detection patterns
        self.signal_patterns = {
            'funding': [
                r'raised \$[\d\.]+[mb]?',
                r'series [abc] funding',
                r'investment round',
                r'venture capital',
                r'seed funding'
            ],
            'hiring': [
                r'hiring \d+ people',
                r'expanding team',
                r'new positions',
                r'job openings',
                r'recruitment drive'
            ],
            'expansion': [
                r'opening new office',
                r'expanding to',
                r'international expansion',
                r'new market',
                r'geographic expansion'
            ],
            'product_launch': [
                r'launching new',
                r'product release',
                r'new feature',
                r'beta launch',
                r'coming soon'
            ],
            'partnership': [
                r'partnership with',
                r'strategic alliance',
                r'collaboration',
                r'joint venture',
                r'announces deal'
            ],
            'leadership': [
                r'new ceo',
                r'executive appointment',
                r'leadership change',
                r'promoted to',
                r'joins as'
            ]
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        if not self.session:
            connector = aiohttp.TCPConnector(
                limit=self.max_concurrent,
                limit_per_host=5,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            self.session = aiohttp.ClientSession(
                connector=connector,
                headers=self.headers,
                timeout=self.timeout
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def scrape_company_intelligence(
        self,
        company_name: str,
        company_domain: str,
        target_signals: List[str] = None
    ) -> List[ScrapedContent]:
        """
        Scrape comprehensive intelligence about a company.
        
        Args:
            company_name: Name of the target company
            company_domain: Company's primary domain
            target_signals: Specific signals to look for
            
        Returns:
            List[ScrapedContent]: Scraped content with signals
        """
        
        start_time = time.time()
        
        try:
            logger.info(
                "Starting company intelligence scraping",
                company=company_name,
                domain=company_domain,
                target_signals=target_signals
            )
            
            # Build scraping targets
            targets = await self._build_company_targets(
                company_name, company_domain, target_signals or []
            )
            
            # Scrape all targets concurrently
            scraped_content = []
            
            async with self:
                semaphore = asyncio.Semaphore(self.max_concurrent)
                tasks = [
                    self._scrape_single_target(target, semaphore)
                    for target in targets
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, ScrapedContent):
                        scraped_content.append(result)
                    elif isinstance(result, Exception):
                        logger.warning(f"Scraping task failed: {result}")
            
            # Filter and prioritize content
            prioritized_content = self._prioritize_scraped_content(
                scraped_content, target_signals or []
            )
            
            execution_time = time.time() - start_time
            
            performance_logger.log_external_api_call(
                service="web_scraping",
                endpoint="company_intelligence",
                response_time=execution_time,
                status_code=200,
                company=company_name,
                targets_scraped=len(targets),
                content_found=len(prioritized_content)
            )
            
            logger.info(
                "Company intelligence scraping completed",
                company=company_name,
                execution_time=execution_time,
                targets_scraped=len(targets),
                content_pieces=len(prioritized_content),
                signals_found=sum(len(content.signals) for content in prioritized_content)
            )
            
            return prioritized_content
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "Company intelligence scraping failed",
                company=company_name,
                execution_time=execution_time,
                error=str(e)
            )
            raise_external_service_error("Web Scraping", f"Company scraping failed: {str(e)}")
    
    async def scrape_industry_news(
        self,
        industry_keywords: List[str],
        time_range: str = "1w"  # 1w, 1m, 3m
    ) -> List[ScrapedContent]:
        """
        Scrape industry news and reports for relevant signals.
        
        Args:
            industry_keywords: Keywords to search for
            time_range: Time range for news articles
            
        Returns:
            List[ScrapedContent]: News articles with signals
        """
        
        start_time = time.time()
        
        try:
            logger.info(
                "Starting industry news scraping",
                keywords=industry_keywords,
                time_range=time_range
            )
            
            # Build news source targets
            targets = await self._build_news_targets(industry_keywords, time_range)
            
            # Scrape news sources
            scraped_articles = []
            
            async with self:
                semaphore = asyncio.Semaphore(self.max_concurrent)
                tasks = [
                    self._scrape_single_target(target, semaphore)
                    for target in targets
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, ScrapedContent):
                        scraped_articles.append(result)
            
            # Filter for relevance and signals
            relevant_articles = self._filter_relevant_content(
                scraped_articles, industry_keywords
            )
            
            execution_time = time.time() - start_time
            
            performance_logger.log_external_api_call(
                service="web_scraping",
                endpoint="industry_news",
                response_time=execution_time,
                status_code=200,
                keywords=len(industry_keywords),
                articles_found=len(relevant_articles)
            )
            
            return relevant_articles
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "Industry news scraping failed",
                keywords=industry_keywords,
                execution_time=execution_time,
                error=str(e)
            )
            raise_external_service_error("Web Scraping", f"News scraping failed: {str(e)}")
    
    async def _scrape_single_target(
        self,
        target: ScrapingTarget,
        semaphore: asyncio.Semaphore
    ) -> Optional[ScrapedContent]:
        """Scrape a single target URL with rate limiting."""
        
        async with semaphore:
            start_time = time.time()
            
            try:
                # Respect rate limiting
                await asyncio.sleep(self.delay_between_requests)
                
                logger.debug(f"Scraping target: {target.url}")
                
                async with self.session.get(target.url) as response:
                    if response.status != 200:
                        logger.warning(
                            f"Non-200 response from {target.url}",
                            status=response.status
                        )
                        return None
                    
                    html_content = await response.text()
                    content_type = response.headers.get('content-type', '').lower()
                    
                    if 'html' not in content_type:
                        logger.warning(f"Non-HTML content from {target.url}")
                        return None
                
                # Parse content
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract structured content
                title = self._extract_title(soup, target)
                content = self._extract_content(soup, target)
                metadata = self._extract_metadata(soup, target)
                
                # Detect business signals
                signals = self._detect_signals(
                    content, target.signal_keywords, target.target_type
                )
                
                processing_time = time.time() - start_time
                
                return ScrapedContent(
                    url=target.url,
                    title=title,
                    content=content,
                    metadata=metadata,
                    signals=signals,
                    scraped_at=time.time(),
                    processing_time=processing_time
                )
                
            except Exception as e:
                processing_time = time.time() - start_time
                logger.error(
                    f"Failed to scrape {target.url}",
                    error=str(e),
                    processing_time=processing_time
                )
                return None
    
    async def _build_company_targets(
        self,
        company_name: str,
        company_domain: str,
        target_signals: List[str]
    ) -> List[ScrapingTarget]:
        """Build list of scraping targets for company intelligence."""
        
        targets = []
        
        # Company website pages
        base_url = f"https://{company_domain}"
        company_pages = [
            ('/', 'company_page', {'title': 'title', 'content': 'main, .content, article'}),
            ('/about', 'company_page', {'title': 'h1, .page-title', 'content': 'main, .content'}),
            ('/news', 'news_section', {'title': 'h1', 'content': '.news-item, article'}),
            ('/press', 'press_section', {'title': 'h1', 'content': '.press-release, article'}),
            ('/careers', 'careers_page', {'title': 'h1', 'content': '.job-listing, .career-content'}),
        ]
        
        for path, target_type, selectors in company_pages:
            targets.append(ScrapingTarget(
                url=urljoin(base_url, path),
                target_type=target_type,
                selectors=selectors,
                signal_keywords=target_signals,
                max_depth=1
            ))
        
        # External news sources
        news_sources = [
            f"https://news.google.com/search?q={company_name}+{'+'.join(target_signals[:3])}",
            f"https://www.businesswire.com/news/home/search?SearchText={company_name}",
        ]
        
        for url in news_sources:
            targets.append(ScrapingTarget(
                url=url,
                target_type='news_search',
                selectors={'title': 'h3, .title', 'content': '.content, p'},
                signal_keywords=target_signals,
                max_depth=1
            ))
        
        return targets
    
    async def _build_news_targets(
        self,
        industry_keywords: List[str],
        time_range: str
    ) -> List[ScrapingTarget]:
        """Build list of news source targets."""
        
        targets = []
        keywords_str = '+'.join(industry_keywords[:5])
        
        # Industry news sources
        news_sources = [
            {
                'url': f"https://news.google.com/search?q={keywords_str}",
                'selectors': {'title': 'h3', 'content': '.content'}
            },
            {
                'url': f"https://www.businesswire.com/news/home/search?SearchText={keywords_str}",
                'selectors': {'title': '.bw-release-title', 'content': '.bw-release-story'}
            },
        ]
        
        for source in news_sources:
            targets.append(ScrapingTarget(
                url=source['url'],
                target_type='industry_news',
                selectors=source['selectors'],
                signal_keywords=industry_keywords,
                max_depth=1
            ))
        
        return targets
    
    def _extract_title(self, soup: BeautifulSoup, target: ScrapingTarget) -> str:
        """Extract title from page."""
        
        title_selector = target.selectors.get('title', 'title')
        title_element = soup.select_one(title_selector)
        
        if title_element:
            return title_element.get_text(strip=True)
        
        # Fallback to page title
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else "No title found"
    
    def _extract_content(self, soup: BeautifulSoup, target: ScrapingTarget) -> str:
        """Extract main content from page."""
        
        content_selector = target.selectors.get('content', 'main, .content, article, p')
        content_elements = soup.select(content_selector)
        
        if not content_elements:
            # Fallback to all paragraphs
            content_elements = soup.find_all('p')
        
        # Clean and combine content
        content_pieces = []
        for element in content_elements[:20]:  # Limit to prevent excessive content
            text = element.get_text(strip=True)
            if len(text) > 50:  # Only include substantial text blocks
                content_pieces.append(text)
        
        return '\n\n'.join(content_pieces)
    
    def _extract_metadata(self, soup: BeautifulSoup, target: ScrapingTarget) -> Dict[str, any]:
        """Extract metadata from page."""
        
        metadata = {
            'target_type': target.target_type,
            'domain': urlparse(target.url).netloc,
            'scraped_elements': 0
        }
        
        # Extract meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property', '').replace('og:', '')
            content = meta.get('content')
            if name and content:
                metadata[f'meta_{name}'] = content
        
        # Extract structured data
        structured_data = soup.find_all('script', type='application/ld+json')
        if structured_data:
            metadata['structured_data_found'] = len(structured_data)
        
        return metadata
    
    def _detect_signals(
        self,
        content: str,
        signal_keywords: List[str],
        target_type: str
    ) -> List[Dict[str, any]]:
        """Detect business signals in content."""
        
        signals = []
        content_lower = content.lower()
        
        # Check each signal pattern
        for signal_type, patterns in self.signal_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                for match in matches:
                    signals.append({
                        'type': signal_type,
                        'pattern': pattern,
                        'match': match,
                        'confidence': self._calculate_signal_confidence(
                            signal_type, match, target_type
                        ),
                        'context': self._extract_signal_context(content, match)
                    })
        
        # Check for custom signal keywords
        for keyword in signal_keywords:
            if keyword.lower() in content_lower:
                signals.append({
                    'type': 'custom',
                    'pattern': keyword,
                    'match': keyword,
                    'confidence': 0.7,
                    'context': self._extract_signal_context(content, keyword)
                })
        
        # Deduplicate and sort by confidence
        unique_signals = []
        seen_matches = set()
        
        for signal in sorted(signals, key=lambda x: x['confidence'], reverse=True):
            match_key = f"{signal['type']}:{signal['match']}"
            if match_key not in seen_matches:
                unique_signals.append(signal)
                seen_matches.add(match_key)
        
        return unique_signals[:10]  # Return top 10 signals
    
    def _calculate_signal_confidence(
        self,
        signal_type: str,
        match: str,
        target_type: str
    ) -> float:
        """Calculate confidence score for a detected signal."""
        
        base_confidence = 0.6
        
        # Boost confidence based on target type
        type_boost = {
            'press_release': 0.3,
            'news_article': 0.2,
            'company_page': 0.1,
            'careers_page': 0.2 if signal_type == 'hiring' else 0.0
        }
        
        confidence = base_confidence + type_boost.get(target_type, 0.0)
        
        # Boost confidence for specific patterns
        if any(word in match.lower() for word in ['million', 'billion', 'series', 'round']):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_signal_context(self, content: str, match: str) -> str:
        """Extract context around a detected signal."""
        
        # Find the sentence containing the match
        sentences = content.split('.')
        for sentence in sentences:
            if match.lower() in sentence.lower():
                return sentence.strip()[:200]  # Return first 200 chars
        
        return match
    
    def _prioritize_scraped_content(
        self,
        content_list: List[ScrapedContent],
        target_signals: List[str]
    ) -> List[ScrapedContent]:
        """Prioritize scraped content based on signal relevance."""
        
        def calculate_priority_score(content: ScrapedContent) -> float:
            score = 0.0
            
            # Base score from signal count and confidence
            for signal in content.signals:
                score += signal['confidence']
            
            # Bonus for target signals
            for signal in content.signals:
                if signal['pattern'] in target_signals:
                    score += 0.5
            
            # Bonus for fresh content (assumed based on processing time)
            if content.processing_time < 2.0:
                score += 0.2
            
            return score
        
        # Sort by priority score
        return sorted(
            content_list,
            key=calculate_priority_score,
            reverse=True
        )
    
    def _filter_relevant_content(
        self,
        content_list: List[ScrapedContent],
        keywords: List[str]
    ) -> List[ScrapedContent]:
        """Filter content for keyword relevance."""
        
        relevant_content = []
        
        for content in content_list:
            relevance_score = 0
            content_text = (content.title + ' ' + content.content).lower()
            
            # Check keyword presence
            for keyword in keywords:
                if keyword.lower() in content_text:
                    relevance_score += 1
            
            # Include if at least one keyword matches or has signals
            if relevance_score > 0 or len(content.signals) > 0:
                relevant_content.append(content)
        
        return relevant_content


# Global service instance
scraping_service = WebScrapingService()