# How to Create the Obsidian Graph Map in Next.js

Your backend Django API now exposes a dedicated endpoint that provides the exact JSON structure needed for standard network graph libraries. It maps all your markdown files and the wikilinks connecting them.

## 1. The API Endpoint

**Route:** `GET /api/notes/graph/`

**Response Format:**
```json
{
  "nodes": [
    { "id": "a-life-to-paint", "name": "A Life to Paint...", "val": 1 },
    { "id": "obsidian-ile-not-tutma", "name": "Obsidian ile Not tutma", "val": 1 }
  ],
  "links": [
    { "source": "a-life-to-paint", "target": "obsidian-ile-not-tutma" }
  ]
}
```

## 2. Setting up the Frontend (Next.js)

The easiest way to render this data interactively (just like Obsidian's native Graph View) is using the **`react-force-graph-2d`** library.

### Install the library
Run this in your Next.js project directory:
```bash
npm install react-force-graph-2d
```

### Create the Component

Because this library relies heavily on HTML Canvas natively via the browser DOM, you MUST disable Next.js server-side rendering (SSR) for the graph component using `next/dynamic`.

Create a file at **`components/GraphView.tsx`**:

```tsx
"use client";
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";

// Force No SSR so Canvas doesn't break in Next.js Server Side Rendering
const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
});

export default function GraphView() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Note: Adjust this to your actual API Base URL if needed
    fetch("http://localhost:8000/api/notes/graph/")
      .then((res) => res.json())
      .then((data) => {
        setGraphData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch graph map:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading Graph View...</div>;

  return (
    <div style={{ border: "1px solid #333", height: "600px", width: "100%", background: "#111" }}>
      {graphData.nodes.length > 0 ? (
        <ForceGraph2D
          graphData={graphData}
          nodeLabel="name" // Hover over nodes to see their Title!
          nodeColor={() => "#4ade80"} // You can make nodes different colors based on type
          nodeAutoColorBy="group"
          linkDirectionalArrowLength={3.5}
          linkDirectionalArrowRelPos={1}
          linkColor={() => "#444"}
          onNodeClick={(node: any) => {
               // Route them to the page when clicked
               window.location.href = `/notes/${node.id}`;
          }}
        />
      ) : (
        <p style={{ color: "white", padding: "1rem" }}>Loading the graph map...</p>
      )}
    </div>
  );
}
```

### 3. Usage

Simply import and drop `<GraphView />` inside any Next.js `page.tsx`!

```tsx
import GraphView from "@/components/GraphView";

export default function Page() {
  return (
    <main>
      <h1>My Vault Graph</h1>
      <GraphView />
    </main>
  );
}
```

You can fully customize the node size, the line colors, and the physics parameters (how fast they pull/repel together) just by attaching properties to the `<ForceGraph2D>` element.
