# World Bank Dashboard

An interactive dashboard showcasing global economic and environmental data using the [Engine AI platform](https://platform.engineai.com).

Dashboard URL: https://platform.engineai.com/workspaces/demo-workspace/apps/demo-app/dashboards/demo-dashboard

## Overview

This dashboard demonstrates how to build data visualizations with real-world datasets. It displays key global indicators including GDP growth, CO2 emissions, renewable energy adoption, and economic metrics across major countries and regions.

**Features:**
- Interactive country selection and filtering
- Data from [World Bank API](https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information)
- Multiple visualization types: tables, charts, maps, and KPI tiles
- Responsive tabbed interface with economic and environmental analysis


## Prerequisites
- Python 3.10 or higher

## Setup

1. **Install dependencies**
   ```bash
   pip install engineai.sdk
   ```

2. **Publish dashboard**
   ```bash
   python dashboard.py
   ```

The dashboard will be deployed to the EngineAI platform and accessible through your workspace.

## Data Sources

- **World Bank API**: Free public data (no API key required)
- **Snowflake**: Processed analytical data

Built with [Engine AI SDK](https://docs.engineai.com/sdk/getting_started/installation.html)
