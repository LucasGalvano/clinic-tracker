"""
Persistencia simples para o Python Server - Parte 1 (passo 2)

Escopo DESTE passo: persistir apenas LOGINS (bot_name + timestamp).
CHANNEL_CREATE / CHANNEL_LIST ainda nao existem, portanto nao ha
persistencia de canais aqui ainda.

Formato escolhido (ver decisao registrada no historico do projeto):
    Um unico arquivo MessagePack contendo uma LISTA de registros de login.
    A cada novo login bem-sucedido: le a lista inteira, adiciona o
    registro, regrava o arquivo inteiro.

    Isso e intencionalmente simples. Nao ha banco de dados, nao ha
    escrita incremental/append-only. Para o volume de um projeto
    academico isso e adequado; nao e otimizado para grande volume de
    escritas (cada escrita reescreve o arquivo inteiro).

Concorrencia: este modulo assume um UNICO processo, single-threaded,
processando uma requisicao REP por vez (e assim que o server.py atual
funciona). Se o server for alterado para processar requisicoes em
paralelo (ex.: multithreading), este modulo precisara de um lock de
arquivo — isso NAO esta implementado aqui porque nao e o caso atual.
"""

import os

import msgpack

DEFAULT_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DEFAULT_LOGINS_PATH = os.path.join(DEFAULT_DATA_DIR, "logins.msgpack")


def _ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def load_logins(path: str = DEFAULT_LOGINS_PATH) -> list:
    """Carrega a lista de logins persistidos.

    Retorna [] se o arquivo ainda nao existe (primeira execucao do
    servidor) ou estiver vazio/corrompido -- nesse caso o servidor deve
    poder subir normalmente, apenas com historico vazio, em vez de
    falhar ao iniciar.
    """
    if not os.path.exists(path):
        return []

    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError:
        return []

    if not raw:
        return []

    try:
        data = msgpack.unpackb(raw, raw=False)
    except (msgpack.exceptions.UnpackException, ValueError):
        # Arquivo corrompido/truncado: nao derruba o servidor, apenas
        # comeca com historico vazio. Isso e uma decisao conservadora
        # para nao bloquear a demonstracao por causa de um arquivo ruim.
        return []

    return data if isinstance(data, list) else []


def save_logins(logins: list, path: str = DEFAULT_LOGINS_PATH) -> None:
    """Regrava o arquivo inteiro com a lista atual de logins."""
    _ensure_parent_dir(path)
    packed = msgpack.packb(logins, use_bin_type=True)
    with open(path, "wb") as f:
        f.write(packed)


def append_login(record: dict, path: str = DEFAULT_LOGINS_PATH) -> list:
    """Adiciona um registro de login e persiste a lista atualizada.

    Retorna a lista completa e atualizada, para o chamador manter em
    memoria sem precisar reler o arquivo em seguida.
    """
    logins = load_logins(path)
    logins.append(record)
    save_logins(logins, path)
    return logins