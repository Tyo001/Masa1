import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Test ayarları
url = "https://phonex.az/"  # Test edilecek URL
total_requests = 1000  # Gönderilecek toplam istek sayısı
concurrent_requests = 7  # Aynı anda gönderilecek istek sayısı
delay_between_chunks = 3  # Veri parçaları arasında bekleme süresi (saniye)

def slow_request():
    """Bir isteği yavaş gönder ve yanıt süresini ölç."""
    try:
        start_time = time.time()
        
        # Yavaş bağlantı simülasyonu: isteği parçalara ayırarak gönderme
        with requests.Session() as session:
            request = requests.Request("GET", url)
            prepped = session.prepare_request(request)

            # Yavaş yavaş veri gönder
            response = session.send(prepped, stream=True, timeout=10)

            for chunk in response.iter_content(chunk_size=1024):
                time.sleep(delay_between_chunks)  # Her veri parçasında gecikme
                if not chunk:
                    break
            
            end_time = time.time()
            
            if response.status_code == 200:
                return end_time - start_time
            else:
                print(f"Sunucu yanıt kodu: {response.status_code}")
                return None
    except requests.RequestException as e:
        print(f"Hata: {e}")
        return None

def run_slow_load_test():
    """Yavaş yük testi gerçekleştir ve sonuçları döndür."""
    response_times = []

    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [executor.submit(slow_request) for _ in range(total_requests)]
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                response_times.append(result)

    # Sonuçları analiz et
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)

        print(f"Toplam istek sayısı: {total_requests}")
        print(f"Eşzamanlı istek sayısı: {concurrent_requests}")
        print(f"Ortalama yanıt süresi: {avg_response_time:.2f} saniye")
        print(f"En uzun yanıt süresi: {max_response_time:.2f} saniye")
        print(f"En kısa yanıt süresi: {min_response_time:.2f} saniye")
    else:
        print("Yanıt alınamadı.")

# Yavaş yük testini başlat
if __name__ == "__main__":
    start_test_time = time.time()
    run_slow_load_test()
    end_test_time = time.time()
    print(f"Toplam test süresi: {end_test_time - start_test_time:.2f} saniye")
