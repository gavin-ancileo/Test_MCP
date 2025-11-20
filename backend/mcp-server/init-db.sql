-- AAP Database Initialization
-- Creates prompts table and inserts all 16 prompts

CREATE TABLE IF NOT EXISTS prompts (
    id SERIAL PRIMARY KEY,
    code TEXT,
    name TEXT,
    categories TEXT,
    content TEXT,
    variables TEXT,
    output_folder TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    schema TEXT
);

-- Check if already populated
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM prompts LIMIT 1) THEN
        -- Insert all 16 prompts
        INSERT INTO prompts (id, code, name, categories, content, variables, output_folder, is_active, schema) VALUES
        
        ('1', 'hr_offer_letter_detailed', 'Offer Letter (Detailed)', '["hr"]', 'Subject: Offer of Employment – {{candidate_name}}

Dear {{candidate_name}},

We are pleased to offer you the position of {{position_title}} at {{company_name}}. Your employment is expected to start on {{start_date}} at our {{work_location}} office (work mode: {{work_mode}}), reporting to {{manager_name}}.

Compensation & Benefits:
- Base salary: {{base_salary}} {{currency}} per {{salary_period}}
- Target bonus: {{bonus?}}
- Equity: {{equity?}}
- Benefits summary: {{benefits_summary?}}
- Probation period: {{probation_length}}

Key Terms:
- Standard working hours and overtime policy per company handbook
- Confidentiality, IP assignment, and code of conduct policies apply
- Employment subject to background/reference checks (if applicable)

Next Steps:
- Please confirm acceptance by {{accept_by_date}} via signing and replying to {{hr_email}}.
- Your onboarding instructions will be sent separately.

We are excited to welcome you to {{company_name}}!

Sincerely,
{{hr_representative}}
Human Resources
{{company_name}}', '["accept_by_date", "base_salary", "benefits_summary", "bonus", "candidate_name", "company_name", "currency", "equity", "hr_email", "hr_representative", "manager_name", "position_title", "probation_length", "salary_period", "start_date", "work_location", "work_mode"]', 'drive://folder/1ViGWBhDzjbNit-oy0YTMaB8PSke8PVrs', '1', '{"type": "object", "properties": {"candidate_name": {"type": "string", "description": "Candidate Name"}, "position_title": {"type": "string", "description": "Position Title"}, "company_name": {"type": "string", "description": "Company Name"}, "start_date": {"type": "string", "description": "Start Date"}, "work_location": {"type": "string", "description": "Work Location"}, "work_mode": {"type": "string", "description": "Work Mode"}, "manager_name": {"type": "string", "description": "Manager Name"}, "base_salary": {"type": "string", "description": "Base Salary"}, "currency": {"type": "string", "description": "Currency"}, "salary_period": {"type": "string", "description": "Salary Period"}, "bonus": {"type": "string", "description": "Bonus"}, "equity": {"type": "string", "description": "Equity"}, "benefits_summary": {"type": "string", "description": "Benefits Summary"}, "probation_length": {"type": "string", "description": "Probation Length"}, "accept_by_date": {"type": "string", "description": "Accept By Date"}, "hr_email": {"type": "string", "description": "Hr Email"}, "hr_representative": {"type": "string", "description": "Hr Representative"}}, "required": ["candidate_name", "position_title", "company_name", "start_date", "work_location", "work_mode", "manager_name", "base_salary", "currency", "salary_period", "probation_length", "accept_by_date", "hr_email", "hr_representative"]}'),
        
        ('2', 'hr_employment_contract_detailed', 'Employment Contract (Detailed)', '["hr"]', 'Employment Agreement

This Employment Agreement ("Agreement") is entered into by and between {{company_name}} ("Company") and {{employee_name}} ("Employee").
Role: {{position_title}} | Start Date: {{start_date}} | Location: {{work_location}} | Employment Type: {{employment_type}}

1) Compensation
- Base salary: {{base_salary}} {{currency}} per {{salary_period}}
- Bonus/Commission: {{bonus_terms?}}
- Equity: {{equity_terms?}}

2) Work Hours & Leave
- Standard hours: {{hours_per_week}} hours/week
- Leave policy: {{leave_policy_url?}}

3) Confidentiality & IP
- Confidentiality clause: {{confidentiality_clause}}
- IP assignment clause: {{ip_clause}}

4) Probation & Termination
- Probation length: {{probation_length}}
- Notice period: {{notice_period}}

5) Governing Law & Dispute Resolution
- Governing law: {{governing_law}}

Agreed and Accepted:

Company:
{{company_signatory_name}}
{{company_signatory_title}}
Date: {{company_sign_date}}

