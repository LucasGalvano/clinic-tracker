"""
Python Client (bot) - Parte 1 (passo 1)

Escopo DESTE passo:
    - Socket ZeroMQ REQ, conforme especificado no enunciado.
    - Envia LOGIN_REQUEST serializado em MessagePack.
    - Exibe o LOGIN_RESPONSE recebido.

O client eh um bot: nao ha nenhuma interacao manual. Nome do bot e endereco
do servidor vem de variaveis de ambiente (facilita configurar via
Docker Compose futuramente, sem mudar o codigo).

Ver contrato completo em protocol/PROTOCOL.md.
"""

import os
import sys
import time

import msgpack
import zmq

SERVER_ADDRESS = os.environ.get("SERVER_ADDRESS", "tcp://localhost:5555")
BOT_NAME = os.environ.get("BOT_NAME", "bot-python-1")

# Timeout de recepcao: evita que o bot fique bloqueado para sempre caso o
# servidor nao responda. Importante porque o projeto nao pode depender de
# interacao manual (regra do enunciado) -- o bot precisa poder desistir
# sozinho e sinalizar erro via exit code.
RECV_TIMEOUT_MS = 5000


def build_envelope(msg_type: str, payload: dict) -> dict:
    return {
        "type": msg_type,
        "sender_id": BOT_NAME,
        "sender_lang": "python",
        "timestamp": int(time.time() * 1000),
        "payload": payload,
    }


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.RCVTIMEO, RECV_TIMEOUT_MS)
    socket.setsockopt(zmq.LINGER, 0)
    socket.connect(SERVER_ADDRESS)
    print(f"[CLIENT] '{BOT_NAME}' conectando em {SERVER_ADDRESS}")

    request = build_envelope("LOGIN_REQUEST", {"bot_name": BOT_NAME})
    socket.send(msgpack.packb(request, use_bin_type=True))
    print(f"[SEND] {request}")

    try:
        raw = socket.recv()
        response = msgpack.unpackb(raw, raw=False)
        print(f"[RECV] {response}")

        if response.get("payload", {}).get("status") == "OK":
            print(f"[CLIENT] Login realizado com sucesso: {BOT_NAME}")
        else:
            error = response.get("payload", {}).get("error_msg", "erro desconhecido")
            print(f"[CLIENT] Login falhou: {error}")
            sys.exit(1)
    except zmq.error.Again:
        print("[CLIENT] Timeout: servidor nao respondeu dentro do prazo")
        sys.exit(1)
    finally:
        socket.close()
        context.term()


if __name__ == "__main__":
    main()
