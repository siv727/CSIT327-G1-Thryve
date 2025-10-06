# Thryve: SME Resource Sharing & Collaboration Network

**Thryve** is a comprehensive web platform designed to connect Small and Medium Enterprises (SMEs) in a collaborative network where businesses can share resources, exchange services, and build meaningful partnerships. The platform serves as a digital marketplace that enables local businesses to optimize their operations through resource sharing and service collaboration.

### 🎯 Mission Statement
To empower SMEs by creating a unified platform that facilitates resource optimization, service exchange, and business collaboration within local communities.

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.0+ (Pure Django - templates, views, models)
- **Database**: Supabase (PostgreSQL-based backend-as-a-service)
- **Authentication**: Django's built-in authentication system
- **ORM**: Django ORM with PostgreSQL adapter

### Frontend
- **Templates**: Django Template Language (DTL)
- **Styling**: TailwindCSS for responsive design and styling
- **Interactivity**: Minimal JavaScript with Django integration

---

## 🚀 Setup & Run Instructions

### Prerequisites
- **Python 3.10+**
- **Git**
- **Supabase account** (free tier available)
- **Node.js** (for TailwindCSS)

---

### 📋 Step-by-Step Installation Guide

#### **1. Clone the Repository**
```bash
# Clone the project repository
git clone https://github.com/your-team/thryve.git
cd thryve
```

#### **2. Set Up Virtual Environment**
```bash
# Create virtual environment
python -m venv env

# Activate virtual environment
# On Windows:
env\\Scripts\\activate

# On macOS/Linux:
source env/bin/activate
```

#### **3. Install Python Dependencies**
```bash
# Install required packages
pip install django psycopg2 dj-database-url python-dotenv
```

#### **4. Set Up Supabase Database**

1. **Create Supabase Project:**
   - Go to [Supabase Dashboard](https://supabase.com/dashboard)
   - Click "New Project"
   - Choose your organization and set project details
   - Wait for project setup to complete

2. **Get Database Connection Details:**
   - In your Supabase project dashboard
   - Go to **Settings → Database**
   - Copy the **Connection Pooling** connection string (Session Pooler)
   - It should look like: `postgresql://postgres:YOUR_PASSWORD@aws-0-<project-ref>.pooler.supabase.com:5432/postgres`

#### **5. Configure Environment Variables**
```bash
# Create .env file in project root
touch .env  # On Windows: echo. > .env
```

Add the following to your `.env` file:
```env
# Django Configuration
SECRET_KEY=your-super-secret-django-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase Database Configuration (Session Pooler)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@aws-0-<project-ref>.pooler.supabase.com:5432/postgres?sslmode=require
```

**Important Notes:**
- Replace `YOUR_PASSWORD` with your Supabase database password
- Replace `<project-ref>` with your actual project reference from Supabase
- Keep `sslmode=require` as Supabase enforces SSL connections

#### **6. Database Setup**
```bash
# Create and apply database migrations
python manage.py makemigrations
python manage.py migrate
```

#### **7. Verify Database Connection (Optional)**
```bash
# Test if Django can connect to Supabase
python manage.py shell

# In the Django shell, run:
import os
print(os.environ.get("DATABASE_URL"))
# Should display your connection string

# Test database connectivity
from django.db import connection
cursor = connection.cursor()
print("Database connection successful!")
exit()
```

#### **8. Run the Development Server**
```bash
# Start Django development server
python manage.py runserver

# Access the application at:
# http://127.0.0.1:8000
```

---

### 🔍 Troubleshooting Common Issues

#### **Database Connection Issues:**
```bash
# If migrations fail, check your DATABASE_URL
python manage.py shell
import os
print(os.environ.get("DATABASE_URL"))

# Ensure .env file is in the correct location (project root)
# Verify Supabase project is active and credentials are correct
```

---

## 👥 Team Members

| Name | Role | Email |
|------|------|-------|
| **Andre Salonga** | Lead Frontend Developer | andre.salonga@cit.edu |
| **Ervin Louis Villas** | Lead Backend Developer | ervinlouis.villas@cit.edu |
| **Justine Vilocura** | Assistant Frontend & Backend Developer | justine.vilocura@cit.edu |

---

## 🌟 Key Features

### 🏢 Business Directory
- **Comprehensive Business Profiles**: Detailed company information, industry categories, and contact details
- **Advanced Search & Filtering**: Find businesses by category, location, and services offered

### 🔄 Resource & Service Marketplace
- **Unified Listing System**: Single platform for both equipment sharing and service offerings
- **Equipment Sharing**: Share underutilized business equipment and tools
- **Service Exchange**: Offer and request professional services and expertise
- **Smart Categorization**: Organized by industry and resource type

### 📅 Booking & Coordination System
- **Unified Booking Workflow**: Simple request-approval process for both resources and services
- **Status Tracking**: Real-time updates on booking requests and approvals

### 💬 Communication Hub
- **Forum Discussions**: Community-wide discussions on industry topics
- **Business Networking**: Connect with like-minded entrepreneurs and businesses

### 📊 User Dashboard
- **Centralized Management**: Manage listings, bookings, and messages from one interface
- **Activity Overview**: Track business interactions and platform engagement
- **Quick Actions**: Fast access to frequently used features

---

<!-- ## 🎯 Core User Workflows

### For Business Owners

1. **Getting Started**
   - Register account and verify email
   - Complete business profile with verification documents
   - Browse platform to understand available opportunities

2. **Resource Sharing**
   - List underutilized equipment or tools
   - Set availability and pricing
   - Manage booking requests and coordinate handovers

3. **Service Exchange**
   - Offer professional services and expertise
   - Browse service requests from other businesses
   - Submit proposals and negotiate terms

4. **Networking & Discovery**
   - Search business directory for potential partners
   - Participate in forum discussions

### Platform Administration

- **Business Verification**: Review and approve business documents
- **Content Moderation**: Monitor listings and forum posts
- **User Support**: Assist with platform usage and resolve disputes
- **Analytics**: Track platform usage and business interactions -->

<!-- 
## 👥 Team

### Development Team
- **Project Lead**: [Your Name]
- **Backend Developers**: [Team Member Names]
- **Frontend Developers**: [Team Member Names]
- **Database Designer**: [Team Member Names] -->
## Academic Context
This project is developed as part of an Information Management 2 course, focusing on practical application of web development technologies and database design principles.

---

**Built with ❤️ for the SME community**

---

*Last Updated: October 2025*
