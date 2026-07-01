# """Contains data structures for the vehicle network."""

# __author__ = 'Adam Morrissett', 'Steven M. Hernandez'

# import csv
# import math
# from vanet_sim import road_net
# from vanet_sim.routing.routing_protocols import Message


# class Vehicle:
#     def __init__(self, node_id, route):
#         """Custom constructor for Vehicle.

#         :param node_id: ID number of vehicle
#         :param route: list of Roads on which the vehicle travels
#         """

#         self.id = node_id
#         self.route = route
#         self.route_index = 0
#         self._cur_road = None
#         self.spd = None
#         self.cur_pos = 0
#         self.at_intersection = False
#         self.is_cur_fwdr = False

#         self.x = 0
#         self.y = 0
#         self.prev_time = 0
#         self.neighbors = []
#         self.border_vehicles = []

#         self.congestion_detected = False

#         self.affected_at = None
#         self.received_at = None
#         self.passed_previous_intersection_at = None

#         self._received_before_affected = False
#         self._affected_not_received = False
#         self._received_early = False
#         self._original_forwarder = False

#         self.set_cur_road(self.route[self.route_index], 0)
#         self.update_location(0)

#         # Packet related information
#         self.dest_intersection = None
#         self.msg = None

#     def update_location(self, time):
#         """Updates position of vehicle with respect to current time.

#         :param time: current simulation time
#         :return: None
#         """

#         d_pos = (time - self.prev_time) * self.spd
#         fwd_n = self._get_forward_neighbor()

#         if self.affected_at is not None:
#             return
#         elif fwd_n is not None and d_pos > _calc_distance(self, fwd_n) - 16 and time > 5:
#             d_pos *= 0.5
#             if self.cur_road.is_obstructed or fwd_n.affected_at is not None:
#                 self.spd = 0
#                 self.affected_at = time
#         elif self.cur_road.is_obstructed and self.cur_pos + d_pos >= self.cur_road.obstruction_pos:
#             d_pos = 0
#             self.spd = 0.0
#             self.affected_at = time

#         if self.cur_pos + d_pos >= self.cur_road.length:
#             d_pos -= self.cur_road.length
#             self._next_road(time)

#         self.cur_pos += d_pos
#         self.at_intersection = self.cur_pos <= road_net.INTERSECTION_RADIUS * 3

#         # Absolute positioning
#         x_range = self.cur_road.end_node.x_pos - self.cur_road.start_node.x_pos
#         y_range = self.cur_road.end_node.y_pos - self.cur_road.start_node.y_pos

#         self.x = self.cur_road.start_node.x_pos + (x_range * self.cur_pos / self.cur_road.length)
#         self.y = self.cur_road.start_node.y_pos + (y_range * self.cur_pos / self.cur_road.length)

#         self.prev_time = time

#     def _next_road(self, time):
#         """Moves vehicle to next road in route."""
#         self.route_index = (self.route_index + 1) % len(self.route)
#         self.set_cur_road(self.route[self.route_index], time)
#         self.spd = self.cur_road.spd_lim

#     def _get_forward_neighbor(self):
#         """Gets the vehicle immediately in front of the current node."""
#         forward_neighbor = None

#         for n in self.neighbors:
#             is_ahead = (self.cur_road == n.cur_road and self.cur_pos < n.cur_pos) or \
#                        (self.cur_road != n.cur_road and self.cur_pos > n.cur_pos)
#             if is_ahead and _calc_distance(self, n) < 16:
#                 if forward_neighbor is None or _calc_distance(self, forward_neighbor) > _calc_distance(self, n):
#                     forward_neighbor = n

#         return forward_neighbor

#     def update_neighbors(self, vehicle_net, communication_radius):
#         """ Updates the list of neighbors that the vehicle sees. """
#         self.neighbors = []
#         for v in vehicle_net:
#             if v.id != self.id and _calc_distance(self, v) < communication_radius:
#                 self.neighbors.append(v)

#     def identify_border_vehicles(self, vehicle_net, communication_radius):
#         """Identifies vehicles at the communication border (UMBBFS logic)."""
#         self.border_vehicles = []
#         for v in vehicle_net:
#             if v.id != self.id:
#                 distance = _calc_distance(self, v)
#                 if communication_radius * 0.8 <= distance <= communication_radius:
#                     self.border_vehicles.append(v)

