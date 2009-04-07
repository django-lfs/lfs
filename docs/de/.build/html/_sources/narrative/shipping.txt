=========
Lieferung
=========

Allgemein
=========

* Verwaltung von beliebigen Liefermethoden aus denen der Kunde auswählen kann, 
  wie beispielsweise ``Standard`` oder ``Express``.

* Liefermethoden können inaktiv geschaltet werden.

* Liefermethoden können durch Kriterien eingegrenzt werden, z.B. der 
  Shopbetreiber möchte ``Express`` nur dann anbieten, wenn der Kunde aus einem
  bestimmten Land kommt.

* Nur wenna alle Kriterien einer Liefermethode zutreffen wird diese zur Auswahl
  angeboten.

* Nur aktive und valide Liefermethode werden zur Auswahl angeboten.

* Liefermethoden haben einen Standardpreis.

* Liefermethoden haben optionale zusätzliche Preise, beispielsweise wenn ein 
  bestimmter Wert im Warenkorb erreicht wird.

* Diese Preise können mit Kriterien eingeschränkt werden. Der erste Preis für 
  den alle Kriterien zutreffen ist der eigentliche Preis der Liefermethode. 
  Falls kein zusätzlicher Preis valide ist, so gilt der Standardpreis der 
  Liefermethode.

* Zuerst wird dem Kunden die Standard-Liefermethode zugewiesen. Diese ist (zur
  Zeit und könnte sich ändern) die erste aktive und valid Liefermethode.

* Falls sich die aktuell gewählte Liefermethode invalide wird (nachdem der Kunde
  beispielsweise das Land geändert hat), so wird im die nächste Standard-
  Liefermethode zugewiesen.
  
  
Berechnung der Lieferzeit
=========================

* Lieferzeiten hängen von der Liefermethode ab, d.h. jede Liefermethode hat
  genau eine Lieferzeit.

* Die Lieferzeit eines Produktes kann sich für die Produktansicht und der
  Warenkorbansicht unterschieden.

* Die Lieferzeit eines Produkts für die Produktansicht wird der Standard-
  Liefermethode eines Produktes entnommen. Diese ist zur Zeit die erste gültige 
  (basierend auf Kriterien) Liefermethode eines Produktes.

* Die Lieferzeit eines Produkts für die Warenkorbansicht wird der Liefermethode
  entnommen, die der Shopkunde gewählt hat. Ist diese jedoch für ein Produkt nicht
  gültig (auf Basis ihrer Kriterien), so wird die Lieferzeit auch hier der 
  Standard-Liefermethode entnommen.

* Die Lieferzeiten der Produkte in Warenkorbansicht werden zwar zu Zeit nicht 
  angezeigt, jedoch dienen diese als Basis für die Berechnung der Gesamtlieferzeit 
  des Warenkorbs.

* Ein Produkt kann eine manuelle Lieferzeiten haben. Ist dies der Fall wird diese 
  Lieferzeit angezeigt und die Berechnung auf Basis der Kriterien entfällt.

* Darüber hinaus kann ein Produkt eine Bestellzeit und eine Bestelldatum haben. 
  Ist ein Proudukt nicht mehr auf Lager, wird diese Bestellzeit (abzüglich der 
  bereits vergangenen Tage seit der Bestellung) hinzugefügt.