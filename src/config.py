from dataclasses import dataclass

@dataclass
class SimulationConfig:
    # Duración de la simulación en ticks
    ticks: int = 600  
    
    arrival_rate_ns: float = 0.3  # Norte-Sur / Sur-Norte
    arrival_rate_ew: float = 0.2  # Este-Oeste / Oeste-Este

    control_mode: str = "fixed"

    green_min: int = 15
    green_max: int = 60
    yellow_time: int = 3
    max_distance: int = 30
    vehicle_speed: float = 1.0
    min_vehicle_gap: float = 4.0
    
    post_cross_distance: float = 25.0

    seed: int = 42

    seconds_per_tick: int = 10
    use_time_of_day: bool = False
