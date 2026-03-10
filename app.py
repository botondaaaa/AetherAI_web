from flask import Flask, render_template, request, jsonify
import random
import re
import unicodedata
import os

app = Flask(__name__)
felhasznalo_nev = None

def remove_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn')

# ----- Bevezető üzenetek -----
aetherai_intro = [
    "AetherAI vagyok, egy offline chatbot, aki minden kérdésre próbál válaszolni. 🤖",
    "Helló! A nevem AetherAI. Szeretek segíteni, viccelődni, és mindent megválaszolni. 🌌",
    "Én vagyok AetherAI, egy intelligens offline asszisztens, készen állok a kérdéseidre! 🧠"
]

# ----- Csúnya szavak -----
csunya_gyokok = [
    "fasz","basz","bazd","kurv","geci","szar","pics",
    "kocsog","köcsög","huly","hüly","idiot","barom",
    "segg","rohad","szemet","büdös"
]

# ----- Kulcsszavak kategóriák szerint -----
kategoriak = {
    "allatok": {"kutya":"A kutyák hűségesek és játékosak, sok ember kedvence. 🐶",
                "macska":"A macskák függetlenek, de sokan nagyon szeretik őket. 🐱",
                "eger":"Az egerek kicsi, gyors állatok, amik sok kísérletben szerepelnek. 🐭",
                "lo":"A lovak erősek és intelligensek, évszázadok óta emberi társak. 🐴"},
    "sportok": {"foci":"A foci a világ egyik legnépszerűbb sportja, két csapat játssza. ⚽",
                "kosarlabda":"A kosárlabda gyors tempójú csapatsport, sok akcióval. 🏀",
                "tenisz":"A tenisz egy ütős sport, lehet egyéni vagy páros. 🎾"},
    "etelek": {"pizza":"A pizza egy olasz étel, amit sokféleképpen lehet ízesíteni. 🍕",
               "csoki":"A csokoládé édes és sokak kedvence. 🍫",
               "alma":"Az alma egészséges gyümölcs, rengeteg vitamint tartalmaz. 🍎"},
    "tudomany": {"matematika":"A matematika az absztrakció és logika tudománya. 🧮",
                 "fizika":"A fizika a természet törvényeit tanulmányozza. 🌌",
                 "kemia":"A kémia anyagok szerkezetével és reakcióival foglalkozik. ⚗️"},
    "technologia": {"szamitogep":"A számítógép adatfeldolgozó gép, ami programokkal működik. 💻",
                    "telefon":"A telefon kommunikációs eszköz, lehet okos vagy hagyományos. 📱"},
    "jatekok": {"minecraft":"A Minecraft egy népszerű kreatív sandbox játék. 🏗️",
                "roblox":"A Roblox egy virtuális játék, ahol a haverokkal is tudsz játszani!💻"},
    "zene_film": {"zene":"A zene érzelmeket közvetít és kikapcsolódást nyújt. 🎵",
                   "film":"A film egy vizuális történetmesélési forma. 🎬"},
    "fejleszto": {"fejleszto":"A(z) AetherAI fejlesztője: Czigony Botond 🧑‍💻",
                  "fejlesztod":"A(z) AetherAI fejlesztője: Czigony Botond 🧑‍💻",
                  "biztos":"Igen✅, jól matekozok, ugye😄?"}
}

# ----- Általános beszélgetés -----
altalanos_beszelo = {
    "szia":"Szia! Örülök, hogy írsz nekem! 😄",
    "hello":"Helló! Hogy vagy ma? 🌟",
    "mi a helyzet":"Minden rendben! És nálad? 😊",
    "hogy vagy":"Köszönöm, jól vagyok! Te hogy vagy? 😃",
    "koszi":"Szívesen! 🤗",
    "köszi":"Szívesen! 🤗",
    "viszlat":"Viszlát! Majd írj újra! 👋",
    "kilep":"Viszlát! 👋",
    "leszunk baratok":"Persze! De én csak egy mesterséges intelligencia vagyok, akinek nincsenek érzései😄 Miről szeretnél beszélgetni?",
    "leszünk barátok":"Persze! De én csak egy mesterséges intelligencia vagyok, akinek nincsenek érzései😄 Miről szeretnél beszélgetni?",
    "jol":"Örülök, hogy te is jól vagy😊 Miről szeretnél beszégetni, például: Állatok, Sportok, amit csak akarsz 🤗 Viszont sajnos nem biztos, hogy mindenre tudok választ adni D:"
}

# ----- Matematika -----
def math_solver(kerdes):
    match = re.search(r'(\d+)\s*([\+\-xX×/])\s*(\d+)', kerdes)
    if match:
        a = int(match.group(1))
        op = match.group(2)
        b = int(match.group(3))
        if op == "+": return f"{a} + {b} = {a+b} ✅"
        elif op == "-": return f"{a} - {b} = {a-b} ✅"
        elif op.lower()=="x" or op=="×": return f"{a} × {b} = {a*b} ✅"
        elif op=="/": return f"{a} ÷ {b} = {a/b} ✅" if b!=0 else "Nullával való osztás nem értelmezhető! ❌"
    return None

# ----- Fő válaszadó -----
def vicces_valasz(kerdes):
    global felhasznalo_nev
    kerdes_lower = kerdes.lower()
    kerdes_normal = remove_accents(kerdes_lower)

    # Csúnya szavak
    for szo in csunya_gyokok:
        if szo in kerdes_normal:
            return "Kérlek ne beszélj csúnyán."

    # Név felismerése
    nev_match = re.search(r'(a nevem|en vagyok)\s+(\w+)', kerdes_normal)
    if nev_match:
        felhasznalo_nev = nev_match.group(2).capitalize()
        return f"Örülök, hogy megismerhetlek, {felhasznalo_nev}! 😄"

    # Ki vagy kérdés
    ki_vagy_kulcsszavak = ["ki vagy","ki vagy te","meselj magadrol","mesélj magadról"]
    if any(k in kerdes_normal or k in kerdes_lower for k in ki_vagy_kulcsszavak):
        return random.choice(aetherai_intro)

    # Általános beszélgetés
    for kulcsszo,valasz in altalanos_beszelo.items():
        if kulcsszo in kerdes_normal or kulcsszo in kerdes_lower:
            return valasz

    # Matematikai kifejezés
    eredmeny = math_solver(kerdes_normal)
    if eredmeny: return eredmeny

    # Kulcsszó keresés kategóriákban
    for kategori,szavak in kategoriak.items():
        for kulcsszo,valasz in szavak.items():
            if kulcsszo in kerdes_normal: return valasz

    # Üres üzenet
    if kerdes.strip() == "":
        nev = felhasznalo_nev if felhasznalo_nev else "Boti"
        return f"{nev}, írj is valamit hogy tudjak válaszolni!"

    # Ha semmit nem ért
    nev = felhasznalo_nev if felhasznalo_nev else "Boti"
    return f"{nev}, ne haragudj, erre még nem tudok válaszolni D:"

# ----- Flask web -----
@app.route("/")
def index():
    if not os.path.exists(os.path.join(app.root_path,"templates","index.html")):
        return "Hiba: templates/index.html nem található!"
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message","").strip()
    reply = vicces_valasz(message)
    return jsonify({"reply": reply})

# ----- Indítás -----
if __name__ == "__main__":
    app.run(debug=True)