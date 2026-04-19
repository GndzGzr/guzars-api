# 01 - Introduction & Architecture

Guzars API, Obsidian kasanızı (Vault) çevrimiçi kullanabilmek, bir sitede görüntüleyebilmek ve yönetebilmek amacıyla **Django** kullanılarak geliştirilmiş bir entegrasyon uygulamasıdır. İçerikler **Obsidian** ile yönetilirken veritabanı olarak **Supabase** üzerine kurgulanmış ve **Vercel** üzerinden yayınlanacak şekilde tasarlanmıştır.

## 🌟 Temel Özellikler
- **Markdown Parsing:** Obsidian'ın spesifik yapısını (Frontmatter, Tagler, Wikilinkler, Başlıklar) doğal olarak ayrıştırır.
- **Automated Sync:** Obsidian Vault'unuzdaki değişiklikleri GitHub Webhook aracılığıyla anında algılar ve veritabanını otomatik günceller.
- **Graph Data Structure:** Notları sadece metin olarak depolamaz, aynı zamanda `NoteLink` yapılarıyla aralarındaki bağlantıları kaydederek interaktif bilgi grafikleri oluşturulmasına imkan sağlar.

## 🏗️ Katmanlar ve Mimari (Layers)

Sistem üç ana bileşenden oluşmaktadır:

### 1. Source Provider (Kaynak Sağlayıcı)
Kaynakları depolamak için farklı yöntemler kullanılabilir. Mevcut projede **Supabase** (Veritabanı) ve **GitHub Webhook** (Dosya Kaynağı) senkronize çalışır.
- Daha güvenli yerel kullanım için **SQLite**.
- Single Source of Truth (Tek Hakikat Kaynağı) için **GitHub Reposu** (guzars-obsidian).
- Ölçeklenebilirlik için **Supabase**.

![Architecture](assets/shapes%20at%2026-03-16%2011.51.26.svg)

### 2. Ingestion & Parser (İçeri Aktarma ve Ayrıştırma)
Obsidian `.md` uzantılı dosyalar ve sayfalar arası wikilinklerden oluşur. Sistem içindeki veriler; Raw Content, Wikilinks, Resim/Belge varlıkları ayrı ayrı çözümlenerek işlenir (Bkz: `04-obsidian-integration.md`).

### 3. Data Store & Synchronization (Veritabanı ve Senkronizasyon)
Veriler sisteme eşetkili (Idempotent) olarak yazılır. Var olan objeler duplicate edilmez, sadece değişen kısımlar güncellenir.

---
*İlgili Repolar:*
- [Obsidian Vault Repo](https://github.com/GndzGzr/guzars-obsidian)
- [Guzars API Repo](https://github.com/GndzGzr/guzars-api)
- [Guzars CMS](https://github.com/GndzGzr/guzars-cms)