# -*- coding: utf-8 -*-
"""Extrai indicadores das bases tratadas e gera data.js para a pagina interativa.
Agenda DEL - prototipo Tabuleiro do Norte."""
import csv, json, os

BASE = os.path.join(os.path.dirname(__file__), "..")
MUNI = {"nome": "Tabuleiro do Norte", "pasta": "tabuleiro_do_norte", "ibge": "2313104"}

def caminho(muni, nome):
    return os.path.join(BASE, muni["pasta"], "03_bases_tratadas", nome + ".csv")

def ler(muni, nome):
    with open(caminho(muni, nome), encoding="utf-8") as f:
        return list(csv.DictReader(f))

def num(x):
    if x is None: return None
    x = x.strip()
    if x == "": return None
    try:
        return float(x)
    except ValueError:
        return None

def extrair(muni):
    d = {}

    # 1. Populacao
    pop = ler(muni, "demografia_populacao")
    pop = sorted([(int(r["ano"]), num(r["populacao"])) for r in pop if num(r["populacao"])], key=lambda x: x[0])
    d["populacao"] = {"anos": [a for a, _ in pop], "valores": [v for _, v in pop]}

    # 2. Cor/raca (2022) - exclui Total
    cr = ler(muni, "censo_2022_cor_raca_sidra_9605")
    cats, vals = [], []
    for r in cr:
        if r["cor_ou_raca"] != "Total" and num(r["valor"]):
            cats.append(r["cor_ou_raca"]); vals.append(num(r["valor"]))
    d["cor_raca"] = {"categorias": cats, "valores": vals, "ano": 2022}

    # 3/4. PIB e VAB setorial
    pib = ler(muni, "economia_pib_municipal")
    pib = sorted(pib, key=lambda r: int(r["ano"]))
    d["pib"] = {
        "anos": [int(r["ano"]) for r in pib],
        "valores": [num(r["pib"]) for r in pib],
    }
    # PIB per capita = pib / populacao do ano
    popmap = {a: v for a, v in pop}
    d["pib_per_capita"] = {
        "anos": [int(r["ano"]) for r in pib if popmap.get(int(r["ano"]))],
        "valores": [round(num(r["pib"]) / popmap[int(r["ano"])], 2) for r in pib if popmap.get(int(r["ano"]))],
    }
    vab = [r for r in pib if num(r["va_agropecuaria"])]
    d["vab"] = {
        "anos": [int(r["ano"]) for r in vab],
        "agropecuaria": [num(r["va_agropecuaria"]) for r in vab],
        "industria": [num(r["va_industria"]) for r in vab],
        "servicos": [num(r["va_servicos"]) for r in vab],
        "adm_publica": [num(r["va_adespss"]) for r in vab],
    }

    # 5. Empregos formais
    emp = ler(muni, "rais_empregos")
    emp = sorted([(int(r["ano"]), num(r["vinculos_formais"])) for r in emp], key=lambda x: x[0])
    d["empregos"] = {"anos": [a for a, _ in emp], "valores": [v for _, v in emp]}

    # 6. Empregos por CNAE (ano mais recente, top 10) - recodifica via 'classe'
    dirc = ler(muni, "diretorio_cnae_2")
    classe2desc = {}
    for r in dirc:
        c = r["classe"].strip()
        if c and c not in classe2desc:
            classe2desc[c] = r["descricao_classe"]
    ecnae = ler(muni, "rais_empregos_por_cnae")
    ano_rec = max(int(r["ano"]) for r in ecnae)
    agg = {}
    for r in ecnae:
        if int(r["ano"]) == ano_rec:
            cod = r["cnae_2"].strip()
            desc = classe2desc.get(cod, "CNAE " + cod)
            agg[desc] = agg.get(desc, 0) + (num(r["vinculos_formais"]) or 0)
    top = sorted(agg.items(), key=lambda x: -x[1])[:10]
    d["empregos_cnae"] = {"ano": ano_rec, "setores": [k for k, _ in top], "valores": [v for _, v in top]}

    # 7/8. IDEB municipio vs Ceara (fundamental) por etapa, com prioridade de rede
    def ideb_serie(rows, prioridade):
        # guarda todas as redes e depois escolhe pela prioridade
        tmp = {}
        for r in rows:
            if r["ensino"] != "fundamental": continue
            v = num(r["ideb"])
            if v is None: continue
            tmp.setdefault((r["anos_escolares"], int(r["ano"])), {})[r["rede"]] = v
        out = {}
        for (etapa, ano), redes in tmp.items():
            for rede in prioridade:
                if rede in redes:
                    out.setdefault(etapa, {})[ano] = redes[rede]
                    break
        return out
    im = ideb_serie(ler(muni, "educacao_ideb"), ["publica", "municipal", "estadual"])
    ic = ideb_serie(ler(muni, "educacao_ideb_ceara"), ["publica", "total", "estadual"])
    etapas = {}
    for et in sorted(set(im) | set(ic)):
        anos = sorted(set(im.get(et, {})) | set(ic.get(et, {})))
        etapas[et] = {
            "anos": anos,
            "municipio": [im.get(et, {}).get(a) for a in anos],
            "ceara": [ic.get(et, {}).get(a) for a in anos],
            "diferenca": [round(im[et][a] - ic[et][a], 2) if im.get(et, {}).get(a) is not None and ic.get(et, {}).get(a) is not None else None for a in anos],
        }
    d["ideb"] = etapas

    # 9. Atendimento escolar (frequencia bruta) por faixa etaria agregada, Total sexo/cor
    at = ler(muni, "educacao_atendimento_escolar_4_14_sidra_10056_raw")
    bandas = ["0 a 3 anos", "4 a 5 anos", "6 a 14 anos", "15 a 17 anos", "18 a 24 anos"]
    amap = {}
    for r in at:
        if r["sexo"] == "Total" and r["cor_ou_raca"] == "Total":
            fx = r["grupo_de_idade"]
            if fx in bandas and num(r["valor"]) is not None:
                amap[fx] = num(r["valor"])
    d["atendimento"] = {"faixas": [b for b in bandas if b in amap],
                         "valores": [amap[b] for b in bandas if b in amap], "ano": 2022}

    return d

dados = {"municipios": {MUNI["nome"]: extrair(MUNI)}, "meta": {"uf": "Ceará", "fonte": "IBGE/SIDRA, INEP, RAIS/MTE — Agenda DEL"}}
out = os.path.join(os.path.dirname(__file__), "data.js")
with open(out, "w", encoding="utf-8") as f:
    f.write("window.DADOS = " + json.dumps(dados, ensure_ascii=False, indent=1) + ";")
print("OK ->", out)
print(json.dumps(dados, ensure_ascii=False, indent=1)[:1500])
