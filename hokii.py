import time
from datetime import datetime
import pytz
from playwright.sync_api import Playwright, sync_playwright
import requests
import os

# Load variabel dari .env
userid = os.getenv("userid")
pw = os.getenv("pw")
telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

wib = datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M WIB")

# Fungsi baca isi file nomor
def baca_file(file_name: str) -> str:
    with open(file_name, 'r') as file:
        return file.read().strip()

# Fungsi untuk menulis log + kirim ke Telegram
def tulis_log(status: str, pesan: str):
    os.makedirs("log", exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text = f"[{now}] {status} - {pesan}"

    # Simpan ke file lokal
    with open("log/riwayat.log", "a") as log_file:
        log_file.write(log_text + "\n")

    print("📦 Token ada:", bool(telegram_token))
    print("📦 Chat ID ada:", bool(telegram_chat_id))

    # Kirim ke Telegram
    if telegram_token and telegram_chat_id:
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                data={
                    "chat_id": telegram_chat_id,
                    "text": log_text
                }
            )
            print("📤 Status kirim:", response.status_code)
            print("📤 Respon:", response.text)

            if response.status_code != 200:
                print(f"⚠️ Gagal kirim ke Telegram. Status: {response.status_code}")
                print(f"📬 Respon Telegram: {response.text}")
        except Exception as e:
            print("⚠️ Error saat mengirim ke Telegram:", e)
    else:
        print("⚠️ Token atau chat_id kosong, tidak mengirim ke Telegram.")


def run(playwright: Playwright) -> None:
    try:
        print("📂 Membaca file...")
        nomor = baca_file("nomor.txt")
        bet = baca_file("bet.txt")

        print("🚀 Memulai browser...")
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("🌐 Membuka halaman utama...")
        page.goto("https://wdbos82553.com/#/index?category=lottery")
        time.sleep(1)
        page.get_by_role("img", name="close").click()
        time.sleep(1)

        print("➡️ Masuk ke HOKI DRAW...")
        with page.expect_popup() as page1_info:
            time.sleep(1)
            page.get_by_role("heading", name="HOKI DRAW").click()
        time.sleep(1)
        page1 = page1_info.value
        time.sleep(1)

        print("🔐 Login...")
        page1.get_by_role("textbox", name="-14 digit atau kombinasi huruf").fill(userid)
        time.sleep(1)
        page1.get_by_role("textbox", name="-16 angka atau kombinasi huruf").fill(pw)
        time.sleep(1)
        page1.get_by_text("Masuk").click()
        time.sleep(1)

        print("✅ Navigasi ke menu betting...")
        page1.get_by_role("link", name="Saya Setuju").click()
        time.sleep(2)
        page1.get_by_role("link", name="5D Fast").click()
        time.sleep(1)
        page1.get_by_text("FULL", exact=True).click()
        time.sleep(1)

        print(f"🎯 Memasang nomor {nomor} dengan bet {bet}...")
        page1.locator("input[name=\"buy3d\"]").fill(bet)
        time.sleep(1)
        page1.locator("#numinput").fill(nomor)
        time.sleep(1)
        page1.get_by_role("button", name="Submit").click()

        jumlah_kombinasi = len(nomor.split("*"))

        print("⏳ Menunggu hasil konfirmasi...")
        try:
            page1.wait_for_selector("text=Bettingan anda berhasil dikirim.", timeout=15000)
            print("✅ Bettingan berhasil dikirim.")
            tulis_log("SUKSES", f"Pasang {jumlah_kombinasi} nomor dengan bet {bet} berhasil. Waktu: {wib}")
        except:
            print("❌ Gagal: Teks konfirmasi tidak ditemukan.")
            tulis_log("GAGAL", "Teks 'Bettingan anda berhasil dikirim.' tidak ditemukan.")

        context.close()
        browser.close()

    except Exception as e:
        print("❌ Terjadi kesalahan saat menjalankan script.")
        print("📛 Detail error:", e)
        tulis_log("GAGAL", f"Error: {str(e)}")


with sync_playwright() as playwright:
    run(playwright)