Employee:
{{employee_name}}
Date: {{employee_sign_date}}', '["base_salary", "bonus_terms", "company_name", "company_sign_date", "company_signatory_name", "company_signatory_title", "confidentiality_clause", "currency", "employee_name", "employee_sign_date", "employment_type", "equity_terms", "governing_law", "hours_per_week", "ip_clause", "leave_policy_url", "notice_period", "position_title", "probation_length", "salary_period", "start_date", "work_location"]', 'drive://folder/1ViGWBhDzjbNit-oy0YTMaB8PSke8PVrs', '1', '{"type": "object", "properties": {"company_name": {"type": "string", "description": "Company Name"}, "employee_name": {"type": "string", "description": "Employee Name"}, "position_title": {"type": "string", "description": "Position Title"}, "start_date": {"type": "string", "description": "Start Date"}, "work_location": {"type": "string", "description": "Work Location"}, "employment_type": {"type": "string", "description": "Employment Type"}, "base_salary": {"type": "string", "description": "Base Salary"}, "currency": {"type": "string", "description": "Currency"}, "salary_period": {"type": "string", "description": "Salary Period"}, "bonus_terms": {"type": "string", "description": "Bonus Terms"}, "equity_terms": {"type": "string", "description": "Equity Terms"}, "hours_per_week": {"type": "string", "description": "Hours Per Week"}, "leave_policy_url": {"type": "string", "description": "Leave Policy URL"}, "confidentiality_clause": {"type": "string", "description": "Confidentiality Clause"}, "ip_clause": {"type": "string", "description": "Ip Clause"}, "probation_length": {"type": "string", "description": "Probation Length"}, "notice_period": {"type": "string", "description": "Notice Period"}, "governing_law": {"type": "string", "description": "Governing Law"}, "company_signatory_name": {"type": "string", "description": "Company Signatory Name"}, "company_signatory_title": {"type": "string", "description": "Company Signatory Title"}, "company_sign_date": {"type": "string", "description": "Company Sign Date"}, "employee_sign_date": {"type": "string", "description": "Employee Sign Date"}}, "required": ["company_name", "employee_name", "position_title", "start_date", "work_location", "employment_type", "base_salary", "currency", "salary_period", "hours_per_week", "confidentiality_clause", "ip_clause", "probation_length", "notice_period", "governing_law", "company_signatory_name", "company_signatory_title", "company_sign_date", "employee_sign_date"]}'),
        
        ('3', 'hr_onboarding_pack', 'Onboarding Plan & Checklist', '["hr"]', 'Onboarding Plan – {{employee_name}} ({{position_title}}, {{department}})
Start date: {{start_date}} | Location: {{location}} | Manager: {{manager_name}} | Buddy: {{buddy_name}}

1) Day 1 Agenda ({{orientation_time}})
- Welcome & Introductions
- Laptop & equipment handover: {{equipment_list}}
- Accounts provisioning: {{accounts_list}}
- Security & compliance briefing

2) Week 1 Plan
- Team onboarding & product overview
- Mandatory training: {{training_list}}
- Meet stakeholders
- First tasks & expectations

3) Policies & Acknowledgements
- Code of Conduct, Privacy, Security training
- PTO/Leave policy acknowledgment
- Payroll setup (deadline: {{payroll_setup_deadline}})

4) 30/60/90-Day Goals
- 30 days: {{goals_30}}
- 60 days: {{goals_60}}
- 90 days: {{goals_90}}

5) Probation & Feedback
- Probation length: {{probation_length}}
- Feedback cadence: weekly with manager
- Mid-probation review date: {{mid_probation_review_date}}

