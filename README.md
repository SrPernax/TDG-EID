# Simulador de una red de distribución de paquetes

## Enlaces del Equipo
- [Informe Técnico](https://prism.openai.com/?u=c3691ad0-79cc-4f46-a467-34c15817ea70&pg=1&m=main.tex)
- [Tablero Jira](https://tdg-eid.atlassian.net/jira/software/projects/KAN/boards/2)

## Estructura del Proyecto
```text
TDG-EID/
├── src/
│   ├── config.py           # Constantes y cotas matemáticas del modelo
│   ├── exceptions.py       # Excepciones personalizadas del modelo y validadores
│   ├── models/
│   │   ├── vertex.py       # Clase Vertex (centro logístico v en V)
│   │   ├── edge.py         # Clase Edge (ruta dirigida e en E y capacidad)
│   │   └── graph.py        # Clase DirectedGraph y operaciones en vivo
│   ├── validators.py       # Validadores matemáticos del modelo y búsqueda de caminos
│   ├── presets.py          # Configuraciones de red y caso de comprobación manual
│   ├── max_flow.py         # Algoritmo de flujo máximo, corte mínimo y verificador
│   └── visualizer.py       # Renderizado visual del grafo con Graphviz (DOT)
├── app.py                  # Interfaz interactiva en Streamlit
├── requirements.txt        # Dependencias del proyecto
└── project.pdf             # Enunciado y rúbrica oficial
```

## Requisitos e Instalación
1. Crear y activar un entorno virtual de Python:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```
2. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución
Para iniciar la aplicación interactiva:
```bash
streamlit run app.py
```
