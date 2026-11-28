Add the ten Learning Coach scenarios and evidence from the mentors' 25 November runs. Original predictions and recordings are retained. Findings now cover the dropped draft and contaminated approval message, with reproduction steps and code causes.

LAB-LRN-06 previously required one lookup route and missed the message problem. The revised capability case removes that route requirement while retaining approval/no-write checks. The original result is 18/30; revised assertions yield 17/30 on the same saved traces, not a new target run. Language matching is presented as an optional suggestion.

Validation: 64 local tests; ten valid scenarios; thirty returned traces; 26 earlier failed runs classified; good/bad scripted checks pass for their intended causes. Target code and protected inputs are unchanged. Hosted checks and peer exchange remain pending.

Base: phase3-lab-review. Own Onboarding evidence is a separate dependent review. Original PR #1 remains available for history.
