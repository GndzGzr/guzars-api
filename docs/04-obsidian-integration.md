# 04 - Ingestion & Obsidian Sync

Markdown ekosistemini REST API üzerine taşıyan Ingestion ve Parsing boru hattı `notes/services.py` ve `notes/parsers.py` içerisinde yapılandırılmıştır.

## 🛠️ Markdown Parsing
Özel Markdown eklentileri (Mistune) yardımıyla, dosya standard HTML yapısına sokulurken bazı dönüştürmeler yapılır:

- **Wikilink Resolution:** `[[Note Name#Subtitle|Alias]]` formatındaki metinler otomatik olarak `<a href="/api/notes/note-name#subtitle" class="internal-link">Alias</a>` formatına derlenir.
- **Asset Mapping:** `![[image.png]]` veya `![image.pdf]` gibi medya çağırma işlemleri otomatik tespit edilir ve `/api/assets/?file=image.png` uç noktasına yönlendiren medya etiketlerine (img/iframe) dönüştürülür.
- **Metadata Extraction:** Dosya başındaki YAML Frontmatter çekilerek Tagler, Başlıklar (TOC) ayrıştırılır, Note Tipi buna göre oluşturulur.

## 🔍 Ingestion ve Idempotency
- **Eşetkililik (Idempotency):** Sistem Idempotent olarak tasarlanmıştır. Aynı markdown dosyasını çoklu kez işlemenin bir sakıncası yoktur, veritabanı şişmez; dosyalar `update_or_create` mantığıyla kendi içeriğini ve `NoteLink`lerini son güncel haline göre siler-yeniden yazar.
- **Backlink Discovery (Two-pass necessity):** Notlar arası bağların (Graf yapısı) kusursuz oluşturulabilmesi için `target_note`'un önceden veritabanına işlenmiş olması beklenir. Eğer 0'dan, çok büyük bir repo tek seferde sisteme yükleniyorsa, Graph bağlantılarının hiçbir eksik vermemesi için scriptin ard arda 2 pass (iki defa) çalıştırılması önerilir.

## 🔄 Senkronizasyon (Sync)
GitHub web kancası `/api/webhook/github/` veya yerel management komutu olan `sync_github` kullanıldığında; GitHub'ın Tree API'si kullanılıp performans optimizasyonu sağlanarak `.md` dışındaki veriler ayıklanır. Değişen dosyaların son commit tarihleri Notlara `updated_at` olarak işlenir.