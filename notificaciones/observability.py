
import logging
import time
import json
import functools
from collections import defaultdict, deque
from datetime import datetime, timezone
from flask import request, g


class JSONFormatter(logging.Formatter):
    """Emite cada línea de log como un objeto JSON."""
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level":     record.levelname,
            "service":   getattr(record, "service", "unknown"),
            "message":   record.getMessage(),
        }
        # Campos extra que se pueden agregar con logger.info("...", extra={...})
        for key in ("usuario_id", "endpoint", "method", "status_code",
                    "latency_ms", "circuit", "error"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def get_logger(service_name: str) -> logging.Logger:
    """Devuelve un logger JSON listo para usar."""
    logger = logging.getLogger(service_name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    # Inyecta el nombre del servicio en todos los records
    logger = logging.LoggerAdapter(logger, {"service": service_name})
    return logger



class CircuitBreaker:


    CLOSED    = "CLOSED"
    OPEN      = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,    # fallos antes de abrir
        recovery_timeout:  int = 30,   # segundos en OPEN antes de probar
        logger=None,
    ):
        self.name              = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout  = recovery_timeout
        self.logger            = logger or get_logger(name)

        self._state         = self.CLOSED
        self._failure_count = 0
        self._opened_at     = None


    @property
    def state(self) -> str:
        if self._state == self.OPEN:
            if time.time() - self._opened_at >= self.recovery_timeout:
                self._state = self.HALF_OPEN
                self.logger.warning(
                    "Circuit HALF_OPEN – probando recuperación",
                    extra={"circuit": self.name},
                )
        return self._state

    @property
    def is_open(self) -> bool:
        return self.state == self.OPEN

    def on_success(self):
        if self._state in (self.HALF_OPEN, self.OPEN):
            self.logger.info(
                "Circuit CLOSED – servicio recuperado",
                extra={"circuit": self.name},
            )
        self._state         = self.CLOSED
        self._failure_count = 0
        self._opened_at     = None

    def on_failure(self, error: Exception):
        self._failure_count += 1
        self.logger.warning(
            f"Fallo en circuito ({self._failure_count}/{self.failure_threshold}): {error}",
            extra={"circuit": self.name, "error": str(error)},
        )
        if self._failure_count >= self.failure_threshold:
            self._state     = self.OPEN
            self._opened_at = time.time()
            self.logger.error(
                "Circuit OPEN – demasiados fallos, bloqueando llamadas",
                extra={"circuit": self.name},
            )

    def call(self, func, *args, **kwargs):
        """Ejecuta `func` respetando el estado del circuit breaker."""
        if self.is_open:
            raise CircuitOpenError(
                f"Servicio '{self.name}' no disponible (circuit OPEN)"
            )
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as exc:
            self.on_failure(exc)
            raise

    def status(self) -> dict:
        return {
            "circuit":       self.name,
            "state":         self.state,
            "failure_count": self._failure_count,
            "opened_at":     self._opened_at,
        }


class CircuitOpenError(Exception):
    """Se lanza cuando el circuit breaker está abierto."""



class LatencyTracker:
    """
    Registra latencias por endpoint (últimas `maxlen` muestras).
    Exposición: GET /metrics/latency
    """

    def __init__(self, maxlen: int = 200):
        self._data: dict[str, deque] = defaultdict(lambda: deque(maxlen=maxlen))

    def record(self, endpoint: str, latency_ms: float):
        self._data[endpoint].append(latency_ms)

    def summary(self) -> dict:
        result = {}
        for endpoint, samples in self._data.items():
            if not samples:
                continue
            lst = list(samples)
            lst.sort()
            n = len(lst)
            result[endpoint] = {
                "count":   n,
                "avg_ms":  round(sum(lst) / n, 2),
                "min_ms":  round(lst[0], 2),
                "max_ms":  round(lst[-1], 2),
                "p95_ms":  round(lst[int(n * 0.95)], 2),
                "p99_ms":  round(lst[int(n * 0.99)], 2),
            }
        return result



def init_observability(app, service_name: str):

    logger  = get_logger(service_name)
    tracker = LatencyTracker()

    @app.before_request
    def _start_timer():
        g._start_time = time.perf_counter()

    @app.after_request
    def _log_request(response):
        elapsed_ms = (time.perf_counter() - g._start_time) * 1000
        endpoint   = request.path
        tracker.record(endpoint, elapsed_ms)
        logger.info(
            f"{request.method} {endpoint} → {response.status_code}",
            extra={
                "endpoint":    endpoint,
                "method":      request.method,
                "status_code": response.status_code,
                "latency_ms":  round(elapsed_ms, 2),
            },
        )
        return response

    @app.route("/metrics/latency")
    def _latency_metrics():
        from flask import jsonify
        return jsonify({
            "service": service_name,
            "metrics": tracker.summary(),
        })

    @app.route("/health")
    def _health():
        from flask import jsonify
        return jsonify({"service": service_name, "status": "ok"})

    return tracker
