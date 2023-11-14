# fast_network

The purpose of the fast_network project is to process the backup of the school server as quickly as possible by maximizing the bandwidth.

My assumption of this world:
- all the communication channels are directed
- each data centre has overall limits on the amount of incoming data it can receive per second, and also on the amount of outgoing data it can send per second.
- maxIn is a list of integers in which maxIn[i] specifies the maximum amount of incoming data that data centre i can process per second.
- The sum of the throughputs across all outgoing communication channels from data centre i should not exceed maxOut[i]
- origin is always not in the targets list
