name: "Universal Consultant Intelligence Platform - Complete Implementation PRP"
description: |

## Purpose
Comprehensive PRP for building a production-ready Universal Consultant Intelligence Platform with AI-powered prospect research, dynamic consultant templates, wizard-based setup, and automated outreach capabilities.

## Core Principles
1. **Context is King**: All necessary documentation, examples, and implementation patterns included
2. **Validation Loops**: Docker-based testing with executable validation at each stage
3. **Information Dense**: Complete technical specifications with real-world examples
4. **Progressive Success**: Modular implementation with validation gates
5. **Global rules**: Strict adherence to CLAUDE.md specifications

---

## Goal
Build a complete Universal Consultant Intelligence Platform that enables consultants across 15+ specializations to:
- Set up personalized prospect research profiles via intelligent wizard
- Automatically discover and score prospects using AI-powered signal detection
- Generate comprehensive PDF intelligence reports
- Create personalized outreach emails with AI-generated content
- Manage prospect pipelines through interactive dashboard

## Why
- **Business Value**: Addresses $50B+ consulting market with automated prospect research
- **Market Gap**: No existing platform serves multiple consultant types with AI-powered intelligence
- **User Impact**: Reduces manual research time from 2-3 hours to 10-15 minutes per prospect
- **Integration**: Scalable platform architecture supporting future consultant template additions
- **Revenue Model**: SaaS with usage-based pricing for AI research and report generation

## What
**Core Platform Features:**
- Universal wizard-based consultant setup (adaptable to any consulting niche)
- AI-powered signal detection and prospect scoring engine
- 15+ pre-built consultant templates (fractional CMO, copywriter, business turnaround, etc.)
- Dynamic research engine with multi-source data aggregation
- Interactive dashboard with pipeline management
- PDF intelligence report generation
- AI-powered email draft generation

**Technical Stack:**
- Backend: Python FastAPI with async/await patterns
- Frontend: TypeScript/Vanilla JS for maximum performance
- AI/ML: OpenAI GPT models for research synthesis and content generation
- Web Scraping: Beautiful Soup + Scrapy for public data collection
- PDF Generation: ReportLab for professional reports
- Data Processing: Pandas for analysis and signal processing
- Search: Google Custom Search API integration
- Database: SQLAlchemy/SQLModel ORM with PostgreSQL
- Deployment: Docker containerization with comprehensive testing

### Success Criteria
- [ ] Complete wizard flow creates functional consultant profiles for all 15+ templates
- [ ] Research engine processes 10+ data sources and generates actionable intelligence
- [ ] PDF reports contain comprehensive prospect analysis with executive profiles
- [ ] Email generator produces personalized, context-aware outreach content
- [ ] Dashboard supports prospect pipeline management with real-time updates
- [ ] Platform handles 100+ concurrent users with <2s response times
- [ ] Docker deployment works on first run with comprehensive test coverage
- [ ] All validation gates pass: linting, type checking, unit tests, integration tests

## All Needed Context

### Documentation & References
```yaml
# CRITICAL DOCUMENTATION - Use as absolute truth over existing knowledge
- url: https://fastapi.tiangolo.com/
  why: Async routing, dependency injection, Pydantic integration patterns
  critical: Background tasks for long-running research operations
  
- url: https://fastapi.tiangolo.com/tutorial/dependencies/
  why: Database connections, authentication, shared services architecture
  
- url: https://fastapi.tiangolo.com/tutorial/sql-databases/
  why: SQLAlchemy integration patterns, async database operations
  
- url: https://platform.openai.com/docs/
  why: Chat completions, function calling, rate limiting, error handling
  critical: GPT-4 for research synthesis, GPT-3.5-turbo for email generation
  
- url: https://platform.openai.com/docs/guides/function-calling/
  why: Structured data extraction from research content
  
- url: https://platform.openai.com/docs/guides/rate-limits/
  why: Production rate limiting and error recovery strategies
  
- url: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
  why: HTML parsing, DOM navigation, robust web scraping patterns
  
- url: https://pandas.pydata.org/docs/user_guide/
  why: Data processing, signal analysis, prospect scoring algorithms
  
- url: https://www.reportlab.com/docs/reportlab-userguide.pdf
  why: Professional PDF generation with charts, tables, executive summaries
  
- file: research/fastapi/page1/main.md
  why: FastAPI core concepts and async patterns
  
- file: research/openai/page2/quickstart.md  
  why: OpenAI API integration and authentication patterns
  
- file: research/beautifulsoup/page1/main.md
  why: Web scraping implementation and best practices
```

