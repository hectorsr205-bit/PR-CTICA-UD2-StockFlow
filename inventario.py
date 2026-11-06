import threading
import time
from datos import STOCK_INICIAL, PEDIDOS, NUM_CAJAS, NUM_TERMINALES, REPOSICIONES, NUM_REVISORES
print_lock = threading.Lock()
terminal_semaphore = threading.Semaphore(NUM_TERMINALES)
class Inventario:
    def __init__(self, stock_base):
        self.stock = dict(stock_base)
        self.lock = threading.RLock()
        self.condition = threading.Condition(self.lock)
    def _actualizar_stock(self, producto, unidades):
        with self.lock:
            self.stock[producto] = self.stock.get(producto, 0) - unidades
    def procesar_pedido(self, id_caja, num_pedido, producto, unidades):
        with self.condition:
            while self.stock.get(producto, 0) < unidades:
                self.condition.wait()
            self._actualizar_stock(producto, unidades)
        with terminal_semaphore:
            time.sleep(0.0002)
            with print_lock:
                print(f"[Caja {id_caja} exito ({num_pedido}): vendidos {unidades}x '{producto}' | quedan: {self.stock[producto]}]")
        return True
    def reponer_stock(self, producto, unidades):
        with self.condition:
            self.stock[producto] = self.stock.get(producto, 0) + unidades
            self.condition.notify_all()
    def mostrar_inventario(self):
        print("\n------ Inventario Final (Prevencion de Deadlock) ------")
        for producto, cantidad in self.stock.items():
            print(f" {producto.capitalize()}: {cantidad} unidades")
        print("-" * 52)
def tarea_caja(id_caja, sublista_pedidos, inventario_obj):
    for num_pedido, producto, unidades in sublista_pedidos:
        inventario_obj.procesar_pedido(id_caja, num_pedido, producto, unidades)
def tarea_almacen(reposiciones_lote, inventario_obj):
    for producto, unidades in reposiciones_lote:
        time.sleep(0.0005)
        inventario_obj.reponer_stock(producto, unidades)
def tarea_revisor(id_revisor, productos_asignados, inventario_obj, barrera):
    time.sleep(0.001)
    with inventario_obj.lock:
        for p in productos_asignados:
            cant = inventario_obj.stock.get(p, 0)
            with print_lock:
                print(f"[Revisor {id_revisor}] Producto '{p}': {cant} unidades verificadas.")
    barrera.wait()
def main():
    print("==================================================")
    print(" FASE 7: PREVENCION DE DEADLOCK                   ")
    print("==================================================")
    print(f"Numero de cajas (hilos): {NUM_CAJAS}")
    print(f"Terminales de cobro simultaneos: {NUM_TERMINALES}")
    print(f"Numero de revisores: {NUM_REVISORES}")
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
    barrera = threading.Barrier(NUM_REVISORES + 1)
    productos_lista = list(STOCK_INICIAL.keys())
    hilos_revisores = []
    for i in range(NUM_REVISORES):
        id_rev = i + 1
        sub_productos = productos_lista[i::NUM_REVISORES]
        hilo_rev = threading.Thread(
            target=tarea_revisor,
            args=(id_rev, sub_productos, mi_inventario, barrera)
        )
        hilos_revisores.append(hilo_rev)
    inicio_tiempo = time.time()
    hilo_almacen.start()
    for hilo in hilos_cajas:
        hilo.start()
    for hilo in hilos_revisores:
        hilo.start()
    hilo_almacen.join()
    for hilo in hilos_cajas:
        hilo.join()
    barrera.wait()
    fin_tiempo = time.time()
    print("-" * 50)
    print(f"Simulacion finalizada en {fin_tiempo - inicio_tiempo:.4f} segundos.")
    mi_inventario.mostrar_inventario()
if __name__ == "__main__":
    main()