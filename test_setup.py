#!/usr/bin/env python3
"""
Test script for Plausible Stats Aggregator

This script validates the installation and configuration without making API calls.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import requests
        print("  ✅ requests")
    except ImportError:
        print("  ❌ requests - run 'pip install requests'")
        return False
    
    try:
        from dotenv import load_dotenv
        print("  ✅ python-dotenv")
    except ImportError:
        print("  ❌ python-dotenv - run 'pip install python-dotenv'")
        return False
    
    try:
        from config.settings import settings
        print("  ✅ config.settings")
    except ImportError as e:
        print(f"  ❌ config.settings - {e}")
        return False
    
    try:
        from src.clients.sites_client import SitesAPIClient
        from src.clients.stats_client import StatsAPIClient
        print("  ✅ API clients")
    except ImportError as e:
        print(f"  ❌ API clients - {e}")
        return False
    
    try:
        from src.processors.stats_processor import StatsProcessor
        from src.exporters.csv_exporter import CSVExporter
        print("  ✅ Processors and exporters")
    except ImportError as e:
        print(f"  ❌ Processors and exporters - {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration setup."""
    print("\nTesting configuration...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("  ⚠️  .env file not found - copy .env.example to .env and configure")
        return False
    
    try:
        from config.settings import settings
        
        # Test basic settings access
        print(f"  ✅ Base URL: {settings.base_url}")
        print(f"  ✅ Output directory: {settings.output_dir}")
        print(f"  ✅ Log level: {settings.log_level}")
        print(f"  ✅ Metrics: {', '.join(settings.metrics)}")
        
        # Check API keys (without revealing them)
        if settings.sites_api_key and settings.sites_api_key != "your_sites_api_key_here":
            print("  ✅ Sites API key configured")
        else:
            print("  ⚠️  Sites API key not configured in .env")
            return False
        
        if settings.stats_api_key and settings.stats_api_key != "your_stats_api_key_here":
            print("  ✅ Stats API key configured")
        else:
            print("  ⚠️  Stats API key not configured in .env")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def test_directories():
    """Test that required directories exist or can be created."""
    print("\nTesting directories...")
    
    directories = ['output', 'logs']
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"  ✅ {directory}/ directory ready")
        except Exception as e:
            print(f"  ❌ Failed to create {directory}/ directory: {e}")
            return False
    
    return True

def test_data_models():
    """Test data model creation."""
    print("\nTesting data models...")
    
    try:
        from src.models.data_models import Site, SiteStats, StatsQuery
        from datetime import datetime
        
        # Test Site model
        site = Site(domain="example.com", timezone="UTC")
        print(f"  ✅ Site model: {site}")
        
        # Test SiteStats model
        stats = SiteStats(
            site_domain="example.com",
            period="month",
            date_range="2024-01-01 to 2024-01-31",
            visitors=100,
            visits=150,
            pageviews=300,
            bounce_rate=45.5,
            visit_duration=120,
            views_per_visit=2.0,
            retrieved_at=datetime.now()
        )
        print(f"  ✅ SiteStats model: visitors={stats.visitors}, visits={stats.visits}")
        
        # Test StatsQuery model
        query = StatsQuery(
            site_id="example.com",
            metrics=["visitors", "visits"],
            date_range="month"
        )
        query_dict = query.to_dict()
        print(f"  ✅ StatsQuery model: {len(query_dict)} fields")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Data model error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Plausible Stats Aggregator - Installation Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_directories,
        test_data_models
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    
    if all(results):
        print("🎉 All tests passed! The application is ready to run.")
        print("\nNext steps:")
        print("1. Ensure your API keys are correctly set in .env")
        print("2. Run: python main.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("- Run: pip install -r requirements.txt")
        print("- Copy .env.example to .env and configure your API keys")
        print("- Check file permissions")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
