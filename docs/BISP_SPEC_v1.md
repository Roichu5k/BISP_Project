BUSINESS INTELLIGENCE SCRAPER PLATFORM (BISP) Diseño Técnico Completo &
Especificación de Datos (Edición "Zero-Cost & Euro-Centric") Versión 1.2 · 2026

================================================================================

1. RESUMEN EJECUTIVO
   ================================================================================

El Business Intelligence Scraper Platform (BISP) es un sistema distribuido de
recopilación, procesamiento y análisis automatizado de información corporativa.
Su objetivo es proporcionar una radiografía completa de empresas, agregando
datos financieros, competitivos, operativos y cualitativos en un único dashboard
accionable.

El sistema está diseñado bajo tres principios rectores para esta edición:

- Presupuesto Cero (Free & Open Source): Priorizar herramientas open-source, de
  auto-alojamiento (self-hosted) y APIs con capas gratuitas (free-tiers) muy
  generosas.
- Soberanía de Datos y Modelos: Uso de LLMs locales o de bajo coste para no
  depender de APIs caras y evitar fugas de privacidad.
- Escalabilidad Eficiente: Capacidad de correr en hardware de consumo
  optimizando el uso de recursos.

Alcance del sistema: → Foco principal en Empresas Cotizadas Europeas (BME
España, Euronext, Xetra Alemania, LSE UK, Milán, etc.) sin dejar de lado EE.UU.
(NYSE, NASDAQ). → Empresas privadas europeas con información pública disponible
en registros mercantiles nacionales. → Adaptabilidad total a las
particularidades europeas: Multilingüismo en documentos, normativas contables
IFRS e informes semestrales.

# ================================================================================ 2. ARQUITECTURA DEL SISTEMA

2.1 Diagrama de Capas

L1 · Orquestación Scheduler de jobs, gestión de prioridades y control de flujos.
Tecnología: Prefect (Open Source, más ligero que Airflow) o Celery.

L2 · Ingesta (Scrapers) Librerías Python (yfinance, OpenBB), scrapers web
headless (Playwright) orientados a portales corporativos europeos, parsers de
registros mercantiles (CNMV, Companies House, AMF, Bundesanzeiger) y SEC EDGAR.

L3 · Normalización (ETL) Limpieza, deduplicación, mapeo canónico (armonización
IFRS vs US GAAP) y gestión de multimoneda. Tecnología: Polars / DuckDB.

L4 · Almacenamiento Data Lake (raw) local o en MinIO, Data Warehouse relacional
de series temporales y vectores. Tecnología: MinIO + PostgreSQL (con extensión
pgvector y TimescaleDB).

L5 · Análisis & AI Cálculo de ratios (Piotroski, ROIC, DCF), análisis de
sentimiento multilingüe y lectura de PDFs por IA. Tecnología: Modelos LLM
Locales (Ollama) o APIs gratuitas (Groq).

L6 · Presentación API FastAPI, dashboard React/Next.js (shadcn/ui), gráficos
dinámicos con D3/Recharts.

# ================================================================================ 3. CAPA DE INGESTA — SCRAPERS & CONECTORES (FOCO EUROPEO)

Para el mercado europeo, la información financiera está más fragmentada y
requiere mayor diversificación de fuentes al no existir un "SEC EDGAR"
centralizado a nivel continental.

3.1 Conectores a APIs Financieras y Librerías Gratuitas

yfinance (Python) — Fuente primaria para precios y fundamentales básicos. Extrae
cotizadas europeas perfectamente si se usan los sufijos correctos (ej: `ITX.MC`
para Inditex/España, `MC.PA` para LVMH/Francia, `VOW3.DE` para
Volkswagen/Alemania, `BP.L` para UK). Gratis y sin límite estricto de API key.
OpenBB Platform — Agregador open-source. Muy poderoso para extraer
identificadores bursátiles, datos macroeconómicos europeos (Eurostat, BCE) y
curvas de tipos. Registros Nacionales y de Transparencia (Vía Scraping o APIs):

- España: web de la CNMV (Hechos relevantes, OIR, informes financieros
  semestrales).
