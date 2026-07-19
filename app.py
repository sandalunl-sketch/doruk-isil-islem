import streamlit as str
import pandas as pd
import os
from datetime import datetime

# Sayfa başlığı ve konfigürasyonu
str.set_page_config(page_title="Doruk Isıl İşlem - Süreç Yönetimi", page_icon="🔥", layout="wide")

# --- DORUK ISIL İŞLEM KURUMSAL KİMLİK TEMASI VE OKUNABİLİRLİK AYARLARI (CSS) ---
str.markdown("""
    <style>
        .stApp {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
        }
        [data-testid="stSidebar"] {
            background-color: #F8FAFC !important;
            border-right: 2px solid #E2E8F0;
        }
        [data-testid="stSidebar"] .stText, [data-testid="stSidebar"] label {
            color: #0F172A !important;
        }
        h1, h2, h3, h4, h5, h6, .stSubheader, p, span, label {
            color: #0F172A !important;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }
        .stTextInput input, .stNumberInput input, .stSelectbox div, .stTextArea textarea, .stDateInput input {
            background-color: #F1F5F9 !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 6px !important;
        }
        div[data-baseweb="select"] div {
            color: #0F172A !important;
        }
        .stDataFrame div, .stDataFrame span, .stDataFrame th, .stDataFrame td {
            color: #0F172A !important;
        }
        div.stButton > button:first-child {
            background-color: #1E40AF !important;
            color: white !important;
            border-radius: 6px !important;
            border: none !important;
            padding: 0.6rem 1.4rem !important;
            font-weight: bold !important;
        }
        div.stButton > button:first-child:hover {
            background-color: #1D4ED8 !important;
        }
        .stAlert {
            background-color: #F0F5FF !important;
            color: #1E3A8A !important;
            border-left: 5px solid #3B82F6 !important;
        }
        .stAlert p {
            color: #1E3A8A !important;
        }
        .firin-kart-bos {
            background-color: #F8FAFC !important;
            padding: 18px;
            border-radius: 8px;
            border: 1px solid #E2E8F0;
            border-top: 5px solid #10B981 !important;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            margin-bottom: 12px;
        }
        .firin-kart-bos h4, .firin-kart-bos p {
            color: #0F172A !important;
        }
        .firin-kart-dolu {
            background-color: #F8FAFC !important;
            padding: 18px;
            border-radius: 8px;
            border: 1px solid #E2E8F0;
            border-top: 5px solid #EA580C !important;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            margin-bottom: 12px;
        }
        .firin-kart-dolu h4, .firin-kart-dolu p, .firin-kart-dolu b {
            color: #0F172A !important;
        }
    </style>
""", unsafe_allow_html=True)

# Klasör ve Dosya Tanımlamaları
SIPARIS_DOSYASI = "siparisler.csv"
BAKIM_DOSYASI = "bakimlar.csv"
RESIM_KLASORU = "resimler"
LOGO_YOLU = "firin_logo.png"

if not os.path.exists(RESIM_KLASORU):
    os.makedirs(RESIM_KLASORU)

# Üretim/Atama İçin Ana Fırın Listesi
FIRIN_LISTESI = ["Kuyu Fırın", "İpsen I", "İpsen II", "Alüminyum Fırın", "Diğer Isıl İşlemciler"]

# Bakım Ekipman Parkuru Listesi
BAKIM_MAKINE_LISTESI = [
    "Kuyu Meneviş Fırını", "Kuyu Önısıtma", "Kuyu Ana Fırın", "Kuyu Yağ Soğutma Banyosu",
    "Kuyu Polimer Soğutma Banyosu", "Kuyu Su Soğutma Banyosu", "İpsen Önısıtma",
    "İpsen Temperleme", "İpsen I", "İpsen II", "Alüminyum Isıl İşlem Fırını",
    "İpsen Yıkama Makinası", "Kompresör", "Isıl İşlem Sepetleri"
]

