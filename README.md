# File Explorer

A web-based file manager for browsing, uploading, downloading, and previewing files across multiple storage drives.

## Features

✅ Browse all storage drives
✅ Upload/Download files (up to 5GB)
✅ Preview images, videos, PDFs, and text files
✅ Create and delete folders
✅ Password-protected login
✅ Docker containerized
✅ Auto-start on boot

### Certificate Configuration

The application uses a **self-signed SSL certificate** for HTTPS encryption on the local network. 

**Why self-signed?**
- Airtel ISP blocks standard ports 80/443 (carrier-level restriction)
- Self-signed certs provide identical encryption to Let's Encrypt
- Perfect for home lab and internal deployments
- Demonstrates understanding of SSL/TLS concepts

**Production Deployment:** For internet-facing deployments, use Let's Encrypt or commercial certificates on unrestricted ports.

**Access:** 
- Local network: `https://192.168.1.150` (accept certificate warning)
- External (with port forwarding): `https://uddissh-verma.duckdns.org:8443`

## Quick Start

### With Docker

```bash
git clone https://github.com/YOUR_USERNAME/file-explorer.git
cd file-explorer
docker-compose up -d
