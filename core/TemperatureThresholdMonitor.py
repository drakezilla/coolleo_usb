class TemperatureThresholdMonitor:
    """
    Emite 'critical' o 'warning' cuando hay N lecturas consecutivas
    por encima de los umbrales. Evita spam: no repite el mismo aviso
    hasta que la temperatura vuelva a 'normal' (por debajo de warning).
    """

    def __init__(self, consecutive_required: int = 3):
        self.N = max(1, consecutive_required)
        self._warn_count = 0
        self._crit_count = 0
        self._last_alert_state = None  # None | "warning" | "critical"

    def reset(self):
        self._warn_count = 0
        self._crit_count = 0
        self._last_alert_state = None

    def check(self, temp_c: float, warning_c: int, critical_c: int):
        """
        Devuelve: "critical" | "warning" | None
        Lógica:
          - Cuenta consecutivos por encima de critical y warning.
          - Prioriza critical sobre warning.
          - No repite avisos del mismo tipo hasta volver a normal.
        """
        try:
            t = float(temp_c)
        except (TypeError, ValueError):
            return None

        if t >= float(critical_c):
            self._crit_count += 1
            self._warn_count = 0
        elif t >= float(warning_c):
            self._warn_count += 1
            self._crit_count = 0
        else:
            self.reset()
            return None

        if self._crit_count >= self.N:
            if self._last_alert_state != "critical":
                self._last_alert_state = "critical"
                return "critical"
            return None

        if self._warn_count >= self.N:
            if self._last_alert_state not in ("warning", "critical"):
                self._last_alert_state = "warning"
                return "warning"
            return None

        return None
