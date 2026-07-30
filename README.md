# Aurora Restaurante

API em FastAPI para operação de restaurante, com mesas, comandas,
cozinha, fechamento, notificações, painel web e aplicativo móvel.

## Requisitos

- Python 3.11 ou superior
- Ambiente virtual recomendado

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite o `.env` e defina uma `SECRET_KEY` longa e exclusiva. Em produção,
a API não inicia sem essa configuração.

## Executar

```bash
uvicorn backend.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Documentação: `http://127.0.0.1:8000/docs`
- Painel web: `http://127.0.0.1:8000/web`

## Primeiro acesso

Quando o banco ainda não possui usuários, crie o primeiro gerente:

```bash
curl -X POST http://127.0.0.1:8000/auth/bootstrap \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Gerente",
    "email": "gerente@example.com",
    "senha": "troque-esta-senha",
    "perfil": "gerente"
  }'
```

O endpoint é bloqueado definitivamente assim que o primeiro usuário é
criado.

## Login

As credenciais são enviadas no corpo JSON, e nunca na URL:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"gerente@example.com","senha":"troque-esta-senha"}'
```

Use o valor de `access_token` nas rotas protegidas:

```text
Authorization: Bearer SEU_TOKEN
```

Senhas novas são armazenadas com hash. Contas antigas que ainda estejam
em texto puro são migradas automaticamente para hash após o primeiro
login válido.

O aplicativo móvel mostra a tela de login antes de carregar mesas e
produtos. Configure o endereço da API antes de iniciar o Expo:

```bash
EXPO_PUBLIC_API_URL=http://SEU-IP:8000 npm start
```

`127.0.0.1` aponta para o próprio aparelho ou emulador; em um celular
físico, use o IP do computador que executa a API.

## Configuração de segurança

| Variável | Uso |
|---|---|
| `ENVIRONMENT` | Use `production` no servidor |
| `SECRET_KEY` | Assina os tokens JWT; obrigatória em produção |
| `CORS_ORIGINS` | Origens permitidas, separadas por vírgula |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token |
| `DATABASE_URL` | Endereço do banco SQLAlchemy |

Não publique o arquivo `.env` nem o banco SQLite.

## Perfis e permissões

| Área | Perfis |
|---|---|
| Mesas e produtos (leitura) | qualquer usuário autenticado |
| Cadastro de mesas e produtos | gerente |
| Comandas e itens | garçom ou gerente |
| Cozinha | cozinha ou gerente |
| Fechamento | caixa ou gerente |
| Administração de usuários | gerente |

Os canais WebSocket exigem o token na conexão:

```text
ws://127.0.0.1:8000/ws/mesas?token=SEU_TOKEN
```

Mensagens enviadas por clientes não são retransmitidas. Os eventos do
sistema continuam sendo publicados somente pelo backend.
