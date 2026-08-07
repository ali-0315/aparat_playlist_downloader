

# Aparat Playlist Downloader

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-lightgrey.svg)

Descargador profesional de listas de reproducción de Aparat con dos interfaces de usuario: CLI y GUI


## 🔧 Requisitos previos

- Python 3.6 o superior
- pip (gestor de paquetes de Python)
- Conexión a internet

## 📦 Instalación

### Instalación rápida

```bash
git clone https://github.com/ali-0315/aparat_playlist_downloader.git
cd aparat_playlist_downloader
pip install -r requirements.txt
# O si solo desea usar CLI
pip install -r cli_requirements
```

## 🚀 Cómo usarlo

### Interfaz gráfica (GUI)

Interfaz gráfica moderna y amigable con funciones avanzadas:

```bash
python gui.py
```

**Pasos para usarlo:**
1. **Seleccionar operación**: Descargar o extraer enlaces
2. **Ingresar identificador**: Uno de los siguientes formatos:
   - Identificador numérico: `822374`
   - Enlace completo: `https://www.aparat.com/playlist/822374`
3. **Seleccionar calidad**: 144, 240, 360, 480, 720, 1080
4. **Seleccionar ruta de salida**: Haciendo clic en "Seleccionar"
5. **Hacer clic en "Ejecutar"**

### Línea de comandos (CLI)

Para un uso simple y rápido:

```bash
python cli.py
```

**Ejemplo de ejecución:**
```
Give me a Aparat playlist id: 822374
Give me the quality: (Examples: 144 , 240 , 360 , 480 , 720 , 1080) :720
Type "y" if you want to create a .txt file that contain all the videos link otherwise type "n" to start download now:n
Give me the destination path (default: ./Downloads):./MyDownloads
```

## 📁 Estructura del proyecto

```
aparat_playlist_downloader/
├── core.py                 # Clase principal AparatDownloader
├── gui.py                  # Interfaz gráfica PyQt5
├── cli.py                  # Interfaz de línea de comandos
├── requirements.txt        # Dependencias completas del proyecto
├── cli_requirements.txt    # Solo dependencias de CLI
└── README.md              # Documentación del proyecto
```

### Descripción de archivos

#### `core.py` - Núcleo principal
```python
class AparatDownloader:
    def __init__(self, playlist_id, quality, for_download_manager, destination_path)
    def download_playlist()        # Descarga completa de la lista de reproducción
    def download_video()           # Descarga de un solo video
    def get_video_download_urls()  # Obtener enlaces de descarga
```

## 🔌 API de Aparat

El proyecto utiliza las siguientes APIs de Aparat:

```
# Obtener información de la lista de reproducción
GET https://www.aparat.com/api/fa/v1/video/playlist/one/playlist_id/{playlist_id}

# Obtener enlaces de descarga del video
GET https://www.aparat.com/api/fa/v1/video/video/show/videohash/{video_uid}
```

**Respuesta de ejemplo de la API:**
```json
{
  "data": {
    "attributes": {
      "title": "Nombre de la lista de reproducción",
      "file_link_all": [
        {
          "profile": "720p",
          "urls": ["https://example.com/video.mp4"]
        }
      ]
    }
  },
  "included": [/* Videos de la lista de reproducción */]
}
```

## 🔄 Ejemplo de uso programático

```python
from core import AparatDownloader

# Crear instancia
downloader = AparatDownloader(
    playlist_id="822374",
    quality="720",
    for_download_manager=False,  # True para archivo txt
    destination_path="./Downloads"
)

# Iniciar descarga
try:
    downloader.download_playlist()
    print("¡Descarga completada con éxito!")
except Exception as e:
    print(f"Error: {e}")
```

## 🤝 Contribución

### Pasos para contribuir

1. **Fork** (bifurcar) el proyecto
2. Crear una nueva **branch** (rama):
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** (confirmar) los cambios:
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. **Push** (enviar) a la rama:
   ```bash
   git push origin feature/amazing-feature
   ```
5. Crear un **Pull Request**

## 🙏 Agradecimientos
<div align="center">
  <h3>Gracias especiales a nuestros colaboradores</h3>
  <table>
    <tr>
      <td align="center">
        <a href="https://github.com/AliAkbarSobhanpour">
          <img src="https://github.com/AliAkbarSobhanpour.png" width="100px;" alt="علی اکبر سبحانپور"/>
          <br />
          <sub><b>علی اکبر سبحانپور</b></sub>
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/AlirezaSakhtemanian">
          <img src="https://github.com/AlirezaSakhtemanian.png" width="100px;" alt="علیرضا"/>
          <br />
          <sub><b>علیرضا</b></sub>
        </a>
      </td>
    </tr>
  </table>
</div>

---

<div align="center">

**⭐ ¡Si este proyecto fue útil, dale una estrella!**

`Escrito con ❤️ `

</div>

## 🏷️ Etiquetas

`aparat` `downloader` `playlist` `python` `pyqt5` `gui` `cli` `video-downloader`
