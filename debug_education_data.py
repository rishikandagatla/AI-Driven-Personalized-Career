#!/usr/bin/env python3
"""
Debug script to check what education data is being captured
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.resume_parser import parse_resume
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

result = parse_resume(sample_resume)

print("="*80)
print("EDUCATION DATA STRUCTURE")
print("="*80)
print(json.dumps(result.get('education'), indent=2))

print("\n" + "="*80)
print("CHECKING FIELD VALUES")
print("="*80)

for i, edu in enumerate(result.get('education', []), 1):
    print(f"\nEntry {i}:")
    for key, value in edu.items():
        print(f"  {key}: '{value}' (type: {type(value).__name__}, bool: {bool(value)})")
