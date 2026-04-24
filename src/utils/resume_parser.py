import re
from typing import List, Dict, Set, Tuple
import logging


def clean_line(line: str) -> str:
    """
    Clean and normalize a line of text for better parsing.
    """
    # Remove excessive whitespace
    line = re.sub(r'\s+', ' ', line)
    
    # Remove special characters but keep important ones
    line = re.sub(r'[^\w\s\.\-\+\&\@\#\(\)]', '', line)
    
    return line.strip()


def extract_name(text: str) -> str:
    """
    Extract the person's name from the resume (usually at the top).
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if not lines:
        return ""
    
    # First line is likely the name, unless it contains special patterns
    first_line = lines[0].strip()
    
    # Filter out common non-name patterns
    if any(keyword in first_line.lower() for keyword in ['email', 'phone', 'address', 'linkedin', 'github']):
        if len(lines) > 1:
            first_line = lines[1].strip()
    
    # Name should be 2-5 words, excluding emails, links, etc.
    if '@' in first_line or 'http' in first_line:
        for line in lines[1:10]:  # Check first 10 lines
            if '@' not in line and 'http' not in line and line.count(' ') <= 4:
                return line.strip()
    
    # Validate that it looks like a name (no numbers, proper length)
    if re.match(r'^[A-Za-z\s\-\']+$', first_line) and 2 <= len(first_line.split()) <= 5:
        return first_line
    
    return ""


def extract_section_advanced(lines: List[str], section_keywords: List[str]) -> List[str]:
    """
    Advanced section extraction that handles multiple keyword variations.
    """
    section = []
    found_section = False
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        # Check if this line contains any of our section keywords
        if any(keyword in line_lower for keyword in section_keywords):
            found_section = True
            continue
        
        # If we found a section, collect content until next major section
        if found_section:
            # Stop if we hit another major section header
            if is_section_header(line):
                break
            
            # Add non-empty lines
            if line.strip():
                section.append(line.strip())
    
    return [clean_line(line) for line in section if line.strip()]


def extract_section_simple(lines: List[str], section_name: str) -> List[str]:
    """
    Simple section extraction that looks for exact section names.
    """
    section = []
    found_section = False
    
    # Create variations of the section name
    variations = [
        section_name.upper(),
        section_name.title(),
        section_name.lower(),
        f"{section_name.upper()}S",
        f"{section_name.title()}S"
    ]
    
    for line in lines:
        line_clean = line.strip()
        
        # Check if this is our section header
        if any(var in line_clean for var in variations):
            found_section = True
            continue
        
        # If we found a section, collect content until next major section
        if found_section:
            # Stop if we hit another major section header
            if is_section_header(line):
                break
            
            # Add non-empty lines
            if line_clean:
                section.append(line_clean)
    
    return section


def is_section_header(line: str) -> bool:
    """
    Determine if a line is likely a section header.
    Excludes common key-value pairs like "GPA: 3.8" that shouldn't be headers.
    """
    line_clean = line.strip()
    
    # Common section headers
    section_headers = {
        'education', 'experience', 'skills', 'projects', 'work', 'employment',
        'academic', 'qualifications', 'certifications', 'languages', 'interests',
        'achievements', 'awards', 'publications', 'references', 'contact'
    }
    
    # Check if line is a known header
    if line_clean.lower() in section_headers:
        return True
    
    # If line has a colon followed by data, it's likely a key-value pair, not a header
    if ':' in line_clean:
        # Check if it looks like "Label: value" (common in education and experience)
        parts = line_clean.split(':', 1)
        if len(parts) == 2 and parts[1].strip():  # Has both key and value
            # Exclude common abbreviations that appear in resumes
            key = parts[0].strip().upper()
            abbreviations = {'GPA', 'CGPA', 'CPI', 'ID', 'URL', 'EMAIL', 'PHONE', '%'}
            if key in abbreviations or len(key) <= 3:
                return False
    
    # Check if line looks like a header (short, all caps, or bold-like)
    if len(line_clean.split()) <= 4:
        if line_clean.isupper() or re.match(r'^[A-Z][A-Z\s]+$', line_clean):
            return True
    
    return False


def extract_skills_advanced(skill_lines: List[str]) -> List[str]:
    """
    Advanced skill extraction with better handling of various formats.
    """
    skills = set()
    
    for line in skill_lines:
        # Remove category labels (e.g., "Programming Languages:", "Technical Skills:")
        if ':' in line:
            line = line.split(':', 1)[1]
        
        # Handle different separators
        separators = [',', ';', '|', '•', '·', '▪', '▫', '◦', '‣', '⁃']
        
        for sep in separators:
            if sep in line:
                parts = [part.strip() for part in line.split(sep) if part.strip()]
                skills.update(parts)
                break
        else:
            # If no separators found, split by spaces for short terms
            words = line.split()
            if len(words) <= 3:  # Likely individual skills
                skills.add(line.strip())
            else:
                # Try to extract skill-like terms
                skill_terms = extract_skill_terms(line)
                skills.update(skill_terms)
    
    # Clean and filter skills
    cleaned_skills = []
    for skill in skills:
        skill_clean = clean_skill(skill)
        if skill_clean and len(skill_clean) > 1:
            cleaned_skills.append(skill_clean)
    
    return list(dict.fromkeys(cleaned_skills))  # Remove duplicates while preserving order


def extract_skill_terms(text: str) -> List[str]:
    """
    Extract skill-like terms from text using pattern matching.
    """
    skills = []
    
    # Common skill patterns
    patterns = [
        r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # CamelCase terms
        r'\b[A-Z]{2,}\b',  # Acronyms
        r'\b[a-z]+\.[a-z]+\b',  # Abbreviations like "m.s."
        r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Two-word capitalized terms
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        skills.extend(matches)
    
    return skills


def clean_skill(skill: str) -> str:
    """
    Clean and normalize a skill term.
    """
    # Remove common prefixes/suffixes
    skill = re.sub(r'^(and|or|&)\s+', '', skill, flags=re.IGNORECASE)
    skill = re.sub(r'\s+(and|or|&)$', '', skill, flags=re.IGNORECASE)
    
    # Remove version numbers and years
    skill = re.sub(r'\s+\d+\.?\d*', '', skill)
    skill = re.sub(r'\s+\d{4}', '', skill)
    
    # Clean up whitespace
    skill = re.sub(r'\s+', ' ', skill).strip()
    
    return skill


def extract_contact_info(text: str) -> Dict[str, str]:
    """
    Extract contact information from resume text.
    """
    contact_info = {}
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        contact_info['email'] = email_match.group()
    
    # Phone pattern - multiple formats
    phone_patterns = [
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',  # (555) 123-4567, 555-123-4567, 555.123.4567, 555 123 4567
        r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,4}\b',  # International
    ]
    
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
            break
    
    # LinkedIn pattern
    linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9-]+'
    linkedin_match = re.search(linkedin_pattern, text)
    if linkedin_match:
        contact_info['linkedin'] = linkedin_match.group()
    
    return contact_info


def parse_resume_single_line(raw_text: str) -> Dict[str, any]:
    """
    Specialized parser for resumes that are extracted as a single line.
    Uses regex patterns to extract sections.
    """
    import re
    
    # Extract contact information
    contact_info = extract_contact_info(raw_text)
    
    # Define regex patterns for each section
    patterns = {
        'education': r'EDUCATION\s+(.*?)(?=SKILLS|PROJECTS|CERTIFICATIONS|ACHIEVEMENTS|$)',
        'skills': r'SKILLS\s+(.*?)(?=PROJECTS|CERTIFICATIONS|ACHIEVEMENTS|$)',
        'projects': r'PROJECTS\s+(.*?)(?=CERTIFICATIONS|ACHIEVEMENTS|EXTRACURRICULAR|$)',
        'certifications': r'CERTIFICATIONS\s+(.*?)(?=ACHIEVEMENTS|EXTRACURRICULAR|$)',
        'achievements': r'ACHIEVEMENTS\s+(.*?)(?=EXTRACURRICULAR|$)',
        'extracurricular': r'EXTRACURRICULAR\s+(.*?)$'
    }
    
    parsed_data = {
        'contact': contact_info,
        'education': [],
        'experience': [],
        'projects': [],
        'skills': [],
        'certifications': [],
        'achievements': [],
        'extracurricular': [],
        'raw_text': raw_text
    }
    
    # Extract sections using regex
    for section_name, pattern in patterns.items():
        match = re.search(pattern, raw_text, re.IGNORECASE | re.DOTALL)
        if match:
            section_content = match.group(1).strip()
            
            if section_name == 'skills':
                # Special handling for skills
                skills = extract_skills_from_text(section_content)
                parsed_data[section_name] = skills
            elif section_name == 'projects':
                # Special handling for projects
                projects = extract_projects_from_text(section_content)
                parsed_data[section_name] = projects
            else:
                # For other sections, split by bullet points
                items = extract_bullet_points(section_content)
                parsed_data[section_name] = items
    
    # Add metadata
    parsed_data['metadata'] = {
        'total_characters': len(raw_text),
        'sections_found': [k for k, v in parsed_data.items() if v and k not in ['contact', 'raw_text', 'metadata']],
        'contact_info_found': bool(contact_info)
    }
    
    return parsed_data


def extract_skills_from_text(skills_text: str) -> List[str]:
    """
    Extract skills from the skills section text.
    """
    skills = []
    
    # Split by bullet points first
    bullet_sections = skills_text.split('•')
    
    for section in bullet_sections:
        section = section.strip()
        if not section:
            continue
            
        # Look for category labels (e.g., "Languages:", "Web Development:")
        if ':' in section:
            category, skills_list = section.split(':', 1)
            # Extract skills from the list
            skill_items = extract_skill_items(skills_list)
            skills.extend(skill_items)
        else:
            # No category, treat as individual skills
            skill_items = extract_skill_items(section)
            skills.extend(skill_items)
    
    return list(dict.fromkeys(skills))  # Remove duplicates


def extract_skill_items(text: str) -> List[str]:
    """
    Extract individual skill items from text.
    """
    skills = []
    
    # Split by common separators
    separators = [',', ';', '|', '&']
    
    for sep in separators:
        if sep in text:
            parts = [part.strip() for part in text.split(sep) if part.strip()]
            skills.extend(parts)
            break
    else:
        # If no separators found, split by spaces for short terms
        words = text.split()
        if len(words) <= 5:  # Likely individual skills
            skills.append(text.strip())
        else:
            # Try to extract skill-like terms
            skill_terms = extract_skill_terms(text)
            skills.extend(skill_terms)
    
    return [clean_skill(skill) for skill in skills if clean_skill(skill)]


def extract_projects_from_text(projects_text: str) -> List[str]:
    """
    Extract projects from the projects section text.
    """
    projects = []
    
    # Split by project indicators
    project_indicators = ['§', '•', 'Tools:', 'Mentor:']
    
    # Look for project names (usually followed by § or Tools:)
    project_patterns = [
        r'([A-Z][A-Za-z\s]+)\s*§',  # Project name followed by §
        r'([A-Z][A-Za-z\s]+)\s*Tools:',  # Project name followed by Tools:
    ]
    
    import re
    for pattern in project_patterns:
        matches = re.findall(pattern, projects_text)
        for match in matches:
            project_name = match.strip()
            if len(project_name) > 3:  # Filter out short matches
                projects.append(project_name)
    
    # If no projects found with patterns, try bullet points
    if not projects:
        bullet_sections = projects_text.split('•')
        for section in bullet_sections:
            section = section.strip()
            if section and len(section) > 10:
                projects.append(section)
    
    return list(dict.fromkeys(projects))


def extract_bullet_points(text: str) -> List[str]:
    """
    Extract bullet points from text.
    """
    items = []
    
    # Split by bullet points
    bullet_sections = text.split('•')
    
    for section in bullet_sections:
        section = section.strip()
        if section and len(section) > 5:  # Filter out very short items
            items.append(section)
    
    return items


def extract_degree_and_field(text: str) -> Tuple[str, str]:
    """
    Extract degree type and field of study from education text.
    Handles formats like:
    - "B.Tech in Computer Science"
    - "Bachelor of Engineering (Computer Science)"
    - "MBA in Business Administration"
    - "Diploma in Mechanical Engineering"
    """
    degree = ""
    field = ""
    
    # Common degree patterns
    degree_patterns = [
        (r'(B\.Tech|Bachelor of Technology)', 'B.Tech'),
        (r'(B\.Sc|Bachelor of Science)', 'B.Sc'),
        (r'(B\.A|Bachelor of Arts)', 'B.A'),
        (r'(B\.E|Bachelor of Engineering)', 'B.E'),
        (r'(M\.Tech|Master of Technology)', 'M.Tech'),
        (r'(M\.Sc|Master of Science)', 'M.Sc'),
        (r'(M\.A|Master of Arts)', 'M.A'),
        (r'(MBA|Master of Business Administration)', 'MBA'),
        (r'(Ph\.D|PhD|Doctor of Philosophy)', 'Ph.D'),
        (r'(Diploma)', 'Diploma'),
        (r'(BCA|Bachelor of Computer Applications)', 'BCA'),
        (r'(MCA|Master of Computer Applications)', 'MCA'),
        (r'(CA|Chartered Accountant)', 'CA'),
    ]
    
    for pattern, normalized_degree in degree_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            degree = normalized_degree
            break
    
    # Extract field of study from various formats
    # Format 1: "B.Tech in Computer Science" or "Bachelor of Science in Physics"
    # Remove the degree part first to avoid confusion
    text_for_field = text
    for pattern, _ in degree_patterns:
        text_for_field = re.sub(pattern, '', text_for_field, flags=re.IGNORECASE)
    
    # Now extract from the remaining text
    # Format 1: "in Computer Science" or "of Computer Science"
    field_pattern_1 = r'\b(?:in|of)\s+([A-Za-z\s\-&]+?)(?:\,|$|\()'
    match = re.search(field_pattern_1, text_for_field, re.IGNORECASE)
    if match:
        field = match.group(1).strip()
    
    # Format 2: "B.Tech (Computer Science)"
    if not field:
        field_pattern_2 = r'\(([A-Za-z\s\-&]+)\)'
        match = re.search(field_pattern_2, text_for_field)
        if match:
            potential_field = match.group(1).strip()
            # Make sure it's not something like "CGPA: 3.8"
            if not any(keyword in potential_field.lower() for keyword in ['cgpa', 'gpa', 'grade', 'score', '%']):
                field = potential_field
    
    # Format 3: Extract from capitalized words in remaining text
    if not field:
        # Look for capitalized words after degree removed
        words = text_for_field.split()
        field_words = []
        for word in words:
            word_clean = word.strip('(),-:')
            if word_clean and word_clean[0].isupper() and len(word_clean) > 2 and not any(char.isdigit() for char in word_clean):
                field_words.append(word_clean)
            elif field_words:  # Stop after first non-capitalized word after finding some
                break
        if field_words:
            field = ' '.join(field_words).strip('(),:-')
    
    return degree, field


def extract_years_from_education(text: str) -> Tuple[str, str]:
    """
    Extract start and end years from education text.
    Handles formats like: "2020-2024", "2020 - 2024", "2020 to 2024", "Graduation: 2024", "07/2023"
    """
    start_year = ""
    end_year = ""
    
    # Pattern for year ranges: "2020-2024" or "2020 - 2024" or "2020 to 2024"
    year_range_pattern = r'(19\d{2}|20\d{2})\s*(?:\-|to|through)\s*(19\d{2}|20\d{2})'
    match = re.search(year_range_pattern, text, re.IGNORECASE)
    if match:
        start_year = match.group(1)
        end_year = match.group(2)
        return start_year, end_year
    
    # Pattern for "Graduation: 2024" or "Graduated: 2024" or "Expected: 2024"
    grad_pattern = r'(?:Graduation|Graduated|Expected|Completing)[\s:]*(?:in\s+)?(19\d{2}|20\d{2})'
    match = re.search(grad_pattern, text, re.IGNORECASE)
    if match:
        end_year = match.group(1)
        return start_year, end_year
    
    # Pattern for month/year format: "07/2023" or "July 2023"
    month_year_pattern = r'(?:\d{1,2}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s/]+(19\d{2}|20\d{2})'
    match = re.search(month_year_pattern, text, re.IGNORECASE)
    if match:
        end_year = match.group(1)
        if not start_year and not end_year:
            # If we only found one year, make it the end year
            return start_year, match.group(1)
    
    # Pattern for single year mentioned
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
    if len(years) >= 2:
        start_year = years[0]
        end_year = years[-1]
    elif len(years) == 1:
        end_year = years[0]
    
    return start_year, end_year


def extract_gpa_cgpa(text: str) -> str:
    """
    Extract GPA, CGPA, or percentage from text.
    Handles formats like: "3.8/4.0", "3.8 out of 4.0", "GPA: 3.8", "85%"
    """
    gpa = ""
    
    # Pattern for GPA/CGPA format: "3.8/4.0" or "3.8 out of 4.0"
    gpa_pattern = r'(?:GPA|CGPA)[\s:]*(\d+\.?\d*)\s*(?:/|out\s+of)?\s*(\d+\.?\d*)?'
    match = re.search(gpa_pattern, text, re.IGNORECASE)
    if match:
        gpa = match.group(0)
        return gpa
    
    # Pattern for percentage: "85%" or "Percentage: 85"
    percentage_pattern = r'(?:Percentage|Score)[\s:]*(\d+(?:\.\d+)?)\s*%?'
    match = re.search(percentage_pattern, text, re.IGNORECASE)
    if match:
        gpa = match.group(0)
        return gpa
    
    # Simpler pattern: just look for "3.8/4.0" or "85%"
    simple_gpa = re.search(r'\d+\.?\d*\s*/\s*\d+\.?\d*', text)
    if simple_gpa:
        gpa = simple_gpa.group(0)
        return gpa
    
    simple_percent = re.search(r'\d+(?:\.\d+)?\s*%', text)
    if simple_percent:
        gpa = simple_percent.group(0)
        return gpa
    
    return gpa


def preprocess_education_lines(education_lines: List[str]) -> List[str]:
    """
    Preprocess education section lines to better group related information
    and improve parsing. Merges lines that belong to the same education entry.
    
    Strategy: Group lines until we see a clear boundary (another degree or institution),
    then merge each group into a single line for better parsing.
    """
    if not education_lines:
        return []
    
    degree_pattern = r'(B\.Tech|B\.Sc|B\.A|B\.E|M\.Tech|M\.Sc|M\.A|MBA|Ph\.D|PhD|Diploma|BCA|MCA|Bachelor|Master|Associate)'
    institution_keywords = ['university', 'college', 'institute', 'school', 'academy', 'polytechnic']
    
    processed_lines = []
    current_group = []
    last_was_degree_or_institution = False
    
    for i, line in enumerate(education_lines):
        line = line.strip()
        if not line:
            continue
        
        has_degree = re.search(degree_pattern, line, re.IGNORECASE) is not None
        has_institution = any(kw in line.lower() for kw in institution_keywords)
        
        # Check if this line starts a new entry
        should_finalize_group = False
        
        if has_degree or has_institution:
            # If we already have degree and institution in current group, this is new entry
            has_degree_in_group = any(
                re.search(degree_pattern, g, re.IGNORECASE) for g in current_group
            )
            has_institution_in_group = any(
                any(kw in g.lower() for kw in institution_keywords) for g in current_group
            )
            
            # If we have a complete entry (degree + institution or year), start fresh
            if (has_degree_in_group and has_institution_in_group and current_group):
                should_finalize_group = True
            elif (has_degree or has_institution) and last_was_degree_or_institution and current_group:
                # Two degree/institution lines in a row - new entry
                should_finalize_group = True
        
        # Finalize current group if needed
        if should_finalize_group and current_group:
            merged = ' '.join(current_group)
            processed_lines.append(merged)
            current_group = []
        
        # Add current line to group
        current_group.append(line)
        last_was_degree_or_institution = (has_degree or has_institution)
    
    # Don't forget the last group
    if current_group:
        merged = ' '.join(current_group)
        processed_lines.append(merged)
    
    return processed_lines


def parse_education_entries(education_lines: List[str]) -> List[Dict[str, str]]:
    """
    Parse education section into structured entries with all relevant fields.
    Handles multi-line entries where degree, institution, dates are on separate lines.
    
    Extracts:
    - degree: Degree type (B.Tech, M.Sc, MBA, etc.)
    - field_of_study: Field/specialization
    - institution: University/College name
    - start_year: Start year if available
    - end_year: Graduation year
    - gpa_cgpa: GPA/CGPA/Percentage if mentioned
    - additional_info: Any other notes (honors, achievements, etc.)
    """
    if not education_lines:
        return []
    
    education_entries = []
    current_entry = None
    
    # Patterns
    degree_pattern = r'(B\.Tech|B\.Sc|B\.A|B\.E|M\.Tech|M\.Sc|M\.A|MBA|Ph\.D|PhD|Diploma|BCA|MCA|Bachelor|Master|Associate)'
    institution_keywords = ['university', 'college', 'institute', 'school', 'academy', 'polytechnic']
    
    for line in education_lines:
        line = line.strip()
        if not line:
            continue
        
        # Classify the line
        has_degree = re.search(degree_pattern, line, re.IGNORECASE) is not None
        has_institution = any(kw in line.lower() for kw in institution_keywords)
        has_year = re.search(r'\b(19\d{2}|20\d{2})\b', line) is not None
        is_gpa_line = re.search(r'(?:GPA|CGPA|percentage|score)', line, re.IGNORECASE) is not None
        
        # If we encounter a DEGREE line and already have a current entry, save it first
        if has_degree and current_entry and (current_entry.get('institution') or current_entry.get('degree')):
            education_entries.append(current_entry)
            current_entry = None
        
        # Create new entry if we don't have one
        if not current_entry:
            current_entry = {
                'degree': '',
                'field_of_study': '',
                'institution': '',
                'start_year': '',
                'end_year': '',
                'gpa_cgpa': '',
                'additional_info': ''
            }
        
        # Process the line based on its type
        if has_degree:
            # Extract degree and field
            degree, field = extract_degree_and_field(line)
            current_entry['degree'] = degree
            if field:
                current_entry['field_of_study'] = field
        
        elif has_institution:
            # Institution line  
            current_entry['institution'] = line
        
        elif has_year:
            # Year/date line
            start_year, end_year = extract_years_from_education(line)
            if start_year:
                current_entry['start_year'] = start_year
            if end_year:
                current_entry['end_year'] = end_year
        
        elif is_gpa_line:
            # GPA/CGPA line
            gpa = extract_gpa_cgpa(line)
            if gpa:
                current_entry['gpa_cgpa'] = gpa
        
        else:
            # Additional info (honors, achievements, etc.)
            if line and len(line) > 2:  # Skip very short lines
                if current_entry.get('additional_info'):
                    current_entry['additional_info'] += ' | ' + line
                else:
                    current_entry['additional_info'] = line
    
    # Save the last entry
    if current_entry and (current_entry.get('degree') or current_entry.get('institution') or current_entry.get('end_year')):
        education_entries.append(current_entry)
    
    # Post-process: Fill in missing field_of_study with common defaults if degree is present
    for entry in education_entries:
        if entry.get('degree') and not entry.get('field_of_study'):
            # Try to infer from institution or additional info
            combined_text = (entry.get('institution', '') + ' ' + entry.get('additional_info', '')).lower()
            
            # Common field patterns
            field_patterns = {
                'Computer Science': r'(computer|CS|software|IT|programming)',
                'Information Technology': r'(information technology)',
                'Engineering': r'(engineering|technology|mechanical|civil|electrical)',
                'Business': r'(business|management|administration|MBA)',
                'Science': r'(science|scientific|physics|chemistry)',
            }
            
            for field, pattern in field_patterns.items():
                if re.search(pattern, combined_text, re.IGNORECASE):
                    if not entry['field_of_study']:
                        entry['field_of_study'] = field
                    break
    
    return education_entries


def parse_experience_entries(experience_lines: List[str]) -> List[Dict[str, str]]:
    """
    Parse experience section into structured entries with company, title, date.
    Handles various formats like: Title + Company + Date or Company + Title + Date
    """
    experience_entries = []
    current_entry = None
    
    for i, line in enumerate(experience_lines):
        line = line.strip()
        if not line:
            continue
        
        # Check for date patterns - strong indicator of entry structure
        has_date = re.search(r'\b(20\d{2}|19\d{2})\b|Present|Current', line, re.IGNORECASE)
        
        # Check for title/company keywords
        has_company = any(kw in line.lower() for kw in ['inc', 'corp', 'ltd', 'llc', 'company', 'solutions', 
                                                         'technologies', 'systems', 'labs', 'studios', 'group',
                                                         'google', 'microsoft', 'amazon', 'apple', 'facebook',
                                                         'meta', 'netflix', 'uber', 'airbnb', 'twitter', 'linkedin'])
        
        # If we have a date, this likely marks end of previous entry and start of new info
        if has_date:
            # Save previous entry if it has meaningful content
            if current_entry and (current_entry.get('title') or current_entry.get('company')):
                if not current_entry.get('date'):  # Only add date if not already set
                    current_entry['date'] = line
                experience_entries.append(current_entry)
                current_entry = None
            
            # Initialize new entry with date
            current_entry = {'title': '', 'company': '', 'date': line, 'description': ''}
        
        # Bullet point - description
        elif '•' in line:
            if not current_entry:
                current_entry = {'title': '', 'company': '', 'date': '', 'description': ''}
            line_clean = line.lstrip('•').strip()
            if current_entry.get('description'):
                current_entry['description'] += ' | ' + line_clean
            else:
                current_entry['description'] = line_clean
        
        # Check for capitalized lines (potential company or title)
        elif line[0].isupper() and len(line) < 100:
            if not current_entry:
                current_entry = {'title': '', 'company': '', 'date': '', 'description': ''}
            
            # Determine if this is company or title based on keywords
            if has_company or ('Inc' in line or 'Corp' in line or 'Ltd' in line):
                current_entry['company'] = line
            else:
                current_entry['title'] = line
    
    # Don't forget the last entry
    if current_entry and (current_entry.get('title') or current_entry.get('company')):
        experience_entries.append(current_entry)
    
    return experience_entries


def parse_project_entries(project_lines: List[str]) -> List[Dict[str, str]]:
    """
    Parse projects section into structured entries with name, description, technologies.
    """
    project_entries = []
    current_project = {}
    
    for line in project_lines:
        line = line.strip()
        if not line:
            continue
        
        # Technology/tools (after "Tech:", "Tools:", "Technologies:")
        if re.search(r'(tech|tools|technologies|stack):', line, re.IGNORECASE):
            if current_project:
                current_project['technologies'] = re.sub(r'(tech|tools|technologies|stack):\s*', '', line, flags=re.IGNORECASE)
            else:
                current_project = {'name': '', 'description': '', 'technologies': line}
        # Project name (usually at start, title-cased, followed by description)
        # Detect as new project if it starts with capital letter, is relatively short, and no bullets yet
        elif (not current_project or (current_project.get('name') and current_project.get('description'))) and \
             line[0].isupper() and len(line) < 80 and '•' not in line:
            # Save previous project if exists and has content
            if current_project and (current_project.get('name') or current_project.get('description')):
                project_entries.append(current_project)
            current_project = {'name': line, 'description': '', 'technologies': ''}
        # Bullet point description or regular text
        elif current_project:
            line_clean = line.lstrip('•').strip()
            if line_clean:
                if current_project.get('description'):
                    current_project['description'] += ' | ' + line_clean
                else:
                    current_project['description'] = line_clean
    
    if current_project and (current_project.get('name') or current_project.get('description')):
        project_entries.append(current_project)
    
    return project_entries


def parse_resume_enhanced(raw_text: str) -> Dict[str, any]:
    """
    Enhanced resume parsing with improved section detection and structured data extraction.
    """
    # Check if text is mostly on one line (common with PyMuPDF)
    lines = raw_text.split('\n')
    if len(lines) <= 3:  # Single line or very few lines
        return parse_resume_single_line(raw_text)
    
    # Clean lines
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    
    # Extract name from the top of the resume
    name = extract_name(raw_text)
    
    # Extract contact information
    contact_info = extract_contact_info(raw_text)
    
    # Try simple section extraction first
    education_lines = extract_section_simple(lines, "EDUCATION")
    experience_lines = extract_section_simple(lines, "EXPERIENCE")
    projects_lines = extract_section_simple(lines, "PROJECTS")
    skills_section = extract_section_simple(lines, "SKILLS")
    
    # If simple extraction didn't work, try advanced
    if not education_lines:
        education_lines = extract_section_advanced(lines, ['education', 'academic', 'qualifications', 'degree', 'university', 'college'])
    
    if not experience_lines:
        experience_lines = extract_section_advanced(lines, ['experience', 'work', 'employment', 'career', 'professional'])
    
    if not projects_lines:
        projects_lines = extract_section_advanced(lines, ['projects', 'project', 'portfolio', 'works'])
    
    if not skills_section:
        skills_section = extract_section_advanced(lines, ['skills', 'technical skills', 'technologies', 'programming', 'languages', 'tools'])
    
    # Parse each section into structured entries
    education = parse_education_entries(education_lines)
    experience = parse_experience_entries(experience_lines)
    projects = parse_project_entries(projects_lines)
    skills = extract_skills_advanced(skills_section)
    
    # Create parsed data
    parsed_data = {
        'name': name,
        'contact': contact_info,
        'education': education,
        'experience': experience,
        'projects': projects,
        'skills': skills,
        'raw_text': raw_text
    }
    
    # Add metadata
    parsed_data['metadata'] = {
        'total_lines': len(lines),
        'sections_found': [k for k, v in {'education': education, 'experience': experience, 'projects': projects, 'skills': skills}.items() if v],
        'contact_info_found': bool(contact_info),
        'name_found': bool(name)
    }
    
    logging.info(f"Parsed resume: Name='{name}', "
                f"{len(education)} education, "
                f"{len(experience)} experience, "
                f"{len(projects)} projects, "
                f"{len(skills)} skills")
    
    return parsed_data


def parse_resume(raw_text: str) -> Dict[str, any]:
    """
    Main resume parsing function (backward compatibility).
    """
    return parse_resume_enhanced(raw_text)


def analyze_resume_quality(parsed_data: Dict[str, any]) -> Dict[str, any]:
    """
    Analyze the quality and completeness of parsed resume data.
    """
    analysis = {
        'completeness_score': 0,
        'missing_sections': [],
        'recommendations': [],
        'strengths': []
    }
    
    total_sections = 4  # education, experience, projects, skills
    found_sections = 0
    
    # Check each section
    if parsed_data.get('education'):
        found_sections += 1
        analysis['strengths'].append('Education information found')
    else:
        analysis['missing_sections'].append('Education')
    
    if parsed_data.get('experience'):
        found_sections += 1
        analysis['strengths'].append('Work experience found')
    else:
        analysis['missing_sections'].append('Experience')
    
    if parsed_data.get('projects'):
        found_sections += 1
        analysis['strengths'].append('Project portfolio found')
    else:
        analysis['missing_sections'].append('Projects')
    
    if parsed_data.get('skills'):
        found_sections += 1
        analysis['strengths'].append(f'Skills found ({len(parsed_data["skills"])} skills)')
    else:
        analysis['missing_sections'].append('Skills')
    
    # Calculate completeness score
    analysis['completeness_score'] = (found_sections / total_sections) * 100
    
    # Generate recommendations
    if analysis['completeness_score'] < 75:
        analysis['recommendations'].append('Consider adding missing sections to improve resume completeness')
    
    if len(parsed_data.get('skills', [])) < 5:
        analysis['recommendations'].append('Add more technical skills to showcase your capabilities')
    
    if len(parsed_data.get('projects', [])) < 2:
        analysis['recommendations'].append('Include more projects to demonstrate practical experience')
    
    return analysis


if __name__ == "__main__":
    # Test the enhanced parser
    test_text = """
    JOHN DOE
    john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology, 2020-2024
    
    EXPERIENCE
    Software Engineer Intern
    Tech Company Inc., Summer 2023
    • Developed web applications using React and Node.js
    • Collaborated with team of 5 developers
    
    PROJECTS
    AI Chatbot Application
    • Built using Python, TensorFlow, and Flask
    • Implemented natural language processing
    
    SKILLS
    Programming Languages: Python, JavaScript, Java, C++
    Frameworks: React, Node.js, Django, Flask
    Tools: Git, Docker, AWS, MongoDB
    """
    
    result = parse_resume_enhanced(test_text)
    print("Parsed Resume Data:")
    for key, value in result.items():
        if key != 'raw_text':
            print(f"{key}: {value}")
    
    # Analyze quality
    quality = analyze_resume_quality(result)
    print(f"\nQuality Analysis:")
    print(f"Completeness Score: {quality['completeness_score']}%")
    print(f"Strengths: {quality['strengths']}")
    print(f"Recommendations: {quality['recommendations']}")
