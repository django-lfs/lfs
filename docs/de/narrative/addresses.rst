Adressenverwaltung
==================

Allgemein
---------

* Der Shopkunde kann beim Checkout zwei Adressen angeben: Versand- und 
  Rechnungsadresse. 
* Der Shopkunde gibt als erstes die Rechnungsadresse ein.
* Wenn sich die Versandadresse von der Rechnungsadresse unterscheidet, gibt er
  die zusätzlich die Rechnungsadresse ein.
  
Speicherung
-----------

Adressen
^^^^^^^^

* Das Bestellungsobjekt speichert beide Adressen in die dafür vorgesehen Felder 
  getrennt voneinander (keine Referenz auf die Objekt), auch wenn diese sich 
  nicht voneinander unterscheiden. Diese Daten bleiben für immer erhalten, auch 
  wenn sich die Adressen später ändern sollten.
  
* Das Kundenobjekt speichert Referenzen auf Adressen. Wenn die Versandadresse
  nicht angegeben wird, bleibt die Referenz leer.

E-Mail
^^^^^^
  
* Wenn der Kunde registriert ist, wird die E-Mail Adresse in Django's Standard
  User-Objekt gespeichert und entnommen. Die E-Mail Adresse wird dann während 
  der Registrierung abgefragt. Infolgedessen wird kein E-Mail Feld innerhalb der 
  Rechnungsadresse angezeigt.
  
* Falls der Kunde nicht registriert ist, wird die E-Mail Adresse in der
  Rechnungsadresse gespeichert. Es wird dann ein E-Mail Feld innerhalb des 
  Formulars für die Rechnungsadresse angezeigt.

Anzeige
-------
* Auf der Bestellung werden beide Adressen angezeigt, auch wenn diese sich nicht
  unterscheiden. Dies geschieht automatisch, da die Felder bei der Erstellung
  der Bestellung automatisch ausgefüllt werden (siehe `Speicherung`_).

Verwaltung
----------

* Der Kunde kann seine Adressen über "Mein Konto" verwalten.

* Zur Zeit kann er maximal zwei Adressen angeben: eine Rechnungs- und eine 
  Versandadresse (Dies kann sich in Zukunft auf eine unbestimmte Anzahl ändern). 
  Sollte keine Versandadresse existieren, kann er diese hinzufügen.