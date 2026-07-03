# import os
# import traci

# protocol = "flooding"  # Change to "umbbfs" if needed

# # Check both possible file locations
# log_file_paths = [
#     f"F:/VANET_Project/sumo/vis_{protocol}.csv",
#     f"F:/VANET_Project/vis_{protocol}.csv"
# ]

# # Find the correct file location
# log_file_path = None
# for path in log_file_paths:
#     if os.path.exists(path):
#         log_file_path = path
#         break

# if log_file_path is None:
#     print(f"ERROR: File vis_{protocol}.csv not found.")
#     exit()

# def run():
#     """Runs SUMO visualization by highlighting affected vehicles."""
#     traci.start(["sumo-gui", "-c", "F:/VANET_Project/sumo/grid.sumocfg"])

#     while traci.simulation.getMinExpectedNumber() > 0:
#         traci.simulationStep()
#         for veh_id in traci.vehicle.getIDList():
#             if veh_id in affected_vehicles:
#                 traci.vehicle.setColor(veh_id, (255, 0, 0))  # Red color for affected vehicles
#     traci.close()

# affected_vehicles = set()

# # Read affected vehicles from log file
# with open(log_file_path, "r") as log_file:
#     next(log_file)  # Skip header
#     for line in log_file:
#         try:
#             time, veh_id, x, y = line.strip().split(",")  # Unpack all four values
#             affected_vehicles.add(veh_id)
#         except ValueError as e:
#             print(f"⚠ WARNING: Skipping malformed line -> {line.strip()} (Error: {e})")

# print(f"✔ Loaded {len(affected_vehicles)} affected vehicles from {log_file_path}.")
# run()


import os
import traci

# Define protocol
# protocol = "umbbfs-cluster"  # flooding, umbbfs, umbbfs-cluster, umbbfs-firefly

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--protocol", type=str, required=True)
args = parser.parse_args()

protocol = args.protocol


# Automatically find the correct CSV log path
log_file_paths = [
    f"F:/VANET_Project/sumo/vis_{protocol}.csv",
    f"F:/VANET_Project/vis_{protocol}.csv"
]

log_file_path = next((path for path in log_file_paths if os.path.exists(path)), None)

if not log_file_path:
    print(f"ERROR: vis_{protocol}.csv not found in known locations.")
    exit()

# Color mappings
role_to_color = {
    "receiver": (255, 255, 0),    # Yellow
    "forwarder": (255, 0, 0),     # Red
    "ch": (0, 255, 0),            # Green
    "sch": (0, 0, 255),           # Blue
}

# Load affected vehicle IDs and their roles
affected_vehicles = {}
with open(log_file_path, "r") as log_file:
    next(log_file)  # Skip header
    for line in log_file:
        try:
            time, veh_id, x, y, role = line.strip().split(",")
            affected_vehicles[veh_id] = role
        except ValueError as e:
            print(f"Skipping malformed line: {line.strip()} (Error: {e})")

print(f"Loaded {len(affected_vehicles)} affected vehicles from {log_file_path}")

def run():
    """Run SUMO and apply colors based on vehicle role."""
    traci.start(["sumo-gui", "-c", "F:/VANET_Project/sumo/grid.sumocfg"])

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        for veh_id in traci.vehicle.getIDList():
            norm_id = veh_id.split('.')[0]
            if norm_id in affected_vehicles:
                role = affected_vehicles[norm_id].lower()
                color = role_to_color.get(role, (0, 196, 196))  # default to yellow
                # print(f"🚗 Coloring {veh_id} (ID={norm_id}) as {role} → {color}")
                traci.vehicle.setColor(veh_id, color)  # Use full veh_id here


    traci.close()

run()
