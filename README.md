## HW4 — Nginx Reverse Proxy

### Verification Steps

**1. nginx is running and proxying to Django:**
```bash
curl -I http://localhost/admin/login/
# Expected: 200 OK with Server: nginx/1.27.5
```

**2. Static files served by nginx with cache:**
```bash
curl -I http://localhost/static/admin/css/base.css
# Expected: 200 OK with Cache-Control: max-age=2592000
```

**3. API returns JSON:**
```bash
curl http://localhost/api/posts/
# Expected: {"count":0,"next":null,"previous":null,"results":[]}
```

**4. nginx returns 502 when web is down:**
```bash
docker compose stop web
curl -I http://localhost/api/posts/
# Expected: 502 Bad Gateway from nginx
docker compose start web
```

**5. Port 8000 is not accessible from host:**
```bash
curl http://localhost:8000/
# Expected: connection refused
```

**6. WebSocket upgrade:**
```bash
wscat -c "ws://localhost/ws/posts/<slug>/comments/?token=<jwt>"
# Expected: 101 Switching Protocols
```