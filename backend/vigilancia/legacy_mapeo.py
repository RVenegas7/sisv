"""Mapeo curado del catálogo ENO legacy (sismai.INFORME_EPI) al catálogo nuevo de
Eventos ENO (vigilancia.EventoENO), y de los grupos de edad legacy (sismai.EDADES)
a la matriz de 13 grupos etarios + edad ignorada de FilaConsolidado.

El catálogo legacy usa una numeración histórica distinta (desgloses por edad en el
propio renglón) que no coincide con el EventoENO actual (numeración EPI-12/EPI-14
con CIE-11). Las equivalencias de abajo se curaron manualmente nombre a nombre el
23/09/2026; los eventos legacy sin equivalente (p. ej. SÍNDROME VIRAL, EMPONZOÑAMIENTO
OFÍDICO, LEPRA) se excluyen de la importación y quedan reportados como «no importados».

Claves: ``LEGACY_ENFERMEDAD_EVENTO`` usa el ID legacy (columna ENFERMEDAD de
RENGLONTELE/RENGLON_EPI15 = sismai.INFORME_EPI.ID) y como valor el
``codigo_evento`` del EventoENO.
"""

import contextlib
import re

__all__ = [
    "LEGACY_ENFERMEDAD_EVENTO",
    "LEGACY_ENFERMEDAD_NOMBRE",
    "GRUPO_EDAD_LEGACY",
    "por_evento_id",
]

# ---------------------------------------------------------------------------
# Enfermedades legacy (INFORME_EPI.ID) → codigo_evento de EventoENO
# ---------------------------------------------------------------------------
LEGACY_ENFERMEDAD_EVENTO = {
    67910: "ENO_colera",
    67903: "ENO_amibiasis",
    67918: "ENO_diarreas",
    67908: "ENO_diarreas",
    67909: "ENO_diarreas",
    67919: "ENO_eta_n_de_brotes",
    67914: "ENO_hepatitis_aguda_tipo_a",
    67905: "ENO_tuberculosis",
    67911: "ENO_influenza_enfermedad_tipo_influenza",
    67924: "ENO_infeccion_gonococcica",
    68037: "ENO_sifilis",
    67925: "ENO_infeccion_asintomatica_vih",
    67923: "ENO_enfermedad_vih_sida",
    67916: "ENO_tosferina",
    67922: "ENO_parotiditis_infecciosa",
    67936: "ENO_tetanos",
    67931: "ENO_difteria",
    67935: "ENO_rubeola",
    68047: "ENO_dengue_sin_signos_de_alarma",
    68048: "ENO_dengue_con_signos_de_alarma",
    67927: "ENO_dengue_grave",
    68049: "ENO_leishmaniasis_visceral",
    68050: "ENO_leishmaniasis_cutanea",
    68052: "ENO_leishmaniasis_no_especifica",
    67939: "ENO_leptospirosis",
    67946: "ENO_meningitis_meningococcica",
    67951: "ENO_meningitis_viral",
    67948: "ENO_varicela",
    67947: "ENO_hepatitis_aguda_tipo_b",
    67943: "ENO_hepatitis_viral_agudas",
    67929: "ENO_tumores_neoplasias",
    67897: "ENO_diabetes_mellitus",
    67974: "ENO_paralisis_flacida_aguda",
    67977: "ENO_hipertension_arterial",
    67991: "ENO_hipertension_arterial",
    67986: "ENO_hipertension_arterial",
    67985: "ENO_enfermedad_cerebrovascular",
    67971: "ENO_faringitis_aguda",
    67973: "ENO_faringitis_aguda",
    67984: "ENO_amigdalitis_aguda",
    67987: "ENO_rinofaringitis_aguda",
    67988: "ENO_rinofaringitis_aguda",
    67989: "ENO_neumonias",
    67997: "ENO_neumonias",
    68000: "ENO_neumonias",
    68001: "ENO_bronquiolitis_aguda_2_anos",
    67992: "ENO_bronquitis_aguda",
    67979: "ENO_asma_bronquial",
    67975: "ENO_asma_bronquial",
    68030: "ENO_leucorrea_no_especificada",
    68003: "ENO_fiebre",
    67874: "ENO_intoxicacion_por_plaguicidas",
    67881: "ENO_accid_transport_terrestre",
    67888: "ENO_mordedura_sospechosa_de_rabia",
    67893: "ENO_sifilis_congenita",
    68040: "ENO_hepatitis_aguda_tipo_c",
    68041: "ENO_meningitis_bacteriana",
    68042: "ENO_enfermedad_meningococcica",
    68043: "ENO_hepatitis_viral_no_especificas",
    68045: "ENO_cardiopatia_isquemica",
    3157284: "ENO_malaria_falciparum",
    3157285: "ENO_malaria_vivax",
    3157286: "ENO_malaria_malariae",
    1135234051: "ENO_sinusitis_aguda",
    1135234063: "ENO_laringitis_y_traqueitis_aguda",
    1135234075: "ENO_infecciones_agud_vias_respirat_superi_si",
    1135234087: "ENO_infeccion_agud_no_especific_vias_respira",
    1135234100: "ENO_enfermedad_de_chagas_cronica",
    1135234130: "ENO_cardiopatia_isquemica",
    1140458498: "ENO_efectos_adversos_de_medicamentos",
    1140458529: "ENO_efectos_adversos_de_vacunas",
    1126697987: "ENO_malaria_mixta",
    3411464456: "ENO_casos_asociados_a_brotes_de_eta",
    3438429455: "ENO_laringitis_obstructiva_y_epiglotitis",
    1126717444: "ENO_infeccion_respiratoria_aguda_grave",
    1126717712: "ENO_sindrome_respiratorio_agudo_severo_sars",
    1126717758: "ENO_enfermedad_de_chagas_aguda",
    1126717787: "ENO_sindrome_de_rubeola_congenita",
    1126717832: "ENO_total_pacientes_hospitalizados_por_todas",
    1126732289: "ENO_infeccion_por_virus_papiloma_humano",
    68060: "ENO_chikungunya",
    68062: "ENO_zika",
    68063: "ENO_sindrome_de_guillain_barre",
    68064: "ENO_paralisis_flacida_aguda",
    68071: "ENO_condiloma_acuminado",
    68072: "ENO_tricomoniasis",
    68073: "ENO_candidiasis_genital",
    68091: "ENO_trast_mentales_y_del_comport",
    68102: "ENO_cardiopatia_isquemica",
    68104: "ENO_enfermedad_pulmonar_obstructiva_cronica",
    68105: "ENO_enfermedad_renal",
}

