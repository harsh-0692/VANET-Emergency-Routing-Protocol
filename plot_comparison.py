import pandas as pd
import matplotlib.pyplot as plt
import os

# Define file paths
base_path = "F:/VANET_Project"
protocol_files = {
    "Flooding": f"{base_path}/simulation_results_flooding.csv",
    "UMBBFS": f"{base_path}/simulation_results_umbbfs.csv",
    "UMBBFS-Cluster": f"{base_path}/simulation_results_umbbfs-cluster.csv",
    "UMBBFS-Cluster-Firefly": f"{base_path}/simulation_results_umbbfs-cluster-firefly.csv"
}

# Load all dataframes
dataframes = {}
for label, file_path in protocol_files.items():
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        dataframes[label] = df
    else:
        print(f"Missing file for {label}: {file_path}")

# Plotting with better layout
fig, axes = plt.subplots(1, 3, figsize=(24, 6), constrained_layout=True)

# Plot 1: Affected Vehicles
for label, df in dataframes.items():
    axes[0].plot(df["Time"], df["Affected_Vehicles"], label=label)
axes[0].set_title("Affected Vehicles Over Time")
axes[0].set_xlabel("Time (s)")
axes[0].set_ylabel("Affected Vehicles")
axes[0].legend()
axes[0].grid(True)

# Plot 2: Average Reaction Time
for label, df in dataframes.items():
    axes[1].plot(df["Time"], df["AVG_Reaction_Time"], label=label)
axes[1].set_title("Average Reaction Time Over Time")
axes[1].set_xlabel("Time (s)")
axes[1].set_ylabel("Avg Reaction Time (s)")
axes[1].legend()
axes[1].grid(True)

# Plot 3: Packet Delivery Ratio (PDR)
TOTAL_VEHICLES = 400
for label, df in dataframes.items():
    pdr = df["Messages_Received"] / TOTAL_VEHICLES
    axes[2].plot(df["Time"], pdr, label=label)
axes[2].set_title("Packet Delivery Ratio (PDR) Over Time")
axes[2].set_xlabel("Time (s)")
axes[2].set_ylabel("PDR")
axes[2].legend()
axes[2].grid(True)

plt.show()
