import streamlit as st
import pandas as pd
import os
import hashlib
import io
import zipfile
import base64
from datetime import datetime

# Sayfa başlığı ve konfigürasyonu
st.set_page_config(page_title="Doruk Isıl İşlem - Süreç Yönetimi", page_icon="🔥", layout="wide")

# --- DORUK ISIL İŞLEM KURUMSAL KİMLİK TEMASI VE OKUNABİLİRLİK AYARLARI (CSS) ---
st.markdown("""
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

/* --- GENEL SAYFA TASARIM İYİLEŞTİRMELERİ --- */
h2 {
    border-bottom: 3px solid #1E40AF;
    padding-bottom: 10px;
    margin-bottom: 20px !important;
}
h3 {
    color: #1E40AF !important;
    margin-top: 10px !important;
}
[data-testid="stMetric"] {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-left: 5px solid #1E40AF;
    border-radius: 10px;
    padding: 16px 18px;
    box-shadow: 0 2px 4px -1px rgba(0,0,0,0.04);
}
[data-testid="stMetricLabel"] {
    color: #475569 !important;
    font-weight: 600;
}
[data-testid="stMetricValue"] {
    color: #1E40AF !important;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 2px 6px -2px rgba(0,0,0,0.06) !important;
    padding: 6px 4px !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
}
.stTabs [data-baseweb="tab"] {
    background-color: #F1F5F9;
    border-radius: 8px 8px 0 0;
    padding: 8px 18px;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background-color: #1E40AF !important;
    color: white !important;
}
.stTabs [aria-selected="true"] p {
    color: white !important;
}
.stDataFrame {
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
div[data-testid="stDataFrame"] thead tr th {
    background-color: #1E40AF !important;
    color: white !important;
}
hr {
    margin: 1.4rem 0 !important;
}
</style>
""", unsafe_allow_html=True)

# Klasör ve Dosya Tanımlamaları
SIPARIS_DOSYASI = "siparisler.csv"
BAKIM_DOSYASI = "bakimlar.csv"
SATINALMA_DOSYASI = "satinalmalar.csv"
KULLANICI_DOSYASI = "kullanicilar.csv"
FIRIN_DOSYASI = "firinlar.csv"
RESIM_KLASORU = "resimler"
LOGO_YOLU = "firin_logo.png"

if not os.path.exists(RESIM_KLASORU):
    os.makedirs(RESIM_KLASORU)

# Sabit Listeler
BAKIM_MAKINE_LISTESI = [
    "Kuyu Meneviş Fırını", "Kuyu Önısıtma", "Kuyu Ana Fırın", "Kuyu Yağ Soğutma Banyosu",
    "Kuyu Polimer Soğutma Banyosu", "Kuyu Su Soğutma Banyosu", "İpsen Önısıtma",
    "İpsen Temperleme", "İpsen I", "İpsen II", "Alüminyum Isıl İşlem Fırını",
    "İpsen Yıkama Makinası", "Kompresör", "Isıl İşlem Sepetleri"
]

VARSAYILAN_FIRINLAR = ["Kuyu Fırın", "İpsen I", "İpsen II", "Alüminyum Fırın", "Diğer Isıl İşlemciler"]

# --- YARDIMCI FONKSİYONLAR ---
def sifre_hashle(sifre):
    return hashlib.sha256(sifre.encode()).hexdigest()

def logo_goster(genislik_px, konteyner=None, ortala=True):
    konteyner = konteyner if konteyner is not None else st
    if os.path.exists(LOGO_YOLU):
        with open(LOGO_YOLU, "rb") as f:
            b64_veri = base64.b64encode(f.read()).decode()
        stil_ortala = "display:block; margin-left:auto; margin-right:auto;" if ortala else "display:block;"
        konteyner.markdown(
            f"<img src='data:image/png;base64,{b64_veri}' "
            f"style='width:{genislik_px}px; height:{genislik_px}px; border-radius:50%; "
            f"object-fit:cover; {stil_ortala}' />",
            unsafe_allow_html=True
        )
    else:
        konteyner.warning("Logo bulunamadı (firin_logo.png)")

def dosya_kontrol(dosya_adi, sutunlar):
    if not os.path.exists(dosya_adi):
        pd.DataFrame(columns=sutunlar).to_csv(dosya_adi, index=False)