# Nombres legacy por si el reporte los necesita (id → nombre).
LEGACY_ENFERMEDAD_NOMBRE = {
    67910: "CÓLERA",
    67903: "AMIBIASIS",
    67918: "DIARREAS MENORES DE 1 AÑO",
    67908: "DIARREAS DE 1 A 4 AÑOS",
    67909: "DIARREAS DE 5 AÑOS Y MAS",
    67919: "ETA Nº DE BROTES",
    67914: "HEPATITIS AGUDA TIPO A",
    67905: "TUBERCULOSIS",
    67911: "INFLUENZA / ENFERMEDAD TIPO INFLUENZA",
    67924: "INFECCION GONOCOCICA",
    68037: "SIFILIS",
    67925: "INFECCIÓN ASINTOMÁTICA VIH",
    67923: "ENFERMEDAD VIH/SIDA",
    67916: "TOSFERINA",
    67922: "PAROTIDITIS INFECCIOSA",
    67936: "OTROS TÉTANOS",
    67931: "DIFTERIA",
    67935: "RUBÉOLA",
    68047: "DENGUE SIN SIGNOS DE ALARMA",
    68048: "DENGUE CON SIGNOS DE ALARMA",
    67927: "DENGUE GRAVE",
    68049: "LEISHMANIASIS VISCERAL",
    68050: "LEISHMANIASIS CUTÁNEA",
    68052: "LEISHMANIASIS NO ESPECÍFICA",
    67939: "LEPTOSPIROSIS",
    67946: "MENINGITIS MENINGOCÓCCICA",
    67951: "MENINGITIS VIRAL",
    67948: "VARICELA",
    67947: "HEPATITIS AGUDA TIPO B",
    67943: "HEPATITIS OTRAS AGUDAS",
    67929: "NEOPLASIAS",
    67897: "DIABETES MELLITUS TIPO II",
    67974: "PARÁLISIS FLÁCIDA MENOR DE 15 AÑOS",
    67977: "HIPERTENSION ARTERIAL MENOR DE 15 AÑOS",
    67991: "HIPERTENSION ARTERIAL 15-44 AÑOS",
    67986: "HIPERTENSION ARTERIAL 45 AÑOS Y MAS",
    67985: "ENFERMEDADES CEREBROVASCULARES",
    67971: "FARINGITIS AGUDA MENOR DE 5 AÑOS",
    67973: "FARINGITIS AGUDA ≥ 5 AÑOS",
    67984: "AMIGDALITIS AGUDA",
    67987: "RINOFARINGITIS AGUDA MENOR DE 5 AÑOS",
    67988: "RINOFARINGITIS AGUDA ≥ 5 AÑOS",
    67989: "NEUMONÍA MENOR DE 1 AÑO",
    67997: "NEUMONÍA 1-4 AÑOS",
    68000: "NEUMONÍA 5 AÑOS Y MAS",
    68001: "BRONQUIOLITIS AGUDA MENOR DE 2 AÑOS",
    67992: "BRONQUITIS AGUDA",
    67979: "ASMA MENOR DE 10 AÑOS",
    67975: "ASMA 10 AÑOS Y MÁS",
    68030: "LEUCORREA NO ESPECIFICA",
    68003: "FIEBRE",
    67874: "INTOXICACIÓN POR PLAGUICIDAS",
    67881: "ACCIDENTES TRANSPORTE TERRESTRE",
    67888: "MORDEDURA SOSPECHOSA DE RABIA",
    67893: "SIFILIS CONGÉNITA",
    68040: "HEPATITIS AGUDA TIPO C",
    68041: "MENINGITIS BACTERIANA",
    68042: "ENFERMEDAD MENINGOCÓCCICA",
    68043: "HEPATITIS NO ESPECIFICAS",
    68045: "INFARTO AGUDO DEL MIOCARDIO < 45 AÑOS",
    3157284: "MALARIA FALCIPARUM",
    3157285: "MALARIA VIVAX",
    3157286: "MALARIA MALARIAE",
    1135234051: "SINUSITIS AGUDA",
    1135234063: "LARINGITIS Y TRAQUEITIS AGUDA",
    1135234075: "IRA VÍAS RESP. SUP. Y SITIOS MÚLTIPLES",
    1135234087: "IRA NO ESPECIF. VÍAS RESP. INFERIORES",
    1135234100: "ENFERMEDAD DE CHAGAS CRÓNICA",
    1135234130: "INFARTO AGUDO DEL MIOCARDIO ≥ 45 AÑOS",
    1140458498: "EFECTOS ADVERSOS DE MEDICAMENTOS",
    1140458529: "EFECTOS ADVERSOS DE VACUNAS",
    1126697987: "MALARIA MIXTA",
    3411464456: "CASOS ASOCIADOS A BROTES DE ETA",
    3438429455: "LARINGITIS OBSTRUCTIVA AGUDA Y EPIGLOTITIS",
    1126717444: "INFECCIÓN RESPIRATORIA AGUDA GRAVE",
    1126717712: "SINDROME RESPIRATORIO AGUDO SEVERO SARS",
    1126717758: "ENFERMEDAD DE CHAGAS AGUDA",
    1126717787: "SÍNDROME DE RUBÉOLA CONGÉNITA",
    1126717832: "TOTAL DE PACIENTES HOSPITALIZADOS POR TODAS CAUSAS",
    1126732289: "INFECCIÓN POR VIRUS PAPILOMA HUMANO",
    68060: "CHIKUNGUNYA",
    68062: "ZIKA",
    68063: "SÍNDROME DE GUILLÁIN BARRÉ",
    68064: "PARÁLISIS FLÁCIDA MAYOR DE 15 AÑOS",
    68071: "CONDILOMA ACUMINADO",
    68072: "TRICOMONIASIS",
    68073: "CANDIDIASIS GENITAL",
    68091: "TRAST MENTAL NO ESPECIFICADO",
    68102: "CARDIOPATÍA ISQUÉMICA",
    68104: "ENFERMEDAD PULMONAR OBSTRUCTIVA CRÓNICA",
    68105: "ENFERMEDAD RENAL",
}

