# """Top-level script to run the simulation with Flooding or UMBBFS."""

# import argparse
# from vanet_sim import simulation, vehicle_net, road_net

# # Parse command-line arguments
# parser = argparse.ArgumentParser(description="Run VANET Simulation with different protocols")
# parser.add_argument("--protocol", type=str, choices=["flooding", "umbbfs"], default="umbbfs",
#                     help="Choose the message dissemination protocol (flooding or umbbfs).")
# args = parser.parse_args()

# # Load road network
# road_map = road_net.RoadMap(intersection_file='intersections.generated.csv',
#                             road_file='roads.generated.csv')

# # Load vehicles
# vehicles = vehicle_net.build_vehicle_net(filepath='vehicles.200.generated.csv',
#                                          road_map=road_map)

# # Run Simulation with selected protocol
# sim = simulation.Simulation(d_time=0.5, road_map=road_map, vehicle_net=vehicles)
# sim.run(time_duration=100, protocol=args.protocol)


"""Top-level script to run the simulation with Flooding or UMBBFS (with/without clustering)."""

import argparse
from vanet_sim import simulation, vehicle_net, road_net

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Run VANET Simulation with different protocols")
parser.add_argument("--protocol", type=str, choices=["flooding", "umbbfs", "umbbfs-cluster", "umbbfs-cluster-firefly"], default="umbbfs")


args = parser.parse_args()

# Load road network
road_map = road_net.RoadMap(intersection_file='intersections.generated.csv',
                            road_file='roads.generated.csv')

# Load vehicles
vehicles = vehicle_net.build_vehicle_net(filepath='vehicles.400.generated.csv',
                                         road_map=road_map)

# Assign cluster IDs and heads
if args.protocol in ["umbbfs-cluster", "umbbfs-cluster-firefly"]:
    cluster_size = 10
    for i, v in enumerate(vehicles):
        v.cluster_id = i // cluster_size  # Group of 10 in a cluster

        # First vehicle in cluster becomes CH, second becomes SCH
        if i % cluster_size == 0:
            v.is_ch = True
        elif i % cluster_size == 1:
            v.is_sch = True


# Run Simulation
sim = simulation.Simulation(d_time=0.5, road_map=road_map, vehicle_net=vehicles)
sim.run(time_duration=200, protocol=args.protocol)
