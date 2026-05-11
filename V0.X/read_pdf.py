import os, fitz, re

wd = os.path.dirname(os.path.realpath(__file__))
file_list = os.listdir(wd)

with fitz.open(wd + "/85108700_2025_Nr.001_Kontoauszug_vom_2025.01.31_20250209125212.pdf") as doc:
    num_pages = len(doc)-1

    all = []
    scripe_start = False
    scripe_pause = False
    for page in range(num_pages):
        page_txt = doc[page].get_text()
        line_split = page_txt.split("\n")
        for line in line_split:
            clean_line = [x for x in line.split(" ") if x != ""]
            pattern = r"\d{2}\.\d{2}\."
            if len(clean_line) > 2:
                if bool(re.fullmatch(pattern, clean_line[0])) and bool(re.fullmatch(pattern, clean_line[1])):
                    scripe_start = True
                if clean_line[0] == "neuer" and clean_line[1] == "Kontostand":
                    scripe_start = False
            if len(clean_line) >= 1:
                if clean_line[0] == "Vorgang":
                    scripe_pause = False
                    continue
                if clean_line[0] == "Übertrag":
                    scripe_pause = True
            if scripe_start and not scripe_pause:
                all.append(clean_line)

activity = []
extra_info = []
extra = []
for line in all:
    #print(line)
    pattern = r"\d{2}\.\d{2}\."
    if len(line) > 2:
        if bool(re.fullmatch(pattern, line[0])) and bool(re.fullmatch(pattern, line[1])):
            if len(extra) > 0:
                extra_info.append(extra)
                extra = []
            activity.append(line)
        else:
            extra.append(line)
    else:
        extra.append(line)
extra_info.append(extra)

extra_info = [[element for sublist in info for element in sublist] for info in extra_info]


for i in range(len(activity)):
    print(activity[i])
    print(extra_info[i])


out_file = wd + "/clean_out.txt"

fout = open(out_file, "w")

for i in range(len(activity)):
    if activity[i][-1] == "H":
        if len(extra_info[i]) >= 3:
            #   Oma Taschengeld
            if extra_info[i][0] == "Maria" and extra_info[i][2] == "taschengeld":
                fout.write("0\t{}\t{}\t{}\t{}\n".format(activity[i][-2],"Taschengeld", "Oma Maria", "Überweisung"))
                continue
            #   Eltern Unterhalt
            if extra_info[i][0] == "Christoph" and extra_info[i][2] == "Unterhalt":
                fout.write("0\t{}\t{}\t{}\t{}\n".format(activity[i][-2],"Taschengeld", "Eltern", "Überweisung"))
                continue
        #   Abschluss
        if activity[i][2] == "Abschluss":
            fout.write("0\t{}\t{}\t{}\t{}\n".format(activity[i][-2],"Abschluss", "PN:905", "Überweisung"))
            continue
        fout.write("0\t{}\n".format(activity[i][-2]))
    if activity[i][-1] == "S":
        if len(extra_info[i]) >= 3:
            #   ASB
            if extra_info[i][0] == "Arbeiter-Samariter-Bund":
                fout.write("{}\t0\t{}\t{}\t{}\n".format(activity[i][-2],"Spende", "ASB", "Abbuchung"))
                continue
            #   Rewe
            if extra_info[i][0] == "REWE":
                fout.write("{}\t0\t{}\t{}\t{}\n".format(activity[i][-2],"Essen", "Rewe", "Karte"))
                continue
            #   DM
            if extra_info[i][0] == "DM":
                fout.write("{}\t0\t{}\t{}\t{}\n".format(activity[i][-2],"Hausrat", "DM", "Karte"))
                continue
            #   Crunchyroll
            if extra_info[i][0] == "Leonie" and extra_info[i][2] == "Crunchyroll":
                fout.write("{}\t0\t{}\t{}\t{}\n".format(activity[i][-2],"Unterhaltung", "Leo Crunchy", "Überweisung"))
                continue
            #   O2
            if extra_info[i][0] == "Telefonica" and activity[i][-2] == "15,00":
                fout.write("{}\t0\t{}\t{}\t{}\n".format(activity[i][-2],"Nebenkosten", "O2", "Paypal"))
                continue
            #   Einstein
            if extra_info[i][7] == "Einstein" and activity[i][-2] == "49,00":
                fout.write("{}\t0\t{}\t{}\t{}\n".format(activity[i][-2],"Sport", "Einstein", "Abbuchung"))
                continue
            #   Steam
            if "www.steampowered.com" in extra_info[i]:
                fout.write("{}\t0\t{}\t{}\t{}\n".format(activity[i][-2],"Zocken", "Steam", "Paypal"))
                continue
            #   Galeria
            if extra_info[i][0] == "GALERIA":
                fout.write("{}\t0\t{}\t{}\t{}\n".format(activity[i][-2],"", "Galeria", "Karte"))
                continue
            #   Etsy
            if "ETSY" in extra_info[i]:
                fout.write("{}\t0\t{}\t{}\t{}\n".format(activity[i][-2],"", "Etsy", "Paypal"))
                continue
            #   Bauhaus
            if extra_info[i][0] == "BAUHAUS":
                fout.write("{}\t0\t{}\t{}\t{}\n".format(activity[i][-2],"", "Bauhaus", "Karte"))
                continue
        #   Abheben
        if activity[i][2] == "Auszahlung":
            fout.write("{}\t0\t{}\t{}\t{}\n".format(activity[i][-2],"Bargeld", "", "Abheben"))
            continue
        
        fout.write("{}\t0\n".format(activity[i][-2]))

fout.close

