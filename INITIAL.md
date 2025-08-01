## FEATURE:

FEATURES:
Core Platform Features

Universal Wizard-Based Setup: Dynamic consultant profile creation that adapts to any consulting niche (fractional CMOs, copywriters, business turnaround, IT transformation, etc.)
Intelligent Signal Detection: AI-powered system that automatically suggests relevant prospect signals based on consultant type, with ability for users to add custom signals
Pre-Built Consultant Templates: Ready-to-use templates for 15+ consultant types including fractional CMOs, copywriters, business turnaround consultants, process optimization, HR consultants, etc.
Dynamic Research Engine: Comprehensive prospect intelligence gathering using publicly available sources (company websites, press releases, LinkedIn, news articles, financial filings, etc.)
Universal Prospect Scoring: Flexible scoring system with customizable weightings based on consultant-specific criteria
Interactive Dashboard: Personalized dashboard showing prospect pipeline, research status, and key insights
PDF Intelligence Reports: Comprehensive prospect analysis reports with executive profiles, pain points, and recommended approach
Email Draft Generator: AI-powered email body text generation for outreach campaigns (copy-paste ready for Gmail)

Wizard Flow Components

Consultant Profile Setup

Industry selection and specialization
Target client ideal customer profile (ICP) definition
Problem/solution framework configuration
Geographic and company size preferences


Research Configuration

Signal priority customization
Data source preferences
Research depth and frequency settings
Output format preferences


Prospect Pipeline Management

Prospect discovery and qualification
Research status tracking
Outreach campaign planning
Results monitoring and optimization



Intelligence Gathering System

Multi-Source Data Aggregation: Company websites, press releases, news articles, LinkedIn profiles, SEC filings, earnings call transcripts
Signal Synthesis Engine: Pattern recognition across multiple data sources to identify operational tensions, growth challenges, and consulting opportunities
Executive Profiling: Leadership team analysis, decision-maker identification, communication style analysis
Timing Intelligence: Identification of decision windows, pressure points, and optimal outreach timing
Competitive Context Analysis: Industry benchmarking and competitive positioning insights

Output Generation

Dynamic Dashboard: Real-time prospect pipeline with filtering, sorting, and drill-down capabilities
Comprehensive PDF Reports: Executive-ready prospect intelligence briefings with actionable insights
Personalized Email Templates: Context-aware outreach messages demonstrating deep understanding of prospect's situation
Campaign Tracking: Multi-touch sequence planning and performance monitoring

EXAMPLES:
Consultant Templates (15+ Types)

Fractional CMO: Focus on marketing chaos signals, growth stagnation, marketing team turnover
Copywriter: Target companies with poor messaging, rebranding initiatives, new product launches
Business Turnaround Consultant: Identify margin pressure, operational inefficiencies, integration challenges
Process Optimization: Look for manual workflows, system integration issues, efficiency complaints
HR/People Consultant: Track hiring freezes, culture issues, leadership changes, employee satisfaction surveys
IT Transformation: Monitor system upgrade mentions, cybersecurity incidents, digital transformation initiatives
Sales Consultant: Identify pipeline issues, CRM problems, sales team turnover, revenue misses
Financial Consultant: Track cash flow issues, audit problems, CFO changes, financial reporting delays
Supply Chain Consultant: Look for logistics issues, vendor problems, inventory challenges
Brand Strategist: Monitor rebranding efforts, brand reputation issues, market positioning changes
Digital Marketing: Track website redesigns, SEO issues, digital advertising spend changes
M&A Advisor: Identify acquisition activity, divestiture signals, strategic planning initiatives
Cybersecurity Consultant: Monitor security breaches, compliance issues, system vulnerabilities
CRM/ERP Implementation: Look for system implementation projects, user adoption issues, integration challenges
Change Management: Track organizational restructuring, cultural transformation, merger integration

Sample Prospect Intelligence Flow
Example: Fractional CMO Template

