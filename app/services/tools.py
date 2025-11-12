"""
Tools (Ferramentas) para o Agente de IA
Funções que o GPT pode chamar para realizar cálculos e consultas
"""

from datetime import datetime, date
from typing import Dict, List, Optional
import json

# ==============================================
# CALCULADORAS DE IMPOSTOS
# ==============================================

def calcular_das_simples_nacional(
    receita_bruta_12_meses: float,
    anexo: int,
    mes_referencia: Optional[str] = None
) -> Dict:
    """
    Calcula o valor da DAS do Simples Nacional
    
    Args:
        receita_bruta_12_meses: Receita bruta acumulada dos últimos 12 meses (R$)
        anexo: Anexo do Simples Nacional (1 a 5)
        mes_referencia: Mês de referência (formato: MM/AAAA). Se None, usa mês atual
    
    Returns:
        Dict com cálculo detalhado da DAS
    """
    
    if mes_referencia is None:
        mes_referencia = datetime.now().strftime("%m/%Y")
    
    # Tabelas simplificadas por faixa (valores 2024/2025)
    # Fonte: Lei Complementar 123/2006 atualizada
    tabelas = {
        1: {  # Comércio
            "nome": "Anexo I - Comércio",
            "faixas": [
                {"ate": 180000, "aliquota": 4.0, "deducao": 0},
                {"ate": 360000, "aliquota": 7.3, "deducao": 5940},
                {"ate": 720000, "aliquota": 9.5, "deducao": 13860},
                {"ate": 1800000, "aliquota": 10.7, "deducao": 22500},
                {"ate": 3600000, "aliquota": 14.3, "deducao": 87300},
                {"ate": 4800000, "aliquota": 19.0, "deducao": 378000}
            ]
        },
        2: {  # Indústria
            "nome": "Anexo II - Indústria",
            "faixas": [
                {"ate": 180000, "aliquota": 4.5, "deducao": 0},
                {"ate": 360000, "aliquota": 7.8, "deducao": 5940},
                {"ate": 720000, "aliquota": 10.0, "deducao": 13860},
                {"ate": 1800000, "aliquota": 11.2, "deducao": 22500},
                {"ate": 3600000, "aliquota": 14.7, "deducao": 85500},
                {"ate": 4800000, "aliquota": 30.0, "deducao": 720000}
            ]
        },
        3: {  # Serviços (sem retenção ISS)
            "nome": "Anexo III - Serviços",
            "faixas": [
                {"ate": 180000, "aliquota": 6.0, "deducao": 0},
                {"ate": 360000, "aliquota": 11.2, "deducao": 9360},
                {"ate": 720000, "aliquota": 13.5, "deducao": 17640},
                {"ate": 1800000, "aliquota": 16.0, "deducao": 35640},
                {"ate": 3600000, "aliquota": 21.0, "deducao": 125640},
                {"ate": 4800000, "aliquota": 33.0, "deducao": 648000}
            ]
        },
        4: {  # Serviços
            "nome": "Anexo IV - Serviços",
            "faixas": [
                {"ate": 180000, "aliquota": 4.5, "deducao": 0},
                {"ate": 360000, "aliquota": 9.0, "deducao": 8100},
                {"ate": 720000, "aliquota": 10.2, "deducao": 12420},
                {"ate": 1800000, "aliquota": 14.0, "deducao": 39780},
                {"ate": 3600000, "aliquota": 22.0, "deducao": 183780},
                {"ate": 4800000, "aliquota": 33.0, "deducao": 828000}
            ]
        },
        5: {  # Serviços (fator R)
            "nome": "Anexo V - Serviços",
            "faixas": [
                {"ate": 180000, "aliquota": 15.5, "deducao": 0},
                {"ate": 360000, "aliquota": 18.0, "deducao": 4500},
                {"ate": 720000, "aliquota": 19.5, "deducao": 9900},
                {"ate": 1800000, "aliquota": 20.5, "deducao": 17100},
                {"ate": 3600000, "aliquota": 23.0, "deducao": 62100},
                {"ate": 4800000, "aliquota": 30.5, "deducao": 540000}
            ]
        }
    }
    
    if anexo not in tabelas:
        return {
            "erro": f"Anexo {anexo} inválido. Use 1, 2, 3, 4 ou 5.",
            "anexos_disponiveis": list(tabelas.keys())
        }
    
    if receita_bruta_12_meses > 4800000:
        return {
            "erro": "Receita bruta excede o limite do Simples Nacional (R$ 4.800.000,00)",
            "sugestao": "Empresa deve migrar para Lucro Presumido ou Lucro Real"
        }
    
    # Encontra a faixa correta
    tabela = tabelas[anexo]
    faixa_aplicavel = None
    
    for faixa in tabela["faixas"]:
        if receita_bruta_12_meses <= faixa["ate"]:
            faixa_aplicavel = faixa
            break
    
    if faixa_aplicavel is None:
        return {"erro": "Não foi possível determinar a faixa"}
    
    # Cálculo da alíquota efetiva
    aliquota_efetiva = ((receita_bruta_12_meses * faixa_aplicavel["aliquota"] / 100) - faixa_aplicavel["deducao"]) / receita_bruta_12_meses * 100
    
    # Assumindo receita mensal média
    receita_mensal_media = receita_bruta_12_meses / 12
    valor_das = receita_mensal_media * aliquota_efetiva / 100
    
    return {
        "anexo": anexo,
        "nome_anexo": tabela["nome"],
        "mes_referencia": mes_referencia,
        "receita_bruta_12_meses": f"R$ {receita_bruta_12_meses:,.2f}",
        "receita_mensal_media": f"R$ {receita_mensal_media:,.2f}",
        "aliquota_nominal": f"{faixa_aplicavel['aliquota']}%",
        "aliquota_efetiva": f"{aliquota_efetiva:.2f}%",
        "valor_deducao": f"R$ {faixa_aplicavel['deducao']:,.2f}",
        "valor_das_mensal": f"R$ {valor_das:,.2f}",
        "vencimento": "Dia 20 do mês seguinte ao de referência",
        "observacao": "Valores aproximados. Consulte um contador para cálculo exato."
    }