- Reino Unido: API de Companies House (Super robusta, gratuita e incluye
  empresas privadas).
- Francia/Alemania: AMF, Balo, Bundesanzeiger, Unternehmensregister (Requieren
  scraping robusto). SEC EDGAR API — Se mantiene (100% gratis) para comparables
  americanos, o para empresas europeas que cotizan como ADRs en NY. Bolsas
  Locales — Scraping directo a secciones de datos de BME (Mercado Continuo, BME
  Growth), Euronext, etc. para obtener índices, dividendos declarados o
  short-selling registers.

3.2 Web Scrapers (Adaptados a Relación con Inversores Europeos)

Playwright (Python) con `playwright-stealth` Herramienta clave. Permite navegar
por la sección de "Investor Relations" de las webs corporativas europeas,
esquivando banners de cookies obligatorios (GDPR) y capturando presentaciones o
PDFs inauditos en feeds de datos centrales.

Parseadores ESEF e iXBRL + pdfplumber Las empresas cotizadas en la UE reportan
en formato ESEF (European Single Electronic Format). Usaremos librerías como
`Arelle` o `python-ixbrl` para sacar el dato financiero exacto de estos
archivos. Para informes más antiguos o no convencionales, `pdfplumber` o
`PyMuPDF` leerán el documento a la antigua usanza.

3.3 Opciones de Backup Gratis / Low-Cost EODHD (EOD Historical Data) o Financial
Modeling Prep (FMP) — Usar solo en sus capas gratuitas para tapar "agujeros" de
yfinance en Europa (frecuentemente los outstanding shares precisos o splits en
small/mid caps europeas fallan en Yahoo).

# ================================================================================ 4. CAPA ETL, NORMALIZACIÓN & RETOS EUROPEOS

4.1 Extracción de alta eficiencia Polars y DuckDB actúan sobre archivos en disco
o memoria, prescindiendo de clusters de Spark. Procesan gigabytes en un solo PC
en segundos.

4.2 Armonización Contable (IFRS vs. US GAAP) La base de datos debe almacenar
métricas bajo un "Modelo Canónico", reconciliando diferencias clave entre IFRS
(Europa) y US GAAP (USA). Por ejemplo, el tratamiento contable de contratos de
alquiler o gastos de I+D.

4.3 Gestión Multimoneda Nativa Las empresas reportarán en EUR, GBP, CHF, SEK,
NOK o DKK. El ETL consultará una tabla maestra de tipos de cambio históricos
(Forex ECB/Yahoo) para homogeneizar y permitir comparar a BMW (EUR) contra Tesla
(USD) en la misma divisa de visualización del dashboard.

4.4 Periodos Incompletos (H1 / H2) A diferencia de EE.UU. (Q1 a Q4 obligatorio),
muchas empresas europeas reportan solo semestralmente (H1/H2), o reportan un
escueto "Trading Update" de solo ingresos en Q1/Q3. El esquema de Postgres
permitirá nulos controlados en márgenes/EBITDA para los trimestres impares
europeos.

# ================================================================================ 5. CAPA DE ALMACENAMIENTO (100% OPEN SOURCE)

Data Lake:

- MinIO (Auto-alojado, reemplaza a S3): Todos los ESEF ZIPs, PDFs de informes,
  HTML scrapeados quedan almacenados localmente de forma vitalicia.

Data Warehouse:

- PostgreSQL 16
  - TimescaleDB (para time-series de cotizaciones de acciones y Fx).
  - pgvector (Extension nativa para guardar los embeddings generados por la
    Inteligencia Artificial, sin depender de un pesado Elasticsearch).

Caché & Broker:

- Redis (Caché asíncrona y gestor de encolado de pequeñas tareas en background).

# ================================================================================ 6. CAPA DE ANÁLISIS & AI (ZERO-COST AI & MULTILINGÜE)

6.1 Modelos LLM Locales (Inferencia Gratuita) y Traductores Al Vuelo El
ecosistema europeo tiene documentos en español, alemán, francés, italiano...

