# File Explorer - Distributed Storage Management System

A production-grade web-based file manager for managing multiple storage drives with HTTPS security, Docker containerization, and system monitoring.

## 🎯 Project Overview

This project demonstrates full-stack development, DevOps practices, and system administration skills. It provides a secure, web-accessible interface to browse, upload, download, and manage files across 6 storage drives totaling 3.8TB of storage.

### Architecture

┌─────────────────┐
│ Web Browser │
│ (HTTPS) │
└────────┬────────┘
│
┌────────▼────────┐
│ Nginx │
│ (Reverse │
│ Proxy) │
└────────┬────────┘
│
┌────────▼────────────────┐
│ Flask Application │
│ (Docker Container) │
└────────┬────────────────┘
│
┌────────▼────────────────┐
│ Storage Drives │
│ ├─ storage_1 (458GB) │
│ ├─ storage_2 (458GB) │
│ ├─ storage_3 (932GB) │
│ ├─ storage_4 (932GB) │
│ ├─ sde3_docs (98GB) │
│ └─ sde5_docs (271GB) │
└─────────────────────────┘


## ✨ Features

### Core Features
✅ **Multi-Drive Support** - Browse 6 storage drives simultaneously
✅ **File Operations** - Upload (5GB max), download, delete, create folders
✅ **File Preview** - Images, videos, PDFs, text files with syntax highlighting
✅ **Search** - Full-text search across all drives with regex support
✅ **System Monitoring** - Real-time CPU, memory, and disk usage stats

### Security Features
✅ **HTTPS/SSL** - Let's Encrypt certificate with auto-renewal
✅ **Password Authentication** - Secure login with session management
✅ **Input Validation** - Protection against path traversal attacks
✅ **Rate Limiting** - Prevent brute-force attacks
✅ **Audit Logging** - Track all file operations

### DevOps Features
✅ **Docker Containerization** - Reproducible deployments
✅ **GitHub Actions CI/CD** - Automated builds and Docker Hub pushes
✅ **Systemd Auto-Start** - Automatic startup on server boot
✅ **Static IP Configuration** - Reliable access via static IP
✅ **Nginx Reverse Proxy** - Load balancing and SSL termination

## 📊 Storage Configuration

| Drive | Mount Point | Size | Type | Purpose |
|-------|-------------|------|------|---------|
| sda1 | /mnt/storage_1 | 458GB | ext4 | Primary storage |
| sdb1 | /mnt/storage_2 | 458GB | ext4 | Secondary storage |
| sdd1 | /mnt/storage_3 | 932GB | NTFS | Seagate backup |
| sdf1 | /mnt/storage_4 | 932GB | NTFS | HIKVISION data |
| sde3 | /mnt/sde3_docs | 98GB | NTFS | Documents |
| sde5 | /mnt/sde5_docs | 271GB | NTFS | Photos/Videos |

**Total Capacity: 3.15 TB**

## 🚀 Quick Start

### With Docker (Recommended)

```bash
git clone https://github.com/Uddissh/file-explorer.git
cd file-explorer
docker-compose up -d
