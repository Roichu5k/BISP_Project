# BISP: Roadmap de Implementación (Sprints & Fases)

Versión 1.0 · 2026

Este documento detalla el plan de acción para construir la **Business
Intelligence Scraper Platform (BISP)** bajo la arquitectura "Zero-Cost &
Euro-Centric".

La filosofía de desarrollo es **Iterativa e Incremental**: cada Fase termina con
un producto funcional que aporta valor por sí mismo, antes de pasar a añadir
complejidad en la siguiente fase.

---

## FASE 1: Fundación y MVP (Minimum Viable Product)

**Objetivo:** Construir el "esqueleto" del sistema, conectarlo a una fuente de
datos gratuita fiable y visualizar los fundamentales básicos de un grupo
reducido de empresas de prueba (ej. IBEX 35 o Euro Stoxx 50).

### Sprint 1: Setup de Infraestructura Local y Base de Datos (1 Semana)

- [ ] Inicializar el repositorio (Python, FastAPI, entorno virtual,
      dependencias).
- [ ] Levantar **PostgreSQL** (con `TimescaleDB` y `pgvector`) usando Docker
      Compose.
- [ ] Levantar **Redis** (para la caché y futura cola de tareas) usando Docker
      Compose.
- [ ] Diseñar el esquema SQL inicial (Tablas: `companies`, `financials_annual`,
      `financials_quarterly`, `price_history`).
- [ ] Crear un script básico para poblar la tabla `companies` con una lista
      estática (ej. 50 tickers europeos y 50 americanos).

### Sprint 2: Ingesta de Datos Estructurados Core (1-2 Semanas)

- [ ] Desarrollar los parsers de ingesta usando la librería **`yfinance`**.
- [ ] Script para descargar y guardar Precios Históricos (OHLCV) en
      `TimescaleDB`.
- [ ] Script para descargar y guardar Estados Financieros (Income Statement,
      Balance Sheet, Cash Flow).
- [ ] Abordar el problema Multi-Divisa: Crear una tabla de Forex y normalizar
      todos los financieros a una divisa base (ej. EUR o USD).
- [ ] Implementar **DuckDB/Polars** para realizar limpiezas rápidas en estos
      datos antes del insert a Postgres.

### Sprint 3: Ratios, Valoración Trivial y API Básica (1 Semana)

- [ ] Endpoints **FastAPI**: crear rutas REST para servir los datos básicos
      (`/companies/{ticker}`, `/financials/{ticker}`).
- [ ] Motor de Ratios (Python): Calcular dinámicamente márgenes, ROIC
      simplificado, EV/EBITDA y Deuda Neta usando los datos almacenados.
- [ ] UI Básica: Crear un frontend estático muy de "guerrilla" (HTML/JS simple o
      un panel rápido en Streamlit/Gradio) solo para comprobar que los datos
      fluyen.

---

## FASE 2: Expansión de Fuentes y Adaptación Europea

**Objetivo:** Mejorar la resiliencia del sistema ante la fragmentación de cómo
reportan las empresas europeas y añadir fuentes robustas corporativas más allá
de Yahoo.

### Sprint 4: Scraping Dinámico y Registros Europeos (2 Semanas)

- [ ] Configurar **Playwright + Stealth** para evasión de bloqueos básica.
- [ ] Desarrollar scraper para **Companies House (UK)** usando su API gratuita
      para nutrir datos de empresas británicas.
