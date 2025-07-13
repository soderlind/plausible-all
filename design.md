# Plausible Stats Aggregator - Design Document

## Overview
A Python script to retrieve comprehensive analytics stats from all sites in a Plausible Analytics account and export them to CSV files for month-to-date and year-to-date metrics.

## Requirements Analysis

### Functional Requirements
1. **Site Discovery**: Retrieve all sites from Plausible account using Sites API
2. **Stats Retrieval**: Get analytics data for each site using Stats API
3. **Data Aggregation**: Combine stats from all sites into unified data structures
4. **CSV Export**: Generate two CSV files:
   - `./output/month-to-date.csv` - Current month's stats
   - `./output/year-to-date.csv` - Current year's stats

### API Endpoints
- **Sites API**: `GET /api/v1/sites` - List all accessible sites
- **Stats API**: `POST /api/v2/query` - Retrieve analytics data

## Architecture Design

### 1. Authentication
- **API Keys**: Two separate API keys required
  - Sites API key for site discovery
  - Stats API key for analytics data
- **Authentication Method**: Bearer Token in Authorization header

### 2. Data Flow
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Sites API     │───▶│  Stats API      │───▶│   CSV Export    │
│ (Get all sites) │    │ (Get site stats)│    │ (MTD & YTD)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 3. Core Components

#### 3.1 Configuration Manager
- Store API keys securely (environment variables)
- Define date ranges for MTD/YTD
- Configure metrics to retrieve

#### 3.2 API Client
- **PlausibleSitesClient**: Handle Sites API requests
- **PlausibleStatsClient**: Handle Stats API requests
- Rate limiting compliance (600 requests/hour for Stats API)
- Error handling and retry logic

#### 3.3 Data Models
```python
@dataclass
class Site:
    domain: str
    timezone: str

@dataclass
class SiteStats:
    site_domain: str
    period: str  # 'month' or 'year'
    visitors: int
    visits: int
    pageviews: int
    bounce_rate: float
    visit_duration: int
    views_per_visit: float
```

#### 3.4 Data Processor
- Aggregate stats from multiple sites
- Handle timezone considerations
- Calculate derived metrics if needed

#### 3.5 CSV Exporter
- Generate formatted CSV files
- Ensure output directory exists
- Handle file writing errors

## Technical Specifications

### 3.1 Metrics to Retrieve
Based on Stats API documentation, we'll collect these core metrics:
- `visitors` - Unique visitors count
- `visits` - Total visits/sessions
- `pageviews` - Total pageviews
- `bounce_rate` - Bounce rate percentage
- `visit_duration` - Average visit duration in seconds
- `views_per_visit` - Pages per visit

### 3.2 Date Ranges
- **Month-to-Date**: `"month"` - Since start of current month
- **Year-to-Date**: `"year"` - Since start of current year

### 3.3 Request Structure
```json
{
  "site_id": "example.com",
  "metrics": ["visitors", "visits", "pageviews", "bounce_rate", "visit_duration", "views_per_visit"],
  "date_range": "month"  // or "year"
}
```

## Implementation Plan

### Phase 1: Core Infrastructure
1. Set up project structure
2. Create configuration management
3. Implement API client classes
4. Add error handling and logging

### Phase 2: Data Retrieval
1. Implement site discovery
2. Implement stats retrieval for individual sites
3. Add rate limiting and retry logic
4. Test with sample sites

### Phase 3: Data Processing & Export
1. Create data aggregation logic
2. Implement CSV export functionality
3. Add data validation
4. Create output directory management

### Phase 4: Testing & Optimization
1. End-to-end testing
2. Performance optimization
3. Error scenario handling
4. Documentation

## File Structure
```
plausible-stats-aggregator/
├── config/
│   └── settings.py          # Configuration management
├── src/
│   ├── clients/
│   │   ├── sites_client.py  # Sites API client
│   │   └── stats_client.py  # Stats API client
│   ├── models/
│   │   └── data_models.py   # Data classes
│   ├── processors/
│   │   └── stats_processor.py # Data aggregation
│   └── exporters/
│       └── csv_exporter.py  # CSV generation
├── output/                  # Generated CSV files
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── main.py                 # Main execution script
```

## Error Handling Strategy

### API Errors
- **Rate Limiting**: Implement exponential backoff
- **Authentication**: Clear error messages for invalid keys
- **Network Issues**: Retry with timeout handling
- **Site Access**: Skip inaccessible sites with logging

### Data Processing Errors
- **Missing Data**: Handle partial responses gracefully
- **Timezone Issues**: Convert all times to consistent timezone
- **Validation**: Verify data integrity before export

## Security Considerations
- Store API keys in environment variables
- Never log sensitive information
- Validate all API responses
- Implement proper error sanitization

## Performance Considerations
- **Concurrent Requests**: Process multiple sites in parallel (within rate limits)
- **Memory Usage**: Stream large datasets instead of loading all in memory
- **Caching**: Cache site list for multiple runs
- **Progress Tracking**: Show progress for long-running operations

## Future Enhancements
- Support for custom date ranges
- Additional metrics (goals, custom events)
- Multiple output formats (JSON, Excel)
- Real-time dashboard integration
- Scheduled execution with cron
- Data visualization components

## Dependencies
- `requests` - HTTP client
- `python-dotenv` - Environment variable management
- `dataclasses` - Data modeling (Python 3.7+)
- `csv` - CSV file generation (built-in)
- `logging` - Application logging (built-in)
- `concurrent.futures` - Parallel processing (built-in)

## Configuration Requirements
Environment variables needed:
- `PLAUSIBLE_SITES_API_KEY` - Sites API key
- `PLAUSIBLE_STATS_API_KEY` - Stats API key
- `PLAUSIBLE_BASE_URL` - Base URL (default: https://plausible.io)
- `OUTPUT_DIR` - Output directory (default: ./output)
- `LOG_LEVEL` - Logging level (default: INFO)
