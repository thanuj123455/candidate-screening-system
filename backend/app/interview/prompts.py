QUESTION_GENERATION_PROMPT = """
You are a senior technical interviewer at a top-tier tech company.
You are interviewing a candidate for the role of: {role}

Candidate profile from their resume:
{resume_summary}

Relevant knowledge base context (use this to ground your questions):
---
{context}
---

Already asked questions (avoid repetition):
{asked_questions}

Instructions:
- Generate exactly 1 technical interview question.
- The question must be specific to the candidate's background AND the role.
- It should test DEEP understanding, not surface-level recall.
- Vary between: conceptual understanding, system design, debugging scenarios, and implementation.
- Current difficulty target: {difficulty}
- Do NOT ask generic HR or behavioural questions.
- Return ONLY the question text. No preamble, no numbering.
"""

FOLLOW_UP_PROMPT = """
You are a senior technical interviewer.
The candidate was asked: {original_question}
They answered: {candidate_answer}

Generate 1 targeted follow-up question that:
- Probes a gap or assumption in their answer
- Asks them to go deeper on a specific aspect
- Is technically rigorous

Return ONLY the follow-up question. No preamble.
"""

REPORT_GENERATION_PROMPT = """
You are a senior hiring manager. Assess the interview below and return ONLY a valid JSON object — no markdown, no explanation outside the JSON.

Role: {role}

Candidate profile:
{resume_summary}

Interview transcript:
{transcript}

Return exactly this JSON structure (keep summary to 3 sentences max):
{{
  "summary": "3 sentence assessment",
  "strengths": ["up to 3 strengths"],
  "weaknesses": ["up to 3 weaknesses"],
  "overall_score": <integer 0-100>,
  "recommendation": "Hire",
  "per_question_scores": [
    {{"question": "Q1 short label", "score": <0-10>, "comment": "1 sentence"}}
  ]
}}

recommendation must be exactly one of: "Hire", "Maybe", "Reject".
Return ONLY the JSON object. No text before or after.
"""
