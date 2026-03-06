import flet as ft
import json
import os

def main(page: ft.Page):
    page.title = "Biblia RVR1960"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Contenedor donde se mostrarán los libros
    contenedor_libros = ft.Column(expand=True, scroll=ft.ScrollMode.ALWAYS)

    def cargar_datos_y_mostrar(e=None):
        # 1. Buscamos el archivo
        ruta = os.path.join(os.getcwd(), "assets", "Biblia.json")
        if not os.path.exists(ruta):
            ruta = "assets/Biblia.json"

        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                # Cargamos los datos
                datos = json.load(f)
                
                # Extraemos la lista de libros (esto es rápido)
                libros = []
                for v in datos:
                    if v['Book'] not in libros:
                        libros.append(v['Book'])
                
                # Limpiamos pantalla y mostramos los libros
                page.clean()
                page.add(
                    ft.Text("BIBLIA RVR1960", size=28, weight="bold", color="#38BDF8"),
                    ft.Text("Selecciona un libro:", size=16),
                    ft.Divider()
                )
                
                grid = ft.Row(wrap=True, spacing=10)
                for lib in libros:
                    grid.controls.append(
                        ft.ElevatedButton(
                            content=ft.Text(lib, weight="bold"),
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                            on_click=lambda e, l=lib: print(f"Seleccionaste {l}")
                        )
                    )
                page.add(grid)
        except Exception as ex:
            page.add(ft.Text(f"Error al leer datos: {str(ex)}", color="red"))
        
        page.update()

    # Pantalla de Bienvenida (Se muestra de inmediato)
    page.add(
        ft.Column([
            ft.Icon(ft.icons.MENU_BOOK_ROUNDED, size=100, color="#38BDF8"),
            ft.Text("Bienvenido a tu Biblia", size=24, weight="bold"),
            ft.Text("Presiona el botón para cargar los libros", size=14, color="grey"),
            ft.ElevatedButton(
                "Entrar a la Biblia", 
                icon=ft.icons.PLAY_ARROW,
                on_click=cargar_datos_y_mostrar,
                height=50
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)