#     def update_routing(self, time, protocol="umbbfs"):
#         """Handles message forwarding based on protocol (Flooding or UMBBFS)."""
        
#         if self.affected_at == time and self.received_at is None:
#             self.is_cur_fwdr = True
#             self.msg = Message(src_rd=self.cur_road, dst_isect=self.cur_road.start_node)
#             self.received_at = time

#             if protocol == "umbbfs":
#                 # Forward only to border vehicles
#                 for border_vehicle in self.border_vehicles:
#                     if not border_vehicle.received_at:
#                         border_vehicle.received_at = time
#             else:
#                 # FLOODING: Forward to all neighbors
#                 for neighbor in self.neighbors:
#                     if not neighbor.received_at:
#                         neighbor.received_at = time

#     @property
#     def received_before_affected(self):
#         return self.affected_at is not None and self.received_at is not None and self.affected_at > self.received_at

#     @property
#     def received_early(self):
#         return self.received_at is not None and self.affected_at is None

#     @property
#     def affected_not_received(self):
#         return self.affected_at is not None and self.received_at is None

#     @property
#     def original_forwarder(self):
#         return self.received_at is not None and self.affected_at is not None and self.received_at == self.affected_at

#     @property
#     def cur_road(self):
#         return self._cur_road

#     def set_cur_road(self, r, t):
#         self.passed_previous_intersection_at = t
#         self._cur_road = r
#         self.spd = self._cur_road.spd_lim

#     def route_contains_rd(self, road):
#         """Checks if a road is in the vehicle’s route."""
#         return any(rd.name == road.name for rd in self.route)


# def build_vehicle_net(filepath, road_map):
#     """Builds a List of Vehicle object from file."""
#     vehicles = []

#     with open(filepath, mode='r', newline='') as fp:
#         reader = csv.reader(fp, delimiter=';')
#         for row in reader:
#             route = [road_map.road_dict[road] for road in row[1].split(',')]
#             vehicles.append(Vehicle(node_id=int(row[0]), route=route))

#     return vehicles


# def _calc_distance(v0, v1):
#     """Calculates Euclidean distance between two vehicles."""
#     return math.sqrt((v1.x - v0.x) ** 2 + (v1.y - v0.y) ** 2)


"""Contains data structures for the vehicle network with support for clustering."""

__author__ = 'Adam Morrissett', 'Steven M. Hernandez'

import csv
import math
from vanet_sim import road_net
from vanet_sim.routing.routing_protocols import Message


