# File: StudentBookDownloader.py
# Path: /home/herb/Desktop/AndyLibrary/Source/Core/StudentBookDownloader.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 01:24PM

"""
Student Book Downloader - Educational Mission Focused
Provides cost-conscious book download with full transparency for students
"""

import os
import sys
import sqlite3
import time
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class BookCostInfo:
    """Information about book download costs for students"""
    book_id: int
    title: str
    file_size_mb: float
    estimated_cost_usd: float
    warning_level: str  # 'low', 'medium', 'high', 'extreme'
    budget_percentage: float  # % of $5 monthly budget

class CostWarningLevel(Enum):
    """Cost warning levels for student protection"""
    LOW = "low"        # <$0.50 (green)
    MEDIUM = "medium"  # $0.50-$1.50 (yellow)  
    HIGH = "high"      # $1.50-$3.00 (orange)
    EXTREME = "extreme" # >$3.00 (red)

class StudentRegion(Enum):
    """Student regions with different data costs"""
    DEVELOPING = "developing"  # $0.10/MB (Africa, rural Asia)
    EMERGING = "emerging"      # $0.05/MB (urban Asia, Latin America) 
    DEVELOPED = "developed"    # $0.02/MB (Europe, North America)

class StudentBookDownloader:
    """Handles book downloads with student cost protection"""
    
    def __init__(self, database_path: str = "Data/Databases/MyLibrary.db"):
        self.database_path = database_path
        self.monthly_budget_usd = 5.00  # Student monthly data budget
        self.cost_per_mb = {
            StudentRegion.DEVELOPING: 0.10,
            StudentRegion.EMERGING: 0.05,
            StudentRegion.DEVELOPED: 0.02
        }
        
        # Student download preferences
        self.default_region = StudentRegion.DEVELOPING  # Most conservative
        self.download_history = []
        self.monthly_spending = 0.0
        
    def GetBookCostEstimate(self, book_id: int, region: StudentRegion = None) -> Optional[BookCostInfo]:
        """Get cost estimate for downloading a book"""
        region = region or self.default_region
        
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        
        try:
            # Get book info from database
            book = conn.execute("""
                SELECT id, title, author, FileSize 
                FROM books 
                WHERE id = ?
            """, (book_id,)).fetchone()
            
            if not book:
                return None
            
            # Calculate costs
            file_size_mb = (book['FileSize'] or 5000000) / (1024 * 1024)  # Default 5MB if unknown
            cost_per_mb_rate = self.cost_per_mb[region]
            estimated_cost = file_size_mb * cost_per_mb_rate
            budget_percentage = (estimated_cost / self.monthly_budget_usd) * 100
            
            # Determine warning level
            if estimated_cost < 0.50:
                warning_level = CostWarningLevel.LOW.value
            elif estimated_cost < 1.50:
                warning_level = CostWarningLevel.MEDIUM.value
            elif estimated_cost < 3.00:
                warning_level = CostWarningLevel.HIGH.value
            else:
                warning_level = CostWarningLevel.EXTREME.value
            
            return BookCostInfo(
                book_id=book_id,
                title=book['title'],
                file_size_mb=round(file_size_mb, 1),
                estimated_cost_usd=round(estimated_cost, 2),
                warning_level=warning_level,
                budget_percentage=round(budget_percentage, 1)
            )
            
        finally:
            conn.close()
    
    def GetMultipleBooksCost(self, book_ids: List[int], region: StudentRegion = None) -> Dict[str, Any]:
        """Get cost estimate for downloading multiple books"""
        region = region or self.default_region
        
        book_costs = []
        total_cost = 0.0
        total_size_mb = 0.0
        
        for book_id in book_ids:
            cost_info = self.GetBookCostEstimate(book_id, region)
            if cost_info:
                book_costs.append(cost_info)
                total_cost += cost_info.estimated_cost_usd
                total_size_mb += cost_info.file_size_mb
        
        # Determine overall warning level
        total_budget_percentage = (total_cost / self.monthly_budget_usd) * 100
        
        if total_cost < 1.00:
            overall_warning = CostWarningLevel.LOW.value
        elif total_cost < 2.50:
            overall_warning = CostWarningLevel.MEDIUM.value
        elif total_cost < 4.00:
            overall_warning = CostWarningLevel.HIGH.value
        else:
            overall_warning = CostWarningLevel.EXTREME.value
        
        return {
            'books': book_costs,
            'total_cost_usd': round(total_cost, 2),
            'total_size_mb': round(total_size_mb, 1),
            'budget_percentage': round(total_budget_percentage, 1),
            'warning_level': overall_warning,
            'region': region.value,
            'remaining_budget': round(self.monthly_budget_usd - self.monthly_spending - total_cost, 2)
        }
    
    def GetDownloadOptions(self, book_id: int, region: StudentRegion = None) -> Dict[str, Any]:
        """Get download options for student choice"""
        cost_info = self.GetBookCostEstimate(book_id, region)
        
        if not cost_info:
            return {'error': 'Book not found'}
        
        # Generate student-friendly options
        options = {
            'book_info': {
                'id': cost_info.book_id,
                'title': cost_info.title,
                'size_mb': cost_info.file_size_mb,
                'cost_usd': cost_info.estimated_cost_usd,
                'warning_level': cost_info.warning_level
            },
            'download_options': [
                {
                    'id': 'download_now',
                    'label': f'Download Now (${cost_info.estimated_cost_usd})',
                    'cost': cost_info.estimated_cost_usd,
                    'immediate': True,
                    'recommended': cost_info.warning_level in ['low', 'medium']
                },
                {
                    'id': 'download_wifi', 
                    'label': 'Wait for WiFi (Free)',
                    'cost': 0.0,
                    'immediate': False,
                    'recommended': cost_info.warning_level in ['high', 'extreme']
                },
                {
                    'id': 'preview_only',
                    'label': 'Read Description Only (Free)',
                    'cost': 0.0,
                    'immediate': True,
                    'recommended': False
                },
                {
                    'id': 'add_to_wishlist',
                    'label': 'Save for Later Download',
                    'cost': 0.0,
                    'immediate': False,
                    'recommended': cost_info.warning_level == 'extreme'
                }
            ],
            'cost_warnings': self._GenerateCostWarnings(cost_info),
            'student_guidance': self._GenerateStudentGuidance(cost_info)
        }
        
        return options
    
    def _GenerateCostWarnings(self, cost_info: BookCostInfo) -> List[str]:
        """Generate appropriate cost warnings for students"""
        warnings = []
        
        if cost_info.warning_level == 'low':
            warnings.append(f"✅ Affordable: Uses {cost_info.budget_percentage}% of monthly budget")
        elif cost_info.warning_level == 'medium':
            warnings.append(f"⚠️ Moderate cost: Uses {cost_info.budget_percentage}% of monthly budget")
        elif cost_info.warning_level == 'high':
            warnings.append(f"🔶 High cost: Uses {cost_info.budget_percentage}% of monthly budget")
            warnings.append("💡 Consider waiting for WiFi to save money")
        else:  # extreme
            warnings.append(f"🚨 Very expensive: Uses {cost_info.budget_percentage}% of monthly budget")
            warnings.append("⚠️ This could exceed your entire monthly data allowance")
            warnings.append("💡 Strongly recommend waiting for WiFi")
        
        # Add budget context
        remaining_budget = self.monthly_budget_usd - self.monthly_spending - cost_info.estimated_cost_usd
        if remaining_budget < 1.0:
            warnings.append(f"📊 Would leave only ${remaining_budget:.2f} for rest of month")
        
        return warnings
    
    def _GenerateStudentGuidance(self, cost_info: BookCostInfo) -> Dict[str, str]:
        """Generate educational guidance for students"""
        if cost_info.warning_level == 'low':
            return {
                'recommendation': 'Good choice for mobile download',
                'explanation': 'This book is affordable and won\'t significantly impact your data budget.',
                'tip': 'You can download several books of this size within your monthly budget.'
            }
        elif cost_info.warning_level == 'medium':
            return {
                'recommendation': 'Consider your monthly budget',
                'explanation': 'This book will use a moderate portion of your data allowance.',
                'tip': 'Make sure you really need this book before downloading.'
            }
        elif cost_info.warning_level == 'high':
            return {
                'recommendation': 'Wait for WiFi if possible',
                'explanation': 'This book is quite expensive for mobile data download.',
                'tip': 'You could download 3-4 smaller books for the same cost.'
            }
        else:  # extreme
            return {
                'recommendation': 'Only download on WiFi',
                'explanation': 'This book would consume most or all of your monthly data budget.',
                'tip': 'Save your mobile data for urgent downloads and smaller resources.'
            }
    
    def RecordDownload(self, book_id: int, actual_cost: float, download_method: str) -> None:
        """Record a download for budget tracking"""
        download_record = {
            'book_id': book_id,
            'cost': actual_cost,
            'method': download_method,
            'timestamp': datetime.now().isoformat(),
            'month': datetime.now().strftime('%Y-%m')
        }
        
        self.download_history.append(download_record)
        
        # Update monthly spending if it's the current month
        current_month = datetime.now().strftime('%Y-%m')
        self.monthly_spending = sum(
            record['cost'] for record in self.download_history 
            if record['month'] == current_month
        )
    
    def GetMonthlySpendingSummary(self) -> Dict[str, Any]:
        """Get summary of student's monthly spending"""
        current_month = datetime.now().strftime('%Y-%m')
        
        month_downloads = [
            record for record in self.download_history 
            if record['month'] == current_month
        ]
        
        total_spent = sum(record['cost'] for record in month_downloads)
        remaining_budget = self.monthly_budget_usd - total_spent
        
        return {
            'month': current_month,
            'total_spent': round(total_spent, 2),
            'remaining_budget': round(remaining_budget, 2),
            'budget_used_percentage': round((total_spent / self.monthly_budget_usd) * 100, 1),
            'downloads_count': len(month_downloads),
            'budget_status': 'good' if remaining_budget > 2.0 else 'caution' if remaining_budget > 0.5 else 'critical'
        }

# Example usage for testing
if __name__ == "__main__":
    print("🎓 Testing Student Book Downloader")
    
    downloader = StudentBookDownloader()
    
    # Test cost estimation for a book
    cost_info = downloader.GetBookCostEstimate(1)  # First book
    if cost_info:
        print(f"\n📖 Book: {cost_info.title}")
        print(f"💾 Size: {cost_info.file_size_mb}MB")
        print(f"💰 Cost: ${cost_info.estimated_cost_usd}")
        print(f"⚠️ Warning: {cost_info.warning_level}")
        print(f"📊 Budget impact: {cost_info.budget_percentage}%")
    
    # Test download options
    options = downloader.GetDownloadOptions(1)
    print(f"\n🎯 Download Options:")
    for option in options['download_options']:
        print(f"  - {option['label']} ({'recommended' if option['recommended'] else 'available'})")
    
    print(f"\n⚠️ Warnings:")
    for warning in options['cost_warnings']:
        print(f"  {warning}")
    
    print(f"\n💡 Guidance: {options['student_guidance']['recommendation']}")
    print(f"   {options['student_guidance']['explanation']}")