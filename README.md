# Distributed-Replicated-Key-Val-Store

## High-Level Approach:

- As a first step for this project I did a lot of reading on Raft. The following summarized key-takeaways from that research.
  - Raft and Paxos are two widely used consensus algorithms, Raft being the easier one to understand and learn.
  - Consensus algorithms are used to synchronize multiple machines to work together.
  - Raft was actually constructed in order to be a more understandable version of paxos and differs in the following roles:
    - Strong leader. 
    - Randomized timers to elect new leaders.
    - Membership changes to allow clusters to operate as usual in the midst of config changes.
  - Replicated state machines are the way that consensus algorithms are msot commonly used.
  - It is the job of the consensus algorithm to keep the replicated log consistent with the following in mind:
    - Safety/Accuracy.
    - Availability.
    - Not dependent on clocks, as this can cause problems with availability should they become un-synced.
    - The faster majority determines the speed of certain function completion, as to not worry about the slower minority.
  - Raft implements consensus by first electing a leader:
    - Accepts logs from clients.
    - Replicates out on other servers. (these two steps define what a "strong leader" is)
    - Tells when it is safe to applu log entries to their state machines. 
    - If a leader fails or disconnects, a new election process starts.
  - The leader problem addresses 3 sub-problems:
    - Leader election.
    - Log Replication.
    - Safety.
  - A server can be one of 3 states:
    - Leader.
    - Follower.
    - Candidate.
  - Raft servers communicate through remote procedure calls (RPCs)
    - RequestVote initiated by candidates.
    - AppendEntries replicate log entries and serve as a heart beat.
  - It is possible to have split election results, but Raft uses randomized elction tinmeouts to solve this. 
  - Leaders send entries as log updates and fills everyone in on when it safe to commit these entries.

## Challenges Faced:



## Testing:



## Resources:
- Raft concepts: https://raft.github.io/raft.pdf
