Kategorien
==========

Allgemein
---------

- Kategorien dienen zur Navigation durch den Shop.
- Kategorien können eine beliebige Anzahl von Produkten zugeordnet bekommen.
- Kategorien können beliebig tief verschachtelt werden.
- Kategorien haben eine Ansichten zu Darstellung ihrer Produkte oder 
  Unterkategorien.
- Diese Ansichten können variable formattiert werden.
- Kategorien können ein :term:`static block` zugeordnet werden zur von beliebigen 
  HTML auf der Kategorieansicht.

Category Tab
------------

- **Name**
    Der Name der Kategorie. Dieser wird u.a. in der Navigation angezeigt.

- **Slug** 
    Dies ist Teil der URL um die Kategorie anzuzeigen. Dieser muss einzigartig 
    unter allen Kategorien sein.
    
- **Elternkategorie**
    Die direkt übergeordnete Kateogrie. Falls diese leer ist, so handelt es sich 
    um eine Top-Level-Kategorie des Shops.

- **Kurzbeschreibung**
    Kurze Beschreibung der Kategorie. Diese wird in einer Übersicht über 
    Kategorien angezeigt, beispielsweise wenn die Ansichtsart ``Unterkategorien``
    für eine Kategorie oder den Shop ausgewählt ist.
    
- **Beschreibung**
    Die Beschreibung der Kategorie. Diese wird in der Detailansicht einer 
    Kategorie angezeigt.

- **Bild**
    Das Bild der Kategorie. Diese wird in einer Übersicht über 
    Kategorien angezeigt, beispielsweise wenn die Ansichtsart ``Unterkategorien``
    für eine Kategorie oder den Shop ausgewählt ist.

- **Statischer Block**
    Falls ein statischer Block ausgewählt ist, so wird dieser in der 
    Detailansicht einer Kategorie angezeigt.
    
- **Content**
    This decides whether the products or the sub category of a category is 
    displayed.

- **Active formats**
    If selected ``product rows``, ``product cols`` and ``category cols`` of the
    category are taken. Otherwise the category inherits formats from the parent
    category.
    
- **product rows**
    If a categories content is ``products`` then so many rows of products are 
    displayed.

- **product cols**
    If a categories content is ``products`` then so many cols of products are 
    displayed.
    
- **categories cols**
    If a categories content is ``categories`` then so many cols of categories 
    are displayed.

Please note that the formats are inherited by sub categories (if they don't 
have ``àctive formats`` selected). So even if a category has selected 
``products`` the information for ``category cols`` could be important for sub 
categories and vice versa.

Products Tab
------------

This tab is used to assign products to the displayed category.

SEO Tab
-------

- **Meta keywords**
   The meta keywords of the category. The content of this field is used for the 
   meta keywords tag of the category page.
   
- **Meta description**
   The meta description of the category. the content of this field is used for 
   the meta description tag of the category page.
   