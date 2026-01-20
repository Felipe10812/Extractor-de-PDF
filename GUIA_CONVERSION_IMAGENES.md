# Guía de Conversión de Imágenes a PDF

Esta guía detalla cómo usar la nueva funcionalidad de conversión de imágenes a PDF en **PDF & Image Converter**.

## 🚀 Introducción

La aplicación ahora incluye un modo dual que permite tanto la extracción de páginas de PDF como la conversión de múltiples imágenes en un PDF profesional. Esta nueva funcionalidad es ideal para:

- Convertir fotografías en documentos PDF organizados
- Crear presentaciones PDF a partir de imágenes
- Digitalizar documentos escaneados como imágenes en un PDF único
- Combinar imágenes de diferentes formatos en un documento unificado

## 📋 Formatos de Imagen Soportados

La aplicación puede procesar los siguientes formatos de imagen:

- **PNG**: Incluye manejo automático de transparencias
- **JPEG/JPG**: Formato comprimido estándar
- **BMP**: Mapas de bits sin compresión
- **TIFF**: Formato para imágenes de alta calidad
- **WebP**: Formato moderno de Google

> **Nota**: Las imágenes con transparencias (PNG con canal alfa) se convierten automáticamente con fondo blanco para garantizar compatibilidad con PDF.

## 🔄 Cambio de Modo

### Selector de Modo
En la parte superior de la aplicación encontrarás un selector de modo con dos opciones:

- **📄 Extraer de PDF**: Modo tradicional para trabajar con documentos PDF
- **🖼️ Convertir imágenes a PDF**: Nuevo modo para conversión de imágenes

### Cambiar entre Modos
1. Haz clic en el modo deseado en la barra de selector
2. La interfaz se actualizará automáticamente
3. Se reiniciará el estado de la aplicación para evitar conflictos

## 📁 Cargando Imágenes

### Proceso de Carga
1. **Selecciona el modo "Convertir imágenes a PDF"**
2. **Haz clic en "Cargar imágenes"**
3. **Selecciona múltiples archivos**: El diálogo permite selección múltiple
4. **Confirma la selección**: La aplicación procesará y validará las imágenes

### Información Mostrada
Una vez cargadas las imágenes, verás:
- Número total de imágenes seleccionadas
- Cantidad de imágenes válidas procesadas
- Mensaje de estado con información detallada

### Ejemplo de Carga
```
Imágenes cargadas: 4 válidas de 5 seleccionadas
```

## 🔍 Previsualización de Imágenes

### Acceso a la Previsualización
1. **Después de cargar las imágenes**, haz clic en "Previsualizar"
2. **Especifica imágenes** (opcional): Usa números separados por comas (ej: 1,3,5) o rangos (ej: 1-4)
3. **Deja vacío para incluir todas**: Si no especificas nada, se incluirán todas las imágenes válidas

### Interacción con Miniaturas
En la pestaña de "Previsualización" puedes:

- **Ver miniaturas**: Cada imagen se muestra como una miniatura numerada
- **Seleccionar/Deseleccionar**: Haz clic en cualquier miniatura para incluirla o excluirla
- **Rotar imágenes**: Usa el botón de rotación en cada miniatura
- **Eliminar imágenes**: Usa el botón X para quitar imágenes de la selección

### Estados de las Miniaturas
- **Borde azul**: Imagen seleccionada (se incluirá en el PDF)
- **Borde gris**: Imagen deseleccionada (no se incluirá)
- **Número en esquina**: Indica el orden/posición de la imagen original

## ⚙️ Configuración de Conversión

### Acceso a Opciones
1. Ve a la pestaña "Exportación"
2. Con imágenes cargadas, verás opciones específicas para conversión a PDF

### Opciones Disponibles

#### 📏 Tamaño de Página
- **A4**: Estándar internacional (210 × 297 mm)
- **Carta (Letter)**: Estándar estadounidense (216 × 279 mm)  
- **Legal**: Formato legal (216 × 356 mm)
- **A3**: Formato grande (297 × 420 mm)
- **A5**: Formato pequeño (148 × 210 mm)

#### 🔄 Orientación
- **Vertical (Portrait)**: Altura mayor que ancho
- **Horizontal (Landscape)**: Ancho mayor que altura

#### 🎯 Modo de Ajuste

##### Ajustar (mantener proporción) - **Recomendado**
- Mantiene las proporciones originales de la imagen
- Centra la imagen en la página
- Puede dejar espacios en blanco si la proporción no coincide
- **Ideal para**: Fotografías y documentos donde la proporción es importante

##### Llenar página (recortar si es necesario)
- Escala la imagen para llenar completamente la página
- Mantiene proporciones pero puede recortar partes de la imagen
- No deja espacios en blanco
- **Ideal para**: Fondos e imágenes donde el recorte es aceptable

##### Estirar (puede deformar)
- Estira la imagen para ocupar toda la página exactamente
- No mantiene las proporciones originales
- Puede causar distorsión visual
- **Ideal para**: Casos específicos donde el ajuste exacto es necesario

### Configuración Recomendada
Para la mayoría de casos, se recomienda:
```
Tamaño: A4
Orientación: Vertical
Ajuste: Ajustar (mantener proporción)
```

## 📤 Formatos de Exportación

### Opciones en Modo Imágenes
Cuando trabajas con imágenes, tienes las siguientes opciones de exportación:

#### 🔹 Convertir a PDF único (Principal)
- Convierte todas las imágenes seleccionadas en un solo PDF
- Usa las configuraciones de página, orientación y ajuste especificadas
- Cada imagen se convierte en una página del PDF
- **Archivo resultante**: Un solo PDF con múltiples páginas

