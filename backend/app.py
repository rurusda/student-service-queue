
import os
import json
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# ==========================================
# KONFIGURASI
# ==========================================

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 5001))

# Lokasi penyimpanan data JSON
DATA_DIR = os.environ.get(
    "DATA_DIR",
    os.path.join(os.path.dirname(__file__), "data")
)

DATA_FILE = os.path.join(DATA_DIR, "queue.json")

# Lock untuk mencegah konflik saat beberapa request bersamaan
data_lock = threading.Lock()


# ==========================================
# FUNGSI PENYIMPANAN DATA
# ==========================================

def initialize_storage():
    """Membuat folder dan file JSON jika belum tersedia."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        initial_data = {
            "last_number": 0,
            "queue": []
        }

        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(initial_data, file, indent=4)


def load_data():
    """Membaca data antrean dari file JSON."""
    initialize_storage()

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data):
    """Menyimpan perubahan data ke file JSON."""
    os.makedirs(DATA_DIR, exist_ok=True)

    temp_file = DATA_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    os.replace(temp_file, DATA_FILE)


# ==========================================
# HTTP RESPONSE
# ==========================================

class QueueHandler(BaseHTTPRequestHandler):

    def send_json(self, status_code, data):
        """Mengirim response dalam format JSON."""

        response = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(status_code)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header("Content-Length", str(len(response)))

        # CORS CONFIGURATION
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, DELETE, OPTIONS"
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()
        self.wfile.write(response)

    def read_json(self):
        """Membaca dan memvalidasi request body JSON."""

        try:
            content_length = int(self.headers.get("Content-Length", 0))

            if content_length <= 0:
                raise ValueError("Request body tidak boleh kosong.")

            if content_length > 10000:
                raise ValueError("Ukuran request terlalu besar.")

            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))

            if not isinstance(data, dict):
                raise ValueError("Format JSON harus berupa object.")

            return data

        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError("Request body JSON tidak valid.")

    # ======================================
    # CORS PREFLIGHT REQUEST
    # ======================================

    def do_OPTIONS(self):
        """Menangani preflight request dari browser."""

        self.send_response(204)

        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, DELETE, OPTIONS"
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()

    # ======================================
    # HEALTH CHECK & GET /queue
    # ======================================

    def do_GET(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/health":
            self.send_json(200, {
                "status": "active",
                "service": "Student Service Queue API"
            })
            return

        # GET /queue
        # Menampilkan daftar antrean

        if parsed_url.path == "/queue":
            with data_lock:
                data = load_data()

            self.send_json(200, {
                "status": "success",
                "total": len(data["queue"]),
                "last_number": data["last_number"],
                "queue": data["queue"]
            })
            return

        self.send_json(404, {
            "error": "Endpoint tidak ditemukan."
        })

    # ======================================
    # POST /queue
    # Mengambil nomor antrean
    # ======================================

    def do_POST(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path != "/queue":
            self.send_json(404, {
                "error": "Endpoint tidak ditemukan."
            })
            return

        try:
            request_data = self.read_json()

            name = request_data.get("name")
            nim = request_data.get("nim")
            service = request_data.get("service")

            # Validasi input
            if not all(
                isinstance(value, str) and value.strip()
                for value in [name, nim, service]
            ):
                self.send_json(400, {
                    "error": "Nama, NIM, dan jenis layanan wajib diisi."
                })
                return

            name = name.strip()
            nim = nim.strip()
            service = service.strip()

            if len(name) > 100 or len(nim) > 30 or len(service) > 100:
                self.send_json(400, {
                    "error": "Panjang data melebihi batas yang diizinkan."
                })
                return

            with data_lock:
                data = load_data()

                # Nomor antrean selalu bertambah
                data["last_number"] += 1

                queue_number = f"A{data['last_number']:03d}"

                new_queue = {
                    "number": queue_number,
                    "name": name,
                    "nim": nim,
                    "service": service,
                    "status": "waiting",
                    "created_at": datetime.now().isoformat(
                        timespec="seconds"
                    )
                }

                data["queue"].append(new_queue)

                save_data(data)

            self.send_json(201, {
                "status": "success",
                "message": "Nomor antrean berhasil dibuat.",
                "data": new_queue
            })

        except ValueError as error:
            self.send_json(400, {
                "error": str(error)
            })

    # ======================================
    # DELETE /queue?index=X
    # Menyelesaikan antrean
    # ======================================

    def do_DELETE(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path != "/queue":
            self.send_json(404, {
                "error": "Endpoint tidak ditemukan."
            })
            return

        query = parse_qs(parsed_url.query)
        index_value = query.get("index", [None])[0]

        if index_value is None:
            self.send_json(400, {
                "error": "Parameter index wajib diisi."
            })
            return

        try:
            index = int(index_value)

            if index < 0:
                raise ValueError

        except ValueError:
            self.send_json(400, {
                "error": "Index harus berupa bilangan bulat non-negatif."
            })
            return

        with data_lock:
            data = load_data()

            if index >= len(data["queue"]):
                self.send_json(404, {
                    "error": "Data antrean tidak ditemukan."
                })
                return

            removed_queue = data["queue"].pop(index)
            save_data(data)

        self.send_json(200, {
            "status": "success",
            "message": "Antrean berhasil diselesaikan.",
            "removed": removed_queue
        })

    # ======================================
    # REQUEST LOG
    # ======================================

    def log_message(self, format, *args):
        print("[API]", format % args)


# ==========================================
# MENJALANKAN SERVER
# ==========================================

if __name__ == "__main__":
    initialize_storage()

    server = ThreadingHTTPServer((HOST, PORT), QueueHandler)

    print("=" * 50)
    print("STUDENT SERVICE QUEUE API")
    print(f"Server berjalan di http://localhost:{PORT}")
    print(f"Data tersimpan di: {DATA_FILE}")
    print("=" * 50)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer dihentikan.")
    finally:
        server.server_close()