### Current Codebase Tree
```bash
clientraker/
├── CLAUDE.md              # Project instructions and conventions
├── INITIAL.md             # Feature requirements and technical specs
├── PRPs/                  # PRP templates and examples
│   └── templates/
│       └── prp_base.md    # Base PRP template structure
├── research/              # Scraped documentation (currently limited due to API limits)
│   ├── fastapi/
│   ├── openai/
│   ├── beautifulsoup/
│   ├── pandas/
│   └── typescript/
├── package.json           # Node.js dependencies for frontend tooling
├── playwright.config.js   # End-to-end testing configuration
└── tests/                 # Test directory structure
```

### Desired Codebase Tree with Implementation Structure
```bash
clientraker/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry point
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── consultants.py         # Consultant profile management
│   │       ├── prospects.py           # Prospect discovery and management
│   │       ├── research.py           # Intelligence gathering endpoints
│   │       ├── reports.py            # PDF generation and dashboard data
│   │       └── campaigns.py          # Outreach campaign management
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                 # Application configuration
│   │   ├── database.py               # Database connection and session management
│   │   └── security.py               # Authentication and authorization
│   ├── services/
│   │   ├── __init__.py
│   │   ├── research_engine.py        # AI-powered research orchestration
│   │   ├── signal_detector.py        # Pattern recognition and signal synthesis
│   │   ├── content_generator.py      # Email and report generation
│   │   ├── web_scraper.py           # Public data collection service
│   │   └── pdf_generator.py         # ReportLab PDF creation service
│   ├── models/
│   │   ├── __init__.py
│   │   ├── consultant.py            # Consultant profile data models
│   │   ├── prospect.py              # Prospect and company data models
│   │   └── research.py              # Research data and signal models
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── ai_helpers.py            # OpenAI integration utilities
│   │   └── data_processing.py       # Data cleaning and analysis utilities
│   └── templates/
│       ├── consultant_templates.py  # 15+ consultant type definitions
│       └── email_templates.py       # Email generation templates
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Wizard/              # Multi-step consultant setup
│   │   │   ├── Dashboard/           # Prospect pipeline interface
│   │   │   ├── Research/            # Research management interface
│   │   │   ├── Reports/             # PDF viewer and generator
│   │   │   └── Campaigns/           # Outreach management
│   │   ├── services/
│   │   │   ├── api.ts               # Backend API integration
│   │   │   └── storage.ts           # Local data management
│   │   ├── types/
│   │   │   ├── consultant.ts        # TypeScript type definitions
│   │   │   └── prospect.ts          # Prospect data types
│   │   └── utils/
│   │       └── helpers.ts           # Utility functions
│   ├── public/
│   │   └── index.html
│   └── dist/                        # Built frontend assets
├── tests/
│   ├── unit/                        # Unit tests for backend services
│   ├── integration/                 # API integration tests
│   └── e2e/                        # Playwright end-to-end tests
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── .env.example                     # Environment configuration template
├── requirements.txt                 # Python dependencies
└── README.md                       # Project documentation
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: OpenAI API Requirements
# - GPT-4 has 8k context limit, GPT-4-turbo has 128k - use appropriately
# - Rate limits: GPT-4 20 RPM, GPT-3.5-turbo 60 RPM for free tier
# - Function calling requires specific message format with 'tools' parameter
# - Always implement exponential backoff for rate limit errors (429)

# CRITICAL: FastAPI Async Patterns
# - All database operations must be async in FastAPI
# - Use dependency injection for database sessions and external services
# - Background tasks for long-running operations (research processing)
# - CORS middleware required for frontend integration

# CRITICAL: Web Scraping Ethics & Legal
# - Respect robots.txt and rate limits (max 1 request/second per domain)
# - Use rotating user agents and headers to avoid blocking
# - Implement retry logic with exponential backoff
# - Only scrape publicly available information

# CRITICAL: ReportLab PDF Generation
# - Use Platypus for complex layouts with flowables
# - Table formatting requires explicit column widths
# - Chart generation requires separate reportlab-graphics package
# - PDF streaming for large reports to avoid memory issues

# CRITICAL: Database Performance
# - Use connection pooling for high concurrency
# - Implement proper indexing for prospect lookup queries
# - Use bulk inserts for large data imports
# - Cache frequently accessed consultant templates

# CRITICAL: Environment Variables
# - Use python-dotenv for .env file loading
# - Separate development/production configurations
# - Never commit API keys to version control
# - Validate required environment variables on startup
```

