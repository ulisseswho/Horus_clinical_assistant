from dataclasses import dataclass


@dataclass
class ParametrosVitais:
    pa: str = "-"
    fc: str = "-"
    fr: str = "-"
    temp: str = "-"
    sato2: str = "-"
    glicemia: str = "-"

    def formatado(self) -> str:
        return (
            f"PA {self.pa} mmHg || "
            f"FC {self.fc} bpm || "
            f"FR {self.fr} irpm || "
            f"Temp {self.temp} °C || "
            f"SatO2 {self.sato2} % || "
            f"Glicemia {self.glicemia} mg/dL"
        )
    
from dataclasses import field


@dataclass
class Paciente:
    id: str
    parametros: ParametrosVitais = field(default_factory=ParametrosVitais)

    # blocos principais
    impressao_diagnostica: str = "-"
    queixa_principal: str = "-"
    hda: str = "-"
    hpp: str = "-"
    exame_fisico: str = "-"
    exames_laboratoriais: str = "-"
    exames_imagem: str = "-"
    pareceres: str = "-"
    condutas: str = "-"

    def resumo(self) -> str:
        return (
            f"Paciente: {self.id}\n"
            f"QP: {self.queixa_principal}\n"
            f"Impressão: {self.impressao_diagnostica}\n"
        )

@dataclass
class AtendimentoClinico:
    paciente: Paciente

    def gerar_texto(self) -> str:
        return (
            "»» Atendimento Clínico\n\n"
            f"»» Impressão Diagnóstica:\n{self.paciente.impressao_diagnostica}\n\n"
            f"»» Queixa Principal:\n{self.paciente.queixa_principal}\n\n"
            f"»» História da Doença Atual:\n{self.paciente.hda}\n\n"
            f"»» Histórico Médico Pregresso:\n{self.paciente.hpp}\n\n"
            f"»» Exame Físico:\n{self.paciente.exame_fisico}\n\n"
            f"»» Parâmetros na admissão:\n{self.paciente.parametros.formatado()}\n\n"
            f"»» Exames laboratoriais:\n{self.paciente.exames_laboratoriais}\n\n"
            f"»» Exames de imagem:\n{self.paciente.exames_imagem}\n\n"
            f"»» Pareceres:\n{self.paciente.pareceres}\n\n"
            f"»» Condutas:\n{self.paciente.condutas}"
        )