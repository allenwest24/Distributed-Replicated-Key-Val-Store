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
- This was the portion of the task I expected to complete by the milsetone.
- I started by following the recommended path of development in the project description but quickly veered off due to a low attention span.
- I implemented a easy version of put and get using a dict and not utilizing the log vs commit portion of RAFT quite yet. 
- From there I implemented the election process to its full potential which took a long time.

## Challenges Faced:
- The concepts of this project definitely took a long time to learn, and it was almost impossible for me to jump into this without reading very carefully everything about RAFT.
- Another challenge was the election process because there were so many moving parts. It was tough to differentiate when to listen to votes and when to reset the states of all parrticipating nodes.
- Consistency is another key issue for my algorithm currently and I think it is due to the fact that I am not using confirmations and sends the same way I'm doing the heartbeats. Essentially, in my version heartbeats and puts are not the same tye of messages and I think I need to change this for better consistency.
- If I set the timeouts to be a small and quick range, there are too many ties. I think once I implement this in Go I will illiminate this problem.

## Testing:
- I have been using the test.py and run.py script tor un simulations to test this implementation.
- In addition to this I used a lot of print statements to see the exact flow and progress and this helped me debug faster.

## Resources:
- Raft concepts: https://raft.github.io/raft.pdf