# Dosya Kontrolleri
if not os.path.exists(SIPARIS_DOSYASI):
    sutunlar = [
        "Sipariş ID", "Tarih", "İrsaliye No", "Müşteri", "Malzeme Adı", 
        "Adet", "Brüt Miktar (KG)", "Dara (KG)", "Net Miktar (KG)", 
        "Birim Fiyat", "Para Birimi", "Toplam Tutar", "Kalite", 
        "Yapılacak İşlem", "İstenen Sertlik", "Termin", "Resim Yolu", "Fırın", "Durum"
    ]
    pd.DataFrame(columns=sutunlar).to_csv(SIPARIS_DOSYASI, index=False)

if not os.path.exists(BAKIM_DOSYASI):
    bakim_sutunlari = ["Bakım Tarihi", "Fırın/Makine Birimi", "Bakım Türü", "Yapılan İşlem / Açıklama", "Bakımı Yapan", "Maliyet (TL)"]
    pd.DataFrame(columns=bakim_sutunlari).to_csv(BAKIM_DOSYASI, index=False)

df_mevcut = pd.read_csv(SIPARIS_DOSYASI)
df_bakimlar = pd.read_csv(BAKIM_DOSYASI)

# --- OTOMATİK SIRALI SİPARİŞ NO ÜRETİMİ ---
if df_mevcut.empty:
    yeni_siparis_no = "DRK0000001"
else:
    try:
        son_id = df_mevcut.iloc[-1]["Sipariş ID"]
        sayisal_kisim = int(son_id.replace("DRK", ""))
        yeni_siparis_no = f"DRK{sayisal_kisim + 1:07d}"
    except:
        yeni_siparis_no = f"DRK{len(df_mevcut) + 1:07d}"

# --- GEÇMİŞ VERİLERDEN AKILLI ÖNERİ LİSTELERİNİN HAZIRLANMASI ---
def liste_hazirla(sutun_adi):
    liste = [""]
    if not df_mevcut.empty:
        benzersizler = df_mevcut[sutun_adi].dropna().unique().tolist()
        liste.extend(benzersizler)
    liste.append("+ Yeni Ekle / Manuel Yaz")
    return liste

kayitli_musteriler = liste_hazirla("Müşteri")
kayitli_malzemeler = liste_hazirla("Malzeme Adı")
kayitli_kaliteler = liste_hazirla("Kalite")
kayitli_sertlikler = liste_hazirla("İstenen Sertlik")

if os.path.exists(LOGO_YOLU):
    str.sidebar.image(LOGO_YOLU, use_container_width=True)
else:
    str.sidebar.warning("Logo bulunamadı (firin_logo.png)")

menu = ["Ana Sayfa", "Sipariş Kayıt", "Fırın & Proses Takip", "Bakım", "Satın Alma", "Yönetim"]
secim = str.sidebar.selectbox("Gitmek İstediğiniz Modül", menu)

# --- MODÜL 1: ANA SAYFA ---
if secim == "Ana Sayfa":
    col_logo, col_baslik = str.columns([1, 5])
    with col_logo:
        if os.path.exists(LOGO_YOLU):
            str.image(LOGO_YOLU, width=120)
    with col_baslik:
        str.markdown("# 🏭 Doruk Isıl İşlem Otomasyon Merkezi")
        str.markdown("<p style='color: #475569;'>Fabrika içi anlık proses, sipariş havuzu ve fırın hatları izleme paneli.</p>", unsafe_allow_html=True)
    
    str.write("---")
    str.subheader("📊 Operasyonel Göstergeler")
    col1, col2, col3 = str.columns(3)
    col1.metric("Toplam Kayıtlı Sipariş", len(df_mevcut))
    col2.metric("Aktif Şarj (Fırındakiler)", len(df_mevcut[df_mevcut["Durum"] == "İşlemde"]) if not df_mevcut.empty else 0)
    col3.metric("Kayıtlı Toplam Bakım Faaliyeti", len(df_bakimlar))

