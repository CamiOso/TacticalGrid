"""Servidor web local para ver visualizaciones HTML."""

import http.server
import socketserver
import webbrowser
from pathlib import Path
import threading
import time

PORT = 8000
DIRECTORY = Path(__file__).parent


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)


def main():
    print("\n" + "=" * 70)
    print("🌐 SERVIDOR WEB LOCAL - TacticalGrid")
    print("=" * 70)

    print(f"\n📁 Sirviendo archivos desde: {DIRECTORY}\n")

    # Listar archivos HTML disponibles
    html_files = sorted(DIRECTORY.glob("visualizacion_*.html"))

    if html_files:
        print("📄 Visualizaciones disponibles:\n")
        for i, f in enumerate(html_files, 1):
            print(f"   {i}. {f.name}")
        print()
    else:
        print("⚠️  No hay visualizaciones HTML generadas")
        print("   Primero ejecuta: python visualizer_terminal.py\n")

    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            url = f"http://localhost:{PORT}"

            print(f"✅ Servidor iniciado en: {url}")
            print(f"\n🌐 Abriendo navegador...\n")

            # Abrir navegador en hilo separado
            def open_browser():
                time.sleep(1)
                webbrowser.open(url)

            thread = threading.Thread(target=open_browser, daemon=True)
            thread.start()

            print("🔗 Presiona Ctrl+C para detener el servidor\n")
            print("=" * 70)

            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\n⚠️  Servidor detenido")
    except OSError as e:
        print(f"\n❌ Error: {e}")
        print(f"   El puerto {PORT} puede estar en uso")
        print(f"   Intenta: netstat -tuln | grep {PORT}")


if __name__ == "__main__":
    main()
