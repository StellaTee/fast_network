from collections import deque
"""
This file consisits of one main method - maxThroughput 

maxThroughput returns the maximum possible data throughput from the data centre origin to the data 
centres specified as targets. 

Last modified: = "17/6/2023"

"""

class Vertex:
    """ 
    This is the Vertex class. It is used to represent a vertex in the graph. 
    """
    def __init__(self, id):
        """
        This is the constructor for the Vertex class. It takes in an integer to represent the id of the vertex.

        :Input:
            id: An integer to represent the id of the vertex.

        :Return:
            None

        :Time complexity: 
            O(1)

        :Aux space complexity:
            O(1)
        """
        self.id = id
        self.edges = []
        self.discovered = False
        self.visited = False

        # purpose: backtracking / where I was from
        self.parent = None
        self.incoming = 0
        self.incoming_vertex = []
    
    def add_edge(self, edge):
        """
        This method is used to add an edge to the vertex. It takes in an edge object.

        :Input:
            edge: An edge object to be added to connect the vertex.

        :Return:
            None

        :Time complexity: 
            O(1)

        :Aux space complexity:
            O(1)
        """
        self.edges.append(edge)

    def __str__ (self):
        """ 
        This method is used to print the vertex.

        :Return:
            A string representation of the vertex.

        :Time complexity: 
            O(E),where E is the number of edges in graph

        :Aux space complexity:
            O(1)
        """
        return_string = str(self.id)
        for edge in self.edges:
            return_string = return_string + "\n with edges " + str(edge) + ", incoming: " + str(self.incoming)
        if len(self.edges) == 0:
            return_string = return_string + "\n"+ "incoming: " + str(self.incoming)
        return return_string

    def added_to_queue(self):
        """ 
        This method is used to acknowldge that the vertex has been added to the queue

        :Return:
            None

        :Time complexity: 
            O(1)

        :Aux space complexity:
            O(1)
        """
        self.discovered = True

    def visited_node(self):
        """ 
        This method is used to acknowldge that the vertex has been visited 

        :Return:
            None

        :Time complexity: 
            O(1)

        :Aux space complexity:
            O(1)
        """
        self.visited = True

class Edge:
    """ 
    This is the Edge class. It is used to represent a edge between the vertices in the graph.     
    """
    def __init__(self, u, v, capacity, forward = True):
        """
        This is the constructor for the Edge class. The edge ensure that the flow we have won't exceed the limit of the capacity of the edge.

        :Input:
            u: A vertex object to represent the starting vertex of the edge.
            v: A vertex object to represent the ending vertex of the edge.
            capacity: An integer to represent the capacity of the edge
            forward: A boolean to represent if the edge is forward or backward. If forward then True, else False

        :Return:
            None

        :Time complexity: 
            O(1)

        :Aux space complexity:
            O(1)
        """
        self.u = u
        self.v = v
        self.capacity = capacity

        self.flow = 0
        self.forward = forward

        # store the reverse edge of the current edge
        self.reverse = None


    def add_flow(self, amount):
        """
        Augment the flow of the residual network. 

        :Input:
            amount: The amount of flow to be added to the edge.

        :Return:
            None

        :Time complexity: 
            O(1)

        :Aux space complexity:
            O(1)
        """
        self.flow += amount
        self.reverse.flow -= amount

    def __str__(self):
        """ 
        This method is used to print the edge.

        :Return:
            A string representation of the edge.

        :Time complexity: 
            O(1)

        :Aux space complexity:
            O(1)
        """
        if self.forward:
            return_string = str(self.u.id) + ", " + str(self.v.id) + ", flow: " + str(self.flow) + ", capacity: " + str(self.capacity)+ ", reverse_edge: ( " + str(self.reverse) + " )"

        else:
            return_string = str(self.u.id) + ", " + str(self.v.id) + ", flow: " + str(self.flow) + ", capacity: " + str(self.capacity)

        return return_string 
    
