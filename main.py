from src.simulation import run_full_day


def main():
    # Simular un día completo con semáforo fijo
    run_full_day(control_mode="fixed", seconds_per_tick=10, seed=42, verbose=True)

    # Simular un día completo con semáforo adaptativo
    run_full_day(control_mode="adaptive", seconds_per_tick=10, seed=42, verbose=True)


if __name__ == "__main__":
    main()
