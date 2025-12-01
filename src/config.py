from dataclasses import dataclass

@dataclass
class SimulationConfig:
    # Duración de la simulación en ticks
    # (para un día completo lo sobreescribiremos)
    ticks: int = 600  

    # Tasas de llegadas "base" (se usan cuando NO usamos hora del día)
    arrival_rate_ns: float = 0.3  # Norte-Sur / Sur-Norte
    arrival_rate_ew: float = 0.2  # Este-Oeste / Oeste-Este

    # Modo de control del semáforo: "fixed" o "adaptive"
    control_mode: str = "fixed"

    # Parámetros del semáforo
    green_min: int = 15
    green_max: int = 60
    yellow_time: int = 3

    # Longitud máxima del tramo antes de la intersección (en "celdas")
    max_distance: int = 30

    # Velocidad de los autos (celdas por tick)
    vehicle_speed: float = 1.0
    # Separación mínima entre autos en el mismo carril (en unidades de distancia del modelo)
    min_vehicle_gap: float = 4.0
    
    # Distancia que recorre el auto DESPUÉS de cruzar la intersección
    # antes de desaparecer (en unidades del modelo)
    post_cross_distance: float = 25.0

    # Semilla para reproducibilidad
    seed: int = 42

    # --- NUEVO: soporte para "día completo" ---
    # Cuántos segundos reales representa 1 tick de simulación
    # Ejemplo: 10 s por tick -> 24h = 8640 ticks
    seconds_per_tick: int = 10

    # Si True, las tasas de llegada se calculan según la hora del día (Lima)
    use_time_of_day: bool = False
