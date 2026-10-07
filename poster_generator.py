"""
Módulo principal de integración con la API de OpenAI para generación y edición iterativa de carteles.
Combina GPT-4o (Visión) para el razonamiento artístico y DALL-E 3 para la síntesis de imagen.
"""

import base64
import io
import json
import os
import time
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from PIL import Image
import requests
from openai import OpenAI

# Directorio base para almacenar las creaciones e historial
OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")


def ensure_output_directories():
    """Asegura que las carpetas de salida existan."""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUTS_DIR, "projects"), exist_ok=True)


def process_image_to_base64(image_input, max_size: int = 1600) -> Tuple[str, str]:
    """
    Convierte una imagen (bytes, PIL Image o UploadedFile) a formato JPEG base64
    redimensionando si es necesario para optimizar el envío a la API de Visión.
    Retorna: (data_url, base64_string)
    """
    if isinstance(image_input, bytes):
        img = Image.open(io.BytesIO(image_input))
    elif hasattr(image_input, "read"):
        image_input.seek(0)
        img = Image.open(io.BytesIO(image_input.read()))
    elif isinstance(image_input, Image.Image):
        img = image_input
    else:
        raise ValueError("Tipo de imagen no soportado")

    # Convertir a RGB si tiene canal alfa o es paleta
    if img.mode in ("RGBA", "P", "LA"):
        rgb_img = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "RGBA":
            rgb_img.paste(img, mask=img.split()[3])
        else:
            rgb_img.paste(img.convert("RGB"))
        img = rgb_img
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # Redimensionar si excede el tamaño máximo
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=88, optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    data_url = f"data:image/jpeg;base64,{encoded}"
    return data_url, encoded


def create_initial_poster_prompt(
    client: OpenAI,
    user_prompt: str,
    style_name: str,
    style_directives: str,
    image_input=None,
    model: str = "gpt-4o"
) -> str:
    """
    Usa GPT-4o Visión como Director de Arte para analizar la foto base (si existe),
    el estilo artístico seleccionado y las intenciones del usuario para crear
    un prompt maestro altamente descriptivo para DALL-E 3.
    """
    system_instruction = (
        "Eres un galardonado Director de Arte y Diseñador Gráfico de cartelería publicitaria y artística. "
        "Tu misión es redactar un prompt en inglés hiperdetallado, visualmente impactante y profesional "
        "para el generador de imágenes DALL-E 3.\n\n"
        "Reglas clave:\n"
        "1. Si se te proporciona una imagen de referencia, analiza minuciosamente su sujeto principal, "
        "composición, paleta y esencia, para reinterpretarla fielmente dentro del estilo artístico pedido.\n"
        "2. Aplica con maestría las directrices del estilo artístico solicitado (texturas, geometría, luz, tipografía).\n"
        "3. Estructura el cartel con jerarquía visual de póster: punto focal principal, fondo con textura de soporte, "
        "sensación de póster de alta gama.\n"
        "4. Devuelve ÚNICAMENTE el texto final del prompt para DALL-E 3 (en inglés), sin introducciones, saludos ni comillas."
    )

    user_content: List[Dict[str, Any]] = []

    text_content = (
        f"ESTILO ARTÍSTICO REQUERIDO: {style_name}\n"
        f"DIRECTIVAS DEL ESTILO: {style_directives}\n\n"
        f"DESCRIPCIÓN Y DESEOS DEL AUTOR:\n{user_prompt}\n\n"
    )

    if image_input is not None:
        try:
            data_url, _ = process_image_to_base64(image_input)
            text_content += (
                "Se adjunta la imagen base que el usuario quiere plasmar en el cartel. "
                "Examina la imagen y sintetiza su sujeto y esencia combinándolos armónicamente con el estilo elegido."
            )
            user_content.append({"type": "text", "text": text_content})
            user_content.append({
                "type": "image_url",
                "image_url": {"url": data_url, "detail": "high"}
            })
        except Exception as e:
            text_content += f"(Nota: No se pudo procesar la imagen adjunta debido a: {e})"
            user_content.append({"type": "text", "text": text_content})
    else:
        text_content += "No se adjuntó imagen de referencia; crea el cartel desde cero basado en la descripción."
        user_content.append({"type": "text", "text": text_content})

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content}
        ],
        temperature=0.7,
        max_tokens=900
    )

    refined_prompt = response.choices[0].message.content.strip()
    return refined_prompt


