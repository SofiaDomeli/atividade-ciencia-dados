from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import os
import re
import difflib
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

# Blueprint
bp = Blueprint("chat", __name__)

# Logs
LOG = "logs/conversa.log"

# LLM config
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Modelos: Atendente (humano ou IA) e Juiz
llm_juiz = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, temperature=0.2)
prompt_juiz = ChatPromptTemplate.from_template(
    """Você é um juiz crítico que está tentando ajudar o aluno a não receber resposta incorretas. Avalie se a resposta do atendente está correta, parcialmente correta ou incorreta.
    Responda nesse estilo:
    A informação está <span class='info'>CORRETA, PARCIALMENTE CORRETA ou INCORRETA!</span> E você deve justificar sua resposta. Não coloque nada em negrito.
    Pergunta do aluno: "{pergunta}"
    Resposta do atendente: "{resposta}"
    """
)

llm_atendente = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, temperature=0.8)
prompt_conversa= ChatPromptTemplate.from_template(
    """Você é um juíz bem gente boa que avalia a conversa entre o aluno e o atendente.
    Avalie a conversa e dê um feedback construtivo.
    Não coloque nada em negrito.\n\n
    {conversa}"""
    )

# Funções principais
def registrar_log(origem, mensagem):
    os.makedirs("logs", exist_ok=True)
    if mensagem.strip():
        with open(LOG, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{origem.upper()}] {mensagem.strip()}\n")


def carregar_historico():
    if not os.path.exists(LOG):
        return []
    with open(LOG, "r") as f:
        linhas = list(f.readlines())
    coloridas = []
    for l in linhas:
        if "[ALUNO]" in l:
            cor = "red"
        elif "[ATENDENTE]" in l:
            cor = "blue"
        elif "[JUIZ]" in l:
            cor = "green"
        else:
            cor = "black"
        coloridas.append(f'<font color="{cor}">{l.strip()}</font>')
    return coloridas


def limpar_historico():
    if os.path.exists(LOG):
        os.remove(LOG)
    os.makedirs("logs", exist_ok=True)


def carregar_conversa():
    return open(LOG).read() if os.path.exists(LOG) else ""


def consultar_rag(pergunta):
    base = []
    documentos_dir = "documentos"
    os.makedirs(documentos_dir, exist_ok=True)
 
    for nome in os.listdir(documentos_dir):
        if nome.endswith(".txt"):
            try:
                with open(f"{documentos_dir}/{nome}", encoding="utf-8") as f:
                    base.append(f.read())
            except IOError as e:
                print(f"Erro ao ler documento {nome}: {e}")
    texto = "\n".join(base)
    sentencas = re.split(r'(?<=\w[.!?]) +', texto) 
    sentencas = sentencas[-20:]
    print(texto)
    print(sentencas)
    melhores = difflib.get_close_matches(pergunta, sentencas, n=3, cutoff=0.6)
    if len(melhores) == 0:
        return "Nenhum contexto relevante encontrado."
    return "\n".join(melhores)


def avaliar_resposta(pergunta, resposta):
    try:
        input_juiz = prompt_juiz.format(pergunta=pergunta, resposta=resposta)
        output = llm_juiz.invoke(input_juiz)
        return output.content
    except Exception as e:
        return f"Erro ao avaliar: {e}"


def avaliar_conversa(conversa):
    try:
        inputs = prompt_conversa.format(conversa=conversa)
        output = llm_atendente.invoke(inputs)
        return output.content
    except Exception as e:
        return f"Erro ao avaliar conversa: {e}"


# Rotas

@bp.route("/")
def home():
    return render_template("index.html")


@bp.route("/usuario", methods=["GET", "POST"])
def usuario():
    if request.method == "POST":
        if "enviar" in request.form:
            registrar_log("aluno", request.form["mensagem"])
        elif "encerrar" in request.form:
            registrar_log("aluno", "CONVERSA ENCERRADA PELO ALUNO")
        elif "reiniciar" in request.form:
            limpar_historico()
            return redirect(url_for(".usuario"))
    return render_template("usuario.html", historico=carregar_historico())


@bp.route("/atendente", methods=["GET", "POST"])
def atendente():
    avaliacao = None
    pergunta = None
    if request.method == "POST":
        if "enviar" in request.form:
            resposta = request.form["mensagem"]
            registrar_log("atendente", resposta)

            conversa = carregar_historico()[-2:]  # Pega as últimas duas linhas
            pergunta = None
            for l in conversa:
                if "[ALUNO]" in l:
                    pergunta = l.split("]")[-1].strip()
                    break
            if pergunta:
                avaliacao = avaliar_resposta(pergunta, resposta)
                registrar_log("juiz", avaliacao)
        elif "encerrar" in request.form:
            registrar_log("atendente", "CONVERSA ENCERRADA PELO ATENDENTE")
        elif "reiniciar" in request.form:
            limpar_historico()
            return redirect(url_for(".usuario"))
    return render_template("atendente.html", historico=carregar_historico(), avaliacao=avaliacao)


@bp.route("/rag")
def api_rag():
    contexto = carregar_conversa().splitlines()[-3:-2]
    print(f"Contexto carregado: {contexto}")
    if len(contexto) > 500:
        contexto = contexto[-500:]
    resultado = consultar_rag(contexto)
    print(resultado)
    return resultado

@bp.route("/juiz")
def api_juiz():
    conversa = carregar_conversa()
    resultado = avaliar_conversa(conversa)
    return jsonify({"resultado": resultado})