# CRM Celery & Redis Setup Guide

This document explains how to set up Celery, Redis, and Celery Beat for the CRM project to automate background and scheduled tasks such as CRM reporting.

---

## 🧩 Prerequisites

Ensure the following are installed:
- Python 3.x
- Redis Server (running on `localhost:6379`)
- Django
- Celery
- django-celery-beat

---

## ⚙️ Installation Steps

### 1. Install Dependencies
Add the following to your `requirements.txt`:

