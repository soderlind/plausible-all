import logging
from typing import List, Dict, Any
from datetime import datetime

from ..models.data_models import Site, SiteStats

class StatsProcessor:
    """Processes and aggregates stats data from multiple sites."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def aggregate_stats_by_period(self, stats_list: List[SiteStats]) -> Dict[str, List[SiteStats]]:
        """
        Group stats by period (month/year).
        
        Args:
            stats_list: List of SiteStats objects
            
        Returns:
            Dictionary with period as key and list of stats as value
        """
        aggregated = {}
        
        for stats in stats_list:
            period = stats.period
            if period not in aggregated:
                aggregated[period] = []
            aggregated[period].append(stats)
        
        self.logger.info(f"Aggregated {len(stats_list)} stats records into {len(aggregated)} periods")
        for period, period_stats in aggregated.items():
            self.logger.debug(f"Period '{period}': {len(period_stats)} sites")
        
        return aggregated
    
    def calculate_totals(self, stats_list: List[SiteStats]) -> Dict[str, Any]:
        """
        Calculate total metrics across all sites for a given period.
        
        Args:
            stats_list: List of SiteStats for the same period
            
        Returns:
            Dictionary with total metrics
        """
        if not stats_list:
            return {}
        
        totals = {
            'total_sites': len(stats_list),
            'total_visitors': sum(stats.visitors for stats in stats_list),
            'total_visits': sum(stats.visits for stats in stats_list),
            'total_pageviews': sum(stats.pageviews for stats in stats_list),
            'total_visit_duration': sum(stats.visit_duration * stats.visits for stats in stats_list),
            'period': stats_list[0].period,
            'calculated_at': datetime.now()
        }
        
        # Calculate weighted averages
        total_visits = totals['total_visits']
        if total_visits > 0:
            # Weighted average bounce rate
            total_bounced_visits = sum(
                (stats.bounce_rate / 100) * stats.visits 
                for stats in stats_list
            )
            totals['avg_bounce_rate'] = (total_bounced_visits / total_visits) * 100
            
            # Weighted average visit duration
            totals['avg_visit_duration'] = totals['total_visit_duration'] / total_visits
            
            # Average views per visit
            totals['avg_views_per_visit'] = totals['total_pageviews'] / total_visits
        else:
            totals['avg_bounce_rate'] = 0.0
            totals['avg_visit_duration'] = 0.0
            totals['avg_views_per_visit'] = 0.0
        
        self.logger.info(f"Calculated totals for {totals['total_sites']} sites in period '{totals['period']}'")
        self.logger.debug(f"Total visitors: {totals['total_visitors']}, Total visits: {totals['total_visits']}")
        
        return totals
    
    def prepare_export_data(self, stats_list: List[SiteStats], include_totals: bool = True) -> List[Dict[str, Any]]:
        """
        Prepare stats data for CSV export.
        
        Args:
            stats_list: List of SiteStats objects
            include_totals: Whether to include a totals row
            
        Returns:
            List of dictionaries ready for CSV export
        """
        export_data = []
        
        # Add individual site data
        for stats in stats_list:
            row = {
                'site_domain': stats.site_domain,
                'period': stats.period,
                'date_range': stats.date_range,
                'visitors': stats.visitors,
                'visits': stats.visits,
                'pageviews': stats.pageviews,
                'bounce_rate': round(stats.bounce_rate, 2),
                'visit_duration': stats.visit_duration,
                'views_per_visit': round(stats.views_per_visit, 2),
                'retrieved_at': stats.retrieved_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            export_data.append(row)
        
        # Add totals row if requested
        if include_totals and stats_list:
            totals = self.calculate_totals(stats_list)
            totals_row = {
                'site_domain': 'TOTAL',
                'period': totals['period'],
                'date_range': f"All sites ({totals['total_sites']} sites)",
                'visitors': totals['total_visitors'],
                'visits': totals['total_visits'],
                'pageviews': totals['total_pageviews'],
                'bounce_rate': round(totals['avg_bounce_rate'], 2),
                'visit_duration': round(totals['avg_visit_duration'], 2),
                'views_per_visit': round(totals['avg_views_per_visit'], 2),
                'retrieved_at': totals['calculated_at'].strftime('%Y-%m-%d %H:%M:%S')
            }
            export_data.append(totals_row)
        
        self.logger.info(f"Prepared {len(export_data)} rows for export")
        return export_data
    
    def filter_by_period(self, stats_list: List[SiteStats], period: str) -> List[SiteStats]:
        """
        Filter stats by specific period.
        
        Args:
            stats_list: List of SiteStats objects
            period: Period to filter by ('month', 'year', etc.)
            
        Returns:
            Filtered list of SiteStats
        """
        filtered = [stats for stats in stats_list if stats.period == period]
        self.logger.debug(f"Filtered {len(stats_list)} stats to {len(filtered)} for period '{period}'")
        return filtered
    
    def validate_stats(self, stats_list: List[SiteStats]) -> List[SiteStats]:
        """
        Validate and clean stats data.
        
        Args:
            stats_list: List of SiteStats objects
            
        Returns:
            List of validated SiteStats objects
        """
        valid_stats = []
        
        for stats in stats_list:
            # Basic validation
            if not stats.site_domain:
                self.logger.warning("Skipping stats with empty site_domain")
                continue
            
            if stats.visitors < 0 or stats.visits < 0 or stats.pageviews < 0:
                self.logger.warning(f"Skipping stats for {stats.site_domain} with negative values")
                continue
            
            if stats.bounce_rate < 0 or stats.bounce_rate > 100:
                self.logger.warning(f"Invalid bounce rate for {stats.site_domain}: {stats.bounce_rate}%. Clamping to 0-100%")
                stats.bounce_rate = max(0, min(100, stats.bounce_rate))
            
            if stats.visit_duration < 0:
                self.logger.warning(f"Negative visit duration for {stats.site_domain}. Setting to 0")
                stats.visit_duration = 0
            
            if stats.views_per_visit < 0:
                self.logger.warning(f"Negative views per visit for {stats.site_domain}. Setting to 0")
                stats.views_per_visit = 0
            
            valid_stats.append(stats)
        
        removed_count = len(stats_list) - len(valid_stats)
        if removed_count > 0:
            self.logger.warning(f"Removed {removed_count} invalid stats records")
        
        return valid_stats
