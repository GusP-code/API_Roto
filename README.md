# API Roto

Esta es una API desarrollada con FastAPI que interactúa con una base de datos MongoDB para consultar información sobre conjuntos ("sets") de herrajes y sus componentes, probablemente para sistemas de ventanas o puertas.

La API permite listar los conjuntos disponibles y obtener datos detallados de un conjunto específico, calculando los componentes aplicables según dimensiones proporcionadas.

## Características

- **Framework**: FastAPI
- **Servidor ASGI**: Uvicorn
- **Base de Datos**: MongoDB
- **Validación de Datos**: Pydantic
- **Gestión de Configuración**: python-dotenv y pydantic-settings

## Requisitos Previos

- Python 3.8+
- Una instancia de MongoDB en ejecución.

## Instalación

1.  **Clona el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_DIRECTORIO>
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    # Para Windows
    python -m venv venv
    venv\Scripts\activate

    # Para macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuración

Esta aplicación requiere un archivo `.env` en la raíz del proyecto para gestionar las variables de entorno.

1.  Crea un archivo llamado `.env` en el directorio raíz del proyecto.

2.  Añade las siguientes variables de entorno al archivo `.env`:

    ```env
    # URL de conexión a tu instancia de MongoDB
    DATABASE_URL="mongodb://usuario:contraseña@host:puerto/"

    # Nombre de la base de datos que utilizará la aplicación
    DATABASE_NAME="nombre_de_la_bd"
    ```
    Asegúrate de reemplazar los valores con tu configuración real de MongoDB.

## Ejecución

Para iniciar la aplicación en modo de desarrollo con recarga automática, ejecuta el siguiente comando en la terminal desde la raíz del proyecto:

```bash
uvicorn app:app --reload
```

El servidor estará disponible en `http://127.0.0.1:8000`.

## Endpoints de la API

La API expone los siguientes endpoints bajo el prefijo `/api/v2`:

### 1. Listar todos los Sets

- **Endpoint**: `GET /api/v2/sets`
- **Descripción**: Devuelve una lista de todos los conjuntos (sets) disponibles en la base de datos.
- **Respuesta Exitosa (200 OK)**:
  ```json
  [
    {
      "_id": "id_del_set",
      "name": "Nombre del Set",
      "minWidth": 600,
      "maxWidth": 1200,
      "minHeight": 800,
      "maxHeight": 1600
    }
  ]
  ```

### 2. Obtener datos completos de un Set

- **Endpoint**: `GET /api/v2/data`
- **Descripción**: Obtiene los herrajes y operaciones aplicables para un `set_id` específico, dadas unas dimensiones de ancho y alto.
- **Parámetros de Consulta (Query Parameters)**:
  - `set_id` (string, **requerido**): El ID del set a consultar.
  - `width` (integer, **requerido**): El ancho en milímetros.
  - `height` (integer, **requerido**): El alto en milímetros.
  - `include_schraube` (boolean, opcional, por defecto `false`): Indica si se deben incluir artículos de tipo "Schraube".
- **URL de Ejemplo**: `http://127.0.0.1:8000/api/v2/data?set_id=ID_EJEMPLO&width=1000&height=1200`
- **Respuesta Exitosa (200 OK)**: Devuelve un objeto `ResponseModel` complejo con la lista de herrajes (`applicable_fittings`), un resumen de opciones y el conteo total. 