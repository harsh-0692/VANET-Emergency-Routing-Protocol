# vanet_sim/routing/firefly_optimizer.py
import math
import random

class Firefly:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.intensity = self.calculate_intensity()

    def calculate_intensity(self):
        degree = len(self.vehicle.neighbors)
        distance_score = 1 / (1 + self.vehicle.cur_pos) if self.vehicle.cur_pos > 0 else 1
        return 0.6 * degree + 0.4 * distance_score

def firefly_distance(f1, f2):
    x1, y1 = f1.vehicle.x, f1.vehicle.y
    x2, y2 = f2.vehicle.x, f2.vehicle.y
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def attractiveness(beta0, gamma, r):
    return beta0 * math.exp(-gamma * (r ** 2))

def firefly_optimization(candidates, max_iter=5):
    fireflies = [Firefly(v) for v in candidates]

    for _ in range(max_iter):
        for i in range(len(fireflies)):
            for j in range(len(fireflies)):
                if fireflies[j].intensity > fireflies[i].intensity:
                    r = firefly_distance(fireflies[i], fireflies[j])
                    beta = attractiveness(beta0=1.0, gamma=0.5, r=r)
                    fireflies[i].intensity += beta

    fireflies.sort(key=lambda f: f.intensity, reverse=True)
    return [f.vehicle for f in fireflies[:3]]


def discrete_firefly_optimization(candidates, max_iter=5):
    fireflies = [Firefly(v) for v in candidates]

    for _ in range(max_iter):
        for i in range(len(fireflies)):
            for j in range(len(fireflies)):
                if fireflies[j].intensity > fireflies[i].intensity:
                    # Apply discrete 'movement': Swap neighbors or tweak intensity
                    if random.random() < 0.5:
                        # Discrete tweak: simulate a 'jump' in neighbor degree
                        fireflies[i].vehicle.neighbors = fireflies[j].vehicle.neighbors[:]
                    else:
                        # Simulate positional preference update
                        fireflies[i].vehicle.cur_pos = fireflies[j].vehicle.cur_pos

                    # Recalculate intensity after discrete move
                    fireflies[i].intensity = fireflies[i].calculate_intensity()

    # Sort and return top vehicles
    fireflies.sort(key=lambda f: f.intensity, reverse=True)
    return [f.vehicle for f in fireflies[:3]]


def binary_sigmoid(x):
    return 1 / (1 + math.exp(-x))

class BinaryFirefly:
    def __init__(self, binary_vector, candidates):
        self.binary_vector = binary_vector  # list of 0/1
        self.candidates = candidates
        self.intensity = self.calculate_intensity()

    def calculate_intensity(self):
        score = 0
        for bit, vehicle in zip(self.binary_vector, self.candidates):
            if bit == 1:
                degree = len(vehicle.neighbors)
                dist_score = 1 / (1 + vehicle.cur_pos) if vehicle.cur_pos > 0 else 1
                score += 0.6 * degree + 0.4 * dist_score
        return score


def binary_firefly_optimization(candidates, population_size=10, max_iter=5):
    num_bits = len(candidates)
    fireflies = []

    # Initialize random binary population
    for _ in range(population_size):
        bin_vec = [random.randint(0, 1) for _ in range(num_bits)]
        fireflies.append(BinaryFirefly(bin_vec, candidates))

    for _ in range(max_iter):
        for i in range(len(fireflies)):
            for j in range(len(fireflies)):
                if fireflies[j].intensity > fireflies[i].intensity:
                    # Move i toward j (binary update)
                    new_vec = fireflies[i].binary_vector[:]
                    for k in range(num_bits):
                        if fireflies[j].binary_vector[k] != fireflies[i].binary_vector[k]:
                            r = abs(k - j)
                            beta = attractiveness(1.0, 0.5, r)
                            prob = binary_sigmoid(beta)
                            if random.random() < prob:
                                new_vec[k] = fireflies[j].binary_vector[k]
                    fireflies[i] = BinaryFirefly(new_vec, candidates)

    # Select firefly with max intensity
    best = max(fireflies, key=lambda f: f.intensity)
    selected_vehicles = [v for b, v in zip(best.binary_vector, candidates) if b == 1]
    return selected_vehicles[:3]  # top 3


# === Chaotic Firefly Algorithm (CFA) ===

def logistic_map(x, mu=4.0):
    return mu * x * (1 - x)

def chaotic_firefly_optimization(candidates, max_iter=5, chaos_seed=0.7):
    fireflies = [Firefly(v) for v in candidates]
    num_fireflies = len(fireflies)
    chaos_val = chaos_seed

    for t in range(max_iter):
        chaos_val = logistic_map(chaos_val)  # generate chaotic number
        for i in range(num_fireflies):
            for j in range(num_fireflies):
                if fireflies[j].intensity > fireflies[i].intensity:
                    r = firefly_distance(fireflies[i], fireflies[j])
                    chaotic_beta = attractiveness(beta0=1.0, gamma=chaos_val, r=r)
                    fireflies[i].intensity += chaotic_beta * chaos_val  # weighted by chaos

    fireflies.sort(key=lambda f: f.intensity, reverse=True)
    return [f.vehicle for f in fireflies[:3]]