dosya_kontrol(SIPARIS_DOSYASI, ["Sipariş ID", "Tarih", "İrsaliye No", "Müşteri", "Malzeme Adı", "Adet", "Brüt Miktar (KG)", "Dara (KG)", "Net Miktar (KG)", "Birim Fiyat", "Para Birimi", "Toplam Tutar", "Kalite", "Yapılacak İşlem", "İstenen Sertlik", "Termin", "Resim Yolu", "Fırın", "Durum"])
dosya_kontrol(BAKIM_DOSYASI, ["Bakım Tarihi", "Fırın/Makine Birimi", "Bakım Türü", "Yapılan İşlem / Açıklama", "Bakımı Yapan", "Maliyet (TL)"])
dosya_kontrol(SATINALMA_DOSYASI, ["Talep No", "Tarih", "Malzeme Adı", "Miktar", "Birim", "Aciliyet", "Birim Fiyat", "Tahmini Tutar", "Para Birimi", "Açıklama", "Durum"])
dosya_kontrol(FIRIN_DOSYASI, ["Fırın Adı", "Eklenme Tarihi"])
dosya_kontrol(KULLANICI_DOSYASI, ["Kullanıcı Adı", "Şifre Hash", "Ad Soyad", "Yetki"])

# Fırınlar dosyası boşsa varsayılan fırınları ekle
df_firinlar_ilk = pd.read_csv(FIRIN_DOSYASI)
if df_firinlar_ilk.empty:
    df_firinlar_ilk = pd.DataFrame({
        "Fırın Adı": VARSAYILAN_FIRINLAR,
        "Eklenme Tarihi": [datetime.now().strftime("%d.%m.%Y")] * len(VARSAYILAN_FIRINLAR)
    })
    df_firinlar_ilk.to_csv(FIRIN_DOSYASI, index=False)

# Kullanıcılar dosyası boşsa varsayılan admin kullanıcısı ekle
df_kullanicilar_ilk = pd.read_csv(KULLANICI_DOSYASI)
if df_kullanicilar_ilk.empty:
    df_kullanicilar_ilk = pd.DataFrame([{
        "Kullanıcı Adı": "admin",
        "Şifre Hash": sifre_hashle("admin123"),
        "Ad Soyad": "Sistem Yöneticisi",
        "Yetki": "Admin"
    }])
    df_kullanicilar_ilk.to_csv(KULLANICI_DOSYASI, index=False)

# --- GİRİŞ (LOGIN) KONTROLÜ ---
if "giris_yapildi" not in st.session_state:
    st.session_state["giris_yapildi"] = False
    st.session_state["kullanici_adi"] = ""
    st.session_state["kullanici_yetki"] = ""
    st.session_state["kullanici_adsoyad"] = ""

if not st.session_state["giris_yapildi"]:
    col_bos1, col_orta, col_bos2 = st.columns([1, 1.2, 1])
    with col_orta:
        logo_goster(64)
        st.markdown("## 🔒 Doruk Isıl İşlem - Giriş")
        giris_kullanici = st.text_input("Kullanıcı Adı")
        giris_sifre = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap", type="primary"):
            df_kul = pd.read_csv(KULLANICI_DOSYASI)
            eslesen = df_kul[
                (df_kul["Kullanıcı Adı"] == giris_kullanici) &
                (df_kul["Şifre Hash"] == sifre_hashle(giris_sifre))
            ]
            if not eslesen.empty:
                st.session_state["giris_yapildi"] = True
                st.session_state["kullanici_adi"] = giris_kullanici
                st.session_state["kullanici_yetki"] = eslesen.iloc[0]["Yetki"]
                st.session_state["kullanici_adsoyad"] = eslesen.iloc[0]["Ad Soyad"]
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı.")
    st.stop()

# Fırın listesini CSV'den dinamik olarak yükle
df_firinlar = pd.read_csv(FIRIN_DOSYASI)
FIRIN_LISTESI = df_firinlar["Fırın Adı"].dropna().tolist()

df_mevcut = pd.read_csv(SIPARIS_DOSYASI)
df_bakimlar = pd.read_csv(BAKIM_DOSYASI)
df_satinalmalar = pd.read_csv(SATINALMA_DOSYASI)

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

# --- OTOMATİK SATIN ALMA TALEP NO ÜRETİMİ ---
if df_satinalmalar.empty:
    yeni_talep_no = "TLP0001"
else:
    try:
        son_tlp = df_satinalmalar.iloc[-1]["Talep No"]
        tlp_sayi = int(son_tlp.replace("TLP", ""))
        yeni_talep_no = f"TLP{tlp_sayi + 1:04d}"
    except:
        yeni_talep_no = f"TLP{len(df_satinalmalar) + 1:04d}"

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

logo_goster(80, konteyner=st.sidebar)

st.sidebar.markdown(f"👤 **{st.session_state['kullanici_adsoyad']}**  \n`{st.session_state['kullanici_yetki']}`")
if st.sidebar.button("Çıkış Yap"):
    st.session_state["giris_yapildi"] = False
    st.rerun()
st.sidebar.write("---")

menu = ["Ana Sayfa", "Sipariş Kayıt", "Fırın & Proses Takip", "Bakım", "Satın Alma", "Raporlama"]
if st.session_state["kullanici_yetki"] == "Admin":
    menu.append("Yönetim")

secim = st.sidebar.selectbox("Gitmek İstediğiniz Modül", menu)