def calcular_ferias(
    salario_bruto: float,
    dias_ferias: int = 30,
    vende_10_dias: bool = False
) -> Dict:
    """
    Calcula férias de um colaborador
    
    Args:
        salario_bruto: Salário bruto mensal do colaborador (R$)
        dias_ferias: Quantidade de dias de férias (padrão: 30)
        vende_10_dias: Se o colaborador vai vender 10 dias de férias (abono pecuniário)
    
    Returns:
        Dict com cálculo detalhado de férias
    """
    
    # Validações
    if dias_ferias < 1 or dias_ferias > 30:
        return {"erro": "Dias de férias deve estar entre 1 e 30"}
    
    dias_gozo = dias_ferias
    dias_vendidos = 0
    
    if vende_10_dias:
        if dias_ferias < 30:
            return {"erro": "Para vender 10 dias, é necessário ter direito a 30 dias de férias"}
        dias_gozo = 20
        dias_vendidos = 10
    
    # Cálculos
    valor_ferias = (salario_bruto / 30) * dias_gozo
    terco_constitucional = valor_ferias / 3
    valor_abono = (salario_bruto / 30) * dias_vendidos if vende_10_dias else 0
    terco_abono = valor_abono / 3 if vende_10_dias else 0
    
    total_bruto = valor_ferias + terco_constitucional + valor_abono + terco_abono
    
    # INSS (tabela 2024/2025 simplificada)
    inss = 0
    if salario_bruto <= 1412.00:
        inss = salario_bruto * 0.075
    elif salario_bruto <= 2666.68:
        inss = salario_bruto * 0.09
    elif salario_bruto <= 4000.03:
        inss = salario_bruto * 0.12
    else:
        inss = salario_bruto * 0.14
    
    # IRRF simplificado (pode variar)
    base_ir = total_bruto - inss
    irrf = 0
    if base_ir > 2259.20:
        if base_ir <= 2826.65:
            irrf = base_ir * 0.075 - 169.44
        elif base_ir <= 3751.05:
            irrf = base_ir * 0.15 - 381.44
        elif base_ir <= 4664.68:
            irrf = base_ir * 0.225 - 662.77
        else:
            irrf = base_ir * 0.275 - 896.00
    
    total_descontos = inss + irrf
    total_liquido = total_bruto - total_descontos
    
    return {
        "salario_bruto": f"R$ {salario_bruto:,.2f}",
        "dias_ferias_total": dias_ferias,
        "dias_gozo": dias_gozo,
        "dias_vendidos": dias_vendidos,
        "calculo": {
            "valor_ferias": f"R$ {valor_ferias:,.2f}",
            "terco_constitucional": f"R$ {terco_constitucional:,.2f}",
            "abono_pecuniario": f"R$ {valor_abono:,.2f}",
            "terco_abono": f"R$ {terco_abono:,.2f}",
            "total_bruto": f"R$ {total_bruto:,.2f}"
        },
        "descontos": {
            "inss": f"R$ {inss:,.2f}",
            "irrf": f"R$ {irrf:,.2f}",
            "total_descontos": f"R$ {total_descontos:,.2f}"
        },
        "total_liquido": f"R$ {total_liquido:,.2f}",
        "observacao": "Cálculo aproximado. Valores exatos dependem de outras variáveis."
    }


