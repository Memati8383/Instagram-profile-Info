# Instagram Profile Info Tool 📸

Bu araç, Instagram kullanıcı profillerini analiz etmek, istatistikleri çekmek ve profil resimlerini (HD) indirmek için geliştirilmiştir. İki farklı modda çalışabilir: **Hızlı API Modu** ve **Gelişmiş Selenium Modu**.

## 🚀 Özellikler

- 👤 **Kullanıcı Bilgileri:** Tam ad, biyografi, dış bağlantı.
- 📊 **İstatistikler:** Takipçi sayısı, takip edilen sayısı, gönderi sayısı.
- 🔒 **Hesap Durumu:** Gizli hesap ve doğrulanmış (mavi tık) kontrolü.
- 🖼️ **HD Profil Resmi:** Profil fotoğraflarını en yüksek çözünürlükte indirme.
- 💾 **Veri Kaydı:** Çekilen tüm bilgileri `.json` formatında kaydetme.
- 🛡️ **Anti-Detection:** Selenium modunda rastgele User-Agent kullanımı ve headless (arka plan) mod.

## 🛠️ Kurulum

Sistemin çalışması için Python ve Google Chrome yüklü olmalıdır.

1. Depoyu bilgisayarınıza indirin veya klonlayın:

   ```bash
   git clone https://github.com/Memati8383/Instagram-profile-Info.git
   cd Instagram-profile-Info
   ```

2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Kullanım

İki farklı çalışma seçeneğiniz bulunmaktadır:

### 1. Standart Mod (Hızlı)

Bu mod doğrudan Instagram API uç noktalarını kullanır. Çok hızlıdır ancak bazen erişim kısıtlamalarına takılabilir.

```bash
python Main.py
```

### 2. Selenium Modu (Gelişmiş & Arka Plan)

Bu mod gerçek bir tarayıcıyı arka planda (headless) kullanarak verileri çeker. Daha güvenilirdir, anti-blokaj sistemine sahiptir ve profil resimlerini indirebilir.

```bash
python SeleniumMain.py
```

## 📁 Dosya Yapısı

- `Main.py`: Standart API tabanlı sorgulama scripti.
- `SeleniumMain.py`: Gelişmiş, arka planda çalışan Selenium tabanlı script.
- `requirements.txt`: Proje için gerekli Python kütüphaneleri listesi.

## ⚖️ Lisans

Bu proje MIT Lisansı ile lisanslanmıştır.

---

**Geliştirici:** [@Memati8383](https://github.com/Memati8383)
