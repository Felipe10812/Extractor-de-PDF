# PDF Extractor Advanced - Guía de Uso

## 🎉 ¡Nueva Versión con Funcionalidades Avanzadas!

### Funcionalidades Principales

#### 1. **Carga de Archivos**
- **Interfaz mejorada**: Solo se muestra el nombre del archivo (no la ruta completa)
- **Barra de progreso**: Indica cuando se está cargando el PDF
- **Información detallada**: Muestra el número total de páginas del PDF

#### 2. **Previsualización Interactiva**
- **Vista en miniatura**: Cada página se muestra como imagen en miniatura
- **Botones de acción por página**:
  - 🔄 **Rotar**: Rota la página 90° en sentido horario
  - 🗑️ **Eliminar**: Elimina la página de la selección
- **Indicador de rotación**: Muestra el ángulo de rotación actual
- **Scroll horizontal**: Navega fácilmente por todas las páginas

#### 3. **Opciones de Exportación**

##### **PDF Único**
- Combina todas las páginas seleccionadas en un solo archivo PDF
- Mantiene las rotaciones aplicadas

##### **PDFs Individuales**
- Crea un archivo PDF separado para cada página
- Ideal para dividir documentos grandes

##### **Imágenes (ZIP)**
- Exporta las páginas como imágenes en un archivo ZIP
- Formatos disponibles: PNG, JPEG, TIFF
- Fácil distribución y almacenamiento

##### **Imágenes (Carpeta)**
- Guarda las imágenes directamente en una carpeta
- Nomenclatura automática: `archivo_pagina_001.png`

### 🚀 Cómo Usar la Aplicación

#### Paso 1: Cargar un PDF
1. Haz clic en **"Cargar PDF"**
2. Selecciona tu archivo PDF
3. Espera a que aparezca el nombre del archivo y el número de páginas

#### Paso 2: Seleccionar Páginas
1. En el campo **"Páginas"**, especifica qué páginas quieres extraer:
   - `1,3,5` - Páginas específicas
   - `1-5` - Rango de páginas
   - `1,3,5-7,10` - Combinación de específicas y rangos
   - Deja vacío para **todas las páginas**

#### Paso 3: Previsualizar
1. Haz clic en **"Previsualizar"**
2. Espera mientras se procesan las páginas
3. Ve a la pestaña **"Previsualización"** para ver las miniaturas

#### Paso 4: Editar Páginas (Opcional)
- **Rotar páginas**: Haz clic en 🔄 para rotar 90°
- **Eliminar páginas**: Haz clic en 🗑️ para remover de la selección

#### Paso 5: Exportar
1. Ve a la pestaña **"Exportación"**
2. Selecciona el **formato de exportación**:
   - PDF único
   - PDFs individuales  
   - Imágenes (ZIP)
   - Imágenes (Carpeta)
3. Si seleccionaste imágenes, elige el **formato** (PNG, JPEG, TIFF)
4. Haz clic en **"Seleccionar carpeta/archivo"** para elegir destino
5. Haz clic en **"Exportar"**
6. **Verás progreso detallado en DOS lugares**:
   - 📊 **Barra inline** en la interfaz principal
   - 💬 **Diálogo modal** que puedes cancelar
   - 🚀 Notificación de inicio
   - 💾 "Guardando archivo..." al final
   - ✅ "Guardada: archivo_001.png" para cada archivo
7. Al terminar, verás:
   - 🔔 **Notificación del sistema** confirmando que terminó
   - 💬 **Diálogo** con opción de abrir la carpeta de destino
   - 🏁 **Path de salida limpiado** automáticamente

### 💡 Consejos y Trucos

#### **Selección de Páginas**
- Para páginas no consecutivas: `1,3,7,9`
- Para rangos grandes: `10-50`
- Para combinaciones: `1-3,8,15-20`

#### **Rotación**
- Las rotaciones se aplican en incrementos de 90°
- Puedes rotar múltiples veces para lograr el ángulo deseado
- Las rotaciones se mantienen en la exportación

#### **Formatos de Imagen**
- **PNG**: Mejor calidad, archivos más grandes, sin pérdida
- **JPEG**: Menor tamaño, ideal para documentos con texto, compresión con pérdida
- **TIFF**: Máxima calidad, archivos muy grandes, formato profesional

#### **Calidad de Imagen Mejorada** 🎆
- **300 DPI**: Las imágenes exportadas tienen calidad de impresión profesional
- **Alta resolución**: Hasta 72x más píxeles que la previsualización
- **Optimización**: Compresión inteligente para equilibrar calidad y tamaño
- **Rotaciones preservadas**: Las rotaciones se aplican sin pérdida de calidad

