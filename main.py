import pygame
import random
import sys

# --- SABİTLER ---
PENCERE_GENISLIK = 600
PENCERE_YUKSEKLIK = 600
GRID_BOYUT = 20
HUCRE_SAYISI_X = PENCERE_GENISLIK // GRID_BOYUT
HUCRE_SAYISI_Y = PENCERE_YUKSEKLIK // GRID_BOYUT
FPS = 15

# Renkler
SIYAH = (15, 15, 25)
KOYU_YESIL = (34, 139, 34)
ACIK_YESIL = (50, 205, 50)
KIRMIZI = (220, 50, 50)
GRID_RENK = (30, 30, 45)
BAS_RENK = (0, 180, 0)

# Yönler
YUKARI = (0, -1)
ASAGI = (0, 1)
SOL = (-1, 0)
SAG = (1, 0)

# Göreceli dönüş tablosu: mevcut_yon -> (sola_don, saga_don)
DONUS_TABLOSU = {
    YUKARI: (SOL, SAG),
    SAG: (YUKARI, ASAGI),
    ASAGI: (SAG, SOL),
    SOL: (ASAGI, YUKARI),
}


class Yilan:
    def __init__(self):
        orta_x = HUCRE_SAYISI_X // 2
        orta_y = HUCRE_SAYISI_Y // 2
        self.govde = [
            (orta_x, orta_y),
            (orta_x, orta_y + 1),
            (orta_x, orta_y + 2),
        ]
        self.yon = YUKARI
        self.buyume = False

    def don(self, taraf):
        """Göreceli dönüş: 'sol' veya 'sag'"""
        sol_yon, sag_yon = DONUS_TABLOSU[self.yon]
        if taraf == "sol":
            self.yon = sol_yon
        elif taraf == "sag":
            self.yon = sag_yon

    def hareket_et(self):
        bas_x, bas_y = self.govde[0]
        yon_x, yon_y = self.yon
        yeni_bas = (bas_x + yon_x, bas_y + yon_y)

        self.govde.insert(0, yeni_bas)

        if self.buyume:
            self.buyume = False
        else:
            self.govde.pop()

    def buyut(self):
        self.buyume = True

    def cizdir(self, ekran):
        for i, parca in enumerate(self.govde):
            x = parca[0] * GRID_BOYUT
            y = parca[1] * GRID_BOYUT

            if i == 0:
                # Kafa - biraz daha koyu ve farklı
                rect = pygame.Rect(x, y, GRID_BOYUT, GRID_BOYUT)
                pygame.draw.rect(ekran, BAS_RENK, rect)
                pygame.draw.rect(ekran, ACIK_YESIL, rect, 1)
            else:
                # Gövde - dama deseni efekti
                renk = KOYU_YESIL if i % 2 == 0 else ACIK_YESIL
                rect = pygame.Rect(x + 1, y + 1, GRID_BOYUT - 2, GRID_BOYUT - 2)
                pygame.draw.rect(ekran, renk, rect, border_radius=4)

    def duvar_carpma(self):
        bas_x, bas_y = self.govde[0]
        return (
            bas_x < 0
            or bas_x >= HUCRE_SAYISI_X
            or bas_y < 0
            or bas_y >= HUCRE_SAYISI_Y
        )

    def kendine_carpma(self):
        return self.govde[0] in self.govde[1:]


