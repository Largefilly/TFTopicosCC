import random
from typing import List, Dict

from .config import SimulationConfig
from .agents import VehicleAgent, TrafficLightAgent, Direction


class TrafficModel:
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.rng = random.Random(config.seed)

        self.time = 0  # tick actual

        # Agente semáforo
        self.traffic_light = TrafficLightAgent(config, self.rng)

        # Lista de vehículos en el sistema
        self.vehicles: List[VehicleAgent] = []

        # Métricas
        self.exited_vehicles: List[VehicleAgent] = []
    #------------------------------------------------
    def get_leading_vehicle_distance(self, vehicle):
        
        if vehicle.distance < 0.0:
            return None

        candidates = [
            v for v in self.vehicles
            if v is not vehicle
            and v.exit_time is None
            and v.direction == vehicle.direction
            and v.distance >= 0.0              
            and v.distance < vehicle.distance  
        ]
        if not candidates:
            return None

        leading = max(candidates, key=lambda v: v.distance)
        return leading.distance
    
    def step(self):
        self._spawn_vehicles()
        self.traffic_light.step(self)
        for vehicle in sorted(list(self.vehicles), key=lambda v: v.distance):
            vehicle.step(self)
        self.time += 1

    # LÓGICA DE LLEGADAS 
    def _spawn_vehicles(self):
        arrival_rate_ns, arrival_rate_ew = self._get_arrival_rates_for_current_time()

        if self.rng.random() < arrival_rate_ns:
            direction = self.rng.choice([Direction.NORTH_SOUTH, Direction.SOUTH_NORTH])
            self._add_vehicle(direction)

        if self.rng.random() < arrival_rate_ew:
            direction = self.rng.choice([Direction.EAST_WEST, Direction.WEST_EAST])
            self._add_vehicle(direction)

    def _add_vehicle(self, direction: Direction):
        v = VehicleAgent(
            direction=direction,
            start_time=self.time,
            start_distance=float(self.config.max_distance),
        )
        self.vehicles.append(v)

    #NUEVO: HORA DEL DÍA Y TASAS DINÁMICAS

    def _get_arrival_rates_for_current_time(self):
        if not self.config.use_time_of_day:
            return self.config.arrival_rate_ns, self.config.arrival_rate_ew

        hour, minute = self.get_simulated_clock()


        ticks_per_hour = max(1, int(3600 / self.config.seconds_per_tick))

    def _get_arrival_rates_for_current_time(self):

        if not self.config.use_time_of_day:
            return self.config.arrival_rate_ns, self.config.arrival_rate_ew

        hour, minute = self.get_simulated_clock()

        ticks_per_hour = max(1, int(3600 / self.config.seconds_per_tick))

        def p_from_rate_per_hour(rate_per_hour: float) -> float:
            return min(rate_per_hour / ticks_per_hour, 1.0)

        if 0 <= hour < 5:
            
            rate_ns_h = 5.0
            rate_ew_h = 5.0

        elif 5 <= hour < 7:
            
            rate_ns_h = 15.0
            rate_ew_h = 15.0

        elif 7 <= hour < 9:
            
            rate_ns_h = 40.0
            rate_ew_h = 40.0

        elif 9 <= hour < 13:
            
            rate_ns_h = 25.0
            rate_ew_h = 25.0

        elif 13 <= hour < 16:
            
            rate_ns_h = 35.0
            rate_ew_h = 15.0

        elif 16 <= hour < 19:
            
            rate_ns_h = 30.0
            rate_ew_h = 30.0

        elif 19 <= hour < 21:
            
            rate_ns_h = 20.0
            rate_ew_h = 20.0

        elif 21 <= hour < 23:
            
            rate_ns_h = 8.0
            rate_ew_h = 8.0

        else:
            
            rate_ns_h = 4.0
            rate_ew_h = 4.0

        arrival_ns = p_from_rate_per_hour(rate_ns_h)
        arrival_ew = p_from_rate_per_hour(rate_ew_h)

        return arrival_ns, arrival_ew

    def get_simulated_clock(self):
        total_seconds = self.time * self.config.seconds_per_tick
        hour = (total_seconds // 3600) % 24
        minute = (total_seconds % 3600) // 60
        return int(hour), int(minute)
    
    def get_time_of_day_segment_label(self) -> str:
        if not self.config.use_time_of_day:
            return "Escenario: Tasas fijas"

        hour, _ = self.get_simulated_clock()

        if 0 <= hour < 6:
            return "Escenario: Flujo bajo (madrugada, balanceado)"
        elif 7 <= hour < 10:
            return "Escenario: Hora punta (mañana)"
        elif 13 <= hour < 16:
            return "Escenario: Flujo desbalanceado (NS > EW, mediodía)"
        elif 18 <= hour < 21:
            return "Escenario: Hora punta (tarde-noche)"
        else:
            # resto de horas: algo moderado/balanceado
            return "Escenario: Flujo moderado/balanceado"

    # ---------- MÉTRICAS Y UTILIDADES ----------
    def mark_vehicle_exited(self, vehicle: VehicleAgent):
        if vehicle in self.vehicles:
            self.vehicles.remove(vehicle)
        self.exited_vehicles.append(vehicle)

    def get_queue_size_ns(self) -> int:
        return sum(
            1
            for v in self.vehicles
            if v.direction in (Direction.NORTH_SOUTH, Direction.SOUTH_NORTH)
            and 0.0 < v.distance <= 5.0   # solo antes del cruce
        )

    def get_queue_size_ew(self) -> int:
        return sum(
            1
            for v in self.vehicles
            if v.direction in (Direction.EAST_WEST, Direction.WEST_EAST)
            and 0.0 < v.distance <= 5.0   # solo antes del cruce
        )

    def get_summary(self) -> Dict[str, float]:
        n_exited = len(self.exited_vehicles)
        if n_exited > 0:
            travel_times = [
                v.exit_time - v.start_time
                for v in self.exited_vehicles
                if v.exit_time is not None
            ]
            avg_travel_time = sum(travel_times) / len(travel_times)
        else:
            avg_travel_time = float("nan")

        return {
            "ticks": self.time,
            "vehicles_exited": n_exited,
            "avg_travel_time": avg_travel_time,
            "vehicles_remaining": len(self.vehicles),
        }
