from Protocolo import *
from queue import Queue,Empty
import socket
import select
import os
import struct
import time
import hashlib


ECHO_MODE = False

def ServidorThread(thread_socket : socket,queue : Queue,thread_id : int,callback):
    THREAD_STATUS.CONNECTED(thread_id)
    msg = ""
    resposta = ""
    esperando = True
    encerrar = False
    try:
        while ( not encerrar ):
            if esperando:
                THREAD_STATUS.WAITING_MENSAGE(thread_id)
                esperando = False

            ready_sockets, _, _ = select.select([thread_socket], [], [], 0.001)

            if ready_sockets:
                try :
                    msg_bytes = thread_socket.recv(BUFFER_SIZE)

                    if not msg_bytes:  # b'' = cliente desconectou
                        THREAD_STATUS.CLIENT_DISCONNECTED(thread_id)
                        encerrar = True
                        break
                    else :
                        msg = msg_bytes.decode(ENCODER_FORMACT)
                        resposta = PegarResposta(msg)
                        if resposta == None :
                            THREAD_STATUS.SENDING_RESPONSE(thread_id, MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_NO_EXIST_ARCHIVE.value)
                            thread_socket.send(MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_NO_EXIST_ARCHIVE.value.encode(ENCODER_FORMACT))
                        elif resposta == MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_MENSAGE_RECEIVED.value:
                            THREAD_STATUS.SENDING_RESPONSE(thread_id, MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_MENSAGE_RECEIVED.value)
                            thread_socket.send(MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_MENSAGE_RECEIVED.value.encode(ENCODER_FORMACT))
                        else :
                            if isinstance(resposta, tuple):
                                nome, _ , _ = resposta
                                THREAD_STATUS.SENDING_FILE(thread_id, nome)
                                EnviarResposta(thread_socket, resposta, ENCODER_FORMACT)

                    if ECHO_MODE:
                        THREAD_STATUS.RECEIVED_MENSAGE(thread_id, msg)
                    terminal(objeto=f"{IDENTIFIERS.SERVER.value}",id=None,mensagem=f"{MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_MENSAGE_RECEIVED.value} {msg}")
                    
                except Exception as e:
                    terminal(objeto=f"{IDENTIFIERS.SERVER.value}",id=None,mensagem=f"Erro : {e} - mensagem: {msg}")

            try:
                queue_msg : MensageQueue = queue.get(block=True, timeout=0.001)
                if queue_msg.type == MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_CLOSE_THREAD:
                    THREAD_STATUS.DISCONNECTING(thread_id, "Comando do servidor")
                    esperando = False
                    break
                elif queue_msg.type == MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_SEND_MENSAGE_CLIENT:
                    THREAD_STATUS.SENDING_MENSAGE(thread_id,f" para : {thread_socket.getpeername()}")
                    thread_socket.send(queue_msg.conteudo.encode(ENCODER_FORMACT))
            except Empty :
                
                pass
            
            
    finally :
        thread_socket.close()
        THREAD_STATUS.CLOSED(thread_id)
        callback(thread_id)

def PegarResposta(comando: str):
    comando = comando.strip()
    if not comando or ' ' not in comando:
        return ""
    
    tipo, conteudo = comando.split(' ', 1)
    tipo = tipo.lower()
    conteudo = conteudo.strip()
    if len(conteudo) > 2:
        conteudo = conteudo[1:-1]
    else :
        return ""
    
    if tipo == "chat":
        return MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_MENSAGE_RECEIVED.value
    
    if tipo == "arquivo":
        caminho = os.path.join(conteudo)
        
        if not os.path.exists(caminho) or not os.path.isfile(caminho):
            return None
        
        with open(caminho, 'rb') as f:
            dados = f.read()
        
        hash_arquivo = hashlib.sha256(dados).hexdigest()
        
        nome = os.path.basename(conteudo)
        return (nome, dados, hash_arquivo)  
    
    return MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_NO_EXIST_ARCHIVE.value
# arquivo [virtualbox.dmg]
def EnviarResposta(socket, resposta, encoding='utf-8'):
    time.sleep(0.1)
    socket.send(MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_EXIST_ARCHIVE.value.encode(encoding))
    
    if isinstance(resposta, str):
        socket.send(resposta.encode(encoding))
        return
    
    if isinstance(resposta, tuple):
        nome, dados, hash_sha = resposta  
        nome_bytes = nome.encode(encoding)
        hash_bytes = hash_sha.encode(encoding)
        # TAMANHO_NOME (2 bytes) + NOME + TAMANHO_HASH (2 bytes) + HASH + TAMANHO_DADOS (8 bytes) + DADOS
        pacote = (
            struct.pack('!H', len(nome_bytes)) +    # 2 bytes: tamanho do nome
            nome_bytes +                            # nome do arquivo
            struct.pack('!H', len(hash_bytes)) +    # 2 bytes: tamanho do hash
            hash_bytes +                            # hash SHA-256
            struct.pack('!Q', len(dados)) +         # 8 bytes: tamanho dos dados
            dados                                   # dados do arquivo
        )
        socket.sendall(pacote)