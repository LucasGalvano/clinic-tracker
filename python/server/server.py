"""
Python Server - Parte 1 (passo 2)
Sistema distribuido de mensagens - dominio: clinica veterinaria

Escopo DESTE passo (nao adiantar nada alem disto):
    - Socket ZeroMQ REP, conforme especificado no enunciado para a Parte 1.
    - Recebe LOGIN_REQUEST serializado em MessagePack.
    - Responde LOGIN_RESPONSE.
    - Persiste cada login bem-sucedido (bot_name + timestamp) em disco
      via persistence.py, e carrega o historico existente ao iniciar.
    - SEM CHANNEL_CREATE / CHANNEL_LIST ainda.

Ver contrato completo em protocol/PROTOCOL.md.
"""

import os
import time

import msgpack
import zmq

import persistence

BIND_ADDRESS = os.environ.get("SERVER_BIND_ADDRESS", "tcp://*:5555")

# Permite sobrescrever o caminho do arquivo de persistencia (util para
# testes isolados e, futuramente, para apontar para um volume montado
# no Docker Compose).
LOGINS_PATH = os.environ.get(
    "LOGINS_PERSISTENCE_PATH", persistence.DEFAULT_LOGINS_PATH
)

# Estado em memoria, carregado do disco ao iniciar. Mantido como lista
# simples porque o loop principal (main) processa uma requisicao REP
# por vez, sequencialmente -- nao ha concorrencia entre requisicoes
# neste processo, entao uma lista global sem lock e segura aqui.
known_logins = []


def build_envelope(msg_type: str, payload: dict) -> dict:
    """Monta um envelope no formato do protocolo comum (ver PROTOCOL.md)."""
    return {
        "type": msg_type,
        "sender_id": "python-server",
        "sender_lang": "python",
        "timestamp": int(time.time() * 1000),  # epoch millis, UTC
        "payload": payload,
    }


def handle_login_request(envelope: dict) -> dict:
    """Trata LOGIN_REQUEST e devolve o envelope de LOGIN_RESPONSE."""
    bot_name = envelope.get("payload", {}).get("bot_name")

    if not bot_name:
        return build_envelope(
            "LOGIN_RESPONSE",
            {"status": "ERROR", "error_msg": "campo 'bot_name' ausente ou vazio"},
        )

    record = {
        "bot_name": bot_name,
        "sender_lang": envelope.get("sender_lang"),
        "timestamp": envelope.get("timestamp"),
    }

    global known_logins
    known_logins = persistence.append_login(record, LOGINS_PATH)

    print(
        f"[LOGIN] bot='{bot_name}' lang={envelope.get('sender_lang')} "
        f"timestamp={envelope.get('timestamp')} "
        f"(total de logins persistidos: {len(known_logins)})"
    )

    return build_envelope("LOGIN_RESPONSE", {"status": "OK"})


def dispatch(envelope: dict) -> dict:
    """Roteia o envelope recebido para o handler correto pelo campo 'type'."""
    msg_type = envelope.get("type")

    if msg_type == "LOGIN_REQUEST":
        return handle_login_request(envelope)

    # Tipo desconhecido nao deve derrubar o servidor (REP exige sempre 1
    # send() por recv(), senao o socket trava em estado inconsistente).
    return build_envelope(
        "LOGIN_RESPONSE",
        {"status": "ERROR", "error_msg": f"tipo de mensagem desconhecido: {msg_type}"},
    )


def main():
    global known_logins
    known_logins = persistence.load_logins(LOGINS_PATH)
    print(
        f"[SERVER] Historico carregado: {len(known_logins)} login(s) "
        f"previamente persistido(s) em '{LOGINS_PATH}'"
    )

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(BIND_ADDRESS)
    print(f"[SERVER] Python Server (REP) ouvindo em {BIND_ADDRESS}")

    try:
        while True:
            raw = socket.recv()
            envelope = msgpack.unpackb(raw, raw=False)
            print(f"[RECV] {envelope}")

            response = dispatch(envelope)

            socket.send(msgpack.packb(response, use_bin_type=True))
            print(f"[SEND] {response}")
    except KeyboardInterrupt:
        print("\n[SERVER] Encerrando...")
    finally:
        socket.close()
        context.term()


if __name__ == "__main__":
    main()