import flet as ft
import json
import os
import unicodedata

def normalizar(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(texto).lower())
                   if unicodedata.category(c) != 'Mn')

def main(page: ft.Page):
    page.title = "Biblia RVR1960"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"
    
    # Lista de variables globales
    datos = []
    libros_nombres = []

    # Contenedor principal donde ocurrirá la magia
    contenido_principal = ft.Column(expand=True, alignment="center", horizontal_alignment="center")
    
    # 1. Función para cargar el archivo (Rápida)
    def cargar_archivo_crudo():
        rutas = [
            "assets/Biblia.json",
            os.path.join(os.getcwd(), "assets", "Biblia.json"),
            "Biblia.json"
        ]
        for r in rutas:
            if os.path.exists(r):
                try:
                    with open(r, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except: continue
        return None

    # 2. Función para construir la interfaz de libros
    def construir_interfaz_libros():
        nonlocal libros_nombres
        grid = ft.Row(wrap=True, scroll=ft.ScrollMode.ALWAYS, expand=True)
        # Extraemos nombres de libros sin procesar todo el texto aún
        libros_nombres = []
        for v in datos:
            if v['Book'] not in libros_nombres:
                libros_nombres.append(v['Book'])
        
        for lib in libros_nombres:
            grid.controls.append(
                ft.Container(
                    content=ft.Text(lib, color="white", weight="bold"),
                    padding=15,
                    bgcolor="#1E293B",
                    border_radius=10,
                    on_click=lambda e, l=lib: print(f"Libro: {l}")
                )
            )
        
        contenido_principal.controls = [
            ft.Text("BIBLIA RVR1960", size=30, weight="bold", color="#38BDF8"),
            ft.Text("Selecciona un libro", size=16, color="grey"),
            grid
        ]
        page.update()

    # --- INICIO DE LA APP ---
    # Mostramos un cargando para que no se vea la pantalla azul vacía
    contenido_principal.controls = [
        ft.ProgressRing(width=50, height=50, stroke_width=5),
        ft.Text("Abriendo las Escrituras...", size=18, italic=True)
    ]
    page.add(contenido_principal)

    # Cargamos datos
    datos_recuperados = cargar_archivo_crudo()
    
    if datos_recuperados:
        datos.extend(datos_recuperados)
        # Construimos la interfaz inmediatamente
        construir_interfaz_libros()
    else:
        contenido_principal.controls = [
            ft.Icon(ft.icons.BLOCK, color="red", size=50),
            ft.Text("No se encontró Biblia.json en assets/", color="red")
        ]
        page.update()

ft.app(target=main)
