from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gerar_questoes(texto_original, qtd_questoes, tipo_questoes, gerar_gabarito):

    if tipo_questoes == "Objetivas":
        instrucao_formato = f"""Crie EXATAMENTE {qtd_questoes} questoes de multipla escolha.
Nem mais, nem menos. Exatamente {qtd_questoes} questoes.
Cada questao deve ter exatamente 5 alternativas rotuladas A, B, C, D, E.
NAO crie questoes discursivas."""

    elif tipo_questoes == "Discursivas":
        instrucao_formato = f"""Crie EXATAMENTE {qtd_questoes} questoes discursivas abertas.
Nem mais, nem menos. Exatamente {qtd_questoes} questoes.
NAO crie alternativas A, B, C, D, E.
Cada questao deve pedir que o aluno desenvolva o raciocinio e apresente os calculos."""

    else:
        metade = qtd_questoes // 2
        resto = qtd_questoes - metade
        instrucao_formato = f"""Crie EXATAMENTE {metade} questoes de multipla escolha com alternativas A, B, C, D, E
e EXATAMENTE {resto} questoes discursivas abertas.
Total EXATO de {qtd_questoes} questoes. Nem mais, nem menos.
Identifique claramente: 'PARTE 1 - OBJETIVAS' e 'PARTE 2 - DISCURSIVAS'."""

    instrucao_gabarito = ""
    if gerar_gabarito:
        if tipo_questoes == "Objetivas":
            instrucao_gabarito = f"""
Ao final adicione:
GABARITO:
1. [letra correta]
... (exatamente {qtd_questoes} linhas de gabarito)
"""
        elif tipo_questoes == "Discursivas":
            instrucao_gabarito = f"""
Ao final adicione:
GABARITO:
1. [resolucao completa com calculos]
... (exatamente {qtd_questoes} linhas de gabarito)
"""
        else:
            instrucao_gabarito = """
Ao final adicione:
GABARITO:
(para as objetivas: letra correta; para as discursivas: resolucao completa)
"""

    prompt = f"""Voce e um professor experiente de Fisica e Matematica do Ensino Medio.

Analise o conteudo abaixo e identifique o conceito que esta sendo avaliado.

{instrucao_formato}

REGRAS OBRIGATORIAS:
- Comece diretamente pela questao 1, sem introducoes ou explicacoes
- Cada questao deve ter contexto, valores numericos e situacao-problema DIFERENTES da original e entre si
- Crie situacoes do cotidiano variadas: automoveis, esportes, objetos domesticos, fenomenos naturais
- Nunca repita o mesmo contexto ou os mesmos valores numericos
- Use linguagem clara e adequada para o Ensino Medio
- Numere as questoes a partir do numero 1
- Nao inclua cabecalho, nome de escola, professor, serie ou data
- NUNCA use formatacao LaTeX
- NUNCA use notacao computacional ou de programacao
- Para expoentes use: m/s², km/h², m/s³
- Para raiz quadrada use o simbolo: √
- Para multiplicacao use o simbolo: ×
- Para divisao use o simbolo: ÷ ou a barra /
- Para aproximacao use: ≈
- Escreva equacoes em linguagem natural: v = √(2gh)

REGRAS PARA ALTERNATIVAS (somente objetivas):
- A alternativa correta deve ocupar letras variadas ao longo da prova
- As alternativas incorretas devem ser resultados de erros comuns de calculo

{instrucao_gabarito}

CONTEUDO ORIGINAL:
{texto_original}
"""

    resposta = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Voce e um professor de Fisica e Matematica do Ensino Medio. Siga as instrucoes com precisao absoluta. Gere EXATAMENTE {qtd_questoes} questoes, nem mais nem menos. Nao adicione texto introdutorio antes das questoes."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9
    )

    texto_gerado = resposta.choices[0].message.content
    return texto_gerado