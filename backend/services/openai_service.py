"""
OpenAI service for the Universal Consultant Intelligence Platform.

Provides AI-powered research synthesis, content analysis, signal prioritization,
and intelligent email generation using GPT-4 and GPT-3.5-turbo models.
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple

import openai
import structlog
from openai import AsyncOpenAI
from pydantic import BaseModel

from backend.core.config import settings
from backend.core.logging import performance_logger
from backend.core.monitoring import record_openai_metrics
from backend.utils.exceptions import raise_external_service_error

logger = structlog.get_logger(__name__)


class ResearchSummary(BaseModel):
    """Research synthesis output model."""
    
    executive_summary: str
    key_findings: List[str]
    business_signals: List[Dict[str, any]]
    recommended_actions: List[str]
    confidence_score: float
    sources_analyzed: int


class SignalAnalysis(BaseModel):
    """Signal analysis output model."""
    
    signal_type: str
    priority_score: float
    business_impact: str
    timing_relevance: str
    action_recommendations: List[str]
    related_signals: List[str]


class EmailContent(BaseModel):
    """Email generation output model."""
    
    subject: str
    body: str
    tone: str
    personalization_points: List[str]
    call_to_action: str


class OpenAIService:
    """OpenAI API service for intelligent content processing."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.research_model = "gpt-4"  # For complex analysis and synthesis
        self.email_model = "gpt-3.5-turbo"  # For email generation
        self.max_retries = 3
        self.retry_delay = 1.0
    
    async def synthesize_research(
        self,
        raw_data: List[Dict[str, any]],
        consultant_profile: Dict[str, any],
        target_company: str,
        research_objectives: List[str]
    ) -> ResearchSummary:
        """
        Synthesize raw research data into actionable insights.
        
        Args:
            raw_data: List of scraped content and signal data
            consultant_profile: Consultant's focus areas and preferences
            target_company: Company being researched
            research_objectives: Specific research goals
            
        Returns:
            ResearchSummary: Structured analysis and recommendations
        """
        
        start_time = time.time()
        
        try:
            # Build comprehensive prompt for research synthesis
            system_prompt = self._build_research_system_prompt(consultant_profile)
            user_prompt = self._build_research_user_prompt(
                raw_data, target_company, research_objectives
            )
            
            logger.info(
                "Starting research synthesis",
                target_company=target_company,
                data_points=len(raw_data),
                objectives_count=len(research_objectives)
            )
            
            # Make OpenAI API call with retry logic
            response = await self._make_api_call_with_retry(
                model=self.research_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more focused analysis
                max_tokens=2000,
                timeout=60
            )
            
            # Parse and structure the response
            synthesis_result = self._parse_research_response(
                response.choices[0].message.content,
                len(raw_data)
            )
            
            # Record metrics
            execution_time = time.time() - start_time
            tokens_used = response.usage.total_tokens if response.usage else 0
            cost = self._calculate_cost(self.research_model, tokens_used)
            
            record_openai_metrics(tokens_used, cost)
            performance_logger.log_external_api_call(
                service="openai",
                endpoint="chat/completions",
                response_time=execution_time,
                status_code=200,
                tokens_used=tokens_used,
                cost=cost,
                model=self.research_model
            )
            
            logger.info(
                "Research synthesis completed",
                target_company=target_company,
                execution_time=execution_time,
                tokens_used=tokens_used,
                confidence_score=synthesis_result.confidence_score
            )
            
            return synthesis_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "Research synthesis failed",
                target_company=target_company,
                execution_time=execution_time,
                error=str(e)
            )
            raise_external_service_error("OpenAI", f"Research synthesis failed: {str(e)}")
    
    async def analyze_signal(
        self,
        signal_data: Dict[str, any],
        consultant_priorities: List[str],
        company_context: Dict[str, any]
    ) -> SignalAnalysis:
        """
        Analyze individual business signals for relevance and priority.
        
        Args:
            signal_data: Raw signal information
            consultant_priorities: Consultant's priority areas
            company_context: Company background information
            
        Returns:
            SignalAnalysis: Structured signal assessment
        """
        
        start_time = time.time()
        
        try:
            system_prompt = self._build_signal_analysis_system_prompt(consultant_priorities)
            user_prompt = self._build_signal_analysis_user_prompt(signal_data, company_context)
            
            logger.info(
                "Starting signal analysis",
                signal_type=signal_data.get("type", "unknown"),
                company=company_context.get("name", "unknown")
            )
            
            response = await self._make_api_call_with_retry(
                model=self.research_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=800,
                timeout=30
            )
            
            analysis_result = self._parse_signal_analysis_response(
                response.choices[0].message.content
            )
            
            # Record metrics
            execution_time = time.time() - start_time
            tokens_used = response.usage.total_tokens if response.usage else 0
            cost = self._calculate_cost(self.research_model, tokens_used)
            
            record_openai_metrics(tokens_used, cost)
            performance_logger.log_external_api_call(
                service="openai",
                endpoint="chat/completions",
                response_time=execution_time,
                tokens_used=tokens_used,
                cost=cost,
                model=self.research_model
            )
            
            return analysis_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "Signal analysis failed",
                signal_data=signal_data,
                execution_time=execution_time,
                error=str(e)
            )
            raise_external_service_error("OpenAI", f"Signal analysis failed: {str(e)}")
    
    async def generate_email_content(
        self,
        prospect_data: Dict[str, any],
        consultant_profile: Dict[str, any],
        email_objective: str,
        template_style: str = "professional"
    ) -> EmailContent:
        """
        Generate personalized email content for prospects.
        
        Args:
            prospect_data: Target prospect information
            consultant_profile: Consultant's background and positioning
            email_objective: Purpose of the email (intro, follow-up, etc.)
            template_style: Communication tone and style
            
        Returns:
            EmailContent: Generated email with personalization
        """
        
        start_time = time.time()
        
        try:
            system_prompt = self._build_email_generation_system_prompt(
                consultant_profile, template_style
            )
            user_prompt = self._build_email_generation_user_prompt(
                prospect_data, email_objective
            )
            
            logger.info(
                "Starting email generation",
                objective=email_objective,
                prospect=prospect_data.get("name", "unknown"),
                style=template_style
            )
            
            response = await self._make_api_call_with_retry(
                model=self.email_model,  # Use GPT-3.5 for email generation
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,  # Higher temperature for more creative content
                max_tokens=1000,
                timeout=30
            )
            
            email_content = self._parse_email_response(
                response.choices[0].message.content,
                template_style
            )
            
            # Record metrics
            execution_time = time.time() - start_time
            tokens_used = response.usage.total_tokens if response.usage else 0
            cost = self._calculate_cost(self.email_model, tokens_used)
            
            record_openai_metrics(tokens_used, cost)
            performance_logger.log_external_api_call(
                service="openai",
                endpoint="chat/completions",
                response_time=execution_time,
                tokens_used=tokens_used,
                cost=cost,
                model=self.email_model
            )
            
            return email_content
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "Email generation failed",
                prospect_data=prospect_data,
                execution_time=execution_time,
                error=str(e)
            )
            raise_external_service_error("OpenAI", f"Email generation failed: {str(e)}")
    
    async def _make_api_call_with_retry(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.5,
        max_tokens: int = 1000,
        timeout: int = 30
    ) -> any:
        """Make OpenAI API call with exponential backoff retry logic."""
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout
                )
                
                return response
                
            except openai.RateLimitError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        f"OpenAI rate limit hit, retrying in {wait_time}s",
                        attempt=attempt + 1,
                        max_retries=self.max_retries
                    )
                    await asyncio.sleep(wait_time)
                    continue
                raise
                
            except openai.APIError as e:
                if attempt < self.max_retries - 1 and e.status_code >= 500:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        f"OpenAI server error, retrying in {wait_time}s",
                        attempt=attempt + 1,
                        error=str(e)
                    )
                    await asyncio.sleep(wait_time)
                    continue
                raise
                
            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}")
                raise
    
    def _build_research_system_prompt(self, consultant_profile: Dict[str, any]) -> str:
        """Build system prompt for research synthesis."""
        
        return f"""You are an expert business intelligence analyst helping {consultant_profile.get('consultant_type', 'consultant')}s 
with {consultant_profile.get('industry_focus', 'business')} expertise. Your role is to synthesize raw research data into 
actionable insights for business development and client engagement.

Focus areas: {', '.join(consultant_profile.get('signal_priorities', []))}
Target company size: {consultant_profile.get('target_company_size', 'all sizes')}
Geographic preference: {consultant_profile.get('geographic_preference', 'global')}

Analyze the provided data and create a comprehensive research summary that:
1. Identifies the most relevant business signals and opportunities
2. Prioritizes findings based on the consultant's focus areas
3. Provides specific, actionable recommendations
4. Assesses confidence levels based on data quality and completeness

Be concise, data-driven, and focus on insights that directly support business development activities."""
    
    def _build_research_user_prompt(
        self,
        raw_data: List[Dict[str, any]],
        target_company: str,
        research_objectives: List[str]
    ) -> str:
        """Build user prompt for research synthesis."""
        
        data_summary = []
        for item in raw_data[:10]:  # Limit to prevent token overflow
            data_summary.append(f"- {item.get('type', 'Unknown')}: {item.get('content', '')[:200]}...")
        
        return f"""Please analyze the following research data for {target_company}:

RESEARCH OBJECTIVES:
{chr(10).join(f'- {obj}' for obj in research_objectives)}

RAW DATA SOURCES ({len(raw_data)} total):
{chr(10).join(data_summary)}

Please provide a structured analysis in the following format:
1. EXECUTIVE SUMMARY (2-3 sentences)
2. KEY FINDINGS (3-5 bullet points)
3. BUSINESS SIGNALS (prioritized list with impact assessment)
4. RECOMMENDED ACTIONS (specific next steps)
5. CONFIDENCE SCORE (0.0-1.0 based on data quality)

Focus on insights that directly support business development and client engagement opportunities."""
    
    def _build_signal_analysis_system_prompt(self, consultant_priorities: List[str]) -> str:
        """Build system prompt for signal analysis."""
        
        return f"""You are a business signal analysis expert. Your role is to evaluate individual business 
signals for their relevance, priority, and potential impact based on consultant priorities.

Priority areas: {', '.join(consultant_priorities)}

For each signal, assess:
1. Business impact and relevance
2. Timing and urgency
3. Actionability and next steps
4. Priority score (0.0-1.0)
5. Connection to other signals

Be objective, data-driven, and focus on practical business implications."""
    
    def _build_signal_analysis_user_prompt(
        self,
        signal_data: Dict[str, any],
        company_context: Dict[str, any]
    ) -> str:
        """Build user prompt for signal analysis."""
        
        return f"""Analyze this business signal:

SIGNAL DATA:
Type: {signal_data.get('type', 'Unknown')}
Content: {signal_data.get('content', '')}
Source: {signal_data.get('source', 'Unknown')}
Date: {signal_data.get('date', 'Unknown')}

COMPANY CONTEXT:
Name: {company_context.get('name', 'Unknown')}
Industry: {company_context.get('industry', 'Unknown')}
Size: {company_context.get('size', 'Unknown')}
Background: {company_context.get('description', 'Unknown')}

Please provide structured analysis:
1. SIGNAL TYPE classification
2. PRIORITY SCORE (0.0-1.0)
3. BUSINESS IMPACT assessment
4. TIMING RELEVANCE
5. ACTION RECOMMENDATIONS
6. RELATED SIGNALS potential"""
    
    def _build_email_generation_system_prompt(
        self,
        consultant_profile: Dict[str, any],
        template_style: str
    ) -> str:
        """Build system prompt for email generation."""
        
        return f"""You are an expert email copywriter specializing in {template_style} business communications 
for {consultant_profile.get('consultant_type', 'consultant')}s.

Consultant background:
- Industry focus: {consultant_profile.get('industry_focus', 'business')}
- Solution positioning: {consultant_profile.get('solution_positioning', 'value creation')}
- Communication style: {template_style}

Create compelling, personalized emails that:
1. Capture attention with relevant insights
2. Demonstrate expertise and value
3. Include clear call-to-action
4. Maintain professional tone
5. Are concise and actionable

Avoid generic templates and focus on personalization based on prospect research."""
    
    def _build_email_generation_user_prompt(
        self,
        prospect_data: Dict[str, any],
        email_objective: str
    ) -> str:
        """Build user prompt for email generation."""
        
        return f"""Generate a personalized email for this prospect:

PROSPECT INFORMATION:
Name: {prospect_data.get('name', 'Unknown')}
Title: {prospect_data.get('title', 'Unknown')}
Company: {prospect_data.get('company', 'Unknown')}
Industry: {prospect_data.get('industry', 'Unknown')}
Recent activity: {prospect_data.get('recent_signals', 'None available')}

EMAIL OBJECTIVE: {email_objective}

Please provide:
1. SUBJECT LINE (compelling and specific)
2. EMAIL BODY (personalized and value-focused)
3. CALL TO ACTION (clear and specific)
4. PERSONALIZATION POINTS (key elements used)

Keep the email concise (under 150 words) and professional."""
    
    def _parse_research_response(self, response: str, sources_count: int) -> ResearchSummary:
        """Parse OpenAI research synthesis response into structured format."""
        
        # TODO: Implement robust parsing logic
        # For now, return a structured placeholder
        return ResearchSummary(
            executive_summary=response[:200] + "..." if len(response) > 200 else response,
            key_findings=["Finding 1", "Finding 2", "Finding 3"],
            business_signals=[
                {"type": "growth", "impact": "high", "confidence": 0.8},
                {"type": "hiring", "impact": "medium", "confidence": 0.7}
            ],
            recommended_actions=["Action 1", "Action 2"],
            confidence_score=0.75,
            sources_analyzed=sources_count
        )
    
    def _parse_signal_analysis_response(self, response: str) -> SignalAnalysis:
        """Parse OpenAI signal analysis response into structured format."""
        
        # TODO: Implement robust parsing logic
        return SignalAnalysis(
            signal_type="growth_indicator",
            priority_score=0.8,
            business_impact="High potential for engagement",
            timing_relevance="Immediate opportunity",
            action_recommendations=["Contact within 48 hours", "Prepare growth strategy proposal"],
            related_signals=["hiring_expansion", "funding_announcement"]
        )
    
    def _parse_email_response(self, response: str, tone: str) -> EmailContent:
        """Parse OpenAI email generation response into structured format."""
        
        # TODO: Implement robust parsing logic
        lines = response.split('\n')
        
        return EmailContent(
            subject=lines[0] if lines else "Subject line generated",
            body=response,
            tone=tone,
            personalization_points=["Company-specific insight", "Role-relevant challenge"],
            call_to_action="Schedule a brief call to discuss opportunities"
        )
    
    def _calculate_cost(self, model: str, tokens: int) -> float:
        """Calculate API cost based on model and token usage."""
        
        # OpenAI pricing (as of implementation date)
        pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}  # per 1K tokens
        }
        
        if model not in pricing:
            return 0.0
        
        # Estimate 75% input, 25% output tokens
        input_tokens = tokens * 0.75
        output_tokens = tokens * 0.25
        
        cost = (
            (input_tokens / 1000) * pricing[model]["input"] +
            (output_tokens / 1000) * pricing[model]["output"]
        )
        
        return round(cost, 6)


# Global service instance
openai_service = OpenAIService()