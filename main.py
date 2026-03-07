import flet as ft
import json
import os
import unicodedata
import re
import threading

def normalizar(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', str(texto).lower()) if unicodedata.category(c) != 'Mn')

def main(page: ft.Page):
    page.title = "Mi Biblia"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"
    page.padding = ft.padding.only(top=50, left=10, right=10, bottom=10)
    
    state = {"datos": None, "datos_norm": [], "libro": "", "cap": 1, "fuente": 22}

    def cargar_datos():
        # Busca en todas las combinaciones posibles
        posibles = ["Biblia.json", "Biblia", "biblia.json", "biblia"]
        for p in posibles:
            ruta = os.path.join("assets", p)
            if os.path.exists(ruta):
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        d = json.load(f)
                        state["datos_norm"] = [normalizar(v["Text"]) for v in d]
                        return d
                except: continue
        return None

    state["datos"] = cargar_datos()

    # Interfaz Básica
    caja = ft.TextField(label="Buscar...", expand=True)
    btn = ft.ElevatedButton("🔍", on_click=lambda _: buscar(caja.value))
    prog = ft.ProgressBar(visible=False, color="#38BDF8")
    res_list = ft.ListView(expand=True, spacing=10)
    res_cont = ft.Container(res_list, expand=True, visible=False, bgcolor="#1E293B", padding=10, border_radius=10)
    
    g_libros = ft.GridView(expand=True, runs_count=5, max_extent=120, child_aspect_ratio=2.0)
    g_caps = ft.GridView(expand=True, max_extent=60, child_aspect_ratio=1.0)
    
    col_sel = ft.Column([
        ft.Text("LIBROS:", weight="bold"), ft.Container(g_libros, height=150),
        ft.Text("CAPÍTULOS:", weight="bold"), ft.Container(g_caps, expand=True)
    ], expand=True)

    area_txt = ft.ListView(expand=True, spacing=10, padding=15)
    nav = ft.Row([ft.ElevatedButton("⬅", on_click=lambda _: saltar(-1)), ft.ElevatedButton("➡", on_click=lambda _: saltar(1))], visible=False)

    def buscar(q):
        q = normalizar(q).strip()
        if len(q) < 2: return
        prog.visible, res_cont.visible, col_sel.visible = True, True, False
        res_list.controls.clear()
        page.update()
        threading.Thread(target=proc_buscar, args=(q,), daemon=True).start()

    def proc_buscar(q):
        items = []
        for i, t in enumerate(state["datos_norm"]):
            if q in t:
                v = state["datos"][i]
                items.append(ft.ListTile(title=ft.Text(f"{v['Book']} {v['Chapter']}:{v['Verse']}"), on_click=lambda _, b=v['Book'], c=v['Chapter']: leer(b, c)))
                if len(items) > 30: break
        res_list.controls = items if items else [ft.Text("No hay resultados")]
        prog.visible = False
        page.update()

    def leer(l, c):
        state["libro"], state["cap"] = l, int(c)
        res_cont.visible, col_sel.visible, area_txt.visible, nav.visible = False, False, True, True
        area_txt.controls.clear()
        versos = [v for v in state["datos"] if v['Book'] == l and int(v['Chapter']) == state['cap']]
        txt = []
        for v in versos:
            txt.append(ft.TextSpan(f"{v['Verse']} ", ft.TextStyle(color="#38BDF8", weight="bold")))
            txt.append(ft.TextSpan(f"{v['Text']}\n\n"))
        area_txt.controls.append(ft.Text(spans=txt, size=state["fuente"], selectable=True))
        page.update()

    def saltar(d):
        leer(state["libro"], state["cap"] + d)

    if state["datos"]:
        libros = sorted(list(set([v['Book'] for v in state["datos"]])), key=lambda x: [v['Book'] for v in state["datos"]].index(x))
        for l in libros:
            g_libros.controls.append(ft.Container(ft.Text(l, size=10), bgcolor="#334155", on_click=lambda e, n=l: sel_libro(n), alignment=ft.alignment.center))
        page.add(ft.Column([ft.Row([caja, btn]), prog, res_cont, col_sel, area_txt, nav], expand=True))
    else:
        page.add(ft.Text("❌ Archivo de Biblia no encontrado en /assets", color="red", size=20))

    def sel_libro(l):
        g_caps.controls.clear()
        caps = sorted(list(set([int(v['Chapter']) for v in state["datos"] if v['Book'] == l])))
        for c in caps:
            g_caps.controls.append(ft.Container(ft.Text(str(c)), bgcolor="#334155", on_click=lambda e, n=l, num=c: leer(n, num), alignment=ft.alignment.center))
        page.update()

ft.app(target=main, assets_dir="assets")
