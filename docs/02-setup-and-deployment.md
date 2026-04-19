# 02 - Setup & Deployment

Sistemi yerel ortamda çalıştırmak ve Vercel üzerinden canlıya almak (Production Deployment) için gereken adımlar aşağıdadır.

## 🔐 Environment Variables (Ortam Değişkenleri)
Uygulamanın çalışması için `.env` dosyasında aşağıdaki değişkenlerin tanımlanması zorunludur:

```env
DEBUG=True # Canlı ortamda (Vercel) False olmalıdır.
SECRET_KEY=kriptografik-anahtar
DATABASE_URL=postgres://user:password@aws-0-eu-central.supabase.com:6543/postgres

# GitHub Integration
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_kisiselToken
GITHUB_WEBHOOK_SECRET=webhook-dogrulama-sifresi
```

## 🛠️ Yerel Geliştirme (Local Setup)

```bash
# Python ortamını hazırlayın
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Veritabanı tablo kurulumunu yapın
python manage.py makemigrations
python manage.py migrate

# Yönetici hesabını oluşturun
python manage.py createsuperuser

# Sunucuyu başlatın
python manage.py runserver
```

## 🚀 Deployment (Vercel Integration)
Proje, Vercel üzerinde geleneksel bir sunucu (VPS) yerine **Serverless Functions** mimarisi kullanılarak dağıtılacak şekilde ayarlanmıştır. `vercel.json` ve `build_files.sh` aracılığıyla otomatize edilir:

1.  **`vercel.json` Konfigürasyonu:**
    `@vercel/python` inşacısı (builder), gelen tüm istekleri `config/wsgi.py` üzerinden serverless ortama aktarır. Lambda boyutu 15mb ile sınırlı tutulmuştur.
2.  **`build_files.sh` Betiği:**
    Kodunuz GitHub'a gönderildiğinde (Push), Vercel bu betiği çalıştırır. Bağımlılıklar yüklenir, uzak veritabanına otomatik `migrate` işlemi yapılır ve statik dosyalar `collectstatic` ile toplanır.