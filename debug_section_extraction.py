#!/usr/bin/env python3
"""
Debug script to check education section extraction
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.resume_parser import parse_resume, extract_section_simple
import json

sample_resume = """
John Smith
john.smith@example.com | (555) 123-4567

EDUCATION
B.Sc in Computer Science
University of California, Berkeley
2019 - 2023
GPA: 3.8/4.0
Dean's List

M.Sc in Machine Learning
Stanford University
2023 - 2025
"""

lines = [line.strip() for line in sample_resume.split('\n') if line.strip()]

print("="*80)
print("ALL LINES IN RESUME")
print("="*80)
for i, line in enumerate(lines):
    print(f"{i}: {line}")

print("\n" + "="*80)
print("EDUCATION SECTION EXTRACTION")
print("="*80)

education_lines = extract_section_simple(lines, "EDUCATION")
print(f"\nExtracted {len(education_lines)} lines from EDUCATION section:")
for i, line in enumerate(education_lines):
    print(f"{i}: {line}")

print("\n" + "="*80)
print("PARSED EDUCATION ENTRIES")
print("="*80)

result = parse_resume(sample_resume)
print(json.dumps(result.get('education'), indent=2))