Notes:
{{additional_notes?}}', '["accounts_list", "additional_notes", "buddy_name", "department", "employee_name", "equipment_list", "goals_30", "goals_60", "goals_90", "location", "manager_name", "mid_probation_review_date", "orientation_time", "payroll_setup_deadline", "position_title", "probation_length", "start_date", "training_list"]', 'drive://folder/1ViGWBhDzjbNit-oy0YTMaB8PSke8PVrs', '1', '{"type": "object", "properties": {"employee_name": {"type": "string", "description": "Employee Name"}, "position_title": {"type": "string", "description": "Position Title"}, "department": {"type": "string", "description": "Department"}, "start_date": {"type": "string", "description": "Start Date"}, "location": {"type": "string", "description": "Location"}, "manager_name": {"type": "string", "description": "Manager Name"}, "buddy_name": {"type": "string", "description": "Buddy Name"}, "orientation_time": {"type": "string", "description": "Orientation Time"}, "equipment_list": {"type": "string", "description": "Equipment List"}, "accounts_list": {"type": "string", "description": "Accounts List"}, "training_list": {"type": "string", "description": "Training List"}, "payroll_setup_deadline": {"type": "string", "description": "Payroll Setup Deadline"}, "goals_30": {"type": "string", "description": "Goals 30"}, "goals_60": {"type": "string", "description": "Goals 60"}, "goals_90": {"type": "string", "description": "Goals 90"}, "probation_length": {"type": "string", "description": "Probation Length"}, "mid_probation_review_date": {"type": "string", "description": "Mid Probation Review Date"}, "additional_notes": {"type": "string", "description": "Additional Notes"}}, "required": ["employee_name", "position_title", "department", "start_date", "location", "manager_name", "buddy_name", "orientation_time", "equipment_list", "accounts_list", "training_list", "payroll_setup_deadline", "goals_30", "goals_60", "goals_90", "probation_length", "mid_probation_review_date"]}'),
        
        ('4', 'hr_termination_notice_detailed', 'Termination Notice (Detailed)', '["hr"]', 'Subject: Notice of Employment Termination – {{employee_name}}

Dear {{employee_name}},

This letter is to inform you that your employment with {{company_name}} will end effective {{termination_date}}. Reason for termination: {{termination_reason}}.

Final Pay and Benefits:
- Final paycheck covers wages up to {{termination_date}} and accrued benefits per policy.
- Insurance/benefits: {{benefits_continuation_info?}}.

Company Property:
- Please return all devices, badges, and materials by {{property_return_deadline}} to {{return_location}}.

Exit Process:
- Exit interview: {{exit_interview_datetime}} with {{hr_contact}}.
- References and employment verification: {{reference_policy?}}.

If you have questions, contact {{hr_contact}} or {{legal_contact}}.

Sincerely,
{{hr_representative}}
Human Resources
{{company_name}}', '["benefits_continuation_info", "company_name", "employee_name", "exit_interview_datetime", "hr_contact", "hr_representative", "legal_contact", "property_return_deadline", "reference_policy", "return_location", "termination_date", "termination_reason"]', 'drive://folder/1ViGWBhDzjbNit-oy0YTMaB8PSke8PVrs', '1', '{"type": "object", "properties": {"employee_name": {"type": "string", "description": "Employee Name"}, "company_name": {"type": "string", "description": "Company Name"}, "termination_date": {"type": "string", "description": "Termination Date"}, "termination_reason": {"type": "string", "description": "Termination Reason"}, "benefits_continuation_info": {"type": "string", "description": "Benefits Continuation Info"}, "property_return_deadline": {"type": "string", "description": "Property Return Deadline"}, "return_location": {"type": "string", "description": "Return Location"}, "exit_interview_datetime": {"type": "string", "description": "Exit Interview Datetime"}, "hr_contact": {"type": "string", "description": "Hr Contact"}, "reference_policy": {"type": "string", "description": "Reference Policy"}, "legal_contact": {"type": "string", "description": "Legal Contact"}, "hr_representative": {"type": "string", "description": "Hr Representative"}}, "required": ["employee_name", "company_name", "termination_date", "termination_reason", "property_return_deadline", "return_location", "exit_interview_datetime", "hr_contact", "legal_contact", "hr_representative"]}'),
        
        ('5', 'ba_brd_detailed', 'Business Requirements Document (BRD) – Detailed', '["ba", "pm"]', 'BRD – {{project_name}}
Client: {{client_name}} | BA: {{ba_name}} | Date: {{date}}

1) Business Context & Objectives
{{business_context}}
Objectives:
{{business_objectives}}

2) Scope
In-Scope:
{{in_scope}}
Out-of-Scope:
{{out_of_scope}}

3) Stakeholders
{{stakeholders}}

4) High-Level Requirements
{{high_level_requirements}}

5) Business Rules
{{business_rules}}

6) Process Overview
As-Is:
{{as_is?}}
To-Be:
{{to_be}}

7) Data & Integrations
Key Entities:
{{data_entities}}
Interfaces/APIs:
{{interfaces}}

8) Non-Functional Requirements (NFR)
{{nfr}}

9) Risks & Assumptions
Risks:
{{risks}}
Assumptions:
{{assumptions?}}

10) Acceptance Criteria
{{acceptance_criteria}}