# ==============================================
# CALENDÁRIO FISCAL
# ==============================================

def obter_obrigacoes_mes(mes: Optional[int] = None, ano: Optional[int] = None) -> Dict:
    """
    Retorna as principais obrigações fiscais de um mês específico
    
    Args:
        mes: Mês (1-12). Se None, usa mês atual
        ano: Ano. Se None, usa ano atual
    
    Returns:
        Dict com lista de obrigações do mês
    """
    
    if mes is None:
        mes = datetime.now().month
    if ano is None:
        ano = datetime.now().year
    
    if mes < 1 or mes > 12:
        return {"erro": "Mês deve estar entre 1 e 12"}
    
    meses_nome = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    # Obrigações mensais recorrentes
    obrigacoes_mensais = [
        {
            "nome": "DAS - Simples Nacional",
            "prazo": "Dia 20",
            "descricao": "Documento de Arrecadação do Simples Nacional",
            "aplica_se": "Empresas optantes pelo Simples Nacional",
            "prioridade": "Alta"
        },
        {
            "nome": "DARF - Tributos Federais",
            "prazo": "Dia 20",
            "descricao": "Pagamento de impostos federais (IRPJ, CSLL, PIS, COFINS)",
            "aplica_se": "Lucro Real e Lucro Presumido",
            "prioridade": "Alta"
        },
        {
            "nome": "GPS - INSS",
            "prazo": "Dia 20",
            "descricao": "Guia da Previdência Social",
            "aplica_se": "Todas as empresas com funcionários",
            "prioridade": "Alta"
        },
        {
            "nome": "FGTS",
            "prazo": "Dia 7",
            "descricao": "Fundo de Garantia do Tempo de Serviço",
            "aplica_se": "Todas as empresas com funcionários",
            "prioridade": "Alta"
        },
        {
            "nome": "SEFIP/GFIP",
            "prazo": "Dia 7",
            "descricao": "Sistema Empresa de Recolhimento do FGTS",
            "aplica_se": "Empresas com funcionários",
            "prioridade": "Média"
        },
        {
            "nome": "DCTF Web",
            "prazo": "Dia 15",
            "descricao": "Declaração de Débitos e Créditos Tributários Federais",
            "aplica_se": "Lucro Real e Presumido",
            "prioridade": "Média"
        }
    ]
    
    # Obrigações anuais por mês
    obrigacoes_anuais = {
        1: [
            {"nome": "13º Salário (2ª Parcela)", "prazo": "Até 20/12 (ano anterior)", 
             "descricao": "Segunda parcela do 13º salário"}
        ],
        2: [
            {"nome": "RAIS", "prazo": "Até o último dia útil de março",
             "descricao": "Relação Anual de Informações Sociais"}
        ],
        3: [
            {"nome": "DIRF", "prazo": "Último dia útil de fevereiro",
             "descricao": "Declaração do Imposto de Renda Retido na Fonte"}
        ],
        4: [
            {"nome": "IRPF", "prazo": "Até 31/05",
             "descricao": "Declaração de Imposto de Renda Pessoa Física"}
        ],
        5: [
            {"nome": "DEFIS", "prazo": "Até 31/03",
             "descricao": "Declaração de Informações Socioeconômicas e Fiscais (Simples)"}
        ]
    }
    
    obrigacoes = obrigacoes_mensais.copy()
    
    if mes in obrigacoes_anuais:
        obrigacoes.extend(obrigacoes_anuais[mes])
    
    return {
        "mes": mes,
        "mes_nome": meses_nome[mes - 1],
        "ano": ano,
        "total_obrigacoes": len(obrigacoes),
        "obrigacoes": obrigacoes,
        "observacao": "Prazos podem variar se caírem em finais de semana ou feriados."
    }