# --- MODÜL 2: SİPARİŞ KAYIT ---
elif secim == "Sipariş Kayıt":
    str.markdown("## 📋 Yeni Sipariş Kayıt Formu")
    col_ust1, col_ust2, col_ust3 = str.columns(3)
    with col_ust1:
        str.info(f"📌 **Sipariş No:** {yeni_siparis_no}")
        bugun_tarihi = datetime.now().strftime("%d.%m.%Y")
        str.text_input("Sipariş Tarihi", value=bugun_tarihi, disabled=True)
    with col_ust2:
        musteri_secim = str.selectbox("Müşteri / Firma", options=kayitli_musteriler)
        musteri = str.text_input("Yeni Müşteri Adı") if musteri_secim == "+ Yeni Ekle / Manuel Yaz" else musteri_secim
        irsaliye_no = str.text_input("İrsaliye No")
    with col_ust3:
        termin_secimi = str.checkbox("Termin Tarihi Belirle", value=False)
        termin = str.date_input("Termin Tarihi").strftime("%d.%m.%Y") if termin_secimi else "Atanmadı"
    
    str.markdown("### 🔍 Malzeme ve Proses Detayları")
    col_detay1, col_detay2, col_detay3 = str.columns(3)
    with col_detay1:
        malzeme_secim = str.selectbox("Malzeme Adı / Parça Seçin", options=kayitli_malzemeler)
        malzeme_adi = str.text_input("Yeni Malzeme/Parça Adı Yazın") if malzeme_secim == "+ Yeni Ekle / Manuel Yaz" else malzeme_secim
        kalite_secim = str.selectbox("Malzeme Kalitesi (Çelik Cinsi) Seçin", options=kayitli_kaliteler)
        kalite = str.text_input("Yeni Çelik Kalitesi Yazın") if kalite_secim == "+ Yeni Ekle / Manuel Yaz" else kalite_secim
        
        # --- İSTEKLERİNİZE GÖRE PROSES LİSTESİ GÜNCELLENDİ ---
        yapilacak_islem = str.selectbox("Uygulanacak İşlem", [
            "KARBON EMDİRME", "VAKUM SERTLEŞTİRME", "T4", "T6",
            "YAY ÇELİĞİ SERTLEŞTİRME", "SEMENTASYON", "ISLAH (SERTLEŞTİRME)", 
            "NİTRASYON", "NORMALİZASYON", "GERİLİM GİDERME", "TAVLAMA"
        ])
        
        sertlik_secim = str.selectbox("İstenen Sertlik Değeri Seçin", options=kayitli_sertlikler)
        istenen_sertlik = str.text_input("Yeni Sertlik Değeri Yazın") if sertlik_secim == "+ Yeni Ekle / Manuel Yaz" else sertlik_secim
    with col_detay2:
        adet = str.number_input("Adet", min_value=1, value=1)
        brut_kg = str.number_input("Brüt Miktar (KG)", min_value=0.0, value=0.0)
        dara_kg = str.number_input("Dara (KG)", min_value=0.0, value=0.0)
        net_kg = brut_kg - dara_kg
        str.markdown(f"<p style='color:#1E40AF; font-weight:bold;'>Hesaplanan Net Ağırlık: {net_kg:.2f} KG</p>", unsafe_allow_html=True)
    with col_detay3:
        fiyat = str.number_input("Birim Fiyat", min_value=0.0, value=0.0)
        para_birimi = str.selectbox("Para Birimi", ["TL (₺)", "USD ($)", "EURO (€)"])
        toplam_tutar = net_kg * fiyat
        str.markdown(f"<p style='color:#1E40AF; font-weight:bold;'>Toplam Tutar: {toplam_tutar:.2f} {para_birimi}</p>", unsafe_allow_html=True)
        yuklenen_resim = str.file_uploader("Malzeme Fotoğrafı Yükle", type=["jpg", "jpeg", "png"])

    if str.button("Siparişi Kaydet ve Onayla", type="primary"):
        if musteri and malzeme_adi and kalite and istenen_sertlik:
            resim_yolu = "Resim Yok"
            if yuklenen_resim is not None:
                resim_yolu = os.path.join(RESIM_KLASORU, f"{yeni_siparis_no}.png")
                with open(resim_yolu, "wb") as f:
                    f.write(yuklenen_resim.getbuffer())
            
            yeni_veri = {
                "Sipariş ID": yeni_siparis_no, "Tarih": bugun_tarihi, "İrsaliye No": irsaliye_no if irsaliye_no else "Girilmedi",
                "Müşteri": musteri, "Malzeme Adı": malzeme_adi, "Adet": adet, "Brüt Miktar (KG)": brut_kg, "Dara (KG)": dara_kg,
                "Net Miktar (KG)": net_kg, "Birim Fiyat": fiyat, "Para Birimi": para_birimi, "Toplam Tutar": toplam_tutar,
                "Kalite": kalite, "Yapılacak İşlem": yapilacak_islem, "İstenen Sertlik": istenen_sertlik, "Termin": termin,
                "Resim Yolu": resim_yolu, "Fırın": "Atanmadı", "Durum": "Başlanmadı"
            }
            df_son = pd.concat([df_mevcut, pd.DataFrame([yeni_veri])], ignore_index=True)
            df_son.to_csv(SIPARIS_DOSYASI, index=False)
            str.success(f"Sipariş başarıyla kaydedildi! No: {yeni_siparis_no}")
            str.rerun()

    str.write("---")
    str.markdown("### 🗂️ Doruk Isıl İşlem Güncel Kabul Havuzu")
    if not df_mevcut.empty:
        str.dataframe(df_mevcut, column_config={"Resim Yolu": str.column_config.ImageColumn("Resim")}, use_container_width=True)