# ---------------------------------------------------------------------------
# Grupos de edad legacy (sismai.EDADES.ID) → columna de FilaConsolidado
# ---------------------------------------------------------------------------
# La matriz oficial de 13 grupos (HCATEGORIA=1) + desbordes históricos:
# - "Menor de 7 días" y "7 a 28 días" son subgrupos del <1 año.
# - "Menor de 2 años" (0-2) es un agregado que se suma al grupo 1-4 (rango 1-4).
# - "MENORES DE 25 AÑOS" es demasiado grueso → edad ignorada (regla oficial:
#   la edad ignorada se anota en la columna Hombres).
GRUPO_EDAD_LEGACY = {
    68071: "menor_1",     # MENORES DE 1 AÑO
    68080: "menor_1",     # Menor de 7 Días
    68081: "menor_1",     # De 7 a 28 Días
    68072: "de_1_4",      # 1 - 4 AÑOS
    3409211: "de_1_4",    # Menor de 2 años
    3411427332: "de_5_6",   # 5 - 6 AÑOS
    3411427334: "de_7_9",   # 7 - 9 AÑOS
    3411427336: "de_10_11", # 10 - 11 AÑOS
    3411427338: "de_12_14", # 12 - 14 AÑOS
    3411427340: "de_15_19", # 15 - 19 AÑOS
    3411427342: "de_20_24", # 20 - 24 AÑOS
    68076: "de_25_44",   # 25 - 44 AÑOS
    3411427344: "de_45_59", # 45 - 59 AÑOS
    3411427346: "de_60_64", # 60 - 64 AÑOS
    68078: "de_65",      # 65 Y MAS AÑOS
    68079: "edad_ignorada",  # EDAD IGNORADA
    68051: "edad_ignorada",  # MENORES DE 25 AÑOS (agregado grueso)
}

for _id, _cod in LEGACY_ENFERMEDAD_EVENTO.items():
    _cod = str(_cod)
_slug = re.compile(r"[^A-Za-z0-9_]")


def por_evento_id(ids_evento_por_codigo):
    """Convierte el mapeo a {id_legacy: id_EventoENO} resolviendo codigo_evento.

    ``ids_evento_por_codigo`` es un dict {codigo_evento: pk}. Las claves que no
    existan en el catálogo actual se omiten (None).
    """
    salida = {}
    with contextlib.suppress(Exception):
        for legacy_id, codigo in LEGACY_ENFERMEDAD_EVENTO.items():
            pk = ids_evento_por_codigo.get(codigo)
            if pk is not None:
                salida[int(legacy_id)] = int(pk)
    return salida