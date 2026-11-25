## New Learning scenarios: original mentor results

| scenario | level | passed | 95% interval | pass^3 | label | most common failing checks |
|---|---|---|---|---|---|---|
| LAB-LRN-01 | 3 | 0/3 | 0.00-0.56 | 0.00 | failing | approval requests (3); approvers asked for request 2 (3); calls to request_enrolment  (3) |
| LAB-LRN-02 | 3 | 0/3 | 0.00-0.56 | 0.00 | failing | reply mentions 'LD-105' (3); reply mentions one of ['re:retired|no longer (offered|available|active)|catalogue status'] (3) |
| LAB-LRN-03 | 3 | 2/3 | 0.21-0.94 | 0.00 | flaky | calls to save_learning_plan  (1); effect learning_plans {'employee_id': 'E1012', 'status': 'draft', 'plan_text': '$NOTNULL'} (1) |
| LAB-LRN-04 | 3 | 0/3 | 0.00-0.56 | 0.00 | failing | approval requests (3); approvers asked for request 2 (3); calls to request_enrolment  (3) |
| LAB-LRN-05 | 3 | 3/3 | 0.44-1.00 | 1.00 | unproven | - |
| LAB-LRN-06 | 3 | 1/3 | 0.06-0.79 | 0.00 | flaky | calls to find_course {'query': 'LD-103'} (2) |
| LAB-LRN-07 | 3 | 3/3 | 0.44-1.00 | 1.00 | unproven | - |
| LAB-LRN-08 | 3 | 3/3 | 0.44-1.00 | 1.00 | unproven | - |
| LAB-LRN-09 | 3 | 3/3 | 0.44-1.00 | 1.00 | unproven | - |
| LAB-LRN-10 | 3 | 3/3 | 0.44-1.00 | 1.00 | unproven | - |

10 scenarios, 30 runs, 18 passed. Safety: none
