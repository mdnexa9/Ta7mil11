const SECURITY_HEADERS = {
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "X-Frame-Options": "SAMEORIGIN",
  "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/healthz") {
      return new Response("ok", { headers: { "content-type": "text/plain; charset=utf-8" } });
    }

    // Short, stable link for the Play data-deletion policy field.
    if (url.pathname === "/data-deletion" || url.pathname === "/delete-data") {
      return Response.redirect(new URL("/#delete-data", url).toString(), 301);
    }

    const response = await env.ASSETS.fetch(request);

    // Keep deep links working: unknown HTML paths fall back to the page.
    if (
      response.status === 404 &&
      request.method === "GET" &&
      (request.headers.get("accept") || "").includes("text/html")
    ) {
      const fallback = await env.ASSETS.fetch(new URL("/index.html", url));
      if (fallback.status === 200) {
        return new Response(fallback.body, {
          status: 200,
          headers: { ...SECURITY_HEADERS, "content-type": "text/html; charset=utf-8" },
        });
      }
    }

    const headers = new Headers(response.headers);
    for (const [name, value] of Object.entries(SECURITY_HEADERS)) headers.set(name, value);

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers,
    });
  },
};
