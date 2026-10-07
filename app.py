"""
Aplicación Streamlit: Generador y Editor Inteligente de Carteles con OpenAI.
Permite subir imágenes temáticas, definir estilos artísticos, generar carteles
y editar o sumar elementos de forma iterativa mediante fotos de referencia.
"""

import io
import os
import sys
import time
from datetime import datetime
from PIL import Image

# Asegurar que el directorio de la aplicación esté en el path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from poster_generator import (
    create_initial_poster_prompt,
    create_iteration_poster_prompt,
    generate_poster_image,
    save_poster_to_project,
    list_project_versions,
    list_all_projects,
    OUTPUTS_DIR
)

# Cargar variables de entorno si existe .env
load_dotenv()

# Configuración de página
st.set_page_config(
    page_title="AI Poster Studio | Creador de Carteles",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para una interfaz pulida y moderna
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(120deg, #ff4b4b 0%, #ff8533 50%, #9933ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #7d8590;
        margin-bottom: 1.5rem;
    }
    .badge-style {
        background-color: rgba(255, 75, 75, 0.12);
        color: #ff4b4b;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }
    .info-box {
        border-radius: 10px;
        padding: 12px 16px;
        background: rgba(125, 133, 144, 0.08);
        border-left: 4px solid #ff4b4b;
        margin-bottom: 14px;
        font-size: 0.92rem;
    }
    .version-card {
        border: 1px solid rgba(125, 133, 144, 0.25);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 14px;
        background-color: rgba(255, 255, 255, 0.02);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        font-weight: 600;
        border-radius: 8px 8px 0px 0px;
    }
</style>
""", unsafe_allow_html=True)

# Inicialización de estado en session_state
if "project_id" not in st.session_state:
    st.session_state.project_id = f"cartel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if "current_poster_bytes" not in st.session_state:
    st.session_state.current_poster_bytes = None

if "current_poster_meta" not in st.session_state:
    st.session_state.current_poster_meta = None

if "current_iteration" not in st.session_state:
    st.session_state.current_iteration = 0


# ==========================================
# BARRA LATERAL (CONFIGURACIÓN & PROYECTOS)
# ==========================================
with st.sidebar:
    st.title("⚙️ Configuración")
    
    # 1. API Key de OpenAI
    env_api_key = os.getenv("OPENAI_API_KEY", "")
    api_key = st.text_input(
        "OpenAI API Key",
        value=env_api_key,
        type="password",
        help="Introduce tu API Key de OpenAI (sk-...). Se detecta automáticamente de tu archivo .env si existe."
    )
    
    if not api_key:
        st.warning("⚠️ Introduce tu clave de OpenAI para generar carteles.")
    else:
        st.success("✅ Clave de OpenAI configurada")

    st.markdown("---")

    # 2. Proyecto Activo
    st.subheader("📁 Proyecto de Cartel")
    col_proj1, col_proj2 = st.columns([3, 1])
    with col_proj1:
        st.caption(f"ID Actual: `{st.session_state.project_id}`")
    with col_proj2:
        if st.button("➕ Nuevo", help="Iniciar un proyecto de cartel desde cero"):
            st.session_state.project_id = f"cartel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.current_poster_bytes = None
            st.session_state.current_poster_meta = None
            st.session_state.current_iteration = 0
            st.rerun()

    # Cargar proyecto existente si hay
    all_projects = list_all_projects()
    if all_projects:
        project_ids = [p["project_id"] for p in all_projects]
        if st.session_state.project_id not in project_ids:
            project_options = [st.session_state.project_id] + project_ids
        else:
            project_options = project_ids

        selected_project = st.selectbox(
            "Cargar proyecto anterior:",
            options=project_options,
            index=project_options.index(st.session_state.project_id),
            help="Selecciona un proyecto anterior para ver sus versiones o continuar editándolo"
        )
        if selected_project != st.session_state.project_id:
            st.session_state.project_id = selected_project
            versions = list_project_versions(selected_project)
            if versions:
                latest = versions[-1]
                with open(latest["image_path"], "rb") as f:
                    st.session_state.current_poster_bytes = f.read()
                st.session_state.current_poster_meta = latest
                st.session_state.current_iteration = latest.get("iteration", 1)
            st.rerun()

    st.markdown("---")

    # 3. Modelo de Generación de Imagen
    st.subheader("🤖 Modelo de Imagen")
    image_model_options = [
        "chatgpt-image-latest",
        "gpt-image-2",
        "gpt-image-1.5",
        "Personalizado"
    ]
    selected_image_model_choice = st.selectbox(
        "Motor de Generación de Imagen:",
        options=image_model_options,
        index=0,
        format_func=lambda m: {
            "chatgpt-image-latest": "⭐ ChatGPT Image (Oficial Activo)",
            "gpt-image-2": "⚡ GPT Image 2",
            "gpt-image-1.5": "🎨 GPT Image 1.5",
            "Personalizado": "✏️ Modelo Personalizado"
        }.get(m, m),
        help="Elige el modelo para crear y editar el cartel. 'chatgpt-image-latest' es el modelo oficial de ChatGPT Image activo en tu cuenta."
    )

    if selected_image_model_choice == "Personalizado":
        image_model_name = st.text_input(
            "Identificador exacto del modelo:",
            value="chatgpt-image-latest",
            help="Escribe el nombre del modelo tal como aparece en tu API de OpenAI"
        )
    else:
        image_model_name = selected_image_model_choice

    # Base URL opcional (para proxies o proveedores compatibles con OpenAI)
    with st.expander("🌐 Endpoint / Base URL (Opcional)"):
        custom_base_url = st.text_input(
            "Base URL",
            value=os.getenv("OPENAI_BASE_URL", ""),
            placeholder="https://api.openai.com/v1",
            help="Déjalo vacío para usar la API oficial de OpenAI, o escribe tu endpoint personalizado."
        )

    st.markdown("---")

    # 4. Parámetros de Generación de Imagen
    st.subheader("📐 Formato del Cartel")
    poster_size = st.selectbox(
        "Orientación & Proporción",
        options=["1024x1536", "1024x1024", "1536x1024"],
        index=0,
        format_func=lambda x: {
            "1024x1536": "📱 Vertical Póster (1024 × 1536) - Recomendado",
            "1024x1024": "⬛ Cuadrado (1024 × 1024)",
            "1536x1024": "🖥️ Horizontal Panorámico (1536 × 1024)"
        }[x]
    )

    poster_quality = st.selectbox(
        "Calidad de Imagen",
        options=["high", "medium", "standard"],
        index=0,
        help="Configuración 'high' para máximo detalle, texturas fotorrealistas y tipografía nítida."
    )

    vision_model = st.selectbox(
        "Modelo de Visión (Director Creativo)",
        options=["gpt-4o", "gpt-4o-mini"],
        index=0,
        help="Analiza tus fotos de referencia y sintetiza la composición artística para el generador de imágenes."
    )

    st.markdown("---")
    st.caption(f"AI Poster Studio • Modelo: {image_model_name} (Calidad: {poster_quality})")


# ==========================================
# CABECERA PRINCIPAL
# ==========================================
st.markdown('<div class="main-header">AI Poster Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Crea carteles publicitarios y artísticos con la API de OpenAI. Sube fotos de referencia, define tu prompt y estilo libremente, e itera añadiendo elementos a tus versiones.</div>', unsafe_allow_html=True)

# TABS PRINCIPALES
tab_crear, tab_editar, tab_historial = st.tabs([
    "🎨 1. Crear Nuevo Cartel",
    "✏️ 2. Editar y Sumar Elementos (Iteración)",
    "🗂️ 3. Historial y Galería del Proyecto"
])


# ==============================================================================
# TAB 1: CREAR NUEVO CARTEL
# ==============================================================================
with tab_crear:
    col_input, col_preview = st.columns([1, 1], gap="large")

    with col_input:
        st.subheader("📝 Definición del Cartel")
        
        # 1. Imagen temática base (opcional o recomendada)
        st.markdown("**1. Imagen temática base** *(opcional)*")
        base_image_file = st.file_uploader(
            "Sube una foto sobre el tema que quieras hacer el cartel (objeto, persona, paisaje, producto...)",
            type=["png", "jpg", "jpeg", "webp"],
            key="base_uploader"
        )
        if base_image_file:
            st.image(base_image_file, caption="Foto de referencia base subida", use_container_width=True)

        # 2. Prompt del Autor (incluye tema, estilo artístico, textos, etc.)
        st.markdown("**2. Prompt / Descripción del Cartel (Tema, Estilo Artístico y Textos)**")
        user_prompt_text = st.text_area(
            "Describe cómo quieres el cartel (estilo artístico, colores, tema, textos o eslogan y detalles):",
            placeholder="Ejemplo: Cartel anunciador de las fiestas patronales de San Juan 2026 en estilo Art Déco elegante y geométrico. En el centro una hoguera estilizada con adornos dorados sobre fondo azul noche, con el texto 'FIESTAS DE SAN JUAN 2026' en tipografía de los años 20...",
            height=160
        )

        generate_btn = st.button("🚀 Generar Cartel", type="primary", use_container_width=True)

    with col_preview:
        st.subheader("🖼️ Cartel Resultante")

        if generate_btn:
            if not api_key:
                st.error("❌ Por favor, proporciona tu clave de OpenAI en la barra lateral para continuar.")
            elif not user_prompt_text.strip() and not base_image_file:
                st.warning("⚠️ Introduce una descripción (prompt) o sube al menos una imagen de referencia.")
            else:
                try:
                    client_kwargs = {"api_key": api_key}
                    if custom_base_url and custom_base_url.strip():
                        client_kwargs["base_url"] = custom_base_url.strip()
                    client = OpenAI(**client_kwargs)

                    with st.spinner("🤖 El Director Creativo (GPT-4o) está analizando la imagen y componiendo el cartel..."):
                        engineered_prompt = create_initial_poster_prompt(
                            client=client,
                            user_prompt=user_prompt_text,
                            image_input=base_image_file,
                            model=vision_model
                        )

                    with st.spinner(f"🎨 {image_model_name} está sintetizando tu cartel en resolución {poster_size} ({poster_quality})..."):
                        img_bytes, revised_prompt, img_url = generate_poster_image(
                            client=client,
                            prompt=engineered_prompt,
                            model=image_model_name,
                            size=poster_size,
                            quality=poster_quality
                        )

                    # Guardar en proyecto
                    iteration_num = 1
                    saved_meta = save_poster_to_project(
                        project_id=st.session_state.project_id,
                        iteration=iteration_num,
                        image_bytes=img_bytes,
                        original_prompt=user_prompt_text,
                        ai_prompt=engineered_prompt,
                        revised_prompt=revised_prompt,
                        size=poster_size,
                        quality=poster_quality,
                        notes=f"Generación inicial con {image_model_name}",
                        image_model=image_model_name
                    )

                    st.session_state.current_poster_bytes = img_bytes
                    st.session_state.current_poster_meta = saved_meta
                    st.session_state.current_iteration = iteration_num
                    st.success("✨ ¡Cartel generado y guardado con éxito!")

                except Exception as ex:
                    st.error(f"❌ Error durante la generación: {ex}")

        # Mostrar cartel activo si existe
        if st.session_state.current_poster_bytes:
            st.image(
                st.session_state.current_poster_bytes,
                caption=f"Cartel (Versión {st.session_state.current_iteration})",
                use_container_width=True
            )

            # Botón de descarga
            st.download_button(
                label="⬇️ Descargar Cartel (PNG Alta Resolución)",
                data=st.session_state.current_poster_bytes,
                file_name=f"{st.session_state.project_id}_v{st.session_state.current_iteration}.png",
                mime="image/png",
                use_container_width=True
            )

            # Detalles técnicos de la IA
            if st.session_state.current_poster_meta:
                with st.expander("🔍 Ver detalles del prompt sintetizado por la IA"):
                    st.markdown("**Prompt compuesto por GPT-4o Visión:**")
                    st.code(st.session_state.current_poster_meta.get("ai_engineered_prompt", ""), language="text")
                    model_used = st.session_state.current_poster_meta.get("model_used", image_model_name)
                    st.markdown(f"**Prompt final procesado por {model_used}:**")
                    revised_p = st.session_state.current_poster_meta.get("image_revised_prompt") or st.session_state.current_poster_meta.get("dalle_revised_prompt", "")
                    st.code(revised_p, language="text")

            st.info("💡 ¿Quieres afinar este cartel o sumarle elementos? Ve a la pestaña **'2. Editar y Sumar Elementos'** arriba.")
        else:
            st.info("Configura tu cartel a la izquierda y pulsa 'Generar Cartel' para ver aquí el resultado.")


# ==============================================================================
# TAB 2: EDITAR Y SUMAR ELEMENTOS (ITERACIÓN CON FOTOS DE REFERENCIA)
# ==============================================================================
with tab_editar:
    st.subheader("✏️ Edición e Integración de Nuevos Elementos")
    st.caption("Toma el cartel actual y evoluciona el diseño sumando objetos, personajes, logos o texturas a partir de fotos de referencia.")

    if not st.session_state.current_poster_bytes:
        st.warning("⚠️ Aún no has generado ningún cartel. Primero genera uno en la pestaña '1. Crear Nuevo Cartel' o carga un proyecto anterior.")
    else:
        col_ed_left, col_ed_right = st.columns([1, 1], gap="large")

        with col_ed_left:
            st.markdown(f"**Cartel Base Actual (Versión {st.session_state.current_iteration}):**")
            st.image(
                st.session_state.current_poster_bytes,
                caption="Versión que se utilizará como base de la edición",
                use_container_width=True
            )

        with col_ed_right:
            st.markdown("**1. Sube 1 o varias fotos de referencia de los elementos a sumar:**")
            ref_photos = st.file_uploader(
                "Adjunta fotos de referencia (personaje, logo, objeto secundario, textura, etc.)",
                type=["png", "jpg", "jpeg", "webp"],
                accept_multiple_files=True,
                key="iteration_uploader"
            )

            if ref_photos:
                st.caption(f"Has adjuntado {len(ref_photos)} foto(s) de referencia:")
                cols_thumbs = st.columns(min(len(ref_photos), 4))
                for i, photo in enumerate(ref_photos):
                    with cols_thumbs[i % len(cols_thumbs)]:
                        st.image(photo, caption=f"Ref #{i+1}: {photo.name[:12]}...", use_container_width=True)

            st.markdown("**2. Instrucciones de edición / Qué deseas sumar o modificar:**")
            edit_instructions_text = st.text_area(
                "Explica exactamente cómo incorporar las referencias al cartel:",
                placeholder="Ejemplo: Suma la guitarra eléctrica de la Foto de Referencia #1 en manos del personaje principal, adaptándola a la misma paleta y estilo. Cambia el fondo para incluir la luna de la Foto #2 y añade el texto 'SPECIAL GUEST' en la parte inferior.",
                height=130
            )

            btn_iterate = st.button("🔄 Generar Nueva Versión del Cartel", type="primary", use_container_width=True)

            if btn_iterate:
                if not api_key:
                    st.error("❌ Por favor, proporciona tu clave de OpenAI en la barra lateral.")
                elif not edit_instructions_text.strip():
                    st.warning("⚠️ Introduce las instrucciones de lo que deseas cambiar o sumar al cartel.")
                else:
                    try:
                        client_kwargs = {"api_key": api_key}
                        if custom_base_url and custom_base_url.strip():
                            client_kwargs["base_url"] = custom_base_url.strip()
                        client = OpenAI(**client_kwargs)

                        with st.spinner("🧠 GPT-4o está analizando el cartel actual y tus nuevas referencias para planificar la integración..."):
                            iter_prompt = create_iteration_poster_prompt(
                                client=client,
                                current_poster_image=st.session_state.current_poster_bytes,
                                edit_instructions=edit_instructions_text,
                                reference_images_list=ref_photos or [],
                                model=vision_model
                            )

                        with st.spinner(f"🎨 {image_model_name} está sintetizando la nueva versión perfeccionada..."):
                            new_bytes, new_revised, new_url = generate_poster_image(
                                client=client,
                                prompt=iter_prompt,
                                model=image_model_name,
                                size=poster_size,
                                quality=poster_quality
                            )

                        next_iter = st.session_state.current_iteration + 1
                        saved_meta = save_poster_to_project(
                            project_id=st.session_state.project_id,
                            iteration=next_iter,
                            image_bytes=new_bytes,
                            original_prompt=edit_instructions_text,
                            ai_prompt=iter_prompt,
                            revised_prompt=new_revised,
                            size=poster_size,
                            quality=poster_quality,
                            notes=f"Iteración v{next_iter} con {image_model_name} y {len(ref_photos or [])} ref.",
                            image_model=image_model_name
                        )

                        # Actualizar estado
                        st.session_state.current_poster_bytes = new_bytes
                        st.session_state.current_poster_meta = saved_meta
                        st.session_state.current_iteration = next_iter
                        st.success(f"🎉 ¡Nueva Versión (v{next_iter}) generada y guardada exitosamente!")
                        st.rerun()

                    except Exception as err:
                        st.error(f"❌ Error al generar la iteración: {err}")


# ==============================================================================
# TAB 3: HISTORIAL Y GALERÍA DEL PROYECTO
# ==============================================================================
with tab_historial:
    st.subheader("🗂️ Galería & Evolución del Cartel")
    versions = list_project_versions(st.session_state.project_id)

    if not versions:
        st.info("No hay versiones registradas aún para este proyecto. Genera tu primer cartel para comenzar el historial.")
    else:
        st.write(f"Evolución del proyecto **{st.session_state.project_id}** ({len(versions)} versión/es):")

        # Vista comparativa antes/después si hay al menos 2 versiones
        if len(versions) >= 2:
            st.markdown("### 🔀 Comparativa: Primera Versión (v1) vs Última Versión")
            col_v1, col_vlast = st.columns(2)
            with col_v1:
                st.markdown(f"**Versión Inicial (v1)** - {versions[0]['date_readable']}")
                st.image(versions[0]["image_path"], use_container_width=True)
            with col_vlast:
                st.markdown(f"**Versión Actual (v{versions[-1]['iteration']})** - {versions[-1]['date_readable']}")
                st.image(versions[-1]["image_path"], use_container_width=True)
            st.markdown("---")

        # Lista cronológica de todas las versiones
        st.markdown("### 📜 Línea de Tiempo de Iteraciones")
        for v in reversed(versions):
            with st.container():
                st.markdown(f"""
                <div class="version-card">
                    <h4>Versión {v['iteration']} • <small>{v['date_readable']}</small></h4>
                    <p><b>Prompt / Instrucciones del autor:</b> {v.get('user_prompt', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)

                col_img, col_info = st.columns([1, 2])
                with col_img:
                    st.image(v["image_path"], use_container_width=True)
                    with open(v["image_path"], "rb") as f_img:
                        btn_data = f_img.read()
                    st.download_button(
                        label=f"⬇️ Descargar v{v['iteration']}",
                        data=btn_data,
                        file_name=f"{st.session_state.project_id}_v{v['iteration']}.png",
                        mime="image/png",
                        key=f"dl_v_{v['iteration']}"
                    )
                with col_info:
                    st.caption(f"🤖 Modelo: `{v.get('model_used', 'gpt-image-2.1')}` • Dimensiones: {v.get('size')} • Calidad: {v.get('quality')}")
                    if v.get('notes'):
                        st.caption(f"📝 {v.get('notes')}")
                    with st.expander(f"Detalles del Prompt de la IA (v{v['iteration']})"):
                        st.markdown("**Prompt Director Creativo (GPT-4o):**")
                        st.code(v.get("ai_engineered_prompt", ""), language="text")
                        st.markdown(f"**Prompt final procesado por {v.get('model_used', 'ChatGPT Image')}:**")
                        revised_p = v.get("image_revised_prompt") or v.get("dalle_revised_prompt", "")
                        st.code(revised_p, language="text")

                    # Botón para restaurar esta versión como activa
                    if st.button(f"⏪ Restaurar v{v['iteration']} como Cartel Activo para seguir editando", key=f"restore_v_{v['iteration']}"):
                        with open(v["image_path"], "rb") as f_img:
                            st.session_state.current_poster_bytes = f_img.read()
                        st.session_state.current_poster_meta = v
                        st.session_state.current_iteration = v["iteration"]
                        st.success(f"Cartel v{v['iteration']} cargado como activo.")
                        st.rerun()

                st.markdown("---")
