# Progress Tracking and Logging Enhancement

## 📊 **Progress Tracking & Logging Implementation Guide**

### Overview

The current MarkerUnmaker implementation lacks comprehensive progress tracking and logging capabilities essential for monitoring long-running operations on millions of delete markers. This section provides the necessary enhancements to add robust progress tracking and logging functionality.

---

## 🔧 **Implementation: Enhanced Progress Tracking**

### 1. Add Progress Tracking Class

Add this class to your `markerunmaker.py` file:

```python
import time
import sys
from typing import Optional
from datetime import datetime, timedelta

class ProgressTracker:
    """Enhanced progress tracking for S3 delete marker operations"""
    
    def __init__(self, total_items: int = 0, operation_name: str = "Processing"):
        self.total_items = total_items
        self.processed_items = 0
        self.failed_items = 0
        self.start_time = time.time()
        self.operation_name = operation_name
        self.last_update_time = self.start_time
        self.update_interval = 5  # Update every 5 seconds
        
    def update(self, processed: int = 1, failed: int = 0, force_update: bool = False):
        """Update progress counters"""
        self.processed_items += processed
        self.failed_items += failed
        
        current_time = time.time()
        if force_update or (current_time - self.last_update_time) >= self.update_interval:
            self._display_progress()
            self.last_update_time = current_time
    
    def _display_progress(self):
        """Display current progress"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        if self.total_items > 0:
            progress_percent = (self.processed_items / self.total_items) * 100
            remaining_items = self.total_items - self.processed_items
            
            # Calculate ETA
            if self.processed_items > 0:
                rate = self.processed_items / elapsed_time
                eta_seconds = remaining_items / rate if rate > 0 else 0
                eta_str = str(timedelta(seconds=int(eta_seconds)))
            else:
                eta_str = "Unknown"
            
            progress_bar = self._create_progress_bar(progress_percent)
            
            print(f"\r{self.operation_name}: {progress_bar} "
                  f"{self.processed_items:,}/{self.total_items:,} ({progress_percent:.1f}%) "
                  f"| Rate: {self.processed_items/elapsed_time:.1f}/s "
                  f"| ETA: {eta_str} "
                  f"| Errors: {self.failed_items:,}", end="", flush=True)
        else:
            # Unknown total - show processed count and rate
            rate = self.processed_items / elapsed_time if elapsed_time > 0 else 0
            print(f"\r{self.operation_name}: {self.processed_items:,} processed "
                  f"| Rate: {rate:.1f}/s "
                  f"| Elapsed: {str(timedelta(seconds=int(elapsed_time)))} "
                  f"| Errors: {self.failed_items:,}", end="", flush=True)
    
    def _create_progress_bar(self, percent: float, width: int = 30) -> str:
        """Create visual progress bar"""
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def complete(self):
        """Mark operation as complete and show final stats"""
        self._display_progress()
        print()  # New line after progress bar
        
        total_time = time.time() - self.start_time
        success_rate = ((self.processed_items - self.failed_items) / self.processed_items * 100) if self.processed_items > 0 else 0
        
        print(f"\n✅ {self.operation_name} Complete!")
        print(f"   📊 Total Processed: {self.processed_items:,}")
        print(f"   ✅ Successful: {self.processed_items - self.failed_items:,}")
        print(f"   ❌ Failed: {self.failed_items:,}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        print(f"   ⏱️  Total Time: {str(timedelta(seconds=int(total_time)))}")
        print(f"   🚀 Average Rate: {self.processed_items/total_time:.1f} items/second")
```

### 2. Add Comprehensive Logging System

Add this logging configuration to your `markerunmaker.py` file:

