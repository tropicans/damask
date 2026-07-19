import re
import json
import os

def recommend_masking_rules(headers: list[str], rules_config_path: str) -> dict[str, str]:
    if not os.path.exists(rules_config_path):
        return {header: "No Masking" for header in headers}
        
    with open(rules_config_path, 'r', encoding='utf-8') as f:
        rules = json.load(f)
        
    recommendations = {}
    for header in headers:
        matched = False
        normalized_header = header.lower().strip()
        for rule_name, patterns in rules.items():
            for pattern in patterns:
                if re.search(pattern, normalized_header):
                    recommendations[header] = rule_name
                    matched = True
                    break
            if matched:
                break
        if not matched:
            recommendations[header] = "No Masking"
            
    return recommendations