# --- MODÜL 1: ANA SAYFA ---
if secim == "Ana Sayfa":
    col_logo, col_baslik = st.columns([1, 5])
    with col_logo:
        logo_goster(48, ortala=False)
    with col_baslik:
        st.markdown("# 🏭 Doruk Isıl İşlem Otomasyon Merkezi")
        st.markdown("<p style='color: #475569;'>Fabrika içi anlık proses, sipariş havuzu ve fırın hatları izleme paneli.</p>", unsafe_allow_html=True)
    st.write("---")
    st.subheader("📊 Operasyonel Göstergeler")
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Kayıtlı Sipariş", len(df_mevcut))
    col2.metric("Aktif Şarj (Fırındakiler)", len(df_mevcut[df_mevcut["Durum"] == "İşlemde"]) if not df_mevcut.empty else 0)
    col3.metric("Bekleyen Satın Alma Talepleri", len(df_satinalmalar[df_satinalmalar["Durum"] == "Beklemede"]) if not df_satinalmalar.empty else 0)

# --- MODÜL 2: SİPARİŞ KAYIT ---
elif secim == "Sipariş Kayıt":
    st.markdown("## 📋 Yeni Sipariş Kayıt Formu")
    col_ust1, col_ust2, col_ust3 = st.columns(3)
    with col_ust1:
        st.info(f"📌 **Sipariş No:** {yeni_siparis_no}")
        bugun_tarihi = datetime.now().strftime("%d.%m.%Y")
        st.text_input("Sipariş Tarihi", value=bugun_tarihi, disabled=True)
    with col_ust2:
        musteri_secim = st.selectbox("Müşteri / Firma", options=kayitli_musteriler)
        musteri = st.text_input("Yeni Müşteri Adı") if musteri_secim == "+ Yeni Ekle / Manuel Yaz" else musteri_secim
        irsaliye_no = st.text_input("İrsaliye No")
    with col_ust3:
        termin_secimi = st.checkbox("Termin Tarihi Belirle", value=False)
        termin = st.date_input("Termin Tarihi").strftime("%d.%m.%Y") if termin_secimi else "Atanmadı"

    st.markdown("### 🔍 Malzeme ve Proses Detayları")
    col_detay1, col_detay2, col_detay3 = st.columns(3)
    with col_detay1:
        malzeme_secim = st.selectbox("Malzeme Adı / Parça Seçin", options=kayitli_malzemeler)
        malzeme_adi = st.text_input("Yeni Malzeme/Parça Adı Yazın") if malzeme_secim == "+ Yeni Ekle / Manuel Yaz" else malzeme_secim
        kalite_secim = st.selectbox("Malzeme Kalitesi (Çelik Cinsi) Seçin", options=kayitli_kaliteler)
        kalite = st.text_input("Yeni Çelik Kalitesi Yazın") if kalite_secim == "+ Yeni Ekle / Manuel Yaz" else kalite_secim
        yapilacak_islem = st.selectbox("Uygulanacak İşlem", ["KARBON EMDİRME", "VAKUM SERTLEŞTİRME", "T4", "T6", "YAY ÇELİĞİ SERTLEŞTİRME", "SEMENTASYON", "ISLAH (SERTLEŞTİRME)", "NİTRASYON", "NORMALİZASYON", "GERİLİM GİDERME", "TAVLAMA"])
        sertlik_secim = st.selectbox("İstenen Sertlik Değeri Seçin", options=kayitli_sertlikler)
        istenen_sertlik = st.text_input("Yeni Sertlik Değeri Yazın") if sertlik_secim == "+ Yeni Ekle / Manuel Yaz" else sertlik_secim
    with col_detay2:
        adet = st.number_input("Adet", min_value=1, value=1)
        brut_kg = st.number_input("Brüt Miktar (KG)", min_value=0.0, value=0.0)
        dara_kg = st.number_input("Dara (KG)", min_value=0.0, value=0.0)
        net_kg = brut_kg - dara_kg
        st.markdown(f"<p style='color:#1E40AF; font-weight:bold;'>Hesaplanan Net Ağırlık: {net_kg:.2f} KG</p>", unsafe_allow_html=True)
    with col_detay3:
        fiyat = st.number_input("Birim Fiyat", min_value=0.0, value=0.0)
        para_birimi = st.selectbox("Para Birimi", ["TL (₺)", "USD ($)", "EURO (€)"])
        toplam_tutar = net_kg * fiyat
        st.markdown(f"<p style='color:#1E40AF; font-weight:bold;'>Toplam Tutar: {toplam_tutar:.2f} {para_birimi}</p>", unsafe_allow_html=True)

    yuklenen_resim = st.file_uploader("Malzeme Fotoğrafı Yükle", type=["jpg", "jpeg", "png"])

    if st.button("Siparişi Kaydet ve Onayla", type="primary"):
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
            st.success(f"Sipariş başarıyla kaydedildi! No: {yeni_siparis_no}")
            st.rerun()

    st.write("---")
    st.markdown("### 🗂️ Doruk Isıl İşlem Güncel Kabul Havuzu")
    if not df_mevcut.empty:
        st.dataframe(df_mevcut, column_config={"Resim Yolu": st.column_config.ImageColumn("Resim")}, use_container_width=True)

