# """Contains code to run the simulations with UMBBFS & Flooding and log SUMO visualization."""

# import os
# import time
# import pandas as pd

# __author__ = 'Adam Morrissett', 'Steven M. Hernandez'

# from vanet_sim.evaluation import Evaluations
# from vanet_sim.routing.routing_protocols import UrbanRoutingHops, UrbanRoutingIntersection, Epidemic, GyTar

# LOG_TO_FILE = True
# URBAN_ROUTING_INT_STRING = "urban-int"
# URBAN_ROUTING_HOPS_STRING = "urban-hops"
# EPIDEMIC_ROUTING_STRING = "epidemic"
# GYTAR_ROUTING_STRING = "gytar"


# class Simulation:
#     """Performs a simulation with support for UMBBFS & Flooding."""

#     def __init__(self, d_time, road_map, vehicle_net):
#         """Custom constructor that initializes parameters.

#         :param d_time: simulation time resolution
#         :param road_map: filepath of the road network config file
#         :param vehicle_net: filepath of the vehicle network config file
#         """
#         self.cur_time = 0
#         self.d_time = d_time
#         self.road_net = road_map
#         self.vehicle_net = vehicle_net
#         self.simulation_data = []
#         self.sumo_log = []  # Stores SUMO visualization data

#         self.experiment_storage = f"../storage/experiments/{int(time.time())}/"
#         os.makedirs(self.experiment_storage, exist_ok=True)

#         self.settings = {
#             "communication_radius": 450,  # Increased range for better UMBBFS performance
#             "protocol": {
#                 "type": URBAN_ROUTING_HOPS_STRING,  # Default routing protocol
#                 "max_hops": 5,
#                 "max_ints": 1,
#                 "min_feed_ratio": 0.1,
#                 "forwarder_ttl": 5,
#             }
#         }

#         self.write_settings_to_file()

#     def log_sumo_visualization(self, protocol):
#         """Logs affected vehicle positions for SUMO visualization."""
#         with open(f"F:/VANET_Project/sumo/vis_{protocol}.csv", "w") as log_file:
#             log_file.write("Time,VehicleID,X,Y\n")  # Add proper header
#             for vehicle in self.vehicle_net:
#                 if vehicle.received_at is not None:  # Only log affected vehicles
#                     log_file.write(f"{self.cur_time},{vehicle.id},{vehicle.x},{vehicle.y}\n")

#     def step(self, protocol="umbbfs"):
#         """Progresses the simulation forward by one time step, using UMBBFS or Flooding."""
        
#         # Update vehicle locations
#         for v in self.vehicle_net:
#             v.update_location(self.cur_time)

#         # Update neighbors
#         for v in self.vehicle_net:
#             v.update_neighbors(self.vehicle_net, self.settings["communication_radius"])
#             if protocol == "umbbfs":
#                 v.identify_border_vehicles(self.vehicle_net, self.settings["communication_radius"])

#         # Update routing based on protocol
#         affected_vehicles = 0
#         messages_received = 0
#         affected_and_received = 0
#         total_reaction_time = 0
#         reacting_vehicles = 0

#         for v in self.vehicle_net:
#             v.update_routing(self.cur_time, protocol)
#             if v.received_at is not None:
#                 affected_vehicles += 1
#                 messages_received += 1
#             if v.affected_at is not None:
#                 if v.received_at is not None:
#                     affected_and_received += 1
#                     reaction_time = v.affected_at - v.received_at
#                     total_reaction_time += reaction_time
#                     reacting_vehicles += 1

#         # Calculate average reaction time
#         avg_reaction_time = total_reaction_time / reacting_vehicles if reacting_vehicles > 0 else 0

#         # Print simulation log in the required format
#         print("\n========")
#         print(f"Time: {self.cur_time:.1f}")
#         print(f"# affected: {affected_vehicles}")
#         print(f"# receiving message: {messages_received}")
#         # print(f"# affected and received: {affected_and_received}")
#         print(f"AVG time to react: {avg_reaction_time:.4f}")

#         # Save the results for analysis
#         self.simulation_data.append([
#             self.cur_time, affected_vehicles, messages_received, affected_and_received, avg_reaction_time
#         ])

#         self.cur_time += self.d_time


#     def run(self, time_duration=100, protocol="umbbfs"):
#         """Executes the simulation for the specified duration, using the chosen protocol."""
        
#         print(f'Starting simulation from t = {self.cur_time:.3f} with {protocol.upper()} protocol')

#         while self.cur_time < time_duration:
#             self.step(protocol)

#         # Save results for analysis
#         df = pd.DataFrame(self.simulation_data, columns=["Time", "Affected_Vehicles", "Messages_Received", "Affected_And_Received", "AVG_Reaction_Time"])

#         df.to_csv(f"simulation_results_{protocol}.csv", index=False)

#         # Save SUMO visualization log
#         df_sumo = pd.DataFrame(self.sumo_log, columns=["Time", "Affected_Vehicles"])
#         df_sumo.to_csv(f"vis_{protocol}.csv", index=False)

#     def write_settings_to_file(self):
#         """Writes simulation settings to a file."""
#         if LOG_TO_FILE:
#             with open(self.experiment_storage + "settings.txt", 'w') as f:
#                 f.write("\n".join(map(lambda x: '"{}": {}'.format(x, self.settings[x]), self.settings)))


"""Contains code to run the simulations with UMBBFS & Flooding and log SUMO visualization."""

import os
import time
import pandas as pd

__author__ = 'Adam Morrissett', 'Steven M. Hernandez'

