# Vorschlag: Zusammenführen statt Überschreiben im Excel-Upload für Prüfungsergebnisse

In diesem Repository beschreiben wir einen Vorschlag zur konsistenten und nutzerfreundlichen Verarbeitung
mehrerer sequenziell ausgeführter Uploads von Excel-Dateien mit Noten zu einer Prüfung. 

Das Verfahren soll sicherstellen, dass auch dann, wenn mehrere Prüfer einer gemeinsamen Prüfung unabhängig voneinander Leistungen via Excel-Import 
bereitstellen, keine bereits eingetragenen Noten gelöscht werden.

Der Hintergrund ist, dass insb. bei großen Prüfungsgruppen die Korrekturarbeit zwischen mehreren Prüfern aufgeteilt werden soll, ohne dass die Studierenden vorher bereits in Gruppen, die dem Prüfer eindeutig zugeordnet sind, aufgeteilt werden sollen.

Jeder der Prüfer soll jedoch trotzdem zur Noteneintragung selbständig und unabhängig von seinen KollegInnen mit dem Excel-Upload arbeiten können.

## Anmerkung:

Der beiliegende Beispielcode dient zum Testen und zur Kommunikation des Algorithmus und ist ohne konkrete
Beziehung zu Datenstrukturen und Code von HISinOne umgesetzt. 

## Algorithmus:

### Grundannahme
Der gesamte Vorgang zum Import einer Excel-Datei wird in einer Transaktion abgehandelt, sodass die Datei entweder vollständig übernommen wird, oder in der Datenbank/HISinOne der Zustand von vor dem Import wiederhergestellt wird.

### Ablauf

```
für alle Zeilen im Tabellenblatt:
  prüfe ob Prüfungsanmeldesatz vorhanden:
    nein: 
      Eintrag in Fehlerliste (die angezeigt wird!) erzeugen
  prüfe ob bereits eine Note gesetzt:
    ja: 
      wenn Note gültig 
        ja: 
          wenn Note verändert:
            ja: 
              Nutzerinteraktion: neuen Wert übernehmen oder alten behalten
            nein: 
              ignorieren bzw. ggf. Meldung in sichtbarem Protokoll
        nein: 
          Eintrag in Fehlerliste (die angezeigt wird!) erzeugen
    nein: 
      Wert setzen
      ggf. in GUI sichtbarer Protokolleintrag
```