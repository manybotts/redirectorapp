import os
from aiohttp import web

# Retrieve your bot's username from the environment.
# Make sure to set BOT_USERNAME (without the "@" symbol) in your Heroku config.
BOT_USERNAME = os.environ.get("BOT_USERNAME", "default_bot_username")
if BOT_USERNAME == "default_bot_username":
    print("WARNING: BOT_USERNAME is not set correctly! Please set it in your Heroku config.")

# Handler for favicon requests – return a 204 to avoid 404 errors.
async def favicon_handler(request):
    return web.Response(status=204)

# Main handler for deep-link redirection.
async def redirect_handler(request):
    # Retrieve the "start" query parameter.
    start_param = request.query.get("start")
    if start_param:
        # Build the Telegram deep-link URL.
        deep_link = f"tg://resolve?domain={BOT_USERNAME}&start={start_param}"
        # Build an HTML page that redirects to Telegram.
        html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Launching Telegram...</title>
  <!-- Fallback meta-refresh after 2 seconds -->
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
  <p>Redirecting to Telegram...</p>
  <p>If nothing happens, please <a href="{deep_link}">click here</a>.</p>
</body>
</html>"""
        return web.Response(text=html_content, content_type="text/html")
    else:
        # When no "start" parameter is provided, show a simple message.
        return web.Response(text="Missing 'start' parameter.", content_type="text/plain")

# Create the aiohttp application and register routes.
app = web.Application()
app.router.add_get("/favicon.ico", favicon_handler)  # Handle favicon requests.
app.router.add_get("/", redirect_handler)             # Handle the root URL.
app.router.add_get("/{tail:.*}", redirect_handler)      # Catch-all to handle missing trailing slashes.

if __name__ == '__main__':
    # Heroku automatically sets the PORT environment variable.
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)
