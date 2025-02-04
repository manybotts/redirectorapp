import os
from aiohttp import web

# Retrieve your bot's username from the environment.
# Make sure you set BOT_USERNAME (without the "@" symbol) in your Heroku config.
BOT_USERNAME = os.environ.get("BOT_USERNAME", "default_bot_username")
if BOT_USERNAME == "default_bot_username":
    print("WARNING: BOT_USERNAME is not set correctly in your Heroku environment!")

# Handler for favicon requests – returns a 204 to avoid 404 errors.
async def favicon_handler(request):
    return web.Response(status=204)

# Main handler for deep‑link redirection.
async def redirect_handler(request):
    # Debug: Log incoming request details.
    full_url = str(request.url)
    path = request.path
    query_params = dict(request.query)
    print("DEBUG: Full URL:", full_url)
    print("DEBUG: Path:", path)
    print("DEBUG: Query Params:", query_params)
    
    # Look for the "start" query parameter.
    start_param = request.query.get("start")
    if start_param:
        # Build the Telegram deep‑link.
        deep_link = f"tg://resolve?domain={BOT_USERNAME}&start={start_param}"
        print("DEBUG: Generated deep-link:", deep_link)
        
        # Build an HTML page that attempts to redirect the user to Telegram.
        html_content = f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Launching Telegram...</title>
    <!-- Meta-refresh fallback (2-second delay) -->
    <meta http-equiv="refresh" content="2; url={deep_link}">
    <script type="text/javascript">
      function redirectToTelegram() {{
          window.location.href = "{deep_link}";
          window.location.replace("{deep_link}");
      }}
      window.onload = function() {{
          setTimeout(redirectToTelegram, 500);
      }};
    </script>
    <style>
      body {{
         font-family: Arial, sans-serif;
         text-align: center;
         padding-top: 50px;
      }}
    </style>
  </head>
  <body>
    <p>Attempting to open Telegram...</p>
    <p>If nothing happens, please <a href="{deep_link}">click here</a>.</p>
    <p>(If the page does not close automatically, please close it manually.)</p>
  </body>
</html>"""
        return web.Response(text=html_content, content_type="text/html")
    else:
        # If no "start" parameter is provided, return a helpful message.
        return web.Response(
            text="No 'start' parameter provided. This page is for Telegram deep‑link redirection.",
            content_type="text/plain"
        )

# Create the aiohttp application and register routes.
app = web.Application()
# Handle favicon requests explicitly.
app.router.add_get("/favicon.ico", favicon_handler)
# Register the root route.
app.router.add_get("/", redirect_handler)
# Also register a catch-all route so that a missing trailing slash doesn’t break the query parameter.
app.router.add_get("/{tail:.*}", redirect_handler)

if __name__ == "__main__":
    # Heroku sets the PORT environment variable.
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)
