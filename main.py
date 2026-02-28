import flet as ft
import json
import os

def main(page: ft.Page):
    # Configuración de la pantalla
    page.title = "Biblia RVR1960 Offline"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0E1117"
    page.padding = 15
    
    # --- 1. CARGA DE DATOS ---
    # Usamos un nombre corto para evitar errores en la "cocina" de GitHub
    nombre_archivo = "Biblia.json"
    ruta_biblia = os.path.join(os.path.dirname(__file__), "assets", nombre_archivo)
    
    try:
        with open(ruta_biblia, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except Exception as e:
        page.add(ft.Text(f"Error: No se encontró '{nombre_archivo}' en la carpeta 'assets'.\nDetalle: {e}", color="red"))
        return

    # --- 2. ESTRUCTURA DE LA BIBLIA ---
    libros_biblia = [libro["name"] for libro in datos["books"]]
    
    # Estado de la aplicación
    state = {
        "libro_idx": 0,
        "capitulo_idx": 0
    }

    # --- 3. FUNCIONES DE NAVEGACIÓN ---
    def cargar_texto():
        libro = datos["books"][state["libro_idx"]]
        capitulo = libro["chapters"][state["capitulo_idx"]]
        
        titulo_app.value = f"{libro['name']} {state['capitulo_idx'] + 1}"
        
        # Limpiar y cargar versículos
        columna_versos.controls.clear()
        for i, verso in enumerate(capitulo["verses"]):
            columna_versos.controls.append(
                ft.Text(
                    spans=[
                        ft.TextSpan(f"{i+1} ", style=ft.TextStyle(color="#FF9800", weight="bold")),
                        ft.TextSpan(verso)
                    ],
                    size=18,
                    selectable=True
                )
            )
        page.update()

    def siguiente_cap(e):
        libro_actual = datos["books"][state["libro_idx"]]
        if state["capitulo_idx"] < len(libro_actual["chapters"]) - 1:
            state["capitulo_idx"] += 1
        elif state["libro_idx"] < len(datos["books"]) - 1:
            state["libro_idx"] += 1
            state["capitulo_idx"] = 0
        cargar_texto()

    def anterior_cap(e):
        if state["capitulo_idx"] > 0:
            state["capitulo_idx"] -= 1
        elif state["libro_idx"] > 0:
            state["libro_idx"] -= 1
            libro_previo = datos["books"][state["libro_idx"]]
            state["capitulo_idx"] = len(libro_previo["chapters"]) - 1
        cargar_texto()

    # --- 4. INTERFAZ DE USUARIO ---
    titulo_app = ft.Text("Biblia", size=22, weight="bold", color="#FF9800")
    columna_versos = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)

    # Botones de navegación
    btn_ant = ft.IconButton(ft.icons.ARROW_BACK_IOS, on_click=anterior_cap, icon_color="white")
    btn_sig = ft.IconButton(ft.icons.ARROW_FORWARD_IOS, on_click=siguiente_cap, icon_color="white")

    # Barra superior
    barra_superior = ft.Container(
        content=ft.Row([
            btn_ant,
            titulo_app,
            btn_sig
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=10,
        bgcolor="#1A1D23",
        border_radius=10
    )

    # Añadir a la página
    page.add(
        barra_superior,
        ft.Divider(color="#333333"),
        columna_versos
    )

    # Carga inicial
    cargar_texto()

ft.app(target=main)
