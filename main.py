import flet as ft
import json
import os
import unicodedata
import re
import threading

def normalizar(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(texto).lower())
                   if unicodedata.category(c) != 'Mn')

def main(page: ft.Page):
    page.title = "Mi Biblia Digital Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"
    page.padding = 10
    
    # --- ESTADO DE LA APP ---
    state = {
        "datos": None,
        "datos_normalizados": [], 
        "libro_actual": "", 
        "cap_actual": 1, 
        "total_caps": 0,
        "fuente_size": 22 
    }

    def cargar_datos():
        # "Súper carga": Busca el archivo con y sin extensión .json por si acaso
        rutas = [
            os.path.join("assets", "Biblia.json"),
            os.path.join("assets", "Biblia"),
            "assets/Biblia.json",
            "assets/Biblia",
            "Biblia.json",
            "Biblia",
            os.path.expanduser("~/Documents/biblia/assets/Biblia.json")
        ]
        for ruta in rutas:
            if os.path.exists(ruta):
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Creamos el índice rápido para que el buscador vuele
                        state["datos_normalizados"] = [normalizar(v["Text"]) for v in data]
                        return data
                except: continue
        return None

    state["datos"] = cargar_datos()

    # --- COMPONENTES DE INTERFAZ ---
    caja_busqueda = ft.TextField(
        label="Escribe una palabra (ej: fe, amor)...", 
        border_radius=15, 
        expand=True,
        on_submit=lambda e: realizar_busqueda(e.control.value)
    )
    btn_buscar = ft.ElevatedButton("🔍 BUSCAR", on_click=lambda _: realizar_busqueda(caja_busqueda.value))
    
    progreso = ft.ProgressBar(visible=False, color="#38BDF8")
    
    # Lista de resultados con scroll independiente
    lista_resultados = ft.ListView(expand=True, spacing=10, padding=10)
    contenedor_resultados = ft.Container(
        content=lista_resultados, 
        expand=True, 
        visible=False, 
        bgcolor="#1E293B", 
        border_radius=15
    )
    
    # Grillas de Libros y Capítulos (Evita la aglomeración)
    grid_libros = ft.GridView(expand=True, runs_count=5, max_extent=120, child_aspect_ratio=2.0, spacing=5)
    grid_capitulos = ft.GridView(expand=True, max_extent=60, child_aspect_ratio=1.0, spacing=5)
    
    seccion_libros = ft.Column([
        ft.Text("📖 LIBROS:", weight="bold", color="#38BDF8"),
        ft.Container(grid_libros, height=180, border=ft.border.all(1, "#334155"), border_radius=10, padding=5)
    ])

    seccion_capitulos = ft.Column([
        ft.Text("🔢 CAPÍTULOS:", weight="bold", color="#38BDF8"),
        ft.Container(grid_capitulos, expand=True, border=ft.border.all(1, "#334155"), border_radius=10, padding=5)
    ], expand=True)

    columna_seleccion = ft.Column([seccion_libros, seccion_capitulos], expand=True)

    # Area de Lectura
    area_texto = ft.ListView(expand=True, spacing=10, padding=15)
    cabecera_lectura = ft.Column()
    
    btn_ant = ft.FilledButton("⬅ Ant.", expand=True, on_click=lambda _: cambiar_capitulo(-1))
    btn_sig = ft.FilledButton("Sig. ➡", expand=True, on_click=lambda _: cambiar_capitulo(1))
    nav_inferior = ft.Container(content=ft.Row([btn_ant, btn_sig], spacing=10), visible=False)

    # --- LÓGICA DE BÚSQUEDA ---
    def realizar_busqueda(valor):
        p = normalizar(valor).strip()
        if len(p) < 2: return
        
        progreso.visible = True
        lista_resultados.controls.clear()
        columna_seleccion.visible = False
        contenedor_resultados.visible = True
        page.update()
        
        # Hilo para no congelar la pantalla
        threading.Thread(target=proceso_busqueda, args=(p,), daemon=True).start()

    def proceso_busqueda(p):
        conteo = 0
        patron = re.compile(rf"\b{re.escape(p)}\b")
        nuevos_items = []
        
        for i, texto_norm in enumerate(state["datos_normalizados"]):
            if p in texto_norm:
                if patron.search(texto_norm):
                    v = state["datos"][i]
                    nuevos_items.append(
                        ft.ListTile(
                            title=ft.Text(f"{v['Book']} {v['Chapter']}:{v['Verse']}", color="#38BDF8"),
                            subtitle=ft.Text(v['Text'], color="white"),
                            on_click=lambda _, b=v['Book'], c=v['Chapter']: mostrar_capitulo(b, c)
                        )
                    )
                    conteo += 1
                if conteo >= 40: break
        
        lista_resultados.controls = nuevos_items if nuevos_items else [ft.Text("No hay resultados exactos.")]
        progreso.visible = False
        page.update()

    # --- LÓGICA DE NAVEGACIÓN ---
    def mostrar_capitulo(libro, num_cap):
        state["libro_actual"], state["cap_actual"] = libro, int(num_cap)
        # Calcular total de capítulos del libro seleccionado
        caps_del_libro = [int(v['Chapter']) for v in state["datos"] if v['Book'] == libro]
        state["total_caps"] = max(caps_del_libro) if caps_del_libro else 0
        
        area_menu.visible, area_lectura.visible, nav_inferior.visible = False, True, True
        area_texto.controls.clear()
        
        versos = [v for v in state["datos"] if v['Book'] == libro and int(v['Chapter']) == state['cap_actual']]
        
        cabecera_lectura.controls = [
            ft.Row([
                ft.Text(f"{libro} {state['cap_actual']}", size=20, color="#38BDF8", weight="bold"),
                ft.Row([
                    ft.ElevatedButton("-", on_click=lambda _: cambiar_zoom(-2), width=45),
                    ft.ElevatedButton("+", on_click=lambda _: cambiar_zoom(2), width=45),
                    ft.FilledButton("ATRÁS", on_click=lambda _: volver_a_menu(), bgcolor="#E11D48")
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]
        
        spans = []
        for v in versos:
            spans.append(ft.TextSpan(f"{v['Verse']} ", ft.TextStyle(color="#38BDF8", weight="bold", size=state["fuente_size"]-4)))
            spans.append(ft.TextSpan(f"{v['Text']}\n\n", ft.TextStyle(size=state["fuente_size"], color="white")))
        
        area_texto.controls.append(ft.Text(spans=spans, selectable=True))
        btn_ant.disabled = (state["cap_actual"] <= 1)
        btn_sig.disabled = (state["cap_actual"] >= state["total_caps"])
        page.update()

    def volver_a_menu():
        area_menu.visible, area_lectura.visible, nav_inferior.visible = True, False, False
        contenedor_resultados.visible, columna_seleccion.visible = False, True
        page.update()

    def seleccionar_libro(nombre):
        grid_capitulos.controls.clear()
        # Obtener lista única de capítulos para ese libro
        caps = sorted(list(set([int(v['Chapter']) for v in state["datos"] if v['Book'] == nombre])))
        for c in caps:
            grid_capitulos.controls.append(
                ft.Container(
                    content=ft.Text(str(c), weight="bold"),
                    alignment=ft.Alignment(0, 0), # Centro compatible
                    bgcolor="#334155",
                    border_radius=5,
                    on_click=lambda e, n=nombre, num=c: mostrar_capitulo(n, num)
                )
            )
        page.update()

    def cambiar_zoom(delta):
        state["fuente_size"] += delta
        mostrar_capitulo(state["libro_actual"], state["cap_actual"])

    def cambiar_capitulo(delta):
        nuevo = state["cap_actual"] + delta
        if 1 <= nuevo <= state["total_caps"]:
            mostrar_capitulo(state["libro_actual"], nuevo)

    # --- ENSAMBLAJE FINAL ---
    area_menu = ft.Column([
        ft.Row([caja_busqueda, btn_buscar]),
        progreso,
        contenedor_resultados,
        columna_seleccion
    ], expand=True)
    
    area_lectura = ft.Column([cabecera_lectura, area_texto], visible=False, expand=True)

    if state["datos"]:
        # Llenar la grilla de libros una sola vez
        libros_vistos = []
        for v in state["datos"]:
            if v['Book'] not in libros_vistos:
                libros_vistos.append(v['Book'])
                grid_libros.controls.append(
                    ft.Container(
                        content=ft.Text(v['Book'], size=12, text_align="center"),
                        bgcolor="#1E293B",
                        border_radius=8,
                        alignment=ft.Alignment(0, 0),
                        on_click=lambda e, n=v['Book']: seleccionar_libro(n)
                    )
                )
        page.add(ft.Container(content=ft.Column([area_menu, area_lectura, nav_inferior], expand=True), expand=True))
    else:
        page.add(ft.Text("❌ Archivo de Biblia no encontrado en /assets", color="red", size=20))

# Para compilar el APK, el target debe ser el main
ft.app(target=main, assets_dir="assets")
