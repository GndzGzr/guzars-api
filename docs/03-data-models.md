# 03 - Data Models & Zettelkasten

Sistemin merkezinde yatan tablo yapıları, Obsidian'ın yapısına ve Zettelkasten prensiplerine uygun tasarlanmıştır.

## 🏗️ Mimari Şema

```mermaid
classDiagram
    class Note {
        +int id
        +string title
        +string slug
        +string note_type "FLT, REF, PRM"
        +string zettel_id
        +json metadata
        +json toc
        +boolean published
        +save()
    }

    class ReferenceNote {
        +string source_url
        +string reference_url
        +string author
        +string reference_type
    }

    class PermanentNote {
        +boolean is_atomic
    }

    class Tag {
        +int id
        +string name
        +string slug
    }

    class NoteLink {
        +int id
        +string link_type "REF, SEQ, STR"
        +string target_block
        +string context_text
    }

    class VaultConfiguration {
        +int pk "Singleton"
        +json include_paths
        +json exclude_paths
        +datetime last_updated
        +load()
    }

    %% Kalıtım (Inheritance)
    Note <|-- ReferenceNote : Inherits
    Note <|-- PermanentNote : Inherits

    %% İlişkiler (Relationships)
    Note "1" --> "0..*" Note : parent_note (children)
    Tag "1" --> "0..*" Tag : parent (children)
    
    Note "1..*" -- "0..*" Tag : tags
    
    Note "1" --> "0..*" NoteLink : source (outgoing)
    NoteLink "1" --> "1" Note : target (incoming)
```

## 📜 Modeller

### 1. Note (Temel Model)
Tüm `.md` dosyalarının baz aldığı nesnedir.
- **note_type:** `FLEETING`, `REFERENCE`, `PERMANENT`.
- **content_raw / content_html:** İşlenmemiş Obsidian metni ve Web'e hazır HTML.
- **zettel_id:** Benzersiz kimlik tanımlayıcısı (UUID + Date).
- **toc:** İçindekiler tablosu (headers `#{1,6}`).
- **tags / parent:** ManyToMany tag bağlantıları ve hiyerarşi dizilimi.

### 2. Reference Note (Note'dan türer)
Kitap, makale vb. dış referansları depolamak için kullanılır. `source_url`, `reference_url`, `author`, `reference_type` bilgilerini barındırır.

### 3. Permanent Note (Note'dan türer)
Bağımsız, spesifik ve kalıcı fikirleri temsil eder. `is_atomic` durumunu saklar.

### 4. Tag
Notların içerisinde geçen etiketleri temsil eder. Kendi içinde hiyerarşiktir (Parent > Child).
    
### 5. NoteLink (Edge / Bağlantılar)
Görsel Obsidian Graf'ının yapısını tutan temel sistemdir.
- **source / target:** Bağlantının çıktığı kaynak ve gittiği hedef.
- **link_type:** Genel Referans (REF), Sequence (SEQ), MOC (STR).
- **target_block:** Spesifik bir başlığa referans verilmişse tutulur (`#heading`).
- **context_text:** Linkin içerisinde geçtiği cümleyi (Backlinks / Linked Mentions) barındırır.

### 6. Vault Configuration
Hangi sistem klasörlerinin işleneceğini belirleyen Singleton modelidir (`include_paths`, `exclude_paths`).