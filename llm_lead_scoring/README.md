# LLM Lead Scoring - AI-Powered Lead Qualification for Odoo 17

## Overview

The **LLM Lead Scoring** module revolutionizes your CRM lead management by integrating state-of-the-art Large Language Models (LLMs) to automatically assess, score, and enrich your leads with intelligent insights.

This module connects to multiple LLM providers (OpenAI, Groq, HuggingFace, Anthropic, Google Gemini, and more) to:
- Calculate AI-driven probability scores for leads
- Research customer information from publicly available sources
- Analyze lead quality based on completeness, clarity, and engagement
- Provide actionable recommendations for sales teams
- Automatically log enrichment data in internal memos

## Key Features

### 🤖 Multi-LLM Provider Support
- **OpenAI** (GPT-4, GPT-3.5)
- **Groq** (Llama 3.1, Mixtral)
- **Anthropic** (Claude 3 Sonnet, Opus, Haiku)
- **Google** (Gemini Pro)
- **HuggingFace** (Various open-source models)
- **Mistral AI** (Mistral Large, Medium)
- **Cohere**
- **Custom API** endpoints

### 📊 AI Probability Scoring
The module calculates a comprehensive AI probability score (0-100) based on three key factors:

1. **Completeness Score (30% weight)**
   - Evaluates how complete the lead information is
   - Checks critical fields: company name, contact, email, phone, requirements
   - Identifies missing information

2. **Requirement Clarity Score (40% weight)**
   - Uses LLM to analyze how clear and specific customer requirements are
   - Assesses actionable information and detailed needs
   - Identifies key points and missing information

3. **Engagement Score (30% weight)**
   - Analyzes activity logs and interactions
   - Counts scheduled activities and communications
   - Considers recency of engagement

### 🔍 Customer Research
- Leverages LLM to research publicly available information about customers
- Provides insights on:
  - Company background and industry
  - Company size and market presence
  - Key products/services
  - Recent news and developments
  - Business credibility indicators
  - Potential buying signals

### 📝 Automated Enrichment Logging
- All enrichment data is automatically logged in internal notes
- Beautifully formatted HTML reports with:
  - Overall and breakdown scores
  - Detailed analysis for each scoring factor
  - Customer research findings
  - AI recommendations for next actions

### ⚙️ Flexible Configuration
- Configure multiple LLM providers with different models
- Set default providers and model parameters (temperature, max tokens, timeout)
- Customize scoring weights to match your business priorities
- Enable/disable auto-enrichment features
- Control customer research functionality

### 🔄 Automated Workflows
- **Auto-enrich new leads**: Automatically score leads when created
- **Auto-enrich on update**: Re-score leads when key fields change
- **Scheduled enrichment**: Background job to enrich pending leads
- **Batch enrichment**: Process multiple leads at once

## Installation

1. Copy the `llm_lead_scoring` folder to your Odoo addons directory
2. Update the apps list: Settings > Apps > Update Apps List
3. Search for "LLM Lead Scoring" and click Install
4. Configure your LLM provider(s) in Settings > CRM > LLM Lead Scoring

## Configuration

### Step 1: Configure LLM Provider

1. Go to **LLM Lead Scoring > Configuration > LLM Providers**
2. Create or edit a provider:
   - Choose provider type (OpenAI, Groq, Anthropic, etc.)
   - Enter your API key
   - Specify the model name (e.g., `gpt-4`, `llama-3.1-70b-versatile`, `claude-3-sonnet`)
   - Adjust parameters (temperature, max tokens, timeout)
   - Set as default provider

### Step 2: Configure Settings

1. Go to **Settings > CRM Settings**
2. Scroll to "LLM Lead Scoring" section
3. Configure:
   - Enable auto-enrichment features
   - Enable customer research
   - Select default LLM provider
   - Adjust scoring weights (must total 100%)

### Step 3: Test on a Lead

1. Open any CRM lead/opportunity
2. Click the **"AI Enrich"** button in the header
3. View the AI scores in the "AI Scoring" tab
4. Check the internal notes for the detailed enrichment report

## Usage

### Manual Enrichment

**Single Lead:**
1. Open a lead form
2. Click "AI Enrich" button
3. Wait for processing (usually 5-15 seconds)
4. View results in "AI Scoring" tab and internal notes

**Batch Enrichment:**
1. Select multiple leads in list view
2. Go to Action menu > "AI Enrich Selected Leads"
3. Configure options in wizard
4. Click "Enrich Leads"

### Automated Enrichment

Enable automated enrichment in Settings:
- **Auto-enrich new leads**: Enriches leads immediately upon creation
- **Auto-enrich on update**: Re-enriches when key fields (name, email, description, etc.) change
- **Scheduled enrichment**: Enable the cron job to process pending leads every hour

### Viewing Results

**AI Probability Score:**
- Visible on lead form (after probability field)
- Shown in list view
- Displayed as badge in kanban view with color coding:
  - 🟢 Green: Score ≥ 70 (High probability)
  - 🟡 Yellow: Score 40-69 (Medium probability)
  - 🔴 Red: Score < 40 (Low probability)

**Detailed Analysis:**
- Go to "AI Scoring" tab on lead form
- View score breakdown (completeness, clarity, engagement)
- Read AI analysis summary
- Review enrichment data in JSON format