## Implementation Blueprint

### Data Models and Structure
```python
# Core Pydantic models for type safety and validation
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ConsultantType(str, Enum):
    """15+ consultant specializations"""
    FRACTIONAL_CMO = "fractional_cmo"
    COPYWRITER = "copywriter"
    BUSINESS_TURNAROUND = "business_turnaround"
    PROCESS_OPTIMIZATION = "process_optimization"
    HR_PEOPLE = "hr_people"
    IT_TRANSFORMATION = "it_transformation"
    SALES_CONSULTANT = "sales_consultant"
    FINANCIAL_CONSULTANT = "financial_consultant"
    SUPPLY_CHAIN = "supply_chain"
    BRAND_STRATEGIST = "brand_strategist"
    DIGITAL_MARKETING = "digital_marketing"
    MA_ADVISOR = "ma_advisor"
    CYBERSECURITY = "cybersecurity"
    CRM_ERP = "crm_erp"
    CHANGE_MANAGEMENT = "change_management"

class ConsultantProfile(BaseModel):
    """Consultant profile with ICP and problem/solution framework"""
    id: Optional[str] = None
    consultant_type: ConsultantType
    industry_focus: List[str]
    target_company_size: str  # "startup", "smb", "mid-market", "enterprise"
    geographic_preference: List[str]
    problem_framework: Dict[str, Any]
    solution_positioning: str
    signal_priorities: Dict[str, float]  # weighted signal importance
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProspectSignal(BaseModel):
    """Individual signal detected for a prospect"""
    signal_type: str
    confidence_score: float  # 0.0 to 1.0
    data_source: str
    raw_data: Dict[str, Any]
    detected_at: datetime
    relevance_score: float  # based on consultant type

class ProspectCompany(BaseModel):
    """Company information and intelligence"""
    id: Optional[str] = None
    name: str
    domain: str
    industry: str
    company_size: str
    revenue_range: Optional[str] = None
    location: str
    description: str
    key_executives: List[Dict[str, Any]]
    signals: List[ProspectSignal]
    overall_score: float  # calculated from weighted signals
    research_status: str  # "pending", "processing", "completed", "failed"
    last_researched: Optional[datetime] = None

class ResearchTask(BaseModel):
    """Background research task tracking"""
    id: str
    consultant_id: str
    prospect_id: str
    task_type: str  # "initial_research", "deep_dive", "refresh"
    status: str  # "queued", "processing", "completed", "failed"
    priority: int  # 1-10, higher is more urgent
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
```

### List of Tasks to Complete the PRP (In Order)

