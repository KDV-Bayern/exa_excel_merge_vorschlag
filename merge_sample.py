#
# Voraussetzungen:
#
# pip install xlrd
# pip install sqlite3
#
# oder unter z. B. Ubuntu: apt install python3-xlrd python3-sqlite3
#

import sqlite3
import xlrd

SQLITE_FILE = "database.db"
connection = sqlite3.connect(SQLITE_FILE)

#con.execute("create table pruefungsergebnis (pruefung_id int not null, "\
#    + "mtknr int not null, note decimal(3,1), primary key(pruefung_id, mtknr))")
#con.commit()

# Hier als Konstante, da in der Praxis wahrscheinlich aus Kontext
# in Webanwendung abgeleitet
PRUEFUNG_ID = 5

def read_file(filename):
    # alle Validierungsschritte zugunsten eines übersichtlichen Beispiels eingespart
    xlfile = xlrd.open_workbook(filename)
    xlsheet = xlfile.sheet_by_index(0)
    print(f"Importiere aus {filename} - {xlsheet.name}")

    data = {
        int(xlsheet.cell(rx, 0).value): xlsheet.cell(rx, 1).value
        for rx in range(1, xlsheet.nrows)
    }

    return data


def is_already_set(con, pruefung_id, mtknr):
    sql = "select count(*) as anzahl from pruefungsergebnis where pruefung_id = ? and mtknr = ?"
    cur = con.cursor()
    cur.execute(sql, (pruefung_id, mtknr))
    result = cur.fetchone()[0]
    return result >= 1


def is_valid_value(pruefung_id, note):
    # Im realen System z. B. auf der Basis der Notengebungsart etc. prüfen
    return note is not None and note in [
        1, 1.3, 1.7, 2, 2.3, 2.7, 3, 3.3, 3.7, 4, 5
    ]


def is_modified(con, pruefung_id, mtknr, note):
    sql = "select count(*) as anzahl from pruefungsergebnis" \
        + " where pruefung_id = ? and mtknr = ? and note = ?"
    cur = con.cursor()
    cur.execute(sql, (pruefung_id, mtknr, note))
    result = cur.fetchone()[0]
    return result == 0


def merge_data(pruefung_id, new_data):
    update_sql = "update pruefungsergebnis set note = ? where pruefung_id = ? and mtknr = ?"
    insert_sql = "insert into pruefungsergebnis (pruefung_id, mtknr, note) values (?, ?, ?)"
    # Transaktionsscope: Fehler führt zuverlässig zum Verwerfen
    # aller Änderungen aus einer Excel-Datei
    with connection:
        for mtknr in new_data.keys():
            note = new_data[mtknr]
            if is_already_set(connection, pruefung_id, mtknr):
                if is_valid_value(pruefung_id, note):
                    if is_modified(connection, pruefung_id, mtknr, note):
                        print(f"Wollen Sie die Note zu {mtknr} auf {note} aktualisieren? (j/n)")
                        answer = input()
                        if answer == 'j':
                            connection.execute(update_sql, (note, pruefung_id, mtknr))
                            print("angepasst")
                        else:
                            print("unverändert")
                    else:
                        print(f"Note zu {mtknr} wird nicht geändert, Notenwert unverändert")
                else:
                    print(f"Note zu {mtknr} wird nicht geändert, Zeile leer oder ungültig")
            elif is_valid_value(pruefung_id, note):
                print(f"Mtknr: {mtknr} Note: {note} hinzufügen")
                # im Falle von HISinOne wegen bereits bestehendem Anmeldesatz auch Update, so aber
                # einfacher im Beispiel darzustellen...
                connection.execute(insert_sql, (pruefung_id, mtknr, note))
            else:
                print(f"Fehlender oder ungültiger Notenwert für Mtknr {mtknr}")


f1 = read_file("excel_file_1.xlsx")
merge_data(PRUEFUNG_ID, f1)

f2 = read_file("excel_file_2.xlsx")
merge_data(PRUEFUNG_ID, f2)
