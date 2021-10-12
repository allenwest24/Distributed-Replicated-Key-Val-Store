#!/usr/bin/env python
# Imports.

import sys, socket, select, time, json, random

#--------------------------------------------------------------------------------------------------
# Global Variables.

# The method chosen to store is obviously a key-val struct.
log = {}
kvs = {}
# When servers start up, they begin as followers.
state = "follower"
# This servers as the election timeout for this server.
elec_to = round(random.uniform(0.5, 10), 6) #TODO: Make this smaller once election bugs are fixed.
# The term we are on.
term = 0
# Default of no.
voted_this_term = False
# If leader is unknown we use 'FFFF'.
leader = 'FFFF'
# Track our votes received in this term.
votes_for_me = 0
# Start with current time.
last = time.time()

#--------------------------------------------------------------------------------------------------
# Global Constants.

# Your ID number
my_id = sys.argv[1]
# The ID numbers of all the other replicas
replica_ids = sys.argv[2:]
# Connect to the network. All messages to/from other replicas and clients will
# occur over this socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
sock.connect(my_id)

#--------------------------------------------------------------------------------------------------
# Helper Methods.

# Depending on terms specified elsewhere, this will start a new election for a leader.
def begin_election():
  # Import the necessary global variables.
  global state
  global term
  global voted_this_term
  global votes_for_me
  global leader

  #print(str(leader) + " has been dethroned as leader.")
  #print(str(my_id) + " becomes a candidate!")
  # To begin an election, a follower increments its current term.
  term += 1
  # Transition to candidate state.
  state = 'candidate'
  # The candidate will vote for itself.
  votes_for_me += 1
  voted_this_term = True
  # The leader cannot declare itself the leader until it receives the majority vote, so the leader becomes unknown and the rfv message will trigger the other servers to change this on their end as well.
  leader = 'FFFF'

  # Issue RequestVote RPC to each of the other servers in the cluster.
  requestvotemsg = {'type': 'rvm', 'src': my_id, 'dst': 'FFFF', 'leader': 'FFFF', 'term': term}
  sock.send(json.dumps(requestvotemsg))
  return

#--------------------------------------------------------------------------------------------------
# Main Algorithm.

while True:
  # Find the availability of the socket.
  ready = select.select([sock], [], [], 0.1)[0]
  if sock in ready:
    # Receive and decode client requests.
    msg_raw = sock.recv(32768)
    if len(msg_raw) == 0: continue
    msg = json.loads(msg_raw)

    # Handle redirect requests.
    # TODO: Implement.
    #if msg['type'] == 'redirect':
        #print('redirect message received.')

    # If requests are of type GET or PUT.
    if msg['type'] in ['get', 'put']:
      msg_back = {}

      # If we received a PUT request.
      if msg['type'] == 'put':
        # Put requests should go through the leader. Therefore, we only actually handle them if they come from the leader or if we ARE the leader.
        # This implementation is called 'strong leader'.
        if msg['src'] == leader:
          # The leader accepts log entries from clients.
          log[msg['key']] = msg['value']
          kvs[msg['key']] = msg['value']
          msg_back['type'] = 'ok'
          # The leader will replicate log entries on the other servers.
        elif leader == my_id:
          kvs[msg['key']] = msg['value']
          replicated_log = {'src': my_id, 'dst': 'FFFF', 'MID': msg['MID'], 'type': 'put', 'key': msg['key'], 'value': msg['value'], 'leader': leader}
          sock.send(json.dumps(replicated_log))
          msg_back['type'] = 'ok' 
        # There is no current leader yet, try again shortly.
        elif leader == 'FFFF':
          #msg_back['type'] = 'fail'
          msg_back['type'] = 'redirect'
        # Redirect to the actual leader.
        else:
          msg_back['type'] = 'redirect'
        # Construct a response message.
        msg_back['src'] = my_id
        msg_back['dst'] = msg['src']
        msg_back['leader'] = leader
        msg_back['MID'] = msg['MID']

      # If we received a GET request.
      elif msg['type'] == 'get':
        # The strong leader requirements here are the same as for put() requests.
        if msg['src'] == leader or leader == my_id:
          # If we have the key-val for this GET request.
          if msg['key'] in kvs:
            msg_back['type'] = 'ok' 
            msg_back['value'] = kvs[msg['key']] 
          # If the GET request fails.
          else:
            msg_back['type'] = 'fail'
        # If there is no elected leader yet, we will try again in a little bit.
        elif leader == 'FFFF':
          msg_back['type'] = 'fail'
        # Enforce strong leadership.
        else:
          msg_back['type'] = 'redirect'

        # Forge the rest of the message.  
        msg_back['src'] = my_id
        msg_back['dst'] = msg['src']
        msg_back['leader'] = leader
        msg_back['MID'] = msg['MID']

      elif msg['type'] == 'commit':
          del log[msg['key']]
          kvs[msg['key']] = msg['value']

      # Regardless of the message changes that were made above, send the previously constructed message.
      sock.send(json.dumps(msg_back))

    # Handle heartbeats.
    # If the supposed leader's term is at least as big as the current server's term, then we recognize the leader as legitimate.
    # Otherwise we reject and continue in the current state.
    elif msg['type'] == 'hb' and msg['term'] >= term:
      last = time.time()
      leader = msg['leader']
      term = msg['term']
      state = 'follower'
      votes_for_me = 0
      voted_this_term = False
    
    # If request to vote is received and we haven't voted, update term, vote, update that we have voted this term.
    elif msg['type'] == 'rvm':
      if msg['term'] > term:
        leader = 'FFFF'
        voted_this_term = False
        term = msg['term']
        state = 'follower'
        votes_for_me = 0
      if not voted_this_term:
        last = time.time()
        vote = {'src': my_id, 'dst': msg['src'], 'type': 'vote', 'leader': leader, 'term': term}
        sock.send(json.dumps(vote))
      voted_this_term = True
    
    # If we receive a vote.
    elif msg['type'] == 'vote':
      if msg['term'] == term and leader == 'FFFF':
        votes_for_me += 1
        # The required amount of votes is a majority (half plus themselves.)
        # This allows both a lot of room for failed servers, as well as insurance that there will only be one leader at a time.
        if votes_for_me >= len(replica_ids) / 2 and state == "candidate":
          # This candidate has won.
          # Send a heartbeat to all other servers to establish the authority and to prevent new elections.
          heartbeat = {'src': my_id, 'dst': 'FFFF', 'leader': my_id, 'type': 'hb', 'term': term}
          sock.send(json.dumps(heartbeat))
          #print(my_id + " has won the election. A heartbeat has been sent out")

          # Reset all values in preparation for a new election.
          state = 'leader'
          leader = my_id
          voted_this_term = False
          votes_for_me = 0

    clock = time.time()
    # If a follower receives no communication in their election timeout window, there is no visible leader and begins an election.
    if clock - last > elec_to:
      # Leaders send periodic heartbeats to all followers in order to maintain their authority.
      if state == 'leader':
        msg = {'src': my_id, 'dst': 'FFFF', 'leader': my_id, 'type': 'hb', 'term': term}
        sock.send(json.dumps(msg))
        #print '%s sending a HB to %s' % (msg['src'], msg['dst'])
      # If a follower receives no communication in their election timeout window, there is no visible leader and we begin an election.
      elif state == 'follower' and not voted_this_term:
        begin_election()
      # If there is a tie, so no one gains a majority of the votes, the candidate should timeout and start a new election.
      elif state == 'candidate':
        begin_election()
      last = clock