# ==============================================
# CONSULTAS E VALIDAÇÕES
# ==============================================

def verificar_tipo_regime_tributario(
    receita_anual: float,
    atividade: str = "comercio"
) -> Dict:
    """
    Sugere o melhor regime tributário baseado na receita
    
    Args:
        receita_anual: Receita bruta anual estimada (R$)
        atividade: Tipo de atividade (comercio, industria, servicos)
    
    Returns:
        Dict com análise e sugestão de regime
    """
    
    analise = {
        "receita_anual": f"R$ {receita_anual:,.2f}",
        "atividade": atividade,
        "regimes_disponiveis": []
    }
    
    # Simples Nacional
    if receita_anual <= 4800000:
        analise["regimes_disponiveis"].append({
            "regime": "Simples Nacional",
            "viavel": True,
            "aliquota_estimada": "4% a 33% (dependendo do anexo e faixa)",
            "vantagens": [
                "Simplificação de obrigações",
                "Unificação de tributos em guia única",
                "Menor carga tributária para pequenas empresas"
            ],
            "desvantagens": [
                "Limite de receita (R$ 4,8 milhões/ano)",
                "Restrições de atividades",
                "Não permite alguns tipos de créditos tributários"
            ]
        })
    
    # Lucro Presumido
    if receita_anual <= 78000000:
        analise["regimes_disponiveis"].append({
            "regime": "Lucro Presumido",
            "viavel": True,
            "aliquota_estimada": "13,33% a 16,33% (aproximado)",
            "vantagens": [
                "Menor complexidade que Lucro Real",
                "Tributação sobre lucro presumido, não real",
                "Adequado para empresas com margens altas"
            ],
            "desvantagens": [
                "Não permite compensação de prejuízos",
                "Limite de receita (R$ 78 milhões/ano)",
                "Pode ser desvantajoso para margens baixas"
            ]
        })
    
    # Lucro Real
    analise["regimes_disponiveis"].append({
        "regime": "Lucro Real",
        "viavel": True,
        "aliquota_estimada": "Variável (sobre lucro efetivo)",
        "vantagens": [
            "Tributa apenas o lucro real",
            "Permite compensação de prejuízos",
            "Obrigatório para receitas acima de R$ 78 milhões"
        ],
        "desvantagens": [
            "Maior complexidade contábil",
            "Mais obrigações acessórias",
            "Custos contábeis maiores"
        ]
    })
    
    # Sugestão
    if receita_anual <= 360000:
        analise["sugestao"] = "Simples Nacional (melhor custo-benefício para pequenas empresas)"
    elif receita_anual <= 4800000:
        analise["sugestao"] = "Avaliar Simples vs Lucro Presumido (depende da margem de lucro)"
    elif receita_anual <= 78000000:
        analise["sugestao"] = "Lucro Presumido (se margens altas) ou Lucro Real"
    else:
        analise["sugestao"] = "Lucro Real (obrigatório)"
    
    analise["observacao"] = "Consultoria com contador é essencial para decisão final."
    
    return analise


