# Nginx Log Rotation Setup Guide

This guide provides step-by-step instructions for setting up automatic log rotation for nginx logs in the Project Docker environment.

## Overview

Without log rotation, nginx access and error logs will grow indefinitely, potentially consuming significant disk space. This guide implements a host-based logrotate solution that:

- Rotates logs daily
- Keeps 30 days of log history
- Compresses old log files
- Automatically signals nginx to reopen log files
- Runs automatically via cron

## Current Log Configuration

Your nginx logs are currently configured as:
- **Container Path**: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`
- **Host Path**: `/<project-dir>/logs/nginx/`
- **Docker Mount**: `./logs/nginx:/var/log/nginx` (in docker-compose.yml)

## Implementation Steps

### Step 1: Create Logrotate Configuration

Create the logrotate configuration file:

```bash
sudo nano /etc/logrotate.d/nginx-<project-name>
```

Add the following configuration:

```bash
/<project-dir>/logs/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    su ubuntu ubuntu
    create 644 ubuntu ubuntu
    sharedscripts
    postrotate
        docker exec <project-ngnix-container-name>-nginx-prod nginx -s reopen >/dev/null 2>&1 || true
    endscript
}
```

### Step 2: Verify File Permissions

Check current log file ownership:

```bash
ls -la /<project-dir>/logs/nginx/
```

If needed, adjust the `create` line in the logrotate config to match the actual file ownership.

### Step 3: Test the Configuration

**Dry run test** (shows what would happen without executing):

```bash
sudo logrotate -d /etc/logrotate.d/nginx-<project-name>
```

Expected output should show the rotation plan without errors.

**Force a test rotation**:

```bash
sudo logrotate -f /etc/logrotate.d/nginx-<project-name>
```

### Step 4: Verify the Rotation Worked

Check the log directory:

```bash
ls -la /<project-dir>/logs/nginx/
```

You should see:
- New empty `access.log` and `error.log` files
- Rotated files like `access.log.1` and `error.log.1`

### Step 5: Test Nginx Log Reopening

Generate some traffic and verify logging:

```bash
# Generate traffic
curl -I https://<project-url>

# Check new logs are being written
tail -f /<project-dir>/logs/nginx/access.log
```

## Configuration Options Explained

| Option | Description |
|--------|-------------|
| `daily` | Rotate logs once per day |
| `rotate 30` | Keep 30 rotated log files (30 days history) |
| `compress` | Compress rotated files with gzip |
| `delaycompress` | Don't compress the most recent rotated file |
| `missingok` | Don't error if log file is missing |
| `notifempty` | Don't rotate empty log files |
| `create 644 root root` | Create new files with specified permissions/ownership |
| `sharedscripts` | Run postrotate script only once for all matched files |

## Customization Options

### Different Rotation Frequencies

```bash
# Weekly rotation
weekly

# Monthly rotation  
monthly

# Size-based rotation (when file reaches 100MB)
size 100M

# Combined: daily OR when size reaches 50MB
daily
size 50M
```

### Different Retention Policies

```bash
# Keep 90 days of logs
rotate 90

# Keep 1 year of weekly logs
weekly
rotate 52

# Keep 6 months of logs regardless of rotation count
maxage 180
```

### Enhanced Configuration Example

```bash
/<project-dir>/logs/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    sharedscripts
    dateext
    dateformat -%Y%m%d
    maxage 365
    size 100M
    
    prerotate
        echo "$(date): Starting nginx log rotation" >> /var/log/logrotate.log
    endprerotate
    
    postrotate
        docker exec <project-nginx-container-name>-nginx-prod nginx -s reopen >/dev/null 2>&1 || true
        echo "$(date): Nginx log rotation completed" >> /var/log/logrotate.log
    endrotate
}
```

## Monitoring and Maintenance

### Check Logrotate Status

```bash
# View logrotate status
sudo cat /var/lib/logrotate/status | grep nginx

# Check logrotate service logs
sudo journalctl -u logrotate

# Check cron logs for logrotate
sudo journalctl -u cron | grep logrotate
```

### Manual Rotation Commands

```bash
# Force immediate rotation
sudo logrotate -f /etc/logrotate.d/nginx-<project-name>

# Verbose dry run
sudo logrotate -d -v /etc/logrotate.d/nginx-<project-name>

# Force rotation with detailed output
sudo logrotate -f -v /etc/logrotate.d/nginx-<project-name>
```

### Monitor Disk Usage

```bash
# Check log directory size
du -sh /<project-dir>/logs/nginx/

# List files by size
ls -lah /<project-dir>/logs/nginx/

# Check available disk space
df -h
```

## Expected File Structure

After logrotate runs for several days, your log directory will look like:

```
/<project-dir>/logs/nginx/
├── access.log              # Current active log file
├── access.log.1            # Yesterday's log (uncompressed due to delaycompress)
├── access.log.2.gz         # 2 days ago (compressed)
├── access.log.3.gz         # 3 days ago (compressed)
├── access.log.4.gz         # 4 days ago (compressed)
├── ...
├── access.log.30.gz        # 30 days ago (compressed)
├── error.log               # Current active error log
├── error.log.1             # Yesterday's error log (uncompressed)
├── error.log.2.gz          # 2 days ago (compressed)
├── error.log.3.gz          # 3 days ago (compressed)
└── ...
```

With the enhanced configuration using `dateext`, it would look like:

```
/<project-dir>/logs/nginx/
├── access.log                    # Current active log file
├── access.log-20251002           # Yesterday's log (uncompressed)
├── access.log-20251001.gz        # 2 days ago (compressed)
├── access.log-20250930.gz        # 3 days ago (compressed)
├── ...
├── error.log                     # Current active error log
├── error.log-20251002            # Yesterday's error log
├── error.log-20251001.gz         # 2 days ago (compressed)
└── ...
```

The dated format makes it easier to identify specific log files by date.

