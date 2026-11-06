import threading
import time
from datos import STOCK_INICIAL, PEDIDOS, NUM_CAJAS, NUM_TERMINALES
print_lock = threading.Lock()
terminal_semaphore = threading.Semaphore(NUM_TERMINALES)
class Inventario:
    def __init__(self, stock_base):
        self.stock = dict(stock_base)
        self.lock = threading.Lock()
    def procesar_pedido(self, id_caja, num_pedido, producto, unidades):
        with terminal_semaphore:
            with print_lock:
                print(f"[Caja {id_caja}] ➜ Terminal de cobro adquirido para pedido {num_pedido}")
            time.sleep(0.0002)
            with self.lock:
                stock_actual = self.stock.get(producto, 0)
                if stock_actual >= unidades:
                    self.stock[producto] = stock_actual - unidades
                    exito = True
                else:
                    exito = False
            with print_lock:
                print(f"[Caja {id_caja}] ⬅ Terminal de cobro liberado")
        if exito:
            with print_lock:
                print(f"[Caja {id_caja} Éxito ({num_pedido}): Vendidos {unidades}x '{producto}' | Quedan: {self.stock[producto]}]")
            return True
        else:
            with print_lock:
                print(f"[Caja {id_caja} Fallido ({num_pedido}): Stock insuficiente para {unidades}x '{producto}' (Quedaban {stock_actual})]")
            return False
    def mostrar_inventario(self):
        print("\n------ Inventario Final (Con Semaphore y Lock) ------")
        for producto, cantidad in self.stock.items():
            print(f" {producto.capitalize()}: {cantidad} unidades")
        print("-" * 52)
def tarea_caja(id_caja, sublista_pedidos, inventario_obj):
    for num_pedido, producto, unidades in sublista_pedidos:
        inventario_obj.procesar_pedido(id_caja, num_pedido, producto, unidades)
def main():
    print("==================================================")
    print(" FASE 3: TERMINALES LIMITADOS CON SEMAPHORE       ")
    print("==================================================")
    print(f"Número de cajas (hilos): {NUM_CAJAS}")
    print(f"Terminales de cobro simultáneos: {NUM_TERMINALES}")
    print(f"Total de pedidos a procesar: {len(PEDIDOS)}")
    print("-" * 50)
    mi_inventario = Inventario(STOCK_INICIAL)
    lotes_pedidos = [[] for _ in range(NUM_CAJAS)]
    for i, pedido in enumerate(PEDIDOS):
        lotes_pedidos[i % NUM_CAJAS].append(pedido)
    hilos = []
    for i in range(NUM_CAJAS):
        id_cajas = i + 1
        hilo = threading.Thread(
            target=tarea_caja,
            args=(id_cajas, lotes_pedidos[i], mi_inventario)
        )
        hilos.append(hilo)
    inicio_tiempo = time.time()
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()
    fin_tiempo = time.time()
    print("-" * 50)
    print(f"Simulación finalizada en {fin_tiempo - inicio_tiempo:.4f} segundos.")
    mi_inventario.mostrar_inventario()
if __name__ == "__main__":
    main()