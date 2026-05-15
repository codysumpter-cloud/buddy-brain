from evolution.core.skill_wrapper import SkillEvolutionWrapper
from evolution.core.dataset_builder import EvalDatasetBuilder

def main(skill_name: str):
    print(f"Initializing evolution for skill: {skill_name}")
    # Assume skills are in skills/ directory for this demo
    path = f"skills/{skill_name}/SKILL.md" 
    
    try:
        wrapper = SkillEvolutionWrapper(path)
        builder = EvalDatasetBuilder(skill_name)
        dataset = builder.generate_synthetic_cases()
        print(f"Generated {len(dataset)} synthetic test cases.")
        print("Ready for GEPA optimization loop.")
    except FileNotFoundError:
        print(f"Error: Skill file {path} not found.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Usage: python -m evolution.skills.evolve_skill <skill_name>")
