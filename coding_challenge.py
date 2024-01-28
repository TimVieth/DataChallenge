import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt




#################################################
################ read data ######################
#################################################

df_freq = pd.read_csv(r'c:\\Users\\User\\Desktop\\Code\\coding_challenge_aktuariat\\freMTPL2freq.csv'
                      , dtype={'IDpol': 'object'})


df_sev = pd.read_csv(r'c:\\Users\\User\\Desktop\\Code\\coding_challenge_aktuariat\\freMTPL2sev.csv'
                      , dtype={'IDpol': 'object'})



#################################################
############ data exploration ###################
#################################################



#### Es gibt packages mit integrierten Funktion, die Datenqualität prüfen. Darüber können verschiedene Test gemacht werden,
#### die Ausreißer, Anomalien oder fasche Daten besser erkennen. Ich beschränke mich hier auf zugänglichere grundlegende 
#### Überprüfungen.

# Prüfe ob null values vorliegen

df_freq.isnull().values.any()
df_sev.isnull().values.any()

# Überprüfe Güte von IDpol

df_freq.dtypes
df_freq = df_freq.astype({'IDpol':'object'})
df_freq["IDpol"][df_freq["IDpol"].duplicated() == True]



#################################################
########## Betrachtung der Policendaten #########
#################################################



# Print Histogramme mit Ausprägungen der Merkmale für ersten Eindruck
# Schritt zur Validierung der Daten und für ersten Eindruck

def plot_hist(df, merkmal, df_name):
    df = pd.DataFrame(
        df.groupby([merkmal])["IDpol"].count().reset_index()
        )
    plt.bar(x = df[merkmal], height = df["IDpol"])
    plt.xlabel(merkmal)
    plt.ylabel("Anzahl")
    plt.title("Anzahl Policen nach Ausprägung in " + df_name)
    plt.show()


    
cols_to_plot = df_freq.columns.to_list()
cols_to_plot.remove("IDpol")

for col in cols_to_plot:
    plot_hist(df_freq, col, "df_freq")

# Region - Sehr granular, aber noch zu plotten
# Exposure - Nicht sinnvoll so zu plotten, besser in bins. Außerdem auffällig, dass es Werte größer 1 gibt 
# ClaimNb - Scheint Ausreißer nach oben zu haben
# VehBrand - umfasst weniger Ausprägungen als gedacht
# VehPower - liegt im Bereich 4 - 15, sind das Leistungsklassen? PS/kW kann es nicht sein
# BonusMalus - soll SF-Klasse beinhalten, aber warum Werte zwischen 50 und 230 und Ausschläge?
# VehGas -  umfasst nur Diesel, Regular, kein Elektro oder Spezialkraftstoffe (E-Fuels, H2, Bio, ...)
# Density - nicht zu plotten, muss in bins betrachtet werden

# Genauere Betrachtung Exposure
df_freq["Exposure"].describe()

plt.hist(df_freq["Exposure"], bins=100, edgecolor = "white")
plt.show()

plt.hist(df_freq["Exposure"][df_freq["Exposure"]<=1], bins=100, edgecolor = "white")
plt.show()

plt.hist(df_freq["Exposure"][df_freq["Exposure"]<=0.1], bins=100, edgecolor = "white")
plt.show()

df_freq[df_freq["Exposure"] > 1]
df_freq[df_freq["Exposure"] == 1]
df_freq[df_freq["Exposure"] < 1/365]

# Wieso gibt es Daten mit Exposure > 1? Die Häufigkeit von Daten mit Exposure = 1 deutet auf eine Jahresscheibe als Betrachtungszeitraum
# Spitze bei 0.08, also Laufzeit von 1 Monat 
# Was ist mit sehr kleinem Exposure? Schwelle für Sofortstorno bei 1/365? 
# Für weitere Tarifierung werden Exposure >1 entfernt

df_freq = df_freq[df_freq["Exposure"] <= 1]

# Betrachte Density in bins
plt.hist(df_freq["Density"], bins=50, edgecolor = "white")
plt.show()

# extremer Ausreißer bei hoher Dichte
df_freq[df_freq["Density"] >= 15000]

