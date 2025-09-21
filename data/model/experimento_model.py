from dataclasses import dataclass
from typing import Optional

@dataclass
class Experimento:
    id: int
    titulo: str
    descricao: str
    materiais: str
    capa: Optional[str] = None  
    video_explicativo: Optional[str] = None