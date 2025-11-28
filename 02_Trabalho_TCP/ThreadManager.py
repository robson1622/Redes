from queue import Queue
from threading import Thread,Lock
from socket import socket
from ServidorThread import ServidorThread
from Protocolo import MensageQueue
from Protocolo import terminal,IDENTIFIERS,MENSAGE_SERVER_TYPE

class ThreadManager:
    def __init__(self):
        # threads de atendimento ao cliente
        self.threads : list[Thread] = []
        # comunicação
        self.queues : list[Queue] = []
        self.client_addres = []
        self.counterThreads : int = 0
        self.lock = Lock()
    
    def listThreads(self) -> None:
        with self.lock :
            if len(self.threads) == 0 :
                terminal(IDENTIFIERS.SERVER.value,None,f"Nenhuma thread para mostrar.")
                return
            terminal(IDENTIFIERS.SERVER.value,None,f"Listando [{len(self.threads)}] threads :")
            for index in range(len(self.threads)):
                terminal(IDENTIFIERS.SERVER.value,int(self.threads[index].name),f"Cliente conectado : {self.client_addres[index]} ")

    def createThread(self,cliente_socket : socket) -> None:
        newQueue = Queue()
        newAddres = cliente_socket.getpeername()
        with self.lock:
            newThread = Thread(
                                target=ServidorThread,
                                args=(cliente_socket,newQueue,self.counterThreads,self.deleteThread,),
                                name=f"{self.counterThreads}"
                                )
        
            self.counterThreads += 1
            self.queues.append(newQueue)
            self.client_addres.append(newAddres)
            self.threads.append(newThread)
        newThread.start()
    # -1 apaga todos
    def deleteThread(self, thread_id: int) -> None:
        lista_ids = []
        with self.lock:
            qtd_threads = len(self.threads)
            if thread_id > qtd_threads:
                return
            if thread_id >= 0:
                for i in range(len(self.threads)):
                    if self.threads[i].name == f"{thread_id}":
                        lista_ids.append(i)
            else :
                for i in range(len(self.threads)):
                    lista_ids.append(i)
                
        for id in lista_ids :
            self.sendMensageToThread(id=id,type=MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_CLOSE_THREAD,msg="")
        with self.lock :
            for i in lista_ids :
                self.threads.pop(i)
                self.queues.pop(i)
                self.client_addres.pop(i)
                self.counterThreads -= 1
        if thread_id == -1 :
            terminal(objeto=IDENTIFIERS.SERVER.value,id=None,mensagem=f"todas as {qtd_threads} fechadas.")
        else :
            terminal(objeto=IDENTIFIERS.SERVER.value,id=None,mensagem=f"thread id [{thread_id}] fechada.")
            
                
    # id = -1 manda para todas.
    def sendMensageToThread(self,id : int,type : MENSAGE_SERVER_TYPE,msg : str) -> None:
        with self.lock :
            mensagem = MensageQueue(type = type,conteudo=msg)
            tam = len(self.queues)
                
            if id > tam:
                terminal(objeto=IDENTIFIERS.SERVER.value,id=None,mensagem=f"thead id {id} inexistente.")
                return
            if id < 0 :
                if tam > 0:
                    for q in self.queues :
                        q.put(mensagem)
                    terminal(objeto=IDENTIFIERS.SERVER.value,id=None,mensagem=f"Mensagem enviada para {tam} clientes.")
            else :
                for index in range(tam) :
                    if f"{id}" == self.threads[index].name :
                        q = self.queues[index]
                        q.put(mensagem)
                        terminal(objeto=IDENTIFIERS.SERVER.value,id=None,mensagem=f"Mensagem enviada para o cliente {index}.")
                        return