```yaml
Task 1: Environment Setup and Project Structure
CREATE backend/core/config.py:
  - IMPLEMENT environment variable loading with python-dotenv
  - DEFINE configuration classes for development/production
  - VALIDATE required API keys (OpenAI, Google Search) on startup
  - SET UP logging configuration with structured logging

CREATE requirements.txt:
  - INCLUDE FastAPI[all], SQLAlchemy, Pydantic, OpenAI, Beautiful Soup
  - ADD ReportLab, Pandas, python-dotenv, pytest, ruff, mypy
  - SPECIFY exact versions for reproducible builds

CREATE docker/Dockerfile.backend:
  - USE Python 3.11+ base image for performance
  - IMPLEMENT multi-stage build for smaller production image
  - CONFIGURE proper user permissions and security hardening
  - SET UP health check endpoint

Task 2: Database Models and Core Infrastructure
CREATE backend/models/consultant.py:
  - IMPLEMENT SQLAlchemy ORM models matching Pydantic schemas
  - ADD proper indexes for query performance
  - INCLUDE audit fields (created_at, updated_at) with auto-population
  - SET UP relationship mappings between consultants and prospects

CREATE backend/core/database.py:
  - IMPLEMENT async database session management
  - CONFIGURE connection pooling for high concurrency
  - ADD database health check and connection retry logic
  - SET UP database migration management

CREATE backend/models/prospect.py:
  - IMPLEMENT prospect and company data models
  - ADD full-text search indexes for company names and descriptions
  - INCLUDE signal storage with JSON columns for flexible data
  - SET UP cascade deletion and data integrity constraints

Task 3: FastAPI Application Structure
CREATE backend/api/main.py:
  - IMPLEMENT FastAPI application with proper middleware
  - ADD CORS configuration for frontend integration
  - CONFIGURE exception handlers for graceful error responses
  - SET UP health check and status endpoints

CREATE backend/api/routes/consultants.py:
  - IMPLEMENT CRUD operations for consultant profiles
  - ADD input validation using Pydantic models
  - INCLUDE proper error handling and HTTP status codes
  - SET UP dependency injection for database sessions

CREATE backend/core/security.py:
  - IMPLEMENT API key authentication for initial version
  - ADD rate limiting middleware to prevent abuse
  - INCLUDE request logging and audit trail
  - SET UP CORS and security headers

Task 4: AI Services and OpenAI Integration
CREATE backend/utils/ai_helpers.py:
  - IMPLEMENT OpenAI client with proper error handling
  - ADD exponential backoff for rate limit errors
  - INCLUDE token counting and cost tracking
  - SET UP model selection logic (GPT-4 vs GPT-3.5-turbo)

CREATE backend/services/content_generator.py:
  - IMPLEMENT email generation using OpenAI function calling
  - ADD context-aware prompt engineering with consultant specialization
  - INCLUDE output validation and fallback strategies
  - SET UP template-based generation for consistency

CREATE backend/services/research_engine.py:
  - IMPLEMENT AI-powered research orchestration
  - ADD multi-source data aggregation and synthesis
  - INCLUDE signal detection and scoring algorithms
  - SET UP background task processing for long-running research

Task 5: Web Scraping and Data Collection
CREATE backend/services/web_scraper.py:
  - IMPLEMENT Beautiful Soup-based scraping with rotation
  - ADD respect for robots.txt and rate limiting
  - INCLUDE error handling and retry logic
  - SET UP data extraction patterns for common website types

CREATE backend/utils/data_processing.py:
  - IMPLEMENT data cleaning and normalization functions
  - ADD signal extraction from unstructured text
  - INCLUDE duplicate detection and data deduplication
  - SET UP data quality scoring and validation

Task 6: Consultant Templates and Signal Detection
CREATE backend/templates/consultant_templates.py:
  - IMPLEMENT 15+ consultant type definitions with signal patterns
  - ADD weighted scoring algorithms for each consultant type
  - INCLUDE problem/solution frameworks and ICP definitions
  - SET UP extensible template system for new consultant types

CREATE backend/services/signal_detector.py:
  - IMPLEMENT pattern recognition for consultant-specific signals
  - ADD machine learning-based signal classification
  - INCLUDE confidence scoring and signal prioritization
  - SET UP real-time signal processing pipeline

Task 7: PDF Generation and Report Services
CREATE backend/services/pdf_generator.py:
  - IMPLEMENT ReportLab-based PDF generation
  - ADD professional templates with charts and tables
  - INCLUDE executive summary and detailed analysis sections
  - SET UP PDF streaming for large reports

CREATE backend/templates/report_templates.py:
  - IMPLEMENT structured report layouts for different consultant types
  - ADD chart generation for prospect scoring and trends
  - INCLUDE executive profile formatting and company analysis
  - SET UP customizable report sections and branding

Task 8: API Routes and Business Logic
CREATE backend/api/routes/prospects.py:
  - IMPLEMENT prospect discovery and management endpoints
  - ADD search and filtering capabilities with pagination
  - INCLUDE bulk operations for prospect imports
  - SET UP webhook endpoints for external data sources

CREATE backend/api/routes/research.py:
  - IMPLEMENT research task management and status tracking
  - ADD background task triggers for research operations
  - INCLUDE research history and caching mechanisms
  - SET UP real-time progress updates via WebSocket

CREATE backend/api/routes/reports.py:
  - IMPLEMENT PDF generation and download endpoints
  - ADD report customization and templating options
  - INCLUDE report sharing and access control
  - SET UP report analytics and usage tracking

Task 9: Frontend TypeScript Application
CREATE frontend/src/types/consultant.ts:
  - IMPLEMENT TypeScript interfaces matching backend Pydantic models
  - ADD type guards for runtime type checking
  - INCLUDE utility types for API responses and forms
  - SET UP enum definitions for consultant types and statuses

CREATE frontend/src/services/api.ts:
  - IMPLEMENT API client with proper error handling
  - ADD request/response interceptors for logging
  - INCLUDE authentication token management
  - SET UP retry logic and offline handling

CREATE frontend/src/components/Wizard/:
  - IMPLEMENT multi-step consultant setup wizard
  - ADD form validation and progress indicators
  - INCLUDE conditional logic based on consultant type
  - SET UP data persistence between wizard steps

Task 10: Dashboard and User Interface
CREATE frontend/src/components/Dashboard/:
  - IMPLEMENT prospect pipeline management interface
  - ADD filtering, sorting, and search capabilities
  - INCLUDE real-time updates and status indicators
  - SET UP drag-and-drop pipeline management

CREATE frontend/src/components/Research/:
  - IMPLEMENT research task monitoring and control
  - ADD progress indicators and error handling
  - INCLUDE manual research trigger capabilities
  - SET UP research history and audit trail

Task 11: Testing Infrastructure
CREATE tests/unit/test_consultants.py:
  - IMPLEMENT comprehensive unit tests for consultant services
  - ADD test fixtures and mock data generators
  - INCLUDE edge case testing and error scenarios
  - SET UP test database isolation and cleanup

CREATE tests/integration/test_api.py:
  - IMPLEMENT full API integration tests
  - ADD authentication and authorization testing
  - INCLUDE performance testing for high-load scenarios
  - SET UP test data seeding and cleanup

CREATE tests/e2e/test_wizard.spec.js:
  - IMPLEMENT Playwright end-to-end tests for wizard flow
  - ADD screenshot comparison and visual regression testing
  - INCLUDE cross-browser compatibility testing
  - SET UP test report generation and CI integration

Task 12: Docker and Deployment
CREATE docker/docker-compose.yml:
  - IMPLEMENT multi-service Docker composition
  - ADD PostgreSQL database with persistent volumes
  - INCLUDE Redis for caching and background tasks
  - SET UP development and production environment configurations

CREATE docker/Dockerfile.frontend:
  - IMPLEMENT Node.js build process for TypeScript
  - ADD static asset optimization and compression
  - INCLUDE nginx configuration for production serving
  - SET UP proper caching headers and security

Task 13: Production Readiness and Monitoring
CREATE backend/core/monitoring.py:
  - IMPLEMENT structured logging with correlation IDs
  - ADD performance metrics and health checks
  - INCLUDE error tracking and alerting integration
  - SET UP database query performance monitoring

CREATE .env.example:
  - DOCUMENT all required environment variables
  - ADD example values and descriptions
  - INCLUDE security notes and best practices
  - SET UP separate configurations for different environments
```

