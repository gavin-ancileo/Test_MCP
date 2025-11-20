-- Simplified prompts with 2-5 key required inputs
-- Optional parameters are kept minimal and clearly marked with ?

TRUNCATE TABLE prompts RESTART IDENTITY CASCADE;

INSERT INTO prompts (code, name, categories, content) VALUES

-- HR PROMPTS
('email_professional', 'Professional Email', ARRAY['Communication', 'Business']::text[],
'Subject: {{subject}}

Dear {{recipient_name}},

{{main_message}}

{{closing_remarks?}}

Best regards,
{{sender_name}}
{{sender_title?}}
{{company_name?}}'),

('meeting_agenda', 'Meeting Agenda', ARRAY['Business', 'Planning']::text[],
'Meeting Agenda
Date: {{meeting_date}}
Topic: {{meeting_topic}}

Attendees: {{attendees}}

Agenda Items:
{{agenda_items}}

Meeting Duration: {{duration?}}
Location: {{location?}}

Notes:
- Please come prepared with relevant materials
- Questions and discussions are encouraged
{{additional_notes?}}'),

('project_proposal', 'Project Proposal', ARRAY['Business', 'Planning']::text[],
'Project Proposal: {{project_name}}

Executive Summary:
{{project_summary}}

Objectives:
{{project_objectives}}

Timeline: {{timeline}}

Budget Estimate: {{budget?}}

Team Requirements:
{{team_requirements?}}

Success Metrics:
{{success_metrics?}}

Risks and Mitigation:
{{risks?}}

Next Steps:
{{next_steps?}}'),

('bug_report', 'Bug Report', ARRAY['Technical', 'Development']::text[],
'Bug Report #{{ticket_number?}}

Title: {{bug_title}}
Severity: {{severity}}

Description:
{{bug_description}}

Steps to Reproduce:
{{reproduction_steps}}

Expected Result: {{expected_result?}}
Actual Result: {{actual_result?}}

Environment:
{{environment?}}

Screenshots/Logs:
{{attachments?}}'),

('code_review', 'Code Review Request', ARRAY['Technical', 'Development']::text[],
'Code Review Request

Pull Request: {{pr_title}}
Branch: {{branch_name}}

Changes Summary:
{{changes_summary}}

Testing Done:
{{testing_details?}}

Checklist:
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
{{additional_checklist?}}

Related Issues: {{related_issues?}}'),

('user_story', 'User Story', ARRAY['Agile', 'Development']::text[],
'User Story: {{story_title}}

As a {{user_role}}
I want to {{user_need}}
So that {{business_value}}

Acceptance Criteria:
{{acceptance_criteria}}

Priority: {{priority?}}
Story Points: {{story_points?}}

Dependencies:
{{dependencies?}}'),

('test_case', 'Test Case', ARRAY['QA', 'Testing']::text[],
'Test Case: {{test_name}}

Objective: {{test_objective}}

Preconditions:
{{preconditions}}

Test Steps:
{{test_steps}}

Expected Results:
{{expected_results}}

Test Data: {{test_data?}}
Environment: {{test_environment?}}

Notes: {{additional_notes?}}'),

('api_documentation', 'API Documentation', ARRAY['Technical', 'Documentation']::text[],
'API Endpoint: {{endpoint_url}}
Method: {{http_method}}

Description:
{{endpoint_description}}

Request Parameters:
{{request_params}}

Response Format:
{{response_format?}}

Example Request:
{{example_request?}}

Example Response:
{{example_response?}}

Error Codes:
{{error_codes?}}'),

('deployment_checklist', 'Deployment Checklist', ARRAY['DevOps', 'Operations']::text[],
'Deployment Checklist for {{application_name}}
Version: {{version}}
Environment: {{environment}}

Pre-Deployment:
{{pre_deployment_steps}}

Deployment Steps:
{{deployment_steps}}

Post-Deployment Verification:
{{verification_steps?}}

Rollback Plan:
{{rollback_plan?}}

Contacts:
{{emergency_contacts?}}'),

('incident_report', 'Incident Report', ARRAY['Operations', 'Support']::text[],
'Incident Report

Incident ID: {{incident_id}}
Date/Time: {{incident_datetime}}
Severity: {{severity}}

Description:
{{incident_description}}

Impact:
{{impact_assessment}}

Root Cause:
{{root_cause?}}

Resolution:
{{resolution_steps?}}

Follow-up Actions:
{{follow_up?}}'),

('performance_review', 'Performance Review', ARRAY['HR', 'Management']::text[],
'Performance Review

Employee: {{employee_name}}
Period: {{review_period}}
Reviewer: {{reviewer_name}}

Performance Summary:
{{performance_summary}}

Key Achievements:
{{achievements}}

Areas for Improvement:
{{improvement_areas?}}

Goals for Next Period:
{{future_goals?}}

Overall Rating: {{rating?}}'),

('job_posting', 'Job Posting', ARRAY['HR', 'Recruitment']::text[],
'Position: {{job_title}}
Department: {{department}}
Location: {{location}}

Job Description:
{{job_description}}

Key Responsibilities:
{{responsibilities}}

Required Qualifications:
{{requirements}}

Preferred Qualifications:
{{preferred_qualifications?}}

Salary Range: {{salary_range?}}

How to Apply:
{{application_instructions?}}'),

('contract_template', 'Contract Template', ARRAY['Legal', 'Business']::text[],
'Service Agreement

Between: {{party1_name}}
And: {{party2_name}}
Date: {{contract_date}}

Scope of Services:
{{services_description}}

Terms:
{{contract_terms}}

Payment Terms:
{{payment_terms?}}

Duration: {{contract_duration?}}

Termination Clause:
{{termination_clause?}}

Signatures:
_____________________
{{party1_name}}

_____________________
{{party2_name}}'),

('invoice_template', 'Invoice Template', ARRAY['Finance', 'Business']::text[],
'INVOICE #{{invoice_number}}
Date: {{invoice_date}}

Bill To:
{{client_name}}
{{client_address?}}

Services/Products:
{{items_description}}

Total Amount: {{total_amount}}

Payment Due: {{due_date?}}
Payment Method: {{payment_method?}}

Terms: {{payment_terms?}}

Thank you for your business!'),

('marketing_campaign', 'Marketing Campaign Brief', ARRAY['Marketing', 'Business']::text[],
'Campaign Name: {{campaign_name}}
Target Audience: {{target_audience}}

Campaign Objectives:
{{campaign_objectives}}

Key Messages:
{{key_messages}}

Channels:
{{marketing_channels?}}

Budget: {{budget?}}
Timeline: {{timeline?}}

Success Metrics:
{{success_metrics?}}'),

('product_launch', 'Product Launch Plan', ARRAY['Product', 'Marketing']::text[],
'Product Launch: {{product_name}}
Launch Date: {{launch_date}}

Product Description:
{{product_description}}

Target Market:
{{target_market}}

Launch Activities:
{{launch_activities}}

Pricing Strategy: {{pricing?}}

Marketing Plan:
{{marketing_plan?}}

Success Metrics:
{{metrics?}}'),

('customer_feedback', 'Customer Feedback Form', ARRAY['Support', 'Customer Service']::text[],
'Customer Feedback

Customer Name: {{customer_name}}
Date: {{feedback_date}}
Product/Service: {{product_service}}

Feedback:
{{feedback_details}}

Rating: {{rating}}

Follow-up Required: {{follow_up?}}
Contacted By: {{agent_name?}}

Action Items:
{{action_items?}}'),

('risk_assessment', 'Risk Assessment', ARRAY['Management', 'Planning']::text[],
'Risk Assessment for {{project_name}}

Risk Description:
{{risk_description}}

Probability: {{probability}}
Impact: {{impact}}

Risk Category: {{risk_category?}}

Mitigation Strategy:
{{mitigation_strategy}}

Contingency Plan:
{{contingency_plan?}}

Risk Owner: {{risk_owner?}}'),

('training_plan', 'Training Plan', ARRAY['HR', 'Development']::text[],
'Training Plan: {{training_title}}

Target Audience: {{audience}}
Duration: {{duration}}

Objectives:
{{training_objectives}}

Content Outline:
{{content_outline}}

Materials Needed:
{{materials?}}

Assessment Method:
{{assessment?}}

Follow-up:
{{follow_up_plan?}}'),

('sprint_planning', 'Sprint Planning', ARRAY['Agile', 'Development']::text[],
'Sprint {{sprint_number}} Planning
Duration: {{sprint_duration}}

Sprint Goal:
{{sprint_goal}}

Selected User Stories:
{{selected_stories}}

Team Capacity: {{team_capacity?}}

Dependencies:
{{dependencies?}}

Risks:
{{sprint_risks?}}

Definition of Done:
{{definition_of_done?}}'),

('database_schema', 'Database Schema Documentation', ARRAY['Technical', 'Database']::text[],
'Database: {{database_name}}
Table: {{table_name}}

Purpose:
{{table_purpose}}

Schema:
{{schema_definition}}

Relationships:
{{relationships?}}

Indexes:
{{indexes?}}

Sample Queries:
{{sample_queries?}}

Notes:
{{additional_notes?}}'),

('security_audit', 'Security Audit Report', ARRAY['Security', 'Compliance']::text[],
'Security Audit Report

System: {{system_name}}
Audit Date: {{audit_date}}
Auditor: {{auditor_name}}

Findings Summary:
{{findings_summary}}

Vulnerabilities Found:
{{vulnerabilities}}

Recommendations:
{{recommendations?}}

Priority Actions:
{{priority_actions?}}

Next Audit Date: {{next_audit_date?}}'),

('sop_template', 'Standard Operating Procedure', ARRAY['Operations', 'Documentation']::text[],
'SOP: {{procedure_name}}
Version: {{version}}
Effective Date: {{effective_date}}

Purpose:
{{purpose}}

Procedure Steps:
{{procedure_steps}}

Responsible Parties:
{{responsible_parties?}}

Tools/Equipment:
{{required_tools?}}

Safety Considerations:
{{safety_notes?}}'),

('sales_pitch', 'Sales Pitch', ARRAY['Sales', 'Business']::text[],
'Sales Pitch for {{product_name}}

Target Customer: {{customer_name}}

Pain Points:
{{customer_pain_points}}

Solution:
{{proposed_solution}}

Value Proposition:
{{value_proposition}}

Pricing: {{pricing?}}

Call to Action:
{{call_to_action?}}

Objection Handling:
{{objections?}}'),

('retrospective', 'Sprint Retrospective', ARRAY['Agile', 'Team']::text[],
'Sprint {{sprint_number}} Retrospective
Date: {{retro_date}}
Facilitator: {{facilitator}}

What Went Well:
{{went_well}}

What Could Be Improved:
{{improvements}}

Action Items:
{{action_items?}}

Team Mood: {{team_mood?}}

Next Steps:
{{next_steps?}}'),

('troubleshooting_guide', 'Troubleshooting Guide', ARRAY['Support', 'Documentation']::text[],
'Troubleshooting: {{issue_title}}

Problem Description:
{{problem_description}}

Common Causes:
{{common_causes}}

Solution Steps:
{{solution_steps}}

If Problem Persists:
{{escalation_steps?}}

Related Articles:
{{related_articles?}}

Contact Support:
{{support_contact?}}'),

('architecture_design', 'Architecture Design Document', ARRAY['Technical', 'Architecture']::text[],
'Architecture Design: {{system_name}}

Overview:
{{system_overview}}

Components:
{{system_components}}

Data Flow:
{{data_flow}}

Technology Stack:
{{tech_stack?}}

Security Considerations:
{{security_considerations?}}

Scalability Plan:
{{scalability?}}

Dependencies:
{{dependencies?}}'),

('change_request', 'Change Request', ARRAY['Management', 'Process']::text[],
'Change Request #{{request_number}}

Requested By: {{requester}}
Date: {{request_date}}

Change Description:
{{change_description}}

Business Justification:
{{justification}}

Impact Analysis:
{{impact_analysis?}}

Implementation Plan:
{{implementation_plan?}}

Approval Status: {{approval_status?}}'),

('data_migration', 'Data Migration Plan', ARRAY['Technical', 'Database']::text[],
'Data Migration Plan

Source System: {{source_system}}
Target System: {{target_system}}

Data Scope:
{{data_scope}}

Migration Strategy:
{{migration_strategy}}

Validation Steps:
{{validation_steps?}}

Rollback Plan:
{{rollback_plan?}}

Timeline:
{{timeline?}}'),

('competitive_analysis', 'Competitive Analysis', ARRAY['Business', 'Strategy']::text[],
'Competitive Analysis

Competitor: {{competitor_name}}
Analysis Date: {{analysis_date}}

Strengths:
{{competitor_strengths}}

Weaknesses:
{{competitor_weaknesses}}

Market Position:
{{market_position?}}

Our Advantages:
{{our_advantages?}}

Strategic Recommendations:
{{recommendations?}}'),

('onboarding_checklist', 'Employee Onboarding Checklist', ARRAY['HR', 'Process']::text[],
'Onboarding Checklist

New Employee: {{employee_name}}
Start Date: {{start_date}}
Department: {{department}}

Day 1 Tasks:
{{day1_tasks}}

Week 1 Tasks:
{{week1_tasks}}

Month 1 Goals:
{{month1_goals?}}

Mentor: {{mentor_name?}}

Equipment Needed:
{{equipment_list?}}'),

('content_calendar', 'Content Calendar', ARRAY['Marketing', 'Content']::text[],
'Content Calendar for {{month_year}}

Content Theme: {{content_theme}}

Publishing Schedule:
{{publishing_schedule}}

Content Types:
{{content_types}}

Target Channels:
{{channels?}}

Key Campaigns:
{{campaigns?}}

Performance Metrics:
{{metrics?}}'),

('vendor_evaluation', 'Vendor Evaluation', ARRAY['Procurement', 'Business']::text[],
'Vendor Evaluation

Vendor Name: {{vendor_name}}
Service/Product: {{service_product}}
Evaluation Date: {{eval_date}}

Evaluation Criteria:
{{evaluation_criteria}}

Overall Score: {{overall_score}}

Strengths:
{{vendor_strengths?}}

Concerns:
{{vendor_concerns?}}

Recommendation:
{{recommendation?}}'),

('crisis_response', 'Crisis Response Plan', ARRAY['Management', 'Emergency']::text[],
'Crisis Response Plan

Crisis Type: {{crisis_type}}
Severity Level: {{severity}}

Immediate Actions:
{{immediate_actions}}

Communication Plan:
{{communication_plan}}

Responsible Team:
{{response_team?}}

Stakeholder Contacts:
{{stakeholder_contacts?}}

Recovery Steps:
{{recovery_steps?}}'),

('product_roadmap', 'Product Roadmap', ARRAY['Product', 'Planning']::text[],
'Product Roadmap: {{product_name}}
Timeline: {{timeline}}

Vision:
{{product_vision}}

Key Milestones:
{{milestones}}

Feature Priorities:
{{feature_list}}

Dependencies:
{{dependencies?}}

Success Metrics:
{{success_metrics?}}

Risks:
{{risks?}}'),

('compliance_checklist', 'Compliance Checklist', ARRAY['Compliance', 'Legal']::text[],
'Compliance Checklist

Regulation: {{regulation_name}}
Review Date: {{review_date}}

Compliance Requirements:
{{requirements}}

Current Status:
{{compliance_status}}

Action Items:
{{action_items?}}

Documentation:
{{required_docs?}}

Next Review: {{next_review_date?}}'),

('knowledge_article', 'Knowledge Base Article', ARRAY['Documentation', 'Support']::text[],
'Knowledge Article: {{article_title}}

Category: {{category}}
Tags: {{tags}}

Problem/Question:
{{problem_statement}}

Solution/Answer:
{{solution}}

Related Articles:
{{related_articles?}}

Last Updated: {{update_date?}}

Was this helpful? {{feedback_option?}}'),

('release_notes', 'Release Notes', ARRAY['Product', 'Documentation']::text[],
'Release Notes - Version {{version}}
Release Date: {{release_date}}

What''s New:
{{new_features}}

Improvements:
{{improvements}}

Bug Fixes:
{{bug_fixes?}}

Known Issues:
{{known_issues?}}

Upgrade Instructions:
{{upgrade_instructions?}}

Contact Support:
{{support_info?}}'),

('survey_template', 'Survey Template', ARRAY['Research', 'Feedback']::text[],
'Survey: {{survey_title}}
Purpose: {{survey_purpose}}

Target Respondents: {{target_audience}}

Questions:
{{survey_questions}}

Response Deadline: {{deadline?}}

Incentive: {{incentive?}}

Privacy Notice:
{{privacy_notice?}}

Thank you for your participation!');