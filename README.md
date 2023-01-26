# Vorschlag: Zusammenführen statt Überschreiben im Excel-Upload für Prüfungsergebnisse

In diesem Repository beschreiben wir einen Vorschlag zur konsistenten und nutzerfreundlichen Verarbeitung
mehrerer sequenziell ausgeführter Uploads von Excel-Dateien mit Noten zu einer Prüfung. 

Das Verfahren soll sicherstellen, dass auch dann, wenn mehrere Prüfer einer gemeinsamen Prüfung unabhängig voneinander Leistungen via Excel-Import 
bereitstellen, keine bereits eingetragenen Noten gelöscht werden.

Hintergrund der Anforderung ist, dass insb. bei großen Prüfungen einem Prüfungsorganisationssatz mehrere Prüfer\*innen zugewiesen werden. Bei Prüfungsanmeldung melden sich Studierende also für einen Prüfungsorganisationssatz mit mehreren Prüfer\*innen an. Erst im Nachgang (also nach Prüfungsanmeldung) wird die Korrektur der Prüfung unter den Prüfer\*innen aufgeteilt. Eine eindeutige Zuordnung Studierender für einen einzelnen Prüfer\*in ist somit bei Prüfungsanmeldung noch nicht möglich. Jeder Prüfer*in einer Prüfergruppe soll also unabhängig die Noten seiner Prüflinge per Excel-Datei pro Prüfungsorganisationssatz uploaden können. Derzeit muss zwingend die Noteneingabemaske verwendet werden, denn ein Upload eines Prüfers überschreibt den vorigen Upload des anderen Prüfers. Es "zählt" der letzte Upload bevor die Noteneingabe abgeschlossen werden kann. Somit läuft die Hochschule Gefahr Prüfungsleistungen unvollständig oder falsch abzubilden.

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
      wenn Note gültig
        ja:
          Wert setzen
          ggf. in GUI sichtbarer Protokolleintrag
        nein: 
          Wert nicht setzen
          ggf. in GUI sichtbarer Protokolleintrag
```

### Output eines Durchlaufs mit den gegebenen Testdaten

```
~/git/example_merge_bug4599$ python3 merge_sample.py 

Importiere aus excel_file_1.xlsx - Tabelle1
Mtknr: 1 Note: 1.0 hinzufügen
Mtknr: 2 Note: 1.3 hinzufügen
Mtknr: 3 Note: 1.0 hinzufügen
Mtknr: 4 Note: 3.0 hinzufügen
Mtknr: 5 Note: 2.3 hinzufügen
Fehlender oder ungültiger Notenwert für Mtknr 6
---
Datenbankstand nach Import: 

pruefung_id     mtknr   note
6               1       1
6               2       1.3
6               3       1
6               4       3
6               5       2.3
---
Importiere aus excel_file_2.xlsx - Tabelle1
Wollen Sie die Note zu 1 auf 1.3 aktualisieren? (j/n)
j
angepasst
Mtknr: 7 Note: 1.3 hinzufügen
Mtknr: 8 Note: 1.0 hinzufügen
Mtknr: 9 Note: 3.0 hinzufügen
Note zu 2 wird nicht geändert, Zeile leer oder ungültig
Note zu 3 wird nicht geändert, Zeile leer oder ungültig
---
Datenbankstand nach Import: 

pruefung_id     mtknr   note
6               1       1.3
6               2       1.3
6               3       1
6               4       3
6               5       2.3
6               7       1.3
6               8       1
6               9       3
```