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
    # --- CONFIGURACIÓN DE PANTALLA ---
    page.title = "Biblia Master 6.8"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#070B14"
    # Margen para la hora del teléfono
    page.padding = ft.padding.only(top=50, left=15, right=15, bottom=15)
    
    state = {
        "datos": None,
        "datos_norm": [],
        "libro_sel": "", 
        "cap_sel": 1,
        "fuente_size": 20,
        "ultima_busqueda": "",
        "en_busqueda": False
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
    main_container = ft.Column(expand=True, spacing=10)

    def mostrar_vista(vista_controles):
        main_container.controls.clear()
        main_container.controls.extend(vista_controles)
        page.update()

    # --- 1. VISTA DE LIBROS ---
    def vista_inicio():
        state["en_busqueda"] = False
        grid = ft.GridView(expand=True, max_extent=150, spacing=10, run_spacing=10)
        if state["datos"]:
            libros = []
            for v in state["datos"]:
                if v['Book'] not in libros:
                    libros.append(v['Book'])
                    grid.controls.append(
                        ft.Container(
                            content=ft.Text(v['Book'], weight="bold", size=13, text_align="center"),
                            bgcolor="#111827", border_radius=10, 
                            alignment=ft.Alignment(0, 0),
                            padding=10, on_click=lambda e, n=v['Book']: seleccionar_libro(n)
                        )
                    )
        
        caja_busqueda = ft.TextField(label="Buscar...", expand=True, border_color="#38BDF8")
        btn_buscar = ft.TextButton("BUSCAR", on_click=lambda _: ejecutar_busqueda(caja_busqueda.value))

        mostrar_vista([
            ft.Text("BIBLIA DIGITAL", size=28, weight="bold", color="#38BDF8"),
            ft.Row([caja_busqueda, btn_buscar], spacing=5),
            ft.Divider(height=10, color="transparent"),
            grid
        ])

    # --- 2. VISTA DE CAPÍTULOS ---
    def seleccionar_libro(nombre):
        state["libro_sel"] = nombre
        caps = sorted(list(set([int(v['Chapter']) for v in state["datos"] if v['Book'] == nombre])))
        grid_caps = ft.GridView(expand=True, max_extent=70, spacing=10)
        for c in caps:
            grid_caps.controls.append(
                ft.Container(
                    content=ft.Text(str(c), weight="bold", size=16), bgcolor="#1E293B",
                    alignment=ft.Alignment(0, 0), border_radius=10,
                    on_click=lambda e, n=c: seleccionar_capitulo(n)
                )
            )
        mostrar_vista([
            ft.Row([ft.TextButton("< LIBROS", on_click=lambda _: vista_inicio()), 
                    ft.Container(ft.Text(nombre, size=22, weight="bold"), expand=True)]),
            grid_caps
        ])

    # --- 3. VISTA DE VERSÍCULOS ---
    def seleccionar_capitulo(num):
        state["cap_sel"] = num
        v_nums = sorted(list(set([int(v['Verse']) for v in state["datos"] 
                                 if v['Book'] == state['libro_sel'] and int(v['Chapter']) == num])))
        
        grid_versos = ft.GridView(expand=True, max_extent=60, spacing=8)
        for v in v_nums:
            grid_versos.controls.append(
                ft.Container(
                    content=ft.Text(str(v), weight="bold"),
                    bgcolor="#0F172A", border_radius=8,
                    border=ft.Border.all(1, "#38BDF8"),
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda e, vn=v: abrir_lectura(state["libro_sel"], state["cap_sel"], vn)
                )
            )
        mostrar_vista([
            ft.Row([ft.TextButton("< CAP", on_click=lambda _: seleccionar_libro(state["libro_sel"])), 
                    ft.Container(ft.Text(f"{state['libro_sel']} {num}", size=22, weight="bold"), expand=True)]),
            grid_versos
        ])

    # --- 4. LECTURA (LÓGICA DE TU IMAGEN: SELECCIÓN NATIVA) ---
    def abrir_lectura(libro, cap, verso_foco):
        state["libro_sel"] = libro
        state["cap_sel"] = int(cap)
        v_data = [v for v in state["datos"] if v['Book'] == libro and int(v['Chapter']) == state['cap_sel']]
        
        lista_v = ft.ListView(expand=True, spacing=12, padding=15)
        for v in v_data:
            es_foco = int(v['Verse']) == verso_foco
            
            # --- AQUÍ ESTÁ LA LÓGICA DE LA IMAGEN ---
            # Ponemos el texto como 'selectable=True' para que Android 
            # muestre el menú de Copy/Share al dejar presionado.
            lista_v.controls.append(
                ft.Container(
                    content=ft.Text(
                        spans=[
                            ft.TextSpan(f"{v['Verse']} ", ft.TextStyle(color="#38BDF8" if not es_foco else "#FACC15", weight="bold")),
                            ft.TextSpan(v['Text'], ft.TextStyle(size=state["fuente_size"], color="white" if not es_foco else "#FACC15"))
                        ],
                        selectable=True # <--- ACTIVA EL MENÚ DE TU IMAGEN
                    ),
                    padding=5
                )
            )
        
        def volver_atras_inteligente(_):
            if state["en_busqueda"]:
                ejecutar_busqueda(state["ultima_busqueda"])
            else:
                seleccionar_capitulo(cap)

        mostrar_vista([
            ft.Row([
                ft.TextButton("< ATRÁS", on_click=volver_atras_inteligente),
                ft.Container(ft.Text(f"{libro} {cap}", size=18, weight="bold"), expand=True),
                ft.TextButton("[+]", on_click=lambda _: cambiar_zoom(2)),
                ft.TextButton("[-]", on_click=lambda _: cambiar_zoom(-2)),
            ]),
            ft.Row([
                ft.ElevatedButton("🏠 INICIO", on_click=lambda _: vista_inicio(), bgcolor="#1E293B", color="#38BDF8"),
                ft.Row([
                    ft.TextButton("< ANT.", on_click=lambda _: navegar_cap(-1)),
                    ft.TextButton("SIG. >", on_click=lambda _: navegar_cap(1)),
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Text("Presiona el texto para copiar o compartir", size=11, color="white60", text_align="center"),
            ft.Container(lista_v, expand=True, bgcolor="#111827", border_radius=15, border=ft.Border.all(1, "#1E293B"))
        ])

    # --- BÚSQUEDA ---
    def ejecutar_busqueda(texto):
        if not texto or len(texto.strip()) < 1: return
        state["ultima_busqueda"] = texto
        state["en_busqueda"] = True
        p_norm = normalizar(texto).strip()
        patron = re.compile(rf"\b{re.escape(p_norm)}\b")
        
        hallazgos = {}
        for i, txt_norm in enumerate(state["datos_norm"]):
            if patron.search(txt_norm):
                v = state["datos"][i]
                libro = v["Book"]
                if libro not in hallazgos: hallazgos[libro] = []
                hallazgos[libro].append(v)
        
        lista_res = ft.ListView(expand=True, spacing=10)
        if not hallazgos:
            lista_res.controls.append(ft.Text("Sin resultados."))
        else:
            for libro, versos in hallazgos.items():
                lista_res.controls.append(
                    ft.Container(
                        content=ft.Row([ft.Text("📖"), ft.Text(f"{libro} ({len(versos)})", size=16)], spacing=10),
                        padding=15, bgcolor="#1E293B", border_radius=10,
                        on_click=lambda e, l=libro, v_lista=versos: vista_resultados_detallados(l, v_lista)
                    )
                )
        mostrar_vista([
            ft.Row([ft.TextButton("< INICIO", on_click=lambda _: vista_inicio()), ft.Text(f"Busca: '{texto}'", size=18)]),
            lista_res
        ])

    def vista_resultados_detallados(libro, lista_v):
        lista_detallada = ft.ListView(expand=True, spacing=15, padding=10)
        for v in lista_v:
            lista_detallada.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"{libro} {v['Chapter']}:{v['Verse']}", weight="bold", color="#38BDF8"),
                        ft.Text(v['Text'], size=state["fuente_size"], color="white", selectable=True), # Lógica nativa también aquí
                    ], spacing=5),
                    padding=15, bgcolor="#111827", border_radius=10, border=ft.Border.all(1, "#1E293B")
                )
            )
        mostrar_vista([
            ft.Row([ft.TextButton("< RESULTADOS", on_click=lambda _: ejecutar_busqueda(state["ultima_busqueda"])), 
                    ft.Text(f"{libro}", size=18)]),
            lista_detallada
        ])

    def navegar_cap(delta):
        nueva_c = state["cap_sel"] + delta
        existe = any(int(v['Chapter']) == nueva_c and v['Book'] == state['libro_sel'] for v in state["datos"])
        if existe:
            abrir_lectura(state["libro_sel"], nueva_c, 1)

    def cambiar_zoom(delta):
        state["fuente_size"] += delta
        abrir_lectura(state["libro_sel"], state["cap_sel"], 1)

    page.add(main_container)
    vista_inicio()

ft.run(main)
