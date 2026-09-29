from dataclasses import dataclass


@dataclass
class Timer:
    duration: float
    remaining: float | None = None
    can_overflow: bool = False
    _overflow: float = 0.0

    def __post_init__(self):
        if self.remaining is None:
            self.remaining = self.duration

    def update(self, dt: float) -> None:
        remaining = self.remaining - dt
        if self.can_overflow:
            self._overflow = (0 - remaining)
        
        self.remaining = max(0.0, remaining)
        if self.remaining <= 1e-9:
            self.remaining = 0.0

    def expired(self) -> bool:
        return self.remaining <= 0.0

    def restart(self) -> None:
        self.remaining = self.duration                
        if self.can_overflow and self._overflow > 0.0:
            self.remaining -= self._overflow
        self._overflow = 0.0
