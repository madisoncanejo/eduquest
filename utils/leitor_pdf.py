import fitz  # pymupdf
import base64
import io
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def pdf_para_imagens(arquivo_pdf):
    """Converte cada página do PDF em imagem base64."""
    doc = fitz.open(stream=arquivo_pdf.read(), filetype="pdf")
    imagens = []
    for pagina in doc:
        pix = pagina.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        imagens.append(img_base64)
    doc.close()
    return imagens

def extrair_texto_pdf(arquivo_pdf):
    """Extrai texto do PDF usando GPT-4o vision."""
    imagens = pdf_para_imagens(arquivo_pdf)
    textos = []

    for i, img_base64 in enumerate(imagens):
        resposta = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Você está recebendo a imagem de uma página de prova escolar de Física ou Matemática. "
                                "Transcreva todo o conteúdo da página exatamente como está, preservando:\n"
                                "- Enunciados das questões\n"
                                "- Alternativas (A, B, C, D, E)\n"
                                "- Fórmulas matemáticas escritas de forma legível (ex: v² = v₀² + 2aΔx, m/s², √)\n"
                                "- Descrições de imagens, gráficos, circuitos ou diagramas que aparecerem\n"
                                "NÃO use LaTeX. NÃO use notação computacional. Escreva como um professor escreveria."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{img_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000
        )
        textos.append(resposta.choices[0].message.content)

    return "\n\n".join(textos)