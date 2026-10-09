# Exercise guide

Each notebook ends with concrete exercises. Use the notebook's own initialized state,
change one condition at a time, and predict the next status before running it. Reset or
rerun the setup cell between experiments. These hints preserve room to discover the result.

| Lesson | Hint |
|---|---|
| 01 | Check the jam before incrementing progress. |
| 02 | Record calls to Enter in a list to prove a guard skips it. |
| 03 | A sequence returns as soon as it sees something other than SUCCESS. |
| 04 | RUNNING is not a reason to fall back. |
| 05 | Count requests to Move, not just requests to the root. |
| 06 | Keep status spelling the same when comparing engines. |
| 07 | initialise owns per-invocation state. |
| 08 | The outer decorator defines the larger policy boundary. |
| 09 | Inspect the fast child's event list, not only its final status. |
| 10 | Store observation time alongside observation value. |
| 11 | A memory selector can skip the new urgent condition. |
| 12 | Count attempts separately from root ticks. |
| 13 | A monitor that never succeeds prevents SuccessOnAll completion. |
| 14 | Put missing-object truth in the world, not a hidden tree variable. |
| 15 | An empty plan and no plan have different meanings. |
| 16 | Validate the complete proposal before calling any tool. |
| 17 | Match communication lifetime to operation lifetime. |
| 18 | Keep the executor alive while the heartbeat is stopped. |
| 19 | Cancellation can arrive before goal acceptance is visible to the client. |
| 20 | A missing server is RUNNING until the request deadline expires. |

See [worked answers](../solutions/README.md) after attempting the experiments.
