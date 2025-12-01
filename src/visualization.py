import pygame
from .agents import Direction, TrafficLightPhase
from .model import TrafficModel


class TrafficVisualizer:
    def __init__(
        self,
        model: TrafficModel,
        width: int = 800,
        height: int = 800,
        scale: float = 8.0,
    ):
        """
        model: instancia de TrafficModel
        width, height: tamaño de la ventana
        scale: cuántos píxeles representa 1 unidad de distancia del modelo
        """
        self.model = model
        self.width = width
        self.height = height
        self.scale = scale

        # Centro de la intersección en pantalla
        self.cx = width // 2
        self.cy = height // 2

        # Inicializar ventana
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Simulación de Intersección - Vista Simple")

        # Colores
        self.COLOR_BACKGROUND = (30, 30, 30)        # gris oscuro
        self.COLOR_ROAD = (80, 80, 80)              # gris carretera
        self.COLOR_CAR_NS = (0, 150, 255)           # azul
        self.COLOR_CAR_EW = (255, 100, 0)           # naranja
        self.COLOR_WHITE = (250, 250, 250)
        self.COLOR_RED = (200, 0, 0)
        self.COLOR_GREEN = (0, 180, 0)
        self.COLOR_YELLOW = (230, 200, 0)

        # Ancho de las vías
        self.road_width = 200  # píxeles
        self.intersection_half = self.road_width // 2  # "radio" de la caja central

        # Velocidad de simulación mostrada en HUD
        self.sim_speed = 1

        # ------ Geometría del paso de cebra y línea de stop ------
        # Grosor del bloque de paso de cebra
        self.crosswalk_width = 30

        # Distancia desde el centro al CENTRO del paso de cebra.
        # Lo colocamos en el borde de la intersección, un poco hacia afuera.
        # Tomas como referencia tu imagen: la cebra está justo en el borde del cruce.
        self.crosswalk_offset = (
            self.intersection_half - self.crosswalk_width // 2 - 5
        )

        # Distancia desde el centro a la LÍNEA DE STOP (un poco antes de la cebra)
        # Orden desde el centro hacia afuera: intersección -> cebra -> línea de stop -> autos
        self.stop_line_offset = (
            self.crosswalk_offset + self.crosswalk_width // 2 + 10
        )

        # Indicador de fin de día y resumen
        self.finished = False
        self.final_summary = None
        # Día simulado actual (1, 2, 3, ...)
        self.current_day = 1

    # ---------------- DIBUJO PRINCIPAL ----------------

    def draw(self):
        """Dibuja un frame completo."""
        self.screen.fill(self.COLOR_BACKGROUND)

        # 1. Vías + pasos de cebra + líneas de stop
        self._draw_roads()

        # 2. Semáforos
        self._draw_traffic_light()

        # 3. Vehículos
        self._draw_vehicles()

        # 4. HUD (texto + posible resumen final)
        self._draw_hud()

        pygame.display.flip()

    # ---------------- COMPONENTES ----------------

    def _draw_roads(self):
        # Carretera horizontal
        pygame.draw.rect(
            self.screen,
            self.COLOR_ROAD,
            (
                0,
                self.cy - self.road_width // 2,
                self.width,
                self.road_width,
            ),
        )
        # Carretera vertical
        pygame.draw.rect(
            self.screen,
            self.COLOR_ROAD,
            (
                self.cx - self.road_width // 2,
                0,
                self.road_width,
                self.height,
            ),
        )

        # Pasos de cebra + líneas de stop
        self._draw_crosswalks_and_stop_lines()

    def _draw_crosswalks_and_stop_lines(self):
        """Dibuja pasos de cebra más cortos (no formando un cuadrado completo)
        y la línea de stop detrás de cada uno.
        """
        stripe_color = self.COLOR_WHITE
        stripe_width = 8
        stripe_gap = 6

        # Las cebras solo ocuparán una franja central de la vía,
        # por ejemplo el 60% del ancho de la carretera.
        span_factor = 0.6
        half_span = int(self.road_width * span_factor / 2)

        # ---------- Pasos de cebra horizontales (NORTE y SUR) ----------
        for sign in (-1, 1):  # -1 = norte, 1 = sur
            # Centro del paso de cebra medido desde el centro de la intersección
            center_y = self.cy + sign * self.crosswalk_offset
            band_half = self.crosswalk_width // 2
            top = center_y - band_half
            height = self.crosswalk_width

            # Solo ocupamos el tramo central de la vía horizontal
            x_start = self.cx - half_span
            x_end = self.cx + half_span

            # Rayas verticales dentro de la banda
            x = x_start
            while x < x_end:
                pygame.draw.rect(
                    self.screen,
                    stripe_color,
                    (x, top, stripe_width, height),
                )
                x += stripe_width + stripe_gap

            # Línea de stop (esta sí cruza todo el carril)
            full_x_start = self.cx - self.road_width // 2
            full_x_end = self.cx + self.road_width // 2

            if sign == -1:
                # Norte: stop más arriba del centro
                stop_y = self.cy - self.stop_line_offset
            else:
                # Sur: stop más abajo del centro
                stop_y = self.cy + self.stop_line_offset

            pygame.draw.line(
                self.screen,
                stripe_color,
                (full_x_start, stop_y),
                (full_x_end, stop_y),
                2,
            )

        # ---------- Pasos de cebra verticales (OESTE y ESTE) ----------
        for sign in (-1, 1):  # -1 = oeste, 1 = este
            center_x = self.cx + sign * self.crosswalk_offset
            band_half = self.crosswalk_width // 2
            left = center_x - band_half
            width = self.crosswalk_width

            # Solo ocupamos el tramo central de la vía vertical
            y_start = self.cy - half_span
            y_end = self.cy + half_span

            # Rayas horizontales dentro de la banda
            y = y_start
            while y < y_end:
                pygame.draw.rect(
                    self.screen,
                    stripe_color,
                    (left, y, width, stripe_width),
                )
                y += stripe_width + stripe_gap

            # Línea de stop (cruza todo el carril)
            full_y_start = self.cy - self.road_width // 2
            full_y_end = self.cy + self.road_width // 2

            if sign == -1:
                # Oeste: stop más a la izquierda del centro
                stop_x = self.cx - self.stop_line_offset
            else:
                # Este: stop más a la derecha del centro
                stop_x = self.cx + self.stop_line_offset

            pygame.draw.line(
                self.screen,
                stripe_color,
                (stop_x, full_y_start),
                (stop_x, full_y_end),
                2,
            )

    def _draw_traffic_light(self):
        """
        Dibuja dos semáforos con tres luces (rojo, amarillo, verde)
        para los flujos NS y EW, encendiendo la luz correspondiente
        según la fase del modelo.
        """
        tl = self.model.traffic_light
        phase = tl.phase
        current_dir = tl.current_green_direction  # "NS" o "EW"

        # --------- Lógica de luces (encendido/apagado) ---------
        # Cada cabeza: (red_on, yellow_on, green_on)

        def get_lights_for(direction: str):
            # Fase amarilla: ambos direcciones en amarillo
            if phase == TrafficLightPhase.YELLOW:
                return (False, True, False)

            if direction == "NS":
                if phase == TrafficLightPhase.NS_GREEN and current_dir == "NS":
                    # NS tiene luz verde
                    return (False, False, True)
                else:
                    # NS en rojo
                    return (True, False, False)
            else:  # "EW"
                if phase == TrafficLightPhase.EW_GREEN and current_dir == "EW":
                    # EW tiene luz verde
                    return (False, False, True)
                else:
                    # EW en rojo
                    return (True, False, False)

        ns_lights = get_lights_for("NS")
        ew_lights = get_lights_for("EW")

        # --------- Parámetros visuales ---------
        box_width = 22
        box_height = 60
        light_radius = 6
        spacing = 4  # margen interno

        off_color = (80, 80, 80)  # color de foco apagado
        box_color = (40, 40, 40)  # cuerpo del semáforo

        # Posiciones de las cajas (ya al costado de los carriles)
        # NS: al lado del carril que viene desde el norte
        ns_cx = self.cx - self.road_width // 2 - 25
        ns_cy = self.cy - self.crosswalk_offset - 20

        # EW: al lado del carril que viene desde el oeste
        ew_cx = self.cx + self.crosswalk_offset + 20
        ew_cy = self.cy - self.road_width // 2 - 25

        def draw_head(cx, cy, lights):
            """Dibuja una cabeza de semáforo (caja + 3 focos)."""
            # Caja
            pygame.draw.rect(
                self.screen,
                box_color,
                (cx - box_width // 2, cy - box_height // 2, box_width, box_height),
                border_radius=4,
            )

            # Posiciones de los 3 focos (top, mid, bottom)
            top_y = cy - box_height // 2 + light_radius + spacing
            mid_y = cy
            bot_y = cy + box_height // 2 - light_radius - spacing

            colors = [self.COLOR_RED, self.COLOR_YELLOW, self.COLOR_GREEN]
            ys = [top_y, mid_y, bot_y]

            for on, col, y in zip(lights, colors, ys):
                color = col if on else off_color
                pygame.draw.circle(self.screen, color, (cx, y), light_radius)

        # Dibujar cabeza NS y cabeza EW
        draw_head(ns_cx, ns_cy, ns_lights)
        draw_head(ew_cx, ew_cy, ew_lights)

    def _draw_vehicles(self):
        # Tamaño base del auto (vista superior)
        base_length = 26  # largo del auto
        base_width = 12   # ancho del auto

        for v in self.model.vehicles:
            x, y = self._vehicle_to_screen(v)

            # Autos en vertical (N-S / S-N) vs horizontal (E-W / W-E)
            if v.direction in (Direction.NORTH_SOUTH, Direction.SOUTH_NORTH):
                color = self.COLOR_CAR_NS
                car_width = base_width
                car_height = base_length   # largo hacia arriba/abajo
            else:
                color = self.COLOR_CAR_EW
                car_width = base_length    # largo hacia izquierda/derecha
                car_height = base_width

            # Rectángulo centrado en (x, y) con la orientación adecuada
            rect = pygame.Rect(0, 0, car_width, car_height)
            rect.center = (x, y)
            pygame.draw.rect(self.screen, color, rect)

    def _draw_hud(self):
        """Dibuja texto con info simple + resumen diario de fixed vs adaptive, incluyendo horas punta."""
        font = pygame.font.SysFont("Arial", 18)

        # Hora simulada (según el modelo que estamos visualizando)
        try:
            hour, minute = self.model.get_simulated_clock()
            time_str = f"{hour:02d}:{minute:02d}"
        except AttributeError:
            time_str = "--:--"

        # Escenario actual (según hora del día)
        try:
            scenario_label = self.model.get_time_of_day_segment_label()
        except AttributeError:
            scenario_label = "Escenario: N/A"

        current_day = getattr(self, "current_day", 1)

        text_lines = [
            f"Día simulado: {current_day}",
            f"Tick: {self.model.time}",
            f"Hora simulada: {time_str}",
            scenario_label,
            f"Modo visualizado: {self.model.config.control_mode}",  # adaptive
            f"Velocidad: x{self.sim_speed}",
            f"Autos en sistema (modo visualizado): {len(self.model.vehicles)}",
        ]

        # Resumen del ÚLTIMO día completo para ambos modos (fixed y adaptive)
        if self.finished and self.final_summary is not None:
            fs = self.final_summary
            cfg = self.model.config

            day_index = fs.get("day", current_day - 1)

            summary_fixed = fs.get("fixed")
            summary_adaptive = fs.get("adaptive")

            text_lines.append("")
            text_lines.append(f"=== Resumen del día {day_index} (24h) ===")

            # --------- MODO FIXED ---------
            if summary_fixed is not None:
                avg_ticks_f = summary_fixed["avg_travel_time"]
                avg_minutes_f = (avg_ticks_f * cfg.seconds_per_tick) / 60.0
                veh_per_hour_f = summary_fixed["vehicles_exited"] / 24.0

                mp_f = summary_fixed.get("morning_peak", {})
                ep_f = summary_fixed.get("evening_peak", {})

                text_lines.append("[FIXED]")
                text_lines.append(
                    f"  Veh. que cruzaron (día): {summary_fixed['vehicles_exited']}"
                )
                text_lines.append(
                    f"  Tiempo medio viaje (día): {avg_ticks_f:.2f} ticks (~{avg_minutes_f:.1f} min)"
                )
                text_lines.append(
                    f"  Flujo medio (día): {veh_per_hour_f:.1f} veh/h"
                )
                text_lines.append(
                    f"  Veh. restantes al final del día: {summary_fixed['vehicles_remaining']}"
                )

                # Horas punta FIXED
                mp_veh_f = mp_f.get("vehicles_exited", 0)
                mp_avg_f = mp_f.get("avg_travel_time", 0.0)
                mp_min_f = (mp_avg_f * cfg.seconds_per_tick) / 60.0 if mp_veh_f > 0 else 0.0

                ep_veh_f = ep_f.get("vehicles_exited", 0)
                ep_avg_f = ep_f.get("avg_travel_time", 0.0)
                ep_min_f = (ep_avg_f * cfg.seconds_per_tick) / 60.0 if ep_veh_f > 0 else 0.0

                text_lines.append("  [Punta mañana 07–09]")
                text_lines.append(
                    f"    Veh: {mp_veh_f}, t_med: {mp_avg_f:.1f} ticks (~{mp_min_f:.1f} min)"
                    if mp_veh_f > 0 else
                    "    (sin vehículos en este intervalo)"
                )
                text_lines.append("  [Punta tarde 18–21]")
                text_lines.append(
                    f"    Veh: {ep_veh_f}, t_med: {ep_avg_f:.1f} ticks (~{ep_min_f:.1f} min)"
                    if ep_veh_f > 0 else
                    "    (sin vehículos en este intervalo)"
                )

            # --------- MODO ADAPTIVE ---------
            if summary_adaptive is not None:
                avg_ticks_a = summary_adaptive["avg_travel_time"]
                avg_minutes_a = (avg_ticks_a * cfg.seconds_per_tick) / 60.0
                veh_per_hour_a = summary_adaptive["vehicles_exited"] / 24.0

                mp_a = summary_adaptive.get("morning_peak", {})
                ep_a = summary_adaptive.get("evening_peak", {})

                text_lines.append("[ADAPTIVE]")
                text_lines.append(
                    f"  Veh. que cruzaron (día): {summary_adaptive['vehicles_exited']}"
                )
                text_lines.append(
                    f"  Tiempo medio viaje (día): {avg_ticks_a:.2f} ticks (~{avg_minutes_a:.1f} min)"
                )
                text_lines.append(
                    f"  Flujo medio (día): {veh_per_hour_a:.1f} veh/h"
                )
                text_lines.append(
                    f"  Veh. restantes al final del día: {summary_adaptive['vehicles_remaining']}"
                )

                # Horas punta ADAPTIVE
                mp_veh_a = mp_a.get("vehicles_exited", 0)
                mp_avg_a = mp_a.get("avg_travel_time", 0.0)
                mp_min_a = (mp_avg_a * cfg.seconds_per_tick) / 60.0 if mp_veh_a > 0 else 0.0

                ep_veh_a = ep_a.get("vehicles_exited", 0)
                ep_avg_a = ep_a.get("avg_travel_time", 0.0)
                ep_min_a = (ep_avg_a * cfg.seconds_per_tick) / 60.0 if ep_veh_a > 0 else 0.0

                text_lines.append("  [Punta mañana 07–09]")
                text_lines.append(
                    f"    Veh: {mp_veh_a}, t_med: {mp_avg_a:.1f} ticks (~{mp_min_a:.1f} min)"
                    if mp_veh_a > 0 else
                    "    (sin vehículos en este intervalo)"
                )
                text_lines.append("  [Punta tarde 18–21]")
                text_lines.append(
                    f"    Veh: {ep_veh_a}, t_med: {ep_avg_a:.1f} ticks (~{ep_min_a:.1f} min)"
                    if ep_veh_a > 0 else
                    "    (sin vehículos en este intervalo)"
                )

        x = 10
        y = 10
        for line in text_lines:
            surface = font.render(line, True, self.COLOR_WHITE)
            self.screen.blit(surface, (x, y))
            y += 22

    # ---------------- UTILIDADES ----------------

    def _vehicle_to_screen(self, vehicle):
        """
        Convierte la distancia + dirección del vehículo en coordenadas (x, y) en pantalla.

        distance = 0  -> justo en la LÍNEA DE STOP (antes del paso de cebra)
        distance > 0  -> más atrás en el carril
        distance < 0  -> ya cruzó la línea de stop y va saliendo.
        """
        d = vehicle.distance
        s = self.scale
        offset = self.stop_line_offset

        x = self.cx
        y = self.cy

        if vehicle.direction == Direction.NORTH_SOUTH:
            # Viene desde arriba hacia abajo
            x = self.cx - self.road_width // 4
            y = self.cy - offset - d * s

        elif vehicle.direction == Direction.SOUTH_NORTH:
            # Viene desde abajo hacia arriba
            x = self.cx + self.road_width // 4
            y = self.cy + offset + d * s

        elif vehicle.direction == Direction.WEST_EAST:
            # Viene desde la izquierda hacia la derecha
            x = self.cx - offset - d * s
            y = self.cy + self.road_width // 4

        elif vehicle.direction == Direction.EAST_WEST:
            # Viene desde la derecha hacia la izquierda
            x = self.cx + offset + d * s
            y = self.cy - self.road_width // 4

        return int(x), int(y)
