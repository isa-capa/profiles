# 🧭 Match Viajero ↔ Guía
### Perfilador Inteligente para Matching de Experiencias

---

## 📌 Descripción

**Match Viajero ↔ Guía** es una aplicación web diseñada para crear perfiles estructurados de **Turistas (Viajeros)** y **Guías**, con el objetivo de recopilar información relevante que permita generar un *match perfecto* entre ambos.

El sistema utiliza formularios progresivos y validaciones dinámicas para construir objetos JSON que representan perfiles completos, listos para ser procesados por un sistema de recomendación.

---

## 🎯 Objetivo del Proyecto

El objetivo principal de este perfilador es:

- Crear perfiles detallados de **Turistas** y **Guías**.
- Estandarizar la información en formato JSON.
- Preparar los datos para un sistema de matching inteligente.
- Validar información en el frontend sin recargar la página.
- Generar una experiencia visual clara, limpia y responsiva.

---

## 👥 Tipos de Perfil

### 🧳 Turista

El perfil de Turista incluye:

1. Intereses
2. Estilo de viaje
   - Tipo de viaje
   - Idiomas
3. Ritmo y compañía
   - Nivel de actividad
   - Preferencia de grupo
4. Comida y planeación
   - Preferencias alimenticias
   - Nivel de planificación
5. Comodidades
   - Transporte
   - Preferencia de fotos
6. Necesidades y logística
   - Accesibilidad
   - Notas adicionales

---

### 🧭 Guía

El perfil de Guía incluye:

1. Áreas de experiencia
2. Ubicaciones
3. Experiencia e idiomas
   - Nivel de experiencia
   - Idiomas
4. Estilo de guía
   - Estilo
   - Tamaño de grupo
5. Ritmo y logística
   - Intensidad del tour
   - Transporte ofrecido
6. Seguridad y accesibilidad
   - Certificaciones
   - Adaptaciones
7. Detalles finales
   - Estilo con fotos
   - Notas adicionales

---



## 🏗️ Tecnologías Utilizadas

- HTML5
- CSS3 (Diseño responsivo)
- JavaScript (Vanilla JS)
- Arquitectura basada en clases (ProfilesController)
- Validación dinámica en frontend
- LocalStorage (persistencia temporal)


---

## ⚙️ Funcionalidades Implementadas

- ✅ Creación de perfiles con validación dinámica
- ✅ Errores mostrados como tarjetas (sin alertas emergentes)
- ✅ Cambio automático entre perfil Turista y Guía
- ✅ Generación de objeto JSON estructurado
- ✅ Sistema modular con controlador de perfiles
- ✅ Diseño responsivo

---

## 🚀 Próximas Mejoras

- Algoritmo de scoring de compatibilidad
- Ranking automático de coincidencias
- Sistema de favoritos
- Conexión con backend / base de datos
- Dashboard de matches sugeridos
- Integración con mapas y disponibilidad

---

## 🧠 Futuro del Proyecto: Matching Inteligente

Este perfilador es la base de un sistema más avanzado que tendrá como finalidad:

- Analizar compatibilidad entre Turistas y Guías.
- Generar recomendaciones personalizadas.
- Optimizar experiencias de viaje.
- Aumentar la satisfacción y seguridad de ambos perfiles.

El algoritmo de matching estará basado en un **estudio propio** que realizamos sobre compatibilidad de experiencia, expectativas, ritmo, intereses y logística.

📄 Puedes consultar el estudio completo aquí:
👉 **[https://drive.google.com/file/d/1HRoivtYmzMpvEKDGXajMlrmqS3sV8rck/view?usp=sharing]**

## 🤖 Algoritmo de Match (Python)

Se agregó una primera versión en `ml/guide_tourist_match.py` con:

- Scoring ponderado por parámetros (intereses, idiomas, ubicación, estilo, logística, etc.).
- Umbral configurable de match (por defecto 90%).
- Ranking tipo swipe/descubrimiento para listar guías por compatibilidad.
- Base preparada para etapa 2 con machine learning (`MLMatcherAdapter`).

Ejecuta un ejemplo rápido:

```bash
python ml/guide_tourist_match.py
```

## 🤝 Todas las contribución son bienvenidas

---

## 📦 Ejemplo de Objeto Generado

```json
{
  "id": 1,
  "role": "traveler",
  "answers": {
    "interests": ["Cultura", "Historia"],
    "languages": ["Español", "Inglés"]
  },
  "createdAt": "2026-02-16T02:18:38.614Z"
}


```

## Future Learning Layer

This section describes a possible evolution path for the matching engine without implementing it yet:

- Capture explicit feedback events per Traveler-Guide pair:
  - `like` / `dislike`
  - booking started
  - booking completed
- Store feedback with context features used at match time:
  - profile snapshot hash
  - dimension breakdown scores
  - final selected guide
- Use feedback to adjust weights dynamically:
  - increase weights for dimensions correlated with successful bookings
  - reduce weights for dimensions correlated with rejections
  - keep hard constraints for safety and business rules
- Introduce a supervised learning stage once enough labeled data exists:
  - features: current rule-based breakdown + profile-derived metadata
  - label: successful booking or positive post-experience rating
  - train/validate offline, then deploy as a re-ranker over the rule-based score
- Keep explainability:
  - preserve per-dimension breakdown in production responses
  - expose top reasons for recommendation to product surfaces
