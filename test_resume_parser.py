#!/usr/bin/env python3
"""
Test script for improved resume parser
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.resume_parser import parse_resume

# Sample resume text
sample_resume = """
John Smith
john.smith@example.com | (555) 123-4567 | linkedin.com/in/johnsmith

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley
2019 - 2023
GPA: 3.8/4.0 | Dean's List

Master of Science in Machine Learning
Stanford University
2023 - 2025

EXPERIENCE
Senior Software Engineer
Google Inc
Jan 2023 - Present
• Led team of 5 engineers in building recommendation system
• Improved model accuracy by 15% through optimization
• Designed and deployed microservices architecture

Software Engineer
Microsoft
June 2021 - Dec 2022
• Built web APIs serving 5M+ daily users
• Optimized database queries reducing latency by 40%

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
Databases: PostgreSQL, MongoDB, Redis
Cloud: AWS, Google Cloud, Azure
"""

# Parse the resume
result = parse_resume(sample_resume)

# Display results
print("=" * 80)
print("RESUME PARSING TEST RESULTS")
print("=" * 80)

print(f"\n✓ Name: {result.get('name', 'NOT FOUND')}")
print(f"✓ Email: {result['contact'].get('email', 'NOT FOUND')}")
print(f"✓ Phone: {result['contact'].get('phone', 'NOT FOUND')}")

print(f"\n--- EDUCATION ({len(result['education'])} entries) ---")
for i, edu in enumerate(result['education'], 1):
    print(f"\n{i}. Education Entry:")
    if edu.get('degree'):
        print(f"   Degree: {edu.get('degree')}")
    if edu.get('field_of_study'):
        print(f"   Field: {edu.get('field_of_study')}")
    if edu.get('institution'):
        print(f"   Institution: {edu.get('institution')}")
    if edu.get('school') and edu.get('school') != edu.get('institution'):
        print(f"   School: {edu.get('school')}")
    if edu.get('start_year'):
        print(f"   Start Year: {edu.get('start_year')}")
    if edu.get('end_year'):
        print(f"   End Year: {edu.get('end_year')}")
    if edu.get('gpa_cgpa'):
        print(f"   GPA/CGPA: {edu.get('gpa_cgpa')}")
    if edu.get('additional_info'):
        print(f"   Additional Info: {edu.get('additional_info')}")
    elif edu.get('details'):
        print(f"   Details: {edu.get('details')}")

print(f"\n--- EXPERIENCE ({len(result['experience'])} entries) ---")
for i, exp in enumerate(result['experience'], 1):
    print(f"\n{i}. {exp.get('title', 'Title not specified')}")
    print(f"   Company: {exp.get('company', 'Company not specified')}")
    print(f"   Date: {exp.get('date', 'Date not specified')}")
    if exp.get('description'):
        print(f"   Description: {exp.get('description')[:100]}...")

print(f"\n--- PROJECTS ({len(result['projects'])} entries) ---")
for i, proj in enumerate(result['projects'], 1):
    print(f"\n{i}. {proj.get('name', 'Project name not specified')}")
    if proj.get('description'):
        print(f"   Description: {proj.get('description')[:100]}...")
    if proj.get('technologies'):
        print(f"   Technologies: {proj.get('technologies')}")

print(f"\n--- SKILLS ({len(result['skills'])} total) ---")
print("Skills:", ", ".join(result['skills'][:10]))
if len(result['skills']) > 10:
    print(f"... and {len(result['skills']) - 10} more")

print(f"\n--- METADATA ---")
print(f"Sections found: {', '.join(result['metadata']['sections_found'])}")
print(f"Contact info found: {result['metadata']['contact_info_found']}")
print(f"Name found: {result['metadata']['name_found']}")

print("\n" + "=" * 80)
print("✓ Test completed successfully!")
print("=" * 80)