**Enrichment Report:**
- Check internal notes/chatter
- Find "AI Lead Enrichment" comment
- Review formatted report with scores, analysis, and research

## API Keys & Providers

### Getting API Keys

**OpenAI:**
- Sign up at https://platform.openai.com/
- Create API key in API Keys section
- Recommended model: `gpt-4-turbo-preview` or `gpt-3.5-turbo`

**Groq:**
- Sign up at https://console.groq.com/
- Generate API key
- Recommended model: `llama-3.1-70b-versatile`

**Anthropic (Claude):**
- Sign up at https://console.anthropic.com/
- Create API key
- Recommended model: `claude-3-sonnet-20240229`

**Google (Gemini):**
- Get API key from https://makersuite.google.com/app/apikey
- Recommended model: `gemini-pro`

**HuggingFace:**
- Create account at https://huggingface.co/
- Generate token in Settings > Access Tokens
- Use model ID like: `mistralai/Mixtral-8x7B-Instruct-v0.1`

**Mistral AI:**
- Sign up at https://console.mistral.ai/
- Create API key
- Recommended model: `mistral-large-latest`

### Cost Considerations

LLM API costs vary by provider and model:
- **OpenAI GPT-4**: ~$0.01-0.03 per enrichment
- **OpenAI GPT-3.5**: ~$0.001-0.002 per enrichment
- **Groq**: Often free tier or very low cost
- **Anthropic Claude**: ~$0.01-0.02 per enrichment
- **Google Gemini**: Free tier available, then ~$0.001 per enrichment

Estimate: For 1000 leads/month with GPT-4, expect $10-30 in API costs.

## Technical Details

### Module Structure
```
llm_lead_scoring/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── llm_provider.py          # LLM provider configuration
│   ├── llm_service.py            # LLM API integration service
│   ├── crm_lead.py               # Extended CRM lead model
│   └── res_config_settings.py   # Settings configuration
├── views/
│   ├── llm_provider_views.xml
│   ├── res_config_settings_views.xml
│   ├── crm_lead_views.xml
│   └── wizard views
├── wizards/
│   ├── __init__.py
│   └── lead_enrichment_wizard.py
├── security/
│   └── ir.model.access.csv
├── data/
│   ├── llm_provider_data.xml
│   └── ir_cron_data.xml
└── static/
    └── description/
```

### Dependencies
- `base`
- `crm`
- `mail`
- Python `requests` library (included in standard Odoo)

### Models

**llm.provider**: Stores LLM provider configurations
**llm.service**: Abstract model providing LLM integration methods
**crm.lead** (extended): Adds AI scoring fields and methods

### New Fields on CRM Lead
- `ai_probability_score`: Overall AI probability (0-100)
- `ai_completeness_score`: Information completeness score
- `ai_clarity_score`: Requirement clarity score
- `ai_engagement_score`: Engagement level score
- `ai_enrichment_data`: JSON data with full analysis
- `ai_last_enrichment_date`: Timestamp of last enrichment
- `ai_enrichment_status`: Status (pending/processing/completed/failed)
- `ai_analysis_summary`: Summary text from LLM
- `auto_enrich`: Boolean flag to enable/disable auto-enrichment per lead

## Troubleshooting

### Issue: "No LLM provider configured"
**Solution:** Configure at least one LLM provider and set it as default in Settings > CRM > LLM Lead Scoring

### Issue: API errors or timeouts
**Solution:**
- Check API key is correct
- Verify you have API credits/quota
- Increase timeout in provider settings
- Try a different provider/model

### Issue: Low-quality scores or analysis
**Solution:**
- Ensure lead has sufficient information (description, contact details)
- Try a more powerful model (e.g., GPT-4 instead of GPT-3.5)
- Adjust temperature (lower = more consistent, higher = more creative)

### Issue: Enrichment taking too long
**Solution:**
- Disable customer research in settings (saves 1 API call per lead)
- Use faster models (GPT-3.5, Groq Llama)
- Reduce max_tokens parameter
- Process leads in smaller batches

## Best Practices

1. **Start with a few test leads** before enabling auto-enrichment
2. **Monitor API costs** especially with premium models like GPT-4
3. **Use scheduled enrichment** for large volumes rather than real-time
4. **Customize scoring weights** based on your sales process
5. **Regularly update provider settings** to use latest model versions
6. **Review enrichment reports** to fine-tune your lead qualification process
7. **Combine with standard Odoo probability** for hybrid scoring

## Privacy & Security

- API keys are stored encrypted in Odoo database
- Customer research only uses publicly available information
- No sensitive data is sent to LLM providers beyond what's in the lead
- Enrichment data is stored in Odoo, not with LLM providers
- Complies with data privacy regulations (configure research features accordingly)

## Roadmap

Future enhancements planned:
- [ ] Integration with web scraping tools for deeper research
- [ ] Custom prompt templates per lead stage
- [ ] A/B testing of different scoring algorithms
- [ ] Lead score trend analysis and reports
- [ ] Integration with email sentiment analysis
- [ ] Multi-language support for international leads
- [ ] Predictive next-best-action recommendations

## Support

For issues, feature requests, or contributions:
- Create an issue in the repository
- Contact support at support@yourcompany.com
- Check documentation at https://docs.yourcompany.com

## License

LGPL-3

## Credits

Developed by: Your Company
Maintainer: Your Company

---

**Transform your lead qualification process with the power of AI! 🚀**
