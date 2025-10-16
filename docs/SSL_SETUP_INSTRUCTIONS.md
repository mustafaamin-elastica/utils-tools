# SSL Setup Instructions for Project - <project-url>

## Prerequisites ✅
1. Domain `<project-url>` pointing to your EC2 instance's public IP
2. AWS Security Group allowing ports 80 and 443
3. Application running and accessible via HTTP

## Step-by-Step Setup

### 1. Verify Domain Configuration ✅
The nginx configuration is already updated for `<project-url>`
- HTTP server: `server_name <project-url>;`
- HTTPS server: `server_name <project-url>;`
- Certificate paths: `/etc/letsencrypt/live/<project-url>/`

### 2. Initial Deployment (HTTP Only)
First, deploy with HTTP only to ensure everything works:

```bash
# Start services without SSL
docker-compose up -d nginx frontend api db redis

# Verify your site is accessible via HTTP
curl -I http://<project-url>
```

### 3. Obtain SSL Certificates
Run the certbot container to obtain certificates:

```bash
# Start certbot container
docker-compose up -d certbot

# Obtain certificates for <project-url> (replace with your email)
docker-compose exec certbot certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email <project-owner-email> \
  --agree-tos \
  --no-eff-email \
  -d <project-url>
```

### 4. Enable SSL Configuration
After obtaining certificates, restart nginx:

```bash
# Restart nginx with SSL configuration
docker-compose restart nginx

# Verify SSL is working
curl -I https://<project-url>
```

### 5. Set Up Automatic Renewal
Make the renewal script executable and set up cron job:

```bash
# Make script executable
chmod +x scripts/renew-certs.sh

# Add to crontab (run twice daily)
echo "0 12,0 * * * /<project-dir>/infra/scripts/renew-certs.sh >> /var/log/letsencrypt-renewal.log 2>&1" | sudo crontab -
```

### 6. Test Certificate Renewal
Test the renewal process:

```bash
# Test renewal (dry run)
docker-compose exec certbot certbot renew --dry-run

# Test renewal script
./scripts/renew-certs.sh
```

## Security Considerations

### AWS Security Group Settings
Ensure your security group has these inbound rules:
- HTTP (80): 0.0.0.0/0
- HTTPS (443): 0.0.0.0/0
- SSH (22): Your IP only
- Custom ports for your application if needed

### Nginx Security Features Included
- HSTS (HTTP Strict Transport Security)
- X-Frame-Options
- X-Content-Type-Options  
- X-XSS-Protection
- Rate limiting
- Modern SSL/TLS configuration
- OCSP stapling

## Troubleshooting

### Common Issues

1. **Certificate not found**: Ensure `<project-url>` DNS is pointing to your EC2 IP
2. **Permission denied**: Check file permissions and ownership
3. **Rate limiting**: Let's Encrypt has rate limits (5 certs per domain per week)

### Verification Commands

```bash
# Check certificate status
docker-compose exec certbot certbot certificates

# Test SSL configuration
openssl s_client -connect <project-url>:443 -servername <project-url>

# Check nginx configuration
docker-compose exec nginx nginx -t

# View nginx logs
docker-compose logs nginx
```

### Certificate Information
```bash
# View certificate details
openssl x509 -in /etc/letsencrypt/live/<project-url>/fullchain.pem -text -noout
```

## Monitoring
Monitor certificate expiration:
```bash
# Check certificate expiry
echo | openssl s_client -servername <project-url> -connect <project-url>:443 2>/dev/null | openssl x509 -noout -dates
```

## Quick Commands for <project-url>

```bash
# Complete setup in one go:
docker-compose up -d
docker-compose exec certbot certbot certonly --webroot --webroot-path=/var/www/html --email <project-owner-email> --agree-tos --no-eff-email -d <project-url>
docker-compose restart nginx

# Verify everything is working
curl -I https://<project-url>
``` 