- Ollama / vLLM (Local): Como motor de ejecución.
- Modelos LLM: Se priorizarán modelos con maestría probada en múltiples idiomas
  (ej. Qwen 2.5, o Llama-3-8B).
  - Los LLMs recibirán el PDF del balance en alemán o el acta en español y se
    les pedirá, en el mismo prompt, que extraigan los riesgos y el 'MOAT',
    devolviendo el JSON final estandarizado en inglés (o en español si lo
    prefieres para tu plataforma).

6.2 APIs Gratuitas de Respaldo Si el procesamiento local ahoga el ordenador:

- Groq API: Nivel gratuito bestial para clasificar decenas de noticias
  financieras europeas por segundo (análisis de sentimiento).
- DeepSeek: Fracciones de céntimo para tareas muy demandantes que requieran
  reasoning avanzado.

6.3 Computación de Embeddings

- Librería `sentence-transformers` en Python usando el modelo `BGE-m3` (soporta
  100 idiomas). Crea la huella dactilar matemática de lo que hace cada empresa
  europea para, posteriormente, hacer `SELECT comparables` en Postgres de forma
  instantánea.

# ================================================================================ 7. ESPECIFICACIÓN DE DATOS (Ajustes Euro-Centric)

Se mantiene la exhaustividad financiera, agregando estas lupas críticas:

7.3 Datos Financieros (y Normativa)

- Se guardan los estados financieros base, pero apuntando la norma contable
  aplicada (`IFRS` vs `Local GAAP`).
- Soporte para desgloses por Divisa Múltiple y ajustes semestrales.

7.6 Peer Group Algorítmico Transeuropeo

- En lugar de limitarnos a comparar un banco español con el ibex, el motor de
  Embeddings + LLM buscará competidores geográficamente cercanos (ej. Santander
  comparado con Intesa Sanpaolo o BNP Paribas).

7.10 "Hechos Relevantes" e Inteligencia Regulatoria

- Las noticias cambian por comunicados oficiales europeos. Sustituimos el SEC
  8-K por triggers en los OIR/IP (Otra Información Relevante / Información
  Privilegiada) de la CNMV, o los RNS (Regulatory News Service) londinenses, que
  mueven los mercados bruscamente de buena mañana.

7.11 ESG (Alta Frecuencia en Europa)

- Europa es líder en regulación medioambiental (Taxonomía Europea, CSRD). El LLM
  local tendrá un prompt especializado en extraer las métricas obligatorias
  reportadas en las Memorias de Sostenibilidad integradas en Europa (Scope 1, 2,
  3 de Emisiones).

# ================================================================================ 8. STACK TECNOLÓGICO Y DESPLIEGUE STARTUP

Lenguaje backend → Python 3.12 (asyncio intensivo) Framework API → FastAPI +
Pydantic v2 Framework web scraping → Playwright + BeautifulSoup + python-ixbrl
Procesamiento de Datos → Polars + DuckDB Orquestación de pipelines → Prefect
(Ideal para gestionar flujos pythonicos) Base de datos principal → PostgreSQL
16 + TimescaleDB + pgvector Data Lake → MinIO local Caché y Colas → Redis Motor
de Búsqueda Semántica → pgvector nativo LLM (Inferencia) → Ollama (Corriendo
Qwen2.5 / Llama 3) Frontend → React 18 / Next.js con shadcn/ui y Tailwind CSS
Infraestructura → Docker (Todo el stack levantable en un clónico potente de
torre personal o VPS mediano/bare-metal en Hetzner para ahorrar sin pagar AWS).

# ================================================================================ RESUMEN EJECUTIVO DE LA EVOLUCIÓN (v1.2)

✓ Presupuesto en servidores/APIs cercano a 0€ al mes. ✓ Adaptado al peculiar,
multilingüe y fragmentado mercado Europeo (IFRS, reguladores locales, semestre
vs trimestre). ✓ Extracción inteligente mediante "LLM Local Translator" para
procesar informes alemanes/franceses sin fricción. ✓ Toda la arquitectura entra
en un contendor Docker, sin requerir clusters pesados, ideal para emprendedores
y setups ágiles.
