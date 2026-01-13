---
name: jd-parser
description: Parse technical job descriptions into a structured JSON schema including role title, seniority, required skills, responsibilities, qualifications, and domain context. Use when users provide a job description to analyze.
---

# Skill: Job Description Parser

This Skill teaches Claude how to parse a technical job description into a structured JSON output based on a schema. When provided with a job description text, Claude should produce the JSON exactly matching the schema below — and only the JSON, no extra text or explanation.

## JSON Output Schema

Produce JSON conforming to this structure:

```json
{
  "role_title": "...",
  "seniority": "...",
  "skills": ["...", "..."],
  "responsibilities": ["...", "..."],
  "qualifications": ["...", "..."],
  "nice_to_have": ["...", "..."],
  "domains": ["...", "..."],
  "outputs_schema_version": "1.0"
}
```

## Field Definitions
1.	role_title (string): The official job title.
2.	seniority (string): One of “Intern”, “Junior”, “Mid”, “Senior”, “Lead”, “Principal”. Use context from the text.
3.	skills (array): List of hard technical skills (languages, frameworks, tools).
4.	responsibilities (array): Core duties and tasks expected.
5.	qualifications (array): Required education, certifications, or experience.
6.	nice_to_have (array): Optional but beneficial experience/skills.
7.	domains (array): High-level domain context (e.g., Cloud, AI/ML, FinTech).
8.	outputs_schema_version (string): Always output "1.0" for this schema version.

## Parsing Instructions
- Focus on explicit mentions in the job description text.
- If a field is not evident, output an empty list (for arrays) or an empty string (for text).
- Use bullet extraction and phrase grouping for list fields.
- Populate all fields in the schema with reasonable inference from the job description.
- Return only JSON.

## Purpose
Extract key topics, required skills, and core technical areas from a job description.

## Input/Example
- Raw job description string
- Example: "Senior Python Backend Engineer with 5+ years of experience building microservices. Must know AWS, Docker, Kubernetes. Responsibilities include API design, performance optimization. Nice to have leadership experience."

## Output
```json
{
  "role_title": "Senior Python Backend Engineer",
  "seniority": "Senior",
  "skills": ["Python", "AWS", "Docker", "Kubernetes", "Microservices"],
  "responsibilities": ["API design", "performance optimization"],
  "qualifications": ["5+ years experience"],
  "nice_to_have": ["leadership experience"],
  "domains": ["Backend Engineering", "Cloud"],
  "outputs_schema_version": "1.0"
}
```