# --- MODÜL 3: FIRIN & PROSES TAKİP ---
elif secim == "Fırın & Proses Takip":
    str.markdown("## ⚙️ Fırın Şarj ve Proses Kontrolü")
    str.markdown("### 📥 Siparişi Fırın Hatlarına Dağıt")
    df_bekleyen = df_mevcut[df_mevcut["Durum"] == "Başlanmadı"]
    
    if not df_bekleyen.empty:
        col_ata1, col_ata2, col_ata3 = str.columns(3)
        with col_ata1:
            secilen_siparis = str.selectbox("Şarja Alınacak Sipariş", df_bekleyen["Sipariş ID"])
            detay = df_bekleyen[df_bekleyen["Sipariş ID"] == secilen_siparis].iloc[0]
            str.markdown(f"<small style='color:#475569;'>Müşteri: {detay['Müşteri']} | Malzeme: {detay['Malzeme Adı']}</small>", unsafe_allow_html=True)
        with col_ata2:
            secilen_firin = str.selectbox("Operasyon Fırını", FIRIN_LISTESI)
        with col_ata3:
            yeni_termin = str.date_input("Termin Onayla")
            
        if str.button("Prosesi Başlat (Şarjı Fırına Ver)", type="primary"):
            df_mevcut.loc[df_mevcut["Sipariş ID"] == secilen_siparis, "Fırın"] = secilen_firin
            df_mevcut.loc[df_mevcut["Sipariş ID"] == secilen_siparis, "Durum"] = "İşlemde"
            df_mevcut.loc[df_mevcut["Sipariş ID"] == secilen_siparis, "Termin"] = yeni_termin.strftime("%d.%m.%Y")
            df_mevcut.to_csv(SIPARIS_DOSYASI, index=False)
            str.success(f"Proses Başladı! {secilen_siparis} -> {secilen_firin}")
            str.rerun()
            
    str.write("---")
    str.markdown("### 🏭 Fırın Hatları Anlık Durum Paneli")
    df_islemde = df_mevcut[df_mevcut["Durum"] == "İşlemde"]
    firin_cols = str.columns(len(FIRIN_LISTESI))
    
    for i, firin_adi in enumerate(FIRIN_LISTESI):
        with firin_cols[i]:
            firin_isleri = df_islemde[df_islemde["Fırın"] == firin_adi]
            if not firin_isleri.empty:
                for index, sira in firin_isleri.iterrows():
                    str.markdown(f"""
                        <div class="firin-kart-dolu">
                            <h4 style="color:#EA580C; margin:0;">🔥 {firin_adi}</h4>
                            <p style="margin:8px 0 0 0; font-size:14px;"><b>No:</b> {sira['Sipariş ID']}</p>
                            <p style="margin:2px 0 0 0; font-size:13px;"><b>Firma:</b> {sira['Müşteri']}</p>
                            <p style="margin:2px 0 0 0; font-size:13px; color:#1E40AF;"><b>İşlem:</b> {sira['Yapılacak İşlem']}</p>
                            <p style="margin:2px 0 0 0; font-size:13px;"><b>Yük:</b> {sira['Net Miktar (KG)']} KG</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if str.button(f"Prosesi Bitir ({sira['Sipariş ID']})", key=sira['Sipariş ID']):
                        df_mevcut.loc[df_mevcut["Sipariş ID"] == sira['Sipariş ID'], "Durum"] = "Tamamlandı"
                        df_mevcut.to_csv(SIPARIS_DOSYASI, index=False)
                        str.rerun()
            else:
                str.markdown(f"""
                    <div class="firin-kart-bos">
                        <h4 style="color:#10B981; margin:0;">🟢 {firin_adi}</h4>
                        <p style="margin:10px 0 0 0; font-size:13px; color:#475569;">Fırın müsait, şarj yüklenebilir.</p>
                    </div>
                """, unsafe_allow_html=True)

# --- MODÜL 4: BAKIM ---
elif secim == "Bakım":
    str.markdown("## 🔧 Fırın Bakım ve Arıza Kayıt Yönetimi")
    col_b1, col_b2 = str.columns(2)
    with col_b1:
        bakim_tarihi = str.date_input("Bakım / Arıza Tarihi", value=datetime.today())
        secilen_makine = str.selectbox("Bakım Gören Fırın / Makine Birimi", BAKIM_MAKINE_LISTESI)
        bakim_turu = str.radio("Bakım Türü", ["Periyodik (Planlı) Bakım", "Arıza (Plansız) Bakım"])
    with col_b2:
        bakimi_yapan = str.text_input("Bakımı Yapan Tekniker / Firma")
        bakim_maliyeti = str.number_input("Bakım Maliyeti (TL)", min_value=0.0, value=0.0, step=50.0)
        yapilan_islem = str.text_area("Yapılan İşlem ve Değişen Parçaların Detayı")
        
    if str.button("Bakım Kaydını Sisteme İşle", type="primary"):
        if yapilan_islem and bakimi_yapan:
            yeni_bakim = {
                "Bakım Tarihi": bakim_tarihi.strftime("%d.%m.%Y"), "Fırın/Makine Birimi": secilen_makine,
                "Bakım Türü": bakim_turu, "Yapılan İşlem / Açıklama": yapilan_islem, "Bakımı Yapan": bakimi_yapan, "Maliyet (TL)": bakim_maliyeti
            }
            df_bakim_son = pd.concat([df_bakimlar, pd.DataFrame([yeni_bakim])], ignore_index=True)
            df_bakim_son.to_csv(BAKIM_DOSYASI, index=False)
            str.success(f"✔️ {secilen_makine} için bakım kaydı başarıyla hafızaya alındı!")
            str.rerun()

    str.write("---")
    str.markdown("### 🗂️ Geçmiş Fırın Bakım Geçmişi")
    if not df_bakimlar.empty:
        filtre_secenekleri = ["Tümü"] + BAKIM_MAKINE_LISTESI
        filtre_firin = str.selectbox("Fırın Birimine Göre Filtrele", filtre_secenekleri)
        df_filtreli = df_bakimlar if filtre_firin == "Tümü" else df_bakimlar[df_bakimlar["Fırın/Makine Birimi"] == filtre_firin]
        toplam_maliyet = df_filtreli["Maliyet (TL)"].sum()
        str.markdown(f"<p style='color:#EA580C; font-size:16px; font-weight:bold;'>💰 Toplam Bakım Gideri: {toplam_maliyet:,.2f} TL</p>", unsafe_allow_html=True)
        str.dataframe(df_filtreli, use_container_width=True)
    else:
        str.info("Sistemde henüz kayıtlı bir fırın bakım faaliyeti bulunmamaktadır.")

# --- DİĞER MODÜLLER ---
elif secim == "Satın Alma":
    str.markdown("## 🛒 Kimyasal ve Yedek Parça Satın Alma")
elif secim == "Yönetim":
    str.markdown("## 📊 Üretim Verimlilik Raporları")