#### 🔹 PDFs individuales en ZIP
- Convierte cada imagen seleccionada en un PDF separado
- Comprime todos los PDFs en un archivo ZIP
- Aplica las configuraciones de página, orientación y ajuste a cada PDF
- **Archivo resultante**: Un ZIP con múltiples archivos PDF individuales

#### 🔹 PDFs individuales en carpeta
- Convierte cada imagen seleccionada en un PDF separado
- Guarda todos los PDFs en una carpeta
- Aplica las configuraciones de página, orientación y ajuste a cada PDF
- **Resultado**: Carpeta con múltiples archivos PDF individuales

## 💡 Flujo de Trabajo Completo

### Ejemplo Paso a Paso
1. **Cambiar a modo imágenes**
   - Selecciona "Convertir imágenes a PDF" en la barra superior

2. **Cargar imágenes**
   - Haz clic en "Cargar imágenes"
   - Selecciona todos los archivos deseados (puedes seleccionar múltiples)
   - Confirma la selección

3. **Previsualizar y organizar**
   - Haz clic en "Previsualizar"
   - Revisa las miniaturas en la pestaña "Previsualización"
   - Deselecciona imágenes no deseadas
   - Rota imágenes si es necesario

4. **Configurar conversión**
   - Ve a la pestaña "Exportación"
   - Selecciona "Convertir a PDF único"
   - Configura tamaño de página (ej: A4)
   - Elige orientación (ej: Vertical)
   - Selecciona modo de ajuste (ej: Ajustar)

5. **Exportar**
   - Haz clic en el ícono de carpeta para seleccionar destino
   - Elige nombre y ubicación del PDF
   - Haz clic en "Exportar"

6. **Seguir progreso**
   - Observa la barra de progreso inline
   - Recibe notificaciones del sistema
   - Al completar, se ofrece abrir la carpeta destino

## 📊 Indicadores de Progreso

### Durante la Conversión
La aplicación muestra progreso detallado:

```
Progreso: 2/4 - Procesando imagen 3
Progreso: 4/4 - Guardando PDF...
Progreso: 4/4 - Completado
```

### Notificaciones del Sistema
Recibirás notificaciones nativas de Windows:
- **Al iniciar**: "Procesando todas las imágenes"
- **Al completar**: "Conversión completada" con opción de abrir carpeta
- **En caso de error**: Descripción del problema

## 🎛️ Configuración Avanzada

### Calidad de Imagen
- Las imágenes se procesan en su resolución original para exportación
- Se optimiza la calidad JPEG al 90% para balance entre calidad y tamaño
- Las imágenes PNG mantienen su calidad sin pérdida

### Manejo de Transparencias
- Imágenes PNG con transparencia obtienen fondo blanco automáticamente
- Imágenes con paleta de colores se convierten a RGB
- Se garantiza compatibilidad completa con formato PDF

### Límites y Recomendaciones
- **Número de imágenes**: Sin límite teórico, pero se recomienda < 100 para rendimiento óptimo
- **Tamaño de archivos**: Imágenes muy grandes (>50MB) pueden requerir más tiempo de procesamiento
- **Memoria**: El procesamiento se realiza imagen por imagen para optimizar el uso de memoria

## 🔧 Solución de Problemas

### Imágenes No Se Cargan
**Problema**: Algunas imágenes aparecen como "ERROR"
**Soluciones**:
- Verifica que el formato sea compatible
- Confirma que el archivo no esté corrupto
- Intenta abrir la imagen en otro programa primero

### PDF No Se Genera
**Problema**: La conversión falla o el PDF está vacío
**Soluciones**:
- Asegúrate de tener al menos una imagen seleccionada
- Verifica permisos de escritura en la carpeta destino
- Comprueba espacio disponible en disco

### Calidad Insatisfactoria
**Problema**: Las imágenes se ven pixeladas o distorsionadas en el PDF
**Soluciones**:
- Usa imágenes de mayor resolución como fuente
- Cambia el modo de ajuste a "Ajustar (mantener proporción)"
- Considera usar un tamaño de página más apropiado

### Rendimiento Lento
**Problema**: El procesamiento toma mucho tiempo
**Soluciones**:
- Reduce el número de imágenes procesadas simultáneamente
- Usa imágenes de menor resolución si la calidad lo permite
- Cierra otras aplicaciones para liberar memoria

## 📝 Tips y Mejores Prácticas

### Para Mejores Resultados
1. **Usa imágenes de resolución similar** para consistencia visual
2. **Ordena las imágenes por nombre** antes de cargarlas para mantener secuencia lógica
3. **Revisa la previsualización** antes de convertir para evitar sorpresas
4. **Usa "Ajustar"** como modo de ajuste predeterminado para preservar calidad

### Casos de Uso Comunes
- **Documentos escaneados**: A4 vertical, ajustar proporción
- **Fotografías**: Orientación según contenido, ajustar proporción
- **Presentaciones**: A4 horizontal, llenar página si es apropiado
- **Archivos técnicos**: Tamaño apropiado para el contenido, mantener proporción

### Organización de Archivos
- Usa nombres descriptivos para los PDFs generados
- Considera crear carpetas separadas para diferentes proyectos
- Mantén las imágenes originales como respaldo

## 🆘 Soporte

Si encuentras problemas o necesitas asistencia adicional, puedes:

1. **Revisar esta guía** para soluciones comunes
2. **Ejecutar el script de prueba** (`test_image_conversion.py`) para verificar funcionalidad
3. **Revisar los logs** en la consola para mensajes de error detallados
4. **Contactar al desarrollador** a través de GitHub

---

**¡Disfruta convirtiendo tus imágenes en PDFs profesionales!** 📄✨
