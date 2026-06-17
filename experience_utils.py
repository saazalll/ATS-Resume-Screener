import re
from typing import List

def estimate_years_of_experience(dates: List[str]) -> int:
    """
    Builds a simple heuristic for total estimated years of experience from extracted date ranges.
    Returns an integer representing estimated years.
    """
    total_years = 0
    seen_years = set()
    
    for d in dates:
        d = d.lower()
        
        # Literal "X years"
        match = re.search(r'(\d+)\s*(?:year|yr)', d)
        if match:
            val = int(match.group(1))
            if val < 40: # sanity check
                total_years += val
            continue
            
        # Date Ranges e.g., 2018 - 2021
        match = re.search(r'(20\d{2}|19\d{2})\s*(?:-|to|–)\s*(20\d{2}|19\d{2}|present|now)', d)
        if match:
            start_yr = int(match.group(1))
            end_str = match.group(2)
            
            if end_str in ['present', 'now']:
                end_yr = 2026 # Assuming current year or slightly future
            else:
                end_yr = int(end_str)
                
            if end_yr >= start_yr:
                diff = end_yr - start_yr
                # Avoid double counting exact same range duration if parsed weirdly
                range_tuple = (start_yr, end_yr)
                if range_tuple not in seen_years:
                    seen_years.add(range_tuple)
                    total_years += diff
                    
    return total_years