# Verdacht: Nur in Area "F", Region "R11"
df_freq[df_freq["Density"] >= 15000][["Region","Area"]].drop_duplicates()

# Betrachten, wie Region und Area mit Density zusammenhängen

df_area = pd.DataFrame(
        df_freq.groupby(["Area"])["Density"].mean().reset_index()
        )

# Area beinhaltet verschiedener durchschnittliche Density in Areas 

df_region = pd.DataFrame(
        df_freq.groupby(["Area","Region"])["Density"].count().reset_index()
        )

# Bei Region ist nicht klar, wie es mit Area zusammenhängt. Man könnte den Zusammenhang anhand verschiedener Merkmale prüfen,
# da Region später aber nicht als Tarifmerkmal gewählt wird, ist dieser Schritt nicht entscheidend

# genauere Betrachtung von ClaimNb
df_freq[df_freq["ClaimNb"] >= 5]

# Auffälligkeit von hohe Claims in Area "D", Region "R91" - Fast alle Policen mit ClaimNb > 5 kommen aus dieser Area und Region



#################################################
#### genauere Betrachtung der Schadendaten ######
#################################################

df_sev["ClaimAmount"].describe()


plt.hist(df_sev["ClaimAmount"], bins=50, edgecolor = "white")
plt.show()

plt.hist(df_sev["ClaimAmount"][df_sev["ClaimAmount"] > 500000], bins=50, edgecolor = "white")
plt.show()

plt.hist(df_sev["ClaimAmount"][df_sev["ClaimAmount"] < 5000], bins=50, edgecolor = "white")
plt.show()


# Auffällig Spitzen zwischen 1100 und 1300 - Könnten Fixbeträge sein oder Betrugsfälle - 1204 scheint Fixbetrag zu sein
# Hier könnte man sich die IDpol zu den Fällen anschauen und prüfen, ob eine IDpol mehrere SChäden mit gleichem Betrag 
# eingereicht hat. Außerdem könnte Nachfrage bei Prouktmanagment zu diesen Fixbeträgen Aufschluss geben

# Klassifizierung von Großschäden, um den Tarif nicht durch weniger große Ausreißer zu verzerren

plt.hist(df_sev["ClaimAmount"][df_sev["ClaimAmount"] > 500000], bins=50, edgecolor = "white")
plt.show()

# Nach einigen Versuchen mit der obern Grenze sieht es aus, als wäre ab 500.000 die Datenlage zu dünn für eine Einbeziehung in das Tarifomdell.
# Durch einzelne Großschäden (Anzahl 4) könnte der Tarif verzerrt werden. (Man könnte noch schauen, was die gemeinsam haben) 
# Deshalb Klassifizierung als Großschäden und Ausschlus aus Tarifierung. 

df_GS = df_sev[df_sev["ClaimAmount"] > 500000]
df_sev = df_sev[df_sev["ClaimAmount"] <= 500000]


# Gruppierung der Schäden pro IDpol mit Summe und Anzahl, um Schäden pro Police zu erhalten

df_sev_g = pd.DataFrame(
        df_sev.groupby(["IDpol"])["ClaimAmount"]
            .agg(["sum", "count"])
            .reset_index()
            .rename(columns={"sum": "Schadensumme", "count": "Schadenanzahl"})
        )

# Kompatibilität von df_freq und df_sev prüfen

df_freq["ClaimNb"].sum()
len(df_sev.index)


# In der Policentabelle sind 36102 SChäden angegeben, aber nur 26639 sind in Schadentabelle aufgeführt.
# Man muss nun feststellen, ob die Daten zu einem bestimmten Merkmaln fehlen, oder allgemein unvollständig sind

# Left join an die Policentabelle

df_all = df_freq.merge(df_sev_g, how= "left", on= "IDpol").fillna(0).astype({'Schadenanzahl':'int'})

# genauere Betrachtung fehlende Schadendaten

df_all["Schadenvalidierung"] = df_all["ClaimNb"] - df_all["Schadenanzahl"]
plt.hist(df_all["Schadenvalidierung"][df_all["Schadenvalidierung"] != 0], edgecolor = "white")
plt.show()

