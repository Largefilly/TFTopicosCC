from statistics import mean
from typing import Dict, List

from .config import SimulationConfig
from .model import TrafficModel



def run_simulation(
    control_mode: str = "fixed",
    arrival_rate_ns: float = 0.30,
    arrival_rate_ew: float = 0.20,
    ticks: int = 600,
    seed: int = 42,
    verbose: bool = True,
) -> Dict[str, float]:

    config = SimulationConfig(
        control_mode=control_mode,
        arrival_rate_ns=arrival_rate_ns,
        arrival_rate_ew=arrival_rate_ew,
        ticks=ticks,
        seed=seed,
        use_time_of_day=False,  # aquí no usamos hora del día
    )
    model = TrafficModel(config)

    for _ in range(config.ticks):
        model.step()

    summary = model.get_summary()
    if verbose:
        print(f"\n=== Modo de control: {control_mode} ===")
        print(f"Ticks simulados:         {summary['ticks']}")
        print(f"Vehículos que cruzaron:  {summary['vehicles_exited']}")
        print(f"Tiempo medio de viaje:   {summary['avg_travel_time']:.2f}")
        print(f"Vehículos restantes:     {summary['vehicles_remaining']}")
    return summary


def run_full_day(
    control_mode: str = "fixed",
    seconds_per_tick: int = 10,
    seed: int = 42,
    verbose: bool = True,
) -> Dict[str, float]:

    # 24 horas * 3600 s / seconds_per_tick
    ticks_per_day = int(24 * 3600 / seconds_per_tick)

    config = SimulationConfig(
        control_mode=control_mode,
        ticks=ticks_per_day,
        seed=seed,
        seconds_per_tick=seconds_per_tick,
        use_time_of_day=True,  # clave: usar hora del día
    )
    model = TrafficModel(config)

    for _ in range(ticks_per_day):
        model.step()

    summary = model.get_summary()
    if verbose:
        print(f"\n=== Simulación de día completo | Modo: {control_mode} ===")
        print(f"Ticks simulados:         {summary['ticks']}")
        print(f"Vehículos que cruzaron:  {summary['vehicles_exited']}")
        print(f"Tiempo medio de viaje:   {summary['avg_travel_time']:.2f}")
        print(f"Vehículos restantes:     {summary['vehicles_remaining']}")

    return summary
