import pandas as pd
import re
from io import BytesIO
import hashlib

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
    if hasattr(valeur, 'strftime'):
        return valeur.strftime('%H:%M')
    return None

def extraire_semaine(df):
    for row in df.values:
        for cell in row:
            if isinstance(cell, str):
                match = re.search(r'(\d{4})-S(\d{2})', cell)
                if match:
                    return int(match.group(1)), int(match.group(2))
    return None, None

def configurer_colonnes():
    colonnes_excel = {
        'Lundi': ['W','X','Y','Z','AA','AB'],
        'Mardi': ['BE','BF','BG','BH','BI','BJ'],
        'Mercredi': ['CM','CN','CO','CP','CQ','CR'],
        'Jeudi': ['DU','DV','DW','DX','DY','DZ'],
        'Vendredi': ['FC','FD','FE','FF','FG','FH'],
        'Samedi': ['GK','GL','GM','GN','GO','GP'],
        'Dimanche': ['HS','HT','HU','HV','HW','HX']
    }
    return {jour:[excel_col_to_index(c) for c in lettres] for jour, lettres in colonnes_excel.items()}

def hash_ccms(ccms: str) -> str:
    return hashlib.sha256(ccms.encode()).hexdigest()

def extraire_planning_tous(df, colonnes):
    agents=[]
    for idx in range(6, len(df)):
        row=df.iloc[idx]
        ccms_val=row.iloc[1]
        if pd.isna(ccms_val):
            continue
        ccms=str(ccms_val).replace('.0','').strip()
        planning_agent={}
        for jour, cols in colonnes.items():
            heures=[]
            for col in cols:
                if col < len(row):
                    h=formater_heure(row.iloc[col])
                    if h: heures.append(h)
            planning_agent[jour] = {"debut": heures[0] if heures else None, "fin": heures[-1] if heures else None}
        agents.append({hash_ccms(ccms): planning_agent})
    return agents

def excel_to_json(file_bytes: bytes):
    df=pd.read_excel(BytesIO(file_bytes), header=None)
    annee, semaine = extraire_semaine(df)
    colonnes = configurer_colonnes()
    agents = extraire_planning_tous(df, colonnes)
    return {"annee": annee, "semaine": semaine, "agents": agents}