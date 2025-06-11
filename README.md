
# Plataforma de Chat com Juízes de IA

**Uma plataforma de chat interativa onde alunos e atendentes tiram dúvidas, com dois juízes de IA para garantir a qualidade das respostas.**

## Funcionalidades
- **Chat Aluno x Atendente**: O aluno envia perguntas e o atendente responde.
- **Juízes de IA**:
  - **Juiz Gente Boa**: Avalia a conversa de forma amigável.
  - **Juiz Rígido**: Avalia a correção das respostas e identifica possíveis erros.
- **Logs de Conversa**: As conversas são registradas em `conversa.log`.

## Tecnologias Utilizadas
- **Flask**
- **python-dotenv**
- **ChatGoogleGenerativeAI**

## Como Rodar

### 1. Clonar o Repositório

```bash
git clone <URL do repositório>
```

### 2. Criar e Ativar o Ambiente Virtual

```bash
python -m venv .venv
.venv\Scripts\Activate  # No Windows
source .venv/bin/activate  # No macOS/Linux
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Crie o arquivo `.env` e adicione sua chave de API do Google Gemini:

```
GEMINI_API_KEY=your_google_api_key_here
```

### 5. Rodar a Aplicação

```bash
flask run
```

Acesse a aplicação em: `http://127.0.0.1:5000/`.

---