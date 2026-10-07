"""
Catálogo de estilos artísticos para el generador de carteles.
Define descripciones, paletas de color y directivas visuales para cada estilo.
"""

STYLES_CATALOG = {
    "Bauhaus & Modernismo": {
        "icon": "📐",
        "category": "Diseño Gráfico Clásico",
        "description": "Formas geométricas puras, colores primarios, asimetría dinámica y tipografía sans-serif limpia inspirada en la escuela alemana de 1919.",
        "prompt_directives": (
            "Bauhaus poster art style. Geometric precision, primary colors (bold red, cobalt blue, cadmium yellow, deep black), "
            "asymmetrical dynamic layout, bold sans-serif modernist typography, abstract geometric constructivism, paper texture grain."
        )
    },
    "Retro Vintage (Años 70 & 80)": {
        "icon": "📻",
        "category": "Retro & Nostalgia",
        "description": "Estética publicitaria analógica de los 70 y 80, grano de película vintage, colores cálidos desgastados y tipografías retro redondeadas.",
        "prompt_directives": (
            "Vintage retro 1970s-1980s poster aesthetic. Warm faded color palette (mustard yellow, burnt orange, avocado green, sepia tones), "
            "film grain, subtle halftone print texture, nostalgic analog advertising poster, distressed paper finish, bold retro groove typography."
        )
    },
    "Cyberpunk & Neon Noir": {
        "icon": "⚡",
        "category": "Futurista & Ciencia Ficción",
        "description": "Luces de neón vibrantes, contrastes oscuros, lluvia, reflejos cromados y atmósfera futurista distópica.",
        "prompt_directives": (
            "Cyberpunk neon noir poster style. High contrast dark shadows, glowing holographic neon lighting (cyan, magenta, electric purple), "
            "rain-slicked reflective surfaces, futuristic mega-city dystopia, cinematic volumetric lighting, high tech aesthetic."
        )
    },
    "Art Déco": {
        "icon": "✨",
        "category": "Elegancia Clásica",
        "description": "Lujo ornamental de los años 1920, patrones geométricos dorados, simetría estilizada y glamour sofisticado.",
        "prompt_directives": (
            "1920s Art Deco luxury poster style. Symmetrical opulent geometric patterns, gold leaf accents, metallic brass and deep emerald or black tones, "
            "streamlined stylized forms, elegant Gatsby-era typography, sleek architectural decorative borders."
        )
    },
    "Minimalismo Suizo": {
        "icon": "🇨🇭",
        "category": "Diseño Editorial Moderno",
        "description": "Espacio negativo generoso, retícula estricta, tipografía suiza audaz (estilo Helvetica), orden y máximo impacto visual.",
        "prompt_directives": (
            "Swiss Style / International Typographic Style poster. Grid-based mathematical layout, generous negative space, bold asymmetric typography, "
            "minimalist color accent on monochrome background, high editorial clarity, crisp modernist graphic design."
        )
    },
    "Pop Art (Warhol / Lichtenstein)": {
        "icon": "💥",
        "category": "Arte Contemporáneo",
        "description": "Colores primarios supersaturados, tramas de puntos Ben-Day, trazos negros gruesos y estética de cómic vintage.",
        "prompt_directives": (
            "Pop Art graphic poster style in the spirit of Andy Warhol and Roy Lichtenstein. Ben-Day dots halftone shading, bold black comic ink outlines, "
            "vibrant saturated primary colors, screen-printing offset effects, energetic graphic novel aesthetic."
        )
    },
    "Acuarela Artística & Tinta": {
        "icon": "🎨",
        "category": "Pictórico & Orgánico",
        "description": "Manchas orgánicas de acuarela, salpicaduras fluidas de tinta, texturas de papel rugoso y bordes etéreos difuminados.",
        "prompt_directives": (
            "Artistic watercolor and sumi ink poster design. Fluid pigment blooms, organic watercolor splatters, soft bleeding edges, "
            "expressive brushstrokes, textured cold-press cotton paper, poetic atmosphere, elegant artistic composition."
        )
    },
    "Grabado Japonés (Ukiyo-e)": {
        "icon": "🌊",
        "category": "Tradicional & Oriental",
        "description": "Grabado xilográfico japonés tradicional al estilo Hokusai, líneas de contorno fluidas, paleta de tintas minerales y olas estilizadas.",
        "prompt_directives": (
            "Traditional Japanese Ukiyo-e woodblock print poster style. Delicate woodcut outlines, washi paper texture, mineral pigment colors (indigo blue, cinnabar red, cream), "
            "stylized decorative clouds and waves, Edo period aesthetic, traditional Japanese calligraphy accents."
        )
    },
    "Psicodélico de los 60s (Woodstock)": {
        "icon": "🌀",
        "category": "Contracultura & Psicodelia",
        "description": "Tipografía líquida y derretida, contrastes cromáticos vibrantes, curvas sinuosas Art Nouveau y patrones caleidoscópicos.",
        "prompt_directives": (
            "1960s psychedelic rock poster style. Liquid swirling typography, vibrant vibrating complementary colors, Art Nouveau organic curves, "
            "kaleidoscopic patterns, San Francisco Fillmore poster aesthetic, mesmerizing optical art elements."
        )
    },
    "Ilustración Vectorial Plana (Flat Vector)": {
        "icon": "✒️",
        "category": "Diseño Vectorial Contemporáneo",
        "description": "Diseño editorial contemporáneo, formas vectoriales limpias, degradados suaves, sombras sólidas y composición publicitaria moderna.",
        "prompt_directives": (
            "Modern flat vector illustration poster style. Clean sharp shapes, sophisticated contemporary color harmonies, subtle soft gradients, "
            "minimal drop shadows, modern travel or event poster layout, elegant digital graphic art."
        )
    },
    "Cine Noir & Alto Contraste": {
        "icon": "🎬",
        "category": "Cinematográfico",
        "description": "Dramatismo visual, sombras pronunciadas estilo claroscuro, estética de thriller clásico y atmósfera misteriosa en blanco y negro o monocromo.",
        "prompt_directives": (
            "Film Noir cinematic poster style. Dramatic low-key lighting, harsh chiaroscuro shadows, blinds Venetian shadow patterns, smoky atmospheric haze, "
            "monochromatic with single accent color, gritty mystery thriller aesthetic."
        )
    },
    "Render 3D Hipermoderno": {
        "icon": "💎",
        "category": "Digital 3D",
        "description": "Estética Cinema 4D / Octane Render, materiales traslúcidos de vidrio acrílico, arcilla mate o metales cromados, con iluminación de estudio.",
        "prompt_directives": (
            "Hypermodern 3D clay and frosted glass render poster. Studio lighting, soft ambient occlusion, glossy holographic and iridescent materials, "
            "translucent acrylic elements, vibrant clean backdrop, high-end 3D graphic design."
        )
    },
    "Personalizado": {
        "icon": "✏️",
        "category": "A medida",
        "description": "Escribe tus propias directivas y estilo artístico exacto.",
        "prompt_directives": ""
    }
}


def get_style_names():
    """Retorna la lista de nombres de estilos disponibles."""
    return list(STYLES_CATALOG.keys())


def get_style_info(style_name: str):
    """Retorna los datos del estilo seleccionado."""
    return STYLES_CATALOG.get(style_name, STYLES_CATALOG["Bauhaus & Modernismo"])
