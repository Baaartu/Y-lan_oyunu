import pygame
import random
import sys

# --- SABİTLER ---
PENCERE_GENISLIK = 600
PENCERE_YUKSEKLIK = 600
GRID_BOYUT = 20
HUCRE_SAYISI_X = PENCERE_GENISLIK // GRID_BOYUT
HUCRE_SAYISI_Y = PENCERE_YUKSEKLIK // GRID_BOYUT
FPS = 10

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
    def __init__(self, engeller=[], harita_tipi=0):
        orta_x = HUCRE_SAYISI_X // 2
        orta_y = HUCRE_SAYISI_Y // 2
        
        # Harita 3 (Labirent) başlangıç noktası daha özel olabilir ancak şimdilik merkezde kalsın
        self.govde = [
            (orta_x, orta_y),
            (orta_x, orta_y + 1),
            (orta_x, orta_y + 2),
        ]
        self.yon = YUKARI
        self.buyume = False
        self.engeller = engeller
        self.harita_tipi = harita_tipi

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
        yeni_bas_x = bas_x + yon_x
        yeni_bas_y = bas_y + yon_y
        
        # Harita 2 (Kutu - Wrap Around) 
        if self.harita_tipi == 1:
            yeni_bas_x %= HUCRE_SAYISI_X
            yeni_bas_y %= HUCRE_SAYISI_Y
            
        yeni_bas = (yeni_bas_x, yeni_bas_y)

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
        if (bas_x, bas_y) in self.engeller:
            return True
            
        # Harita 2 (Kutu) ise duvar çarpması yoktur, engellere çarpar
        if self.harita_tipi == 1:
            return False
            
        return (
            bas_x < 0
            or bas_x >= HUCRE_SAYISI_X
            or bas_y < 0
            or bas_y >= HUCRE_SAYISI_Y
        )

    def kendine_carpma(self):
        return self.govde[0] in self.govde[1:]


class YemYoneticisi:
    def __init__(self, engeller=[]):
        self.yemler = []
        self.engeller = engeller

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
                if (x, y) not in yilan_govde and (x, y) not in self.yemler and (x, y) not in self.engeller:
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


