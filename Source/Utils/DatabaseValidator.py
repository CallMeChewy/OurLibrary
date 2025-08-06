# File: DatabaseValidator.py
# Path: Source/Utils/DatabaseValidator.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 21:45PM
"""
Comprehensive database validation and repair utilities.
Ensures database integrity across different deployment environments.
"""

import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class DatabaseValidator:
    """Validate and repair database files"""
    
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.issues = []
        self.repair_log = []
    
    def ValidateComplete(self) -> Dict[str, any]:
        """Run complete database validation"""
        validation_result = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'stats': {},
            'repair_suggestions': []
        }
        
        try:
            # Basic existence check
            if not self.db_path.exists():
                validation_result['valid'] = False
                validation_result['issues'].append('Database file does not exist')
                return validation_result
            
            # Size check
            size_mb = self.db_path.stat().st_size / 1024 / 1024
            if size_mb < 0.01:  # Less than 10KB
                validation_result['valid'] = False
                validation_result['issues'].append(f'Database too small: {size_mb:.2f} MB')
            
            # SQLite integrity
            integrity_ok, integrity_msg = self.CheckIntegrity()
            if not integrity_ok:
                validation_result['valid'] = False
                validation_result['issues'].append(f'Integrity check failed: {integrity_msg}')
            
            # Schema validation
            schema_ok, schema_issues = self.ValidateSchema()
            if not schema_ok:
                validation_result['valid'] = False
                validation_result['issues'].extend(schema_issues)
            
            # Data validation
            data_stats = self.ValidateData()
            validation_result['stats'] = data_stats
            
            if data_stats['total_records'] == 0:
                validation_result['warnings'].append('Database contains no records')
            elif data_stats['total_records'] < 10:
                validation_result['warnings'].append(f'Database has very few records: {data_stats["total_records"]}')
            
            # Repair suggestions
            if not validation_result['valid']:
                validation_result['repair_suggestions'] = self.GenerateRepairSuggestions(validation_result)
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['issues'].append(f'Validation error: {str(e)}')
        
        return validation_result
    
    def CheckIntegrity(self) -> Tuple[bool, str]:
        """Check SQLite database integrity"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] == 'ok':
                return True, 'OK'
            else:
                return False, result[0] if result else 'Unknown error'
                
        except Exception as e:
            return False, str(e)
    
    def ValidateSchema(self) -> Tuple[bool, List[str]]:
        """Validate database schema"""
        issues = []
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Required tables
            required_tables = ['books', 'categories', 'subjects']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                issues.append(f'Missing required tables: {", ".join(missing_tables)}')
            
            # Validate books table structure
            if 'books' in tables:
                cursor.execute("PRAGMA table_info(books)")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                required_columns = ['id', 'title', 'author']
                missing_columns = [col for col in required_columns if col not in column_names]
                
                if missing_columns:
                    issues.append(f'Books table missing columns: {", ".join(missing_columns)}')
            
            conn.close()
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f'Schema validation error: {str(e)}']
    
    def ValidateData(self) -> Dict[str, int]:
        """Validate database data and return statistics"""
        stats = {
            'total_records': 0,
            'books_count': 0,
            'categories_count': 0,
            'subjects_count': 0
        }
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Count records in each table
            tables = ['books', 'categories', 'subjects']
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    stats[f'{table}_count'] = count
                    stats['total_records'] += count
                except:
                    pass  # Table might not exist
            
            conn.close()
            
        except Exception:
            pass  # Return empty stats
        
        return stats
    
    def GenerateRepairSuggestions(self, validation_result: Dict) -> List[str]:
        """Generate repair suggestions based on validation results"""
        suggestions = []
        
        for issue in validation_result['issues']:
            if 'does not exist' in issue:
                suggestions.append('Initialize database from Google Drive or create minimal database')
            elif 'too small' in issue:
                suggestions.append('Database appears to be placeholder - sync from Google Drive')
            elif 'Integrity check failed' in issue:
                suggestions.append('Database corrupted - restore from backup or re-sync')
            elif 'Missing required tables' in issue:
                suggestions.append('Database schema incomplete - reinitialize database')
        
        return suggestions

def ValidateDatabase(db_path: Path) -> Dict[str, any]:
    """Quick database validation function"""
    validator = DatabaseValidator(db_path)
    return validator.ValidateComplete()
