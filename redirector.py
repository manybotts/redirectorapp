import os
from aiohttp import web

# Retrieve the bot's username.
# (You can choose to have this passed as a query parameter too,
#  but for simplicity we use an environment variable.)
BOT_USERNAME = os.environ.get("BOT_USERNAME", "default_bot_username")
if BOT_USERNAME == "default_bot_username":
    print("WARNING: BOT_USERNAME is not set correctly in your Heroku environment!")

async def favicon_handler(request):
    # Avoid 404s for /favicon.ico.
    return web.Response(status=204)

async def redirect_handler(request):
    # Log request info (for debugging).
    full_url = str(request.url)
    query_params = dict(request.query)
    print("DEBUG: Full URL:", full_url)
    print("DEBUG: Query Params:", query_params)
    
    # Expect a "start" query parameter.
    start_param = request.query.get("start")
    if start_param:
        # Build the Telegram deep‑link URL.
        deep_link = f"tg://resolve?domain={BOT_USERNAME}&start={start_param}"
        print("DEBUG: Generated deep-link:", deep_link)
        
        # Return an HTML page that redirects to Telegram.
        html_content = f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Launching Telegram...</title>
    <meta http-equiv="refresh" content="2; url={deep_link}">
    <script type="text/javascript">
      function redirect() {{
          window.location.href = "{deep_link}";
          window.location.replace("{deep_link}");
      }}
      window.onload = function() {{
          setTimeout(redirect, 500);
      }};
    </script>
    <style>
      body {{ font-family: Arial, sans-serif; text-align: center; padding-top: 50px; }}
    </style>
  </head>
  <body>
    <p>Redirecting to Telegram...</p>
    <p>If nothing happens, please <a href="{deep_link}">click here</a>.</p>
  </body>
</html>"""
        return web.Response(text=html_content, content_type="text/html")
    else:
        # If no start parameter is provided, show an error message.
        return web.Response(text="Missing 'start' parameter.", content_type="text/plain")

app = web.Application()
app.router.add_get("/favicon.ico", favicon_handler)
app.router.add_get("/", redirect_handler)
app.router.add_get("/{tail:.*}", redirect_handler)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)
