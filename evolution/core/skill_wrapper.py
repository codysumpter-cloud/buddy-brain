import dspy
from typing import List, Tuple

class SkillSignature(dspy.Signature):
    """
    Standard signature for evolving a skill.
    Input: The task and the skill instructions.
    Output: The agent's response following the skill.
    """
    task = dspy.InputField(desc="The specific task to perform")
    skill_instructions = dspy.InputField(desc="The procedural instructions (SKILL.md)")
    response = dspy.OutputField(desc="The result of following the skill")

class SkillEvolutionWrapper:
    def __init__(self, skill_path: str):
        self.skill_path = skill_path
        with open(skill_path, 'r') as f:
            self.instructions = f.read()

    def wrap_as_module(self):
        # Wraps the skill as a Predictor using the SkillSignature
        return dspy.Predict(SkillSignature)

    def run_task(self, predictor, task: str) -> str:
        # Executes the predictor with the current skill instructions
        result = predictor(task=task, skill_instructions=self.instructions)
        return result.response
