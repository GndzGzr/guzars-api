# Frontend Implementation Guide: Obsidian Headless CMS

This document outlines how to build a frontend application (e.g., using Next.js, React, Vue, or Svelte) that consumes your Obsidian Headless CMS built with Django.

## 📡 API Overview

- **Base URL**: `https://guzars-api.vercel.app/api/`
- **Authentication**: Token-based. You must include an `Authorization` header in all requests (except webhooks).
- **Format**: JSON

---

## 🔐 Authentication

To fetch your private notes securely, your frontend needs your API token. 

### 1. Getting a Token
You can generate a token by sending your admin credentials to the token endpoint:
```http
POST /api/auth/token/
Content-Type: application/json

{
    "username": "g",
    "password": "g"
}
```
**Response:**
```json
{
    "token": "14df91e1f3deac6b54b2452342402942792bb3e9"
}
```

### 2. Using the Token in your Frontend
In your frontend (like Next.js), save this token in your `.env.local` file as `OBSIDIAN_API_TOKEN`.

When making requests, include it in the headers:
```javascript
const response = await fetch('https://guzars-api.vercel.app/api/notes/', {
  headers: {
    'Authorization': `Token ${process.env.OBSIDIAN_API_TOKEN}`,
    'Content-Type': 'application/json'
  }
});
```

---

## 🛣️ Core Endpoints

### 1. Fetch All Notes
`GET /api/notes/`

Returns a paginated list of all notes in your vault.

**Response Map:**
- `id`: Database ID
- `title`: The display name of the note.
- `slug`: The URL-friendly identifier (use this for your frontend routes, e.g., `/notes/[slug]`).
- `note_type`: `"PRM"` (Permanent), `"REF"` (Reference), or `"FLT"` (Fleeting).
- `tags`: Array of tag objects.
- `metadata`: The raw YAML frontmatter parsed as a JSON object.

### 2. Fetch a Single Note
`GET /api/notes/<slug>/`

Returns the full details of a note, including its compiled HTML and relational graph data.

**Key Fields to utilize in the Frontend:**
- `content_html`: The fully compiled HTML of your markdown note. 
- `outgoing_links`: An array of notes that *this* note links to.
- `incoming_links` (Backlinks): An array of notes that link *to this* note. (Perfect for building an Obsidian-style "Backlinks" panel).

---

## 🎨 Rendering the Content

The backend automatically parses Obsidian Markdown and compiles it into valid HTML via Mistune. 

### Handling Wikilinks
When you type `[[My Note]]` in Obsidian, the backend API converts it into:
```html
<a href="/api/notes/my-note" class="internal-link">My Note</a>
```

**Frontend Strategy:**
If you are using a framework like Next.js or React, rendering raw HTML is easy, but you'll want to intercept clicks on those `internal-link` anchor tags so they trigger client-side routing (e.g., routing the user to `/notes/my-note` instead of reloading the page to the raw API url).

**React Example (Next.js):**
```jsx
import parse from 'html-react-parser';
import Link from 'next/link';

export default function NotePage({ note }) {
  
  // Intercept internal links to use Next.js <Link> wrapper
  const options = {
    replace: ({ attribs, children }) => {
      if (!attribs) return;
      if (attribs.class === 'internal-link') {
        const localPath = attribs.href.replace('/api/', '/');
        return (
          <Link href={localPath} className="text-blue-500 hover:underline">
            {children[0].data}
          </Link>
        );
      }
    }
  };

  return (
    <article className="prose lg:prose-xl">
      <h1>{note.title}</h1>
      
      {/* Safely render the backend HTML */}
      <div>{parse(note.content_html, options)}</div>
      
      {/* Render Obsidian Backlinks */}
      <div className="mt-10 border-t pt-5">
        <h3>Backlinks</h3>
        <ul>
          {note.incoming_links?.map(link => (
            <li key={link.id}>
              <Link href={`/notes/${link.source_slug}`}>
                {link.source_title}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </article>
  );
}
```

---

## 🕷️ Building a Knowledge Graph
Because the API exposes `outgoing_links` and `incoming_links` for every note, you can easily build an interactive canvas graph (like Obsidian's Graph View) in the frontend using libraries like:
- **`react-force-graph`**
- **`d3.js`**
- **`cytoscape.js`**

You can map `notes` as **Nodes**, and `outgoing_links` as **Edges** linking the `source` node to the `target` node. 
