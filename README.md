# Studex — Android APK (Kivy versiyasi)

Bu papka `STUDEX.py` (Tkinter, faqat PC) ilovasining to'liq **Kivy'ga qayta
yozilgan** versiyasi. GitHub Actions yordamida **bepul, avtomatik** ravishda
haqiqiy `.apk` fayl yasab beradi — Linux, WSL yoki Android Studio kerak emas.

## Fayllar

- `main.py` — asosiy ilova (ekranlar, navigatsiya, chat mantiqi)
- `studex.kv` — barcha ekranlarning tashqi ko'rinishi (Kivy layout tili)
- `data.py` — lug'at bazasi (A1-A2: 373 ta, B1-B2: 150 ta, C1-C2: 99 ta so'z)
- `ai.py` — Jo'rabek AI va IELTS Speaking uchun Cerebras API integratsiyasi
- `storage.py` — chat tarixini saqlash va ovozli talaffuz (TTS)
- `buildozer.spec` — APK qanday yig'ilishini belgilaydigan sozlama fayli
- `.github/workflows/build-apk.yml` — GitHub'ning bepul serverida avtomatik
  APK yasab beruvchi ish oqimi (workflow)

## APK'ni olish — qadamlar

1. **GitHub'da yangi repository yarating** (masalan `studex-app`), Public
   yoki Private — farqi yo'q.
2. Shu papkadagi **barcha fayllarni** (yashirin `.github` papkasi bilan
   birga) o'sha repositoryga yuklang. Eng oson yo'li — GitHub'ning veb saytida
   "Add file → Upload files" tugmasidan foydalanib, hamma faylni bir vaqtda
   tashlab yuborish (drag & drop), keyin "Commit changes" bosish.
   - Agar Git terminal orqali qilmoqchi bo'lsangiz:
     ```
     git init
     git add .
     git commit -m "Studex Kivy versiyasi"
     git branch -M main
     git remote add origin https://github.com/FOYDALANUVCHI_NOMI/studex-app.git
     git push -u origin main
     ```
3. Yuklangandan so'ng GitHub avtomatik ravishda **Actions** bo'limida
   qurilishni boshlaydi (chunki workflow fayli shunga sozlangan). Repo
   sahifasida yuqoridagi **"Actions"** tabga o'ting va "Build Studex APK"
   ishga tushganini ko'rasiz.
4. Birinchi marta qurilish (Android SDK/NDK yuklanishi sababli) **15-30
   daqiqa** vaqt olishi mumkin. Keyingi safarlarda tezroq bo'ladi (keshlanadi).
5. Qurilish tugagach (yashil belgi ✅), o'sha ishning sahifasiga kiring,
   pastda **"Artifacts"** bo'limida `studex-apk` degan faylni ko'rasiz —
   shuni yuklab oling, ichida tayyor `.apk` fayl bo'ladi.
6. Telefoningizga o'sha `.apk`ni ko'chirib, o'rnating (noma'lum manbalardan
   o'rnatishga ruxsat berish kerak bo'lishi mumkin).

## Nimalar o'zgardi (Tkinter → Kivy)

- Barcha 6 bo'lim, lug'at bazasi (A1-A2/B1-B2/C1-C2), Flashcard, General
  Dictionary, Jo'rabek AI chat va IELTS Speaking simulyatori **saqlanib
  qoldi**.
- **"Speaking" kartasi endi ishlaydi**: asl kodda IELTS Speaking
  simulyatorining to'liq mantiqi yozilgan edi (`open_speaking`), lekin bosh
  sahifadagi karta unga ulanmagan, "tez orada" degan bo'sh xabar ko'rsatilar
  edi. Kivy versiyasida shu funksiya bosh sahifadagi "Speaking" kartasiga
  ulab qo'yildi.
- Cerebras API kaliti xuddi asl koddagidek ilova ichida saqlangan (`ai.py`).
- Windows SAPI ovoz (`win32com`) o'rniga Android'ning o'z ovozli
  talaffuzidan (`plyer.tts`) foydalaniladi.
- Chat tarixi endi Android'ning ilova uchun ajratilgan xavfsiz papkasida
  (`user_data_dir`) saqlanadi.

## Bilishingiz kerak bo'lgan cheklovlar

- Bu muhitda (mening ishchi konteynerimda) internet yo'q, shuning uchun men
  APK'ni bevosita sinab ko'ra olmadim — Python kodining sintaksisi va
  mantig'i tekshirildi, lekin haqiqiy qurilish va ishga tushirish
  GitHub Actions orqali birinchi marta sodir bo'ladi. Agar xatolik chiqsa,
  "Actions" bo'limidagi qizil ❌ belgisi ustiga bosib, xato matnini menga
  yuborsangiz, tuzataman.
- Orqa fon gradienti (yashil→oq) yo'nalishi teskari chiqib qolishi mumkin —
  bu faqat estetik masala, `main.py`dagi `GRADIENT_TOP`/`GRADIENT_BOTTOM`
  qiymatlarini almashtirib tuzatsa bo'ladi.
- Ilova ikonkasi hozircha standart Kivy ikonkasi — `buildozer.spec` ichida
  ko'rsatma bor, xohlasangiz o'z rasmingizni qo'shishingiz mumkin.
