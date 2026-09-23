# vet_flow — Sistema Distribuído de Mensagens (Clínica Veterinária)

> **Status atual do projeto: Parte 1, em andamento.**
> Implementado até aqui: login de bots via `LOGIN_REQUEST`/`LOGIN_RESPONSE`,
> **sem persistência ainda**. Este README documenta apenas o que já existe —
> não descreve funcionalidades futuras como já implementadas.

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

## O que já está implementado (Parte 1, passo 1)

- `python/server`: servidor ZeroMQ (`REP`) que recebe `LOGIN_REQUEST` em
  MessagePack e responde `LOGIN_RESPONSE`.
- `python/client`: bot ZeroMQ (`REQ`) que envia `LOGIN_REQUEST` e exibe a
  resposta.
- Sem persistência em disco ainda.
- Sem criação/listagem de canais ainda.
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
| `BOT_NAME` | client | `bot-python-1` | Nome do bot que faz login |
| `SERVER_ADDRESS` | client | `tcp://localhost:5555` | Endereço do servidor |
| `SERVER_BIND_ADDRESS` | server | `tcp://*:5555` | Endereço de bind do servidor |

O projeto **não** usa `python-dotenv` — as variáveis são lidas diretamente
via `os.environ.get(...)`. Para usá-las, exporte-as no shell antes de rodar
(a sintaxe varia por sistema operacional — veja abaixo).

## Como testar: Python Client ↔ Python Server

**Terminal 1 — subir o servidor:**

```bash
cd python/server
python3 server.py
```

Deve aparecer: `[SERVER] Python Server (REP) ouvindo em tcp://*:5555`

**Terminal 2 — rodar o client (bot):**

A forma de definir a variável de ambiente `BOT_NAME` antes de rodar o
script muda conforme o terminal usado:

- **Linux / macOS (bash/zsh):**
  ```bash
  cd python/client
  BOT_NAME="dra-ana-vet" python3 client.py
  ```

- **Windows — CMD (`cmd.exe`):**
  ```cmd
  cd python\client
  set BOT_NAME=dra-ana-vet
  python client.py
  ```

- **Windows — PowerShell:**
  ```powershell
  cd python\client
  $env:BOT_NAME="dra-ana-vet"
  python client.py
  ```

  ⚠️ **Atenção no PowerShell:** o comando `set BOT_NAME=dra-ana-vet` (sintaxe
  do CMD) **não funciona como esperado no PowerShell** — ele não gera erro,
  mas também não define a variável de ambiente para o processo filho, então
  o client roda com o valor padrão (`bot-python-1`) em vez do valor que
  você tentou definir. No PowerShell, use sempre `$env:NOME="valor"`.

Saída esperada no client (com `BOT_NAME=dra-ana-vet`):

```
[CLIENT] 'dra-ana-vet' conectando em tcp://localhost:5555
[SEND] {'type': 'LOGIN_REQUEST', ...}
[RECV] {'type': 'LOGIN_RESPONSE', ..., 'payload': {'status': 'OK'}}
[CLIENT] Login realizado com sucesso: dra-ana-vet
```

No terminal do servidor, deve aparecer uma linha `[LOGIN] bot='dra-ana-vet' ...`.

## Docker

O projeto **exige** Docker/Podman + Docker Compose para a execução final
(conforme o enunciado), mas isso ainda não foi implementado — o passo atual
roda apenas localmente, sem containers, para simplificar o desenvolvimento
incremental. `Dockerfile`s e `docker-compose.yml` serão adicionados quando
o projeto atingir esse ponto do roteiro.

## Próximos passos

1. Persistência (login + timestamp; canais) no `python/server`.
2. `CHANNEL_CREATE` / `CHANNEL_LIST`.
3. Implementação Java equivalente (server + client).
4. Teste de interoperabilidade Python ↔ Java.
5. Dockerização (Parte 1 completa).