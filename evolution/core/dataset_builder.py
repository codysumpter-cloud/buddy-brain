import json
from typing import List, Dict

class EvalDatasetBuilder:
    def __init__(self, skill_name: str):
        self.skill_name = skill_name

    def generate_synthetic_cases(self, count: int = 10) -> List[Dict]:
        # In a real impl, this would call a strong LLM to generate pairs
        # For the scaffold, we return structural placeholders
        return [
            {"task": f"Synthetic task {i} for {self.skill_name}", "expected": "Rubric-based success criteria"}
            for i in range(count)
        ]

    def save_dataset(self, data: List[Dict], path: str):
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
