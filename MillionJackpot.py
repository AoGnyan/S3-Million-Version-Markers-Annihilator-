import boto3
import botocore
import os
from typing import List, Dict, Optional

# Configuration - Use environment variables or AWS credential chain
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'your_bucket_name')
PREFIX = os.environ.get('S3_PREFIX', 'your_prefix')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Create S3 client using default credential chain
s3 = boto3.client('s3', region_name=AWS_REGION)

def handle_s3_error(e: botocore.exceptions.ClientError, context: str = "") -> str:
    """Centralized S3 error handling"""
    error_code = e.response['Error']['Code']
    error_message = e.response['Error']['Message']
    
    error_handlers = {
        'NoSuchBucket': f"Bucket '{BUCKET_NAME}' does not exist",
        'NoSuchKey': f"Object key does not exist: {context}",
        'AccessDenied': f"Access denied for operation: {context}",
        'InvalidBucketName': f"Invalid bucket name: {BUCKET_NAME}",
    }
    
    message = error_handlers.get(error_code, f"AWS Error ({error_code}): {error_message}")
    print(message)
    return error_code

def get_all_delete_markers() -> List[Dict[str, str]]:
    """Get all delete markers with proper pagination"""
    all_delete_markers = []
    continuation_token = None
    
    while True:
        params = {'Bucket': BUCKET_NAME, 'Prefix': PREFIX}
        
        if continuation_token:
            if 'NextKeyMarker' in continuation_token:
                params['KeyMarker'] = continuation_token['NextKeyMarker']
            if 'NextVersionIdMarker' in continuation_token:
                params['VersionIdMarker'] = continuation_token['NextVersionIdMarker']
        
        try:
            response = s3.list_object_versions(**params)
            
            # Collect latest delete markers
            for delete_marker in response.get('DeleteMarkers', []):
                if delete_marker.get('IsLatest'):
                    all_delete_markers.append({
                        'Key': delete_marker['Key'], 
                        'VersionId': delete_marker['VersionId']
                    })
            
            # Handle pagination
            if response.get('IsTruncated'):
                continuation_token = {}
                if 'NextKeyMarker' in response:
                    continuation_token['NextKeyMarker'] = response['NextKeyMarker']
                if 'NextVersionIdMarker' in response:
                    continuation_token['NextVersionIdMarker'] = response['NextVersionIdMarker']
            else:
                break
                
        except botocore.exceptions.ClientError as e:
            handle_s3_error(e, "listing object versions")
            break
    
    return all_delete_markers

def delete_objects_batch(objects_to_delete: List[Dict[str, str]]) -> bool:
    """Delete objects in batch with fallback to individual deletion"""
    try:
        s3.delete_objects(Bucket=BUCKET_NAME, Delete={'Objects': objects_to_delete})
        print(f"Successfully deleted {len(objects_to_delete)} delete markers")
        return True
    except botocore.exceptions.ClientError as e:
        error_code = handle_s3_error(e, "batch delete")
        
        # Fallback to individual deletion for problematic objects
        if error_code in ['InvalidRequest', 'NoSuchKey']:
            print("Falling back to individual object deletion...")
            success_count = 0
            for obj in objects_to_delete:
                try:
                    s3.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'], VersionId=obj['VersionId'])
                    success_count += 1
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchKey':
                        handle_s3_error(e, f"deleting {obj['Key']}")
            
            print(f"Successfully deleted {success_count}/{len(objects_to_delete)} delete markers individually")
            return success_count > 0
        
        return False

def remove_delete_markers() -> None:
    """Main function to remove delete markers"""
    try:
        print(f"Scanning bucket '{BUCKET_NAME}' with prefix '{PREFIX}' for delete markers...")
        delete_markers = get_all_delete_markers()
        
        if not delete_markers:
            print("No delete markers found.")
            return
        
        print(f"Found {len(delete_markers)} delete markers to remove.")
        
        # Process in batches of 1000 (S3 API limit)
        batch_size = 1000
        total_deleted = 0
        
        for i in range(0, len(delete_markers), batch_size):
            batch = delete_markers[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}: {len(batch)} objects...")
            
            if delete_objects_batch(batch):
                total_deleted += len(batch)
        
        print(f"Operation completed. Total delete markers removed: {total_deleted}")
        
    except botocore.exceptions.ClientError as e:
        handle_s3_error(e, "main operation")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Validate required environment variables
    if BUCKET_NAME == 'your_bucket_name':
        print("Error: Please set S3_BUCKET_NAME environment variable")
        exit(1)
    
    remove_delete_markers()