Sign-Off:
Sponsor: {{sponsor}} | Target Release: {{target_release}}
', '["acceptance_criteria", "as_is", "assumptions", "ba_name", "business_context", "business_objectives", "business_rules", "client_name", "data_entities", "date", "high_level_requirements", "in_scope", "interfaces", "nfr", "out_of_scope", "project_name", "risks", "sponsor", "stakeholders", "target_release", "to_be"]', '', '1', '{"type": "object", "properties": {"project_name": {"type": "string", "description": "Project Name"}, "client_name": {"type": "string", "description": "Client Name"}, "ba_name": {"type": "string", "description": "BA Name"}, "date": {"type": "string", "description": "Date"}, "business_context": {"type": "string", "description": "Business Context"}, "business_objectives": {"type": "string", "description": "Business Objectives"}, "in_scope": {"type": "string", "description": "In Scope"}, "out_of_scope": {"type": "string", "description": "Out Of Scope"}, "stakeholders": {"type": "string", "description": "Stakeholders"}, "high_level_requirements": {"type": "string", "description": "High Level Requirements"}, "business_rules": {"type": "string", "description": "Business Rules"}, "as_is": {"type": "string", "description": "As Is"}, "to_be": {"type": "string", "description": "To Be"}, "data_entities": {"type": "string", "description": "Data Entities"}, "interfaces": {"type": "string", "description": "Interfaces"}, "nfr": {"type": "string", "description": "NFR"}, "risks": {"type": "string", "description": "Risks"}, "assumptions": {"type": "string", "description": "Assumptions"}, "acceptance_criteria": {"type": "string", "description": "Acceptance Criteria"}, "sponsor": {"type": "string", "description": "Sponsor"}, "target_release": {"type": "string", "description": "Target Release"}}, "required": ["project_name", "client_name", "ba_name", "date", "business_context", "business_objectives", "in_scope", "out_of_scope", "stakeholders", "high_level_requirements", "business_rules", "to_be", "data_entities", "interfaces", "nfr", "risks", "acceptance_criteria", "sponsor", "target_release"]}'),
        
        ('6', 'ba_user_story_set_detailed', 'User Story Pack – Detailed', '["ba", "pm", "tech_lead"]', 'User Story Pack – {{project_name}}
Author: {{ba_name}} | Date: {{date}}

Epic/Feature: {{epic_name}}

1) Story List
{{stories}}

2) Acceptance Criteria Template
GIVEN {{ac_given}}
WHEN {{ac_when}}
THEN {{ac_then}}

3) Dependencies
{{dependencies?}}

4) DoR / DoD
- DoR: {{dor?}}
- DoD: {{dod?}}

Notes:
{{notes?}}
', '["ac_given", "ac_then", "ac_when", "ba_name", "date", "dependencies", "dod", "dor", "epic_name", "notes", "project_name", "stories"]', '', '1', '{"type": "object", "properties": {"project_name": {"type": "string", "description": "Project Name"}, "ba_name": {"type": "string", "description": "BA Name"}, "date": {"type": "string", "description": "Date"}, "epic_name": {"type": "string", "description": "Epic Name"}, "stories": {"type": "string", "description": "Stories"}, "ac_given": {"type": "string", "description": "Ac Given"}, "ac_when": {"type": "string", "description": "Ac When"}, "ac_then": {"type": "string", "description": "Ac Then"}, "dependencies": {"type": "string", "description": "Dependencies"}, "dor": {"type": "string", "description": "Dor"}, "dod": {"type": "string", "description": "Dod"}, "notes": {"type": "string", "description": "Notes"}}, "required": ["project_name", "ba_name", "date", "epic_name", "stories", "ac_given", "ac_when", "ac_then"]}'),
        
        ('7', 'ba_process_flow_spec', 'Process Flow & State Machine Spec', '["ba", "pm", "qa"]', 'Process Flow Spec – {{project_name}}
Scope Area: {{scope_area}} | Author: {{ba_name}} | Date: {{date}}

1) Actors & Swimlanes
Primary Actors:
{{primary_actors}}
Swimlanes:
{{swimlanes}}

2) As-Is Process
{{asis_description?}}

3) To-Be Process
{{tobe_description}}

4) Happy Path
{{happy_path}}

5) Alternate Flows / Exceptions
{{alternate_flows}}
{{exceptions?}}

6) Business Rules
{{business_rules}}

7) Data Entities & State Transitions
{{data_entities}}
State Machine:
{{state_machine}}

8) Non-Functional Requirements
{{nfrs?}}

9) Open Questions
{{open_questions?}}', '["alternate_flows", "asis_description", "ba_name", "business_rules", "data_entities", "date", "exceptions", "happy_path", "nfrs", "open_questions", "primary_actors", "project_name", "scope_area", "state_machine", "swimlanes", "tobe_description"]', 'drive://folder/1ViGWBhDzjbNit-oy0YTMaB8PSke8PVrs', '1', '{"type": "object", "properties": {"project_name": {"type": "string", "description": "Project Name"}, "scope_area": {"type": "string", "description": "Scope Area"}, "ba_name": {"type": "string", "description": "BA Name"}, "date": {"type": "string", "description": "Date"}, "primary_actors": {"type": "string", "description": "Primary Actors"}, "swimlanes": {"type": "string", "description": "Swimlanes"}, "asis_description": {"type": "string", "description": "Asis Description"}, "tobe_description": {"type": "string", "description": "Tobe Description"}, "happy_path": {"type": "string", "description": "Happy Path"}, "alternate_flows": {"type": "string", "description": "Alternate Flows"}, "exceptions": {"type": "string", "description": "Exceptions"}, "business_rules": {"type": "string", "description": "Business Rules"}, "data_entities": {"type": "string", "description": "Data Entities"}, "state_machine": {"type": "string", "description": "State Machine"}, "nfrs": {"type": "string", "description": "Nfrs"}, "open_questions": {"type": "string", "description": "Open Questions"}}, "required": ["project_name", "scope_area", "ba_name", "date", "primary_actors", "swimlanes", "tobe_description", "happy_path", "alternate_flows", "business_rules", "data_entities", "state_machine"]}'),
        
        ('8', 'ba_rtm_matrix', 'Requirements Traceability Matrix (RTM)', '["ba", "pm", "qa"]', 'RTM – {{project_name}}
Owner: {{ba_name}} | Date: {{date}}

1) Requirements List
{{requirements_list}}

