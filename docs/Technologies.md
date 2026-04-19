# Technologies Stack

Obsidian entegrasyonu, Graph renderleme, Ingestion Pipeline vb. operasyonlar için birbiriyle harmonize çalışan temel framework paketleri aşağıda listelenmiştir:

- **Django & Django REST Framework (DRF):** Backend sunucusu ve API servisi altyapısı.
- **Supabase (PostgreSQL):** Bulut ortamı veritabanı yönetimi ve entegrasyonu.
- **mistune & markdown2:** Özel pluginlerle (Wikilink & Asset proxy) donatılan Markdown -> HTML çözümleyiciler.
- **python-frontmatter:** Obsidian dosya meta verilerinin `.md` header'larından YAML formatında ayrıştırılması.
- **pygithub:** GitHub Repo üzerinden Webhook ve ağaç (Tree) indirme entegrasyonu.
- **drf-spectacular:** `/api/docs/` üzerinde otomatik Swagger OpenAPI test ve arayüz yaratıcı aracı.
- **Vercel Environments:** Python Serverless Server (`@vercel/python`) deploy ortamı.