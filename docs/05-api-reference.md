# 05 - API Reference & Endpoints

Tüm iş mantığı `api/` veya `api/notes/` rotaları üzerinden sağlanır. Uç noktaların büyük bir kısmı Okuma Odaklı (ReadOnly) olup Yetkilendirme (Auth Token) gerektirir.

## 🌐 API Layer Capabilities (API Sağlayıcı Yetenekleri)
- **Filter and Request:** Sistem, Yayın durumu (`published=True`), Kategori/NoteType (`fleeting/`, `reference/`) ve Query Tag (`?tag=ai`) gibi esnek REST Framework filtrelemelerini barındırır.
- **Image/Media Proxy:** `GET /api/assets/` özel bir proxy olarak çalışır, backend tarafından yönlendirilen medya CDN URL'lerine korumalı yönlendirmeler yapar.
- **Authentication Security:** Data uç noktalarında İstemci Taraflı JWT/Token kimlikleri dinlenir; `/api/webhook/github/` noktası sahte sızmaları engellemek için `X-Hub-Signature-256` HMAC güvenliği ile kodlanmıştır.
- **On-the-fly Transformation:** Frontmatter, Wikilinkler ve Başlık Hiyerarşisi anında istemcilerin kullanabileceği Standard JSON / HTML veri tiplerine evrilir.
- **Graph Data Endpoint:** İnteraktif Knowledge Graph çizimine uygun formata (Node ve Edge) getirilmiş `notes/graph/` uç noktası mevcuttur.
- **Automated Documentation:** OpenAPI v3 / Swagger UI dökümanları `drf-spectacular` yardımıyla (`/api/docs/` rotasında) sistemle beraber her değişimde yaşar.
- **Caching Layer:** *Sistem performansı Queryset seviyesinde optimize edilmiştir.* `NoteTree` ve `Graph` nesneleri çağrıldığında "N+1 Sorgu" problemini engellemek için Django'nun `prefetch_related` metotları devreye girer.

---

## 🔌 API Rotaları (Endpoints)

#### `/api/notes/` & `/api/notes/<slug>/`
Tüm (veya istenen tek) notun detaylı içeriğini (Raw, HTML, Toc, Metadatalar ve Linkler) barındırır.

*Note Detail JSON Repsonse:*
```json
{
  "title": "Django'da Optimizasyon",
  "note_type": "PRM",
  "content_html": "<p>Ağır sorgularda...</p>",
  "outgoing_links": [ { "target_slug": "python", "context_text": "..." } ],
  "incoming_links": [ { "source_slug": "report", "context_text": "[[Optimizasyon]] tamamlandı..." } ]
}
```

#### `/api/notes/tree/`
File Explorer listesi veya Sidebar ağacı çizilmesi için optimize edilmiştir. Performans (Payload tasarrufu) adına HTML Raw Data'yı ve İç linkleri JSON yanıtından ayıklar.

#### `/api/notes/graph/`
Obsidian's native Node-Edge mimarisi (Örn: `react-force-graph` ile kullanım için)
```json
{
  "nodes": [ {"id": "slug", "name": "Title", "val": 1} ],
  "links": [ {"source": "slug_a", "target": "slug_b"} ]
}
```

#### Özel Kategori Rotaları
`/api/notes/fleeting/`, `/api/notes/reference/`, `/api/notes/permanent/`