2) Mapping to User Stories
{{stories_mapping}}

3) Mapping to Test Cases
{{test_cases_mapping}}

4) Risks & Dependencies
{{risks?}}
{{dependencies?}}

5) Ownership & Due Dates
{{owners}}
Target Due Date: {{due_date}}

Notes:
{{notes?}}', '["ba_name", "date", "dependencies", "due_date", "notes", "owners", "project_name", "requirements_list", "risks", "stories_mapping", "test_cases_mapping"]', 'drive://folder/1ViGWBhDzjbNit-oy0YTMaB8PSke8PVrs', '1', '{"type": "object", "properties": {"project_name": {"type": "string", "description": "Project Name"}, "ba_name": {"type": "string", "description": "BA Name"}, "date": {"type": "string", "description": "Date"}, "requirements_list": {"type": "string", "description": "Requirements List"}, "stories_mapping": {"type": "string", "description": "Stories Mapping"}, "test_cases_mapping": {"type": "string", "description": "Test Cases Mapping"}, "risks": {"type": "string", "description": "Risks"}, "dependencies": {"type": "string", "description": "Dependencies"}, "owners": {"type": "string", "description": "Owners"}, "due_date": {"type": "string", "description": "Due Date"}, "notes": {"type": "string", "description": "Notes"}}, "required": ["project_name", "ba_name", "date", "requirements_list", "stories_mapping", "test_cases_mapping", "owners", "due_date"]}'),
        
        ('9', 'ba_fsd_generator', 'Functional Specification Document (FSD) Generator', '["ba", "pm", "tech_lead"]', 'FSD – {{project_name}}
Source: {{brd_document_id?}} / Inline BRD: {{brd_text?}}
Author: {{author_name}} | Date: {{date}}

1) Overview & Goals
{{overview}}

2) Functional Scope
{{functional_scope}}

3) Detailed Requirements
{{detailed_requirements}}

4) Screens / UX Flows
{{ux_flows?}}

5) Data Model
{{data_model}}

6) Integrations
{{integrations}}

7) NFR
{{nfr}}

8) Acceptance Criteria
{{acceptance_criteria}}