def create_iteration_poster_prompt(
    client: OpenAI,
    current_poster_image,
    edit_instructions: str,
    reference_images_list: List[Any],
    original_style_name: str,
    original_style_directives: str,
    model: str = "gpt-4o"
) -> str:
    """
    Toma el cartel actual generado + una o varias fotos de referencia + instrucciones
    del usuario para redactar el nuevo prompt de DALL-E 3 que integra los nuevos elementos
    preservando la coherencia y el estilo.
    """
    system_instruction = (
        "Eres un Director de Arte experto en edición, remezcla y composición visual de carteles. "
        "El usuario tiene un cartel ya generado y quiere crear una nueva versión modificada o añadir nuevos elementos. "
        "El usuario te proporciona:\n"
        "1. La imagen del cartel actual.\n"
        "2. Una o más imágenes de referencia con los nuevos elementos, personajes, objetos o motivos a incorporar.\n"
        "3. Las instrucciones precisas de lo que desea cambiar, sumar o reorganizar.\n\n"
        "Tu tarea:\n"
        "- Analizar el cartel original: mantener su paleta de color, estilo gráfico, iluminación y atmósfera general.\n"
        "- Analizar cada una de las nuevas fotos de referencia y extraer exactamente los elementos que el autor pide sumar.\n"
        "- Describir cómo se integran esos nuevos elementos orgánicamente en el cartel existente como si siempre hubiesen estado ahí.\n"
        "- Redactar el prompt final para DALL-E 3 (en inglés) que recree esta nueva versión completa del cartel con los añadidos.\n"
        "- Devuelve ÚNICAMENTE el texto final del prompt para DALL-E 3 (en inglés), sin saludos ni explicaciones."
    )

    user_content: List[Dict[str, Any]] = []

    text_content = (
        f"ESTILO ARTÍSTICO BASE: {original_style_name}\n"
        f"DIRECTIVAS ESTILÍSTICAS: {original_style_directives}\n\n"
        f"INSTRUCCIONES DE EDICIÓN / ELEMENTOS A SUMAR:\n{edit_instructions}\n\n"
        f"Se adjunta a continuación:\n"
        f"- Primera imagen: El cartel generado actualmente (Versión previa).\n"
        f"- Siguientes imágenes: Las {len(reference_images_list)} fotos de referencia proporcionadas por el autor."
    )

    user_content.append({"type": "text", "text": text_content})

    # 1. Adjuntar el cartel actual
    poster_data_url, _ = process_image_to_base64(current_poster_image)
    user_content.append({
        "type": "image_url",
        "image_url": {"url": poster_data_url, "detail": "high"}
    })

    # 2. Adjuntar las fotos de referencia adicionales
    for idx, ref_img in enumerate(reference_images_list, start=1):
        try:
            ref_data_url, _ = process_image_to_base64(ref_img)
            user_content.append({
                "type": "image_url",
                "image_url": {"url": ref_data_url, "detail": "high"}
            })
        except Exception as e:
            print(f"Error procesando imagen de referencia {idx}: {e}")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content}
        ],
        temperature=0.7,
        max_tokens=900
    )

    iteration_prompt = response.choices[0].message.content.strip()
    return iteration_prompt


def get_account_image_models(client: OpenAI) -> List[str]:
    """
    Consulta los modelos de imagen reales y activos en la cuenta del usuario.
    Prioriza chatgpt-image-latest y la serie gpt-image-2.
    """
    try:
        models = [m.id for m in client.models.list().data]
        img_models = [m for m in models if 'image' in m.lower() or 'dall' in m.lower()]
        preferred_order = [
            "chatgpt-image-latest",
            "gpt-image-2",
            "gpt-image-2-2026-04-21",
            "gpt-image-1.5",
            "gpt-image-1"
        ]
        sorted_models = []
        for pref in preferred_order:
            if pref in img_models and pref not in sorted_models:
                sorted_models.append(pref)
        for m in img_models:
            if m not in sorted_models:
                sorted_models.append(m)
        return sorted_models if sorted_models else ["chatgpt-image-latest", "gpt-image-2"]
    except Exception:
        return ["chatgpt-image-latest", "gpt-image-2", "gpt-image-1.5"]