df_all_inkl = df_freq.merge(df_sev_g, how= "outer", on= "IDpol").fillna(0).astype({'Schadenanzahl':'int'})
len(df_all_inkl.index)

# Es gibt 6 Schäden, die nicht zu Policen zugeordnet werden können
# Etwa 10000 Schäden, die in der Policentabelle gegeben sind, finden sich nicht in der Schadentabelle wieder

df_missing = df_all[df_all["ClaimNb"] != df_all["Schadenanzahl"]]

# Vergleiche Ausprägung der Merkmal in Gesamtheit der Policen, bei denen Schäden angefallen sind mit
## Policendaten, bei denen die Schadenhöhen fehlen

cols_to_plot_2 = df_all.columns.to_list()
for item in ["IDpol", "Exposure", "ClaimNb", "Schadensumme", "Density", "Schadenvalidierung", "Schadenanzahl"]:
    cols_to_plot_2.remove(item)

for col in cols_to_plot_2:
    plot_hist(df_missing, col, "df_missing")
    plot_hist(df_freq[df_freq["ClaimNb"] > 0], col, "df_freq mit ClaimNb > 0")


# Auffällig: Viele Schadenfälle missing bei kleinem Veh_Age, Veh_Brand "B12" und Gas "Regular", 

# Genauere Betrachtung von VehAge
plot_hist(df_missing[df_missing["VehAge"].between(0,40)], "VehAge", "df_missing")
plot_hist(df_freq[(df_freq["ClaimNb"] > 0) & (df_freq["VehAge"].between(0,40))], 
                      "VehAge", "df_freq > 0")

# Tatsächlich viele Schadenfälle bei jungen Fahren missing

# Sollte man dann die Policen mit fehlenden Schadendaten aus der Schadenhöhenmodellierung ausschließen?
## Pro: Wenn man die fehlenden Daten ignoriert, werden die Ausprägungen mit ungewöhnlich hohem Anteil an missing zu gut bewertet
## Pro: Man arbeitet mit einer Teilmenge der Schadenaten, die in den Tarifmerkmalen dieselbe Verteilung haben
### wie die Gesamtheit der Policen mit Schäden und man mit vollständigen Informationen zu den vorhandenen Daten arbeitet
## Kontra: Bspw. Veh_Age hat im Normalfall einen großen Einfluss auf den Tarif
# Für Schadenfrequenz kann man die Angaben aus der freq Tabelle nutzen, hier sind die Schadenhöhen nicht relevant


# Zusammenfassung der Datenlage und vermuteten Tarifmerkmale:
# Aufgrund der schlechten Datenlage könnten folgende Merkmale als Tarifmerkmale ausheschlossen werden:
## VehBrand, VehAge, Gas



##########################################################
### plotten von Exposure und Schadenhöhen nach Merkmal ###
##########################################################

df_all_clean = df_all[df_all["Schadenvalidierung"] == 0].drop(columns=["Schadenvalidierung"])

# Plan für Plot: Pro Tarifmerkmal ein plot. x-Achse: Ausprägung des Merkmals
## y-Achse: Exposure als Barplot, Schdadenhöhe als Linie. Oder durchschnittlicher Schaden?


# Funktion, um Exposure und Schadensumme zu plotten

def plot_sb(df, merkmal):
    df = pd.DataFrame(df.groupby([merkmal])
            .agg(
                Exposure=("Exposure", "sum"), 
                Schadensumme=("Schadensumme", "sum")
                )
            .reset_index())

    figure, axisl = plt.subplots()

    # x-Achse
    axisl.set_xlabel(merkmal)
    
    # zweite y-Achse
    axisr = axisl.twinx()

    # Anpassung y-Achse links und Bars

    axisl.set_ylabel("Exposure", color="tab:blue")
    axisl.set_ylim(0, df["Exposure"].max()*1.5)
    axisl.bar(df[merkmal], df["Exposure"], color="tab:blue")  
    axisl.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
  
    # Anpassung y-Achse rechts und Linie

    axisr.set_ylabel("Schadensumme", color="tab:red")
    axisr.set_ylim(0, df["Schadensumme"].max()*1.2)
    axisr.plot(df[merkmal], df["Schadensumme"], color="tab:red")
    axisr.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))  
   
    plt.title("Exposure und Schadensumme nach " + merkmal)
    plt.show()

