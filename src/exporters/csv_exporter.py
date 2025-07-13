import csv
import os
import logging
from typing import List, Dict, Any
from datetime import datetime

class CSVExporter:
    """Exports stats data to CSV files."""
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        self.logger.info(f"CSV exporter initialized with output directory: {output_dir}")
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Export data to CSV file.
        
        Args:
            data: List of dictionaries containing the data
            filename: Name of the output file (without path)
            
        Returns:
            Full path to the created file
        """
        if not data:
            self.logger.warning(f"No data to export for {filename}")
            return ""
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                # Use the keys from the first row as fieldnames
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write data rows
                for row in data:
                    writer.writerow(row)
            
            self.logger.info(f"Successfully exported {len(data)} rows to {filepath}")
            return filepath
            
        except Exception as e:
            error_msg = f"Failed to export CSV to {filepath}: {e}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def export_month_to_date(self, data: List[Dict[str, Any]]) -> str:
        """
        Export month-to-date stats to CSV.
        
        Args:
            data: List of dictionaries containing month-to-date stats
            
        Returns:
            Full path to the created file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"month-to-date_{timestamp}.csv"
        
        self.logger.info("Exporting month-to-date stats")
        return self.export_to_csv(data, filename)
    
    def export_year_to_date(self, data: List[Dict[str, Any]]) -> str:
        """
        Export year-to-date stats to CSV.
        
        Args:
            data: List of dictionaries containing year-to-date stats
            
        Returns:
            Full path to the created file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"year-to-date_{timestamp}.csv"
        
        self.logger.info("Exporting year-to-date stats")
        return self.export_to_csv(data, filename)
    
    def export_combined_report(self, mtd_data: List[Dict[str, Any]], ytd_data: List[Dict[str, Any]]) -> str:
        """
        Export a combined report with both MTD and YTD data.
        
        Args:
            mtd_data: Month-to-date stats data
            ytd_data: Year-to-date stats data
            
        Returns:
            Full path to the created file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"combined-stats_{timestamp}.csv"
        
        # Combine data with period indicators
        combined_data = []
        
        # Add MTD data
        for row in mtd_data:
            combined_row = row.copy()
            combined_row['report_type'] = 'Month-to-Date'
            combined_data.append(combined_row)
        
        # Add YTD data
        for row in ytd_data:
            combined_row = row.copy()
            combined_row['report_type'] = 'Year-to-Date'
            combined_data.append(combined_row)
        
        self.logger.info(f"Exporting combined report with {len(mtd_data)} MTD and {len(ytd_data)} YTD records")
        return self.export_to_csv(combined_data, filename)
    
    def create_summary_file(self, mtd_file: str, ytd_file: str) -> str:
        """
        Create a summary file with export information.
        
        Args:
            mtd_file: Path to month-to-date CSV file
            ytd_file: Path to year-to-date CSV file
            
        Returns:
            Full path to the summary file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_filename = f"export-summary_{timestamp}.txt"
        summary_filepath = os.path.join(self.output_dir, summary_filename)
        
        try:
            with open(summary_filepath, 'w', encoding='utf-8') as f:
                f.write("Plausible Stats Export Summary\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("Files Generated:\n")
                if mtd_file:
                    f.write(f"  - Month-to-Date: {os.path.basename(mtd_file)}\n")
                if ytd_file:
                    f.write(f"  - Year-to-Date: {os.path.basename(ytd_file)}\n")
                
                f.write("\nFile Locations:\n")
                if mtd_file:
                    f.write(f"  - MTD: {mtd_file}\n")
                if ytd_file:
                    f.write(f"  - YTD: {ytd_file}\n")
                
                # Add file sizes if files exist
                f.write("\nFile Sizes:\n")
                if mtd_file and os.path.exists(mtd_file):
                    size = os.path.getsize(mtd_file)
                    f.write(f"  - MTD: {size:,} bytes\n")
                if ytd_file and os.path.exists(ytd_file):
                    size = os.path.getsize(ytd_file)
                    f.write(f"  - YTD: {size:,} bytes\n")
            
            self.logger.info(f"Created export summary: {summary_filepath}")
            return summary_filepath
            
        except Exception as e:
            error_msg = f"Failed to create summary file: {e}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_available_exports(self) -> List[str]:
        """
        Get list of available export files in the output directory.
        
        Returns:
            List of CSV filenames in the output directory
        """
        try:
            files = [f for f in os.listdir(self.output_dir) if f.endswith('.csv')]
            files.sort(reverse=True)  # Most recent first
            return files
        except Exception as e:
            self.logger.error(f"Error listing export files: {e}")
            return []
