# MX-UI v2.3.0

پنل مدیریت Xray با VLESS-WebSocket و Trojan-WebSocket.

نسخه ۲.۱: پروتکل Trojan (کنار VLESS) و طراحی جدید لوگو و آیکون‌ها. نسخه ۲: رابط کاربری کاملاً نو، کنترل دسترسی زنده روی هر کانفیگ (بدون ری‌استارت Xray)، محدودیت سرعت، پشتیبان‌گیری/بازیابی JSON، لاگ زنده و صفحه‌ی اشتراک جدید. مشخصات تغییرات در فایل CHANGELOG.md است.

---

## Deploy روی Railway

**۱. Push به GitHub**
```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```

**۲. ساخت پروژه در Railway**
- [railway.app](https://railway.app) → New Project → Deploy from GitHub Repo
- ریپو رو انتخاب کن — Railway خودش Dockerfile رو detect و build می‌کنه

**۳. Volume (توصیه‌شده)**
- Railway → Add Service → Volume → Mount path: `/data`
- بدون Volume داده‌ها بعد از redeploy پاک می‌شن

**۴. اولین ورود**
- آدرس `https://yourapp.railway.app/setup` رو باز کن
- پسورد ادمین رو تنظیم کن

> هیچ environment variable ای لازم نیست.
> `SECRET_KEY` خودکار ساخته می‌شه و در `/data` ذخیره می‌شه.
> SSL به‌صورت خودکار توسط Railway مدیریت می‌شه.

---

## اجرای لوکال

```bash
docker compose up -d
# http://localhost:8080/setup
```