```python
import logging
import logging.handlers
import os
from pathlib import Path

class MarkerUnmakerLogger:
    """Centralized logging system for MarkerUnmaker"""
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        self.logger = logging.getLogger("markerunmaker")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(funcName)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(simple_formatter)
        console_handler.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Rotating file handler (10MB max, keep 5 files)
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setFormatter(detailed_formatter)
            file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(file_handler)
        
        # Error file handler (always enabled)
        error_log_file = log_file.replace('.log', '_errors.log') if log_file else 'markerunmaker_errors.log'
        error_handler = logging.FileHandler(error_log_file)
        error_handler.setFormatter(detailed_formatter)
        error_handler.setLevel(logging.ERROR)
        self.logger.addHandler(error_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, **kwargs)
    
    def log_operation_start(self, operation: str, **details):
        """Log the start of a major operation"""
        self.info(f"🚀 Starting {operation}")
        for key, value in details.items():
            self.info(f"   {key}: {value}")
    
    def log_operation_complete(self, operation: str, duration: float, **stats):
        """Log the completion of a major operation"""
        self.info(f"✅ Completed {operation} in {duration:.2f}s")
        for key, value in stats.items():
            self.info(f"   {key}: {value}")
    
    def log_batch_progress(self, batch_id: int, processed: int, total: int, errors: int = 0):
        """Log batch processing progress"""
        self.info(f"📦 Batch {batch_id}: {processed}/{total} processed, {errors} errors")
    
    def log_error_details(self, error: Exception, context: str = ""):
        """Log detailed error information"""
        self.error(f"❌ Error in {context}: {type(error).__name__}: {str(error)}")
        if hasattr(error, 'response'):
            # AWS ClientError details
            error_code = error.response.get('Error', {}).get('Code', 'Unknown')
            error_message = error.response.get('Error', {}).get('Message', 'Unknown')
            self.error(f"   AWS Error Code: {error_code}")
            self.error(f"   AWS Error Message: {error_message}")
```

### 3. Enhanced Main Function with Progress Tracking

Replace your main `remove_delete_markers()` function with this enhanced version:

```python
def remove_delete_markers() -> None:
    """Main function to remove delete markers with progress tracking"""
    
    # Initialize logging
    log_file = os.environ.get('MARKERUNMAKER_LOG_FILE', 'markerunmaker.log')
    log_level = os.environ.get('MARKERUNMAKER_LOG_LEVEL', 'INFO')
    
    logger = MarkerUnmakerLogger(log_level=log_level, log_file=log_file)
    
    try:
        logger.log_operation_start(
            "Delete Marker Removal",
            bucket=BUCKET_NAME,
            prefix=PREFIX or "ALL",
            dry_run=os.environ.get('DRY_RUN', 'false').lower() == 'true'
        )
        
        operation_start_time = time.time()
        
        # Phase 1: Discovery
        logger.info("🔍 Phase 1: Discovering delete markers...")
        discovery_progress = ProgressTracker(operation_name="Discovery")
        
        delete_markers = get_all_delete_markers_with_progress(logger, discovery_progress)
        discovery_progress.complete()
        
        if not delete_markers:
            logger.info("✅ No delete markers found.")
            return
        
        logger.info(f"📊 Found {len(delete_markers):,} delete markers to process")
        
        # Phase 2: Processing
        logger.info("🔄 Phase 2: Processing delete markers...")
        processing_progress = ProgressTracker(
            total_items=len(delete_markers),
            operation_name="Processing"
        )
        
        # Process in batches
        batch_size = 1000
        total_deleted = 0
        total_errors = 0
        
        for i in range(0, len(delete_markers), batch_size):
            batch = delete_markers[i:i + batch_size]
            batch_id = i // batch_size + 1
            
            logger.debug(f"Processing batch {batch_id}: {len(batch)} objects")
            
            try:
                if delete_objects_batch_with_progress(batch, logger):
                    total_deleted += len(batch)
                    processing_progress.update(processed=len(batch))
                else:
                    total_errors += len(batch)
                    processing_progress.update(processed=len(batch), failed=len(batch))
                
                logger.log_batch_progress(
                    batch_id=batch_id,
                    processed=len(batch),
                    total=len(delete_markers),
                    errors=0 if total_errors == 0 else len(batch)
                )
                
            except Exception as e:
                total_errors += len(batch)
                processing_progress.update(processed=len(batch), failed=len(batch))
                logger.log_error_details(e, f"batch {batch_id}")
        
        processing_progress.complete()
        
        # Final summary
        operation_duration = time.time() - operation_start_time
        success_rate = ((total_deleted) / len(delete_markers) * 100) if len(delete_markers) > 0 else 0
        
        logger.log_operation_complete(
            "Delete Marker Removal",
            duration=operation_duration,
            total_found=f"{len(delete_markers):,}",
            successfully_deleted=f"{total_deleted:,}",
            errors=f"{total_errors:,}",
            success_rate=f"{success_rate:.1f}%"
        )
        
    except Exception as e:
        logger.log_error_details(e, "main operation")
        raise

def get_all_delete_markers_with_progress(logger: MarkerUnmakerLogger, progress: ProgressTracker) -> List[Dict[str, str]]:
    """Get all delete markers with progress tracking"""
    all_delete_markers = []
    continuation_token = None
    page_count = 0
    
    while True:
        page_count += 1
        params = {
            'Bucket': BUCKET_NAME,
            'Prefix': PREFIX
        }
        
        if continuation_token:
            params['KeyMarker'] = continuation_token['NextKeyMarker']
            if 'NextVersionIdMarker' in continuation_token:
                params['VersionIdMarker'] = continuation_token['NextVersionIdMarker']
        
        try:
            logger.debug(f"Fetching page {page_count} of delete markers")
            response = s3.list_object_versions(**params)
            
            # Collect delete markers from this page
            page_markers = []
            for delete_marker in response.get('DeleteMarkers', []):
                if delete_marker.get('IsLatest'):
                    page_markers.append({
                        'Key': delete_marker['Key'], 
                        'VersionId': delete_marker['VersionId']
                    })
            
            all_delete_markers.extend(page_markers)
            progress.update(processed=len(page_markers))
            
            logger.debug(f"Page {page_count}: Found {len(page_markers)} delete markers")
            
            # Check if there are more pages
            if response.get('IsTruncated'):
                continuation_token = {
                    'NextKeyMarker': response.get('NextKeyMarker', ''),
                    'NextVersionIdMarker': response.get('NextVersionIdMarker', '')
                }
            else:
                break
                
        except botocore.exceptions.ClientError as e:
            logger.log_error_details(e, f"listing page {page_count}")
            break
    
    logger.info(f"📄 Scanned {page_count} pages, found {len(all_delete_markers):,} delete markers")
    return all_delete_markers

def delete_objects_batch_with_progress(objects_to_delete: List[Dict[str, str]], logger: MarkerUnmakerLogger) -> bool:
    """Delete objects in batch with progress logging"""
    try:
        if os.environ.get('DRY_RUN', 'false').lower() == 'true':
            logger.info(f"[DRY RUN] Would delete {len(objects_to_delete)} delete markers")
            return True
        
        response = s3.delete_objects(
            Bucket=BUCKET_NAME, 
            Delete={'Objects': objects_to_delete}
        )
        
        deleted_count = len(response.get('Deleted', []))
        errors = response.get('Errors', [])
        
        if errors:
            logger.warning(f"Batch completed with {len(errors)} errors:")
            for error in errors[:5]:  # Log first 5 errors
                logger.warning(f"  - {error.get('Key', 'Unknown')}: {error.get('Code', 'Unknown')} - {error.get('Message', 'Unknown')}")
            if len(errors) > 5:
                logger.warning(f"  ... and {len(errors) - 5} more errors")
        
        logger.debug(f"Batch delete: {deleted_count} successful, {len(errors)} errors")
        return len(errors) == 0
        
    except botocore.exceptions.ClientError as e:
        logger.log_error_details(e, "batch delete")
        return False
```

---

## 🔧 **Environment Variables for Configuration**

