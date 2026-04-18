# Next.js Frontend Implementation Guide

This guide provides a complete blueprint for building a frontend application using **Next.js (App Router)** to consume your Obsidian Headless CMS.

## 🚀 1. Project Setup
Initialize a new Next.js project with Tailwind CSS (highly recommended for formatting the markdown):
```bash
npx create-next-app@latest guzars-frontend
cd guzars-frontend
npm install html-react-parser @tailwindcss/typography
```
*Note: We install `@tailwindcss/typography` to easily style the raw HTML our API sends us using the `prose` class.*

Update your `tailwind.config.js` to include the typography plugin:
```javascript
module.exports = {
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
```

## 🔐 2. Environment Variables
Create a `.env.local` file in your Next.js root:
```env
NEXT_PUBLIC_API_URL=https://guzars-api.vercel.app/api
OBSIDIAN_API_TOKEN=your_token_here
```

## 📡 3. Data Fetching Utility
In Next.js App Router, you can fetch data directly in your Server Components. Create a `lib/api.js` utility:

```javascript
// lib/api.js
const API_URL = process.env.NEXT_PUBLIC_API_URL;
const TOKEN = process.env.OBSIDIAN_API_TOKEN;

export async function fetchAPI(endpoint) {
  const res = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      'Authorization': `Token ${TOKEN}`,
      'Content-Type': 'application/json'
    },
    // Cache the response, revalidate every 60 seconds (ISR)
    next: { revalidate: 60 } 
  });
  
  if (!res.ok) throw new Error(`Failed to fetch ${endpoint}`);
  return res.json();
}
```

## 🛣️ 4. Building the Routes

### A. The Notes Index (`app/notes/page.jsx`)
Fetch and display all notes (Fleeting, Reference, Permanent).

```jsx
import Link from 'next/link';
import { fetchAPI } from '@/lib/api';

export default async function NotesIndex() {
  const data = await fetchAPI('/notes/');
  const notes = data.results || data;

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">My Digital Garden</h1>
      <ul className="space-y-4">
        {notes.map(note => (
          <li key={note.id} className="p-4 border rounded shadow-sm hover:shadow-md transition">
            <Link href={`/notes/${note.slug}`} className="text-xl text-blue-600 font-semibold">
              {note.title}
            </Link>
            <div className="text-sm text-gray-500 mt-2 space-x-2">
              <span>{note.note_type}</span>
              {note.tags.map(tag => (
                <span key={tag.slug} className="bg-gray-100 px-2 py-1 rounded">#{tag.name}</span>
              ))}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### B. The Single Note Page (`app/notes/[slug]/page.jsx`)
Fetch the single note and render the HTML safely, intercepting Obsidian Wikilinks.

```jsx
import { fetchAPI } from '@/lib/api';
import parse, { domToReact } from 'html-react-parser';
import Link from 'next/link';
import { notFound } from 'next/navigation';

export async function generateMetadata({ params }) {
  try {
    const note = await fetchAPI(`/notes/${params.slug}/`);
    return { title: note.title };
  } catch {
    return { title: 'Note Not Found' };
  }
}

export default async function NotePage({ params }) {
  let note;
  try {
    note = await fetchAPI(`/notes/${params.slug}/`);
  } catch (error) {
    notFound();
  }

  // Intercept Obsidian internal links to use Next.js <Link> wrapper
  const options = {
    replace: ({ name, attribs, children }) => {
      if (name === 'a' && attribs?.class === 'internal-link') {
        const localPath = attribs.href.replace('/api/notes/', '/notes/');
        return (
          <Link href={localPath} className="text-blue-500 hover:underline">
            {domToReact(children, options)}
          </Link>
        );
      }
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">{note.title}</h1>
        <div className="flex gap-2">
          {note.tags.map(t => <span key={t.slug} className="text-sm bg-blue-100 text-blue-800 px-2 rounded">#{t.name}</span>)}
        </div>
      </div>
      
      {/* Safely render the compiled markdown HTML with Tailwind Typography */}
      <div className="prose prose-blue prose-lg max-w-none">
        {parse(note.content_html, options)}
      </div>
      
      {/* Render Obsidian Backlinks */}
      {note.incoming_links && note.incoming_links.length > 0 && (
        <div className="mt-16 border-t pt-8">
          <h3 className="text-2xl font-semibold mb-4">Backlinks</h3>
          <ul className="list-disc pl-5">
            {note.incoming_links.map(link => (
              <li key={link.id} className="mb-2">
                <Link href={`/notes/${link.source.slug}`} className="text-blue-500 hover:underline">
                  {link.source.title}
                </Link>
                {link.context_text && (
                  <p className="text-sm text-gray-500 italic mt-1">{link.context_text}</p>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

## 🖼️ 5. Handling Images and PDFs
Our API uses a specialized proxy (`/api/assets/?file=...`) for images and PDFs. 
Since `html-react-parser` loads the `src` attribute exactly as the backend compiled it, **images and PDFs will work out of the box**! The Next.js client request will call your Django backend proxy, which acts as a secure tunnel to your GitHub repository raw files.

If you specifically want to optimize images using Next.js `<Image />`, you can add another rule to the `options` parser inside `app/notes/[slug]/page.jsx`:
```jsx
// inside replace function:
if (name === 'img' && attribs?.class === 'obsidian-embed-image') {
  return (
    <img 
      src={`https://guzars-api.vercel.app${attribs.src}`} 
      alt={attribs.alt} 
      className="rounded-lg shadow-md"
      loading="lazy"
    />
  );
}
```

## 🕸️ 6. Graph View (Optional)
To build an interactive Graph View natively in React, use `react-force-graph-2d`.
```bash
npm install react-force-graph-2d
```
Fetch all notes, map `notes` to Nodes (id = note.id), and map `outgoing_links` to Links (source = source.id, target = target.id), then pass them to the `<ForceGraph2D graphData={data} />` component.