class YemYoneticisi:
    def __init__(self):
        self.yemler = []

    def yemleri_olustur(self, yilan_govde):
        """Ekrandaki yem sayısını 2-4 arası rastgele bir değere tamamla."""
        hedef_sayi = random.randint(2, 4)

        while len(self.yemler) < hedef_sayi:
            yeni_yem = self._rastgele_pozisyon(yilan_govde)
            if yeni_yem and yeni_yem not in self.yemler:
                self.yemler.append(yeni_yem)

    def _rastgele_pozisyon(self, yilan_govde):
        """Yılanın üzerinde olmayan rastgele bir pozisyon döndür."""
        bos_hucreler = []
        for x in range(HUCRE_SAYISI_X):
            for y in range(HUCRE_SAYISI_Y):
                if (x, y) not in yilan_govde and (x, y) not in self.yemler:
                    bos_hucreler.append((x, y))

        if bos_hucreler:
            return random.choice(bos_hucreler)
        return None

    def yem_kontrol(self, bas_pozisyon):
        """Yılanın başı bir yeme denk geldi mi kontrol et."""
        if bas_pozisyon in self.yemler:
            self.yemler.remove(bas_pozisyon)
            return True
        return False

    def cizdir(self, ekran):
        for yem in self.yemler:
            x = yem[0] * GRID_BOYUT + GRID_BOYUT // 2
            y = yem[1] * GRID_BOYUT + GRID_BOYUT // 2
            yaricap = GRID_BOYUT // 2 - 2

            # Yem dairesi
            pygame.draw.circle(ekran, KIRMIZI, (x, y), yaricap)
            # Parlak nokta efekti
            pygame.draw.circle(
                ekran, (255, 120, 120), (x - 2, y - 2), yaricap // 3
            )


def skor_cizdir(ekran, skor):
    """Ekrana skoru yazdır."""
    font = pygame.font.SysFont("Arial", 24, bold=True)
    metin = font.render(f"Skor: {skor}", True, (255, 255, 255))
    ekran.blit(metin, (10, 10))


def grid_ciz(ekran):
    """Arka plan grid çizgileri."""
    for x in range(0, PENCERE_GENISLIK, GRID_BOYUT):
        pygame.draw.line(ekran, GRID_RENK, (x, 0), (x, PENCERE_YUKSEKLIK))
    for y in range(0, PENCERE_YUKSEKLIK, GRID_BOYUT):
        pygame.draw.line(ekran, GRID_RENK, (0, y), (PENCERE_GENISLIK, y))


