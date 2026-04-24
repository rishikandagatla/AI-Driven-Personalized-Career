#!/usr/bin/env python3
"""
Test to verify the complete flow from resume to template context
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.resume_parser import parse_resume
import json

sample_resume = """
John Smith
john.smith@example.com | (555) 123-4567 | linkedin.com/in/johnsmith

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley
2019 - 2023
GPA: 3.8/4.0
Dean's List

Master of Science in Machine Learning
Stanford University
2023 - 2025

EXPERIENCE
Senior Software Engineer
Google Inc
Jan 2023 - Present
• Led team of 5 engineers in building recommendation system
• Improved model accuracy by 15% through optimization

PROJECTS
Recommendation Engine
Built ML-based recommendation system using PyTorch and deployed on AWS
Technologies: Python, PyTorch, AWS, PostgreSQL, Redis

Chat Application
Real-time chat application with end-to-end encryption
Technologies: React, Node.js, WebSocket, MongoDB

SKILLS
Programming Languages: Python, JavaScript, Java, C++
Web Development: React, Node.js, Django, FastAPI
Machine Learning: PyTorch, TensorFlow, scikit-learn
"""

print("="*80)
print("FULL RESUME PARSING AND TEMPLATE CONTEXT TEST")
print("="*80)

# Parse resume
resume_data = parse_resume(sample_resume)

print(f"\n✓ Resume parsed successfully")

# Try JSON serialization (like Django session would do)
try:
    json_str = json.dumps(resume_data, default=str)
    resume_data_from_session = json.loads(json_str)
    print(f"✓ Resume data successfully JSON serialized (session compatible)")
except Exception as e:
    print(f"✗ ERROR: Could not serialize to JSON: {e}")
    resume_data_from_session = resume_data

# Create context like the view would
context = {
    'resume_data': resume_data_from_session,
    'skills_count': len(resume_data_from_session.get('skills', [])),
    'projects_count': len(resume_data_from_session.get('projects', [])),
    'education_count': len(resume_data_from_session.get('education', [])),
    'experience_count': len(resume_data_from_session.get('experience', [])),
}

print(f"\n📊 CONTEXT THAT GOES TO TEMPLATE:")
print(f"   Education Count: {context['education_count']}")
print(f"   Experience Count: {context['experience_count']}")
print(f"   Projects Count: {context['projects_count']}")
print(f"   Skills Count: {context['skills_count']}")

# Verify template conditions
print(f"\n🔍 TEMPLATE CONDITION CHECKS:")
print(f"   resume_data.education exists: {bool(context['resume_data'].get('education'))}")
print(f"   resume_data.education length: {len(context['resume_data'].get('education', []))}")
print(f"   Will show education? {bool(context['resume_data'].get('education'))}")

print(f"   resume_data.projects exists: {bool(context['resume_data'].get('projects'))}")
print(f"   resume_data.projects length: {len(context['resume_data'].get('projects', []))}")
print(f"   Will show projects? {bool(context['resume_data'].get('projects'))}")

# Show actual data
print(f"\n📚 EDUCATION DATA:")
for i, edu in enumerate(context['resume_data'].get('education', []), 1):
    print(f"\n  Entry {i}:")
    print(f"    Type: {type(edu)}")
    print(f"    Keys: {list(edu.keys()) if isinstance(edu, dict) else 'NOT A DICT'}")
    if isinstance(edu, dict):
        print(f"    Degree: {edu.get('degree')}")
        print(f"    Institution: {edu.get('institution')}")

print(f"\n🎯 PROJECT DATA:")
for i, proj in enumerate(context['resume_data'].get('projects', []), 1):
    print(f"\n  Entry {i}:")
    print(f"    Type: {type(proj)}")
    print(f"    Keys: {list(proj.keys()) if isinstance(proj, dict) else 'NOT A DICT'}")
    if isinstance(proj, dict):
        print(f"    Name: {proj.get('name')}")
        print(f"    Description: {proj.get('description', '')[:50]}")

print("\n" + "="*80)
