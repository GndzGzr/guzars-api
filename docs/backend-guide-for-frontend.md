# Backend API Guide for Frontend Integration

This guide details how your frontend application (e.g., Next.js) interfaces with the Django backend. Since the frontend serves as your personal unified portal, it is designed to operate with **Superuser Privileges** using a master Admin Token.

## 📖 Interactive API Documentation (Swagger)

The absolute best way to inspect the API, test requests, and view the exact JSON schemas is through the interactive Swagger UI provided by `drf-spectacular`.

👉 **Swagger UI URL:** [https://guzars-api.vercel.app/api/docs/](https://guzars-api.vercel.app/api/docs/)

> **Tip:** You can click "Authorize" at the top of the Swagger UI and enter `Token <your_token>` to test authenticated endpoints directly in your browser. There is also an alternative Redoc view available at `/api/redoc/`.

---

## 🔐 Authentication & Sign Up (Superuser Context)

Your frontend server logic acts on behalf of the backend **superuser**. Because you provide the master `OBSIDIAN_API_TOKEN` through your server variables, Next.js can pull configurations (`/api/vault-configuration/`) and bypass `published=False` logic globally for the admin view.

Include your superuser token in the HTTP Headers for every server-side fetch:
```javascript
const headers = {
  'Authorization': `Token ${process.env.OBSIDIAN_API_TOKEN}`,
  'Content-Type': 'application/json'
};
```

### Creating the Signup Logic (End Users)
If you intend for other users to register and consume parts of the API independently (or have restricted content logic applied), the frontend can interface with the Signup Endpoint:

```http
POST /api/auth/signup/
```
**Request Body:**
```json
{
  "username": "new_reader",
  "password": "secure_password",
  "email": "reader@example.com"
}
```
**Response:**
Returns a `201 Created` containing the newly minted user token which your frontend application can then store securely and map individual client privileges against.

---

## 🔍 Retrieving Specific Information

Here are the primary ways to extract specialized data directly from the Django backend.

### 1. Fetching Notes by Type
Instead of downloading the entire vault, you can filter notes by their type mapping (Permanent, Reference, Fleeting). Check Swagger for the exact query parameters or dedicated route structures.

```http
GET /api/notes/?note_type=PRM   # For Permanent Notes
GET /api/notes/?note_type=REF   # For Reference Notes
GET /api/notes/?note_type=FLT   # For Fleeting Notes
```

### 2. File System Generation (Lightweight Tree)
When building a sidebar, file explorer, or navigation pane, fetching the entire note content is too heavy. You can request a "tree" representation which strips out the heavy HTML and Knowledge Graph arrays, returning only headers/metadata:

```http
GET /api/notes/tree/
```
**Key Data Returned (per object):**
- `id` and `slug` (for routing)
- `title` and `tags`
- `parent_note_slug` (allows you to reconstruct nested directory structures)
- `note_type` and `metadata` (allows you to show icons/emojis mapped from frontmatter)

### 3. Full Note Payload (Graph + HTML + TOC)
When you query a single note by its slug, the backend does the heavy lifting to provide everything you need to render the page and its surrounding context.

```http
GET /api/notes/my-note-slug/
```
**Key Data Returned:**
- `content_html`: The fully parsed HTML (including Mistune-compiled wikilinks and asset proxies).
- `metadata`: A JSON object of all YAML frontmatter (e.g., `date`, `aliases`, `author`).
- `incoming_links` & `outgoing_links`: Graph structure showing exactly what connects to this note.

### 3. Fetching Notes by Tag
If you are building a tag-explorer view, you can filter the notes endpoint by tag slugs.

```http
GET /api/notes/?tags=software-engineering
```

### 4. Reading the Vault Configuration
Since your Next.js application acts as an Admin interface, you can dynamically retrieve (and potentially update) the CMS synchronization rules (like what folders to include/exclude).

```http
GET /api/vault-configuration/
```

### 5. Local Assets and PDF Proxy
Images and attachments from your GitHub Obsidian vault shouldn't expose your GitHub credentials or raw repo paths. The backend serves as a secure proxy.
When rendering markdown, image paths will point to the proxy endpoint natively:

```http
GET /api/assets/?file=attachments/image.png
```
*(The frontend usually doesn't need to call this manually; the `content_html` strings out of the backend already map `<img>` tags to this secure route.)*

---

## 🛠️ Typical Frontend Fetch Utility (Next.js)

For retrieving this specific information on the server within Next.js:

```javascript
// Example: Getting specifically Permanent Notes
export async function getPermanentNotes() {
  const res = await fetch('https://guzars-api.vercel.app/api/notes/?note_type=PRM', {
    headers: { 'Authorization': `Token ${process.env.OBSIDIAN_API_TOKEN}` },
    next: { revalidate: 3600 } // Cache for 1 hour
  });
  return res.json();
}
```
