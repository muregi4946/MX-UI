# Changelog

## 2.2.0

**Protocols**
- VMess (over WebSocket + TLS) and Shadowsocks (over WebSocket + TLS via v2ray-plugin) join VLESS and Trojan.
- Every config can enable any mix of the four. Each protocol gets its own share link and QR, plus the subscription.
- VMess and Shadowsocks paths carry a per-config secret token, so the panel enforces on/off, quota and expiry for them too.
- Shadowsocks passwords are per config. Rotated credentials are re-synced live.

**Design**
- Flat colours throughout (no gradients). Protocol pills, filters and toggles cover all four protocols.

**Responsive**
- Header wraps on small screens, logs and subscription page tighten up on phones, dialogs use the full width on mobile.

## 2.1.1
- Gradients removed, flat palette; responsive fixes on header, logs, subscription page and sign-in.

## 2.1.0

**Protocols**
- Trojan (over WebSocket + TLS) is live next to VLESS. Each config picks VLESS, Trojan, or both.
- Trojan passwords are per config, derived once and stored, so links keep working across restarts.
- Share links: `vless://…` and `trojan://…`, one per protocol per address (domain and pinned IPs).
- Subscriptions include every enabled protocol. Old v2.0 configs migrate to VLESS automatically.
- Trojan users are hot-added and removed through the Xray API, same as VLESS. A rotated password is a remove + add.

**Design**
- New brand mark and wordmark (MX-UI), used in the header, sign-in, subscription page and favicon.
- Icon set rebuilt with a consistent 24px grid, plus protocol marks (VLESS bolt, Trojan shield).
- Dashboard: protocol filter, protocol pills on every row, protocol mix in the hero, per-protocol QR codes.
- Light/dark theme toggle now shows the right glyph in each mode. Logs and dialogs share the same chrome.

**Fixes**
- `/api/qr` requires a session (it was an open QR generator).
- Kubernetes manifests no longer expose ports the panel never listens on (8081–8089, 443).
- `docker-compose.yml` drops unused variables and the NET_ADMIN/SYS_ADMIN capabilities.
- `scripts/start.sh` no longer points at docs that don't exist.

## 2.0.0

**Reliability**
- Panel startup no longer waits for Xray validation or boot.
- Xray outbound DNS and connections prefer IPv4 to avoid slow dual-stack
  fallbacks on Railway and similar hosts.
- Kubernetes defaults to one replica because sessions and Xray state are local.

**Panel**
- Rebuilt dashboard: live throughput scope, 24h traffic chart, system VU meters, filterable config list.
- Subscription page redesigned as a boarding-pass card (QR stub, quota gauge, copy-all).
- Logs page with level/source filters and live tail.
- Light and dark themes, keyboard-friendly dialogs, mobile layout.

**Core**
- Enable/disable, expiry, quota and device limits are enforced at the gateway: toggling a config
  no longer restarts Xray and no longer kicks other users.
- Live sessions are cut within ~5 s when a config is disabled, expires or runs out of data.
- Configs are hot-added and removed through the Xray API; full reload is only a fallback.
- Xray is supervised and restarted automatically if it crashes.
- Per-config speed caps apply to both directions (token bucket).
- Xray API calls fixed: `--server` must come right after the sub-command.
- Blocking spawn moved off the event loop.

**Security**
- Passwords stored with PBKDF2 (v1 hashes upgrade on next login).
- Login rate limiting, HttpOnly + SameSite cookies (Secure behind HTTPS), sessions stored hashed.
- Security headers on HTML responses.

**Subscriptions**
- `/sub/<id>` returns the base64 list for VPN clients and the page for browsers (`?raw` forces the list).
- Standard `subscription-userinfo`, `profile-title` and `profile-update-interval` headers.

**Backup**
- Download and restore (merge or replace) a JSON backup from the dashboard.

## 1.0.0
- Initial release.
