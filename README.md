# vet_flow — Sistema Distribuído de Mensagens (Clínica Veterinária)

> **Status atual do projeto: Parte 1, em andamento.**
> Implementado até aqui: login, criação e listagem de canais, todos com
> persistência em disco — **apenas em Python**. Este README documenta
> apenas o que já existe — não descreve funcionalidades futuras como já
> implementadas.

## Objetivo

Projeto acadêmico da disciplina de Sistemas Distribuídos: um sistema de
troca de mensagens usando ZeroMQ, com múltiplos clientes (bots) e múltiplos
servidores, aplicado ao domínio de uma clínica veterinária (registros de
validade de produtos, limpeza, avisos, histórico de operações).

O sistema é implementado em duas linguagens — **Python** e **Java** —, cada
uma com uma implementação completa (client + server), como réplicas
heterogêneas que falam o mesmo protocolo.

## Arquitetura geral (visão do projeto completo)

> Esta seção descreve a arquitetura **pretendida** para o projeto completo,
> não o que já está implementado. Veja "Status atual" acima para saber o
> que já funciona.

O projeto terá 5 partes: (1) login/canais/persistência, (2) Pub/Sub via
broker, (3) relógios lógicos + heartbeat + Reference Service, (4) eleição
de coordenador + algoritmo de Berkeley, (5) replicação entre réplicas.

O contrato de mensagens comum entre Python e Java está documentado em
[`protocol/PROTOCOL.md`](protocol/PROTOCOL.md) e é atualizado conforme cada
parte é implementada.

## O que já está implementado (Parte 1)

- `python/server`: servidor ZeroMQ (`REP`) que trata `LOGIN_REQUEST`,
  `CHANNEL_CREATE_REQUEST` e `CHANNEL_LIST_REQUEST`, com persistência em
  disco (MessagePack) para logins e canais.
- `python/client`: bot ZeroMQ (`REQ`) que envia uma dessas requisições por
  execução, escolhida via variável `ACTION`.
- Nome de canal duplicado é rejeitado com erro.
- Sem implementação Java ainda.

## Estrutura de diretórios

```
projeto/
├── .gitignore
├── .env.example
├── README.md
├── protocol/
│   └── PROTOCOL.md        # contrato comum de mensagens Python <-> Java
├── python/
│   ├── server/
│   │   ├── server.py
│   │   └── requirements.txt
│   └── client/
│       ├── client.py
│       └── requirements.txt
└── java/
    ├── server/             # ainda vazio — implementação futura
    └── client/             # ainda vazio — implementação futura
```

## Dependências (Python)

- Python 3.10+
- [pyzmq](https://pypi.org/project/pyzmq/) — bindings ZeroMQ
- [msgpack](https://pypi.org/project/msgpack/) — serialização binária

Instalação:

```bash
cd python/server && pip install -r requirements.txt
cd python/client && pip install -r requirements.txt
```

## Variáveis de ambiente

Veja [`.env.example`](.env.example) para a lista completa. Nenhuma delas é
obrigatória — todas têm valor padrão seguro no código.

| Variável | Usado por | Padrão | Descrição |
|---|---|---|---|
| `BOT_NAME` | client | `bot-python-1` | Nome do bot que faz login / cria canais |
| `SERVER_ADDRESS` | client | `tcp://localhost:5555` | Endereço do servidor |
| `ACTION` | client | `LOGIN` | Ação a executar: `LOGIN`, `CHANNEL_CREATE` ou `CHANNEL_LIST` |
| `CHANNEL_NAME` | client | `avisos-gerais` | Nome do canal, usado quando `ACTION=CHANNEL_CREATE` |
| `SERVER_BIND_ADDRESS` | server | `tcp://*:5555` | Endereço de bind do servidor |
| `LOGINS_PERSISTENCE_PATH` | server | `python/server/data/logins.msgpack` | Caminho do arquivo de persistência de logins |
| `CHANNELS_PERSISTENCE_PATH` | server | `python/server/data/channels.msgpack` | Caminho do arquivo de persistência de canais |

O projeto **não** usa `python-dotenv` — as variáveis são lidas diretamente
via `os.environ.get(...)`. Para usá-las, exporte-as no shell antes de rodar
(a sintaxe varia por sistema operacional — veja abaixo).

## Como testar: Python Client ↔ Python Server

**Terminal 1 — subir o servidor:**

```bash
cd python/server
python3 server.py
```

Deve aparecer: `[SERVER] Historico carregado: N login(s) e N canal(is) ...`

**Terminal 2 — rodar o client (bot) para cada ação:**

- **Linux / macOS (bash/zsh):**
  ```bash
  cd python/client
  BOT_NAME="dra-ana-vet" ACTION=LOGIN python3 client.py
  BOT_NAME="dra-ana-vet" ACTION=CHANNEL_CREATE CHANNEL_NAME="vacinas" python3 client.py
  ACTION=CHANNEL_LIST python3 client.py
  ```

- **Windows — PowerShell:**
  ```powershell
  cd python\client
  $env:BOT_NAME="dra-ana-vet"; $env:ACTION="LOGIN"; python client.py
  $env:ACTION="CHANNEL_CREATE"; $env:CHANNEL_NAME="vacinas"; python client.py
  $env:ACTION="CHANNEL_LIST"; python client.py
  ```

  ⚠️ Lembre-se: `set VAR=valor` (sintaxe do CMD) não funciona no PowerShell
  — use sempre `$env:VAR="valor"`.

Saída esperada de `ACTION=CHANNEL_LIST`:

```
[CLIENT] Canais existentes (1): ['vacinas']
```

## Docker

O projeto **exige** Docker/Podman + Docker Compose para a execução final
(conforme o enunciado), mas isso ainda não foi implementado — o passo atual
roda apenas localmente, sem containers, para simplificar o desenvolvimento
incremental. `Dockerfile`s e `docker-compose.yml` serão adicionados quando
o projeto atingir esse ponto do roteiro.

## Próximos passos

1. Implementação Java equivalente (server + client): login, canais, persistência.
2. Teste de interoperabilidade Python ↔ Java.
3. Dockerização (Parte 1 completa).
4. Parte 2 (Pub/Sub + broker).