### Critical Integration Points
```yaml
DATABASE:
  - migration: "Initial schema with consultants, prospects, signals, and research_tasks tables"
  - indexes: "CREATE INDEX idx_prospect_score ON prospects(overall_score DESC)"
  - indexes: "CREATE INDEX idx_signal_type ON signals(signal_type, confidence_score)"
  
CONFIG:
  - add to: backend/core/config.py
  - pattern: "OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')"
  - pattern: "RESEARCH_TIMEOUT = int(os.getenv('RESEARCH_TIMEOUT', '300'))"
  
ROUTES:
  - add to: backend/api/main.py  
  - pattern: "app.include_router(consultant_router, prefix='/api/v1/consultants')"
  - pattern: "app.include_router(research_router, prefix='/api/v1/research')"

BACKGROUND_TASKS:
  - setup: "Celery with Redis for long-running research operations"
  - pattern: "research_task.delay(consultant_id, prospect_id)"
  - monitoring: "Task status tracking and progress updates"
```

### Per-Task Pseudocode Examples

```python
# Task 4: AI Services Implementation
async def generate_prospect_email(
    consultant_profile: ConsultantProfile,
    prospect: ProspectCompany,
    research_data: Dict[str, Any]
) -> EmailDraft:
    # PATTERN: Use function calling for structured output
    system_prompt = build_email_prompt(consultant_profile.consultant_type)
    
    # CRITICAL: Use GPT-3.5-turbo for cost efficiency on email generation
    response = await openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate email for {prospect.name}"}
        ],
        tools=[EMAIL_GENERATION_TOOL],  # Function calling schema
        temperature=0.7,  # Slight creativity for personalization
        max_tokens=500    # Keep emails concise
    )
    
    # PATTERN: Validate and fallback on generation failures
    if not response.choices[0].message.tool_calls:
        return fallback_email_template(consultant_profile, prospect)
    
    return parse_email_response(response.choices[0].message.tool_calls[0])

# Task 6: Signal Detection Implementation  
async def detect_signals_for_prospect(
    prospect: ProspectCompany,
    consultant_type: ConsultantType,
    scraped_data: Dict[str, Any]
) -> List[ProspectSignal]:
    # PATTERN: Use consultant-specific signal patterns
    signal_patterns = CONSULTANT_TEMPLATES[consultant_type].signal_patterns
    detected_signals = []
    
    for pattern_name, pattern_config in signal_patterns.items():
        # CRITICAL: Use regex and NLP for pattern matching
        confidence = calculate_signal_confidence(
            scraped_data, 
            pattern_config.keywords,
            pattern_config.context_rules
        )
        
        if confidence > pattern_config.threshold:
            signal = ProspectSignal(
                signal_type=pattern_name,
                confidence_score=confidence,
                data_source="web_scraping",
                raw_data=extract_relevant_data(scraped_data, pattern_config),
                detected_at=datetime.utcnow(),
                relevance_score=pattern_config.weight
            )
            detected_signals.append(signal)
    
    return detected_signals

# Task 7: PDF Generation Implementation
async def generate_intelligence_report(
    consultant: ConsultantProfile,
    prospect: ProspectCompany,
    research_data: Dict[str, Any]
) -> bytes:
    # PATTERN: Use ReportLab Platypus for complex layouts
    doc = SimpleDocTemplate(
        BytesIO(),
        pagesize=letter,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    story = []
    
    # CRITICAL: Executive summary first for business users
    story.append(build_executive_summary(prospect, research_data))
    story.append(PageBreak())
    
    # PATTERN: Structured sections for different analysis types
    story.append(build_company_overview(prospect))
    story.append(build_signal_analysis(prospect.signals, consultant.consultant_type))
    story.append(build_executive_profiles(prospect.key_executives))
    story.append(build_recommendations(consultant, prospect, research_data))
    
    # GOTCHA: ReportLab requires explicit table column widths
    if research_data.get('financial_data'):
        financial_table = build_financial_table(
            research_data['financial_data'],
            colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch]
        )
        story.append(financial_table)
    
    doc.build(story)
    return doc.buffer.getvalue()
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
ruff check backend/ --fix          # Auto-fix formatting and import issues
mypy backend/                      # Type checking for all backend code
ruff check frontend/src/ --fix     # Frontend linting and formatting

# Expected: No errors. If errors occur, read and fix systematically
```

