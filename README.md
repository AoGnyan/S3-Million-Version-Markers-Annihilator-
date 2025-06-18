# MarkerUnmaker Documentation

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [API Reference](#api-reference)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Security Considerations](#security-considerations)
12. [Contributing](#contributing)
13. [License](#license)

---

## Overview

**MarkerUnmaker** is a Python utility designed to efficiently remove delete markers from Amazon S3 versioned buckets. Delete markers are created when objects are deleted in versioned S3 buckets, and over time, these can accumulate and impact storage costs and bucket performance.

### What are Delete Markers?

Delete markers are placeholder objects created when you delete an object in a versioned S3 bucket. They don't contain actual data but mark the object as "deleted" while preserving previous versions. Removing unnecessary delete markers can:

- Reduce storage costs
- Improve bucket listing performance
- Clean up bucket organization
- Optimize backup and replication processes

---

## Features

- ✅ **Batch Processing**: Efficiently processes up to 1000 delete markers per API call
- ✅ **Pagination Support**: Handles buckets with unlimited numbers of objects
- ✅ **Robust Error Handling**: Graceful handling of AWS API errors with fallback mechanisms
- ✅ **Security First**: Supports AWS credential best practices
- ✅ **Prefix Filtering**: Target specific object prefixes within buckets
- ✅ **Progress Tracking**: Real-time feedback on processing status
- ✅ **Dry Run Mode**: Preview operations before execution
- ✅ **Enterprise Ready**: Suitable for production environments

---

## Prerequisites

### System Requirements
- Python 3.7 or higher
- AWS CLI configured (recommended) or valid AWS credentials
- Network access to AWS S3 endpoints

### AWS Requirements
- Valid AWS account with S3 access
- IAM permissions for S3 operations (see [Security Considerations](#security-considerations))
- S3 bucket with versioning enabled

### Required Python Packages
```
boto3>=1.26.0
botocore>=1.29.0
```

---

## Installation

### Option 1: Direct Download
```bash
# Download the script
curl -O https://raw.githubusercontent.com/AoGnyan/S3-Million-Version-Markers-Annihilator-/refs/heads/main/markerunmaker.py

# Install dependencies
pip install boto3 botocore
```

### Option 2: Clone Repository
```bash
git clone https://github.com/AoGnyan/S3-Million-Version-Markers-Annihilator-.git
cd markerunmaker
pip install -r requirements.txt
```

### Option 3: Package Installation
```bash
pip install markerunmaker
```

---

## Configuration

### Environment Variables

The tool uses environment variables for configuration, following AWS best practices:

```bash
# Required
export S3_BUCKET_NAME="your-bucket-name"

# Optional
export S3_PREFIX="path/to/objects/"          # Default: "" (all objects)
export AWS_REGION="us-west-2"                # Default: "us-east-1"
export AWS_PROFILE="your-aws-profile"        # Default: "default"
```

### Configuration File (Optional)

Create a `config.json` file for advanced configuration:

```json
{
  "bucket_name": "your-bucket-name",
  "prefix": "logs/2023/",
  "region": "us-west-2",
  "batch_size": 1000,
  "dry_run": false,
  "verbose": true
}
```

### AWS Credentials Setup

#### Method 1: AWS CLI (Recommended)
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

#### Method 2: Environment Variables
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

#### Method 3: IAM Roles (For EC2/Lambda)
No additional configuration needed when running on AWS services with attached IAM roles.

---

## Usage

### Basic Usage

```bash
# Set required environment variables
export S3_BUCKET_NAME="my-versioned-bucket"

# Run MarkerUnmaker
python markerunmaker.py
```

### Advanced Usage Examples

#### Target Specific Prefix
```bash
export S3_BUCKET_NAME="my-bucket"
export S3_PREFIX="logs/2023/"
python markerunmaker.py
```

#### Dry Run Mode
```bash
export S3_BUCKET_NAME="my-bucket"
export DRY_RUN="true"
python markerunmaker.py
```

#### Verbose Output
```bash
export S3_BUCKET_NAME="my-bucket"
export VERBOSE="true"
python markerunmaker.py
```

### Command Line Interface

```bash
# Basic usage
python markerunmaker.py --bucket my-bucket

# With options
python markerunmaker.py \
  --bucket my-bucket \
  --prefix logs/2023/ \
  --region us-west-2 \
  --dry-run \
  --verbose

# Using configuration file
python markerunmaker.py --config config.json
```

---

## API Reference

### Core Functions

#### `remove_delete_markers()`
Main entry point for delete marker removal.

**Parameters:** None (uses environment variables)
**Returns:** None
**Raises:** `botocore.exceptions.ClientError` for AWS API errors

#### `get_all_delete_markers() -> List[Dict[str, str]]`
Retrieves all delete markers from the specified bucket and prefix.

**Returns:** List of dictionaries containing:
- `Key`: Object key
- `VersionId`: Version ID of the delete marker

**Example:**
```python
delete_markers = get_all_delete_markers()
print(f"Found {len(delete_markers)} delete markers")
```

#### `delete_objects_batch(objects_to_delete: List[Dict[str, str]]) -> bool`
Deletes a batch of objects with fallback to individual deletion.

**Parameters:**
- `objects_to_delete`: List of objects to delete

**Returns:** `True` if successful, `False` otherwise

#### `handle_s3_error(e: ClientError, context: str = "") -> str`
Centralized error handling for S3 operations.

**Parameters:**
- `e`: The ClientError exception
- `context`: Additional context for the error

**Returns:** AWS error code string

---

## Error Handling

### Common Error Scenarios

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `NoSuchBucket` | Bucket doesn't exist | Verify bucket name and region |
| `AccessDenied` | Insufficient permissions | Check IAM policies |
| `NoSuchKey` | Object key not found | Normal during concurrent operations |
| `InvalidBucketName` | Invalid bucket name format | Use valid S3 bucket naming |
| `BucketNotEmpty` | Bucket contains objects | Expected for non-empty buckets |

### Error Recovery

MarkerUnmaker implements automatic error recovery:

1. **Batch Failures**: Falls back to individual object deletion
2. **Transient Errors**: Implements exponential backoff retry
3. **Permission Errors**: Provides clear guidance for resolution
4. **Network Issues**: Graceful handling with retry mechanisms

### Logging

Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

###Progress Tracking enhancement
You can use the [following guide](https://github.com/AoGnyan/S3-Million-Version-Markers-Annihilator-/blob/main/Progress%20Tracking%20and%20Logging%20Enhancement.md) to add progress tracking and logging into the code 


---

## Best Practices

### Before Running

1. **Backup Important Data**: Ensure you have backups of critical objects
2. **Test with Small Prefix**: Start with a limited scope using prefixes
3. **Use Dry Run**: Always test with dry run mode first
4. **Check Permissions**: Verify IAM permissions before execution
5. **Monitor Costs**: Understand potential cost implications

### During Execution

1. **Monitor Progress**: Watch console output for progress updates
2. **Check CloudWatch**: Monitor S3 API metrics during execution
3. **Avoid Concurrent Operations**: Don't run multiple instances simultaneously
4. **Network Stability**: Ensure stable internet connection for large operations

### After Execution

1. **Verify Results**: Check bucket contents to confirm expected results
2. **Monitor Costs**: Track storage cost changes after cleanup
3. **Document Changes**: Keep records of cleanup operations
4. **Update Lifecycle Policies**: Consider implementing lifecycle rules

---

## Troubleshooting

### Common Issues

#### Issue: "Bucket not found" Error
```
Solution: Verify bucket name and region configuration
- Check S3_BUCKET_NAME environment variable
- Ensure bucket exists in the specified region
- Verify AWS credentials have access to the bucket
```

#### Issue: "Access Denied" Error
```
Solution: Check IAM permissions
Required permissions:
- s3:ListBucketVersions
- s3:DeleteObject
- s3:DeleteObjectVersion
```

#### Issue: MarkerUnmaker Runs But No Delete Markers Found
```
Solution: Verify bucket has versioning enabled and contains delete markers
- Check bucket versioning status
- Verify objects have been deleted (creating delete markers)
- Check if prefix filter is too restrictive
```

#### Issue: Slow Performance
```
Solution: Optimize execution
- Use more specific prefixes to reduce scope
- Check network connectivity
- Consider running from AWS EC2 for better performance
```

### Debug Mode

Enable debug mode for detailed troubleshooting:

```bash
export DEBUG="true"
export VERBOSE="true"
python markerunmaker.py
```

### Getting Help

1. Check the [troubleshooting section](#troubleshooting)
2. Review AWS CloudTrail logs for API call details
3. Enable debug logging for detailed error information
4. Consult AWS S3 documentation for specific error codes

---

## Security Considerations

### IAM Policy Template

Create a minimal IAM policy for MarkerUnmaker:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucketVersions",
                "s3:DeleteObject",
                "s3:DeleteObjectVersion"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

### Security Best Practices

1. **Principle of Least Privilege**: Grant only necessary permissions
2. **Use IAM Roles**: Prefer IAM roles over access keys when possible
3. **Rotate Credentials**: Regularly rotate AWS access keys
4. **Audit Access**: Monitor CloudTrail logs for API usage
5. **Secure Storage**: Never commit credentials to version control
6. **Network Security**: Use VPC endpoints for enhanced security

### Credential Management

#### ✅ Recommended Methods
- AWS IAM roles (for EC2/Lambda)
- AWS CLI profiles
- Environment variables (for local development)
- AWS SSO integration

#### ❌ Avoid
- Hardcoded credentials in source code
- Sharing credentials via email or chat
- Using root account credentials
- Storing credentials in version control

---

## Performance Optimization

### Batch Size Tuning

```python
# Adjust batch size based on your needs
BATCH_SIZE = 1000  # Maximum allowed by S3 API
# For smaller operations, reduce to minimize impact:
BATCH_SIZE = 100   # More granular progress updates
```

### Parallel Processing

For very large buckets, consider parallel processing:

```python
# Example: Process different prefixes in parallel
prefixes = ['logs/2023/01/', 'logs/2023/02/', 'logs/2023/03/']
# Use threading or multiprocessing to handle prefixes concurrently
```

### Monitoring and Metrics

Track performance metrics:

```python
import time
start_time = time.time()
# ... processing ...
end_time = time.time()
print(f"Processing completed in {end_time - start_time:.2f} seconds")
```

---

## Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup

```bash
git clone https://github.com/your-repo/markerunmaker.git
cd markerunmaker
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
```

### Code Standards

- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include docstrings for public functions
- Write unit tests for new features
- Update documentation for changes

### Testing

```bash
# Run unit tests
python -m pytest tests/

# Run integration tests (requires AWS credentials)
python -m pytest tests/integration/

# Run linting
flake8 markerunmaker.py
mypy markerunmaker.py
```

### Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

---

## License

This project is licensed under the MIT GNU Affero General Public License v3.0 - see the [LICENSE](https://github.com/AoGnyan/S3-Million-Version-Markers-Annihilator-/blob/main/LICENSE) file for details.

```
MIT License

Copyright (c) 2024 MarkerUnmaker Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Support and Community

### Getting Support

- 📖 **Documentation**: This comprehensive guide
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/AoGnyan/S3-Million-Version-Markers-Annihilator-/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/AoGnyan/S3-Million-Version-Markers-Annihilator-/discussions)
- 📧 **Email Support**: partnerldm@gmail.com



## Quick Start Guide

### 1. Install MarkerUnmaker
```bash
pip install boto3 botocore
curl -O https://raw.githubusercontent.com/your-repo/markerunmaker/main/markerunmaker.py
```

### 2. Configure AWS Credentials
```bash
aws configure
```

### 3. Set Environment Variables
```bash
export S3_BUCKET_NAME="your-bucket-name"
export S3_PREFIX="optional/prefix/"  # Optional
```

### 4. Test with Dry Run
```bash
export DRY_RUN="true"
python markerunmaker.py
```

### 5. Run MarkerUnmaker
```bash
unset DRY_RUN  # Remove dry run mode
python markerunmaker.py
```

---

## Acknowledgments

- AWS SDK for Python (Boto3) team
- AWS documentation team for excellent API documentation

---

**⚠️ Important Notice**: MarkerUnmaker permanently removes delete markers from your S3 bucket. Always test in a non-production environment first and ensure you have appropriate backups before running in production.

**🎯 MarkerUnmaker Mission**: Simplifying S3 bucket maintenance by efficiently removing unnecessary delete markers, reducing costs, and improving performance.
