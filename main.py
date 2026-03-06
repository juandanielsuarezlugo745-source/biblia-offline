import flet as ft
import json
import os
import unicodedata
import re

# Función para quitar acentos y buscar mejor
def normalizar(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(texto).lower())
                   if unicodedata.category(c) != 'Mn')

def main(page: ft.Page):
    page.title = "Biblia RVR1960 Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"
    page.padding = 15
    page.window_full_screen = True

    state = {
        "libro_actual": "", 
        "cap_actual": 1, 
        "total_caps": 0,
        "fuente_size": 22 
    }

    # --- CARGA DE DATOS ADAPTADA A TU GITHUB ---
    def cargar_y_preparar():
        # Buscamos el archivo Biblia.json en la raíz o en assets
        posibles_rutas = ["Biblia.json", "assets/Biblia.json", "Biblia_Reina_Valera_1960_Esp.json"]
        ruta_final = None
        for r in posibles_rutas:
            if os.path.exists(r):
                ruta_final = r
                break
        
        try:
            if ruta_final:
                with open(ruta_final, 'r', encoding='utf-8') as f:
                    datos_raw = json.load(f)
                    for v in datos_raw:
                        v["t_limpio"] = normalizar(v["Text"])
                    return datos_raw
            return None
        except: return None

    datos = cargar_y_preparar()

    # --- COMPONENTES DE INTERFAZ ---
    caja_busqueda = ft.TextField(label="Buscar palabra...", border_radius=15)
    lista_resultados = ft.Column(scroll=ft.ScrollMode.ALWAYS)
    contenedor_resultados = ft.Container(
        content=lista_resultados, expand=True, visible=False, 
        bgcolor="#1E293B", border_radius=15, padding=10
    )
    
    grid_libros = ft.Row(wrap=True, scroll=ft.ScrollMode.ALWAYS, height=180)
    grid_capitulos = ft.Row(wrap=True, spacing=5)
    
    columna_seleccion = ft.Column([
        ft.Text("Libros:", weight="bold", color="#38BDF8", size=18),
        grid_libros,
        ft.Divider(height=10, color="transparent"),
        ft.Text("Capítulos:", weight="bold", color="#38BDF8", size=18),
        grid_capitulos
    ], expand=True)

    area_texto = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
    cabecera_lectura = ft.Column()
    
    estilo_nav = ft.ButtonStyle(color="white", bgcolor="#38BDF8")
    btn_ant = ft.FilledButton("⬅ Anterior", style=estilo_nav, expand=True)
    btn_sig = ft.FilledButton("Siguiente ➡", style=estilo_nav, expand=True)
    
    nav_inferior = ft.Container(
        content=ft.Row([btn_ant, btn_sig], spacing=10), 
        visible=False
    )

    # --- FUNCIONES ---
    def cambiar_zoom(delta):
        nueva_fuente = state["fuente_size"] + delta
        if 14 <= nueva_fuente <= 45: 
            state["fuente_size"] = nueva_fuente
            mostrar_capitulo(state["libro_actual"], state["cap_actual"])

    def mostrar_capitulo(libro, num_cap):
        state["libro_actual"] = libro
        state["cap_actual"] = int(num_cap)
        state["total_caps"] = max([int(v['Chapter']) for v in datos if v['Book'] == libro])
        
        area_menu.visible = False
        area_lectura.visible = True
        nav_inferior.visible = True
        
        area_texto.controls.clear()
        versos = [v for v in datos if v['Book'] == libro and int(v['Chapter']) == state['cap_actual']]
        
        cabecera_lectura.controls = [
            ft.Row([
                ft.Column([
                    ft.Text(f"📖 {libro} {state['cap_actual']}", size=20, color="#38BDF8", weight="bold"),
                    ft.Row([
                        ft.FilledButton("-", on_click=lambda _: cambiar_zoom(-2), width=45),
                        ft.Text(f"{state['fuente_size']}"),
                        ft.FilledButton("+", on_click=lambda _: cambiar_zoom(2), width=45),
                    ], spacing=5)
                ]),
                ft.FilledButton("Cerrar", on_click=lambda _: volver_a_menu(), bgcolor="#E11D48")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]
        
        contenido_spans = []
        for v in versos:
            cita = f"{v['Book']} {v['Chapter']}:{v['Verse']} "
            contenido_spans.append(ft.TextSpan(cita, ft.TextStyle(color="#38BDF8", weight="bold", size=state["fuente_size"]-4)))
            contenido_spans.append(ft.TextSpan(f"{v['Text']}\n\n", ft.TextStyle(size=state["fuente_size"], color="white")))
        
        area_texto.controls.append(ft.Text(spans=contenido_spans, selectable=True))
        
        btn_ant.disabled = (state["cap_actual"] <= 1)
        btn_sig.disabled = (state["cap_actual"] >= state["total_caps"])
        page.update()

    def volver_a_menu():
        area_menu.visible = True
        area_lectura.visible = False
        nav_inferior.visible = False
        caja_busqueda.value = ""
        contenedor_resultados.visible = False
        columna_seleccion.visible = True
        btn_volver_libros.visible = False
        grid_capitulos.controls.clear()
        page.update()

    def cambiar_capitulo(delta):
        nuevo_cap = state["cap_actual"] + delta
        if 1 <= nuevo_cap <= state["total_caps"]:
            mostrar_capitulo(state["libro_actual"], nuevo_cap)

    btn_ant.on_click = lambda _: cambiar_capitulo(-1)
    btn_sig.on_click = lambda _: cambiar_capitulo(1)
    caja_busqueda.on_change = lambda e: realizar_busqueda(e)

    def realizar_busqueda(e):
        palabra_buscada = normalizar(e.control.value).strip()
        lista_resultados.controls.clear()
        if len(palabra_buscada) < 3:
            contenedor_resultados.visible = False
            btn_volver_libros.visible = False 
            columna_seleccion.visible = True 
            page.update()
            return
        
        columna_seleccion.visible = False
        btn_volver_libros.visible = True
        conteo = 0
        patron = re.compile(rf"\b{palabra_buscada}\b")
        for v in datos:
            if patron.search(v["t_limpio"]):
                conteo += 1
                lista_resultados.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"{v['Book']} {v['Chapter']}:{v['Verse']}", color="#38BDF8", weight="bold"),
                        subtitle=ft.Text(v['Text'], color="white", size=14),
                        on_click=lambda _, b=v['Book'], c=v['Chapter']: mostrar_capitulo(b, c)
                    )
                )
                if conteo >= 30: break
        contenedor_resultados.visible = True if conteo > 0 else False
        page.update()

    def recuperar_libros(e):
        columna_seleccion.visible = True
        btn_volver_libros.visible = False
        contenedor_resultados.visible = False
        page.update()

    btn_volver_libros = ft.FilledButton(
        "MOSTRAR LIBROS Y CAPÍTULOS", 
        visible=False, on_click=recuperar_libros,
        style=ft.ButtonStyle(bgcolor="#1E293B", color="#38BDF8")
    )

    # --- ENSAMBLAJE ---
    area_menu = ft.Column([caja_busqueda, btn_volver_libros, contenedor_resultados, columna_seleccion], expand=True)
    area_lectura = ft.Column([cabecera_lectura, area_texto], visible=False, expand=True)

    if datos:
        libros_unid = []
        for v in datos:
            if v['Book'] not in libros_unid:
                libros_unid.append(v['Book'])
                grid_libros.controls.append(ft.TextButton(v['Book'], on_click=lambda e, n=v['Book']: seleccionar_libro(n)))

    def seleccionar_libro(nombre):
        grid_capitulos.controls.clear()
        caps = sorted(list(set([int(v['Chapter']) for v in datos if v['Book'] == nombre])))
        for c in caps:
            grid_capitulos.controls.append(ft.FilledButton(str(c), on_click=lambda e, n=nombre, num=c: mostrar_capitulo(n, num)))
        page.update()

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("MI BIBLIA DIGITAL", size=24, weight="bold", color="#38BDF8"),
                area_menu, area_lectura, nav_inferior
            ], expand=True),
            expand=True
        )
    )

# Para Android es vital el assets_dir si usas imagenes, pero por ahora lo dejamos simple
ft.app(target=main)
