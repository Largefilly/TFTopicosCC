import pygame
from pygame.locals import K_ESCAPE, K_UP, K_DOWN, K_RIGHT
import csv
import os

from src.config import SimulationConfig
from src.model import TrafficModel
from src.visualization import TrafficVisualizer

METRICS_FILE = "metrics_log.csv"


def compute_day_summary(
    model: TrafficModel,
    day_start_tick: int,
    day_end_tick: int,
    day_index: int,
    ticks_per_day: int,
):
    """
    Calcula el resumen SOLO para los vehículos que terminaron su viaje
    entre day_start_tick (incluido) y day_end_tick (excluido).

    Además calcula métricas de horas punta:
    - Mañana: 07:00–09:00
    - Tarde:  18:00–21:00
    """
    # Vehículos que salieron en este día
    vehicles_in_day = [
        v for v in model.exited_vehicles
        if v.exit_time is not None
        and day_start_tick <= v.exit_time < day_end_tick
    ]

    # Duraciones globales (todo el día)
    durations_all = []
    for v in vehicles_in_day:
        if v.start_time is None:
            continue
        durations_all.append(v.exit_time - v.start_time)

    vehicles_exited = len(durations_all)
    if vehicles_exited > 0:
        total_travel = sum(durations_all)
        avg_travel_time = total_travel / vehicles_exited
    else:
        avg_travel_time = 0.0

    vehicles_remaining = len(model.vehicles)

    # --- Horas punta ---
    ticks_per_hour = ticks_per_day // 24

    # 07:00–09:00
    morning_start = day_start_tick + 7 * ticks_per_hour
    morning_end   = day_start_tick + 9 * ticks_per_hour

    # 18:00–21:00
    evening_start = day_start_tick + 18 * ticks_per_hour
    evening_end   = day_start_tick + 21 * ticks_per_hour

    def summarize_window(start_tick, end_tick):
        vs = [
            v for v in vehicles_in_day
            if start_tick <= v.exit_time < end_tick
        ]
        durs = []
        for v in vs:
            if v.start_time is None:
                continue
            durs.append(v.exit_time - v.start_time)

        n = len(durs)
        if n > 0:
            avg_t = sum(durs) / n
        else:
            avg_t = 0.0

        return {
            "vehicles_exited": n,
            "avg_travel_time": avg_t,  # en ticks
        }

    morning_peak = summarize_window(morning_start, morning_end)
    evening_peak = summarize_window(evening_start, evening_end)

    return {
        "day": day_index,
        "ticks": day_end_tick - day_start_tick,
        "vehicles_exited": vehicles_exited,
        "avg_travel_time": avg_travel_time,
        "vehicles_remaining": vehicles_remaining,
        "morning_peak": morning_peak,
        "evening_peak": evening_peak,
    }