# --- MODÜL 3: FIRIN & PROSES TAKİP ---
elif secim == "Fırın & Proses Takip":
    st.markdown("## ⚙️ Fırın Şarj ve Proses Kontrolü")
    st.markdown("### 📥 Siparişi Fırın Hatlarına Dağıt")
    df_bekleyen = df_mevcut[df_mevcut["Durum"] == "Başlanmadı"]
    if not df_bekleyen.empty:
        col_ata1, col_ata2, col_ata3 = st.columns(3)
        with col_ata1:
            secilen_siparis = st.selectbox("Şarja Alınacak Sipariş", df_bekleyen["Sipariş ID"])
            detay = df_bekleyen[df_bekleyen["Sipariş ID"] == secilen_siparis].iloc[0]
            st.markdown(f"<small style='color:#475569;'>Müşteri: {detay['Müşteri']} | Malzeme: {detay['Malzeme Adı']}</small>", unsafe_allow_html=True)
        with col_ata2:
            secilen_firin = st.selectbox("Operasyon Fırını", FIRIN_LISTESI)
        with col_ata3:
            yeni_termin = st.date_input("Termin Onayla")
        if st.button("Prosesi Başlat (Şarjı Fırına Ver)", type="primary"):
            df_mevcut.loc[df_mevcut["Sipariş ID"] == secilen_siparis, "Fırın"] = secilen_firin
            df_mevcut.loc[df_mevcut["Sipariş ID"] == secilen_siparis, "Durum"] = "İşlemde"
            df_mevcut.loc[df_mevcut["Sipariş ID"] == secilen_siparis, "Termin"] = yeni_termin.strftime("%d.%m.%Y")
            df_mevcut.to_csv(SIPARIS_DOSYASI, index=False)
            st.success(f"Proses Başladı! {secilen_siparis} -> {secilen_firin}")
            st.rerun()

    st.write("---")
    st.markdown("### 🏭 Fırın Hatları Anlık Durum Paneli")
    df_islemde = df_mevcut[df_mevcut["Durum"] == "İşlemde"]
    firin_cols = st.columns(len(FIRIN_LISTESI)) if FIRIN_LISTESI else []
    for i, firin_adi in enumerate(FIRIN_LISTESI):
        with firin_cols[i]:
            firin_isleri = df_islemde[df_islemde["Fırın"] == firin_adi]
            if not firin_isleri.empty:
                for index, sira in firin_isleri.iterrows():
                    st.markdown(f"""
                    <div class="firin-kart-dolu">
                        <h4 style="color:#EA580C; margin:0;">🔥 {firin_adi}</h4>
                        <p style="margin:8px 0 0 0; font-size:14px;"><b>No:</b> {sira['Sipariş ID']}</p>
                        <p style="margin:2px 0 0 0; font-size:13px;"><b>Firma:</b> {sira['Müşteri']}</p>
                        <p style="margin:2px 0 0 0; font-size:13px; color:#1E40AF;"><b>İşlem:</b> {sira['Yapılacak İşlem']}</p>
                        <p style="margin:2px 0 0 0; font-size:13px;"><b>Yük:</b> {sira['Net Miktar (KG)']} KG</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Prosesi Bitir ({sira['Sipariş ID']})", key=sira['Sipariş ID']):
                        df_mevcut.loc[df_mevcut["Sipariş ID"] == sira['Sipariş ID'], "Durum"] = "Tamamlandı"
                        df_mevcut.to_csv(SIPARIS_DOSYASI, index=False)
                        st.rerun()
            else:
                st.markdown(f"""
                <div class="firin-kart-bos">
                    <h4 style="color:#10B981; margin:0;">🟢 {firin_adi}</h4>
                    <p style="margin:10px 0 0 0; font-size:13px; color:#475569;">Fırın müsait, şarj yüklenebilir.</p>
                </div>
                """, unsafe_allow_html=True)

# --- MODÜL 4: BAKIM ---
elif secim == "Bakım":
    st.markdown("## 🔧 Fırın Bakım ve Arıza Kayıt Yönetimi")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        bakim_tarihi = st.date_input("Bakım / Arıza Tarihi", value=datetime.today())
        secilen_makine = st.selectbox("Bakım Gören Fırın / Makine Birimi", BAKIM_MAKINE_LISTESI)
        bakim_turu = st.radio("Bakım Türü", ["Periyodik (Planlı) Bakım", "Arıza (Plansız) Bakım"])
    with col_b2:
        bakimi_yapan = st.text_input("Bakımı Yapan Tekniker / Firma")
        bakim_maliyeti = st.number_input("Bakım Maliyeti (TL)", min_value=0.0, value=0.0, step=50.0)
    yapilan_islem = st.text_area("Yapılan İşlem ve Değişen Parçaların Detayı")

    if st.button("Bakım Kaydını Sisteme İşle", type="primary"):
        if yapilan_islem and bakimi_yapan:
            yeni_bakim = {
                "Bakım Tarihi": bakim_tarihi.strftime("%d.%m.%Y"), "Fırın/Makine Birimi": secilen_makine,
                "Bakım Türü": bakim_turu, "Yapılan İşlem / Açıklama": yapilan_islem, "Bakımı Yapan": bakimi_yapan, "Maliyet (TL)": bakim_maliyeti
            }
            df_bakim_son = pd.concat([df_bakimlar, pd.DataFrame([yeni_bakim])], ignore_index=True)
            df_bakim_son.to_csv(BAKIM_DOSYASI, index=False)
            st.success(f"✔️ {secilen_makine} için bakım kaydı başarıyla hafızaya alındı!")
            st.rerun()

    st.write("---")
    st.markdown("### 🗂️ Geçmiş Fırın Bakım Geçmişi")
    if not df_bakimlar.empty:
        filtre_secenekleri = ["Tümü"] + BAKIM_MAKINE_LISTESI
        filtre_firin = st.selectbox("Fırın Birimine Göre Filtrele", filtre_secenekleri)
        df_filtreli = df_bakimlar if filtre_firin == "Tümü" else df_bakimlar[df_bakimlar["Fırın/Makine Birimi"] == filtre_firin]
        toplam_maliyet = df_filtreli["Maliyet (TL)"].sum()
        st.markdown(f"<p style='color:#EA580C; font-size:16px; font-weight:bold;'>💰 Toplam Bakım Gideri: {toplam_maliyet:,.2f} TL</p>", unsafe_allow_html=True)
        st.dataframe(df_filtreli, use_container_width=True)

# --- MODÜL 5: SATIN ALMA ---
elif secim == "Satın Alma":
    st.markdown("## 🛒 Kimyasal, Sarf ve Yedek Parça Satın Alma Yönetimi")
    st.markdown("### ➕ Yeni Malzeme / Hizmet Talebi Oluştur")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.info(f"📌 **Talep No:** {yeni_talep_no}")
        malzeme_talep = st.text_input("Talep Edilen Malzeme / Hizmet Adı")
        aciliyet = st.selectbox("Aciliyet Durumu", ["Normal", "Acil", "Kritik (Üretim Durdu!)"])
    with col_s2:
        miktar_talep = st.number_input("Miktar", min_value=1, value=1)
        birim = st.selectbox("Birim", ["Litre (L)", "Adet", "Kg", "Ton", "Metre", "Koli"])
        para_secim = st.selectbox("Para Birimi ", ["TL (₺)", "USD ($)", "EURO (€)"])
    with col_s3:
        birim_fiyat_talep = st.number_input("Birim Fiyat", min_value=0.0, value=0.0)
        tahmini_fiyat = miktar_talep * birim_fiyat_talep
        st.markdown(f"<p style='color:#1E40AF; font-weight:bold;'>💰 Hesaplanan Toplam Maliyet: {tahmini_fiyat:,.2f} {para_secim}</p>", unsafe_allow_html=True)
        aciklama_talep = st.text_area("Talep Nedeni / Detaylı Teknik Özellikler")

    if st.button("Satın Alma Talebini Gönder", type="primary"):
        if malzeme_talep:
            yeni_talep = {
                "Talep No": yeni_talep_no, "Tarih": datetime.now().strftime("%d.%m.%Y"), "Malzeme Adı": malzeme_talep,
                "Miktar": miktar_talep, "Birim": birim, "Aciliyet": aciliyet, "Birim Fiyat": birim_fiyat_talep, "Tahmini Tutar": tahmini_fiyat,
                "Para Birimi": para_secim, "Açıklama": aciklama_talep if aciklama_talep else "Açıklama Yok", "Durum": "Beklemede"
            }
            df_satinalma_son = pd.concat([df_satinalmalar, pd.DataFrame([yeni_talep])], ignore_index=True)
            df_satinalma_son.to_csv(SATINALMA_DOSYASI, index=False)
            st.success(f"✔️ {yeni_talep_no} numaralı talep eklendi!")
            st.rerun()

    st.write("---")
    st.markdown("### ✏️ Talep Detaylarını Düzenle")
    st.markdown("<p style='color:#475569;'>Bir talep 'Teslim Alındı / Stokta' durumuna geçtikten sonra miktar/fiyat bilgileri kilitlenir; sadece bu duruma gelene kadar düzenlenebilir.</p>", unsafe_allow_html=True)
    df_duzenlenebilir = df_satinalmalar[df_satinalmalar["Durum"] != "Teslim Alındı / Stokta"]
    if not df_duzenlenebilir.empty:
        duzenlenecek_id = st.selectbox("Düzenlenecek Talep No", df_duzenlenebilir["Talep No"], key="duzenle_secim")
        secili_talep = df_satinalmalar[df_satinalmalar["Talep No"] == duzenlenecek_id].iloc[0]
        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        with col_d1:
            duzenlenmis_miktar = st.number_input("Miktar (KG/Adet)", min_value=0.0, value=float(secili_talep["Miktar"]), key="duzenle_miktar")
        with col_d2:
            mevcut_birim_fiyat = float(secili_talep["Birim Fiyat"]) if "Birim Fiyat" in secili_talep and pd.notna(secili_talep["Birim Fiyat"]) else 0.0
            duzenlenmis_birim_fiyat = st.number_input("Birim Fiyat", min_value=0.0, value=mevcut_birim_fiyat, key="duzenle_fiyat")
        with col_d3:
            yeni_toplam = duzenlenmis_miktar * duzenlenmis_birim_fiyat
            st.markdown(f"<p style='color:#1E40AF; font-weight:bold; margin-top:28px;'>💰 Yeni Toplam: {yeni_toplam:,.2f} {secili_talep['Para Birimi']}</p>", unsafe_allow_html=True)
        with col_d4:
            st.write("")
            st.write("")
            if st.button("Detayları Güncelle ve Kaydet", type="primary"):
                df_satinalmalar.loc[df_satinalmalar["Talep No"] == duzenlenecek_id, "Miktar"] = duzenlenmis_miktar
                df_satinalmalar.loc[df_satinalmalar["Talep No"] == duzenlenecek_id, "Birim Fiyat"] = duzenlenmis_birim_fiyat
                df_satinalmalar.loc[df_satinalmalar["Talep No"] == duzenlenecek_id, "Tahmini Tutar"] = yeni_toplam
                df_satinalmalar.to_csv(SATINALMA_DOSYASI, index=False)
                st.success(f"✔️ {duzenlenecek_id} talebinin detayları güncellendi!")
                st.rerun()
    else:
        st.info("Düzenlenebilecek (henüz stoğa girmemiş) talep bulunmuyor.")

    if not df_satinalmalar.empty:
        st.write("---")
        st.markdown("### 🔄 Durum Güncelle")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            guncellenecek_id = st.selectbox("Durumu Değişecek Talep No", df_satinalmalar["Talep No"])
        with col_g2:
            yeni_durum = st.selectbox("Yeni Durum Belirle", ["Beklemede", "Sipariş Verildi", "Teslim Alındı / Stokta", "İptal Edildi"])
        if st.button("Durumu Güncelle ve Kaydet"):
            df_satinalmalar.loc[df_satinalmalar["Talep No"] == guncellenecek_id, "Durum"] = yeni_durum
            df_satinalmalar.to_csv(SATINALMA_DOSYASI, index=False)
            st.success(f"✔️ Durum güncellendi!")
            st.rerun()

        st.write("---")
        st.markdown("### 🗂️ Aktif Satın Alma Talepleri Havuzu")
        st.dataframe(df_satinalmalar, use_container_width=True)

# --- MODÜL 6: RAPORLAMA ---
elif secim == "Raporlama":
    st.markdown("## 📊 Doruk Isıl İşlem Akıllı Raporlama ve Analiz Paneli")
    st.markdown("Tonaj, ciro, müşteri portföyü ve fırın verimlilik analizlerini buradan takip edebilirsiniz.")
    if not df_mevcut.empty:
        df_mevcut['Yıl'] = df_mevcut['Tarih'].apply(lambda x: getattr(x, '__str__')().split('.')[2] if len(getattr(x, '__str__')().split('.')) == 3 else "2026")
        df_mevcut['Ay'] = df_mevcut['Tarih'].apply(lambda x: getattr(x, '__str__')().split('.')[1] if len(getattr(x, '__str__')().split('.')) == 3 else "07")

        st.markdown("### 🔍 Genel Rapor Filtreleri")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            secili_yil = st.selectbox("Yıl Seçin", sorted(df_mevcut['Yıl'].unique(), reverse=True))
        with col_f2:
            aylar = ["Tüm Aylar"] + sorted(df_mevcut[df_mevcut['Yıl'] == secili_yil]['Ay'].unique().tolist())
            secili_ay = st.selectbox("Ay Seçin", aylar)

        df_rapor = df_mevcut[df_mevcut['Yıl'] == secili_yil]
        if secili_ay != "Tüm Aylar":
            df_rapor = df_rapor[df_rapor['Ay'] == secili_ay]

        st.write("---")
        st.markdown("### ⏳ Zaman Bazlı Genel Üretim Hacmi")
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam İşlenen Sipariş", f"{len(df_rapor)} Adet")
        c2.metric("Toplam Net Yük (Tonaj)", f"{df_rapor['Net Miktar (KG)'].sum():,.1f} KG")
        ciro_ozet = ""
        for pb in df_rapor['Para Birimi'].unique():
            alt_toplam = df_rapor[df_rapor['Para Birimi'] == pb]['Toplam Tutar'].sum()
            ciro_ozet += f"**{alt_toplam:,.2f} {pb}** | "
        c3.markdown(f"<p style='font-size:15px; font-weight:bold; color:#1E40AF; margin-top:25px;'>Finansal Hacim:<br>{ciro_ozet[:-3] if ciro_ozet else '0 TL'}</p>", unsafe_allow_html=True)

        st.write(" ")
        st.markdown("### 🤝 Müşteri / Firma Bazlı İş Hacmi Kırılımı")
        df_musteri_analiz = df_rapor.groupby('Müşteri').agg(
            Sipariş_Sayısı=('Sipariş ID', 'count'),
            Toplam_Net_Yuk_KG=('Net Miktar (KG)', 'sum'),
            Toplam_Parca_Adedi=('Adet', 'sum')
        ).reset_index()
        st.dataframe(df_musteri_analiz.rename(columns={
            "Sipariş_Sayısı": "Sipariş Sayısı",
            "Toplam_Net_Yuk_KG": "Toplam Net Yük (KG)",
            "Toplam_Parca_Adedi": "Toplam Parça Adedi"
        }), use_container_width=True)

        st.write(" ")
        st.markdown("### 🏭 Fırın Bazlı Tonaj ve Yük Analizi")
        df_firin_analiz = df_rapor.groupby('Fırın').agg(
            Şarj_Sayısı=('Sipariş ID', 'count'),
            Toplam_Tonaj_KG=('Net Miktar (KG)', 'sum')
        ).reset_index()
        col_grafik1, col_grafik2 = st.columns(2)
        with col_grafik1:
            st.markdown("**Fırın Bazlı Net Yük Tablosu (KG)**")
            st.dataframe(df_firin_analiz.rename(columns={
                "Şarj_Sayısı": "Şarj Sayısı",
                "Toplam_Tonaj_KG": "Toplam Tonaj (KG)"
            }), use_container_width=True)
        with col_grafik2:
            st.markdown("**Fırın Yük Dağılım Grafiği (Bar Chart)**")
            if not df_firin_analiz.empty:
                st.bar_chart(data=df_firin_analiz, x='Fırın', y='Toplam_Tonaj_KG', use_container_width=True)
    else:
        st.info("Rapor oluşturabilmek için sistemde tamamlanmış veya kayıtlı en az bir sipariş bulunmalıdır.")

# --- MODÜL 7: YÖNETİM ---
elif secim == "Yönetim":
    st.markdown("## 🛡️ Yönetim Paneli")
    st.markdown("<p style='color:#475569;'>Kullanıcı erişimleri, fırın hattı tanımları ve sistem veri yedeklemesi buradan yönetilir.</p>", unsafe_allow_html=True)
    st.write("---")

    sekme_kullanici, sekme_firin, sekme_yedek = st.tabs(["👤 Kullanıcı Yönetimi", "🏭 Fırın Yönetimi", "💾 Yedekleme & Dışa Aktarma"])

    # --- 7.1 KULLANICI YÖNETİMİ ---
    with sekme_kullanici:
        df_kullanicilar = pd.read_csv(KULLANICI_DOSYASI)

        st.markdown("### ➕ Yeni Kullanıcı Ekle")
        col_k1, col_k2, col_k3, col_k4 = st.columns(4)
        with col_k1:
            yeni_kul_adi = st.text_input("Kullanıcı Adı", key="yeni_kul_adi")
        with col_k2:
            yeni_kul_adsoyad = st.text_input("Ad Soyad", key="yeni_kul_adsoyad")
        with col_k3:
            yeni_kul_sifre = st.text_input("Şifre", type="password", key="yeni_kul_sifre")
        with col_k4:
            yeni_kul_yetki = st.selectbox("Yetki", ["Kullanıcı", "Admin"], key="yeni_kul_yetki")

        if st.button("Kullanıcıyı Sisteme Ekle", type="primary"):
            if not yeni_kul_adi or not yeni_kul_sifre or not yeni_kul_adsoyad:
                st.error("Kullanıcı adı, ad soyad ve şifre alanları zorunludur.")
            elif yeni_kul_adi in df_kullanicilar["Kullanıcı Adı"].values:
                st.error("Bu kullanıcı adı zaten kayıtlı. Farklı bir kullanıcı adı seçin.")
            else:
                yeni_kullanici = {
                    "Kullanıcı Adı": yeni_kul_adi,
                    "Şifre Hash": sifre_hashle(yeni_kul_sifre),
                    "Ad Soyad": yeni_kul_adsoyad,
                    "Yetki": yeni_kul_yetki
                }
                df_kullanicilar = pd.concat([df_kullanicilar, pd.DataFrame([yeni_kullanici])], ignore_index=True)
                df_kullanicilar.to_csv(KULLANICI_DOSYASI, index=False)
                st.success(f"✔️ {yeni_kul_adi} kullanıcısı başarıyla eklendi!")
                st.rerun()

        st.write("---")
        st.markdown("### 🗂️ Kayıtlı Kullanıcılar")
        st.dataframe(df_kullanicilar[["Kullanıcı Adı", "Ad Soyad", "Yetki"]], use_container_width=True)

        st.markdown("### 🗑️ Kullanıcı Sil")
        silinecek_liste = [k for k in df_kullanicilar["Kullanıcı Adı"].tolist() if k != "admin"]
        if silinecek_liste:
            col_sil1, col_sil2 = st.columns([3, 1])
            with col_sil1:
                silinecek_kullanici = st.selectbox("Silinecek Kullanıcı", silinecek_liste)
            with col_sil2:
                st.write("")
                st.write("")
                if st.button("Kullanıcıyı Sil"):
                    df_kullanicilar = df_kullanicilar[df_kullanicilar["Kullanıcı Adı"] != silinecek_kullanici]
                    df_kullanicilar.to_csv(KULLANICI_DOSYASI, index=False)
                    st.success(f"✔️ {silinecek_kullanici} silindi.")
                    st.rerun()
        else:
            st.info("Silinebilecek başka kullanıcı bulunmuyor.")

    # --- 7.2 FIRIN YÖNETİMİ ---
    with sekme_firin:
        st.markdown("### ➕ Yeni Fırın / Hat Ekle")
        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            yeni_firin_adi = st.text_input("Yeni Fırın / Hat Adı")
        with col_f2:
            st.write("")
            st.write("")
            if st.button("Fırını Ekle", type="primary"):
                if not yeni_firin_adi:
                    st.error("Fırın adı boş olamaz.")
                elif yeni_firin_adi in df_firinlar["Fırın Adı"].values:
                    st.error("Bu fırın zaten kayıtlı.")
                else:
                    yeni_firin = {"Fırın Adı": yeni_firin_adi, "Eklenme Tarihi": datetime.now().strftime("%d.%m.%Y")}
                    df_firinlar = pd.concat([df_firinlar, pd.DataFrame([yeni_firin])], ignore_index=True)
                    df_firinlar.to_csv(FIRIN_DOSYASI, index=False)
                    st.success(f"✔️ {yeni_firin_adi} eklendi!")
                    st.rerun()

        st.write("---")
        st.markdown("### 🗂️ Kayıtlı Fırınlar / Hatlar")
        st.dataframe(df_firinlar, use_container_width=True)

        st.markdown("### 🗑️ Fırın Sil")
        if not df_firinlar.empty:
            col_sf1, col_sf2 = st.columns([3, 1])
            with col_sf1:
                silinecek_firin = st.selectbox("Silinecek Fırın", df_firinlar["Fırın Adı"].tolist())
            with col_sf2:
                st.write("")
                st.write("")
                if st.button("Fırını Sil"):
                    df_firinlar = df_firinlar[df_firinlar["Fırın Adı"] != silinecek_firin]
                    df_firinlar.to_csv(FIRIN_DOSYASI, index=False)
                    st.success(f"✔️ {silinecek_firin} silindi.")
                    st.rerun()

    # --- 7.3 YEDEKLEME & DIŞA AKTARMA ---
    with sekme_yedek:
        st.markdown("### 💾 Tüm Sistem Verilerini Yedekle")
        st.markdown("<p style='color:#475569;'>Aşağıdaki buton, sistemdeki tüm kayıtları (siparişler, bakımlar, satın almalar, fırınlar, kullanıcılar) tek bir ZIP dosyası olarak indirir.</p>", unsafe_allow_html=True)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_dosya:
            for dosya_adi in [SIPARIS_DOSYASI, BAKIM_DOSYASI, SATINALMA_DOSYASI, FIRIN_DOSYASI, KULLANICI_DOSYASI]:
                if os.path.exists(dosya_adi):
                    zip_dosya.write(dosya_adi)

        st.download_button(
            label="📥 Tüm Verileri ZIP Olarak İndir",
            data=zip_buffer.getvalue(),
            file_name=f"doruk_isil_islem_yedek_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
            mime="application/zip",
            type="primary"
        )

        st.write("---")
        st.markdown("### 📤 Tek Tek Tablo Dışa Aktarma (Excel/CSV)")
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            st.download_button("📄 Siparişler (CSV)", data=df_mevcut.to_csv(index=False).encode("utf-8-sig"), file_name="siparisler.csv", mime="text/csv")
        with col_e2:
            st.download_button("📄 Bakımlar (CSV)", data=df_bakimlar.to_csv(index=False).encode("utf-8-sig"), file_name="bakimlar.csv", mime="text/csv")
        with col_e3:
            st.download_button("📄 Satın Almalar (CSV)", data=df_satinalmalar.to_csv(index=False).encode("utf-8-sig"), file_name="satinalmalar.csv", mime="text/csv")