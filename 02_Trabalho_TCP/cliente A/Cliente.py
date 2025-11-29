import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Protocolo import *

import socket
from threading import Thread,Lock
import re
import time
import select
import struct
import os
import hashlib


class Client():
    def __init__(self):
        self.lock = Lock()
        self.thread_input = None
        self.thread_action = None
        self.host = None
        self.porta = None
        self.socket = None
        self.running = True
        self.first_config_complete = False
        self.receiving_file = False
        pass
    
    def run(self):
        

        print(f"=====================================\n"
              f"======== Sistema Cliente TCP ========\n"
              f"=====================================\n")
        self.print("Bem vindo cliente !.")
        try:
            while (self.running):
                while(not self.first_config_complete and self.running):
                    if self.porta is None :
                        entrada = input(f"[{IDENTIFIERS.CLIENTE.value}] Digite a porta do servidor.\n[{IDENTIFIERS.CLIENTE.value}] Pressione [return/enter] para porta padrão [{PORTA_SERVIDOR}].\n[{IDENTIFIERS.CLIENTE.value}] >> ")
                        if entrada == "sair":
                            self.ActionExit()
                            return
                        if entrada == "" :
                            self.print(f"Porta padrao setada : [{PORTA_SERVIDOR}]")
                            self.porta = PORTA_SERVIDOR
                        else:
                            try :
                                self.porta = int(entrada)
                            except ValueError:
                                self.print("Por favor, insira um número válido para a porta.")
                                self.porta = None
                                continue

                    if self.host is None :
                        entrada = input(f"[{IDENTIFIERS.CLIENTE.value}] Digite o host/IP do servidor.\n[{IDENTIFIERS.CLIENTE.value}] Pressione [return/enter] para padrão [{HOST_PADRAO}].\n[{IDENTIFIERS.CLIENTE.value}] >> ")
                        if entrada == "sair":
                            self.ActionExit()
                            return
                        if entrada == "" :
                            self.print(f"Host padrao setada : [{HOST_PADRAO}]")
                            self.host = HOST_PADRAO
                        else:
                            self.host = entrada
                            
                    if self.host and self.porta :
                        try :
                            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            self.socket.connect((self.host,self.porta))
                            self.print(f"Conectado ao servidor {self.host}:{self.porta}")
                            self.first_config_complete = True
                        except Exception as e:
                            self.host = None
                            self.porta = None
                            self.print(f"Erro ao conectar ao servidor: {e}\n")
                            time.sleep(2)
                            self.print("Tentando novamente...")

                self.print("Digite 'ajuda' para ver os comandos.")
                self.thread_input = Thread(target=self.inputThread,
                                   args=(),
                                   name="Cluente Imput Thread")
                self.thread_input.start()
                self.first_config_complete = True
                while (self.running and self.first_config_complete):
                    ready_sockets, _, _ = select.select([self.socket], [], [], 0.001)

                    if ready_sockets:
                        try :
                            msg_bytes = self.socket.recv(BUFFER_SIZE)

                            if msg_bytes:  # b'' = cliente desconectou
                                mensagem = msg_bytes.decode(ENCODER_FORMACT) 
                                self.print(f"{CLIENT_STATUS.RECEIVED_MENSAGE.value} {mensagem}")
                                if mensagem == MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_EXIST_ARCHIVE.value:
                                    self.receiving_file = True
                                    if self.ReceberArquivo():
                                        self.print("Arquivo recebido com sucesso.")
                                    self.receiving_file = False
                            else:
                                self.print(CLIENT_STATUS.DISCONNECTED.value)
                                self.first_config_complete = False
                                self.socket.close()
                        except :
                            continue
        
        except ConnectionRefusedError:
            self.print("Erro: Não foi possível conectar ao servidor")
        except Exception as e:
            self.print(f"Erro: {e}")
        finally:
            self.running = False
            time.sleep(1)
            self.socket.close()
            self.ActionExit()
            self.print("Programa encerrado.")
            exit(0)

    def inputThread(self):
        comando = ""
        while(self.running):
            time.sleep(2)
            if comando != 'sair' and self.running and not self.receiving_file:
                comando = input(f"[{IDENTIFIERS.CLIENTE.value}] >> ")
                self.thread_action = Thread(target=self.ActionThread,
                                            args=(comando,),
                                            name="Cliente Thread Action")
                self.thread_action.start()
            elif self.receiving_file :
                self.print("Recebendo arquivo do servidor...")
                time.sleep(3)

    def ActionThread(self,mensagem: str):
        match = re.search(r'\[(.*?)\]', mensagem)
        msg = match.group(1) if match else ""
        palavras = mensagem.split()
        command = palavras[0].lower() if palavras else ""

        if MENSAGE_CLIENT.MENSAGE_CLIENT_EXIT.value == command :
            self.ActionExit()
            return
        elif MENSAGE_CLIENT.MENSAGE_CLIENT_MENSAGE.value == command or MENSAGE_CLIENT.MENSAGE_CLIENT_ARCHIVE.value == command :
            self.ActionSendMensage(f"{command} [{msg}]")
            return
        elif MENSAGE_CLIENT.MENSAGE_CLIENT_HELP.value == command :
            self.ActionHelp()
            return
        self.print(f"Comando não encontrado : {mensagem}")
        return
                    
    def ActionSendMensage(self,mensage : str):
        with self.lock :
            try :
                self.socket.send(mensage.encode(ENCODER_FORMACT))
                self.print(f"Mensagem enviada.")
            except Exception as e:
                self.print(f"Erro ao enviar mensagem: {e}")

    def ReceberArquivo(self, pasta_destino="./arquivos_recebidos", encoding='utf-8'):
        try:
            # Cria pasta se não existir
            os.makedirs(pasta_destino, exist_ok=True)
            
            tamanho_nome_bytes = self._receber_exato(2)
            tamanho_nome = struct.unpack('!H', tamanho_nome_bytes)[0]
            
            nome_bytes = self._receber_exato(tamanho_nome)
            nome = nome_bytes.decode(encoding)
            
            tamanho_hash_bytes = self._receber_exato(2)
            tamanho_hash = struct.unpack('!H', tamanho_hash_bytes)[0]
            
            hash_bytes = self._receber_exato(tamanho_hash)
            hash_servidor = hash_bytes.decode(encoding)
            
            tamanho_dados_bytes = self._receber_exato(8)
            tamanho_dados = struct.unpack('!Q', tamanho_dados_bytes)[0]
            
            dados = self._receber_exato(tamanho_dados)
            
            hash_calculado = hashlib.sha256(dados).hexdigest()
            
            if hash_calculado == hash_servidor:
                self.print(f"Hash verificado : {hash_calculado}")
            else:
                self.print(f"Hash inválido :")
                print(f"   Hash esperado:  {hash_servidor}")
                print(f"   Hash calculado: {hash_calculado}")
                return False
            
            caminho_completo = os.path.join(pasta_destino, f"cliente_{nome}")
            with open(caminho_completo, 'wb') as f:
                f.write(dados)
            
            self.print(f"Arquivo salvo: {caminho_completo} ({tamanho_dados} bytes)")
            return True
            
        except Exception as e:
            self.print(f"Erro ao receber arquivo: {e}")
            return False

    def _receber_exato(self, num_bytes):
        buffer = b''
        while len(buffer) < num_bytes:
            chunk = self.socket.recv(num_bytes - len(buffer))
            if not chunk:
                raise ConnectionError("Conexão fechada")
            buffer += chunk
        return buffer
    
    def ActionExit(self) :
        self.running = False

    def ActionHelp(self):
        self.print("Comandos disponíveis:\n"
                       "  ajuda                         - Mostra esta mensagem de ajuda.\n"
                       "  chat [sua mensagem]           - Envia uma mensagem de chat para o servidor.\n"
                       "  arquivo [caminho do arquivo]  - Envia um arquivo para o servidor.\n"
                       "  sair                          - Encerra o cliente.\n")
        return

    def print(self,msg : str):
        terminal(objeto=IDENTIFIERS.CLIENTE.value,id=None,mensagem=msg)

    def serverPrint(self,msg : str):
        terminal(objeto=IDENTIFIERS.SERVER.value,id=None,mensagem=msg)

if __name__ == "__main__":
    cliente = Client()
    cliente.run()