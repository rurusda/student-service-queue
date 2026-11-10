
// ==========================================
// KONFIGURASI API
// ==========================================

const API_URL = "http://localhost:5001";

// ==========================================
// ELEMEN HTML
// ==========================================

const queueForm = document.getElementById("queueForm");
const queueTable = document.getElementById("queueTable");
const totalQueue = document.getElementById("totalQueue");
const waitingQueue = document.getElementById("waitingQueue");
const lastNumber = document.getElementById("lastNumber");
const nextQueue = document.getElementById("nextQueue");

const resultBox = document.getElementById("resultBox");
const resultNumber = document.getElementById("resultNumber");
const resultName = document.getElementById("resultName");
const formMessage = document.getElementById("formMessage");
const submitButton = document.getElementById("submitButton");

const refreshButton = document.getElementById("refreshButton");


// ==========================================
// HELPER: MENCEGAH HTML INJECTION
// ==========================================

function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, function (character) {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        };

        return entities[character];
    });
}


// ==========================================
// MENAMPILKAN PESAN
// ==========================================

function showMessage(message, type) {
    formMessage.textContent = message;
    formMessage.className = `message ${type}`;
}


// ==========================================
// MENGAMBIL DATA ANTREAN
// ==========================================

async function loadQueue() {
    try {
        const response = await fetch(`${API_URL}/queue`);

        if (!response.ok) {
            throw new Error("Gagal mengambil data antrean.");
        }

        const data = await response.json();

        // Memperbarui statistik
        totalQueue.textContent = data.total;
        waitingQueue.textContent = data.total;
        lastNumber.textContent =
            data.last_number > 0
                ? `A${String(data.last_number).padStart(3, "0")}`
                : "-";

        // Menampilkan antrean berikutnya
        nextQueue.textContent =
            data.queue.length > 0
                ? data.queue[0].number
                : "-";

        // Menampilkan tabel
        renderQueue(data.queue);

    } catch (error) {
        queueTable.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    Tidak dapat terhubung ke server.
                    Periksa apakah backend sedang berjalan.
                </td>
            </tr>
        `;

        console.error("Load Queue Error:", error);
    }
}


// ==========================================
// MENAMPILKAN TABEL ANTREAN
// ==========================================

function renderQueue(queue) {
    if (queue.length === 0) {
        queueTable.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    Belum ada mahasiswa yang mengantre.
                </td>
            </tr>
        `;
        return;
    }

    queueTable.innerHTML = queue.map((item, index) => `
        <tr>
            <td><strong>${escapeHTML(item.number)}</strong></td>
            <td>${escapeHTML(item.name)}</td>
            <td>${escapeHTML(item.nim)}</td>
            <td>${escapeHTML(item.service)}</td>
            <td>
                <span class="status-badge">Menunggu</span>
            </td>
            <td>
                <button
                    class="btn-complete"
                    data-index="${index}"
                >
                    Selesai
                </button>
            </td>
        </tr>
    `).join("");
}


// ==========================================
// MENAMBAHKAN ANTREAN BARU
// ==========================================

queueForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const name = document.getElementById("name").value.trim();
    const nim = document.getElementById("nim").value.trim();
    const service = document.getElementById("service").value;

    const requestData = {
        name: name,
        nim: nim,
        service: service
    };

    submitButton.disabled = true;
    submitButton.textContent = "Memproses...";

    resultBox.classList.add("hidden");
    formMessage.classList.add("hidden");

    try {
        const response = await fetch(`${API_URL}/queue`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestData)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Gagal membuat antrean.");
        }

        // Menampilkan nomor antrean
        resultNumber.textContent = result.data.number;
        resultName.textContent = result.data.name;

        resultBox.classList.remove("hidden");

        showMessage(
            "Nomor antrean berhasil dibuat!",
            "success"
        );

        queueForm.reset();

        // Memperbarui tabel dan statistik
        await loadQueue();

    } catch (error) {
        showMessage(error.message, "error");
        console.error("POST Queue Error:", error);

    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Ambil Nomor Antrean →";
    }
});


// ==========================================
// MENYELESAIKAN ANTREAN
// ==========================================

queueTable.addEventListener("click", async function (event) {
    const button = event.target.closest(".btn-complete");

    if (!button) {
        return;
    }

    const index = button.dataset.index;

    const confirmation = confirm(
        "Apakah antrean ini sudah selesai dilayani?"
    );

    if (!confirmation) {
        return;
    }

    button.disabled = true;

    try {
        const response = await fetch(
            `${API_URL}/queue?index=${encodeURIComponent(index)}`,
            {
                method: "DELETE"
            }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Gagal menyelesaikan antrean.");
        }

        alert(result.message);

        await loadQueue();

    } catch (error) {
        alert(error.message);
        console.error("DELETE Queue Error:", error);

    } finally {
        button.disabled = false;
    }
});


// ==========================================
// TOMBOL REFRESH
// ==========================================

refreshButton.addEventListener("click", function () {
    loadQueue();
});


// ==========================================
// INISIALISASI APLIKASI
// ==========================================

loadQueue();

// Memperbarui data otomatis setiap 5 detik
setInterval(loadQueue, 5000);
