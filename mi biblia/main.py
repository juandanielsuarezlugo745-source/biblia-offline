import flet as ft
import json
import os
import random

def main(page: ft.Page):
    # Configuración de la ventana/pantalla
    page.title = "Biblia RVR1960 Offline"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0E1117"
    page.padding = 15
    page.fonts = {"Georgia": "https://github.com/google/fonts/raw/main/ofl/georgia/Georgia.ttf"}

    # 1. CARGA DE DATOS (Preparado para APK Offline)
    ruta_biblia = os.path.join("assets", "Biblia_Reina_Valera_1960_Esp.json")
    
    try:
        with open(ruta_biblia, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except Exception as e:
        page.add(ft.Text(f"Error: Asegúrate de que el archivo JSON esté en la carpeta 'assets'.\nDetalle: {e}", color="red"))
        return

    # 2. LISTAS MAESTRAS
    AT = ["Génesis", "Éxodo", "Levítico", "Números", "Deuteronomio", "Josué", "Jueces", "Rut", "1 Samuel", "2 Samuel", "1 Reyes", "2 Reyes", "1 Crónicas", "2 Crónicas", "Esdras", "Nehemías", "Ester", "Job", "Salmos", "Proverbios", "Eclesiastés", "Cantares", "Isaías", "Jeremías", "Lamentaciones", "Ezequiel", "Daniel", "Oseas", "Joel", "Amós", "Abdías", "Jonás", "Miqueas", "Nahúm", "Habacuc", "Sofonías", "Hageo", "Zacarías", "Malaquías"]
    NT = ["Mateo", "Marcos", "Lucas", "Juan", "Hechos", "Romanos", "1 Corintios", "2 Corintios", "Gálatas", "Efesios", "Filipenses", "Colosenses", "1 Tesalonicenses", "2 Tesalonicenses", "1 Timoteo", "2 Timoteo", "Tito", "Filemón", "Hebreos", "Santiago", "1 Pedro", "2 Pedro", "1 Juan", "2 Juan", "3 Juan", "Judas", "Apocalipsis"]

    # 3. VARIABLES DE ESTADO
    state = {"libro": "Génesis", "cap": 1}

    # 4. COMPONENTES VISUALES
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

    def cambio_seccion(e):
        libros = AT if selector_sec.value == "AT" else NT
        selector_libro.options = [ft.dropdown.Option(l) for l in libros]
        selector_libro.value = libros[0]
        state["libro"] = libros[0]
        state["cap"] = 1
        actualizar_capitulos()
        cargar_capitulo()

    def cambio_libro(e):
        state["libro"] = selector_libro.value
        state["cap"] = 1
        actualizar_capitulos()
        cargar_capitulo()

    def actualizar_capitulos():
        caps = sorted(list(set(int(v['Chapter']) for v in datos if v['Book'] == state["libro"])))
        selector_cap.options = [ft.dropdown.Option(str(c)) for c in caps]
        selector_cap.value = "1"
        page.update()

    # Selectores
    selector_sec = ft.Dropdown(
        label="Sec.", options=[ft.dropdown.Option("AT"), ft.dropdown.Option("NT")],
        value="AT", width=80, on_change=cambio_seccion, color="#FF9800", border_color="#FF9800"
    )
    selector_libro = ft.Dropdown(
        label="Libro", options=[ft.dropdown.Option(l) for l in AT],
        value="Génesis", expand=True, on_change=cambio_libro, color="#FF9800", border_color="#FF9800"
    )
    selector_cap = ft.Dropdown(
        label="Cap.", width=80, on_change=lambda e: (setattr(state, "cap", int(selector_cap.value)), cargar_capitulo()),
        color="#FF9800", border_color="#FF9800"
    )

    # Botones de navegación
    def navega(delta):
        caps = sorted(list(set(int(v['Chapter']) for v in datos if v['Book'] == state["libro"])))
        nuevo = state["cap"] + delta
        if 1 <= nuevo <= max(caps):
            state["cap"] = nuevo
            selector_cap.value = str(nuevo)
            cargar_capitulo()

    btn_ant = ft.ElevatedButton("⬅️", on_click=lambda _: navega(-1), bgcolor="#1e1e2f", color="#FF9800", expand=True)
    btn_sig = ft.ElevatedButton("➡️", on_click=lambda _: navega(1), bgcolor="#1e1e2f", color="#FF9800", expand=True)

    # Buscador (Expander style)
    def buscar(e):
        query = txt_busqueda.value.lower()
        if not query: return
        resultados.controls.clear()
        hallazgos = [v for v in datos if query in v['Text'].lower()][:15]
        for h in hallazgos:
            res_btn = ft.ListTile(
                title=ft.Text(f"{h['Book']} {h['Chapter']}:{h['Verse']}", color="#FF9800"),
                subtitle=ft.Text(h['Text'], color="#B0B0B0", max_lines=2),
                on_click=lambda _, b=h['Book'], c=h['Chapter']: ir_a(b, c)
            )
            resultados.controls.append(res_btn)
        page.update()

    def ir_a(libro, cap):
        state["libro"] = libro
        state["cap"] = int(cap)
        selector_sec.value = "AT" if libro in AT else "NT"
        selector_libro.options = [ft.dropdown.Option(l) for l in (AT if selector_sec.value == "AT" else NT)]
        selector_libro.value = libro
        actualizar_capitulos()
        selector_cap.value = str(cap)
        bs.open = False
        cargar_capitulo()

    txt_busqueda = ft.TextField(label="Palabra clave...", expand=True, border_color="#FF9800")
    resultados = ft.Column(scroll=ft.ScrollMode.ALWAYS, height=300)
    
    bs = ft.BottomSheet(
        ft.Container(
            ft.Column([
                ft.Row([txt_busqueda, ft.IconButton(ft.icons.SEARCH, on_click=buscar, icon_color="#FF9800")]),
                resultados
            ], tight=True), padding=20, bgcolor="#0E1117"
        )
    )
    page.overlay.append(bs)

    # Layout Principal
    page.add(
        ft.Row([
            ft.Text("RVR 1960", size=24, color="#FF9800", weight="bold"),
            ft.IconButton(ft.icons.SEARCH, on_click=lambda _: setattr(bs, "open", True) or page.update(), icon_color="#FF9800")
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([selector_sec, selector_libro, selector_cap]),
        ft.Row([btn_ant, btn_sig]),
        ft.Divider(color="#333333"),
        visor_texto
    )

    actualizar_capitulos()
    cargar_capitulo()

ft.app(target=main)