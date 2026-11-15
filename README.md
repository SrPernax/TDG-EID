# Proyecto 2: Simulador de una red de distribución de paquetes (INFO1158)

## Enlaces del Equipo
- [Informe Técnico](https://prism.openai.com/?u=c3691ad0-79cc-4f46-a467-34c15817ea70&pg=1&m=main.tex)
- [Tablero Jira](https://tdg-eid.atlassian.net/jira/software/projects/KAN/boards/2)

## Estructura del Proyecto
```text
TDG-EID/
├── src/
│   ├── __init__.py
│   ├── graph_model.py      # Modelo del grafo, validaciones y modificaciones
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
