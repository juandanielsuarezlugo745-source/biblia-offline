import flet as ft
import json
import os
import unicodedata
import sys

# --- FUNCIÓN DE NORMALIZACIÓN (Para que "Génesis" se encuentre como "genesis") ---
def normalizar(texto):
    if not texto: return ""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.lower())
        if unicodedata.category(c) != 'Mn'
    )

def main(page: ft.Page):
    # --- CONFIGURACIÓN DE PÁGINA Y MARGEN SUPERIOR (Patch 50px) ---
    page.title = "Biblia Reina Valera Offline"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = ft.padding.only(top=50, left=10, right=10, bottom=10)
    
    state = {"datos": [], "datos_norm": []}

    # --- FUNCIÓN "LLAVE MAESTRA" PARA CARGAR EL JSON ---
    def cargar_datos():
        # Buscamos en todas las rutas posibles donde Android guarda los assets
        posibilidades = [
            "assets/Biblia.json",
            "assets/biblia.json",
            "Biblia.json",
            "biblia.json",
            os.path.join(getattr(sys, '_MEIPASS', ''), "assets", "Biblia.json")
        ]
        
        for ruta in posibilidades:
            if os.path.exists(ruta):
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        d = json.load(f)
                        # Creamos una lista normalizada para búsquedas rápidas
                        state["datos_norm"] = [normalizar(v["Text"]) for v in d]
                        return d
                except Exception:
                    continue
        return None

    state["datos"] = cargar_datos()

    # --- INTERFAZ DE USUARIO ---
    lista_resultados = ft.ListView(expand=True, spacing=10)
    input_busqueda = ft.TextField(
        label="Escribe libro, capítulo o palabra...",
        on_submit=lambda e: buscar(e.control.value),
        prefix_icon=ft.icons.SEARCH
    )

    def buscar(query):
        lista_resultados.controls.clear()
        if not state["datos"] or not query:
            lista_resultados.controls.append(ft.Text("Escribe algo para buscar..."))
            page.update()
            return

        query_norm = normalizar(query)
        encontrados = 0
        
        for i, texto_n in enumerate(state["datos_norm"]):
            if query_norm in texto_n:
                v = state["datos"][i]
                lista_resultados.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Column([
                                ft.Text(f"{v['Book']} {v['Chapter']}:{v['Verse']}", 
                                        weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
                                ft.Text(v['Text'], size=16)
                            ])
                        )
                    )
                )
                encontrados += 1
                if encontrados >= 50: break # Límite para que no se pegue el celular

        if encontrados == 0:
            lista_resultados.controls.append(ft.Text("No se encontraron resultados."))
        
        page.update()

    # --- VALIDACIÓN INICIAL ---
    if state["datos"] is None:
        page.add(ft.Text("⚠️ ERROR: No se encontró el archivo Biblia.json.\nVerifica que esté en la carpeta /assets", 
                         color=ft.colors.RED, size=20))
    else:
        page.add(
            ft.Text("Biblia Reina Valera 1960", size=24, weight=ft.FontWeight.BOLD),
            input_busqueda,
            ft.Divider(),
            lista_resultados
        )

ft.app(target=main)