from vanet_sim.evaluation import Evaluations
from vanet_sim.routing.routing_protocols import UrbanRoutingHops, UrbanRoutingIntersection, Epidemic, GyTar
from vanet_sim.clustering.super_cluster import perform_super_clustering  # ⬅️ NEW IMPORT

LOG_TO_FILE = True
URBAN_ROUTING_INT_STRING = "urban-int"
URBAN_ROUTING_HOPS_STRING = "urban-hops"
EPIDEMIC_ROUTING_STRING = "epidemic"
GYTAR_ROUTING_STRING = "gytar"


class Simulation:
    """Performs a simulation with support for UMBBFS, UMBBFS-Cluster & Flooding."""

    def __init__(self, d_time, road_map, vehicle_net):
        self.cur_time = 0
        self.d_time = d_time
        self.road_net = road_map
        self.vehicle_net = vehicle_net
        self.simulation_data = []
        self.sumo_log = []

        self.experiment_storage = f"../storage/experiments/{int(time.time())}/"
        os.makedirs(self.experiment_storage, exist_ok=True)

        self.settings = {
            "communication_radius": 450,
            "protocol": {
                "type": URBAN_ROUTING_HOPS_STRING,
                "max_hops": 5,
                "max_ints": 1,
                "min_feed_ratio": 0.1,
                "forwarder_ttl": 5,
            }
        }

        self.write_settings_to_file()

    # def log_sumo_visualization(self, protocol):
    #     with open(f"F:/VANET_Project/sumo/vis_{protocol}.csv", "w") as log_file:
    #         log_file.write("Time,VehicleID,X,Y\n")
    #         for vehicle in self.vehicle_net:
    #             if vehicle.received_at is not None:
    #                 log_file.write(f"{self.cur_time},{vehicle.id},{vehicle.x},{vehicle.y}\n")

    def log_sumo_visualization(self, protocol):
        """Logs affected vehicle positions and roles for SUMO visualization."""
        log_file_path = f"F:/VANET_Project/sumo/vis_{protocol}.csv"

        with open(log_file_path, "w") as log_file:
            log_file.write("time,veh_id,x,y,role\n")  # Updated header

            for vehicle in self.vehicle_net:
                if vehicle.received_at is not None:
                    # 🔍 Determine role
                    if vehicle.is_cur_fwdr:
                        role = "Forwarder"
                    elif vehicle.is_ch:
                        role = "CH"
                    elif vehicle.is_sch:
                        role = "SCH"
                    else:
                        role = "Receiver"

                    log_file.write(f"{self.cur_time},{vehicle.id},{vehicle.x:.2f},{vehicle.y:.2f},{role}\n")


    def step(self, protocol="umbbfs"):
        for v in self.vehicle_net:
            v.update_location(self.cur_time)

        for v in self.vehicle_net:
            v.update_neighbors(self.vehicle_net, self.settings["communication_radius"])
            if protocol.startswith("umbbfs"):
                v.identify_border_vehicles(self.vehicle_net, self.settings["communication_radius"])

        # ⬇️ Perform super clustering if required
        if protocol == "umbbfs-cluster":
            from vanet_sim.clustering.super_cluster import perform_super_clustering
            perform_super_clustering(self.vehicle_net)

        affected_vehicles = 0
        messages_received = 0
        affected_and_received = 0
        total_reaction_time = 0
        reacting_vehicles = 0

        for v in self.vehicle_net:
            v.update_routing(self.cur_time, protocol)
            if v.received_at is not None:
                affected_vehicles += 1
                messages_received += 1
            if v.affected_at is not None and v.received_at is not None:
                affected_and_received += 1
                total_reaction_time += (v.affected_at - v.received_at)
                reacting_vehicles += 1

        avg_reaction_time = total_reaction_time / reacting_vehicles if reacting_vehicles > 0 else 0

        print("\n========")
        print(f"Time: {self.cur_time:.1f}")
        print(f"# affected: {affected_vehicles}")
        print(f"# receiving message: {messages_received}")
        print(f"AVG time to react: {avg_reaction_time:.4f}")

        self.simulation_data.append([
            self.cur_time, affected_vehicles, messages_received, affected_and_received, avg_reaction_time
        ])

        self.cur_time += self.d_time

    # def run(self, time_duration=100, protocol="umbbfs"):
    #     print(f'Starting simulation from t = {self.cur_time:.3f} with {protocol.upper()} protocol')

    #     while self.cur_time < time_duration:
    #         self.step(protocol)

    #     df = pd.DataFrame(self.simulation_data, columns=["Time", "Affected_Vehicles", "Messages_Received", "Affected_And_Received", "AVG_Reaction_Time"])
    #     df.to_csv(f"simulation_results_{protocol}.csv", index=False)

    #     df_sumo = pd.DataFrame(self.sumo_log, columns=["Time", "Affected_Vehicles"])
    #     df_sumo.to_csv(f"vis_{protocol}.csv", index=False)

    def run(self, time_duration=100, protocol="umbbfs"):
        print(f'Starting simulation from t = {self.cur_time:.3f} with {protocol.upper()} protocol')

        while self.cur_time < time_duration:
            self.step(protocol)

        # Save simulation results
        df = pd.DataFrame(
            self.simulation_data,
            columns=["Time", "Affected_Vehicles", "Messages_Received", "Affected_And_Received", "AVG_Reaction_Time"]
        )
        df.to_csv(f"simulation_results_{protocol}.csv", index=False)

        # Save SUMO visualization log with roles
        self.log_sumo_visualization(protocol)


    def write_settings_to_file(self):
        if LOG_TO_FILE:
            with open(self.experiment_storage + "settings.txt", 'w') as f:
                f.write("\n".join(map(lambda x: '"{}": {}'.format(x, self.settings[x]), self.settings)))