# ==============================================
# LISTA DE FERRAMENTAS PARA O GPT
# ==============================================

AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calcular_das_simples_nacional",
            "description": "Calcula o valor da DAS (Documento de Arrecadação do Simples Nacional) baseado na receita bruta dos últimos 12 meses e no anexo da empresa",
            "parameters": {
                "type": "object",
                "properties": {
                    "receita_bruta_12_meses": {
                        "type": "number",
                        "description": "Receita bruta acumulada dos últimos 12 meses em reais (R$)"
                    },
                    "anexo": {
                        "type": "integer",
                        "description": "Anexo do Simples Nacional: 1=Comércio, 2=Indústria, 3=Serviços, 4=Serviços, 5=Serviços com fator R",
                        "enum": [1, 2, 3, 4, 5]
                    },
                    "mes_referencia": {
                        "type": "string",
                        "description": "Mês de referência no formato MM/AAAA (opcional)",
                        "nullable": True
                    }
                },
                "required": ["receita_bruta_12_meses", "anexo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calcular_ferias",
            "description": "Calcula o valor de férias de um colaborador, incluindo 1/3 constitucional e abono pecuniário (venda de férias)",
            "parameters": {
                "type": "object",
                "properties": {
                    "salario_bruto": {
                        "type": "number",
                        "description": "Salário bruto mensal do colaborador em reais (R$)"
                    },
                    "dias_ferias": {
                        "type": "integer",
                        "description": "Quantidade de dias de férias (padrão: 30 dias)",
                        "default": 30
                    },
                    "vende_10_dias": {
                        "type": "boolean",
                        "description": "Se o colaborador vai vender 10 dias de férias (abono pecuniário)",
                        "default": False
                    }
                },
                "required": ["salario_bruto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obter_obrigacoes_mes",
            "description": "Retorna a lista de obrigações fiscais e trabalhistas de um mês específico, incluindo prazos e descrições",
            "parameters": {
                "type": "object",
                "properties": {
                    "mes": {
                        "type": "integer",
                        "description": "Número do mês (1-12). Se não informado, usa o mês atual",
                        "minimum": 1,
                        "maximum": 12,
                        "nullable": True
                    },
                    "ano": {
                        "type": "integer",
                        "description": "Ano de referência. Se não informado, usa o ano atual",
                        "nullable": True
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verificar_tipo_regime_tributario",
            "description": "Analisa e sugere o melhor regime tributário (Simples Nacional, Lucro Presumido ou Lucro Real) baseado na receita anual da empresa",
            "parameters": {
                "type": "object",
                "properties": {
                    "receita_anual": {
                        "type": "number",
                        "description": "Receita bruta anual estimada ou realizada em reais (R$)"
                    },
                    "atividade": {
                        "type": "string",
                        "description": "Tipo de atividade da empresa",
                        "enum": ["comercio", "industria", "servicos"],
                        "default": "comercio"
                    }
                },
                "required": ["receita_anual"]
            }
        }
    }
]

# Mapeamento de funções para execução
FUNCTION_MAP = {
    "calcular_das_simples_nacional": calcular_das_simples_nacional,
    "calcular_ferias": calcular_ferias,
    "obter_obrigacoes_mes": obter_obrigacoes_mes,
    "verificar_tipo_regime_tributario": verificar_tipo_regime_tributario
}
