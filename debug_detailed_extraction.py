#!/usr/bin/env python3
"""
Debug script with detailed extraction tracing
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import re

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

def is_section_header(line: str) -> bool:
    line_clean = line.strip()
    section_headers = {
        'education', 'experience', 'skills', 'projects', 'work', 'employment',
        'academic', 'qualifications', 'certifications', 'languages', 'interests',
        'achievements', 'awards', 'publications', 'references', 'contact'
    }
    if line_clean.lower() in section_headers:
        return True
    if len(line_clean.split()) <= 4:
        if line_clean.isupper() or re.match(r'^[A-Z][A-Z\s]+$', line_clean):
            return True
    return False

lines = [line.strip() for line in sample_resume.split('\n') if line.strip()]

print("="*80)
print("CHECKING EACH LINE FOR SECTION HEADER")
print("="*80)

for i, line in enumerate(lines):
    is_header = is_section_header(line)
    word_count = len(line.split())
    is_upper = line.isupper()
    regex_match = re.match(r'^[A-Z][A-Z\s]+$', line)
    
    print(f"\n{i:2d}: {line[:50]:50s} | Header: {is_header} | Words: {word_count} | Upper: {is_upper} | Regex: {bool(regex_match)}")

print("\n" + "="*80)
print("SECTION EXTRACTION TRACE")
print("="*80)

section = []
found_section = False

for i, line in enumerate(lines):
    line_clean = line.strip()
    
    # Check if this is EDUCATION header
    if "EDUCATION" in line_clean:
        found_section = True
        print(f"{i}: Found EDUCATION section header, starting collection")
        continue
    
    if found_section:
        # Check if this is another section header
        if is_section_header(line):
            print(f"{i}: STOPPED - {line[:50]:50s} looks like section header")
            break
        
        if line_clean:
            section.append(line_clean)
            print(f"{i}: ADDED - {line[:50]:50s}")

print(f"\nTotal lines extracted: {len(section)}")
print("\nExtracted lines:")
for i, line in enumerate(section):
    print(f"  {i}: {line}")