class Vehicle:
    def __init__(self, node_id, route):
        self.id = node_id
        self.route = route
        self.route_index = 0
        self._cur_road = None
        self.spd = None
        self.cur_pos = 0
        self.at_intersection = False
        self.is_cur_fwdr = False

        self.x = 0
        self.y = 0
        self.prev_time = 0
        self.neighbors = []
        self.border_vehicles = []

        self.affected_at = None
        self.received_at = None
        self.passed_previous_intersection_at = None

        # Super Cluster attributes
        self.cluster_id = -1
        self.is_ch = False  # Cluster Head
        self.is_sch = False  # Slave Cluster Head

        self.set_cur_road(self.route[self.route_index], 0)
        self.update_location(0)

        self.msg = None

    def update_location(self, time):
        d_pos = (time - self.prev_time) * self.spd
        fwd_n = self._get_forward_neighbor()

        if self.affected_at is not None:
            return
        elif fwd_n is not None and d_pos > _calc_distance(self, fwd_n) - 16 and time > 5:
            d_pos *= 0.5
            if self.cur_road.is_obstructed or fwd_n.affected_at is not None:
                self.spd = 0
                self.affected_at = time
        elif self.cur_road.is_obstructed and self.cur_pos + d_pos >= self.cur_road.obstruction_pos:
            d_pos = 0
            self.spd = 0.0
            self.affected_at = time

        if self.cur_pos + d_pos >= self.cur_road.length:
            d_pos -= self.cur_road.length
            self._next_road(time)

        self.cur_pos += d_pos
        self.at_intersection = self.cur_pos <= road_net.INTERSECTION_RADIUS * 3

        x_range = self.cur_road.end_node.x_pos - self.cur_road.start_node.x_pos
        y_range = self.cur_road.end_node.y_pos - self.cur_road.start_node.y_pos

        self.x = self.cur_road.start_node.x_pos + (x_range * self.cur_pos / self.cur_road.length)
        self.y = self.cur_road.start_node.y_pos + (y_range * self.cur_pos / self.cur_road.length)

        self.prev_time = time

    def _next_road(self, time):
        self.route_index = (self.route_index + 1) % len(self.route)
        self.set_cur_road(self.route[self.route_index], time)
        self.spd = self.cur_road.spd_lim

    def _get_forward_neighbor(self):
        forward_neighbor = None
        for n in self.neighbors:
            is_ahead = (self.cur_road == n.cur_road and self.cur_pos < n.cur_pos) or \
                       (self.cur_road != n.cur_road and self.cur_pos > n.cur_pos)
            if is_ahead and _calc_distance(self, n) < 16:
                if forward_neighbor is None or _calc_distance(self, forward_neighbor) > _calc_distance(self, n):
                    forward_neighbor = n
        return forward_neighbor

    def update_neighbors(self, vehicle_net, communication_radius):
        self.neighbors = []
        for v in vehicle_net:
            if v.id != self.id and _calc_distance(self, v) < communication_radius:
                self.neighbors.append(v)

    def identify_border_vehicles(self, vehicle_net, communication_radius):
        self.border_vehicles = []
        for v in vehicle_net:
            if v.id != self.id:
                distance = _calc_distance(self, v)
                if communication_radius * 0.8 <= distance <= communication_radius:
                    self.border_vehicles.append(v)

    def receive_message(self, time):
        """Mark the vehicle as having received the message at a given time."""
        if self.received_at is None:
            self.received_at = time

    def update_routing(self, time, protocol="umbbfs"):
        """Handles message forwarding based on protocol (Flooding, UMBBFS, UMBBFS-Cluster)."""

        if self.affected_at == time and self.received_at is None:
            self.is_cur_fwdr = True
            self.msg = Message(src_rd=self.cur_road, dst_isect=self.cur_road.start_node)
            self.received_at = time

            if protocol == "flooding":
                for neighbor in self.neighbors:
                    neighbor.receive_message(time)

            elif protocol == "umbbfs":
                for border_vehicle in self.border_vehicles:
                    border_vehicle.receive_message(time)

            elif protocol == "umbbfs-cluster":
                if self.is_ch or self.is_sch:
                    for neighbor in self.neighbors:
                        neighbor.receive_message(time)

            elif protocol == "umbbfs-cluster-firefly":
                # print(f"[DEBUG] Vehicle {self.id} - CH: {self.is_ch}, SCH: {self.is_sch}")
                if self.is_ch or self.is_sch:
                    from vanet_sim.routing.firefly_optimizer import firefly_optimization, discrete_firefly_optimization, binary_firefly_optimization, chaotic_firefly_optimization
                    candidate_neighbors = [n for n in self.neighbors if n.received_at is None]
                    best_forwarders = firefly_optimization(candidate_neighbors)

                    for fwdr in best_forwarders:
                        if fwdr.received_at is None and fwdr.affected_at != time:
                            fwdr.received_at = time
                            # print(f"Firefly Forwarded to: {fwdr.id} at time {time}")


    @property
    def received_before_affected(self):
        return self.affected_at is not None and self.received_at is not None and self.affected_at > self.received_at

    @property
    def received_early(self):
        return self.received_at is not None and self.affected_at is None

    @property
    def affected_not_received(self):
        return self.affected_at is not None and self.received_at is None

    @property
    def original_forwarder(self):
        return self.received_at is not None and self.affected_at is not None and self.received_at == self.affected_at

    @property
    def cur_road(self):
        return self._cur_road

    def set_cur_road(self, r, t):
        self.passed_previous_intersection_at = t
        self._cur_road = r
        self.spd = self._cur_road.spd_lim

    def route_contains_rd(self, road):
        return any(rd.name == road.name for rd in self.route)


def build_vehicle_net(filepath, road_map):
    vehicles = []
    with open(filepath, mode='r', newline='') as fp:
        reader = csv.reader(fp, delimiter=';')
        for row in reader:
            route = [road_map.road_dict[road] for road in row[1].split(',')]
            vehicles.append(Vehicle(node_id=int(row[0]), route=route))
    return vehicles


def _calc_distance(v0, v1):
    return math.sqrt((v1.x - v0.x) ** 2 + (v1.y - v0.y) ** 2)