def append_metrics_to_csv(day_index, summary_fixed, summary_adaptive, seconds_per_tick):
    """
    Guarda en metrics_log.csv un resumen de FIXED y ADAPTIVE por día.
    Si el archivo no existe, escribe cabecera.
    """
    file_exists = os.path.isfile(METRICS_FILE)

    # Convertir tiempos de ticks a minutos
    def ticks_to_min(ticks):
        return (ticks * seconds_per_tick) / 60.0

    row = {
        "day": day_index,
        "fixed_veh_day": summary_fixed["vehicles_exited"],
        "fixed_avg_ticks_day": summary_fixed["avg_travel_time"],
        "fixed_avg_min_day": ticks_to_min(summary_fixed["avg_travel_time"]),
        "fixed_veh_morning": summary_fixed["morning_peak"]["vehicles_exited"],
        "fixed_avg_ticks_morning": summary_fixed["morning_peak"]["avg_travel_time"],
        "fixed_avg_min_morning": ticks_to_min(summary_fixed["morning_peak"]["avg_travel_time"]),
        "fixed_veh_evening": summary_fixed["evening_peak"]["vehicles_exited"],
        "fixed_avg_ticks_evening": summary_fixed["evening_peak"]["avg_travel_time"],
        "fixed_avg_min_evening": ticks_to_min(summary_fixed["evening_peak"]["avg_travel_time"]),
        "adaptive_veh_day": summary_adaptive["vehicles_exited"],
        "adaptive_avg_ticks_day": summary_adaptive["avg_travel_time"],
        "adaptive_avg_min_day": ticks_to_min(summary_adaptive["avg_travel_time"]),
        "adaptive_veh_morning": summary_adaptive["morning_peak"]["vehicles_exited"],
        "adaptive_avg_ticks_morning": summary_adaptive["morning_peak"]["avg_travel_time"],
        "adaptive_avg_min_morning": ticks_to_min(summary_adaptive["morning_peak"]["avg_travel_time"]),
        "adaptive_veh_evening": summary_adaptive["evening_peak"]["vehicles_exited"],
        "adaptive_avg_ticks_evening": summary_adaptive["evening_peak"]["avg_travel_time"],
        "adaptive_avg_min_evening": ticks_to_min(summary_adaptive["evening_peak"]["avg_travel_time"]),
    }

    fieldnames = list(row.keys())

    with open(METRICS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def main():
    pygame.init()

    # 30 s/tick -> 24h = 2880 ticks
    seconds_per_tick = 30
    ticks_per_day = int(24 * 3600 / seconds_per_tick)

    # Config base (solo cambia el modo de control)
    base_kwargs = dict(
        ticks=ticks_per_day,          # lo usamos como "ticks por día"
        seconds_per_tick=seconds_per_tick,
        use_time_of_day=True,
        seed=42,                      # misma semilla para que los dos vean patrones similares
    )

    # Modelo FIXED
    config_fixed = SimulationConfig(
        control_mode="fixed",
        **base_kwargs,
    )
    model_fixed = TrafficModel(config_fixed)

    # Modelo ADAPTIVE
    config_adaptive = SimulationConfig(
        control_mode="adaptive",
        **base_kwargs,
    )
    model_adaptive = TrafficModel(config_adaptive)

    # Visualizador: mostramos el modelo adaptive (el más interesante visualmente)
    visualizer = TrafficVisualizer(model_adaptive)

    clock = pygame.time.Clock()
    running = True

    # Velocidad de simulación: ticks por frame (0 = pausado)
    sim_speed = 1
    visualizer.sim_speed = sim_speed

    step_once = False

    # Día simulado actual
    current_day_index = 0  # 0-based
    visualizer.current_day = 1

    while running:
        # 1. Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_UP:
                    sim_speed = min(sim_speed + 1, 20)
                elif event.key == K_DOWN:
                    sim_speed = max(sim_speed - 1, 0)
                elif event.key == K_RIGHT:
                    step_once = True

        visualizer.sim_speed = sim_speed if sim_speed > 0 else 0

        # 2. Avanzar ambos modelos (SIEMPRE en lockstep)
        if sim_speed > 0:
            for _ in range(sim_speed):
                prev_time = model_adaptive.time  # mismo que fixed
                prev_day = prev_time // ticks_per_day

                # Avanzar los dos
                model_fixed.step()
                model_adaptive.step()

                new_time = model_adaptive.time
                new_day = new_time // ticks_per_day

                # Actualizar día actual mostrado en HUD
                visualizer.current_day = new_day + 1

                # ¿Cruzamos el límite de un día en este paso?
                if new_day > prev_day:
                    # Día completado: prev_day (0-based); para humanos, prev_day + 1
                    day_index = prev_day + 1
                    day_start = prev_day * ticks_per_day
                    day_end = day_start + ticks_per_day

                    summary_fixed = compute_day_summary(
                        model_fixed, day_start, day_end, day_index, ticks_per_day
                    )
                    summary_adaptive = compute_day_summary(
                        model_adaptive, day_start, day_end, day_index, ticks_per_day
                    )

                    visualizer.finished = True
                    visualizer.final_summary = {
                        "day": day_index,
                        "fixed": summary_fixed,
                        "adaptive": summary_adaptive,
                    }
                    append_metrics_to_csv(day_index, summary_fixed, summary_adaptive, seconds_per_tick)

        elif step_once:
            prev_time = model_adaptive.time
            prev_day = prev_time // ticks_per_day

            model_fixed.step()
            model_adaptive.step()
            step_once = False

            new_time = model_adaptive.time
            new_day = new_time // ticks_per_day

            visualizer.current_day = new_day + 1

            if new_day > prev_day:
                day_index = prev_day + 1
                day_start = prev_day * ticks_per_day
                day_end = day_start + ticks_per_day

                summary_fixed = compute_day_summary(
                    model_fixed, day_start, day_end, day_index
                )
                summary_adaptive = compute_day_summary(
                    model_adaptive, day_start, day_end, day_index
                )

                visualizer.finished = True
                visualizer.final_summary = {
                    "day": day_index,
                    "fixed": summary_fixed,
                    "adaptive": summary_adaptive,
                }

        # 3. Dibujar (muestra solo el modelo adaptive)
        visualizer.draw()

        # 4. FPS
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