class ResidualNetwork:
    """ 
    This class is used to create a residual network flow and use the ford fulkerson method to find the maximum flow of
    the network flow. I created residual network without network flow as in the specification of this question all the 
    flow initialised with 0, therefore I can create a residual network directly. This residual network has 2 edges for each pair of vertex, 
    one is its flow edge, another is its reverse edge to get back to the outgoing vertex. 

    The residual network must have a super target node in this implementation. As we know there might be more than 1 targets in a flow, 
    therefore we use super target node to connect them together. Besides that, to ensure the flow won't exceed the MaxIn or 
    MaxOut constraints of the vertex, I create an extra vertex for each existing vertex. Based on the flow conservation property, we know that 
    incoming flow = outgoing flow, therefore by selecting the minimum of MaxIn and MaxOut of that vertex will ensure this property.

    The residual network is represented by an adjacency list. The adjacency list is represented by an array of vertices. 
    Each vertex has an array of edges.
    """
    
    def __init__(self, connections, maxIn, maxOut, origin, targets):
        """
        This is the constructor for the ResidualNetwork class. It takes in a list of connections, 
        a list of maxIn, a list of maxOut, an integer origin and a list of targets. It will initialise the residual network.

        :Input:
            connections: A list of integers representing the vertices that are passengers
            maxIn: a list of integers in which maxIn[i] specifies the maximum amount of incoming data that 
                data centre i can process per second
            maxOut: a list of integers in which maxOut[i] specifies the maximum amount of outgoing data that 
                data centre i can process per second.
            origin: the integer ID origin of the data centre where the data to be backed up is located
            targets: a of data centres that are deemed appropriate locations for the backup data to be stored.
        
        :Return:
            None

        :Time complexity: 
            O(E),where E is the number of edges in graph

        :Aux space complexity:
            O(V), where V is the number of element in graph
        """
        self.targets = targets
        self.path = []
        vertex_count = len(maxIn)

        # keep one for super target 
        self.residual_network_vertices = [None] * (vertex_count+1) * 2
        for i in range (len(self.residual_network_vertices)):
            self.residual_network_vertices[i] = Vertex(i)

        # connect the vertex with the newly created extra vertex
        for i in range (len(connections)):
            new_vertex = connections[i][0] + (len(maxIn)+1)

            connections[i] = (new_vertex,connections[i][1],connections[i][2], True)

        self.generate_network_flow(connections)

        # take care of maxIn maxOut 
        edges_to_be_added = []
        self.max_min_flow = []

        # compare maxIn and maxOut pick the minimum 
        for i in range (len(maxIn)):
            if i == origin:
                flow = maxOut[i]
                self.max_min_flow.append(flow)
            elif i in targets:
                flow = maxIn[i]
                self.max_min_flow.append(flow)

            else:
                flow = min(maxIn[i],maxOut[i])
                self.max_min_flow.append(flow)

        # take care of maxIn maxOut to link to the extra vertex of the original vertex, ensuring their flow by setting the capacity 
        # of the edge 
        for i in range (len(maxIn)):
            edges_to_be_added.append((i, i + (len(maxIn)+1) ,self.max_min_flow[i], True))

        self.generate_network_flow(edges_to_be_added)

        # always make a super node as destination 
        self.super_target_node(maxIn)
    
    def super_target_node(self, maxIn):
        """
        Connects all the target to the super target node.

        :Input:
            maxIn: a list of integers in which maxIn[i] specifies the maximum amount of incoming data that 
            data centre i can process per second
        
        :Return:
            None

        :Time complexity: 
            O(T),where T is the number of target

        :Aux space complexity:
            O(1)
        """
        edge_to_add = []
        # add the edge to connect to the super target 
        for target_id in self.targets:
            target = self.residual_network_vertices[target_id + (len(maxIn)+1)]
            super_target = self.residual_network_vertices[len(maxIn) + (len(maxIn)+1)]

            # take the incoming from the original vertex
            capacity = self.residual_network_vertices[target_id].incoming

            edge_to_add.append((target.id,super_target.id,capacity, True))

        self.generate_network_flow(edge_to_add)
                

    def __str__ (self):
        """
        This method is used to print the graph.

        :Return:
            return_string: A string that represents the graph.

        :Time complexity: 
            O(V),where V is the number of vertices in graph

        :Aux space complexity:
            O(1)
        """
        return_string = ""
        for vertex in self.residual_network_vertices:
            return_string = return_string + "Vertex " + str(vertex) + "\n"
        return return_string
    
    def generate_network_flow(self, connections):
        """
        This method is used to generate the residual network. 

        :Input:
            connections: 
                A list of tuples. Each tuple contains 4 elements. The first element is the starting vertex, 
                the second element is the ending vertex, the third element is the capacity of the edge and 
                the last element is a boolean to represent if the edge is forward or backward.

        :Return:
            None

        :Time complexity: 
            O(E),where E is the number of edges in graph

        :Aux space complexity:
            O(1)
        """
        self.add_edges(connections)
    
    def add_edges (self, argv_edges):
        """
        This method is used to add edges to the residual network. Each edge will have a reverse edge of the current edge. The current 
        edge will store the reference of reference edge, so we don't have to loop through the edges to find the reverse edge of the 
        current edge.  

        :Input:
            argv_edges: 
                A list of tuples. Each tuple contains 4 elements. The first element is the starting vertex, 
                the second element is the ending vertex, the third element is the capacity of the edge and 
                the last element is a boolean to represent if the edge is forward or backward.
        :Return:
            None

        :Time complexity: 
            O(E),where E is the number of edges in graph

        :Aux space complexity:
            O(1)
        """
        for edge in argv_edges:
            u = edge[0]
            v = edge[1]
            capacity = edge[2]
            forward = edge[3]
            
            current_edge = Edge(self.residual_network_vertices[u],self.residual_network_vertices[v],capacity, forward)
            reverse_edge = Edge(self.residual_network_vertices[v],self.residual_network_vertices[u],capacity, False)

            # to ensure that we can augment the reverse edge easily instead of looping through it 
            current_edge.reverse = reverse_edge
            reverse_edge.reverse = current_edge
            reverse_edge.flow = capacity

            #forward edge
            current_vertex = self.residual_network_vertices[u]
            self.residual_network_vertices[v].incoming += capacity
            self.residual_network_vertices[v].incoming_vertex.append(self.residual_network_vertices[u])
            current_vertex.add_edge(current_edge)

            #backward edge
            current_vertex = self.residual_network_vertices[v]
            self.residual_network_vertices[u].incoming_vertex.append(self.residual_network_vertices[v])
            current_vertex.add_edge(reverse_edge)

    def reset(self):
        """
        This method is used to reset some of the attributes (discovered and visited) of all vertices in the residual network.
        So it works like a new residual network with updated flow. 
        
        :Return:
            None

        :Time complexity: 
            O(V),where V is the number of vertices in graph

        :Aux space complexity:
            O(1)
        """
        self.path = []
        for vertex in self.residual_network_vertices:
            vertex.discovered = False
            vertex.visited = False

    def has_AugmentingPath(self, origin):
        """
        This method is used to check if there's a path to augment. I check this by using breadth first search 
        to obtain the shortest path. 

        :Input:
            origin: the integer ID origin of the data centre where the data to be backed up is located
        
        :Return:
            True, if there is a path to augment. Otherwise, False.

        :Time complexity: 
            O(V + E),where V is the number of vertex and E is the number of edges in graph

        :Aux space complexity:
            O(1)
        """
        # reset all the vertices
        self.reset() 

        source = self.residual_network_vertices[origin] 

        discovered = deque()
        discovered.append(source)

        while len(discovered) > 0 :
            # serve from queue 
            u = discovered.popleft() 
            u.visited_node()

            # # visit the edges of vertex
            for edge in u.edges:
                v = edge.v.id 
                v = self.residual_network_vertices[v]

                # if the path is available to augment 
                if v.discovered == False and v.visited == False and edge.capacity > edge.flow:
                    discovered.append(v)
                    v.parent = u

                    v.added_to_queue() 

                    #reach the target
                    if v.id == self.residual_network_vertices[-1].id:
                        return True

        return False
    
 
    def get_AugmentingPath(self, origin):
        """
        This method is get the path I am going to augment the flow.

        :Input:
            origin: the integer ID origin of the data centre where the data to be backed up is located
        
        :Return:
            The path which will be augment. 

        :Time complexity: 
            O(V+E),where V is the number of vertex and E is the number of edges in graph

        :Aux space complexity:
            O(E), where E is the number of edges in graph
        """
        max_flow_to_be_added_lst = []
        self.path = []

        # backtrack to obtain the path
        vertex = self.residual_network_vertices[-1] # the target
        while vertex != self.residual_network_vertices[origin]:
            parent = vertex.parent
            for edge in parent.edges:
                # to ensure the edge is connected 
                if edge.v.id == vertex.id:
                        max_flow_to_be_added_lst.append(edge.capacity - edge.flow)
                        self.path.append(edge)
                        break

            vertex = parent

        # reverse the path as we find the path by backtracking 
        for i in range(len(self.path) // 2):
            self.path[i], self.path[-i - 1] = self.path[-i - 1], self.path[i]

        # Find the max flow can be added to the path we found
        if len(self.path)>0:       
            self.max_flow_to_be_added_in_the_path = min(max_flow_to_be_added_lst)
        else:
            self.max_flow_to_be_added_in_the_path = 0

        return self.path

    
    def augmentFlow(self, path):
        """
        This method is augment the path we found. 

        :Input:
            path: a list of edge object which is the path we can augment 
        
        :Return:
            None 

        :Time complexity: 
            O(E),where E is the number of edges in graph

        :Aux space complexity:
            O(1)
        """
        for edge in path:
            edge.add_flow(self.max_flow_to_be_added_in_the_path)

    

def maxThroughput(connections, maxIn, maxOut, origin, targets):
    """
    Function description:
        This function returns the maximum possible data throughput from the 
        data centre origin to the data centres specified in targets.

    Approach description:
        This is inspired by the https://cs.stackexchange.com/questions/55041/residual-graph-in-maximum-flow
        and https://en.wikipedia.org/wiki/Edmonds–Karp_algorithm 

        I will use Ford–Fulkerson method with Edmonds-Karp algorithm. This allows me to select shortest augmenting path
        by using breadth-first-search. We will find augmenting paths with the fewest number of edges. This can also ensure that
        the time complexity of my function will not exceed O(VE^2). 
        
        Besides that, I will have multiple of 2 of the vertices given. Each vertex will have another extra vertexto ensure that 
        their incoming and outgoing flow is within the bound. The id of the extra vertex will always be original_vertex_id + (len(maxIn)+1).
        For example, if the original vertex id is 0, then the extra vertex id will be 0 + (len(maxIn)+1), in this case is 6. 
        This is to ensure that the flow conservation property is satisfied. 

        For the connections given, we have to update the incoming vertex.id as we did an extra vertex above, we need to link them back.
        For instance, connection (0,1,3000) given, I will update this connnection to (6,1,3000) to make sure all the vertices
        are connected. 

        After setting up the graph, we will run ford-fulkerson method to obtain the maximum possible data throughput from the 
        data centre origin to the data centres specified in targets.

    :Input:
        connections: A list of integers representing the vertices that are passengers
        maxIn: a list of integers in which maxIn[i] specifies the maximum amount of incoming data that data centre i can process per second
        maxOut: a list of integers in which maxOut[i] specifies the maximum amount of outgoing data that data centre i can process per second.
        origin: the integer ID origin of the data centre where the data to be backed up is located
        targets: a of data centres that are deemed appropriate locations for the backup data to be stored.

    :Return:
        An interger of the maximum possible data throughput from the 
            data centre origin to the data centres specified in targets.

    :Time complexity: 
        Best = Worst: O(VE^2), where V is the number of vertex and E is the number of edges

    :Aux space complexity: 
        O(V), where V is the number of element in graph
    """
    # # initialise the residual network
    residual_network = ResidualNetwork(connections, maxIn, maxOut, origin, targets)
    return ford_fulkerson(residual_network, origin)

def ford_fulkerson(residual_network, origin):
    """
    Function description:
        This function returns the maximum flow that can be augmented on the residual network

    Approach description:
        This is inspired by the https://cs.stackexchange.com/questions/55041/residual-graph-in-maximum-flow
        and https://en.wikipedia.org/wiki/Edmonds–Karp_algorithm 

        I will use Ford–Fulkerson method with Edmonds-Karp algorithm. This allows me to select shortest augmenting path
        by using breadth-first-search. We will find augmenting paths with the fewest number of edges. This can also ensure that
        the time complexity of my function will not exceed O(VE^2). 

    :Input:
        residual_network: A residualNetwork object 
        origin: the integer ID origin of the data centre where the data to be backed up is located

    :Return:
        flow: An interger of the maximum possible data throughput from the 
            data centre origin to the data centres specified in targets.

    :Time complexity: 
        Best = Worst: O(VE^2), where V is the number of vertex and E is the number of edges. Based on the lecture slides given, 
        we know that the time complexity of Edmonds-Karp algorithm is always O(VE^2).

    :Aux space complexity: 
        O(1)
    """
    flow = 0
    
    # find an augmenting path
    while residual_network.has_AugmentingPath(origin):

        # obtain the path
        path = residual_network.get_AugmentingPath(origin) 

        #augment the flow equal to the residual capacity
        flow += residual_network.max_flow_to_be_added_in_the_path

        # update the residual network
        residual_network.augmentFlow(path) 

    return flow 

if __name__ == "__main__":
    connections = [(0, 1, 3000), (1, 2, 2000), (1, 3, 1000),(0, 3, 2000), (3, 4, 2000), (3, 2, 1000)]
    maxIn = [5000, 3000, 3000, 3000, 2000]
    maxOut = [5000, 3000, 3000, 2500, 1500]
    origin = 0
    targets = [4, 2]
    max_flow = maxThroughput(connections, maxIn, maxOut, origin, targets)
    print("The maximum throughput of this network:", max_flow)
 