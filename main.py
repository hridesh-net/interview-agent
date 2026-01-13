from skill_engine import SkillEngine, SkillRegistry
from llm.huggingface_client import HuggingFaceClient

registry = SkillRegistry()
registry.load("./skills")

llm = HuggingFaceClient(
    model_id="meta-llama/Llama-3.1-8B-Instruct:novita"
)
print("Using model:", llm.model)

engine = SkillEngine(registry, llm)

print("Available skills:", registry.list_metadata())

# print(engine.run("Generate Terraform for an S3 bucket"))

# Run
response = engine.run(
    """A Java Developer designs, develops, tests, and maintains Java-based applications, focusing on writing clean, efficient, scalable code for web, mobile, or enterprise systems, working within the full software development lifecycle (SDLC), collaborating with teams, and ensuring high performance and reliability by analyzing requirements, debugging issues, and integrating systems, often using frameworks like Spring and REST APIs. 
Key Responsibilities:
Design & Development: Architecting and building new Java applications, contributing to all phases of the SDLC, from concept to deployment.
Coding: Writing high-quality, efficient, testable, and maintainable Java code.
Testing & Debugging: Conducting software analysis, debugging, troubleshooting, and fixing issues.
Collaboration: Working with cross-functional teams (QA, product managers, other engineers) to gather requirements and deliver features.
Performance & Optimization: Optimizing applications for speed, scalability, and security.
Documentation: Creating technical documentation and user guides.
Integration: Integrating applications with external systems and front-end elements. 
Key Skills & Technologies:
Strong understanding of Java fundamentals and Object-Oriented Programming (OOP).
Experience with Java EE, Spring Framework, Hibernate, or other relevant frameworks.
Proficiency with RESTful APIs and web services.
Familiarity with databases (SQL/NoSQL) and ORM tools.
Experience with build tools (Maven/Gradle) and version control (Git).
Knowledge of Agile/Scrum methodologies. 
Senior Java Developer Focus:
Mentoring junior developers.
Leading project planning and architectural discussions.
Aligning technical solutions with broader business goals.
Managing large-scale, mission-critical systems. """)

print("----- Response -----")
print(response)