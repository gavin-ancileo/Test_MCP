"""
40 Prompts Data for AAP Platform based on Persona Sheet
Each prompt has 2-5 requirement fields and role-based categories
"""

PROMPTS_DATA = [
    # Business Analyst Agent (BA-1 to BA-4)
    ('ba_1_qualify_sms', 'BA-1: SMS Business Requirements Qualification', '["ba","service_delivery"]', '''List of questions to qualify SMS business requirements.

Project: {{project_name}}
Stakeholder: {{stakeholder_name}}
Business Domain: {{business_domain}}
Priority: {{priority}}

Questions to ask:
- What is the business problem you are trying to solve?
- What are the key success metrics?
- Who are the target users?
- What is the expected timeline?
- What are the integration requirements?'''),

    ('ba_2_bdd_analysis', 'BA-2: BDD File Analysis', '["ba","tech_delivery"]', '''Analyze BDD file and extract requirements.

BDD File: {{bdd_file}}
Feature: {{feature_name}}
Scenarios: {{scenario_count}}

Extract:
- User stories from scenarios
- Acceptance criteria
- Test cases
- Data requirements
- Integration points'''),

    ('ba_3_requirements_gathering', 'BA-3: Requirements Gathering Session', '["ba","general_delivery"]', '''Conduct requirements gathering session.

Session Type: {{session_type}}
Participants: {{participants}}
Duration: {{duration}}
Objectives: {{objectives}}

Document:
- Business requirements
- Functional requirements
- Non-functional requirements
- Assumptions and constraints
- Open questions'''),

    ('ba_4_stakeholder_mapping', 'BA-4: Stakeholder Mapping', '["ba","operations"]', '''Create stakeholder mapping for project.

Project: {{project_name}}
Business Unit: {{business_unit}}
Region: {{region}}

Identify:
- Primary stakeholders
- Secondary stakeholders
- Influence and interest levels
- Communication requirements
- Decision makers'''),

    # Cybersecurity Agent (C-1, C-2)
    ('cyber_1_security_report', 'C-1: Security Report Generation', '["cybersecurity","security"]', '''Generate security reporting and analysis.

Report Type: {{report_type}}
Period: {{report_period}}
System: {{system_name}}
Severity Level: {{severity_level}}

Include:
- Threat analysis
- Vulnerability assessment
- Incident summary
- Compliance status
- Recommendations'''),

    ('cyber_2_security_audit', 'C-2: Security Audit', '["cybersecurity","security"]', '''Conduct security audit.

Audit Type: {{audit_type}}
Scope: {{audit_scope}}
Compliance Framework: {{compliance_framework}}
Findings Severity: {{severity}}

Audit Areas:
- Access controls
- Data encryption
- Network security
- Application security
- Policy compliance'''),

    # Finance Agent (F-1)
    ('finance_1_financial_report', 'F-1: Financial Reporting and Analysis', '["finance","finance"]', '''Generate financial reporting and analysis.

Report Period: {{report_period}}
Customer: {{customer}}
Currency: {{currency}}
Invoice Type: {{invoice_type}}

Report Sections:
- Revenue analysis
- Cost breakdown
- Profitability metrics
- Budget variance
- Forecast'''),

    # Business Intelligence Agent (BI-1, BI-2)
    ('bi_1_performance_report', 'BI-1: Performance Reporting and Analysis - Clarity', '["bi","data"]', '''Generate performance reporting and analysis from Clarity.

Report Period: {{report_period}}
Customer: {{customer}}
Report Type: {{report_type}}
Region: {{region}}
Product: {{product}}

Metrics:
- Key performance indicators
- Trends analysis
- Benchmark comparison
- Forecast
- Recommendations'''),

    ('bi_2_data_strategy', 'BI-2: Data Strategy and Reporting', '["bi","data"]', '''Access all data strategy and reporting.

Strategy Area: {{strategy_area}}
Data Source: {{data_source}}
Business Unit: {{business_unit}}
Report Format: {{report_format}}

Include:
- Data strategy overview
- Current state assessment
- Target state vision
- Implementation roadmap
- Success metrics'''),

    # Developer Agent (D-1)
    ('dev_1_code_review', 'D-1: Code Review and Analysis', '["dev","tech_delivery"]', '''Review code and provide analysis.

Repository: {{repository}}
Branch: {{branch}}
Pull Request: {{pr_number}}
Language: {{language}}

Review Areas:
- Code quality
- Security vulnerabilities
- Performance issues
- Test coverage
- Best practices'''),

    # PM Agent (PM-1)
    ('pm_1_project_charter', 'PM-1: Project Charter Creation', '["pm","project_management"]', '''Create project charter.

Project Name: {{project_name}}
Sponsor: {{sponsor}}
Project Manager: {{project_manager}}
Timeline: {{timeline}}
Budget: {{budget}}

Charter Sections:
- Project objectives
- Scope definition
- Stakeholders
- Risks and assumptions
- Success criteria'''),

    # HR Agent (HR-1 to HR-4)
    ('hr_1_offer_letter', 'HR-1: Offer Letter Generation', '["hr","hr"]', '''Generate employment offer letter.

Candidate Name: {{candidate_name}}
Position Title: {{position_title}}
Company Name: {{company_name}}
Start Date: {{start_date}}
Base Salary: {{base_salary}}
Currency: {{currency}}

Letter Includes:
- Position details
- Compensation package
- Benefits summary
- Start date and location
- Acceptance deadline'''),

    ('hr_2_onboarding', 'HR-2: Employee Onboarding', '["hr","hr"]', '''Create employee onboarding plan.

Employee Name: {{employee_name}}
Position: {{position}}
Department: {{department}}
Start Date: {{start_date}}

Onboarding Checklist:
- First day agenda
- Training schedule
- Equipment setup
- Access provisioning
- Mentor assignment'''),

    ('hr_3_performance_review', 'HR-3: Performance Review', '["hr","hr"]', '''Conduct performance review.

Employee Name: {{employee_name}}
Review Period: {{review_period}}
Reviewer: {{reviewer}}
Role: {{role}}

Review Areas:
- Goals achievement
- Strengths and development areas
- Feedback
- Career development
- Next period objectives'''),

    ('hr_4_exit_interview', 'HR-4: Exit Interview', '["hr","hr"]', '''Conduct exit interview.

Employee Name: {{employee_name}}
Last Day: {{last_day}}
Department: {{department}}
Reason: {{reason}}

Interview Topics:
- Reasons for leaving
- Work experience feedback
- Suggestions for improvement
- Knowledge transfer
- Future plans'''),

    # Principal Engineer (PE-1)
    ('pe_1_architecture_review', 'PE-1: Architecture Review', '["principal_engineer","infrastructure"]', '''Conduct architecture review.

System Name: {{system_name}}
Review Scope: {{review_scope}}
Technology Stack: {{tech_stack}}
Team Size: {{team_size}}

Review Focus:
- System design
- Scalability
- Security architecture
- Performance optimization
- Technical debt'''),

    # DevOps Agent (DA-1)
    ('devops_1_deployment', 'DA-1: Deployment Planning', '["devops","infrastructure"]', '''Plan deployment strategy.

Application: {{application}}
Environment: {{environment}}
Version: {{version}}
Deployment Type: {{deployment_type}}

Deployment Plan:
- Pre-deployment checklist
- Deployment steps
- Rollback procedure
- Monitoring setup
- Post-deployment validation'''),

    # Configuration Agent (CA-1)
    ('config_1_config_management', 'CA-1: Configuration Management', '["config","infrastructure"]', '''Manage system configuration.

System: {{system}}
Environment: {{environment}}
Configuration Type: {{config_type}}
Change Request: {{change_request}}

Configuration Tasks:
- Current state analysis
- Change requirements
- Impact assessment
- Implementation plan
- Validation steps'''),

    # QA Agent (QA-1)
    ('qa_1_test_planning', 'QA-1: Test Planning', '["qa","tech_delivery"]', '''Create test plan.

Project: {{project}}
Feature: {{feature}}
Test Level: {{test_level}}
Timeline: {{timeline}}

Test Plan Includes:
- Test scope
- Test cases
- Test data requirements
- Test environment setup
- Test schedule'''),

    # Scrum Master Agent (SM-1 to SM-6)
    ('sm_1_sprint_planning', 'SM-1: Sprint Planning - Distribution', '["scrum_master","agile"]', '''Facilitate sprint planning meeting.

Sprint Number: {{sprint_number}}
Team: {{team}}
Duration: {{duration}}
Velocity: {{velocity}}

Planning Activities:
- Sprint goal definition
- User story selection
- Task breakdown
- Effort estimation
- Capacity planning'''),

    ('sm_2_daily_standup', 'SM-2: Daily Standup Facilitation', '["scrum_master","agile"]', '''Facilitate daily standup.

Team: {{team}}
Sprint Day: {{sprint_day}}
Attendees: {{attendees}}
Format: {{format}}

Standup Topics:
- Yesterday accomplishments
- Today plans
- Blockers
- Action items
- Metrics update'''),

    ('sm_3_sprint_review', 'SM-3: Sprint Review', '["scrum_master","agile"]', '''Conduct sprint review.

Sprint Number: {{sprint_number}}
Team: {{team}}
Demo Duration: {{demo_duration}}
Stakeholders: {{stakeholders}}

Review Agenda:
- Sprint goal achievement
- Demo of completed work
- Feedback collection
- Product backlog refinement
- Next sprint preview'''),

    ('sm_4_retrospective', 'SM-4: Sprint Retrospective', '["scrum_master","agile"]', '''Facilitate sprint retrospective.

Sprint Number: {{sprint_number}}
Team: {{team}}
Format: {{format}}
Focus Area: {{focus_area}}

Retrospective Sections:
- What went well
- What could be improved
- Action items
- Team health check
- Process improvements'''),

    ('sm_5_backlog_refinement', 'SM-5: Backlog Refinement', '["scrum_master","agile"]', '''Facilitate backlog refinement.

Product: {{product}}
Sprint: {{sprint}}
Items to Refine: {{item_count}}
Priority: {{priority}}

Refinement Activities:
- User story review
- Acceptance criteria definition
- Effort estimation
- Dependencies identification
- Priority ordering'''),

    ('sm_6_team_metrics', 'SM-6: Team Metrics Dashboard', '["scrum_master","agile"]', '''Generate team metrics dashboard.

Team: {{team}}
Sprint Range: {{sprint_range}}
Metrics: {{metrics}}
Visualization: {{visualization}}

Metrics Include:
- Velocity trends
- Burndown chart
- Defect rate
- Cycle time
- Team happiness'''),

    # Project Management Agent (PMA-1 to PMA-3)
    ('pma_1_project_status', 'PMA-1: Project Status Report', '["pm","project_management"]', '''Generate project status report.

Project: {{project}}
Report Period: {{report_period}}
Status: {{status}}
Stakeholders: {{stakeholders}}

Report Sections:
- Executive summary
- Progress update
- Milestones achieved
- Risks and issues
- Next steps'''),

    ('pma_2_risk_management', 'PMA-2: Risk Management', '["pm","project_management"]', '''Manage project risks.

Project: {{project}}
Risk Category: {{risk_category}}
Impact: {{impact}}
Probability: {{probability}}

Risk Management:
- Risk identification
- Risk assessment
- Mitigation strategies
- Contingency plans
- Risk monitoring'''),

    ('pma_3_stakeholder_communication', 'PMA-3: Stakeholder Communication', '["pm","project_management"]', '''Manage stakeholder communication.

Project: {{project}}
Stakeholder Group: {{stakeholder_group}}
Communication Type: {{comm_type}}
Frequency: {{frequency}}

Communication Plan:
- Message content
- Delivery method
- Timeline
- Feedback mechanism
- Escalation path'''),

    # Tech Lead Agent (TL-1 to TL-4)
    ('tl_1_technical_design', 'TL-1: Technical Design Document', '["tech_lead","tech_delivery"]', '''Create technical design document.

Feature: {{feature}}
System: {{system}}
Technology: {{technology}}
Team: {{team}}

Design Sections:
- Architecture overview
- Component design
- Data model
- API specifications
- Implementation approach'''),

    ('tl_2_code_standards', 'TL-2: Code Standards Review', '["tech_lead","tech_delivery"]', '''Review and enforce code standards.

Language: {{language}}
Framework: {{framework}}
Team: {{team}}
Project: {{project}}

Standards Review:
- Coding conventions
- Best practices
- Code review checklist
- Documentation requirements
- Testing standards'''),

    ('tl_3_technical_debt', 'TL-3: Technical Debt Assessment', '["tech_lead","tech_delivery"]', '''Assess technical debt.

Project: {{project}}
Area: {{area}}
Priority: {{priority}}
Impact: {{impact}}

Assessment Includes:
- Debt inventory
- Impact analysis
- Cost estimation
- Prioritization
- Remediation plan'''),

    ('tl_4_team_coaching', 'TL-4: Team Technical Coaching', '["tech_lead","tech_delivery"]', '''Provide technical coaching to team.

Team: {{team}}
Focus Area: {{focus_area}}
Duration: {{duration}}
Format: {{format}}

Coaching Areas:
- Technical skills development
- Code review practices
- Architecture principles
- Problem-solving approaches
- Knowledge sharing'''),

    # Additional prompts to reach 40
    ('ba_5_use_case_analysis', 'BA-5: Use Case Analysis', '["ba","service_delivery"]', '''Analyze use cases for system design.

System: {{system}}
Use Case: {{use_case}}
Actor: {{actor}}
Goal: {{goal}}

Analysis Includes:
- Use case description
- Pre-conditions
- Post-conditions
- Main flow
- Alternative flows
- Exception handling'''),

    ('cyber_3_incident_response', 'C-3: Security Incident Response', '["cybersecurity","security"]', '''Manage security incident response.

Incident ID: {{incident_id}}
Severity: {{severity}}
Affected Systems: {{affected_systems}}
Detection Time: {{detection_time}}

Response Steps:
- Incident classification
- Containment actions
- Eradication steps
- Recovery procedures
- Lessons learned'''),

    ('bi_3_dashboard_creation', 'BI-3: Dashboard Creation', '["bi","data"]', '''Create business intelligence dashboard.

Dashboard Type: {{dashboard_type}}
Data Source: {{data_source}}
Metrics: {{metrics}}
Audience: {{audience}}

Dashboard Components:
- Key metrics visualization
- Trend analysis
- Comparative charts
- Drill-down capabilities
- Export functionality'''),

    ('dev_2_api_design', 'D-2: API Design and Documentation', '["dev","tech_delivery"]', '''Design and document API.

API Name: {{api_name}}
Version: {{version}}
Protocol: {{protocol}}
Authentication: {{auth_type}}

API Design Includes:
- Endpoint definitions
- Request/response schemas
- Authentication methods
- Error handling
- Rate limiting'''),

    ('hr_5_training_plan', 'HR-5: Employee Training Plan', '["hr","hr"]', '''Create employee training plan.

Employee Name: {{employee_name}}
Role: {{role}}
Training Type: {{training_type}}
Duration: {{duration}}

Training Plan:
- Training objectives
- Course modules
- Timeline
- Assessment criteria
- Certification requirements'''),

    ('qa_2_test_automation', 'QA-2: Test Automation Strategy', '["qa","tech_delivery"]', '''Develop test automation strategy.

Project: {{project}}
Framework: {{framework}}
Test Levels: {{test_levels}}
Timeline: {{timeline}}

Automation Strategy:
- Tool selection
- Test scope
- Framework architecture
- CI/CD integration
- Maintenance plan'''),

    ('pma_4_budget_management', 'PMA-4: Budget Management', '["pm","project_management"]', '''Manage project budget.

Project: {{project}}
Total Budget: {{total_budget}}
Current Spend: {{current_spend}}
Variance: {{variance}}

Budget Management:
- Budget breakdown
- Cost tracking
- Variance analysis
- Forecast
- Cost optimization'''),

    ('tl_5_integration_design', 'TL-5: System Integration Design', '["tech_lead","tech_delivery"]', '''Design system integration.

System A: {{system_a}}
System B: {{system_b}}
Integration Type: {{integration_type}}
Protocol: {{protocol}}

Integration Design:
- Architecture pattern
- Data flow
- Error handling
- Monitoring
- Security considerations''')
]
