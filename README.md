Pokretanje projekta

Da bi se pokrenuo projekat, potrebno je instalirati pakete navedene tekstualnom fajlu requirements.txt. Ti paketi se mogu instalirati jednostavno komandom pip intall -r requirements.txt.

Uz pakete navedene u fajlu requirements.txt se može pokrenuti program pod nazivom app.py korišćenjem komande python app.py. Kada se program pokrene iskače pitanje koji video snimak se želi gledati, i nakon kucanja rednog broja snimka (1 ili 2) se prikazuje izabradi snimak. Iskače prozor sa snimkom igre sa leve strane i iscrtanom igrom sa desne.

Beleške o kodu i način funkcionisanja programa

Prvobitno se detektuju ivice sa funkcijom detect_grid_lines:
U ovoj finkciji se pomoću Canny operatora detektuju ivice. Canny operator se može pronaći kao metoda u biblioteci OpenCV
Dalje, pomoću Hough transormacije možemo izdvojiti linije na snimku (odnosno po frejmu). Za ovo se koristi metoda HoughLinesP
Dektovane linije se klasifikuju na horizontalne i vertikalne linije
Pomoću detektovanih linija se pravi “mapa” ispisane igre:
Kada se detektuju 2 vertikalne i 2 horizontalne linije mogu se izvojiti pozicije kvadrata gde će se znakovi X i O upisivati
Kocke se izdvajaju tako što se odredi središnja kocka, odnosno tačke preseka tih linija, a time se može dobiti širina i visina kocke (pa samim tim i centar)
Pomeranjem centra ulevo, udesno, nagore i na dole za po jednu jedinicu mere (što su visina ili širina ćelije) dobija se maps svih mogućih pozicija za upis veličine 3x3 (matrica veličine 3x3) - ovo se čuva u listi zvanoj cell_positions


Posle detekcije ivica se poziva funkcija detect_hand koja detektuje ruku u frejmu, odnosno neko neočekivano kretanje. Želimo da znamo kada je ruka u frejmu, da ne bi se uključivala u detekciju samih ivica, i pokvarila detekciju. Pored toga, kada detektujemo ruku u frejmu, ne dozvoljavamo da se već upisane ćelije menjaju (ovo je moguće jer su pravila igre takva da ukoliko se u neku kocku upiše X ili O, to se neće menjati do kraja igre).

Nakon ovoga se mogu prikazati linije i znakovi X i O upisati na desni prozor, Za ovo se koriste funkcije draw_detected_lines i draw_shapes. U funkciji draw_shapes se detektuju znakovi X i O, upisuju u matricu pod nazivom game_state i pomoću informacija iz matrice se crtaju na desnom ekranu. Matrica game_state se koristi i za praćenje rezultata igre (dvodimenzionalni array sa -1 na praznim poljima, 0 na poljima sa O i 1 na poljima sa X.

Uz sve ove infomacije i metode, se lako iscrtava i linija koja povezuje pobednički niz. Ukoliko se ne detektuje niz O ili X, ne iscrtava se linija. Kada se igra završi (pobedom jednog od dva znaka, ili se sva polja popune bez ijednog niza od 3) ispisuje se rezultat u desnom prozoru iznad iscrtane igre.

Zaključak
	
OpenCV daje dovoljno metoda da se ovo samostalno izvrši (izuzev potrebih paketa za matematičke operacije). Program je veoma zavistan od redosleda operacija (funkcija) kojie se koriste. Detekcija ruke, zbog toga što se u oba videa se može videti samo u određenom delu frejma, je postavljena samo na taj deo. Ovo omogućava da ostale sitne promene na videu ne utiču na rezultat. Ovaj program se ne bi mogao koristi ako je, na primer, papir zakošen na za neki određeni ugao, jer se ovde detektuju horizontalne i vertikalne linije samo. Za neki veći skup videa, bi se morao sastaviti mnogo kompleksniji program za detekciju.