Target Signals: Marketing team departures, declining lead generation, rebranding announcements, new product launches, marketing budget increases/cuts
Research Sources: Company press releases, marketing job postings, LinkedIn activity, industry publications
Key Metrics: Marketing spend efficiency, lead generation trends, brand mention sentiment, competitive positioning
Pain Point Synthesis: Marketing chaos indicators, growth bottlenecks, team capability gaps
Outreach Angle: Marketing strategy optimization, team building, growth acceleration



## EXAMPLES:

In the `examples/` folder, there is a README for you to read to understand what the example is all about and also how to structure your own README when you create documentation for the above feature.

- `examples/cli.py` - use this as a template to create the CLI
- `examples/agent/` - read through all of the files here to understand best practices for creating Pydantic AI agents that support different providers and LLMs, handling agent dependencies, and adding tools to the agent.

Don't copy any of these examples directly, it is for a different project entirely. But use this as inspiration and for best practices.

## DOCUMENTATION:

DOCUMENTATION:
Core Technologies

Frontend: TypeScript/Vanilla JS for maximum flexibility and performance
Backend: Python FastAPI for robust API development and AI integration
AI/ML Integration: OpenAI GPT models for research synthesis and content generation
Web Scraping: Beautiful Soup, Scrapy for public data collection
PDF Generation: ReportLab or WeasyPrint for professional report creation
Data Processing: Pandas for data analysis and signal processing
Search APIs: Google Custom Search API for publicly available information

Key Documentation Resources

FastAPI Documentation: https://fastapi.tiangolo.com/
TypeScript Documentation: https://www.typescriptlang.org/docs/
OpenAI API Documentation: https://platform.openai.com/docs
Beautiful Soup Documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
Pandas Documentation: https://pandas.pydata.org/docs/
ReportLab Documentation: https://www.reportlab.com/docs/reportlab-userguide.pdf



## OTHER CONSIDERATIONS:

TECHNICAL ARCHITECTURE:
Backend Structure
/backend
  /api
    /routes
      - consultants.py (consultant profile management)
      - prospects.py (prospect discovery and management)
      - research.py (intelligence gathering endpoints)
      - reports.py (PDF generation and dashboard data)
      - campaigns.py (outreach campaign management)
  /core
    - config.py (application configuration)
    - database.py (data persistence layer)
  /services
    - research_engine.py (AI-powered research orchestration)
    - signal_detector.py (pattern recognition and signal synthesis)
    - content_generator.py (email and report generation)
    - web_scraper.py (public data collection)
  /models
    - consultant.py (consultant profile data models)
    - prospect.py (prospect and company data models)
    - research.py (research data and signal models)
  /utils
    - ai_helpers.py (OpenAI integration utilities)
    - data_processing.py (data cleaning and analysis)
Frontend Structure
/frontend
  /src
    /components
      - Wizard/ (multi-step consultant setup)
      - Dashboard/ (prospect pipeline interface)
      - Research/ (research management interface)
      - Reports/ (PDF viewer and generator)
      - Campaigns/ (outreach management)
    /services
      - api.ts (backend API integration)
      - storage.ts (local data management)
    /types
      - consultant.ts (TypeScript type definitions)
      - prospect.ts (prospect data types)
    /utils
      - helpers.ts (utility functions)
OTHER CONSIDERATIONS:
Environment Configuration

Include comprehensive .env.example with all required API keys and configuration options
Support for multiple AI model providers (OpenAI, Anthropic, local models)
Configurable research depth and frequency settings
Customizable scoring weights and criteria

Data Privacy & Ethics

Exclusive use of publicly available information
No scraping of private or password-protected content
Compliance with robots.txt and website terms of service
Data retention and deletion policies

Scalability Considerations

Efficient caching for repeated research queries
Rate limiting for external API calls
Batch processing for large prospect lists
Performance optimization for dashboard loading

User Experience

Intuitive wizard flow with progress indicators
Real-time research status updates
Exportable data in multiple formats (CSV, JSON, PDF)
Responsive design for desktop and mobile use

Development Guidelines

Comprehensive error handling and user feedback
Extensive logging for debugging and optimization
Unit tests for core business logic
API documentation with OpenAPI/Swagger
Docker containerization for easy deployment



