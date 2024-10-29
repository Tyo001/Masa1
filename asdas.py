import urllib3
import json
import threading
import time

# Gönderilecek URL
url = "https://appmobile.svurguns.cyou/Data/api/app/rezevr.php"

# Gönderilecek veri
base_data = {
    "selectedDay": "2024-10-29",
    "selectedTime": "23.30",
    "selectedFlourId": "R2",
    "note": "",
    "userId": "285"
}

# Masa numaraları listesi
masa_list = [52, 48]

# Bağlantı havuzu oluştur (örneğin, 20 bağlantıya izin ver)
http = urllib3.PoolManager(num_pools=10, maxsize=20, block=True)

# İsteği gönderecek fonksiyon
def send_request(masa):
    data = base_data.copy()  # Her istekte veri kopyalıyoruz
    data["Masa"] = masa  # Masa numarasını ekliyoruz
    
    try:
        encoded_data = json.dumps(data)
        response = http.request(
            "POST",
            url,
            body=encoded_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Masa: {masa}, Status Code: {response.status}, Response: {response.data.decode('utf-8')}")
    except Exception as e:
        print(f"Error for Masa {masa}: {e}")
        # Hata olduğunda yeniden deneme
        retry_request(masa)

# Başarısız istekler için yeniden deneme fonksiyonu
def retry_request(masa, retries=3, delay=2):
    for attempt in range(retries):
        try:
            print(f"Retrying for Masa {masa} (Attempt {attempt + 1}/{retries})")
            send_request(masa)  # Yeniden istek gönder
            return  # Başarılı olursa döngüden çık
        except Exception as e:
            print(f"Retry failed for Masa {masa} (Attempt {attempt + 1}/{retries}): {e}")
            time.sleep(delay)  # Yeniden denemeden önce biraz bekle

# Tüm masalar için aynı anda istek gönderen fonksiyon
def send_requests_for_all_tables():
    threads = []
    
    # Her masa için ayrı bir thread başlatıyoruz
    for masa in masa_list:
        thread = threading.Thread(target=send_request, args=(masa,))
        threads.append(thread)
        thread.start()

    # Bütün thread'lerin bitmesini bekliyoruz
    for thread in threads:
        thread.join()

# Sonsuz döngüde sürekli olarak istek gönder
def continuous_request_loop():
    while True:
        send_requests_for_all_tables()  # 3 masaya istek gönder
        time.sleep(0.1)  # İstekler arasında 0.1 saniyelik gecikme (GEREKİRSE ARTTIR AZALT)

# Sonsuz döngüyü başlat
continuous_request_loop()
