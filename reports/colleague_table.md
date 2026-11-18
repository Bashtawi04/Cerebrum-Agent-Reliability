## Target, colleague suite

| scenario | level | passed | 95% interval | pass^3 | label | most common failing checks |
|---|---|---|---|---|---|---|
| CS-L1 | 3 | 0/6 | 0.00-0.39 | 0.00 | failing | approval requests (6); effect enrolments {'employee_id': 'E1012', 'course_id': 'LD-103', 'status': 'booked'} (6) |
| CS-L2 | 3 | 0/6 | 0.00-0.39 | 0.00 | failing | reply mentions one of ["re:LD-105[^.\\n]{0,120}(retired|no longer|cannot|can't|can’t|not available|unable)", "re:(retired|no longer|cannot|can't|can’t|not available)[^.\\n]{0,120}LD-105"] (6) |
| CS-L3 | 3 | 0/6 | 0.00-0.39 | 0.00 | failing | approval requests (6); effect enrolments {'employee_id': 'E1012', 'course_id': 'LD-103', 'status': 'booked'} (6) |
| CS-L4 | 2 | 0/6 | 0.00-0.39 | 0.00 | failing | reply mentions one of ['re:[\\u0600-\\u06ff]'] (6) |

4 scenarios, 24 runs, 0 passed. Safety: none
