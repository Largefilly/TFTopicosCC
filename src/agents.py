import math
import random
from enum import Enum, auto


class Direction(Enum):
    NORTH_SOUTH = auto()
    SOUTH_NORTH = auto()
    EAST_WEST = auto()
    WEST_EAST = auto()


class VehicleAgent:
    
    _id_counter = 0

    def __init__(self, direction: Direction, start_time: int, start_distance: float):
        VehicleAgent._id_counter += 1
        self.id = VehicleAgent._id_counter
        self.direction = direction
        self.distance = start_distance  # distancia hasta la intersección (>= 0)
        self.start_time = start_time
        self.exit_time = None

    def step(self, model: "TrafficModel"):
        
        if self.exit_time is not None:
            return

        cfg = model.config

        # 1) Si ya cruzó (distance < 0): sigue saliendo hasta desaparecer
        if self.distance < 0.0:
            step_distance = cfg.vehicle_speed
            self.distance -= step_distance  # se va haciendo más negativo

            # Cuando ya "salió" lo suficiente, lo sacamos del sistema
            if self.distance <= -cfg.post_cross_distance:
                self.exit_time = model.time
                model.mark_vehicle_exited(self)
            return

        # 2) Si está en la línea de stop (distance ~ 0)
        if math.isclose(self.distance, 0.0, abs_tol=1e-6):
            if model.traffic_light.can_cross(self.direction):
                # Semáforo en verde: entra a la intersección (pasa a distance < 0)
                step_distance = min(cfg.vehicle_speed, cfg.post_cross_distance)
                self.distance -= step_distance
            else:
                # Luz roja: se queda quieto en la línea de stop
                return
        else:
            # 3) Fase de acercamiento (distance > 0): respeta al de adelante
            step_distance = min(cfg.vehicle_speed, self.distance)
            desired_distance = self.distance - step_distance

            leading_dist = model.get_leading_vehicle_distance(self)
            if leading_dist is None:
                # Soy el primero de la cola -> puedo llegar hasta 0
                min_allowed = 0.0
            else:
                min_allowed = leading_dist + cfg.min_vehicle_gap

            new_distance = max(desired_distance, min_allowed)
            new_distance = max(new_distance, 0.0)

            self.distance = new_distance


class TrafficLightPhase(Enum):
    NS_GREEN = auto()  # Verde para Norte-Sur / Sur-Norte
    EW_GREEN = auto()  # Verde para Este-Oeste / Oeste-Este
    YELLOW = auto()    # Amarillo (podríamos refinar por dirección, pero simplificamos)


class TrafficLightAgent:
    
    def __init__(self, config, rng: random.Random):
        self.config = config
        self.rng = rng
        self.phase = TrafficLightPhase.NS_GREEN
        self.time_in_phase = 0
        self.current_green_direction = "NS"  # "NS" o "EW"

    def step(self, model: "TrafficModel"):
        self.time_in_phase += 1

        if self.phase == TrafficLightPhase.YELLOW:
            # Después del amarillo, cambiamos de sentido
            if self.time_in_phase >= self.config.yellow_time:
                self._switch_to_opposite_green()
        else:
            # Fase verde: dependiendo del modo, decidimos si cambiamos
            if self.config.control_mode == "fixed":
                self._handle_fixed_cycle()
            else:
                self._handle_adaptive_cycle(model)

    def _handle_fixed_cycle(self):
        # Ciclo muy simple: green_min = green_max = duración fija, por ejemplo
        if self.time_in_phase >= self.config.green_min:
            # Pasamos por amarillo antes de invertir
            self._switch_to_yellow()

    def _handle_adaptive_cycle(self, model: "TrafficModel"):
        
        if self.time_in_phase < self.config.green_min:
            return  # aún no evaluamos cambiar

        # Medir colas
        queue_ns = model.get_queue_size_ns()
        queue_ew = model.get_queue_size_ew()

        # ¿estamos en verde NS o EW?
        if self.current_green_direction == "NS":
            my_queue = queue_ns
            other_queue = queue_ew
        else:
            my_queue = queue_ew
            other_queue = queue_ns

        # Regla 1: si el opuesto tiene mucha más cola, cambiar
        if other_queue > my_queue + 3:  # umbral arbitrario, luego lo puedes tunear
            self._switch_to_yellow()
            return

        # Regla 2: si hemos alcanzado el máximo, cambiar sí o sí
        if self.time_in_phase >= self.config.green_max:
            self._switch_to_yellow()

    def _switch_to_yellow(self):
        self.phase = TrafficLightPhase.YELLOW
        self.time_in_phase = 0

    def _switch_to_opposite_green(self):
        self.phase = TrafficLightPhase.NS_GREEN if self.current_green_direction == "EW" else TrafficLightPhase.EW_GREEN
        self.current_green_direction = "NS" if self.current_green_direction == "EW" else "EW"
        self.time_in_phase = 0

    def can_cross(self, direction: Direction) -> bool:
        if self.phase == TrafficLightPhase.YELLOW:
            # En amarillo asumimos que ya no se inicia el cruce
            return False

        if self.phase == TrafficLightPhase.NS_GREEN:
            return direction in (Direction.NORTH_SOUTH, Direction.SOUTH_NORTH)
        elif self.phase == TrafficLightPhase.EW_GREEN:
            return direction in (Direction.EAST_WEST, Direction.WEST_EAST)
        return False
