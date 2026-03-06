import flet as ft
import json
import os

def main(page: ft.Page):
    page.title = "Biblia RVR1960"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"
    page.padding = 20

    # Variable para guardar los datos SOLO cuando se necesiten
    datos_biblia = []

    # Contenedor dinámico
    vista_principal = ft.Column(expand=True, scroll=ft.ScrollMode.ALWAYS)

    def cargar_datos_seguro():
        nonlocal datos_biblia
        if datos_biblia: # Si ya están cargados, no repetir
            return True
        
        rutas = ["assets/Biblia.json", "Biblia.json", os.path.join(os.getcwd(), "assets", "Biblia.json")]
        for r in rutas:
            if os.path.exists(r):
                try:
                    with open(r, 'r', encoding='utf-8') as f:
                        datos_biblia = json.load(f)
                        return True
                except: continue
        return False

    def mostrar_capitulo(libro, cap):
        # Limpiamos y mostramos carga
        page.clean()
        page.add(ft.Center(ft.ProgressRing()))
        
        if cargar_datos_seguro():
            versos = [v for v in datos_biblia if v['Book'] == libro and int(v['Chapter']) == int(cap)]
            
            contenido = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
            spans = []
            for v in versos:
                spans.append(ft.TextSpan(f"{v['Verse']} ", ft.TextStyle(color="#38BDF8", weight="bold")))
                spans.append(ft.TextSpan(f"{v['Text']}\n\n", ft.TextStyle(size=18)))
            
            page.clean()
            page.add(
                ft.Row([
                    ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: mostrar_inicio()),
                    ft.Text(f"{libro} {cap}", size=22, weight="bold")
                ]),
                ft.Divider(),
                ft.Text(spans=spans, selectable=True)
            )
        page.update()

    def seleccionar_capitulos(libro):
        page.clean()
        # No cargamos el JSON aquí todavía, solo mostramos números del 1 al 50 (ejemplo)
        # O mejor, cargamos rápido solo para saber cuántos capítulos tiene
        grid_caps = ft.Row(wrap=True)
        
        if cargar_datos_seguro():
            caps = sorted(list(set([int(v['Chapter']) for v in datos_biblia if v['Book'] == libro])))
            for c in caps:
                grid_caps.controls.append(
                    ft.ElevatedButton(str(c), on_click=lambda e, l=libro, n=c: mostrar_capitulo(l, n))
                )
        
        page.add(
            ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: mostrar_inicio()),
            ft.Text(f"Capítulos de {libro}", size=20, weight="bold"),
            grid_caps
        )
        page.update()

    def mostrar_inicio():
        page.clean()
        page.add(
            ft.Text("BIBLIA RVR1960", size=28, weight="bold", color="#38BDF8"),
            ft.Text("Selecciona un libro:", size=16),
            ft.Divider()
        )
        
        # Lista estática de libros para que la App abra en MILISEGUNDOS
        libros_lista = [
            "Génesis", "Éxodo", "Levítico", "Números", "Deuteronomio",
            "Josué", "Jueces", "Rut", "1 Samuel", "2 Samuel", "1 Reyes", "2 Reyes",
            "Isaías", "Jeremías", "Salmos", "Proverbios", "Juan", "Mateo" # Añade los que gustes
        ]
        
        grid = ft.Row(wrap=True, scroll=ft.ScrollMode.ALWAYS)
        for lib in libros_lista:
            grid.controls.append(
                ft.Container(
                    content=ft.Text(lib, weight="bold"),
                    padding=15, bgcolor="#1E293B", border_radius=10,
                    on_click=lambda e, l=lib: seleccionar_capitulos(l)
                )
            )
        page.add(grid)
        page.update()

    # Ejecutar inicio
    mostrar_inicio()

ft.app(target=main)
