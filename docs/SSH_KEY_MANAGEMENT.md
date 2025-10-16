# SSH Key Management for EC2 and GitHub Actions

## 🔑 Using Existing AWS Key Pair

### If you have the original .pem file:
```bash
# Convert .pem to public key (for reference)
ssh-keygen -y -f your-key.pem > public_key.pub

# The .pem file content goes directly into GitHub Secret EC2_SSH_KEY
cat your-key.pem
```

### If you lost the .pem file:
- Use the key pair name from AWS Console → EC2 → Key Pairs
- Download a new .pem file from AWS Console (if possible)
- Or create a new key pair (see below)

## 🆕 Creating New Key Pair

### Generate new SSH key pair:
```bash
# Generate new key pair
ssh-keygen -t rsa -b 4096 -f ~/.ssh/ec2-github-key

# Set proper permissions
chmod 600 ~/.ssh/ec2-github-key
chmod 644 ~/.ssh/ec2-github-key.pub
```

### Generate a new .pem file directly:
```bash
# Generate RSA private key in PEM format (modern method)
openssl genpkey -algorithm RSA -out privatekey.pem -pkeyopt rsa_keygen_bits:4096

# Generate RSA private key in PEM format (older method)
openssl genrsa -out privatekey.pem 4096

# Generate with passphrase protection
openssl genrsa -aes256 -out privatekey.pem 4096

# Set proper permissions
chmod 600 privatekey.pem
```

### Convert OpenSSH key to .pem format:
```bash
# Convert existing OpenSSH key to PEM format
ssh-keygen -p -m PEM -f ~/.ssh/ec2-github-key

# Convert with passphrase change
ssh-keygen -p -m PEM -f ~/.ssh/ec2-github-key
```

### Convert between key formats:
```bash
# Convert .crt to .pem
openssl x509 -in certificate.crt -out certificate.pem -outform PEM

# Convert .pfx to .pem
openssl pkcs12 -in certificate.pfx -out certificate.pem -nodes

# Convert .der to .pem
openssl x509 -inform DER -in certificate.der -out certificate.pem

# Convert .p12 to .pem
openssl pkcs12 -in certificate.p12 -out certificate.pem -nodes

# Convert OpenSSH to PEM format
ssh-keygen -p -m PEM -f ~/.ssh/your-existing-key
```

### Create combined .pem files:
```bash
# Combine private key and certificate into one .pem file
cat privatekey.pem certificate.crt > combined.pem

# Combine private key, certificate, and intermediate certificates
cat privatekey.pem certificate.crt intermediate.crt > full-chain.pem

# Create .pem file with multiple certificates
cat certificate1.crt certificate2.crt > bundle.pem
```

### Extract components from .pem files:
```bash
# Extract public key from private key
openssl rsa -in privatekey.pem -pubout -out publickey.pem

# Extract certificate information
openssl x509 -in certificate.pem -text -noout

# Check .pem file format
openssl x509 -in certificate.pem -text -noout
```

### Add public key to EC2 instance:
```bash
# Method 1: Using ssh-copy-id (if you have password access)
ssh-copy-id -i ~/.ssh/ec2-github-key.pub ec2-user@your-ec2-ip

# Method 2: Manual copy (if you have existing SSH access)
cat ~/.ssh/ec2-github-key.pub | ssh ec2-user@your-ec2-ip "cat >> ~/.ssh/authorized_keys"

# Method 3: Using AWS Systems Manager (if configured)
aws ssm send-command \
  --instance-ids i-1234567890abcdef0 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["echo \"$(cat ~/.ssh/ec2-github-key.pub)\" >> ~/.ssh/authorized_keys"]'
```

## 🔑 Using New .pem File to Access EC2 Instance

### Step 1: Add public key to EC2 instance
```bash
# If you have existing SSH access to the instance:
# Copy the public key content
cat ~/.ssh/ec2-github-key.pub

# SSH into your instance and add the public key
ssh -i your-existing-key.pem ec2-user@your-ec2-ip

# Once inside the instance, add the new public key:
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC..." >> ~/.ssh/authorized_keys

# Set proper permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### Step 2: Test the new .pem file
```bash
# Test SSH connection with new .pem file
ssh -i ~/.ssh/ec2-github-key ec2-user@your-ec2-ip

# Test with verbose output (for debugging)
ssh -vvv -i ~/.ssh/ec2-github-key ec2-user@your-ec2-ip

# Test with specific port (if not default 22)
ssh -i ~/.ssh/ec2-github-key -p 2222 ec2-user@your-ec2-ip
```

### Step 3: Update GitHub Secrets
```bash
# Get the private key content for GitHub Secret
cat ~/.ssh/ec2-github-key

# Copy this entire output (including BEGIN/END lines) to GitHub Secret EC2_SSH_KEY
```

### Step 4: Verify GitHub Actions can connect
```bash
# Test the exact same connection that GitHub Actions will use
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -i ~/.ssh/ec2-github-key ec2-user@your-ec2-ip "echo 'Connection successful'"
```

### Alternative: Convert to .pem format for AWS compatibility
```bash
# If you need the key in .pem format for AWS:
ssh-keygen -p -m PEM -f ~/.ssh/ec2-github-key

