import flet as ft
import json
import os
import unicodedata
import re

def normalizar(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(texto).lower())
                   if unicodedata.category(c) != 'Mn')

def main(page: ft.Page):
    page.title = "Biblia RVR1960 Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"
    page.padding = 10

    state = {"libro_actual": "", "cap_actual": 1, "total_caps": 0, "fuente_size": 22}

    def cargar_y_preparar():
        # Buscamos en las rutas que Flet usa para empaquetar en Android
        posibles_rutas = [
            "assets/Biblia.json",
            "Biblia.json",
            os.path.join(os.getcwd(), "assets", "Biblia.json"),
            "/assets/Biblia.json"
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                        for v in datos:
                            v["t_limpio"] = normalizar(v["Text"])
                        return datos
                except:
                    continue
        return None

    datos = cargar_y_preparar()

    # --- ELEMENTOS DE INTERFAZ ---
    caja_busqueda = ft.TextField(label="Buscar en la Biblia...", border_radius=15, prefix_icon=ft.icons.SEARCH)
    lista_resultados = ft.Column(scroll=ft.ScrollMode.ALWAYS)
    contenedor_resultados = ft.Container(content=lista_resultados, expand=True, visible=False, bgcolor="#1E293B", border_radius=15, padding=10)
    grid_libros = ft.Row(wrap=True, scroll=ft.ScrollMode.ALWAYS, height=250)
    grid_capitulos = ft.Row(wrap=True, spacing=8)
    columna_seleccion = ft.Column([ft.Text("Libros:", weight="bold", color="#38BDF8"), grid_libros, ft.Divider(), ft.Text("Capítulos:", weight="bold", color="#38BDF8"), grid_capitulos], expand=True, scroll=ft.ScrollMode.ALWAYS)
    area_texto = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
    cabecera_lectura = ft.Column()
    btn_ant = ft.FilledButton("⬅ Ant.", expand=True, disabled=True, on_click=lambda _: cambiar_capitulo(-1))
    btn_sig = ft.FilledButton("Sig. ➡", expand=True, disabled=True, on_click=lambda _: cambiar_capitulo(1))
    nav_inferior = ft.Container(content=ft.Row([btn_ant, btn_sig], spacing=10), visible=False, padding=10)

    def mostrar_capitulo(libro, num_cap):
        state["libro_actual"], state["cap_actual"] = libro, int(num_cap)
        versos = [v for v in datos if v['Book'] == libro and int(v['Chapter']) == state['cap_actual']]
        state["total_caps"] = max([int(v['Chapter']) for v in datos if v['Book'] == libro])
        area_menu.visible, area_lectura.visible, nav_inferior.visible = False, True, True
        area_texto.controls.clear()
        
        cabecera_lectura.controls = [
            ft.Row([
                ft.Text(f"{libro} {num_cap}", size=22, color="#38BDF8", weight="bold"),
                ft.IconButton(ft.icons.CLOSE, icon_color="#E11D48", on_click=lambda _: volver_a_menu())
            ], alignment="spaceBetween"),
            ft.Row([
                ft.IconButton(ft.icons.TEXT_DECREASE, on_click=lambda _: cambiar_zoom(-2)),
                ft.Text(f"Tamaño: {state['fuente_size']}"),
                ft.IconButton(ft.icons.TEXT_INCREASE, on_click=lambda _: cambiar_zoom(2)),
            ], alignment="center")
        ]
        
        spans = []
        for v in versos:
            spans.append(ft.TextSpan(f"{v['Verse']} ", ft.TextStyle(color="#38BDF8", weight="bold", size=state["fuente_size"]-4)))
            spans.append(ft.TextSpan(f"{v['Text']}\n\n", ft.TextStyle(size=state["fuente_size"], color="white")))
        
        area_texto.controls.append(ft.Text(spans=spans, selectable=True))
        btn_ant.disabled, btn_sig.disabled = (state["cap_actual"] <= 1), (state["cap_actual"] >= state["total_caps"])
        page.update()

    def cambiar_zoom(delta):
        state["fuente_size"] = max(12, min(50, state["fuente_size"] + delta))
        mostrar_capitulo(state["libro_actual"], state["cap_actual"])

    def volver_a_menu():
        area_menu.visible, area_lectura.visible, nav_inferior.visible = True, False, False
        page.update()

    def cambiar_capitulo(delta):
        nuevo = state["cap_actual"] + delta
        if 1 <= nuevo <= state["total_caps"]: mostrar_capitulo(state["libro_actual"], nuevo)

    def buscar(e):
        p = normalizar(e.control.value).strip()
        if len(p) < 3:
            contenedor_resultados.visible, columna_seleccion.visible = False, True
            page.update(); return
        
        lista_resultados.controls.clear()
        columna_seleccion.visible = False
        count = 0
        for v in datos:
            if p in v["t_limpio"]:
                lista_resultados.controls.append(ft.ListTile(title=ft.Text(f"{v['Book']} {v['Chapter']}:{v['Verse']}", color="#38BDF8"), subtitle=ft.Text(v['Text']), on_click=lambda _, b=v['Book'], c=v['Chapter']: mostrar_capitulo(b, c)))
                count += 1
                if count > 40: break
        contenedor_resultados.visible = True
        page.update()

    caja_busqueda.on_change = buscar

    def sel_libro(nombre):
        grid_capitulos.controls.clear()
        caps = sorted(list(set([int(v['Chapter']) for v in datos if v['Book'] == nombre])))
        for c in caps:
            grid_capitulos.controls.append(ft.FilledButton(str(c), on_click=lambda e, n=nombre, num=c: mostrar_capitulo(n, num)))
        page.update()

    if datos:
        libros = []
        for v in datos:
            if v['Book'] not in libros:
                libros.append(v['Book'])
                grid_libros.controls.append(ft.TextButton(v['Book'], on_click=lambda e, n=v['Book']: sel_libro(n)))
    
    area_menu = ft.Column([caja_busqueda, contenedor_resultados, columna_seleccion], expand=True)
    area_lectura = ft.Column([cabecera_lectura, area_texto], visible=False, expand=True)
    
    if not datos:
        page.add(ft.Text("ERROR: Biblia.json no detectado en carpeta assets", color="red", size=20))
    else:
        page.add(ft.Container(content=ft.Column([ft.Text("BIBLIA RVR1960", size=24, weight="bold", color="#38BDF8"), area_menu, area_lectura, nav_inferior], expand=True), expand=True))

ft.app(target=main)
