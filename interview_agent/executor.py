import time
from interview_agent.logger import JsonLogger
from interview_agent.exceptions import SkillValidationError
from interview_agent.utils import extract_json
from pydantic import ValidationError


class SkillExecutor:
    def __init__(self, skill_engine, retries=2, logger=None):
        self.engine = skill_engine
        self.retries = retries
        self.logger = logger or JsonLogger()

    def run(self, *, skill: str, input, schema, trace):
        for attempt in range(self.retries):
            start = time.time()

            try:
                self.logger.log(
                    event="skill_execution_started",
                    interview_id=trace.interview_id,
                    trace_id=trace.trace_id,
                    skill=skill,
                    attempt=attempt + 1,
                )

                raw = self.engine.run_skill(
                    skill=skill,
                    user_input=input
                )
                
                parsed = extract_json(raw)

                validated = schema.model_validate(parsed)

                duration = round(time.time() - start, 3)

                self.logger.log(
                    event="skill_execution_success",
                    interview_id=trace.interview_id,
                    trace_id=trace.trace_id,
                    skill=skill,
                    duration_sec=duration,
                )

                return validated

            except ValidationError as ve:
                self.logger.log(
                    event="skill_validation_failed",
                    interview_id=trace.interview_id,
                    trace_id=trace.trace_id,
                    skill=skill,
                    error=str(ve),
                )

            except Exception as e:
                self.logger.log(
                    event="skill_execution_error",
                    interview_id=trace.interview_id,
                    trace_id=trace.trace_id,
                    skill=skill,
                    error=str(e),
                )

        raise SkillValidationError(
            f"Skill '{skill}' failed after {self.retries} attempts"
        )