### Level 2: Unit Tests
```python
# CREATE comprehensive unit tests for each service
def test_consultant_profile_creation():
    """Test consultant profile creation and validation"""
    profile_data = {
        "consultant_type": "fractional_cmo",
        "industry_focus": ["technology", "saas"],
        "target_company_size": "mid-market",
        "geographic_preference": ["north_america"],
        "problem_framework": {"primary_focus": "marketing_chaos"},
        "solution_positioning": "Marketing strategy optimization"
    }
    
    profile = ConsultantProfile(**profile_data)
    assert profile.consultant_type == ConsultantType.FRACTIONAL_CMO
    assert len(profile.industry_focus) == 2

def test_signal_detection_accuracy():
    """Test signal detection with known patterns"""
    test_data = {
        "press_releases": ["CMO departure announced", "Marketing team restructuring"],
        "job_postings": ["Seeking fractional marketing leader"],
        "financial_reports": ["Marketing spend efficiency concerns"]
    }
    
    signals = detect_signals_for_prospect(
        mock_prospect,
        ConsultantType.FRACTIONAL_CMO,
        test_data
    )
    
    assert len(signals) >= 2
    assert any(s.signal_type == "cmo_departure" for s in signals)
    assert all(s.confidence_score > 0.5 for s in signals)

def test_email_generation_personalization():
    """Test email generation with consultant context"""
    email = generate_prospect_email(
        mock_consultant_profile,
        mock_prospect,
        {"recent_news": "Product launch challenges"}
    )
    
    assert mock_prospect.name in email.body
    assert mock_consultant_profile.solution_positioning in email.body
    assert len(email.body) > 100  # Substantial content
    assert email.subject is not None
```