#### **Exportación Eficiente**
- **ZIP** es más rápido que carpeta para muchas imágenes
- **PDFs individuales** son útiles para distribuir páginas por separado
- **PDF único** mantiene la calidad original

#### **Notificaciones**
- Las notificaciones aparecen en el área de notificaciones de Windows
- Puedes continuar usando otras aplicaciones mientras se procesa
- El diálogo final te permite abrir directamente la carpeta de destino
- Si hay errores, recibirás notificación inmediata

#### **Progreso Detallado** 🆕
- **Doble indicador**: Barra inline + Diálogo modal
- **Estado en tiempo real**: "Procesando página 3/10"
- **Guardado individual**: "Guardada: documento_pagina_003.png"
- **Finalización**: "Guardando archivo ZIP..." → "Completado"
- **Cancelación**: Botón "Cancelar" en el diálogo modal
- **Prevención de errores**: Path de salida se limpia automáticamente

#### **Protección contra Corrupción** ⚠️
- **Auto-limpiado**: El path se resetea entre exportaciones
- **Formatos seguros**: No se mezclan PDF y ZIP en el mismo path
- **Validación**: Verificación antes de sobrescribir archivos

### 🛠️ Funciones Técnicas

#### **Procesamiento en Segundo Plano**
- La carga y exportación no bloquean la interfaz
- Barras de progreso en tiempo real
- Posibilidad de cancelar operaciones largas

#### **Sistema de Notificaciones**
- **Notificaciones del sistema**: Se muestran en el área de notificaciones de Windows
- **Notificaciones de inicio**: Te avisan cuando comienza una operación
- **Notificaciones de finalización**: Te alertan cuando termina el guardado
- **Diálogo de completación**: Con opción para abrir la carpeta de destino
- **Notificaciones de error**: Te informan si algo sale mal

#### **Gestión de Memoria**
- Optimizado para PDFs grandes
- Renderizado eficiente de imágenes
- Liberación automática de recursos

#### **Compatibilidad**
- Funciona con cualquier PDF estándar
- No requiere instalaciones adicionales del sistema
- Compatible con Windows (probado en Windows 10/11)

#### **Interfaz**
- 🌙 **Tema oscuro**: Diseño moderno y cómodo para la vista
- 🎯 **Centrada automáticamente**: La ventana aparece en el centro de la pantalla
- **Responsive**: Se adapta a diferentes tamaños de ventana (800x600 mínimo)
- **Intuitiva**: Navegación por tabs organizada
- **Redimensionable**: Puedes ajustar el tamaño según tu preferencia

### 🔧 Resolución de Problemas

#### **El PDF no carga**
- Verifica que el archivo no esté corrupto
- Asegúrate de que tienes permisos de lectura
- Intenta con otro archivo PDF

#### **Las imágenes se ven pixeladas**
- Es normal en la previsualización (son miniaturas de 300px de ancho)
- ✅ **SOLUCIONADO**: La exportación ahora usa 300 DPI de alta calidad
- Las imágenes exportadas son hasta 72x más nítidas que el preview
- Para máxima calidad: PNG > TIFF > JPEG

#### **La aplicación se cuelga**
- Espera un momento, puede estar procesando
- Para PDFs muy grandes, el procesamiento toma tiempo
- Reinicia la aplicación si es necesario

### 📁 Estructura de Archivos Exportados

#### **PDF Único**
```
documento_extraído.pdf
```

#### **PDFs Individuales**
```
carpeta_destino/
├── documento_pagina_001.pdf
├── documento_pagina_003.pdf
└── documento_pagina_005.pdf
```

#### **Imágenes ZIP**
```
documento_imagenes.zip
├── documento_pagina_001.png
├── documento_pagina_003.png
└── documento_pagina_005.png
```

#### **Imágenes Carpeta**
```
carpeta_destino/
├── documento_pagina_001.png
├── documento_pagina_003.png
└── documento_pagina_005.png
```

---

## 🎯 Casos de Uso Comunes

### **Estudiante**
1. Cargar libro de texto PDF
2. Seleccionar solo los capítulos necesarios
3. Exportar como PDF único para estudio
4. O exportar como imágenes para presentaciones

### **Oficina**
1. Cargar reporte extenso
2. Extraer páginas específicas para cada departamento
3. Rotar páginas si están mal orientadas
4. Exportar PDFs individuales para distribución

### **Diseñador**
1. Cargar documento con imágenes
2. Extraer páginas con gráficos importantes
3. Exportar como imágenes de alta calidad
4. Usar en otros proyectos

---

¡Disfruta de tu nueva herramienta de extracción de PDF! 🚀