# Plotten von Exposure und Schadensumme pro Merkmal

cols_to_plot_3 = df_all_clean.columns.to_list()

cols_to_drop = ["IDpol", 
                "ClaimNb", 
                "Exposure", 
                "Density",
                "Schadensumme", 
                "Schadenanzahl"]

for item in cols_to_drop: 
    cols_to_plot_3.remove(item)

for merkmal in cols_to_plot_3:
    plot_sb(df_all_clean, merkmal)


### Analyse
# Area: Merkmal im Vergleich relativ unauffällig
# VehPower: "5" eher niedrig, "9" auffällig hoch, aber Merkmal im Vergleich relativ unauffällig
# VehAge: Ausschlag bei jüngeren Fahrzeugen, genauere Betrachtung notwendig
# DrivAge: Sehr deutlicher Ausschlag nach oben bei jungen Fahrern, alte Fahrer ebenfalls auffällig
# BonusMalus: Zwei deutliche Ausschläge nach oben, genauer Betrachtung notwengig
# VehBrand: Schwankungen, aber keine großen Asureißer
# VehGas: Unauffällig

# Genauere Betrachtung Veh Age
plot_sb(df_all_clean[df_all_clean["VehAge"].between(0,20)], "VehAge")

# Insgesamt je jünger desto höher der durchschnittliche Schadenaufwand

# Genauere Betrachtung BonusMalus
plot_sb(df_all_clean[df_all_clean["BonusMalus"].between(0,150)], "BonusMalus")



# Ausschlag nach oben bei BonusMalus "100", ansonsten unauffällig

### Hypothesen für Tarifvariablen - Einflusskategorien: unwesentlich, mittel, hoch
# Area: mittel
# Region: unwesentlich
# VehPower: mittel
# VehAge: hoch - aufgrund schlechter Datenlage ausgeschlossen
# DrivAge: hoch
# BonusMalus: hoch
# VehBrand: mittel - aufgrund schlechter Datenlage ausgeschlossen
# VehGas: unwesentlich - aufgrund schlechter Datenlage ausgeschlossen





#################################################
########### Modellierung ########################
#################################################

# Modellierung mit GLM, Gamma-verteilung für Schadenhöhen und Poisson-Verteilung für Schadenfrequenz, anschließed Multiplikation für Schadenbedarf
# Aufteilung der Daten in Trainings und Testdaten
# technisch umsetzbar bspw. mit scikit-learn
# Aufgrund mangelnder Erfahrung der Implementierung solcher Modell in  Python und der begrenzten Bearbeitungszeit leder nicht möglich.

# Um Zahlen in einer sinnvollen Größenordnung für die weiteren Bearbeitungschritte zu erhalten, wähle vereinfachte Berechnung des SB
# # Neuer Ansatz: Für jedes Merkmal einen Durchschnittswert der Schadenhöhe nach Ausprägung des Merkmals
# Für jede Ausprägung des Merkmal einen Faktor für Abweichung vom Durchschnittswert
# Ergebnis ist ein Faktor pro Tarifmerkmal und Ausprägung für Abweihung von der duchschnittlichen Schadenhöhe
# Im wesentlichen ein Zu- oder Abschlag vom Durchschnittsbeitrag für jede Merkmalausprägung
# Der Tarif entsteht dann durch Multiplikation aller Faktoren mit der durchschnittlichen Schadenhöhe

# Beschränkung auf wenige Tarifmerkmale aufgrund von geschätzter Wesentlichkeit und Datenlage
# Area, VehPower, DriveAge (kategorisiert), BonusMalus (kategorisiert)

# Datenkategorisierung

bins = [0, 22, 69, df_all_clean["DrivAge"].max()]
df_all_clean["DrivAge_binned"] = pd.cut(df_all_clean["DrivAge"], bins = bins, include_lowest = True)
df_all["DrivAge_binned"] = pd.cut(df_all["DrivAge"], bins = bins, include_lowest = True)


