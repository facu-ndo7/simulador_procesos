from dataclasses import dataclass, field

ESTADOS_PROCESO = (
    "Nuevo",
    "Esperando memoria",
    "Listo",
    "Ejecutando",
    "Bloqueado",
    "Esperando página",
    "Terminado",
)

@dataclass
class Proceso:
    pid: str
    rafaga: int
    memoria: int
    estado: str = "Nuevo"
    restante: int = field(init=False)


    def __post_init__(self):
        self.restante = self.rafaga


@dataclass
class Bloque:
    inicio: int
    tamanio: int
    pid: str | None = None


    @property
    def libre(self):
        return self.pid is None


    @property
    def fin(self):
        return self.inicio + self.tamanio - 1