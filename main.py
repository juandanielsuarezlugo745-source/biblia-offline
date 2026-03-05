import flet as ft
import json
import os

def main(page: ft.Page):
    page.title = "Biblia RVR1960 Offline"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0E1117"
    page.padding = 15

    # 1. CARGA DE DATOS (Ruta simplificada para evitar errores en la cocina)
    # IMPORTANTE: El archivo en assets debe llamarse 'Biblia.json'
    base_path = os.path.dirname(__file__)
    ruta_biblia = os.path.join(base_path, "assets", "Biblia.json")
    
    try:
        with open(ruta_biblia, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except Exception as e:
        page.add(ft.Text(f"Error: No se encontró 'Biblia.json' en assets.\n{e}", color="red"))
        return

    # 2. LISTAS MAESTRAS
    AT = ["Génesis", "Éxodo", "Levítico", "Números", "Deuteronomio", "Josué", "Jueces", "Rut", "1 Samuel", "2 Samuel", "1 Reyes", "2 Reyes", "1 Crónicas", "2 Crónicas", "Esdras", "Nehemías", "Ester", "Job", "Salmos", "Proverbios", "Eclesiastés", "Cantares", "Isaías", "Jeremías", "Lamentaciones", "Ezequiel", "Daniel", "Oseas", "Joel", "Amós", "Abdías", "Jonás", "Miqueas", "Nahúm", "Habacuc", "Sofonías", "Hageo", "Zacarías", "Malaquías"]
    NT = ["Mateo", "Marcos", "Lucas", "Juan", "Hechos", "Romanos", "1 Corintios", "2 Corintios", "Gálatas", "Efesios", "Filipenses", "Colosenses", "1 Tesalonicenses", "2 Tesalonicenses", "1 Timoteo", "2 Timoteo", "Tito", "Filemón", "Hebreos", "Santiago", "1 Pedro", "2 Pedro", "1 Juan", "2 Juan", "3 Juan", "Judas", "Apocalipsis"]

    state = {"libro": "Génesis", "cap": 1}
    visor_texto = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)
    
    def cargar_capitulo(e=None):
        visor_texto.controls.clear()
        versos = [v for v in datos if v['Book'] == state["libro"] and int(v['Chapter']) == state["cap"]]
        for v in versos:
            visor_texto.controls.append(
                ft.Row([
                    ft.Text(f"{v['Verse']}", color="#FF9800", weight="bold", size=16),
                    ft.Text(v['Text'], color="#E0E0E0", size=18, expand=True)
                ], vertical_alignment=ft.CrossAxisAlignment.START)
            )
        page.update()

    def actualizar_capitulos():
        caps = sorted(list(set(int(v['Chapter']) for v in datos if v['Book'] == state["libro"])))
        selector_cap.options = [ft.dropdown.Option(str(c)) for c in caps]
        selector_cap.value = "1"
        page.update()

    selector_sec = ft.Dropdown(
        label="Sec.", options=[ft.dropdown.Option("AT"), ft.dropdown.Option("NT")],
        value="AT", width=80, color="#FF9800", border_color="#FF9800",
        on_change=lambda e: (
            setattr(selector_libro, "options", [ft.dropdown.Option(l) for l in (AT if selector_sec.value == "AT" else NT)]),
            setattr(selector_libro, "value", selector_libro.options[0].key),
            setattr(state, "libro", selector_libro.value),
            setattr(state, "cap", 1),
            actualizar_capitulos(),
            cargar_capitulo()
        )
    )
    
    selector_libro = ft.Dropdown(
        label="Libro", options=[ft.dropdown.Option(l) for l in AT],
        value="Génesis", expand=True, color="#FF9800", border_color="#FF9800",
        on_change=lambda e: (setattr(state, "libro", selector_libro.value), setattr(state, "cap", 1), actualizar_capitulos(), cargar_capitulo())
    )
    
    selector_cap = ft.Dropdown(
        label="Cap.", width=80, color="#FF9800", border_color="#FF9800",
        on_change=lambda e: (setattr(state, "cap", int(selector_cap.value)), cargar_capitulo())
    )

    page.add(
        ft.Row([ft.Text("MI BIBLIA", size=24, color="#FF9800", weight="bold")]),
        ft.Row([selector_sec, selector_libro, selector_cap]),
        ft.Divider(color="#333333"),
        visor_texto
    )

    actualizar_capitulos()
    cargar_capitulo()

ft.app(target=main)
