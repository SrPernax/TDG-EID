# Simulador de una Red de Distribución de Paquetes

Proyecto práctico final para la asignatura **Teoría de Grafos (INFO1158)**. Implementación propia del algoritmo de **Edmonds–Karp** (flujo máximo), identificación de **corte mínimo $(S, T)$**, verificación matemática de optimalidad y simulación interactiva de contingencias logísticas.

**Integrantes:** Ignacio Loncón Pérez · Lukas Macalusso Trillat · Nicolás Cayuman Hernández

## Documentación y Gestión
- [Informe Técnico (PDF)](report/Informe_tecnico.pdf)
- [Enunciado y Rúbrica Oficial (PDF)](report/project.pdf)
- [Tablero Jira](https://tdg-eid.atlassian.net/jira/software/projects/KAN/boards/2)

## Especificaciones Técnicas y Dependencias
- **Python:** `>= 3.10`
- **Núcleo algorítmico:** Implementado íntegramente con estructuras nativas de Python (`dict`, `list`, `set`, `collections.deque`), sin bibliotecas externas de cálculo sobre grafos.
- **Dependencias de interfaz y visualización (`requirements.txt`):**
  - `streamlit >= 1.46.0` — Interfaz interactiva y paneles de simulación.
  - `graphviz >= 0.20.0` — Generación del grafo dirigido en notación DOT (renderizado en navegador vía WebAssembly por Streamlit, sin requerir binarios externos del sistema).

## Estructura del Proyecto
```text
TDG-EID/
├── .streamlit/
│   └── config.toml         # Configuración de tema visual (modo oscuro)
├── report/
│   ├── Informe_tecnico.pdf # Informe técnico final del proyecto
│   └── project.pdf         # Enunciado y rúbrica oficial
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py       # Constantes y cotas matemáticas del modelo
│   │   ├── exceptions.py   # Jerarquía de excepciones personalizadas
│   │   └── validators.py   # Validadores matemáticos, cotas y conectividad
│   ├── models/
│   │   ├── __init__.py
│   │   ├── vertex.py       # Clase Vertex (centro logístico v en V)
│   │   ├── edge.py         # Clase Edge (ruta dirigida e en E y capacidad)
│   │   └── graph.py        # Clase DirectedGraph y operaciones en vivo
│   ├── algorithms/
│   │   ├── __init__.py
│   │   └── max_flow.py     # Edmonds-Karp, corte mínimo y verificador de optimalidad
│   ├── data/
│   │   ├── __init__.py
│   │   └── presets.py      # Configuraciones de red y caso de comprobación manual
│   └── ui/
│       ├── __init__.py
│       └── visualizer.py   # Generación visual del grafo con Graphviz (DOT)
├── app.py                  # Aplicación interactiva principal en Streamlit
└── requirements.txt        # Dependencias de Python
```

## Instalación y Ejecución

1. Clonar el repositorio e ingresar al directorio:
   ```bash
   git clone https://github.com/SrPernax/TDG-EID.git
   cd TDG-EID
   ```

2. Crear y activar un entorno virtual de Python (`>= 3.10`):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```

3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecutar el simulador interactivo:
   ```bash
   streamlit run app.py
   ```
