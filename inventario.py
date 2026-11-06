import threading
import time
from datos import STOCK_INICIAL, PEDIDOS, NUM_CAJAS, NUM_TERMINALES, REPOSICIONES
print_lock = threading.Lock()
terminal_semaphore = threading.Semaphore(NUM_TERMINALES)
class Inventario:
    def __init__(self, stock_base):
        self.stock = dict(stock_base)
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
    def procesar_pedido(self, id_caja, num_pedido, producto, unidades):
        with self.condition:
            while self.stock.get(producto, 0) < unidades:
                with print_lock:
                    print(f"[Caja {id_caja}] ⏳ Esperando stock para {unidades}x '{producto}' (Pedido {num_pedido})...")
                self.condition.wait()
            self.stock[producto] -= unidades
        with terminal_semaphore:
            time.sleep(0.0002)
            with print_lock:
                print(f"[Caja {id_caja} Éxito ({num_pedido}): Vendidos {unidades}x '{producto}' | Quedan: {self.stock[producto]}]")
        return True
    def reponer_stock(self, producto, unidades):
        with self.condition:
            self.stock[producto] = self.stock.get(producto, 0) + unidades
            with print_lock:
                print(f"[ALMACÉN] 📦 Reposición: +{unidades}x '{producto}' | Stock actual: {self.stock[producto]}")
            self.condition.notify_all()
    def mostrar_inventario(self):
        print("\n------ Inventario Final (Con Condition y Reposición) ------")
        for producto, cantidad in self.stock.items():
            print(f" {producto.capitalize()}: {cantidad} unidades")
        print("-" * 58)
def tarea_caja(id_caja, sublista_pedidos, inventario_obj):
    for num_pedido, producto, unidades in sublista_pedidos:
        inventario_obj.procesar_pedido(id_caja, num_pedido, producto, unidades)
def tarea_almacen(reposiciones_lote, inventario_obj):
    for producto, unidades in reposiciones_lote:
        time.sleep(0.0005)
        inventario_obj.reponer_stock(producto, unidades)
def main():
    print("==================================================")
    print(" FASE 4: REPOSICIÓN CON CONDITION                 ")
    print("==================================================")
    print(f"Número de cajas (hilos): {NUM_CAJAS}")
    print(f"Terminales de cobro simultáneos: {NUM_TERMINALES}")
    print(f"Total de pedidos a procesar: {len(PEDIDOS)}")
    print(f"Total de reposiciones: {len(REPOSICIONES)}")
    print("-" * 50)
    mi_inventario = Inventario(STOCK_INICIAL)
    lotes_pedidos = [[] for _ in range(NUM_CAJAS)]
    for i, pedido in enumerate(PEDIDOS):
        lotes_pedidos[i % NUM_CAJAS].append(pedido)
    hilos_cajas = []
    for i in range(NUM_CAJAS):
        id_cajas = i + 1
        hilo = threading.Thread(
            target=tarea_caja,
            args=(id_cajas, lotes_pedidos[i], mi_inventario)
        )
        hilos_cajas.append(hilo)
    hilo_almacen = threading.Thread(
        target=tarea_almacen,
        args=(REPOSICIONES, mi_inventario)
    )
    inicio_tiempo = time.time()
    hilo_almacen.start()
    for hilo in hilos_cajas:
        hilo.start()
    hilo_almacen.join()
    for hilo in hilos_cajas:
        hilo.join()
    fin_tiempo = time.time()
    print("-" * 50)
    print(f"Simulación finalizada en {fin_tiempo - inicio_tiempo:.4f} segundos.")
    mi_inventario.mostrar_inventario()
if __name__ == "__main__":
    main()