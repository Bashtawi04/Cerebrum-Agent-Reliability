Handle null trace messages without losing audit evidence, and add boundary tests for the lab's statistics and honesty rules. This is the first of three replacement reviews; Learning and Onboarding evidence follow in dependent branches.

Validation: 59 local tests, 232 protected input hashes, supplied tables, gate and honesty controls. The 47 original tests and frozen inputs are unchanged. CI is configured for Python 3.10/3.12; hosted results must be checked after push. No model calls or agent changes.

The previous combined submission remains in PR #1 for review history. No Phase 2 housekeeping is included here.
