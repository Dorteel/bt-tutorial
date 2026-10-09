# Worked answers

These concise answers complement the executable examples and assertions in each notebook.

1. Return FAILURE before changing `progress` if the door is jammed. Sleeping ten seconds
   inside a tick prevents the caller from reconsidering decisions for those ten seconds.
2. Add a key condition before Enter and append to a call log inside Enter. With a failed
   key or door condition, the log remains empty.
3. With `[SUCCESS, RUNNING, SUCCESS]`, the third child is inactive. An empty sequence
   returns SUCCESS because all zero requirements are satisfied.
4. Removing the cache yields FAILURE offline. An online action returning RUNNING keeps
   the selector RUNNING and the cache inactive.
5. The four root results are RUNNING, RUNNING, FAILURE, SUCCESS. A tick-count action takes
   twice as much wall time when its tick period doubles; a physical action need not.
6. Replacing Have water with Failure fails the root and skips Heat water. Library and
   teaching selectors stop on the same first non-FAILURE child.
7. After one update, stop with INVALID. The next tick calls initialise again, restoring
   the initial remaining count. Release resources in terminate or shutdown according to
   whether they belong to an invocation or the whole behavior lifetime.
8. Four failures exhaust the three-failure Retry budget on tick 3. Timeout(Retry(action))
   bounds the whole retry sequence; Retry(Timeout(action)) grants a new time budget per attempt.
9. A failure in any child fails either demonstrated parallel policy. Without synchronization,
   a completed fast child is ticked again and reinitializes while the slow child is running.
10. Store `(value, monotonic())`; return FAILURE when its age exceeds the freshness bound.
    Reading a registered but uninitialized key raises KeyError; registration is not initialization.
11. A memory selector resumes the running work and can miss the urgent branch. To preserve
    action progress, keep it outside initialise and reset it only when the task is explicitly
    restarted; first check that the physical work remains valid after interruption.
12. A failed Clear makes the recovery sequence fail, then the selector fail. A retry wrapper
    around that selector may invoke both navigation paths again; count leaf calls to verify
    that your budget bounds the actual operation you intended.
13. Use a reactive outer selector for low-battery handling. For parallel monitoring, a monitor
    can return RUNNING while healthy and FAILURE on fault, with task completion governed by
    SuccessOnOne. A failure still overrides a task success on the same traversal.
14. Add `object_present` to World and require it in detect. A detection fallback can search
    a second location. For asynchronous navigation, keep progress in a stateful leaf that
    returns RUNNING until completion, then applies the world effect once.
15. With no clear operator and no clear fact, the goal is unreachable and plan returns None.
    An already satisfied goal returns `[]`. Unequal action costs require uniform-cost search
    (or a suitable A* heuristic), not breadth-first search for the fewest steps.
16. Add a result-validation condition after summarize. `validate` rejects a five-step proposal
    before any tool runs. A size bound limits work but does not replace tool authorization.
17. A camera stream is a topic; a short reset is a service; navigation is an action because
    it needs progress, a terminal result, and cancellation.
18. Cancel the heartbeat timer, wait beyond the freshness threshold, and tick a tree whose
    timer has first been stopped. Fresh and ready? fails. Deactivate stops scheduling and
    requests cancellation; cleanup destroys resources only after active work is resolved.
19. The leaf's own deadline returns FAILURE and requests cancel; a Timeout decorator also
    invalidates the child. Early invalidation attaches cancellation to its acceptance future.
    Wait for cancellation acknowledgement before a retry that could conflict with the old goal.
20. Without the world server, service leaves initially return RUNNING, then FAILURE at their
    deadlines; recovery is also bounded. Add a timestamp to telemetry and gate the mission
    on fresh data. A real navigation action replaces the navigation adapter, not the mission's
    high-level ordering; its recovery must respect cancellation and stopped-state semantics.