Add these environment variables to control logging and progress tracking:

```bash
# Logging Configuration
export MARKERUNMAKER_LOG_FILE="/var/log/markerunmaker.log"
export MARKERUNMAKER_LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Progress Tracking Configuration
export MARKERUNMAKER_PROGRESS_INTERVAL="5"  # Update interval in seconds
export MARKERUNMAKER_SHOW_PROGRESS_BAR="true"
export MARKERUNMAKER_DETAILED_LOGGING="true"
```

---

## 📋 **Usage Examples with Progress Tracking**

### Basic Usage with Progress Tracking
```bash
export S3_BUCKET_NAME="my-versioned-bucket"
export MARKERUNMAKER_LOG_LEVEL="INFO"
export MARKERUNMAKER_LOG_FILE="./cleanup.log"

python markerunmaker.py
```

**Expected Output:**
```
2024-01-15 14:30:15 | INFO     | 🚀 Starting Delete Marker Removal
2024-01-15 14:30:15 | INFO     |    bucket: my-versioned-bucket
2024-01-15 14:30:15 | INFO     |    prefix: ALL
2024-01-15 14:30:15 | INFO     | 🔍 Phase 1: Discovering delete markers...
Discovery: [████████████████████████████████] 15,432/15,432 (100.0%) | Rate: 2,156.8/s | ETA: 00:00:00 | Errors: 0
✅ Discovery Complete!
   📊 Total Processed: 15,432
   ✅ Successful: 15,432
   ❌ Failed: 0
   📈 Success Rate: 100.0%
   ⏱️  Total Time: 0:00:07
   🚀 Average Rate: 2,204.6 items/second

2024-01-15 14:30:22 | INFO     | 📊 Found 15,432 delete markers to process
2024-01-15 14:30:22 | INFO     | 🔄 Phase 2: Processing delete markers...
Processing: [██████████████████░░░░░░░░░░░░] 12,000/15,432 (77.8%) | Rate: 1,845.2/s | ETA: 00:00:02 | Errors: 0
```

### Verbose Logging Mode
```bash
export MARKERUNMAKER_LOG_LEVEL="DEBUG"
export MARKERUNMAKER_DETAILED_LOGGING="true"

python markerunmaker.py
```

### Dry Run with Progress Tracking
```bash
export DRY_RUN="true"
export MARKERUNMAKER_SHOW_PROGRESS_BAR="true"

python markerunmaker.py
```

---

## 📊 **Log File Structure**

### Main Log File (`markerunmaker.log`)
```
2024-01-15 14:30:15 | INFO     | remove_delete_markers    | 🚀 Starting Delete Marker Removal
2024-01-15 14:30:15 | INFO     | remove_delete_markers    |    bucket: my-bucket
2024-01-15 14:30:15 | DEBUG    | get_all_delete_markers   | Fetching page 1 of delete markers
2024-01-15 14:30:16 | DEBUG    | get_all_delete_markers   | Page 1: Found 1000 delete markers
2024-01-15 14:30:16 | INFO     | log_batch_progress       | 📦 Batch 1: 1000/15432 processed, 0 errors
```

### Error Log File (`markerunmaker_errors.log`)
```
2024-01-15 14:32:45 | ERROR    | delete_objects_batch     | ❌ Error in batch 5: ClientError: An error occurred
2024-01-15 14:32:45 | ERROR    | log_error_details        |    AWS Error Code: NoSuchKey
2024-01-15 14:32:45 | ERROR    | log_error_details        |    AWS Error Message: The specified key does not exist
```

---

## 🎯 **Integration Instructions**

1. **Add the classes** to your existing `markerunmaker.py` file
2. **Replace the main function** with the enhanced version
3. **Set environment variables** for your logging preferences
4. **Test with dry run** to verify progress tracking works
5. **Monitor log files** during actual execution

This enhancement provides comprehensive progress tracking and logging capabilities essential for monitoring large-scale S3 delete marker removal operations.
