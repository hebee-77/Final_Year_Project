# AI-Powered Learning Management System

A comprehensive Django-based LMS with AI integration using Google Gemini API for personalized learning experiences.

## Features

- **User Management**: Role-based authentication (Students, Teachers, Admins)
- **Course Management**: Create and manage courses with materials and assignments
- **AI Integration**: Chat assistant, content summaries, explanations, and feedback
- **Analytics Dashboard**: Track student progress and engagement
- **Assignment System**: Submit work and receive AI-powered feedback
- **Learning Goals**: Set and track personal learning objectives
- **Feedback System**: Course surveys and system feedback

## Technologies Used

- **Backend**: Django 5.1.4, Python 3.11.9
- **Database**: MySQL
- **AI**: Google Gemini API
- **Frontend**: Bootstrap 5, HTML, CSS, JavaScript
- **Additional**: Chart.js for visualizations

## Installation

### Prerequisites

- Python 3.11.9
- MySQL Server
- Google Gemini API Key

### Setup Instructions

#### Create virtual environment 
python -m venv venv
source venv/bin/activate  # Linux/Mac
k12_venv1\Scripts\activate     # Windows

#### Install dependencies
pip install -r requirements.txt

#### Configure MySQL Database
CREATE DATABASE ai_lms_db ;

#### Configure Environment Variables
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=ai_lms_db
DB_USER=lms_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
GEMINI_API_KEY=your-gemini-api-key

#### Run Migrations
python manage.py makemigrations
python manage.py migrate

#### Create Superuser
python manage.py createsuperuser

#### Generate Sample Data (Optional)
python manage.py generate_sample_data

If you want to delete the existing data and recreate it:
python manage.py generate_sample_data --reset


#### Run Development Server
python manage.py runserver


# Usage
## For Students
Register/Login to your account

Browse and enroll in courses

Access learning materials

Complete assignments

Chat with AI assistant for help

Track your progress

Set learning goals

## For Teachers
Create and manage courses

Upload learning materials

Create assignments

Grade student submissions

View class analytics

Monitor student performance

## For Admins
Manage users and roles

Oversee all courses

View system analytics

Review feedback

Manage subjects