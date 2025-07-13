#!/usr/bin/env python3
"""
Plausible Stats Aggregator

A script to retrieve analytics stats from all sites in a Plausible account
and export them to CSV files for month-to-date and year-to-date metrics.
"""

import logging
import sys
import os
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import settings
from src.clients.sites_client import SitesAPIClient
from src.clients.stats_client import StatsAPIClient
from src.processors.stats_processor import StatsProcessor
from src.exporters.csv_exporter import CSVExporter

def setup_logging():
    """Set up application logging."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # File handler
    log_filename = f"logs/plausible_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return log_filename

def main():
    """Main application entry point."""
    # Set up logging
    log_file = setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Plausible Stats Aggregator Started")
    logger.info("=" * 60)
    logger.info(f"Log file: {log_file}")
    
    try:
        # Validate configuration
        settings.validate()
        logger.info("Configuration validated successfully")
        
        # Initialize clients
        logger.info("Initializing API clients...")
        sites_client = SitesAPIClient(
            api_key=settings.sites_api_key,
            base_url=settings.sites_api_url,
            timeout=settings.request_timeout
        )
        
        stats_client = StatsAPIClient(
            api_key=settings.stats_api_key,
            base_url=settings.stats_api_url,
            timeout=settings.request_timeout,
            request_delay=settings.request_delay
        )
        
        # Initialize processor and exporter
        processor = StatsProcessor()
        exporter = CSVExporter(output_dir=settings.output_dir)
        
        # Step 1: Get all sites
        logger.info("Step 1: Retrieving all sites from Plausible account...")
        sites = sites_client.get_sites()
        
        if not sites:
            logger.error("No sites found in your Plausible account")
            return 1
        
        logger.info(f"Found {len(sites)} sites:")
        for site in sites:
            logger.info(f"  - {site.domain} (timezone: {site.timezone})")
        
        # Step 2: Get stats for all sites
        logger.info("Step 2: Retrieving stats for all sites...")
        site_domains = [site.domain for site in sites]
        date_ranges = ['month', 'year']  # MTD and YTD
        
        all_stats = stats_client.get_bulk_stats(
            sites=site_domains,
            metrics=settings.metrics,
            date_ranges=date_ranges
        )
        
        if not all_stats:
            logger.error("No stats data retrieved")
            return 1
        
        logger.info(f"Retrieved stats for {len(all_stats)} site/period combinations")
        
        # Step 3: Validate and process stats
        logger.info("Step 3: Processing and validating stats data...")
        valid_stats = processor.validate_stats(all_stats)
        aggregated_stats = processor.aggregate_stats_by_period(valid_stats)
        
        # Step 4: Export data
        logger.info("Step 4: Exporting data to CSV files...")
        
        mtd_file = ""
        ytd_file = ""
        
        # Export Month-to-Date stats
        if 'month' in aggregated_stats:
            mtd_stats = aggregated_stats['month']
            mtd_data = processor.prepare_export_data(mtd_stats, include_totals=True)
            mtd_file = exporter.export_month_to_date(mtd_data)
            logger.info(f"Month-to-Date stats exported to: {mtd_file}")
        else:
            logger.warning("No month-to-date stats available")
        
        # Export Year-to-Date stats
        if 'year' in aggregated_stats:
            ytd_stats = aggregated_stats['year']
            ytd_data = processor.prepare_export_data(ytd_stats, include_totals=True)
            ytd_file = exporter.export_year_to_date(ytd_data)
            logger.info(f"Year-to-Date stats exported to: {ytd_file}")
        else:
            logger.warning("No year-to-date stats available")
        
        # Create summary file
        if mtd_file or ytd_file:
            summary_file = exporter.create_summary_file(mtd_file, ytd_file)
            logger.info(f"Export summary created: {summary_file}")
        
        # Final summary
        logger.info("=" * 60)
        logger.info("Export completed successfully!")
        logger.info("=" * 60)
        logger.info(f"Sites processed: {len(sites)}")
        logger.info(f"Stats records: {len(valid_stats)}")
        
        if mtd_file:
            logger.info(f"Month-to-Date file: {os.path.basename(mtd_file)}")
        if ytd_file:
            logger.info(f"Year-to-Date file: {os.path.basename(ytd_file)}")
        
        logger.info(f"Output directory: {settings.output_dir}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        return 1
    
    finally:
        # Clean up
        try:
            sites_client.close()
            stats_client.close()
        except:
            pass

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