def generate_poster_image(
    client: OpenAI,
    prompt: str,
    model: str = "chatgpt-image-latest",
    size: str = "1024x1536",
    quality: str = "high"
) -> Tuple[bytes, str, str]:
    """
    Llama al endpoint de generación de imágenes de OpenAI (chatgpt-image-latest, gpt-image-2, etc.).
    Soporta tanto respuestas con URL externa como b64_json embebido y gestiona parámetros específicos.
    Retorna: (image_bytes, revised_prompt, image_url)
    """
    # Para chatgpt-image-latest, los tamaños soportados son 1024x1536, 1024x1024, 1536x1024 o auto
    if "chatgpt-image" in model:
        if size == "1024x1792":
            size = "1024x1536"
        elif size == "1792x1024":
            size = "1536x1024"

    call_kwargs: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "n": 1,
    }
    if size:
        call_kwargs["size"] = size

    # Parámetro de calidad (high por defecto)
    if quality:
        call_kwargs["quality"] = quality

    try:
        response = client.images.generate(**call_kwargs)
    except Exception as e:
        err_msg = str(e).lower()
        # Si el modelo no acepta el argumento 'quality', reintentar sin él
        if "quality" in err_msg or "unexpected keyword" in err_msg or "extra fields" in err_msg:
            call_kwargs.pop("quality", None)
            response = client.images.generate(**call_kwargs)
        else:
            raise e

    image_data = response.data[0]
    revised_prompt = getattr(image_data, "revised_prompt", None) or prompt

    # Procesar según venga como base64 o URL
    if getattr(image_data, "b64_json", None):
        image_bytes = base64.b64decode(image_data.b64_json)
        image_url = "data:image/png;base64,[embedded]"
    elif getattr(image_data, "url", None):
        image_url = image_data.url
        img_resp = requests.get(image_url, timeout=60)
        img_resp.raise_for_status()
        image_bytes = img_resp.content
    else:
        raise ValueError("La respuesta de la API no contiene ni URL ni datos Base64.")

    return image_bytes, revised_prompt, image_url


# Alias para compatibilidad hacia atrás
generate_dalle_poster = generate_poster_image



def save_poster_to_project(
    project_id: str,
    iteration: int,
    image_bytes: bytes,
    style_name: str,
    original_prompt: str,
    ai_prompt: str,
    revised_prompt: str,
    size: str,
    quality: str = "high",
    notes: str = "",
    image_model: str = "chatgpt-image-latest"
) -> Dict[str, Any]:
    """
    Guarda el cartel generado y su metadata en disco en la carpeta de proyectos.
    """
    ensure_output_directories()
    project_dir = os.path.join(OUTPUTS_DIR, "projects", project_id)
    os.makedirs(project_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_base = f"cartel_v{iteration}_{timestamp}"
    image_path = os.path.join(project_dir, f"{file_base}.png")
    meta_path = os.path.join(project_dir, f"{file_base}.json")

    # Guardar PNG
    with open(image_path, "wb") as f:
        f.write(image_bytes)

    # Metadatos del cartel
    metadata = {
        "project_id": project_id,
        "iteration": iteration,
        "timestamp": timestamp,
        "date_readable": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "style_name": style_name,
        "model_used": image_model,
        "user_prompt": original_prompt,
        "ai_engineered_prompt": ai_prompt,
        "image_revised_prompt": revised_prompt,
        "size": size,
        "quality": quality,
        "notes": notes,
        "image_file": os.path.basename(image_path)
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    metadata["image_path"] = image_path
    return metadata


def list_project_versions(project_id: str) -> List[Dict[str, Any]]:
    """
    Lista todas las versiones generadas de un proyecto ordenadas por iteración.
    """
    project_dir = os.path.join(OUTPUTS_DIR, "projects", project_id)
    if not os.path.exists(project_dir):
        return []

    versions = []
    for fname in os.listdir(project_dir):
        if fname.endswith(".json"):
            json_path = os.path.join(project_dir, fname)
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    img_path = os.path.join(project_dir, meta.get("image_file", ""))
                    if os.path.exists(img_path):
                        meta["image_path"] = img_path
                        versions.append(meta)
            except Exception:
                continue

    versions.sort(key=lambda x: x.get("iteration", 0))
    return versions


def list_all_projects() -> List[Dict[str, Any]]:
    """
    Lista todos los proyectos existentes con su versión más reciente.
    """
    ensure_output_directories()
    projects_dir = os.path.join(OUTPUTS_DIR, "projects")
    projects = []

    if not os.path.exists(projects_dir):
        return []

    for item in os.listdir(projects_dir):
        pdir = os.path.join(projects_dir, item)
        if os.path.isdir(pdir):
            versions = list_project_versions(item)
            if versions:
                latest = versions[-1]
                projects.append({
                    "project_id": item,
                    "versions_count": len(versions),
                    "latest_version": latest,
                    "created_at": versions[0].get("date_readable", ""),
                    "updated_at": latest.get("date_readable", "")
                })

    projects.sort(key=lambda x: x["updated_at"], reverse=True)
    return projects
