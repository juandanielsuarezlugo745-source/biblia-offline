import flet as ft
import json
import os
import sys
import unicodedata

# --- FUNCIÓN PARA QUITAR TILDES (Para que el buscador sea inteligente) ---
def normalizar(texto):
    if not texto: return ""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.lower())
        if unicodedata.category(c) != 'Mn'
    )

def main(page: ft.Page):
    # Configuración de la página (Margen de 50px arriba)
    page.title = "Biblia Reina Valera"
    page.padding = ft.padding.only(top=50, left=15, right=15, bottom=20)
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Estado de la App
    state = {"datos": [], "datos_norm": []}

    # --- CARGAR LA BIBLIA ---
    def cargar_datos():
        rutas = [
            "assets/Biblia.json",
            os.path.join(getattr(sys, '_MEIPASS', ''), "assets", "Biblia.json"),
            "Biblia.json"
        ]
        for ruta in rutas:
            if os.path.exists(ruta):
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        d = json.load(f)
                        # Pre-normalizamos para que la búsqueda sea instantánea
                        state["datos_norm"] = [normalizar(v["Text"]) for v in d]
                        return d
                except: continue
        return None

    state["datos"] = cargar_datos()

    # --- INTERFAZ ---
    lista_resultados = ft.ListView(expand=True, spacing=10)
    
    def realizar_busqueda(e):
        query = normalizar(e.control.value)
        lista_resultados.controls.clear()
        
        if len(query) < 3: # No busca hasta que escribas 3 letras
            page.update()
            return

        encontrados = 0
        for i, texto_n in enumerate(state["datos_norm"]):
            if query in texto_n:
                v = state["datos"][i]
                lista_resultados.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Column([
                                ft.Text(f"{v['Book']} {v['Chapter']}:{v['Verse']}", 
                                        weight="bold", color="blue"),
                                ft.Text(v['Text'], size=16)
                            ])
                        )
                    )
                )
                encontrados += 1
                if encontrados >= 50: break # Límite para velocidad
        
        page.update()

    input_busqueda = ft.TextField(
        label="Escribe libro o palabra (ej: Juan 3 o fe)...",
        on_change=realizar_busqueda, # Busca mientras escribes
        prefix_icon=ft.icons.SEARCH,
        border_radius=10
    )

    # --- LÓGICA DE INICIO ---
    if state["datos"] is None:
        page.add(ft.Text("⚠️ Archivo Biblia.json no encontrado", color="red", size=20))
    else:
        page.add(
            ft.Text("Biblia Reina Valera 1960", size=28, weight="bold"),
            input_busqueda,
            ft.Divider(),
            lista_resultados
        )

ft.app(target=main)