def oyun_bitti_ekrani(ekran, skor):
    """Oyun bitti ekranını göster."""
    # Yarı saydam karartma
    karartma = pygame.Surface((PENCERE_GENISLIK, PENCERE_YUKSEKLIK))
    karartma.set_alpha(150)
    karartma.fill(SIYAH)
    ekran.blit(karartma, (0, 0))

    font_buyuk = pygame.font.SysFont("Arial", 48, bold=True)
    font_kucuk = pygame.font.SysFont("Arial", 24)

    # "OYUN BİTTİ" yazısı
    metin1 = font_buyuk.render("OYUN BITTI", True, KIRMIZI)
    rect1 = metin1.get_rect(center=(PENCERE_GENISLIK // 2, PENCERE_YUKSEKLIK // 2 - 50))
    ekran.blit(metin1, rect1)

    # Skor yazısı
    metin_skor = font_kucuk.render(f"Skor: {skor}", True, ACIK_YESIL)
    rect_skor = metin_skor.get_rect(center=(PENCERE_GENISLIK // 2, PENCERE_YUKSEKLIK // 2))
    ekran.blit(metin_skor, rect_skor)

    # Yeniden başlatma bilgisi
    metin2 = font_kucuk.render("Tekrar: SPACE | Cikis: ESC", True, (200, 200, 200))
    rect2 = metin2.get_rect(center=(PENCERE_GENISLIK // 2, PENCERE_YUKSEKLIK // 2 + 50))
    ekran.blit(metin2, rect2)

    pygame.display.flip()


def baslangic_menusu(ekran, saat):
    """Oyun başlangıç menüsünü gösterir."""
    menu_aktif = True
    secili_secenek = 0  # 0: Başla, 1: Çık
    
    font_baslik = pygame.font.SysFont("Arial", 60, bold=True)
    font_secenek = pygame.font.SysFont("Arial", 36, bold=True)
    font_bilgi = pygame.font.SysFont("Arial", 18)
    
    while menu_aktif:
        ekran.fill(SIYAH)
        grid_ciz(ekran)
        
        # Başlık
        metin_baslik = font_baslik.render("YILAN OYUNU", True, ACIK_YESIL)
        rect_baslik = metin_baslik.get_rect(center=(PENCERE_GENISLIK // 2, PENCERE_YUKSEKLIK // 3))
        ekran.blit(metin_baslik, rect_baslik)
        
        # Seçenekler
        renk_basla = KIRMIZI if secili_secenek == 0 else (200, 200, 200)
        sembol_basla = "> " if secili_secenek == 0 else ""
        metin_basla = font_secenek.render(f"{sembol_basla}Başla", True, renk_basla)
        rect_basla = metin_basla.get_rect(center=(PENCERE_GENISLIK // 2, PENCERE_YUKSEKLIK // 2))
        ekran.blit(metin_basla, rect_basla)
        
        renk_cik = KIRMIZI if secili_secenek == 1 else (200, 200, 200)
        sembol_cik = "> " if secili_secenek == 1 else ""
        metin_cik = font_secenek.render(f"{sembol_cik}Çık", True, renk_cik)
        rect_cik = metin_cik.get_rect(center=(PENCERE_GENISLIK // 2, PENCERE_YUKSEKLIK // 2 + 60))
        ekran.blit(metin_cik, rect_cik)
        
        # Kullanım bilgisi
        metin_bilgi = font_bilgi.render("Yon Tuslari: Yukari/Asagi | Secim: ENTER veya SPACE", True, (120, 120, 120))
        rect_bilgi = metin_bilgi.get_rect(center=(PENCERE_GENISLIK // 2, PENCERE_YUKSEKLIK - 30))
        ekran.blit(metin_bilgi, rect_bilgi)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    secili_secenek = (secili_secenek - 1) % 2
                elif event.key == pygame.K_DOWN:
                    secili_secenek = (secili_secenek + 1) % 2
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if secili_secenek == 0:
                        return  # Menü döngüsünden çık, oyuna başla
                    else:
                        pygame.quit()
                        sys.exit()  # Oyundan çık
                        
        saat.tick(FPS)


def ana_dongu():
    pygame.init()
    ekran = pygame.display.set_mode((PENCERE_GENISLIK, PENCERE_YUKSEKLIK))
    pygame.display.set_caption("Yılan Oyunu")
    saat = pygame.time.Clock()

    baslangic_menusu(ekran, saat)

    yilan = Yilan()
    yem_yoneticisi = YemYoneticisi()
    yem_yoneticisi.yemleri_olustur(yilan.govde)
    
    skor = 0

    oyun_aktif = True
    oyun_bitti = False

    while oyun_aktif:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                oyun_aktif = False

            if event.type == pygame.KEYDOWN:
                if oyun_bitti:
                    if event.key == pygame.K_SPACE:
                        # Oyunu yeniden başlat
                        yilan = Yilan()
                        yem_yoneticisi = YemYoneticisi()
                        yem_yoneticisi.yemleri_olustur(yilan.govde)
                        skor = 0
                        oyun_bitti = False
                    elif event.key == pygame.K_ESCAPE:
                        oyun_aktif = False
                else:
                    if event.key == pygame.K_LEFT:
                        yilan.don("sol")
                    elif event.key == pygame.K_RIGHT:
                        yilan.don("sag")
                    elif event.key == pygame.K_ESCAPE:
                        oyun_aktif = False

        if not oyun_bitti:
            # Yılanı hareket ettir
            yilan.hareket_et()

            # Çarpışma kontrolü
            if yilan.duvar_carpma() or yilan.kendine_carpma():
                oyun_bitti = True
            else:
                # Yem yeme kontrolü
                if yem_yoneticisi.yem_kontrol(yilan.govde[0]):
                    yilan.buyut()
                    yem_yoneticisi.yemleri_olustur(yilan.govde)
                    skor += 10

            # Çizim
            ekran.fill(SIYAH)
            grid_ciz(ekran)
            yem_yoneticisi.cizdir(ekran)
            yilan.cizdir(ekran)
            
            # Skoru ekrana yazdır (Oyun devam ediyorsa veya bitmemişse de arka planda görünsün)
            skor_cizdir(ekran, skor)

            if oyun_bitti:
                oyun_bitti_ekrani(ekran, skor)

            pygame.display.flip()

        saat.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    ana_dongu()
