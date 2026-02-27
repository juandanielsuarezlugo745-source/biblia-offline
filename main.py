import flet as ft
import json
import os

def main(page: ft.Page):
    page.title = "Mi Biblia Offline"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Intentar cargar el icono desde assets o desde la raíz
    icon_path = "assets/icon.png" if os.path.exists("assets/icon.png") else "icon.png"
    
    # Cargar la Biblia
    try:
        with open("assets/Biblia_Reina_Valera_1960_Esp.json", "r", encoding="utf-8") as f:
            biblia_data = json.load(f)
    except Exception as e:
        page.add(ft.Text(f"Error al cargar la Biblia: {e}"))
        return

    def cambiar_capitulo(e):
        # Lógica fluida que te gustó anoche
        page.clean()
        page.add(ft.Text("Cargando capítulo...", size=20))
        # (Aquí va el resto de tu lógica optimizada)
        page.update()

    page.add(ft.Text("¡Bienvenido a tu Biblia!", size=30, weight="bold"))
    page.update()

ft.app(target=main, assets_dir="assets")