```bash
# Run and iterate until all tests pass:
docker run --rm -v $(pwd):/app consultant-platform pytest tests/unit/ -v
# If failing: Analyze error, fix root cause, re-run
```

### Level 3: Integration Tests
```bash
# Start the full stack with Docker
docker-compose up -d

# Wait for services to be ready
sleep 30

# Test the complete wizard flow
curl -X POST http://localhost:8000/api/v1/consultants \
  -H "Content-Type: application/json" \
  -d '{
    "consultant_type": "fractional_cmo",
    "industry_focus": ["technology"],
    "target_company_size": "mid-market",
    "geographic_preference": ["north_america"],
    "problem_framework": {"focus": "marketing_chaos"},
    "solution_positioning": "Marketing strategy optimization"
  }'

# Expected: {"id": "uuid", "status": "created", ...}

# Test prospect research trigger
curl -X POST http://localhost:8000/api/v1/research/start \
  -H "Content-Type: application/json" \
  -d '{
    "consultant_id": "uuid-from-above",
    "prospect_domain": "example-company.com"
  }'

# Expected: {"task_id": "uuid", "status": "queued", ...}

# Test PDF report generation
curl -X GET http://localhost:8000/api/v1/reports/uuid-from-above \
  -H "Accept: application/pdf" \
  -o test_report.pdf

# Expected: PDF file with prospect intelligence report
```

### Level 4: End-to-End Testing
```bash
# Run Playwright tests for complete user flows
docker run --rm -v $(pwd):/app consultant-platform npm run test:e2e

# Test wizard completion, prospect research, and report generation
# Expected: All E2E scenarios pass with screenshots and performance metrics
```

## Final Validation Checklist
- [ ] All unit tests pass: `docker run consultant-platform pytest tests/ -v`
- [ ] No linting errors: `ruff check backend/ frontend/src/`
- [ ] No type errors: `mypy backend/`
- [ ] Integration tests successful: Complete API workflow functions
- [ ] E2E tests pass: Full user journey from wizard to report generation
- [ ] Docker deployment works: `docker-compose up` starts all services
- [ ] Performance benchmarks met: <2s API response times under load
- [ ] Security validation: No exposed secrets or vulnerable endpoints
- [ ] Documentation complete: API docs generated and accessible

## Anti-Patterns to Avoid
- ❌ Don't hardcode consultant templates - use extensible configuration system
- ❌ Don't ignore OpenAI rate limits - implement proper backoff and queuing
- ❌ Don't scrape without respecting robots.txt and rate limits
- ❌ Don't generate PDFs synchronously - use background tasks for large reports
- ❌ Don't store API keys in code - use environment variables exclusively
- ❌ Don't skip input validation - use Pydantic models throughout
- ❌ Don't ignore database indexing - optimize for common query patterns
- ❌ Don't deploy without comprehensive logging and monitoring

---

## Quality Assessment Score: 9/10

**Strengths:**
- Comprehensive technical specifications with detailed implementation guidance
- Complete validation pipeline with executable tests at each level
- Extensive context including documentation references and gotchas
- Modular architecture supporting extensibility and maintainability
- Production-ready considerations including Docker, monitoring, and security

**Areas for Enhancement:**
- Limited actual scraped documentation due to API balance constraints
- Could benefit from more specific performance benchmarks and SLA definitions

**One-Pass Implementation Confidence:** HIGH - This PRP provides sufficient context, validation loops, and detailed specifications to enable successful implementation by an AI agent with access to the referenced documentation and codebase patterns.