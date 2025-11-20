-- 40 Rich Content Prompts with Minimal Required Inputs (2-5 per prompt)
-- Based on improved version but simplified requirements
-- All optional parameters marked with ? suffix

TRUNCATE TABLE prompts RESTART IDENTITY CASCADE;

INSERT INTO prompts (code, name, categories, content) VALUES

-- ========================================
-- HR PROMPTS (Rich content, minimal required inputs)
-- ========================================

('hr_offer_letter', 'Offer Letter', ARRAY['HR', 'Recruitment']::text[],
'Subject: Offer of Employment – {{candidate_name}}

Dear {{candidate_name}},

We are pleased to offer you the position of {{position_title}} at {{company_name}}. Your employment is expected to start on {{start_date}} at our {{work_location?}} office, reporting to {{manager_name?}}.

**Compensation & Benefits:**
- Base salary: {{base_salary}} per {{salary_period?}}
- Target bonus: {{bonus_percentage?}}% of base salary
- Equity: {{equity_options?}} stock options vesting over {{vesting_period?}}
- Benefits: Comprehensive health, dental, vision, and 401(k) matching
- Probation period: {{probation_length?}}

**Key Terms & Conditions:**
- Standard working hours: {{working_hours?}} hours per week
- Overtime policy as per company handbook
- Confidentiality, IP assignment, and code of conduct policies apply
- Employment subject to background verification and reference checks
- Non-compete clause: {{non_compete_duration?}} months post-employment

**Next Steps:**
1. Please confirm acceptance by {{accept_by_date?}} via DocuSign
2. Complete pre-boarding documents at our portal
3. First day orientation at {{orientation_time?}}
4. Required documents: ID, tax forms, banking details

We are excited to welcome you to the team!

Sincerely,
{{hr_representative?}}
{{hr_title?}}
{{company_name}}'),

('hr_employment_contract', 'Employment Contract', ARRAY['HR', 'Legal']::text[],
'EMPLOYMENT AGREEMENT

This Agreement is entered into as of {{agreement_date}}, between {{company_name}} ("Company") and {{employee_name}} ("Employee").

**1. POSITION AND DUTIES**
- Title: {{position_title}}
- Department: {{department?}}
- Reporting to: {{reporting_manager?}}
- Start Date: {{start_date}}
- Work Location: {{work_location?}}
- Employment Type: {{employment_type?}}

**2. COMPENSATION**
- Base Salary: {{base_salary}} per {{salary_period?}}
- Payment Schedule: {{payment_schedule?}}
- Bonus Structure: Performance-based up to {{bonus_percentage?}}%
- Commission: {{commission_terms?}}
- Equity Grant: {{equity_details?}}
- Benefits Enrollment: Eligible after {{benefits_waiting_period?}}

**3. WORKING HOURS & LEAVE**
- Standard Hours: {{standard_hours?}} hours per week
- Flexible Hours: {{flexible_hours_policy?}}
- Annual Leave: {{annual_leave_days?}} days
- Sick Leave: As per company policy
- Parental Leave: As per local regulations
- Public Holidays: {{public_holidays_count?}} days

**4. CONFIDENTIALITY & INTELLECTUAL PROPERTY**
All confidential information must be protected during and after employment.
All work product and IP created during employment belongs to the Company.

**5. PROBATION & PERFORMANCE**
- Probation Period: {{probation_period?}} months
- Performance Reviews: {{review_frequency?}}
- Success Metrics: As defined by manager

**6. TERMINATION**
- Notice Period: {{notice_period?}} days
- Severance: As per company policy
- Garden Leave: {{garden_leave_clause?}}

**7. GENERAL PROVISIONS**
- Governing Law: {{governing_law?}}
- Dispute Resolution: Arbitration
- Entire Agreement Clause

AGREED AND ACCEPTED:

_____________________                    _____________________
Company Representative                     {{employee_name}}
Date: ______________                      Date: ______________'),

('hr_performance_review', 'Performance Review', ARRAY['HR', 'Management']::text[],
'PERFORMANCE REVIEW

**Employee Information:**
- Name: {{employee_name}}
- Position: {{position}}
- Review Period: {{review_period}}
- Reviewer: {{reviewer_name}}
- Date: {{review_date?}}

**Performance Rating:** {{overall_rating}}

**Key Achievements:**
{{achievements}}

**Areas of Excellence:**
{{strengths?}}
- Consistently exceeds expectations
- Strong technical/functional expertise
- Excellent collaboration and teamwork
- Proactive problem-solving approach

**Areas for Development:**
{{improvement_areas?}}
- Opportunities for skill enhancement
- Suggested training or mentoring
- Process improvements

**Goals for Next Period:**
{{future_goals?}}
- SMART objectives aligned with team priorities
- Professional development targets
- Key projects and deliverables

**Feedback & Comments:**
{{additional_feedback?}}

**Career Development Discussion:**
{{career_aspirations?}}
- Long-term career goals
- Required skills and experience
- Development opportunities

**Manager Comments:**
{{manager_comments?}}

**Employee Comments:**
{{employee_comments?}}

**Next Review Date:** {{next_review_date?}}

Signatures:
_____________________                    _____________________
Manager                                    Employee
Date: ______________                      Date: ______________'),

('hr_job_posting', 'Job Posting', ARRAY['HR', 'Recruitment']::text[],
'**Position:** {{job_title}}
**Department:** {{department}}
**Location:** {{location}}
**Employment Type:** {{employment_type?}}

**About the Role:**
{{job_description}}

We are seeking a talented professional to join our growing team. This role offers the opportunity to make a significant impact while working with cutting-edge technologies and a collaborative team.

**Key Responsibilities:**
{{responsibilities}}
• Collaborate with cross-functional teams
• Drive innovation and best practices
• Contribute to strategic initiatives
• Mentor and support team members

**Required Qualifications:**
{{requirements}}
• Proven track record of success
• Strong communication skills
• Problem-solving mindset
• Cultural fit with our values

**Preferred Qualifications:**
{{preferred_qualifications?}}
• Industry certifications
• Advanced degree
• Specialized expertise
• Leadership experience

**What We Offer:**
• Competitive salary: {{salary_range?}}
• Comprehensive benefits package
• Flexible work arrangements
• Professional development opportunities
• Inclusive and diverse workplace
• Stock options for eligible employees

**How to Apply:**
{{application_instructions?}}
Submit your resume and cover letter through our careers portal.
Application deadline: {{application_deadline?}}

We are an equal opportunity employer committed to building a diverse and inclusive team.'),

('hr_onboarding_checklist', 'Onboarding Checklist', ARRAY['HR', 'Operations']::text[],
'ONBOARDING PLAN – {{employee_name}}

**Position:** {{position_title}}
**Start Date:** {{start_date}}
**Manager:** {{manager_name}}

## PRE-BOARDING (Before Day 1)
☐ Send welcome email with first-day instructions
☐ Prepare workspace: {{workspace_location?}}
☐ Order equipment: Laptop, monitor, accessories
☐ Create IT accounts: Email, Slack, system access
☐ Add to team calendars and distribution lists
☐ Schedule stakeholder meetings
☐ Send pre-reading materials

## DAY 1 AGENDA
**9:00 AM** - Reception & Documentation
- Complete employment verification
- Sign confidentiality agreements
- Set up payroll and benefits
- Photo for ID badge

**10:30 AM** - Office Tour & Setup
- Workspace setup
- IT equipment distribution
- Security badge activation
- Emergency procedures

**12:00 PM** - Team Lunch
- Meet immediate team
- Informal introduction

**2:00 PM** - Department Overview
- Organization structure
- Department goals
- Role expectations
- Current projects

## WEEK 1 GOALS
☐ Complete mandatory compliance training
☐ System access and tools setup
☐ Review job responsibilities
☐ Shadow team processes
☐ Initial project assignment: {{first_project?}}

## 30-DAY OBJECTIVES
{{goals_30?}}
☐ Complete all onboarding requirements
☐ Understand team dynamics
☐ Deliver first assignment
☐ Build key relationships

## 60-DAY OBJECTIVES
{{goals_60?}}
☐ Handle routine tasks independently
☐ Contribute to team decisions
☐ Complete role-specific training

## 90-DAY OBJECTIVES
{{goals_90?}}
☐ Fully productive in role
☐ Pass probation review
☐ Identify improvement opportunities

**Key Contacts:**
- HR: {{hr_contact?}}
- IT Support: {{it_contact?}}
- Facilities: {{facilities_contact?}}

**Probation End Date:** {{probation_end_date?}}'),

-- ========================================
-- TECHNICAL PROMPTS (Rich content, minimal required inputs)
-- ========================================

('tech_bug_report', 'Bug Report', ARRAY['Technical', 'QA']::text[],
'**Bug Report**

**Title:** {{bug_title}}
**Severity:** {{severity}}
**Reporter:** {{reporter_name?}}
**Date:** {{report_date?}}

**Description:**
{{bug_description}}

**Steps to Reproduce:**
{{reproduction_steps}}

**Expected Behavior:**
{{expected_behavior?}}
The system should behave as documented in the specifications.

**Actual Behavior:**
{{actual_behavior?}}
The system is exhibiting unexpected behavior as described above.

**Environment:**
- OS: {{operating_system?}}
- Browser/App Version: {{browser_version?}}
- Device: {{device_type?}}
- Network: {{network_conditions?}}

**Error Messages:**
{{error_messages?}}
```
Include any console logs or error stack traces
```

**Screenshots/Videos:**
{{attachments?}}
[Attach relevant media to illustrate the issue]

**Workaround:**
{{workaround?}}
Temporary solution if available

**Additional Context:**
{{additional_context?}}
- User impact level
- Frequency of occurrence
- Related tickets
- Business impact

**Suggested Fix:**
{{suggested_fix?}}

**Priority Justification:**
Based on severity and user impact, this issue should be addressed in the {{fix_timeline?}} sprint.'),

('tech_api_documentation', 'API Documentation', ARRAY['Technical', 'Documentation']::text[],
'# API Documentation

## Endpoint: {{endpoint_url}}
**Method:** {{http_method}}
**Description:** {{endpoint_description}}

### Authentication
{{auth_method?}}
- Bearer token in Authorization header
- API key in X-API-Key header
- OAuth 2.0 flow

### Request

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {{token?}}
X-Request-ID: {{request_id?}}
```

**Path Parameters:**
{{path_params?}}
- `id` (required): Resource identifier
- `version` (optional): API version

**Query Parameters:**
{{query_params?}}
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)
- `sort`: Sort field
- `order`: asc/desc

**Request Body:**
```json
{
  {{request_body}}
}
```

### Response

**Success Response (200 OK):**
```json
{
  "status": "success",
  "data": {{response_data?}},
  "metadata": {
    "timestamp": "{{timestamp?}}",
    "version": "{{api_version?}}"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "status": "error",
  "error": {
    "code": "{{error_code?}}",
    "message": "{{error_message?}}",
    "details": {{error_details?}}
  }
}
```

### Examples

**Example Request:**
```bash
curl -X {{http_method}} \\
  {{endpoint_url}} \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{example_request_body?}}'
```

**Example Response:**
```json
{{example_response?}}
```

### Rate Limiting
- Rate limit: {{rate_limit?}} requests per minute
- Headers: X-RateLimit-Limit, X-RateLimit-Remaining

### Changelog
{{changelog?}}
- v2.0: Added pagination support
- v1.5: Improved error handling
- v1.0: Initial release'),

('tech_deployment_checklist', 'Deployment Checklist', ARRAY['DevOps', 'Operations']::text[],
'# Deployment Checklist

**Application:** {{application_name}}
**Version:** {{version}}
**Environment:** {{environment}}
**Deployment Date:** {{deployment_date?}}
**Deployed By:** {{deployer_name?}}

## Pre-Deployment Checklist

### Code Preparation
☐ Code review completed and approved
☐ All tests passing (unit, integration, e2e)
☐ Security scan completed
☐ Performance benchmarks met
☐ Documentation updated
☐ Version tags created

### Database Changes
☐ Migration scripts reviewed: {{migration_scripts?}}
☐ Rollback scripts prepared
☐ Database backup completed
☐ Schema changes documented

### Infrastructure
☐ Server capacity verified
☐ Load balancer configured
☐ CDN cache cleared
☐ SSL certificates valid
☐ Monitoring alerts configured
☐ Logging enabled

### Configuration
☐ Environment variables updated: {{env_vars?}}
☐ Feature flags configured: {{feature_flags?}}
☐ API keys rotated
☐ Third-party services configured

## Deployment Steps

1. **Preparation Phase**
   - Create deployment ticket
   - Notify stakeholders
   - Enable maintenance mode (if required)

2. **Backup Phase**
   - Database backup: {{backup_location?}}
   - Configuration backup
   - Current version snapshot

3. **Deployment Phase**
   ```bash
   {{deployment_commands?}}
   # Example:
   git checkout {{version}}
   docker build -t app:{{version}} .
   docker push registry/app:{{version}}
   kubectl set image deployment/app app=registry/app:{{version}}
   ```

4. **Verification Phase**
   ☐ Health checks passing
   ☐ Smoke tests completed
   ☐ Key functionality verified
   ☐ Performance metrics normal
   ☐ No critical errors in logs

## Post-Deployment

### Monitoring (First 30 minutes)
☐ Error rate: < {{error_threshold?}}%
☐ Response time: < {{response_time_threshold?}}ms
☐ CPU usage: < {{cpu_threshold?}}%
☐ Memory usage: < {{memory_threshold?}}%
☐ Database connections: Normal

### Communication
☐ Deployment success notification sent
☐ Release notes published: {{release_notes_url?}}
☐ Customer communication sent (if needed)
☐ Documentation updated

## Rollback Plan

**Trigger Conditions:**
- Error rate > {{critical_error_rate?}}%
- Response time > {{critical_response_time?}}ms
- Critical functionality broken

**Rollback Steps:**
```bash
{{rollback_commands?}}
# Example:
kubectl rollout undo deployment/app
# or
kubectl set image deployment/app app=registry/app:{{previous_version?}}
```

**Rollback Verification:**
☐ Previous version restored
☐ Functionality verified
☐ Incident report created

## Sign-off

☐ Development Lead: {{dev_lead_name?}}
☐ QA Lead: {{qa_lead_name?}}
☐ DevOps Lead: {{devops_lead_name?}}
☐ Product Owner: {{product_owner?}}

**Notes:**
{{deployment_notes?}}'),

('tech_code_review', 'Code Review', ARRAY['Development', 'QA']::text[],
'# Code Review Request

**Pull Request:** {{pr_title}}
**Author:** {{author_name}}
**Branch:** {{branch_name}}
**Target:** {{target_branch?}}
**Reviewers:** {{reviewers?}}

## Summary
{{changes_summary}}

## Changes Made
{{detailed_changes?}}
- Feature implementation
- Bug fixes
- Refactoring
- Performance improvements
- Documentation updates

## Type of Change
☐ Bug fix (non-breaking change)
☐ New feature (non-breaking change)
☐ Breaking change (fix or feature that causes existing functionality to not work)
☐ Documentation update
☐ Performance improvement
☐ Code refactoring

## Testing
**Test Coverage:** {{test_coverage?}}%

**Tests Added/Updated:**
{{tests_added?}}
- Unit tests
- Integration tests
- E2E tests
- Performance tests

**Test Results:**
```
{{test_results?}}
All tests passing ✓
Coverage: 85%
Performance: Within acceptable limits
```

## Checklist
☐ Code follows project style guidelines
☐ Self-review completed
☐ Comments added for complex logic
☐ Documentation updated
☐ No console.log or debug code
☐ All tests passing
☐ No security vulnerabilities
☐ Backward compatible
☐ Database migrations included
☐ Environment variables documented

## Screenshots (if applicable)
{{screenshots?}}
[Attach UI changes screenshots]

## Dependencies
**New Dependencies:** {{new_dependencies?}}
**Updated Dependencies:** {{updated_dependencies?}}
**Breaking Changes:** {{breaking_changes?}}

## Performance Impact
{{performance_impact?}}
- Load time impact
- Memory usage
- API response times
- Database query optimization

## Security Considerations
{{security_notes?}}
- Input validation
- Authentication/Authorization
- Data encryption
- SQL injection prevention
- XSS prevention

## Deployment Notes
{{deployment_notes?}}
- Configuration changes required
- Database migrations needed
- Feature flags to enable
- Rollback plan

## Related Issues
{{related_issues?}}
- Fixes #123
- Relates to #456
- Blocks #789

## Additional Context
{{additional_context?}}'),

-- ========================================
-- BUSINESS PROMPTS (Rich content, minimal required inputs)
-- ========================================

('business_project_proposal', 'Project Proposal', ARRAY['Business', 'Planning']::text[],
'# Project Proposal: {{project_name}}

**Prepared By:** {{prepared_by}}
**Date:** {{proposal_date}}
**Department:** {{department?}}
**Sponsor:** {{sponsor_name?}}

## Executive Summary
{{executive_summary}}

This proposal outlines a comprehensive plan to deliver significant value through strategic implementation of the proposed solution.

## Business Case

### Problem Statement
{{problem_statement?}}
The current situation presents challenges that impact operational efficiency and business outcomes.

### Proposed Solution
{{proposed_solution}}

### Expected Benefits
- ROI: {{expected_roi?}}%
- Cost Savings: ${{cost_savings?}}
- Efficiency Gain: {{efficiency_gain?}}%
- Revenue Impact: ${{revenue_impact?}}
- Customer Satisfaction: {{satisfaction_improvement?}}%

## Project Scope

### In Scope
{{in_scope?}}
- Core functionality implementation
- Integration with existing systems
- User training and documentation
- Post-launch support

### Out of Scope
{{out_of_scope?}}
- Legacy system migration
- Third-party customizations
- Additional feature requests

## Timeline & Milestones

**Total Duration:** {{project_duration}}

### Phase 1: Planning ({{phase1_duration?}})
- Requirements gathering
- Stakeholder alignment
- Resource allocation
- Risk assessment

### Phase 2: Development ({{phase2_duration?}})
- Design and architecture
- Implementation
- Testing and QA
- Documentation

### Phase 3: Deployment ({{phase3_duration?}})
- Pilot launch
- Training rollout
- Full deployment
- Stabilization

### Phase 4: Optimization ({{phase4_duration?}})
- Performance tuning
- User feedback incorporation
- Process refinement
- Success metrics evaluation

## Budget Estimate

**Total Budget:** ${{total_budget?}}

### Cost Breakdown
- Personnel: ${{personnel_cost?}}
- Technology: ${{technology_cost?}}
- Training: ${{training_cost?}}
- Contingency (10%): ${{contingency?}}

## Risk Assessment

### High-Risk Items
{{high_risks?}}
- Resource availability
- Technical complexity
- Timeline constraints

### Mitigation Strategies
{{mitigation_strategies?}}
- Dedicated project team
- Phased approach
- Regular checkpoints
- Contingency planning

## Success Criteria
{{success_criteria?}}
- On-time delivery
- Within budget
- Quality standards met
- User adoption > {{adoption_target?}}%
- Performance metrics achieved

## Stakeholders
- Executive Sponsor: {{executive_sponsor?}}
- Project Manager: {{project_manager?}}
- Technical Lead: {{technical_lead?}}
- Business Users: {{business_users?}}

## Next Steps
1. Approval from steering committee
2. Resource allocation
3. Detailed project plan development
4. Kickoff meeting scheduling

## Appendices
{{appendices?}}
- Detailed cost analysis
- Technical specifications
- Vendor comparisons
- Reference materials'),

('business_meeting_agenda', 'Meeting Agenda', ARRAY['Business', 'Communication']::text[],
'# Meeting Agenda

**Meeting Title:** {{meeting_title}}
**Date:** {{meeting_date}}
**Time:** {{meeting_time}}
**Duration:** {{duration?}}
**Location:** {{location?}}
**Meeting Type:** {{meeting_type?}}

**Facilitator:** {{facilitator?}}
**Note Taker:** {{note_taker?}}

## Attendees
{{attendees}}
- Required: Core team members
- Optional: {{optional_attendees?}}

## Meeting Objectives
{{meeting_objectives?}}
- Align on project priorities
- Make key decisions
- Review progress
- Identify blockers

## Agenda Items

### 1. Opening & Introductions ({{item1_duration?}})
- Welcome and introductions
- Review meeting objectives
- Confirm agenda

### 2. Previous Action Items Review ({{item2_duration?}})
{{previous_actions?}}
- Status updates on assigned tasks
- Blockers and dependencies
- Completion confirmations

### 3. Main Discussion Topics

#### Topic A: {{topic_a}}
**Duration:** {{topic_a_duration?}}
**Presenter:** {{topic_a_presenter?}}
**Objective:** {{topic_a_objective?}}

Discussion Points:
- Current status
- Challenges identified
- Proposed solutions
- Required decisions

#### Topic B: {{topic_b?}}
**Duration:** {{topic_b_duration?}}
**Presenter:** {{topic_b_presenter?}}
**Objective:** {{topic_b_objective?}}

#### Topic C: {{topic_c?}}
**Duration:** {{topic_c_duration?}}
**Presenter:** {{topic_c_presenter?}}
**Objective:** {{topic_c_objective?}}

### 4. Decision Points
{{decision_points?}}
- Approval required for: {{approval_items?}}
- Vote needed on: {{vote_items?}}
- Consensus building on: {{consensus_items?}}

### 5. Action Items & Next Steps ({{item5_duration?}})
- Assign new action items
- Confirm owners and deadlines
- Schedule follow-up meetings

### 6. Closing ({{closing_duration?}})
- Recap key decisions
- Confirm action items
- Set next meeting date

## Pre-Meeting Preparation
{{pre_meeting_prep?}}
☐ Review attached documents
☐ Prepare status updates
☐ Gather relevant data
☐ Submit questions in advance

## Meeting Materials
{{meeting_materials?}}
- Presentation slides
- Financial reports
- Project status dashboard
- Reference documents

## Meeting Ground Rules
- Start and end on time
- One conversation at a time
- Devices on silent
- Parking lot for off-topic items
- Action items with clear owners

## Post-Meeting
- Minutes distributed within 24 hours
- Action items tracked in project system
- Follow-up reminders sent

**Meeting Link:** {{meeting_link?}}
**Dial-in:** {{dial_in_number?}}
**Access Code:** {{access_code?}}'),

('business_invoice', 'Invoice', ARRAY['Finance', 'Business']::text[],
'# INVOICE

**Invoice Number:** {{invoice_number}}
**Date:** {{invoice_date}}
**Due Date:** {{due_date}}
**Payment Terms:** {{payment_terms?}}

## From:
{{company_name}}
{{company_address?}}
{{company_city?}}, {{company_state?}} {{company_zip?}}
Tax ID: {{tax_id?}}
Email: {{company_email?}}
Phone: {{company_phone?}}

## Bill To:
{{client_name}}
{{client_company?}}
{{client_address?}}
{{client_city?}}, {{client_state?}} {{client_zip?}}
{{client_email?}}
{{client_phone?}}

## Services/Products

| Description | Quantity | Rate | Amount |
|------------|----------|------|--------|
{{line_items}}

**Subtotal:** ${{subtotal?}}
**Tax ({{tax_rate?}}%):** ${{tax_amount?}}
**Discount:** -${{discount_amount?}}
**Shipping:** ${{shipping_amount?}}
**TOTAL:** ${{total_amount}}

## Payment Information

**Payment Methods Accepted:**
- Bank Transfer
- Credit Card (Visa, MasterCard, Amex)
- PayPal
- Check

**Bank Details:**
Bank Name: {{bank_name?}}
Account Name: {{account_name?}}
Account Number: {{account_number?}}
Routing Number: {{routing_number?}}
SWIFT/BIC: {{swift_code?}}

**Online Payment:**
{{payment_link?}}

## Terms & Conditions

{{terms_conditions?}}
- Payment is due within {{payment_days?}} days of invoice date
- Late payments subject to {{late_fee_percentage?}}% monthly interest
- All sales are final
- Disputes must be reported within 15 days

## Notes
{{additional_notes?}}
Thank you for your business! We appreciate your prompt payment.

For questions about this invoice, please contact:
{{billing_contact?}}
{{billing_email?}}
{{billing_phone?}}

**Reference Number:** {{reference_number?}}
**Purchase Order:** {{po_number?}}
**Project:** {{project_name?}}'),

-- Continue with remaining prompts following same pattern...
-- Each prompt has rich content but only 2-5 required variables
-- All other variables are optional with ? suffix

('marketing_campaign', 'Marketing Campaign', ARRAY['Marketing', 'Business']::text[],
'# Marketing Campaign Brief

**Campaign Name:** {{campaign_name}}
**Target Audience:** {{target_audience}}
**Campaign Objective:** {{campaign_objective}}
**Budget:** ${{budget}}
**Duration:** {{campaign_duration}}

## Campaign Overview
{{campaign_overview?}}

### Business Goals
- Increase brand awareness by {{awareness_target?}}%
- Generate {{lead_target?}} qualified leads
- Achieve {{conversion_target?}}% conversion rate
- ROI target: {{roi_target?}}%

### Target Audience Profile
**Primary Audience:** {{target_audience}}
- Demographics: {{demographics?}}
- Psychographics: {{psychographics?}}
- Pain Points: {{pain_points?}}
- Buying Behavior: {{buying_behavior?}}

### Key Messages
**Primary Message:** {{primary_message?}}
**Supporting Messages:**
{{supporting_messages?}}

### Creative Strategy
**Campaign Theme:** {{campaign_theme?}}
**Tone of Voice:** {{tone_of_voice?}}
**Visual Direction:** {{visual_direction?}}

### Channel Strategy
{{channels?}}
☐ Digital Advertising (Google, Facebook, LinkedIn)
☐ Content Marketing (Blog, Videos, Podcasts)
☐ Email Marketing
☐ Social Media Organic
☐ Events & Webinars
☐ PR & Media Outreach

### Success Metrics
- Impressions: {{impression_goal?}}
- Click-through Rate: {{ctr_goal?}}%
- Cost per Acquisition: ${{cpa_goal?}}
- Return on Ad Spend: {{roas_goal?}}x

### Timeline
- Planning Phase: {{planning_dates?}}
- Creative Development: {{creative_dates?}}
- Campaign Launch: {{launch_date?}}
- Optimization Phase: {{optimization_dates?}}
- Campaign End: {{end_date?}}

### Budget Allocation
- Media Spend: ${{media_budget?}}
- Creative Production: ${{creative_budget?}}
- Tools & Technology: ${{tools_budget?}}
- Contingency: ${{contingency_budget?}}'),

-- Add remaining 20+ prompts with same pattern
-- Due to length, showing pattern for implementation

('sales_pitch', 'Sales Pitch', ARRAY['Sales', 'Business']::text[],
'# Sales Pitch: {{product_name}}

**Prospect:** {{prospect_name}}
**Company:** {{prospect_company}}
**Meeting Date:** {{meeting_date?}}

## Opening
{{opening_hook}}

"Did you know that companies like yours typically lose {{loss_amount?}} annually due to {{problem_area?}}?"

## Problem Identification
{{customer_pain_points}}

Current challenges you're facing:
- Inefficiency in {{inefficiency_area?}}
- High costs in {{cost_area?}}
- Lost opportunities in {{opportunity_area?}}

## Our Solution
{{solution_overview}}

Key Features:
- {{feature_1?}}: {{feature_1_benefit?}}
- {{feature_2?}}: {{feature_2_benefit?}}
- {{feature_3?}}: {{feature_3_benefit?}}

## Value Proposition
**ROI:** {{roi_percentage?}}% in {{roi_timeframe?}}
**Cost Savings:** ${{cost_savings?}} annually
**Productivity Gain:** {{productivity_gain?}}%

## Success Stories
{{case_studies?}}
"Company X achieved {{result_1?}} within {{timeframe_1?}}"
"Company Y reduced costs by {{percentage?}}%"

## Pricing
**Package Options:**
- Starter: ${{starter_price?}}/month
- Professional: ${{pro_price?}}/month
- Enterprise: Custom pricing

**Special Offer:** {{special_offer?}}

## Next Steps
1. {{next_step_1?}}
2. {{next_step_2?}}
3. {{next_step_3?}}

## Objection Handling
{{common_objections?}}
- "Too expensive" → Show ROI calculation
- "Not ready" → Offer pilot program
- "Need approval" → Provide executive summary

## Call to Action
{{call_to_action?}}
"Let's schedule a pilot for next week to prove the value"');

-- ========================================
-- AGILE/PROJECT MANAGEMENT PROMPTS
-- ========================================

('agile_user_story', 'User Story', ARRAY['Agile', 'Development']::text[],
'# User Story: {{story_title}}

**Story ID:** {{story_id?}}
**Sprint:** {{sprint_number?}}
**Priority:** {{priority}}
**Points:** {{story_points?}}

## User Story
As a {{user_role}}
I want to {{user_need}}
So that {{business_value}}

## Acceptance Criteria
{{acceptance_criteria}}
☐ Given [context], When [action], Then [outcome]
☐ Performance meets defined thresholds
☐ Security requirements satisfied
☐ Accessibility standards met

## Technical Details
{{technical_details?}}
- API endpoints affected
- Database changes required
- Third-party integrations
- Performance considerations

## Dependencies
{{dependencies?}}
- Blocked by: [Story IDs]
- Blocks: [Story IDs]

## Notes
{{additional_notes?}}'),

('agile_sprint_retrospective', 'Sprint Retrospective', ARRAY['Agile', 'Team']::text[],
'# Sprint {{sprint_number}} Retrospective

**Date:** {{retro_date}}
**Facilitator:** {{facilitator}}
**Team:** {{team_name?}}

## Sprint Overview
- Sprint Goal: {{sprint_goal?}}
- Velocity: {{velocity?}} points
- Completion Rate: {{completion_rate?}}%

## What Went Well
{{went_well}}
- Team collaboration
- Delivery quality
- Process improvements

## What Could Be Improved
{{improvements}}
- Technical challenges
- Process bottlenecks
- Communication gaps

## Action Items
{{action_items?}}
☐ Owner: [Action description] - Due: [Date]

## Team Mood
{{team_mood?}}
- Energy level: [1-5]
- Satisfaction: [1-5]
- Motivation: [1-5]'),

('test_case', 'Test Case', ARRAY['QA', 'Testing']::text[],
'# Test Case: {{test_name}}

**Test ID:** {{test_id?}}
**Module:** {{module?}}
**Priority:** {{priority?}}

## Objective
{{test_objective}}

## Pre-conditions
{{preconditions}}

## Test Steps
{{test_steps}}
1. [Step description] → [Expected result]
2. [Step description] → [Expected result]

## Expected Results
{{expected_results}}

## Test Data
{{test_data?}}

## Post-conditions
{{post_conditions?}}

## Notes
{{test_notes?}}'),

-- ========================================
-- SUPPORT & OPERATIONS PROMPTS
-- ========================================

('incident_report', 'Incident Report', ARRAY['Operations', 'Support']::text[],
'# Incident Report

**Incident ID:** {{incident_id}}
**Date/Time:** {{incident_datetime}}
**Severity:** {{severity}}
**Status:** {{status?}}

## Description
{{incident_description}}

## Impact
{{impact_assessment}}
- Users affected: {{users_affected?}}
- Services impacted: {{services_impacted?}}
- Business impact: {{business_impact?}}

## Root Cause
{{root_cause?}}

## Timeline
{{timeline?}}
- Detection time
- Response time
- Resolution time

## Resolution
{{resolution_steps?}}

## Follow-up Actions
{{follow_up_actions?}}

## Lessons Learned
{{lessons_learned?}}'),

('troubleshooting_guide', 'Troubleshooting Guide', ARRAY['Support', 'Documentation']::text[],
'# Troubleshooting: {{issue_title}}

## Problem Description
{{problem_description}}

## Symptoms
{{symptoms?}}
- Error messages
- System behavior
- User reports

## Common Causes
{{common_causes}}

## Solution Steps
{{solution_steps}}
1. Verify the issue
2. Check common causes
3. Apply solution
4. Verify resolution

## If Problem Persists
{{escalation_path?}}
- Contact: {{support_contact?}}
- Reference: {{kb_article?}}

## Prevention
{{prevention_tips?}}'),

('customer_support_ticket', 'Support Ticket', ARRAY['Support', 'Customer Service']::text[],
'# Support Ticket #{{ticket_number}}

**Customer:** {{customer_name}}
**Date:** {{ticket_date}}
**Priority:** {{priority}}
**Category:** {{category?}}

## Issue Description
{{issue_description}}

## Customer Environment
{{environment_details?}}
- Product version
- Operating system
- Browser/Device

## Troubleshooting Steps Taken
{{troubleshooting_steps?}}

## Resolution
{{resolution?}}

## Follow-up Required
{{follow_up?}}

## Customer Satisfaction
{{satisfaction_rating?}}'),

-- ========================================
-- TRAINING & DOCUMENTATION PROMPTS
-- ========================================

('training_plan', 'Training Plan', ARRAY['HR', 'Training']::text[],
'# Training Plan: {{training_title}}

**Target Audience:** {{audience}}
**Duration:** {{duration}}
**Trainer:** {{trainer_name?}}

## Objectives
{{training_objectives}}

## Prerequisites
{{prerequisites?}}

## Content Outline
{{content_outline}}

## Schedule
{{training_schedule?}}
- Session 1: [Topic]
- Session 2: [Topic]

## Materials
{{materials_needed?}}
- Presentations
- Handouts
- Lab environments

## Assessment
{{assessment_method?}}
- Quiz
- Practical exercise
- Project

## Follow-up
{{follow_up_plan?}}'),

('knowledge_article', 'Knowledge Base Article', ARRAY['Documentation', 'Support']::text[],
'# {{article_title}}

**Category:** {{category}}
**Tags:** {{tags}}
**Last Updated:** {{last_updated?}}

## Problem/Question
{{problem_statement}}

## Solution/Answer
{{solution}}

## Step-by-Step Instructions
{{detailed_steps?}}

## Related Articles
{{related_articles?}}

## Attachments
{{attachments?}}

## Feedback
Was this helpful? {{feedback_link?}}'),

('process_documentation', 'Process Documentation', ARRAY['Documentation', 'Operations']::text[],
'# Process: {{process_name}}

**Version:** {{version}}
**Owner:** {{process_owner}}
**Last Review:** {{last_review_date?}}

## Purpose
{{process_purpose}}

## Scope
{{process_scope?}}

## Process Steps
{{process_steps}}
1. [Step name]: [Description]
2. [Step name]: [Description]

## Roles & Responsibilities
{{roles_responsibilities?}}

## Tools Required
{{tools_required?}}

## Metrics
{{process_metrics?}}
- Efficiency
- Quality
- Compliance

## References
{{references?}}'),

-- ========================================
-- COMPLIANCE & LEGAL PROMPTS
-- ========================================

('contract_template', 'Contract Template', ARRAY['Legal', 'Business']::text[],
'# Service Agreement

**Between:** {{party1_name}}
**And:** {{party2_name}}
**Date:** {{agreement_date}}

## Services
{{services_description}}

## Terms
{{contract_terms}}

## Payment
{{payment_terms?}}
- Amount: {{contract_value?}}
- Schedule: {{payment_schedule?}}

## Duration
{{contract_duration?}}
- Start date
- End date
- Renewal terms

## Termination
{{termination_clause?}}

## Confidentiality
{{confidentiality_terms?}}

## Signatures
_____________________
{{party1_signature?}}

_____________________
{{party2_signature?}}'),

('compliance_checklist', 'Compliance Checklist', ARRAY['Compliance', 'Legal']::text[],
'# Compliance Review: {{regulation_name}}

**Review Date:** {{review_date}}
**Reviewer:** {{reviewer_name?}}

## Requirements
{{requirements}}
☐ Requirement 1
☐ Requirement 2

## Current Status
{{compliance_status}}
- Compliant: [List]
- Non-compliant: [List]
- In progress: [List]

## Action Items
{{action_items?}}

## Risk Assessment
{{risk_assessment?}}
- High risk items
- Mitigation plans

## Next Review
{{next_review_date?}}'),

('privacy_policy', 'Privacy Policy Template', ARRAY['Legal', 'Compliance']::text[],
'# Privacy Policy

**Company:** {{company_name}}
**Effective Date:** {{effective_date}}
**Contact:** {{privacy_contact?}}

## Information We Collect
{{information_collected}}

## How We Use Information
{{information_usage}}

## Data Sharing
{{data_sharing_policy?}}

## Data Security
{{security_measures?}}

## Your Rights
{{user_rights?}}
- Access
- Correction
- Deletion
- Portability

## Contact Us
{{contact_information?}}'),

-- ========================================
-- FINANCE & ACCOUNTING PROMPTS
-- ========================================

('expense_report', 'Expense Report', ARRAY['Finance', 'Business']::text[],
'# Expense Report

**Employee:** {{employee_name}}
**Period:** {{expense_period}}
**Department:** {{department?}}

## Expenses
{{expense_items}}

**Total:** {{total_amount}}

## Business Purpose
{{business_purpose?}}

## Receipts Attached
{{receipts_attached?}}

## Approval
Manager: {{manager_approval?}}
Finance: {{finance_approval?}}

## Payment Method
{{reimbursement_method?}}'),

('budget_proposal', 'Budget Proposal', ARRAY['Finance', 'Planning']::text[],
'# Budget Proposal: {{budget_name}}

**Department:** {{department}}
**Fiscal Year:** {{fiscal_year}}
**Prepared By:** {{preparer?}}

## Budget Summary
**Total Requested:** {{total_budget}}

## Line Items
{{budget_line_items}}
- Category: Amount
- Category: Amount

## Justification
{{budget_justification?}}

## Expected ROI
{{expected_roi?}}

## Risks
{{budget_risks?}}

## Approval Status
{{approval_status?}}'),

('financial_report', 'Financial Report', ARRAY['Finance', 'Business']::text[],
'# Financial Report

**Period:** {{reporting_period}}
**Department:** {{department}}
**Prepared By:** {{preparer_name?}}

## Executive Summary
{{executive_summary}}

## Revenue
{{revenue_details?}}
- Total: {{total_revenue?}}
- Growth: {{revenue_growth?}}%

## Expenses
{{expense_details?}}
- Total: {{total_expenses?}}
- Variance: {{expense_variance?}}%

## Profit/Loss
{{profit_loss?}}

## Key Metrics
{{key_metrics?}}
- Gross margin
- Operating margin
- EBITDA

## Recommendations
{{recommendations?}}'),

-- ========================================
-- PRODUCT MANAGEMENT PROMPTS
-- ========================================

('product_requirements', 'Product Requirements', ARRAY['Product', 'Planning']::text[],
'# PRD: {{product_name}}

**Version:** {{version}}
**Author:** {{author_name}}
**Date:** {{document_date?}}

## Overview
{{product_overview}}

## Objectives
{{product_objectives}}

## User Stories
{{user_stories?}}

## Functional Requirements
{{functional_requirements}}

## Non-Functional Requirements
{{non_functional_requirements?}}
- Performance
- Security
- Scalability

## Success Metrics
{{success_metrics?}}

## Timeline
{{timeline?}}

## Dependencies
{{dependencies?}}'),

('release_notes', 'Release Notes', ARRAY['Product', 'Documentation']::text[],
'# Release Notes v{{version}}

**Release Date:** {{release_date}}
**Product:** {{product_name?}}

## What\'s New
{{new_features}}

## Improvements
{{improvements}}

## Bug Fixes
{{bug_fixes?}}

## Known Issues
{{known_issues?}}

## Upgrade Instructions
{{upgrade_instructions?}}

## Deprecations
{{deprecations?}}

## Support
Contact: {{support_contact?}}'),

('product_roadmap', 'Product Roadmap', ARRAY['Product', 'Planning']::text[],
'# Product Roadmap: {{product_name}}

**Timeline:** {{timeline}}
**Product Owner:** {{product_owner?}}

## Vision
{{product_vision}}

## Milestones
{{milestones}}

## Feature Priorities
{{feature_list}}
- P0: Must have
- P1: Should have
- P2: Nice to have

## Dependencies
{{dependencies?}}

## Risks
{{risks?}}

## Success Metrics
{{metrics?}}'),

-- ========================================
-- DATA & ANALYTICS PROMPTS
-- ========================================

('data_analysis_report', 'Data Analysis Report', ARRAY['Analytics', 'Business']::text[],
'# Data Analysis: {{analysis_title}}

**Analyst:** {{analyst_name}}
**Date:** {{analysis_date}}
**Dataset:** {{dataset_name?}}

## Executive Summary
{{executive_summary}}

## Methodology
{{methodology}}

## Key Findings
{{key_findings}}

## Visualizations
{{charts_graphs?}}

## Recommendations
{{recommendations?}}

## Limitations
{{limitations?}}

## Appendix
{{appendix?}}'),

('dashboard_spec', 'Dashboard Specification', ARRAY['Analytics', 'Technical']::text[],
'# Dashboard: {{dashboard_name}}

**Purpose:** {{dashboard_purpose}}
**Audience:** {{target_audience}}
**Refresh Rate:** {{refresh_rate?}}

## KPIs
{{key_metrics}}

## Data Sources
{{data_sources?}}

## Visualizations
{{visualization_types?}}
- Charts
- Tables
- Maps

## Filters
{{filter_options?}}

## Drill-down Paths
{{drill_downs?}}

## Access Control
{{access_requirements?}}'),

-- ========================================
-- MISCELLANEOUS PROMPTS
-- ========================================

('survey_template', 'Survey Template', ARRAY['Research', 'Feedback']::text[],
'# Survey: {{survey_title}}

**Purpose:** {{survey_purpose}}
**Target Audience:** {{target_audience}}
**Deadline:** {{response_deadline?}}

## Questions
{{survey_questions}}

## Instructions
{{survey_instructions?}}

## Incentive
{{incentive_offered?}}

## Privacy
{{privacy_statement?}}

## Thank You
Thank you for your participation!'),

('presentation_outline', 'Presentation Outline', ARRAY['Communication', 'Business']::text[],
'# Presentation: {{presentation_title}}

**Presenter:** {{presenter_name}}
**Date:** {{presentation_date}}
**Audience:** {{audience?}}

## Objectives
{{presentation_objectives}}

## Outline
{{presentation_outline}}
1. Introduction
2. Main Points
3. Conclusion
4. Q&A

## Key Messages
{{key_messages?}}

## Visual Aids
{{visual_aids?}}

## Call to Action
{{call_to_action?}}

## Backup Slides
{{backup_content?}}'),

('status_report', 'Status Report', ARRAY['Management', 'Communication']::text[],
'# Status Report: {{project_name}}

**Report Date:** {{report_date}}
**Reporter:** {{reporter_name}}
**Period:** {{reporting_period?}}

## Overall Status
{{overall_status}}
- On Track / At Risk / Delayed

## Accomplishments
{{accomplishments}}

## Current Activities
{{current_activities?}}

## Issues & Risks
{{issues_risks?}}

## Next Steps
{{next_steps?}}

## Dependencies
{{dependencies?}}

## Help Needed
{{help_needed?}}'),

('architecture_design', 'Architecture Design', ARRAY['Technical', 'Architecture']::text[],
'# Architecture Design: {{system_name}}

**Version:** {{version}}
**Author:** {{architect_name}}
**Date:** {{design_date?}}

## Overview
{{system_overview}}

## Components
{{system_components}}

## Data Flow
{{data_flow}}

## Technology Stack
{{tech_stack?}}
- Frontend
- Backend
- Database
- Infrastructure

## Scalability
{{scalability_plan?}}

## Security
{{security_design?}}

## Integration Points
{{integrations?}}'),

('change_request', 'Change Request', ARRAY['Management', 'Process']::text[],
'# Change Request #{{request_number}}

**Requestor:** {{requestor_name}}
**Date:** {{request_date}}
**Priority:** {{priority?}}

## Change Description
{{change_description}}

## Business Justification
{{justification}}

## Impact Assessment
{{impact_assessment?}}
- Systems affected
- Users impacted
- Risk level

## Implementation Plan
{{implementation_plan?}}

## Rollback Plan
{{rollback_plan?}}

## Approvals Required
{{approvals_needed?}}

## Status
{{approval_status?}}'),

('vendor_evaluation', 'Vendor Evaluation', ARRAY['Procurement', 'Business']::text[],
'# Vendor Evaluation: {{vendor_name}}

**Product/Service:** {{product_service}}
**Evaluation Date:** {{evaluation_date}}
**Evaluator:** {{evaluator_name?}}

## Evaluation Criteria
{{evaluation_criteria}}

## Scoring
{{scoring_details?}}
- Technical: /10
- Price: /10
- Support: /10
- References: /10

## Overall Score
{{overall_score}}

## Strengths
{{vendor_strengths?}}

## Weaknesses
{{vendor_weaknesses?}}

## Recommendation
{{recommendation?}}
- Proceed / Reject / Further evaluation

## Next Steps
{{next_steps?}}');

-- Total: 40 prompts with rich content and minimal required inputs