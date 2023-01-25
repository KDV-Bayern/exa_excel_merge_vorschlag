import xlrd
import sqlite3

SQLITE_FILE = "database.db"
con = sqlite3.connect(SQLITE_FILE)
#con.execute("create table pruefungsergebnis (pruefung_id int not null, mtknr int not null, note decimal(3,1), primary key(pruefung_id, mtknr))")
#con.commit()

# Hier als Konstante, da in der Praxis wahrscheinlich aus Kontext in Webanwendung abgeleitet
PRUEFUNG_ID = 2

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


def merge_data(new_data):
    update_sql = "update pruefungsergebnis set note = ? where pruefung_id = ? and mtknr = ?"
    insert_sql = "insert into pruefungsergebnis (pruefung_id, mtknr, note) values (?, ?, ?)"
    with con: # Transaktionsscope: Fehler führt zuverlässig zum Verwerfen aller Änderungen aus einer Excel-Datei
        for mtknr in new_data.keys():
            note = new_data[mtknr]
            if is_already_set(con, PRUEFUNG_ID, mtknr):                
                print(f"Wollen Sie die Note zu {mtknr} auf {note} aktualisieren? (j/n)")
                answer = input()
                if answer == 'j':
                    con.execute(update_sql, (note, PRUEFUNG_ID, mtknr))
                    print(f"angepasst")
                else:
                    print(f"wird nicht geändert")
            else:
                print(f"Mtknr: {mtknr} Note: {note}")
                # im Falle von HISinOne wegen bereits bestehendem Anmeldesatz auch Update, so aber
                # einfacher im Beispiel darzustellen...
                con.execute(insert_sql, (PRUEFUNG_ID, mtknr, note))



f1 = read_file("excel_file_1.xlsx")
merge_data(f1)

f2 = read_file("excel_file_2.xlsx")
merge_data(f2)
