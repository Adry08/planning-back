import pandas as pd
import re
from io import BytesIO

def excel_col_to_index(col):
    col = col.upper()
    idx = 0
    for c in col:
        idx = idx * 26 + (ord(c) - ord('A') + 1)
    return idx - 1


def formater_heure(valeur):
    if pd.isna(valeur):
        return None
    if isinstance(valeur, str):
        return valeur[:5] if ':' in valeur else None
    if isinstance(valeur, (int, float)):
        total_minutes = int(round(valeur * 24 * 60))
        h = total_minutes // 60
        m = total_minutes % 60
        return f"{h:02d}:{m:02d}"
    if hasattr(valeur, "strftime"):
        return valeur.strftime("%H:%M")
    return None


def extraire_semaine(df):
    for row in df.values:
        for cell in row:
            if isinstance(cell, str):
                match = re.search(r"(\d{4})-S(\d{2})", cell)
                if match:
                    return int(match.group(1)), int(match.group(2))
    return None, None


def configurer_colonnes():
    mapping = {
        "Lundi":     ['W','X','Y','Z','AA','AB'],
        "Mardi":     ['BE','BF','BG','BH','BI','BJ'],
        "Mercredi":  ['CM','CN','CO','CP','CQ','CR'],
        "Jeudi":     ['DU','DV','DW','DX','DY','DZ'],
        "Vendredi":  ['FC','FD','FE','FF','FG','FH'],
        "Samedi":    ['GK','GL','GM','GN','GO','GP'],
        "Dimanche":  ['HS','HT','HU','HV','HW','HX']
    }

    return {
        jour: [excel_col_to_index(c) for c in cols]
        for jour, cols in mapping.items()
    }


def extraire_planning(df, colonnes):
    agents = []

    for idx in range(6, len(df)):
        row = df.iloc[idx]

        if pd.isna(row.iloc[1]):
            continue

        agent = {
            "ccms": str(row.iloc[1]).replace(".0", "").strip(),
            "nom": str(row.iloc[8]).strip() if not pd.isna(row.iloc[8]) else "",
            "n1": str(row.iloc[9]).strip() if not pd.isna(row.iloc[9]) else "",
            "n2": str(row.iloc[10]).strip() if not pd.isna(row.iloc[10]) else "",
            "commentaire": str(row.iloc[17]).strip() if not pd.isna(row.iloc[17]) else "",
            "planning": {}
        }

        for jour, cols in colonnes.items():
            heures = [
                formater_heure(row.iloc[c])
                for c in cols if c < len(row)
            ]
            heures = [h for h in heures if h]

            agent["planning"][jour] = {
                "debut": heures[0] if heures else None,
                "fin": heures[-1] if heures else None
            }

        agents.append(agent)

    return agents


def excel_to_json(file_bytes: bytes) -> dict:
    df = pd.read_excel(BytesIO(file_bytes), header=None)

    annee, semaine = extraire_semaine(df)
    colonnes = configurer_colonnes()
    agents = extraire_planning(df, colonnes)

    return {
        "annee": annee,
        "semaine": semaine,
        "agents": agents
    }