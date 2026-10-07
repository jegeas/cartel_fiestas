# 🎨 AI Poster Studio | Generador & Editor de Carteles con OpenAI

Aplicación profesional en Python con **Streamlit** y la **API de OpenAI** para la creación y edición iterativa de carteles publicitarios y artísticos.

---

## 🌟 Características Principales

1. **Subida de Imagen Base / Temática**: Sube cualquier foto que quieras que sirva de inspiración o sujeto del cartel.
2. **Catálogo de Estilos Artísticos**:
   - 📐 Bauhaus & Modernismo
   - 📻 Retro Vintage (Años 70 & 80)
   - ⚡ Cyberpunk & Neon Noir
   - ✨ Art Déco
   - 🇨🇭 Minimalismo Suizo
   - 💥 Pop Art (Warhol / Lichtenstein)
   - 🎨 Acuarela Artística & Tinta
   - 🌊 Grabado Japonés (Ukiyo-e)
   - 🌀 Psicodélico de los 60s
   - ✒️ Ilustración Vectorial Plana
   - 🎬 Cine Noir
   - 💎 Render 3D Hipermoderno
   - ✏️ Estilo Personalizado
3. **Soporte para ChatGPT Image 2.1**: Integra por defecto el modelo de generación de imagen `gpt-image-2.1` / `chatgpt-image-2.1`, con soporte alternativo para `gpt-image-2`, `gpt-image-2.5-sunburst`, `dall-e-3` o modelos personalizados, además de endpoints personalizados (Base URL).
4. **Director Creativo con Visión (GPT-4o)**: Analiza la imagen temática y las fotos de referencia, extrayendo composición, paleta cromática y sujetos para redactar las instrucciones precisas para el modelo de imagen.
5. **Edición Iterativa con Referencias Múltiples**:
   - Sobre cualquier cartel generado, puedes subir **1 o varias fotos de referencia adicionales** (ej: un personaje, un logo, un accesorio o un fondo secundario).
   - Escribes instrucciones de qué sumar o modificar.
   - El sistema analiza el cartel original + las fotos nuevas y genera una nueva versión (**v2, v3...**) manteniendo la coherencia y el estilo.
6. **Historial, Comparativa & Descargas**:
   - Comparativa lado a lado (Antes vs Después).
   - Descarga directa en alta resolución (PNG).
   - Guardado automático local de cada versión con metadatos completos en `outputs/projects/`.

---

## 🚀 Cómo Iniciar la Aplicación

### 1. Configurar la clave de OpenAI
Puedes crear un archivo `.env` en la raíz de la carpeta `c:\Cartel` con tu clave:
```env
OPENAI_API_KEY=tu_clave_de_openai_aqui
```
*(También puedes introducirla directamente en la barra lateral de la aplicación web).*

### 2. Ejecutar la Aplicación
Abre una terminal en esta carpeta y ejecuta:
```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador web en `http://localhost:8501`.

---

## 📁 Estructura del Proyecto

- `app.py`: Interfaz visual en Streamlit con pestañas de creación, edición y galería.
- `poster_generator.py`: Motor de integración con OpenAI (GPT-4o Vision + DALL-E 3, guardado de proyectos y gestión de versiones).
- `styles.py`: Catálogo de estilos artísticos y directivas de diseño.
- `outputs/`: Directorio donde se guardan automáticamente las versiones en PNG y JSON de cada proyecto.
- `requirements.txt`: Lista de dependencias del proyecto.
