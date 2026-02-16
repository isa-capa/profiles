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