9) Open Issues
{{open_issues?}}', '["acceptance_criteria", "author_name", "brd_document_id", "brd_text", "data_model", "date", "detailed_requirements", "functional_scope", "integrations", "nfr", "open_issues", "overview", "project_name", "ux_flows"]', 'drive://folder/1ViGWBhDzjbNit-oy0YTMaB8PSke8PVrs', '1', '{"type": "object", "properties": {"project_name": {"type": "string", "description": "Project Name"}, "brd_document_id": {"type": "string", "description": "Brd Document ID"}, "brd_text": {"type": "string", "description": "Brd Text"}, "author_name": {"type": "string", "description": "Author Name"}, "date": {"type": "string", "description": "Date"}, "overview": {"type": "string", "description": "Overview"}, "functional_scope": {"type": "string", "description": "Functional Scope"}, "detailed_requirements": {"type": "string", "description": "Detailed Requirements"}, "ux_flows": {"type": "string", "description": "UX Flows"}, "data_model": {"type": "string", "description": "Data Model"}, "integrations": {"type": "string", "description": "Integrations"}, "nfr": {"type": "string", "description": "NFR"}, "acceptance_criteria": {"type": "string", "description": "Acceptance Criteria"}, "open_issues": {"type": "string", "description": "Open Issues"}}, "required": ["project_name", "author_name", "date", "overview", "functional_scope", "detailed_requirements", "data_model", "integrations", "nfr", "acceptance_criteria"]}'),
        
        ('10', 'ba_openapi_generator', 'OpenAPI Spec Generator', '["ba", "pm", "tech_lead", "backend"]', 'API Specification – {{project_name}}
Context: {{system_context}}
Auth: {{auth_mode}}
Resources:
{{resources}}

Conventions: {{conventions?}}
Rate Limits: {{rate_limits?}}
Error Model: {{error_model?}}
Security Notes: {{security_notes?}}
Examples: {{examples?}}', '["auth_mode", "conventions", "error_model", "examples", "project_name", "rate_limits", "resources", "security_notes", "system_context"]', 'drive://folder/1ViGWBhDzjbNit-oy0YTMaB8PSke8PVrs', '1', '{"type": "object", "properties": {"project_name": {"type": "string", "description": "Project Name"}, "system_context": {"type": "string", "description": "System Context"}, "auth_mode": {"type": "string", "description": "Auth Mode"}, "resources": {"type": "string", "description": "Resources"}, "conventions": {"type": "string", "description": "Conventions"}, "rate_limits": {"type": "string", "description": "Rate Limits"}, "error_model": {"type": "string", "description": "Error Model"}, "security_notes": {"type": "string", "description": "Security Notes"}, "examples": {"type": "string", "description": "Examples"}}, "required": ["project_name", "system_context", "auth_mode", "resources"]}'),
        
        ('11', 'ba_fsd_to_jira', 'FSD → Jira Tickets', '["ba", "pm", "qa"]', 'Ticketization Plan – {{project_name}}
Source FSD: {{fsd_document_id?}} / Inline: {{fsd_text?}}
Epic: {{epic_name}} | Labels: {{labels?}}
Assignee Rules: {{assignee_rules?}}

BACKLOG
{{backlog_items}}

QA Test Plan Summary
{{qa_plan?}}', '["assignee_rules", "backlog_items", "epic_name", "fsd_document_id", "fsd_text", "labels", "project_name", "qa_plan"]', 'drive://folder/1ViGWBhDzjbNit-oy0YTMaB8PSke8PVrs', '1', '{"type": "object", "properties": {"project_name": {"type": "string", "description": "Project Name"}, "fsd_document_id": {"type": "string", "description": "Fsd Document ID"}, "fsd_text": {"type": "string", "description": "Fsd Text"}, "epic_name": {"type": "string", "description": "Epic Name"}, "labels": {"type": "string", "description": "Labels"}, "assignee_rules": {"type": "string", "description": "Assignee Rules"}, "backlog_items": {"type": "string", "description": "Backlog Items"}, "qa_plan": {"type": "string", "description": "QA Plan"}}, "required": ["project_name", "epic_name", "backlog_items"]}'),
        
        ('12', 'github_security_audit', 'GitHub Security Audit (Auto-Detected)', '["security", "github", "devops"]', '# GitHub Security Audit – {{repo_url}}
Auditor: {{auditor_name}}
Date: {{audit_date?}}

## Instructions
- Analyze the repository at {{repo_url}} (optionally branch {{repo_branch?}}).
- AUTO-DETECT findings and severities (critical/high/medium/low) from code, configs, CI, dependencies, containers, IaC.
- DO NOT require the user to provide counts. Derive counts from your findings and show the math.
- Score rules: start 100, deduct Critical×25, High×10, Medium×5, Low×1 (min 0).
- Gating: if any Critical > 0 ⇒ final_status = BLOCKER.
- Output MUST include: derived_counts, security_score (computed), final_grade, final_status, top_risks, remediation_plan with owners & SLAs.
- If {{audit_date}} is empty, use today''s date.

## Context (Optional)
{{repo_analysis?}}

## Results
### Derived Counts
- Critical: {{derived_critical?}}
- High: {{derived_high?}}
- Medium: {{derived_medium?}}
- Low: {{derived_low?}}

### Findings (summarized)
{{findings_overview?}}

### Detailed Findings by Category
- Secrets/Creds: {{secrets_findings?}}
- Dependencies/SBOM: {{deps_findings?}}
- CI/CD: {{cicd_findings?}}
- Code Scanning/CodeQL: {{codeql_findings?}}
- IAM/Least Privilege: {{iam_findings?}}
- Containers/Docker: {{container_findings?}}
- IaC: {{iac_findings?}}
- Runtime/Observability: {{runtime_findings?}}

### Score & Decision
- Score: {{security_score?}}
- Grade: {{final_grade?}}
- Status: {{final_status?}} (APPROVED | CONDITIONAL_APPROVAL | BLOCKER | REJECTED)
- Notes: {{final_notes?}}
', '["audit_date", "auditor_name", "cicd_findings", "codeql_findings", "container_findings", "deps_findings", "derived_critical", "derived_high", "derived_low", "derived_medium", "final_grade", "final_notes", "final_status", "findings_overview", "iac_findings", "iam_findings", "repo_analysis", "repo_branch", "repo_url", "runtime_findings", "secrets_findings", "security_score"]', '', '1', '{"type": "object", "properties": {"repo_url": {"type": "string", "description": "Repo URL"}, "auditor_name": {"type": "string", "description": "Auditor Name"}, "audit_date": {"type": "string", "description": "Audit Date"}, "repo_branch": {"type": "string", "description": "Repo Branch"}, "repo_analysis": {"type": "string", "description": "Repo Analysis"}, "derived_critical": {"type": "string", "description": "Derived Critical"}, "derived_high": {"type": "string", "description": "Derived High"}, "derived_medium": {"type": "string", "description": "Derived Medium"}, "derived_low": {"type": "string", "description": "Derived Low"}, "findings_overview": {"type": "string", "description": "Findings Overview"}, "secrets_findings": {"type": "string", "description": "Secrets Findings"}, "deps_findings": {"type": "string", "description": "Deps Findings"}, "cicd_findings": {"type": "string", "description": "Cicd Findings"}, "codeql_findings": {"type": "string", "description": "Codeql Findings"}, "iam_findings": {"type": "string", "description": "IAM Findings"}, "container_findings": {"type": "string", "description": "Container Findings"}, "iac_findings": {"type": "string", "description": "Iac Findings"}, "runtime_findings": {"type": "string", "description": "Runtime Findings"}, "security_score": {"type": "string", "description": "Security Score"}, "final_grade": {"type": "string", "description": "Final Grade"}, "final_status": {"type": "string", "description": "Final Status"}, "final_notes": {"type": "string", "description": "Final Notes"}}, "required": ["repo_url", "auditor_name"]}'),
        
        ('13', 'qa_test_plan', 'QA Test Plan', '["qa", "testing"]', '# QA Test Plan – {{project_name}}
Release: {{release_version}} | Owner: {{qa_owner}} | Date: {{date}}

## Scope
{{scope}}

## Strategy
- Levels: {{test_levels}}
- Environments: {{environments}}
- Entry/Exit Criteria: {{entry_exit_criteria}}

## Design
- Risk Areas: {{risk_areas}}
- Test Data: {{test_data}}
- Tools: {{tooling?}}

## Traceability & Coverage
- Requirements Map: {{requirements_map}}
- Coverage Goals: {{coverage_goals}}

## Schedule & Owners
- Timeline: {{timeline}}
- Owners: {{owners}}
- Reporting: {{reporting_cadence}}
', '["coverage_goals", "date", "entry_exit_criteria", "environments", "owners", "project_name", "qa_owner", "release_version", "reporting_cadence", "requirements_map", "risk_areas", "scope", "test_data", "test_levels", "timeline", "tooling"]', '', '1', '{"type": "object", "properties": {"project_name": {"type": "string", "description": "Project Name"}, "release_version": {"type": "string", "description": "Release Version"}, "qa_owner": {"type": "string", "description": "QA Owner"}, "date": {"type": "string", "description": "Date"}, "scope": {"type": "string", "description": "Scope"}, "test_levels": {"type": "string", "description": "Test Levels"}, "environments": {"type": "string", "description": "Environments"}, "entry_exit_criteria": {"type": "string", "description": "Entry Exit Criteria"}, "risk_areas": {"type": "string", "description": "Risk Areas"}, "test_data": {"type": "string", "description": "Test Data"}, "tooling": {"type": "string", "description": "Tooling"}, "requirements_map": {"type": "string", "description": "Requirements Map"}, "coverage_goals": {"type": "string", "description": "Coverage Goals"}, "timeline": {"type": "string", "description": "Timeline"}, "owners": {"type": "string", "description": "Owners"}, "reporting_cadence": {"type": "string", "description": "Reporting Cadence"}}, "required": ["project_name", "release_version", "qa_owner", "date", "scope", "test_levels", "environments", "entry_exit_criteria", "risk_areas", "test_data", "requirements_map", "coverage_goals", "timeline", "owners", "reporting_cadence"]}'),
        
        ('14', 'qa_test_execution', 'QA Test Execution Report', '["qa", "testing"]', '# QA Execution – {{project_name}} ({{cycle_name}})
Owner: {{qa_owner}} | Date: {{date}}

## Summary
- Total: {{total_cases}}
- Executed: {{executed_cases}}
- Passed: {{passed_cases}}
- Failed: {{failed_cases}}
- Blocked: {{blocked_cases?}}
- Pass Rate: {{pass_rate?}}

## Defects by Severity
- Critical: {{defect_critical}}
- High: {{defect_high}}
- Medium: {{defect_medium}}
- Low: {{defect_low}}

## Risks & Recommendations
{{risks}}
{{recommendations}}
', '["blocked_cases", "cycle_name", "date", "defect_critical", "defect_high", "defect_low", "defect_medium", "executed_cases", "failed_cases", "pass_rate", "passed_cases", "project_name", "qa_owner", "recommendations", "risks", "total_cases"]', '', '1', '{"type": "object", "properties": {"project_name": {"type": "string", "description": "Project Name"}, "cycle_name": {"type": "string", "description": "Cycle Name"}, "qa_owner": {"type": "string", "description": "QA Owner"}, "date": {"type": "string", "description": "Date"}, "total_cases": {"type": "string", "description": "Total Cases"}, "executed_cases": {"type": "string", "description": "Executed Cases"}, "passed_cases": {"type": "string", "description": "Passed Cases"}, "failed_cases": {"type": "string", "description": "Failed Cases"}, "blocked_cases": {"type": "string", "description": "Blocked Cases"}, "pass_rate": {"type": "string", "description": "Pass Rate"}, "defect_critical": {"type": "string", "description": "Defect Critical"}, "defect_high": {"type": "string", "description": "Defect High"}, "defect_medium": {"type": "string", "description": "Defect Medium"}, "defect_low": {"type": "string", "description": "Defect Low"}, "risks": {"type": "string", "description": "Risks"}, "recommendations": {"type": "string", "description": "Recommendations"}}, "required": ["project_name", "cycle_name", "qa_owner", "date", "total_cases", "executed_cases", "passed_cases", "failed_cases", "defect_critical", "defect_high", "defect_medium", "defect_low", "risks", "recommendations"]}'),
        
        ('15', 'jira_ba_epic_stories', 'Jira – BA Epics & Stories Generator', '["ba", "pm", "jira"]', '# Jira Backlog – {{project_key}} / {{epic_name}}
BA: {{ba_name}} | Date: {{date}}

## Epic
- Goal: {{epic_goal}}
- Acceptance: {{epic_acceptance}}

## Stories (GIVEN/WHEN/THEN)
{{stories}}

## Tasks
{{tasks?}}

## Links & Labels
- Labels: {{labels?}}
- Components: {{components?}}
- Dependencies: {{dependencies?}}
- Services: {{services?}}
', '["ba_name", "components", "date", "dependencies", "epic_acceptance", "epic_goal", "epic_name", "labels", "project_key", "services", "stories", "tasks"]', '', '1', '{"type": "object", "properties": {"project_key": {"type": "string", "description": "Project Key"}, "epic_name": {"type": "string", "description": "Epic Name"}, "ba_name": {"type": "string", "description": "BA Name"}, "date": {"type": "string", "description": "Date"}, "epic_goal": {"type": "string", "description": "Epic Goal"}, "epic_acceptance": {"type": "string", "description": "Epic Acceptance"}, "stories": {"type": "string", "description": "Stories"}, "tasks": {"type": "string", "description": "Tasks"}, "labels": {"type": "string", "description": "Labels"}, "components": {"type": "string", "description": "Components"}, "dependencies": {"type": "string", "description": "Dependencies"}, "services": {"type": "string", "description": "Services"}}, "required": ["project_key", "epic_name", "ba_name", "date", "epic_goal", "epic_acceptance", "stories"]}'),
        
        ('16', 'github_code_review', 'GitHub Code Review (Focused)', '["github", "review"]', '# Code Review – PR {{pr_number}} ({{repo}})
Focus: {{focus_areas=security,performance,correctness,testing,docs}}

## Summary
{{summary?}}

## Findings
- Correctness: {{findings_correctness?}}
- Security: {{findings_security?}}
- Performance: {{findings_perf?}}
- Testing: {{findings_testing?}}
- Maintainability: {{findings_maintain?}}

## Action Items
{{action_items}}
## Verdict
{{verdict}}  (approve/request changes/comment)
', '["action_items", "findings_correctness", "findings_maintain", "findings_perf", "findings_security", "findings_testing", "focus_areas", "pr_number", "repo", "summary", "verdict"]', '', '1', '{"type": "object", "properties": {"pr_number": {"type": "string", "description": "PR Number"}, "repo": {"type": "string", "description": "Repo"}, "focus_areas": {"type": "string", "description": "Focus Areas", "default": "security,performance,correctness,testing,docs"}, "summary": {"type": "string", "description": "Summary"}, "findings_correctness": {"type": "string", "description": "Findings Correctness"}, "findings_security": {"type": "string", "description": "Findings Security"}, "findings_perf": {"type": "string", "description": "Findings Perf"}, "findings_testing": {"type": "string", "description": "Findings Testing"}, "findings_maintain": {"type": "string", "description": "Findings Maintain"}, "action_items": {"type": "string", "description": "Action Items"}, "verdict": {"type": "string", "description": "Verdict"}}, "required": ["pr_number", "repo", "action_items", "verdict"]}');
        
        RAISE NOTICE '✅ Inserted 16 prompts successfully';
    ELSE
        RAISE NOTICE '⚠️  Prompts table already populated, skipping insert';
    END IF;
END $$;