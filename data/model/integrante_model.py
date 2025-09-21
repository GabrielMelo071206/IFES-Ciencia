from dataclasses import dataclass
from typing import Optional

@dataclass
class Integrante:
    id: int
    nome: str
    turma: str
    funcao: str  
    foto: Optional[str] = None  
    redes_sociais: Optional[str] = None 