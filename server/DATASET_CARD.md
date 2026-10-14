# NASAN Scholarship Dataset Card

## Purpose

`scholarships.json` is the retrieval catalog for NU Laguna scholarship and discount assistance. Each record contains the scholarship name, minimum GWA, year-level restriction, program restriction, affiliation preference, required documents, and deadline.

## Coverage

The catalog contains 18 records covering incoming first-year students, incoming Grade 11 students, continuing students, NU SHS graduates, academic awards, family and affiliation discounts, PWD assistance, and public-service dependents. It intentionally includes both percentage GWA values for incoming students and CGWA values for continuing students.

## Quality and limitations

- Records are structured JSON with a consistent schema and UTF-8 encoding.
- The catalog has meaningful variety across student type, grade scale, program, and affiliation.
- `Not specified` values are preserved rather than invented by the chatbot.
- This is a small domain catalog, not a broad conversational corpus. The current system supplements it with labeled intent examples in `evaluate.py` and explicit rule coverage in `entity_extractor.py`.
- Scholarship policies and deadlines can change. The catalog should be reviewed against the official NU source before production use.

## Intended use

Use the records for scholarship lookup and eligibility guidance. Do not treat a match as an official award decision; direct students to SDAO for confirmation.