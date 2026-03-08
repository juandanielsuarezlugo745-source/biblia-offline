import flet as ft
import json
import os
import unicodedata
import re
import sys

def normalizar(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(texto).lower())
                   if unicodedata.category(c) != 'Mn')

def main(page: ft.Page):
    page.title = "Biblia Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"
    page.padding = ft.Padding(10, 45, 10, 10)
    
    state = {
        "datos": None,
        "datos_norm": [],
        "libro_actual": "", 
        "cap_actual": 1, 
        "total_caps": 0,
        "fuente_size": 22 
    }

    def cargar_datos():
        rutas = [os.path.join(getattr(sys, '_MEIPASS', ''), "assets", "Biblia.json"), "assets/Biblia.json", "Biblia.json"]
        for ruta in rutas:
            if os.path.exists(ruta):
                try:
                    with open(ruta, 'r', encoding='utf-8-sig') as f:
                        data = json.load(f)
                        state["datos_norm"] = [normalizar(v["Text"]) for v in data]
                        return data
                except: continue
        return None

    state["datos"] = cargar_datos()

    # --- 1. DEFINIR COMPONENTES PRIMERO ---
    progreso = ft.ProgressBar(visible=False, color="#38BDF8")
    lista_resultados = ft.ListView(expand=True, spacing=10)
    contenedor_resultados = ft.Container(content=lista_resultados, expand=True, visible=False, bgcolor="#1E293B", border_radius=15, padding=10)
    
    grid_libros = ft.GridView(expand=True, runs_count=5, max_extent=120, child_aspect_ratio=2.0, spacing=5)
    grid_capitulos = ft.GridView(expand=True, max_extent=60, child_aspect_ratio=1.0, spacing=5)

    seccion_libros = ft.Column([
        ft.Text("LIBROS:", weight="bold", color="#38BDF8"),
        ft.Container(grid_libros, height=220, border=ft.Border.all(1, "#334155"), border_radius=10, padding=5)
    ])

    seccion_capitulos = ft.Column([
        ft.Text("CAPÍTULOS:", weight="bold", color="#38BDF8"),
        ft.Container(grid_capitulos, expand=True, border=ft.Border.all(1, "#334155"), border_radius=10, padding=5)
    ], expand=True, visible=False)

    # AQUÍ SE DEFINE columna_seleccion ANTES DE USARLA
    columna_seleccion = ft.Column([seccion_libros, seccion_capitulos], expand=True)

    # --- 2. LÓGICA DE FUNCIONES ---
    def volver_a_menu():
        area_menu.visible, area_lectura.visible, nav_inferior.visible = True, False, False
        contenedor_resultados.visible, columna_seleccion.visible = False, True
        page.update()

    def realizar_busqueda(valor):
        p = normalizar(valor).strip()
        if len(p) < 2: return 
        progreso.visible = True
        page.update()
        
        lista_resultados.controls.clear()
        lista_resultados.controls.append(
            ft.ElevatedButton("⬅ VOLVER A LIBROS", on_click=lambda _: volver_a_menu(), bgcolor="#E11D48", color="white")
        )

        patron = re.compile(rf"\b{re.escape(p)}\b")
        resultados_encontrados = []
        for i, texto_norm in enumerate(state["datos_norm"]):
            if patron.search(texto_norm):
                v = state["datos"][i]
                resultados_encontrados.append(
                    ft.ListTile(
                        title=ft.Text(f"{v['Book']} {v['Chapter']}:{v['Verse']}", color="#38BDF8", weight="bold"),
                        subtitle=ft.Text(v['Text'], color="white"),
                        on_click=lambda _, b=v['Book'], c=v['Chapter']: mostrar_capitulo(b, c)
                    )
                )
                if len(resultados_encontrados) > 50: break

        lista_resultados.controls.extend(resultados_encontrados)
        progreso.visible = False
        columna_seleccion.visible = False
        contenedor_resultados.visible = True
        page.update()

    def cambiar_zoom(delta):
        state["fuente_size"] += delta
        mostrar_capitulo(state["libro_actual"], state["cap_actual"])

    def cambiar_capitulo(delta):
        nuevo = state["cap_actual"] + delta
        if 1 <= nuevo <= state["total_caps"]: mostrar_capitulo(state["libro_actual"], nuevo)

    def mostrar_capitulo(libro, num_cap):
        state["libro_actual"], state["cap_actual"] = libro, int(num_cap)
        caps_list = [int(v['Chapter']) for v in state["datos"] if v['Book'] == libro]
        state["total_caps"] = max(caps_list) if caps_list else 0
        area_menu.visible, area_lectura.visible, nav_inferior.visible = False, True, True
        area_texto.controls.clear()
        versos = [v for v in state["datos"] if v['Book'] == libro and int(v['Chapter']) == state['cap_actual']]
        cabecera_lectura.controls = [
            ft.Row([
                ft.Text(f"{libro} {state['cap_actual']}", size=20, color="#38BDF8", weight="bold"),
                ft.Row([
                    ft.ElevatedButton("A-", on_click=lambda _: cambiar_zoom(-2), width=55),
                    ft.ElevatedButton("A+", on_click=lambda _: cambiar_zoom(2), width=55),
                    ft.FilledButton("ATRÁS", on_click=lambda _: volver_a_menu(), bgcolor="#E11D48")
                ], spacing=5)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]
        spans = []
        for v in versos:
            spans.append(ft.TextSpan(f"{v['Verse']} ", ft.TextStyle(color="#38BDF8", weight="bold", size=max(12, state["fuente_size"]-6))))
            spans.append(ft.TextSpan(f"{v['Text']}\n\n", ft.TextStyle(size=state["fuente_size"], color="white")))
        area_texto.controls.append(ft.Text(spans=spans, selectable=True))
        btn_ant.disabled, btn_sig.disabled = (state["cap_actual"] <= 1), (state["cap_actual"] >= state["total_caps"])
        page.update()

    def seleccionar_libro(nombre):
        seccion_capitulos.visible = True
        grid_capitulos.controls.clear()
        caps = sorted(list(set([int(v['Chapter']) for v in state["datos"] if v['Book'] == nombre])))
        for c in caps:
            grid_capitulos.controls.append(
                ft.Container(
                    content=ft.Text(str(c), weight="bold", color="white"),
                    alignment=ft.Alignment(0, 0),
                    bgcolor="#334155", border_radius=5,
                    on_click=lambda e, n=nombre, num=c: mostrar_capitulo(n, num)
                )
            )
        page.update()

    # --- 3. DEFINIR ÁREAS PRINCIPALES ---
    caja_busqueda = ft.TextField(label="Palabra exacta (ej: Fe)", border_radius=15, expand=True, on_submit=lambda e: realizar_busqueda(e.control.value))
    btn_buscar = ft.ElevatedButton("BUSCAR 🔍", on_click=lambda _: realizar_busqueda(caja_busqueda.value), bgcolor="#38BDF8", color="white")
    
    area_menu = ft.Column([ft.Row([caja_busqueda, btn_buscar]), progreso, contenedor_resultados, columna_seleccion], expand=True)
    
    area_texto = ft.ListView(expand=True, spacing=10, padding=15)
    cabecera_lectura = ft.Column()
    area_lectura = ft.Column([cabecera_lectura, area_texto], visible=False, expand=True)
    
    btn_ant = ft.FilledButton("⬅ Anterior", expand=True, on_click=lambda _: cambiar_capitulo(-1))
    btn_sig = ft.FilledButton("Siguiente ➡", expand=True, on_click=lambda _: cambiar_capitulo(1))
    nav_inferior = ft.Container(content=ft.Row([btn_ant, btn_sig], spacing=10), visible=False)

    # --- 4. CARGA INICIAL ---
    if state["datos"]:
        libros_vistos = []
        for v in state["datos"]:
            if v['Book'] not in libros_vistos:
                libros_vistos.append(v['Book'])
                grid_libros.controls.append(
                    ft.Container(
                        content=ft.Text(v['Book'], size=11, text_align="center", color="white"),
                        bgcolor="#1E293B", border_radius=8, alignment=ft.Alignment(0, 0),
                        on_click=lambda e, n=v['Book']: seleccionar_libro(n)
                    )
                )
        page.add(ft.Container(content=ft.Column([area_menu, area_lectura, nav_inferior], expand=True), expand=True))
    else:
        page.add(ft.Text("Error: No se encontró Biblia.json", color="red"))

ft.app(target=main)
