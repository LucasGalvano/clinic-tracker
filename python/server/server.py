"""
Python Server - Parte 1 (passo 1)
Sistema distribuido de mensagens - dominio: clinica veterinaria

Escopo DESTE passo (nao adiantar nada alem disto):
    - Socket ZeroMQ REP, conforme especificado no enunciado para a Parte 1.
    - Recebe LOGIN_REQUEST serializado em MessagePack.
    - Responde LOGIN_RESPONSE.
    - SEM persistencia ainda (sera adicionada no proximo passo).
    - SEM CHANNEL_CREATE / CHANNEL_LIST ainda.

Ver contrato completo em protocol/PROTOCOL.md.
"""

import os
import time

import msgpack
import zmq

BIND_ADDRESS = os.environ.get("SERVER_BIND_ADDRESS", "tcp://*:5555")


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

    # Nesta etapa so imprimimos o login. A persistencia entra no proximo passo.
    print(
        f"[LOGIN] bot='{bot_name}' lang={envelope.get('sender_lang')} "
        f"timestamp={envelope.get('timestamp')}"
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