# --- HARİTALAR ---
def harita_olustur(harita_tipi):
    engeller = []
    cikis = None
    
    if harita_tipi == 1:
        # Harita 2: Kutu (Kenarlardan geçmeli, rastgele 2x2 engeller)
        eklenecek_engel_sayisi = 4
        while eklenecek_engel_sayisi > 0:
            rx = random.randint(2, HUCRE_SAYISI_X - 4)
            ry = random.randint(2, HUCRE_SAYISI_Y - 4)
            yeni_engel = [(rx, ry), (rx+1, ry), (rx, ry+1), (rx+1, ry+1)]
            
            # Üst üste gelmesini veya merkeze denk gelmesini önle
            merkez_x, merkez_y = HUCRE_SAYISI_X // 2, HUCRE_SAYISI_Y // 2
            if not any(e in engeller for e in yeni_engel) and not any(abs(e[0] - merkez_x) < 3 and abs(e[1] - merkez_y) < 3 for e in yeni_engel):
                engeller.extend(yeni_engel)
                eklenecek_engel_sayisi -= 1
                
    elif harita_tipi == 2:
        # Harita 3: Daha Oynanabilir Basit Labirent ve Varyasyonları
        labirent_secenekleri = [
            # Orijinal Taslak (Daha Oynanabilir Basit Labirent)
            [
                "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                "XC         X                 X",
                "X  XXXXX   X   XXXXXXXXXXX   X",
                "X  X       X               X X",
                "X  X   XXXXX   XXXXXXXXX   X X",
                "X  X       X           X   X X",
                "X  X   X   X   XXXXX   X   X X",
                "X  X   X   X       X   X   X X",
                "X      X   XXXXX   X   X     X",
                "XXXXX  X           X   X   XXX",
                "X      X   XXXXXXXXX   X     X",
                "X  XXXXX               XXXX  X",
                "X          XXXX    X         X",
                "X  XXXXXXXX        XXXXXXX   X",
                "X          X   X             X",
                "XXXXXXX    X   XXXXX   XXXXXXX",
                "X          X       X         X",
                "X  XXXXXXXXXXXXX   XXXXXXX   X",
                "X                  X         X",
                "X  XXXXX   XXXXXXXXX   XXXX  X",
                "X      X           X         X",
                "XXXX   XXXXXXXXX   X   XXXXXXX",
                "X              X   X         X",
                "X  XXXXXXXXX   X   XXXXXXX   X",
                "X          X                 X",
                "X  XXXXX   XXXXXXXXXXXXX   XXX",
                "X      X                   X X",
                "XXXX   XXXXXXXXXXXXXXXXXXX   X",
                "X                            X",
                "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            ],
            # Varyasyon 1 (Kıvrımlı Koridorlar)
            [
                "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                "X         X                C X",
                "X XXXXXXX X XXXXXXXXXXXXXXXX X",
                "X X       X                  X",
                "X X XXXXXXXXXXXXXXXXXXXXXXXX X",
                "X X                          X",
                "X XXXXX XXXXXXXXXXXXXXXXXXXX X",
                "X     X X                    X",
                "XXXXX X X XXXXXXXXXXXXXXXXXXXX",
                "X     X X                    X",
                "X XXXXX X XXXXXXXXXXXXXXXXXX X",
                "X X     X X                  X",
                "X X XXXXX X XXXXXXXXXXXXXXXX X",
                "X X X     X X                X",
                "X X X XXXXX X XXXXXXXXXXXXXX X",
                "X X X       X                X",
                "X X XXXXXXXXXXXXXXXXXXXXXX X X",
                "X X                        X X",
                "X XXXXXXXXXXXXXXXXXXXXXXXX X X",
                "X                          X X",
                "X XXXXXXXXXXXXXXXXXXXXXXXX X X",
                "X X                        X X",
                "X X XXXXXXXXXXXXXXXXXXXXXX X X",
                "X X X                      X X",
                "X X X XXXXXXXXXXXXXXXXXXXX X X",
                "X X X                      X X",
                "X X XXXXXXXXXXXXXXXXXXXXXXXX X",
                "X X                          X",
                "X XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            ],
            # Varyasyon 2 (Geniş Odalar ve Dar Yollar)
            [
                "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                "X                            X",
                "X XXXX XXXXXXXXXXXXXXXX XXXX X",
                "X X  X X              X X  X X",
                "X X  X X XXXXXXXXXXXX X X  X X",
                "X X  X X X          X X X  X X",
                "X XXXX X X XXXXXXXX X X XXXX X",
                "X      X X X      X X X      X",
                "XXXX XXX X X XXXX X X XXX XXXX",
                "X      X X X X  X X X X      X",
                "X XXXXXX X X X  X X X XXXXXX X",
                "X X      X X X  X X X      X X",
                "X X XXXXXX X XXXX X XXXXXX X X",
                "X X        X      X        X X",
                "X XXXXXXXX XXXXXXXX XXXXXXXX X",
                "X                            X",
                "X XXXXXXXX XXXXXXXX XXXXXXXX X",
                "X X        X      X        X X",
                "X X XXXXXX X XXXX X XXXXXX X X",
                "X X      X X X  X X X      X X",
                "X XXXXXX X X X  X X XXXXXX X X",
                "X      X X X X  X X X      X X",
                "XXXX XXX X X XXXX X X XXX XXXX",
                "X      X X X      X X        X",
                "X XXXX X X XXXXXXXX X X XXXX X",
                "X X  X X X          X X X  X X",
                "X X  X X XXXXXXXXXXXX X X  X X",
                "X XXXX C              X XXXX X",
                "X                            X",
                "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            ],
            # Varyasyon 3 (Döngüler ve Yanıltmacalar)
            [
                "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                "XC       X                   X",
                "X XXXXX  X  XXXXXX  XXXXXX   X",
                "X X      X       X  X    X   X",
                "X X  XXXXXXXXXX  X  X    X   X",
                "X X  X           X  X    X   X",
                "X X  X  XXXXXXX  X  XXXXXX   X",
                "X X  X  X        X           X",
                "X X  X  X  XXXXXXXXXXXXXXX   X",
                "X X  X  X                    X",
                "X X  X  XXXXXXXXXXXXXXXXXX   X",
                "X X  X                   X   X",
                "X X  XXXXXXXX  XXXXX  X  X   X",
                "X X         X  X      X  X   X",
                "X XXXXXXXX  X  X  XXXXX  X   X",
                "X           X  X         X   X",
                "X XXXXXXXX  X  XXXXXXXX  X   X",
                "X X      X  X         X  X   X",
                "X X      X  X  XXXXX  X  X   X",
                "X X      X  X  X   X  X  X   X",
                "X XXXXX  X  X  X   X  X  X   X",
                "X     X  X  X  X   X  X  X   X",
                "XXXX  X  X  X  X   X  X  X   X",
                "X     X  X  X  XXXXX  X  X   X",
                "X  XXXX  X  X         X  X   X",
                "X        X  XXXXXXXXXXX  X   X",
                "X  XXXXXXX               X   X",
                "X        XXXXXXXXXXXXXXXXX   X",
                "X                            X",
                "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            ]
        ]
        
        harita_taslagi = random.choice(labirent_secenekleri)
        
        for y, satir in enumerate(harita_taslagi):
            if y >= len(harita_taslagi): continue
            for x, char in enumerate(satir):
                if x >= HUCRE_SAYISI_X: continue
                if char == 'X':
                    engeller.append((x, y))
                elif char == 'C':
                    cikis = (x, y)

        # Başlangıç odası: Yılanın doğduğu merkezin çevresini temizliyoruz (15,15 çevresi 6x6 boşluk)
        merkez_guvenli_alan = [(gx, gy) for gx in range(12, 18) for gy in range(12, 18)]
        engeller = [e for e in engeller if e not in merkez_guvenli_alan]

    return list(set(engeller)), cikis


def harita_ciz(ekran, engeller, cikis):
    """Duvarları ve çıkış noktasını ekrana çizer."""
    for engel in engeller:
        x = engel[0] * GRID_BOYUT
        y = engel[1] * GRID_BOYUT
        rect = pygame.Rect(x, y, GRID_BOYUT, GRID_BOYUT)
        pygame.draw.rect(ekran, (100, 100, 120), rect)
        
    if cikis:
        cx, cy = cikis
        x = cx * GRID_BOYUT
        y = cy * GRID_BOYUT
        rect = pygame.Rect(x, y, GRID_BOYUT, GRID_BOYUT)
        pygame.draw.rect(ekran, (255, 215, 0), rect) # Altın sarısı çıkış
        pygame.draw.rect(ekran, (200, 100, 0), rect, 3) # Çerçeve


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


def oyun_bitti_ekrani(ekran, skor, kazandin_mi=False):
    """Oyun bitti veya kazanma ekranını göster."""
    # Yarı saydam karartma
    karartma = pygame.Surface((PENCERE_GENISLIK, PENCERE_YUKSEKLIK))
    karartma.set_alpha(150)
    karartma.fill(SIYAH)
    ekran.blit(karartma, (0, 0))

    font_buyuk = pygame.font.SysFont("Arial", 48, bold=True)
    font_kucuk = pygame.font.SysFont("Arial", 24)

    # Başlık yazısı
    if kazandin_mi:
        baslik = "KAZANDINIZ!"
        renk_baslik = (255, 215, 0)
    else:
        baslik = "OYUN BITTI"
        renk_baslik = KIRMIZI

    metin1 = font_buyuk.render(baslik, True, renk_baslik)
    rect1 = metin1.get_rect(center=(PENCERE_GENISLIK // 2, PENCERE_YUKSEKLIK // 2 - 50))
    ekran.blit(metin1, rect1)

    # Skor yazısı
    metin_skor = font_kucuk.render(f"Skor: {skor}", True, ACIK_YESIL)
    rect_skor = metin_skor.get_rect(center=(PENCERE_GENISLIK // 2, PENCERE_YUKSEKLIK // 2))
    ekran.blit(metin_skor, rect_skor)

    # Yeniden başlatma bilgisi
    metin2 = font_kucuk.render("Menuye Don: TAB | Tekrar: SPACE | Cikis: ESC", True, (200, 200, 200))
    rect2 = metin2.get_rect(center=(PENCERE_GENISLIK // 2, PENCERE_YUKSEKLIK // 2 + 50))
    ekran.blit(metin2, rect2)

    pygame.display.flip()


def baslangic_menusu(ekran, saat):
    """Oyun başlangıç menüsünü ve harita seçimini gösterir."""
    menu_aktif = True
    alt_menu_aktif = False
    secili_secenek = 0
    secili_harita = 0
    
    font_baslik = pygame.font.SysFont("Arial", 60, bold=True)
    font_secenek = pygame.font.SysFont("Arial", 36, bold=True)
    font_bilgi = pygame.font.SysFont("Arial", 18)
    
    secenekler_ana = ["Başla", "Harita Seç", "Çık"]
    secenekler_harita = ["Klasik", "Kutu", "Labirent", "Geri"]
    
    while menu_aktif:
        ekran.fill(SIYAH)
        grid_ciz(ekran)
        
        # Başlık
        baslik_metin = "HARITA SECIMI" if alt_menu_aktif else "YILAN OYUNU"
        metin_baslik = font_baslik.render(baslik_metin, True, ACIK_YESIL)
        rect_baslik = metin_baslik.get_rect(center=(PENCERE_GENISLIK // 2, PENCERE_YUKSEKLIK // 3))
        ekran.blit(metin_baslik, rect_baslik)
        
        guncel_secenekler = secenekler_harita if alt_menu_aktif else secenekler_ana
        
        for i, sec in enumerate(guncel_secenekler):
            renk = KIRMIZI if secili_secenek == i else (200, 200, 200)
            sembol = "> " if secili_secenek == i else ""
            
            # Seçili haritayı belirt
            if alt_menu_aktif and i < 3 and secili_harita == i:
                sec += " (Secili)"
                
            metin = font_secenek.render(f"{sembol}{sec}", True, renk)
            rect = metin.get_rect(center=(PENCERE_GENISLIK // 2, PENCERE_YUKSEKLIK // 2 + i * 50))
            ekran.blit(metin, rect)
        
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
                guncel_uzunluk = len(guncel_secenekler)
                if event.key == pygame.K_UP:
                    secili_secenek = (secili_secenek - 1) % guncel_uzunluk
                elif event.key == pygame.K_DOWN:
                    secili_secenek = (secili_secenek + 1) % guncel_uzunluk
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if not alt_menu_aktif:
                        if secili_secenek == 0:  # Başla
                            return secili_harita
                        elif secili_secenek == 1:  # Harita Seç
                            alt_menu_aktif = True
                            secili_secenek = 0
                        elif secili_secenek == 2:  # Çık
                            pygame.quit()
                            sys.exit()
                    else:
                        if secili_secenek == 3:  # Geri
                            alt_menu_aktif = False
                            secili_secenek = 1
                        else:  # Harita seçildi
                            secili_harita = secili_secenek
                            alt_menu_aktif = False
                            secili_secenek = 0
                        
        saat.tick(FPS)


def ana_dongu():
    pygame.init()
    ekran = pygame.display.set_mode((PENCERE_GENISLIK, PENCERE_YUKSEKLIK))
    pygame.display.set_caption("Yılan Oyunu")
    saat = pygame.time.Clock()

    # Oyun her yeniden başladığında (TAB ile) tüm döngüyü sıfırlamak için ana bir while döngüsü
    while True:
        secilen_harita_tipi = baslangic_menusu(ekran, saat)
        engeller, cikis = harita_olustur(secilen_harita_tipi)

        yilan = Yilan(engeller, secilen_harita_tipi)
        yem_yoneticisi = YemYoneticisi(engeller)
        
        # Harita 3 (Labirent) hızı yavaşlat
        gecerli_fps = 8 if secilen_harita_tipi == 2 else 10
        
        # Harita 3 (Labirent) ise yem oluşturma
        if secilen_harita_tipi != 2:
            yem_yoneticisi.yemleri_olustur(yilan.govde)
        
        skor = 0

        oyun_aktif = True
        oyun_bitti = False
        kazandin = False

        while oyun_aktif:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if oyun_bitti:
                        if event.key == pygame.K_SPACE:
                            # Aynı haritada yeniden başlat
                            yilan = Yilan(engeller, secilen_harita_tipi)
                            yem_yoneticisi = YemYoneticisi(engeller)
                            if secilen_harita_tipi != 2:
                                yem_yoneticisi.yemleri_olustur(yilan.govde)
                            skor = 0
                            oyun_bitti = False
                            kazandin = False
                        elif event.key == pygame.K_TAB:
                            # Menüye dön (mevcut while oyun_aktif döngüsünü bitirir, en dış while baştan başlar)
                            oyun_aktif = False
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                    else:
                        if event.key == pygame.K_LEFT:
                            yilan.don("sol")
                        elif event.key == pygame.K_RIGHT:
                            yilan.don("sag")
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()

            if not oyun_bitti:
                # Yılanı hareket ettir
                yilan.hareket_et()

                # Çarpışma kontrolü
                if yilan.duvar_carpma() or yilan.kendine_carpma():
                    oyun_bitti = True
                    kazandin = False
                
                # Labirent kazanma kontrolü
                if secilen_harita_tipi == 2 and not oyun_bitti:
                    if yilan.govde[0] == cikis:
                        oyun_bitti = True
                        kazandin = True
                
                # Yem yeme kontrolü (Labirent değilse)
                if not oyun_bitti and secilen_harita_tipi != 2:
                    if yem_yoneticisi.yem_kontrol(yilan.govde[0]):
                        yilan.buyut()
                        yem_yoneticisi.yemleri_olustur(yilan.govde)
                        skor += 10

                # Çizim
                ekran.fill(SIYAH)
                grid_ciz(ekran)
                harita_ciz(ekran, engeller, cikis)
                
                if secilen_harita_tipi != 2:
                    yem_yoneticisi.cizdir(ekran)
                    
                yilan.cizdir(ekran)
                
                # Skoru ekrana yazdır (Oyun devam ediyorsa veya bitmemişse de arka planda görünsün)
                skor_cizdir(ekran, skor)

                if oyun_bitti:
                    oyun_bitti_ekrani(ekran, skor, kazandin)

                pygame.display.flip()

            saat.tick(gecerli_fps)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    ana_dongu()