- [ ] Desarrollar parser para la web de la **CNMV (España)** (Buscar "Otra
      Información Relevante").
- [ ] Adaptar la base de datos a los "Periodos Incompletos" europeos (Soporte
      nativo para informes semestrales H1/H2 sin romper los cálculos
      trimestrales).

### Sprint 5: Orquestación, Jobs Automatizados y MinIO (2 Semanas)

- [ ] Levantar y configurar de **MinIO** en Docker (nuestro "S3" local
      gratuito).
- [ ] Implementar **Celery / Prefect** para automatizar la extracción.
- [ ] Crear "Jobs/Cron" diarios (Actualizar cotizaciones al cierre del mercado).
- [ ] Crear "Jobs" de fin de semana (Actualizar fundamentales extensos y
      rastrear nuevas empresas).

---

## FASE 3: La Capa de Inteligencia Artificial (Zero-Cost AI)

**Objetivo:** Darle "cerebro" a la plataforma usando Modelos de Lenguaje Locales
(LLM) y técnicas de embeddings para analizar el texto, no solo los números.

### Sprint 6: Inferencia Local y Traducción Universal (2 Semanas)

- [ ] Instalar y enlazar **Ollama** con el backend de Python.
- [ ] Descargar y probar modelos multilingües (ej. Qwen 2.5 7B o Llama 3 8B).
- [ ] Módulo de "Lectura de Earnings Calls": Scrapear o conseguir
      transcripciones de llamadas de resultados, pasárselas al LLM y extraer:
      "Tono del CEO", "Guidance para el año que viene", "Riesgos mencionados".
- [ ] Módulo Traductor: Mapear para que el sistema le pase un informe en alemán
      o francés al LLM y nos extraiga las conclusiones en nuestro idioma base.

### Sprint 7: Búsqueda Semántica y Peer Groups (1-2 Semanas)

- [ ] Generar **Embeddings** de las descripciones y modelos de negocio de todas
      las empresas usando la librería `sentence-transformers` (ej. BGE-m3).
- [ ] Guardar estos vectores en **PostgreSQL (`pgvector`)**.
- [ ] Crear el endpoint: "Buscar competidores" -> Usando similitud cosenoidal
      matemática entre los vectores, para que la app agrupe automáticamente
      competidores de toda Europa (sin depender de clasificaciones sectoriales
      rígidas).

### Sprint 8: Scraping en PDF (Informes Complejos y ESEF) (2 Semanas)

- [ ] Crear el pipeline de "Data Lake RAW": Descarga automática de los extensos
      archivos PDF (Memorias Anuales) directos de las webs de '_Relación con
      Inversores_'. Guárdalos en MinIO.
- [ ] Parseo de texto (usando `pdfplumber` o `PyMuPDF`) y extracción de bloques
      clave (ej. sección de Litigios o sección Medioambiental ESG).
- [ ] Pasar esos bloques críticos por el LLM local para obtener un "Summary"
      accionable que se guarda en Postgres.

---

## FASE 4: Refinamiento, Calidad (Moats) y Frontend

**Objetivo:** Ensamblar todas las métricas complejas, estabilizar la plataforma
y construir el Dashboard definitivo que impresione visualmente.

### Sprint 9: Motor Avanzado de Valoración y Scorings (2 Semanas)

- [ ] Implementar el **MOAT Score Engine**: Algoritmo que mezcla los datos duros
      (márgenes consistentes, ROIC alto sobre WACC) con conclusiones del LLM
      ("barreras de entrada", "poder de marca detectado en textos").
- [ ] Implementar Modelos Teóricos Deterministas: **Piotroski F-Score** (0-9)
      para calidad contable y **Beneish M-Score** (manipulación de cuentas).
- [ ] Modelado de Vencimientos de Deuda (Extraído vía LLM de los informes
      anuales).

### Sprint 10: Inteligencia de Noticias (1 Semana)

- [ ] Conectar RSS gratuitos financieros o usar Scrapy para portales de nicho.
- [ ] Usar la **Groq API** (Free Tier - ultra rápido) o el LLM local para
      clasificar cada noticia: `Sentiment Score (-1 a 1)` y extraer "Qué empresa
      se menciona".

### Sprint 11: Frontend Definitive UI (React/Next.js) (2-3 Semanas)

- [ ] Setup de **Next.js** o React 18, implementando el sistema de diseño de
      **shadcn/ui** y TailwindCSS para lograr un aspecto financiero "Premium"
      (estilo terminal Bloomberg o Koyfin).
- [ ] Construir la **"Radiografía de Empresa" (Company View)**: Gráficos
      dinámicos con D3/Recharts para cotizaciones y Revenue/EBITDA histórico en
      barras.
- [ ] Vista de **Comparativa**: Mostrar la empresa frente a su "Peer Group"
      (obtenido en el Sprint 7).
- [ ] Tarjetas de IA: Mostrar resúmenes de riesgos, últimas noticias con tono
      (+/o/-) y el Moat Score desglosado.

---

## FASE 5: Maduración y Operación en "Piloto Automático"

**Objetivo:** Pulir errores, lidiar con baneos reales y dejar el sistema
corriendo de forma autónoma a nivel masivo.

### Sprint 12: Evasión Avanzada y Estabilidad (Continuo)

- [ ] Integrar soluciones más sólidas (Tor proxies rotatorios gratuitos o
      validadores de listas libres) si los scrapers web empiezan a fallar
      masivamente.
- [ ] Alertas: Sistema de notificaciones (Slack/Telegram) si un scraper rompe
      (ej. cambió la web de la CNMV).

### Sprint 13: Exportaciones y Reportes Personalizados

- [ ] Función para generar un "Dossier PDF" auto-maqutado de la empresa que
      resuma toda la info para que puedas llevártelo (Reportes generables desde
      el Frontend).
- [ ] Endpoint de descarga directa de los dataset crudos a `.xlsx` para tu
      propio análisis en Excel.