# Now you can use it like an AWS .pem file:
ssh -i ~/.ssh/ec2-github-key ec2-user@your-ec2-ip
```

## 🔐 GitHub Secrets Setup

### Required Secrets:
1. **EC2_SSH_KEY** - Private key content (entire .pem or private key file)
2. **EC2_USER** - SSH user (usually `ec2-user`, `ubuntu`, or `admin`)
3. **EC2_HOST** - EC2 instance IP or domain

### Getting private key content:
```bash
# For .pem file
cat your-key.pem

# For generated key
cat ~/.ssh/ec2-github-key
```

## 🧪 Testing SSH Connection

### Test SSH connection:
```bash
# Test with existing key
ssh -i your-key.pem ec2-user@your-ec2-ip

# Test with new key
ssh -i ~/.ssh/ec2-github-key ec2-user@your-ec2-ip

# Test with verbose output (for debugging)
ssh -v -i ~/.ssh/ec2-github-key ec2-user@your-ec2-ip
```

## 🔧 Troubleshooting

### Common issues:
```bash
# Fix permissions
chmod 600 ~/.ssh/ec2-github-key
chmod 644 ~/.ssh/ec2-github-key.pub

# Check SSH agent
ssh-add -l

# Remove old keys from known_hosts
ssh-keygen -R your-ec2-ip

# Test SSH connection with specific key
ssh -o IdentitiesOnly=yes -i ~/.ssh/ec2-github-key ec2-user@your-ec2-ip
```

### Debug GitHub Actions SSH:
```bash
# Add debug output to workflow
- name: Debug SSH
  run: |
    echo "Testing SSH connection..."
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
        ${{ secrets.EC2_USER }}@${{ secrets.EC2_HOST }} "echo 'SSH connection successful'"
```

## 📋 Quick Reference

### For existing AWS key:
1. Use the `.pem` file content as `EC2_SSH_KEY` secret
2. Set `EC2_USER` to your instance user
3. Set `EC2_HOST` to your instance IP

### For new key:
1. Generate: `ssh-keygen -t rsa -b 4096 -f ~/.ssh/ec2-github-key`
2. Add public key to EC2: `ssh-copy-id -i ~/.ssh/ec2-github-key.pub ec2-user@your-ec2-ip`
3. Use private key content as `EC2_SSH_KEY` secret: `cat ~/.ssh/ec2-github-key`

## 🔐 SSH Key Security Best Practices

### Key Security:
```bash
# Add passphrase to existing key
ssh-keygen -p -f ~/.ssh/your-key

# Remove passphrase from key (NOT recommended for production)
ssh-keygen -p -f ~/.ssh/your-key

# Check key fingerprint
ssh-keygen -lf ~/.ssh/your-key.pub

# Verify key fingerprint matches server
ssh-keygen -lf ~/.ssh/your-key.pub | cut -d' ' -f2
```

### SSH Agent Management:
```bash
# Start SSH agent
eval "$(ssh-agent -s)"

# Add key to SSH agent
ssh-add ~/.ssh/your-key

# List keys in SSH agent
ssh-add -l

# Remove key from SSH agent
ssh-add -d ~/.ssh/your-key

# Clear all keys from SSH agent
ssh-add -D

# SSH agent forwarding (use with caution)
ssh -A user@server
```

### Key Types and Comparison:
```bash
# Generate ED25519 key (recommended - faster, more secure)
ssh-keygen -t ed25519 -f ~/.ssh/ed25519-key

# Generate RSA key (traditional, widely supported)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/rsa-key

# Generate ECDSA key (good balance)
ssh-keygen -t ecdsa -b 521 -f ~/.ssh/ecdsa-key
```

### Key Fingerprint Verification:
```bash
# Get key fingerprint (MD5)
ssh-keygen -lf ~/.ssh/your-key.pub

# Get key fingerprint (SHA256)
ssh-keygen -lf ~/.ssh/your-key.pub -E sha256

# Verify server host key
ssh-keyscan -t rsa your-server.com

# Check known_hosts entries
ssh-keygen -F your-server.com
```

### Advanced SSH Key Operations:
```bash
# Copy key to remote server (with specific port)
ssh-copy-id -i ~/.ssh/your-key.pub -p 2222 user@server

# Test SSH connection with specific key
ssh -i ~/.ssh/your-key -o IdentitiesOnly=yes user@server

# SSH with key and port
ssh -i ~/.ssh/your-key -p 2222 user@server

# SSH with verbose output for debugging
ssh -vvv -i ~/.ssh/your-key user@server
```

## 🚨 Security Notes

- Never commit private keys to git
- Use GitHub Secrets for all sensitive data
- Regularly rotate SSH keys (every 6-12 months)
- Use key-based authentication (disable password auth)
- Keep your .pem files secure and backed up
- Use ED25519 keys when possible (more secure than RSA)
- Add passphrases to all private keys
- Monitor SSH access logs regularly
- Disable root login via SSH
- Use SSH agent forwarding carefully
- Verify key fingerprints before trusting new keys