bins= [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, df_all_clean["BonusMalus"].max()]
df_all_clean["BonusMalus_binned"] = pd.cut(df_all_clean["BonusMalus"], bins = bins, include_lowest = True)
df_all["BonusMalus_binned"] = pd.cut(df_all["BonusMalus"], bins = bins, include_lowest = True)

## Teste Anzahl Tarifgruppen

def mult(a , b, c, d):
  return a * b * c * d

mult(
    len(df_all_clean["Area"].unique()),
    len(df_all_clean["VehPower"].unique()),
    len(df_all_clean["DrivAge_binned"].unique()),
    len(df_all_clean["BonusMalus_binned"].unique())
    )

# 1512 Tarifgruppen

# Durchschnittliche Schadenhöhe pro Police

df_all_clean["Schadenhöhe_mean"] = df_all_clean["Schadensumme"].div(df_all_clean["Schadenanzahl"]).fillna(0)

Tarifmerkmale = ["Area",
                 "VehPower",
                 "DrivAge_binned",
                 "BonusMalus_binned" 
                 ]


df_tarif_help = df_all_clean

for col in Tarifmerkmale:
    df_faktor = pd.DataFrame(df_tarif_help[[col, "Schadenhöhe_mean"]].groupby(col)
        .agg(
            Schadenhöhe_est = ("Schadenhöhe_mean", "mean"), 
            )
        .reset_index())
    df_faktor["Faktor_" + col] = df_faktor["Schadenhöhe_est"] / df_all_clean["Schadenhöhe_mean"].mean()
    df_faktor = df_faktor.drop(columns = "Schadenhöhe_est")
    df_tarif_help = df_tarif_help.merge(df_faktor, how= "left", on= col)

df_tarif_help["Tariffaktor"] = df_tarif_help.loc[:, df_tarif_help.columns.str.startswith('Faktor')].product(axis=1)
df_tarif_help["erw_Schadenhöhe"] = df_tarif_help["Tariffaktor"] * df_all_clean["Schadenhöhe_mean"].mean()

df_tarif = df_tarif_help[["Area", "VehPower", "DrivAge_binned", "BonusMalus_binned", "erw_Schadenhöhe"]].drop_duplicates().reset_index(drop = True)


## Es fehlen die Tarffaktoren für Kombinationen, die nicht in den freq Daten vorhanden sind

## Zu Schadenfrequenz: Selber Prozess wie oben, aber auf df_all, nachher left join df_tarif und df_tarif_freq



#################################################
########### Bewertung Schadenbedarf #############
#################################################


df_valid = df_all.merge(df_tarif, on = Tarifmerkmale)
df_valid["Schadenbedarf"] = df_valid["erw_Schadenhöhe"]

# Funktion, um Schadenbedarf und tatsächlich Schadenhöhe zu vergleichen

def plot_valid(df, merkmal):


    df = pd.DataFrame(df.groupby([merkmal])
            .agg(
                Schadenbedarf=("Schadenbedarf", "mean"), 
                Schadenhöhe_actual=("Schadensumme", "mean")
                )
            .reset_index())

    plt.plot(df[merkmal], df["Schadenbedarf"], color="tab:red", label = "Schadenbedarf")
    plt.plot(df[merkmal], df["Schadenhöhe_actual"], color="tab:blue", label = "tatsächliche Schadenhöhe")

    plt.xlabel(merkmal)
    plt.ylabel("Betrag")
    plt.legend()
    plt.title("Schadenbedarf und tatsächliche Schadenhöhe")
    plt.show()
    
    

    plt.show()

plot_valid(df_valid, "DrivAge") 
plot_valid(df_valid, "Area")
plot_valid(df_valid, "Region")
plot_valid(df_valid, "BonusMalus")


# Einfluss der Tarifmerkmale
#######
df_Einfluss = pd.DataFrame(df_tarif_help.loc[:, df_tarif_help.columns.str.startswith('Faktor')].drop_duplicates().describe())





















