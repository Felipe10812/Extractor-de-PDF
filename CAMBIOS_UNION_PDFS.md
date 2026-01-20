# Funcionalidad de Unión de Múltiples PDFs

## Resumen
Se ha agregado exitosamente la funcionalidad para unir múltiples archivos PDF en uno solo, con opciones avanzadas de previsualización y organización.

## Nuevas Características

### 1. Modo "Unir PDFs"
- Nuevo modo junto a "Extraer de PDF" y "Convertir imágenes a PDF"
- Permite seleccionar múltiples archivos PDF para unirlos
- Muestra información detallada: cantidad de archivos y páginas totales

### 2. Vistas de Organización
La previsualización ahora soporta dos modos de vista:

#### Vista "Por hojas"
- Muestra todas las páginas en secuencia lineal
- Ideal para ver el orden final del documento

#### Vista "Por archivo"
- Agrupa páginas por su archivo PDF origen
- Cada grupo muestra:
  - Icono y nombre del archivo
  - Número de páginas del archivo
  - Miniaturas de todas las páginas
- Facilita identificar de dónde viene cada página

### 3. Metadata de Origen
Cada página ahora incluye:
- Nombre del archivo PDF de origen
- Índice del PDF en la lista
- Número de página original dentro del PDF
- Esta información se muestra en la vista "Por hojas"

### 4. Capacidades de Exportación
En modo "Unir PDFs":
- **PDF único unificado**: Combina todas las páginas seleccionadas en un solo archivo
- **Imágenes (ZIP)**: Exporta las páginas como imágenes en formato PNG, JPEG o TIFF
- **Imágenes (Carpeta)**: Exporta las imágenes en una carpeta individual

## Archivos Modificados

### Archivos Nuevos
- `services/pdf_merger_service.py` - Servicio para manejar múltiples PDFs

### Archivos Modificados
- `app.py` - Agregado modo merge_pdfs y lógica de carga múltiple
- `services/page_manager.py` - Extendido con metadata de origen
- `ui/interactive_preview.py` - Agregadas vistas de organización
- `ui/export_options.py` - Adaptadas opciones para modo merge

## Uso

1. **Seleccionar modo**: Hacer clic en "Unir PDFs" en el selector de modo

2. **Cargar archivos**: Hacer clic en "Cargar PDFs" y seleccionar múltiples archivos PDF

3. **Vista de archivos cargados**: 
   ```
   3 archivos PDF seleccionados
   3 PDFs cargados: 45 páginas totales
   ```

4. **Previsualizar**: Hacer clic en "Previsualizar" para ver todas las páginas
   - Usar el toggle "Por hojas" / "Por archivo" para cambiar la vista
   - Rotar páginas individuales con el botón de rotación
   - Eliminar páginas no deseadas con el botón de eliminar

5. **Exportar**: 
   - Ir a la pestaña "Exportación"
   - Seleccionar formato (PDF único o imágenes)
   - Elegir ubicación de salida
   - Hacer clic en "Exportar"

## Flujo de Trabajo Típico

```
Usuario → Selecciona "Unir PDFs"
       → Carga 3 PDFs (doc1.pdf, doc2.pdf, doc3.pdf)
       → Sistema muestra: "3 PDFs cargados: 45 páginas totales"
       → Usuario hace clic en "Previsualizar"
       → Ve todas las páginas en vista "Por archivo":
          📄 doc1.pdf (15 páginas)
          📄 doc2.pdf (20 páginas)  
          📄 doc3.pdf (10 páginas)
       → Cambia a vista "Por hojas" para ver orden final
       → Rota página 5, elimina página 12
       → Va a pestaña "Exportación"
       → Selecciona "PDF único unificado"
       → Elige ubicación y nombre
       → Exporta exitosamente
```

## Ventajas

- **Flexibilidad**: Organización visual por archivo o por página
- **Control total**: Rotar y eliminar páginas individuales
- **Eficiencia**: Procesamiento en segundo plano con indicadores de progreso
- **Calidad**: Renderizado a 300 DPI para exportación profesional
- **Trazabilidad**: Cada página muestra su archivo de origen

## Compatibilidad

- Compatible con todos los formatos PDF estándar
- Funciona con los modos existentes sin conflictos
- Mantiene la arquitectura modular del proyecto
