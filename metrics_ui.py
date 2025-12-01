# metrics_ui.py
import csv
import os
import tkinter as tk
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

METRICS_FILE = "metrics_log.csv"


class MetricsWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparación de semáforo fijo vs adaptativo")

        # ---------------- LAYOUT PRINCIPAL ----------------
        frame_top = ttk.Frame(root)
        frame_top.pack(side="top", fill="x", expand=False)

        frame_top_fixed = ttk.Frame(frame_top)
        frame_top_fixed.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        frame_top_adaptive = ttk.Frame(frame_top)
        frame_top_adaptive.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        frame_bottom = ttk.Frame(root)
        frame_bottom.pack(side="bottom", fill="both", expand=True)

        # ---------------- TABLA FIXED ----------------
        ttk.Label(
            frame_top_fixed,
            text="FIXED - métricas por día",
            font=("Arial", 11, "bold")
        ).pack(side="top", anchor="w")

        columns_fixed = [
            "day",
            "fixed_veh_day",
            "fixed_avg_min_day",
            "fixed_veh_morning",
            "fixed_avg_min_morning",
            "fixed_veh_evening",
            "fixed_avg_min_evening",
        ]

        self.tree_fixed = ttk.Treeview(
            frame_top_fixed, columns=columns_fixed, show="headings", height=4
        )
        self.tree_fixed.pack(side="left", fill="both", expand=True)

        vsb_f = ttk.Scrollbar(
            frame_top_fixed, orient="vertical", command=self.tree_fixed.yview
        )
        self.tree_fixed.configure(yscroll=vsb_f.set)
        vsb_f.pack(side="right", fill="y")

        headers_fixed = {
            "day": "Día",
            "fixed_veh_day": "Vehículos / día",
            "fixed_avg_min_day": "Tiempo medio / día (min)",
            "fixed_veh_morning": "Vehículos 7:00–9:00",
            "fixed_avg_min_morning": "Tiempo medio 7:00–9:00 (min)",
            "fixed_veh_evening": "Vehículos 18:00–21:00",
            "fixed_avg_min_evening": "Tiempo medio 18:00–21:00 (min)",
        }

        for col in columns_fixed:
            self.tree_fixed.heading(col, text=headers_fixed[col])
            self.tree_fixed.column(col, width=130, anchor="center")

        # ---------------- TABLA ADAPTIVE ----------------
        ttk.Label(
            frame_top_adaptive,
            text="ADAPTIVE - métricas por día",
            font=("Arial", 11, "bold")
        ).pack(side="top", anchor="w")

        columns_adaptive = [
            "day",
            "adaptive_veh_day",
            "adaptive_avg_min_day",
            "adaptive_veh_morning",
            "adaptive_avg_min_morning",
            "adaptive_veh_evening",
            "adaptive_avg_min_evening",
        ]

        self.tree_adaptive = ttk.Treeview(
            frame_top_adaptive, columns=columns_adaptive, show="headings", height=4
        )
        self.tree_adaptive.pack(side="left", fill="both", expand=True)

        vsb_a = ttk.Scrollbar(
            frame_top_adaptive, orient="vertical", command=self.tree_adaptive.yview
        )
        self.tree_adaptive.configure(yscroll=vsb_a.set)
        vsb_a.pack(side="right", fill="y")

        headers_adaptive = {
            "day": "Día",
            "adaptive_veh_day": "Vehículos / día",
            "adaptive_avg_min_day": "Tiempo medio / día (min)",
            "adaptive_veh_morning": "Vehículos 7:00–9:00",
            "adaptive_avg_min_morning": "Tiempo medio 7:00–9:00 (min)",
            "adaptive_veh_evening": "Vehículos 18:00–21:00",
            "adaptive_avg_min_evening": "Tiempo medio 18:00–21:00 (min)",
        }
        for col in columns_adaptive:
            self.tree_adaptive.heading(col, text=headers_adaptive[col])
            self.tree_adaptive.column(col, width=130, anchor="center")

        # ---------------- GRÁFICOS ----------------
        self.fig = Figure(figsize=(8, 3.2), dpi=100)
        self.ax_fixed = self.fig.add_subplot(1, 2, 1)
        self.ax_adaptive = self.fig.add_subplot(1, 2, 2)

        self.ax_fixed.set_title("FIXED - evolución tiempos medios")
        self.ax_adaptive.set_title("ADAPTIVE - evolución tiempos medios")

        for ax in (self.ax_fixed, self.ax_adaptive):
            ax.set_xlabel("Día")
            ax.set_ylabel("Tiempo medio (min)")

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_bottom)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Datos de las curvas
        self.days = []
        self.fixed_day = []
        self.fixed_morning = []
        self.fixed_evening = []
        self.adaptive_day = []
        self.adaptive_morning = []
        self.adaptive_evening = []

        # Elementos interactivos
        self.annot_fixed = None
        self.annot_adaptive = None
        self.vline_fixed = None
        self.vline_adaptive = None

        # Evento de movimiento del mouse
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)

        # Arrancar
        self.refresh()

    def refresh(self):
        # Limpiar tablas
        for row in self.tree_fixed.get_children():
            self.tree_fixed.delete(row)
        for row in self.tree_adaptive.get_children():
            self.tree_adaptive.delete(row)

        days = []
        fixed_day = []
        fixed_morning = []
        fixed_evening = []
        adaptive_day = []
        adaptive_morning = []
        adaptive_evening = []

        if os.path.isfile(METRICS_FILE):
            with open(METRICS_FILE, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    try:
                        day = r["day"]

                        # Tabla FIXED
                        self.tree_fixed.insert(
                            "",
                            "end",
                            values=[
                                day,
                                r["fixed_veh_day"],
                                f"{float(r['fixed_avg_min_day']):.1f}",
                                r["fixed_veh_morning"],
                                f"{float(r['fixed_avg_min_morning']):.1f}",
                                r["fixed_veh_evening"],
                                f"{float(r['fixed_avg_min_evening']):.1f}",
                            ],
                        )

                        # Tabla ADAPTIVE
                        self.tree_adaptive.insert(
                            "",
                            "end",
                            values=[
                                day,
                                r["adaptive_veh_day"],
                                f"{float(r['adaptive_avg_min_day']):.1f}",
                                r["adaptive_veh_morning"],
                                f"{float(r['adaptive_avg_min_morning']):.1f}",
                                r["adaptive_veh_evening"],
                                f"{float(r['adaptive_avg_min_evening']):.1f}",
                            ],
                        )

                        # Datos para gráficos
                        d = int(day)
                        days.append(d)

                        fixed_day.append(float(r["fixed_avg_min_day"]))
                        fixed_morning.append(float(r["fixed_avg_min_morning"]))
                        fixed_evening.append(float(r["fixed_avg_min_evening"]))

                        adaptive_day.append(float(r["adaptive_avg_min_day"]))
                        adaptive_morning.append(float(r["adaptive_avg_min_morning"]))
                        adaptive_evening.append(float(r["adaptive_avg_min_evening"]))
                    except (KeyError, ValueError):
                        continue

        # Guardar
        self.days = days
        self.fixed_day = fixed_day
        self.fixed_morning = fixed_morning
        self.fixed_evening = fixed_evening
        self.adaptive_day = adaptive_day
        self.adaptive_morning = adaptive_morning
        self.adaptive_evening = adaptive_evening

        # Redibujar
        self.ax_fixed.clear()
        self.ax_adaptive.clear()

        self.ax_fixed.set_title("FIXED - evolución tiempos medios")
        self.ax_adaptive.set_title("ADAPTIVE - evolución tiempos medios")
        for ax in (self.ax_fixed, self.ax_adaptive):
            ax.set_xlabel("Día")
            ax.set_ylabel("Tiempo medio (min)")
            ax.grid(True, alpha=0.3)

        if days:
            self.ax_fixed.plot(days, fixed_day, marker="o", label="Día completo")
            self.ax_fixed.plot(days, fixed_morning, marker="o", linestyle="--",
                               label="Punta 7–9")
            self.ax_fixed.plot(days, fixed_evening, marker="o", linestyle=":",
                               label="Punta 18–21")
            self.ax_fixed.legend(loc="upper right")

            self.ax_adaptive.plot(days, adaptive_day, marker="o", label="Día completo")
            self.ax_adaptive.plot(days, adaptive_morning, marker="o", linestyle="--",
                                  label="Punta 7–9")
            self.ax_adaptive.plot(days, adaptive_evening, marker="o", linestyle=":",
                                  label="Punta 18–21")
            self.ax_adaptive.legend(loc="upper right")

        self._create_interactive_elements()
        self.canvas.draw_idle()

        self.root.after(1000, self.refresh)

    # ---------- ELEMENTOS INTERACTIVOS ----------

    def _create_interactive_elements(self):
        # Limpiar anteriores si existen
        if self.annot_fixed is not None:
            try:
                self.annot_fixed.remove()
                self.annot_adaptive.remove()
                self.vline_fixed.remove()
                self.vline_adaptive.remove()
            except Exception:
                pass

        self.annot_fixed = self.ax_fixed.annotate(
            "",
            xy=(0, 0),
            xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="white", alpha=0.8),
            arrowprops=dict(arrowstyle="->"),
        )
        self.annot_fixed.set_visible(False)

        self.annot_adaptive = self.ax_adaptive.annotate(
            "",
            xy=(0, 0),
            xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="white", alpha=0.8),
            arrowprops=dict(arrowstyle="->"),
        )
        self.annot_adaptive.set_visible(False)

        # Líneas verticales
        self.vline_fixed = self.ax_fixed.axvline(
            x=self.days[0] if self.days else 0,
            color="gray",
            linestyle="--",
            alpha=0.5,
        )
        self.vline_fixed.set_visible(False)

        self.vline_adaptive = self.ax_adaptive.axvline(
            x=self.days[0] if self.days else 0,
            color="gray",
            linestyle="--",
            alpha=0.5,
        )
        self.vline_adaptive.set_visible(False)

    def on_mouse_move(self, event):
        """Muestra tooltip SOLO de la serie más cercana (día completo / 7–9 / 18–21),
        y lo refleja también en el otro gráfico para el mismo día y misma serie.
        """
        if not self.days:
            return

        if event.inaxes not in (self.ax_fixed, self.ax_adaptive):
            # Fuera de los ejes: ocultar todo
            if self.annot_fixed is not None:
                self.annot_fixed.set_visible(False)
                self.annot_adaptive.set_visible(False)
                if self.vline_fixed is not None:
                    self.vline_fixed.set_visible(False)
                if self.vline_adaptive is not None:
                    self.vline_adaptive.set_visible(False)
                self.canvas.draw_idle()
            return

        if event.xdata is None or event.ydata is None:
            return

        x = event.xdata
        y = event.ydata

        # Día más cercano al cursor
        idx = min(range(len(self.days)), key=lambda i: abs(self.days[i] - x))
        day = self.days[idx]

        # Decide en qué panel estás y qué serie está más cerca en Y
        if event.inaxes == self.ax_fixed:
            # --- Panel FIXED como origen del hover ---
            candidates = []
            if idx < len(self.fixed_day):
                candidates.append(("day", "Día completo", self.fixed_day[idx]))
            if idx < len(self.fixed_morning):
                candidates.append(("morning", "Punta 7–9", self.fixed_morning[idx]))
            if idx < len(self.fixed_evening):
                candidates.append(("evening", "Punta 18–21", self.fixed_evening[idx]))

            if not candidates:
                return

            # Serie más cercana en Y
            series_key, series_label, series_y = min(
                candidates, key=lambda t: abs(t[2] - y)
            )

            # Línea vertical
            if self.vline_fixed is not None:
                self.vline_fixed.set_xdata([day, day])
                self.vline_fixed.set_visible(True)
            if self.vline_adaptive is not None:
                self.vline_adaptive.set_xdata([day, day])
                self.vline_adaptive.set_visible(True)

            # Tooltip FIXED (solo serie seleccionada)
            self.annot_fixed.xy = (day, series_y)
            self.annot_fixed.set_text(
                f"Día {day}\n{series_label}: {series_y:.1f} min"
            )
            self.annot_fixed.set_visible(True)

            # Tooltip ADAPTIVE para misma serie y día
            if series_key == "day" and idx < len(self.adaptive_day):
                y2 = self.adaptive_day[idx]
            elif series_key == "morning" and idx < len(self.adaptive_morning):
                y2 = self.adaptive_morning[idx]
            elif series_key == "evening" and idx < len(self.adaptive_evening):
                y2 = self.adaptive_evening[idx]
            else:
                y2 = None

            if y2 is not None:
                self.annot_adaptive.xy = (day, y2)
                self.annot_adaptive.set_text(
                    f"Día {day}\n{series_label}: {y2:.1f} min"
                )
                self.annot_adaptive.set_visible(True)
            else:
                self.annot_adaptive.set_visible(False)

        else:
            # --- Panel ADAPTIVE como origen del hover ---
            candidates = []
            if idx < len(self.adaptive_day):
                candidates.append(("day", "Día completo", self.adaptive_day[idx]))
            if idx < len(self.adaptive_morning):
                candidates.append(("morning", "Punta 7–9", self.adaptive_morning[idx]))
            if idx < len(self.adaptive_evening):
                candidates.append(("evening", "Punta 18–21", self.adaptive_evening[idx]))

            if not candidates:
                return

            series_key, series_label, series_y = min(
                candidates, key=lambda t: abs(t[2] - y)
            )

            # Línea vertical
            if self.vline_fixed is not None:
                self.vline_fixed.set_xdata([day, day])
                self.vline_fixed.set_visible(True)
            if self.vline_adaptive is not None:
                self.vline_adaptive.set_xdata([day, day])
                self.vline_adaptive.set_visible(True)

            # Tooltip ADAPTIVE
            self.annot_adaptive.xy = (day, series_y)
            self.annot_adaptive.set_text(
                f"Día {day}\n{series_label}: {series_y:.1f} min"
            )
            self.annot_adaptive.set_visible(True)

            # Tooltip FIXED misma serie
            if series_key == "day" and idx < len(self.fixed_day):
                y2 = self.fixed_day[idx]
            elif series_key == "morning" and idx < len(self.fixed_morning):
                y2 = self.fixed_morning[idx]
            elif series_key == "evening" and idx < len(self.fixed_evening):
                y2 = self.fixed_evening[idx]
            else:
                y2 = None

            if y2 is not None:
                self.annot_fixed.xy = (day, y2)
                self.annot_fixed.set_text(
                    f"Día {day}\n{series_label}: {y2:.1f} min"
                )
                self.annot_fixed.set_visible(True)
            else:
                self.annot_fixed.set_visible(False)

        self.canvas.draw_idle()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x650")
    app = MetricsWindow(root)
    root.mainloop()
