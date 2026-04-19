# 06 - Usage & Administration

Günlük veri operasyonlarınızı, Obsidan istemcinizi veya doğrudan API yöneticisini (CMS) ilgilendiren yönetim basamaklarıdır.

## 🔄 Daily Usage & Syncing
Tüm işlemleri yerel PC'niz (Local Setup) üzerinden tetiklemek veya entegre bir repo ile çalıştırmak için Django built-in scriptleri bulunur:

```bash
# Repo senkronunu (veriyi içeri almayı) başlatır:
python manage.py sync_github GndzGzr/guzars-obsidian --branch main

# Notları tamamen silip veritabanı yığını sıfırlamak için:
python manage.py clear_notes
```

## 🛠️ CMS & Django Admin
Guzars API, CMS mantığını entegre bir biçimde çalıştırmak üzere Django Admin arayüzünü baz almıştır. Sunucunuzda `https://<url>/admin` dizininden erişim sağlanır.

- **Taslak (Draft) Yönetimi:** Obsidian'da `published: true` Frontmatter'ı kapatıldığında da gerçekleşen bu durum, admin panelinden toplu (bulk) olarak ayarlanabilir; eksik / taslak olarak kalmış notlar canlı API'den gizlenir.
- **Inspect Relationships:** Admin panel, size ReferenceNotes veya NoteLink üzerinden orphaned (bağlantı dışı bırakılmış kırık objeleri) denetleme gücü verecek tablo görünümleri barındırır.
- **Tags & Taxonomies:** Herhangi bir Markdown dosyasına girmeden, Global etiket isimlerinizi buradan topluca temizleyip birleştirebilirsiniz.