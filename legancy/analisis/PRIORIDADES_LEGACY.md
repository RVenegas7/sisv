# Inventario priorizado del sistema legacy SISMAI

**Generado por** `manage.py mapear_legacy`. Modelo de referencia: `backend/legacy/models_legacy.py` (un modelo `managed=False` por tabla/vista, solo lectura).
Esquemas migrados: `sismai`, `inbdlar1`, `legacy`, `historico` (origen: Oracle 10g).

## Criterios de prioridad

- **P1 — Dominio/negocio:** catálogos de centro, usuarios, jerarquía, territorio, CIE legacy y  las fuentes de vigilancia cuya integración a `registros`/`vigilancia` está por decidir.
- **P2 — Operativo/registro:** tablas de hechos (nacimientos/defunciones), espejos centrales/efectivos  (`T_*`) y logs de actividad.
- **P3 — Catálogos de soporte / configuración / colas:** resto.

## Resumen

| Tier | Tablas |
|---|---|
| P1 | 32 |
| P2 | 185 |
| P3 | 213 |

## Inventario (filas aproximadas, ordenado por prioridad y tamaño)

| Tier | Esquema | Tabla | Tipo | Filas (aprox) | Col | PK | FKs | Nota |
|---|---|---|---|---|---|---|---|---|
| P1 | `sismai` | `RENGLONTELE` | tabla | 2.663.432 | 12 | 0 | 0 | Consolidado semanal RENGLONTELE (morbilidad, EPI-12) |
| P1 | `sismai` | `RENGLON_EPI15` | tabla | 632.665 | 8 | 0 | 0 | Consolidado EPI-15 |
| P1 | `sismai` | `RENGLON_DSP04` | tabla | 323.004 | 4 | 0 | 0 | Consolidado DSP-04 |
| P1 | `sismai` | `PERSONALSALUD` | tabla | 106.979 | 27 | 0 | 0 | Personal de salud |
| P1 | `sismai` | `ORG_GEOGRAFICA` | tabla | 58.939 | 40 | 0 | 0 | División político territorial (Estado-Municipio-Parroquia-Comunidad) |
| P1 | `sismai` | `ESTABLECIMIENTO` | tabla | 21.148 | 28 | 0 | 0 | Catálogo maestro de establecimientos (a integrar a seguridad.Organizacion) |
| P1 | `sismai` | `CIE10` | tabla | 16.627 | 21 | 0 | 0 | Catálogo CIE-10 legacy (códigos con punto) |
| P1 | `historico` | `EVENTOS` | tabla | 15.281 | 6 | 0 | 0 | Log de eventos procesados (STATUS != 0) |
| P1 | `sismai` | `VALIDARCIE10` | tabla | 14.304 | 27 | 0 | 0 | Validación CIE-10 legacy (sin punto) |
| P1 | `sismai` | `M_VIOLENTA` | tabla | 12.409 | 9 | 0 | 0 | Violencia (accidente/homicidio/suicidio) ligada a CERTIFICADO |
| P1 | `sismai` | `CASOS_MMI` | tabla | 10.742 | 17 | 0 | 0 | Fichas de vigilancia individuales materno-infantil (integración pendiente) |
| P1 | `sismai` | `RENGLON_CASOSMI` | tabla | 9.993 | 14 | 0 | 0 | Causas de CASOS_MMI con CIE-10 |
| P1 | `sismai` | `PERSONALMEDICO` | tabla | 8.607 | 13 | 0 | 0 | Personal médico firmante |
| P1 | `sismai` | `USUARIOS` | tabla | 844 | 21 | 0 | 0 | Usuarios SISMAI (LOGIN, ESTATUS, perfil, jerarquía) |
| P1 | `inbdlar1` | `T_USUARIOS` | tabla | 670 | 21 | 0 | 0 | Usuarios efectivos región Lara |
| P1 | `sismai` | `CODIF_CIE10` | tabla | 498 | 3 | 0 | 0 | Mapeo CODIFICADOR - CIE-10 |
| P1 | `sismai` | `INFORME_EPI` | tabla | 298 | 10 | 0 | 0 | Informe EPI agregado (CASOSP/S/X) - fuente de ConsolidadoSemanal |
| P1 | `sismai` | `EDADES` | tabla | 162 | 15 | 0 | 0 | Catálogo de edades |
| P1 | `sismai` | `DEPENDENCIA_ADM` | tabla | 104 | 9 | 0 | 0 | Dependencia administrativa (campo HDEPENDENCIA_ADM) |
| P1 | `inbdlar1` | `T_ESTABLE` | tabla | -1 | 21 | 0 | 0 | Establecimientos efectivos región Lara |
| P1 | `inbdlar1` | `T_ORGGEOG` | tabla | -1 | 40 | 0 | 0 | Geografía efectiva región Lara |
| P1 | `legacy` | `T_ESTABLE` | tabla | -1 | 21 | 0 | 0 | Establecimientos (lista nivel central) |
| P1 | `legacy` | `T_ORGGEOG` | tabla | -1 | 40 | 0 | 0 | Organización geográfica (nivel central) |
| P1 | `legacy` | `T_PERSMEDI` | tabla | -1 | 13 | 0 | 0 | Personal médico (nivel central) |
| P1 | `legacy` | `T_USUARIOS` | tabla | -1 | 21 | 0 | 0 | Usuarios (lista nivel central) |
| P1 | `sismai` | `CAMBIOS` | tabla | -1 | 6 | 0 | 0 | Bitácora de cambios (TABLA/EVENTO/FECHA/ID/STATUS/AMS) |
| P1 | `sismai` | `CATEGORIA_CIE10` | tabla | -1 | 2 | 0 | 0 | Niveles de categoría CIE-10 (Cap/Grupo/Cat/Subcat) |
| P1 | `sismai` | `ESTABLECIMIENTO_MAESTRA` | tabla | -1 | 14 | 0 | 0 | Maestra de establecimientos |
| P1 | `sismai` | `LOCALIDADESTAB` | tabla | -1 | 5 | 0 | 0 | Vinculación establecimiento - localidad |
| P1 | `sismai` | `NIVEL` | tabla | -1 | 5 | 0 | 0 | Nivel de atención (campo HNIVEL) |
| P1 | `sismai` | `SEXO` | tabla | -1 | 5 | 0 | 0 | Catálogo de sexo (legacy: 1=Femenino, 2=Masculino) |
| P1 | `sismai` | `USUARIO_ESTAB` | tabla | -1 | 3 | 0 | 0 | Vinculación usuario - establecimiento |
| P2 | `sismai` | `NAC_MADRE` | tabla | 438.942 | 60 | 0 | 0 |  |
| P2 | `sismai` | `CERTNACIMIENTO` | tabla | 438.910 | 35 | 0 | 0 |  |
| P2 | `sismai` | `NAC_RNACIDO` | tabla | 438.646 | 21 | 0 | 0 |  |
| P2 | `sismai` | `CAUSA_MMEDICO` | tabla | 332.337 | 10 | 0 | 0 |  |
| P2 | `sismai` | `CAUSA_M` | tabla | 211.258 | 8 | 0 | 0 |  |
| P2 | `sismai` | `CERTIFICADO` | tabla | 173.391 | 98 | 0 | 0 |  |
| P2 | `sismai` | `DOCUMENTO` | tabla | 138.946 | 12 | 0 | 0 |  |
| P2 | `sismai` | `RENGLON_RESUMEN` | tabla | 56.929 | 7 | 0 | 0 |  |
| P2 | `sismai` | `RENGLON_SITUACION` | tabla | 30.699 | 16 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_EVENTOS` | tabla | 18.680 | 6 | 0 | 0 |  |
| P2 | `sismai` | `M_MADRE` | tabla | 13.417 | 22 | 0 | 0 |  |
| P2 | `sismai` | `M_FETAL` | tabla | 12.205 | 13 | 0 | 0 |  |
| P2 | `legacy` | `T_EVENTOS` | tabla | 7.802 | 6 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_RENGRES` | tabla | 7.555 | 7 | 0 | 0 |  |
| P2 | `legacy` | `T_AUDITORIA` | tabla | 7.403 | 10 | 0 | 0 |  |
| P2 | `sismai` | `CAUSA_MORBOSAS` | tabla | 7.401 | 5 | 0 | 0 |  |
| P2 | `sismai` | `ACTIVIDAD` | tabla | 6.542 | 11 | 0 | 0 |  |
| P2 | `sismai` | `CAUSA_M_REPA` | tabla | 6.455 | 8 | 0 | 0 |  |
| P2 | `sismai` | `NAC_ANULADOS` | tabla | 6.407 | 10 | 0 | 0 |  |
| P2 | `legacy` | `T_RENGTELE` | tabla | 5.007 | 12 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_AUDITORIA` | tabla | 4.085 | 10 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_RENGSIT` | tabla | 2.654 | 16 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_RENGTELE` | tabla | 2.592 | 12 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_RESUMEN` | tabla | 1.081 | 9 | 0 | 0 |  |
| P2 | `sismai` | `RENGLON_CASOSMM` | tabla | 749 | 18 | 0 | 0 |  |
| P2 | `legacy` | `T_CAUMMEDI` | tabla | 544 | 10 | 0 | 0 |  |
| P2 | `legacy` | `T_RENEPI15` | tabla | 521 | 8 | 0 | 0 |  |
| P2 | `legacy` | `T_DOCUMENT` | tabla | 364 | 12 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_CERTNACI` | tabla | 321 | 30 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_MADRNACI` | tabla | 321 | 60 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_RNACNACI` | tabla | 321 | 21 | 0 | 0 |  |
| P2 | `legacy` | `T_MADRNACI` | tabla | 241 | 60 | 0 | 0 |  |
| P2 | `legacy` | `T_RNACNACI` | tabla | 241 | 21 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_MORTCAUS` | tabla | 195 | 8 | 0 | 0 |  |
| P2 | `legacy` | `T_CERTMORT` | tabla | 185 | 98 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_CERTMORT` | tabla | 120 | 96 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_DOCUMENT` | tabla | 96 | 12 | 0 | 0 |  |
| P2 | `legacy` | `T_MORTANUL` | tabla | 64 | 10 | 0 | 0 |  |
| P2 | `legacy` | `T_RENGRES` | tabla | 63 | 7 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_MBASED` | tabla | 56 | 8 | 0 | 0 |  |
| P2 | `historico` | `EVENTO2` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `historico` | `EVENTOS_DBLINK` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_ACCILABO` | tabla | -1 | 24 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_ACCTRANS` | tabla | -1 | 11 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_ALABCARD` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_ANALABOR` | tabla | -1 | 9 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_ANTEFACT` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_BIOPSEG` | tabla | -1 | 2 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_BIOPSIAT` | tabla | -1 | 56 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_CASOSMM` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_CASOSMMI` | tabla | -1 | 17 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_CAUMMEDI` | tabla | -1 | 10 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_COMAGUDA` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_COMCRONI` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_COMDISCA` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_COMPCARD` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_COMPLICA` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_COMQUIR` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_COMSEGIM` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_DIAGASOC` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_DOCUDENG` | tabla | -1 | 17 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_DOCUSOSP` | tabla | -1 | 7 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_FDOLORTO` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_FICHAACC` | tabla | -1 | 12 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_FICHASEP` | tabla | -1 | 14 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_HECHOSVI` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_INTQUIR` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_LUGARVIS` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_MCAUMORB` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_MCAUSMRE` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_MHOJAREP` | tabla | -1 | 17 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_MORTANUL` | tabla | -1 | 10 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_MORTFETA` | tabla | -1 | 13 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_MORTMADR` | tabla | -1 | 22 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_MORTVIOL` | tabla | -1 | 9 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_MRESPA` | tabla | -1 | 11 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_NOTDSP04` | tabla | -1 | 4 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_OTROTRAT` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_PACCONDE` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_PACIEND` | tabla | -1 | 18 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_PACIENFE` | tabla | -1 | 30 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_PACIENTT` | tabla | -1 | 15 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_PACIMISI` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_PERQUIR` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_PERSMEDI` | tabla | -1 | 13 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_POBESTA` | tabla | -1 | 7 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_PRODIABE` | tabla | -1 | 9 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_PROGCARD` | tabla | -1 | 10 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_PROGMCHE` | tabla | -1 | 26 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_PROGTUBE` | tabla | -1 | 24 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_PROTTROM` | tabla | -1 | 30 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_PRVIHSID` | tabla | -1 | 17 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_RCASOSMI` | tabla | -1 | 14 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_RCASOSMM` | tabla | -1 | 14 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_REGCIRU` | tabla | -1 | 19 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_REGVACU` | tabla | -1 | 13 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_RENDSP04` | tabla | -1 | 4 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_RENEPI15` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_RNACANUL` | tabla | -1 | 10 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_SEGDIABE` | tabla | -1 | 35 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_SEGEVOLP` | tabla | -1 | 16 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_SEGUCARD` | tabla | -1 | 9 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_SIGNSINT` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_SIGSINSE` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_SITUESPE` | tabla | -1 | 10 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_TRASEGIM` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_TRATAMIE` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_TRATUBER` | tabla | -1 | 30 | 0 | 0 |  |
| P2 | `inbdlar1` | `T_TSEGCARD` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `legacy` | `T_ACCILABO` | tabla | -1 | 24 | 0 | 0 |  |
| P2 | `legacy` | `T_ACCTRANS` | tabla | -1 | 11 | 0 | 0 |  |
| P2 | `legacy` | `T_ALABCARD` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `legacy` | `T_ANALABOR` | tabla | -1 | 9 | 0 | 0 |  |
| P2 | `legacy` | `T_ANTEFACT` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `legacy` | `T_BIOPSEG` | tabla | -1 | 2 | 0 | 0 |  |
| P2 | `legacy` | `T_BIOPSIAT` | tabla | -1 | 56 | 0 | 0 |  |
| P2 | `legacy` | `T_CASOSMM` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `legacy` | `T_CASOSMMI` | tabla | -1 | 17 | 0 | 0 |  |
| P2 | `legacy` | `T_COMAGUDA` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `legacy` | `T_COMCRONI` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `legacy` | `T_COMDISCA` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `legacy` | `T_COMPCARD` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `legacy` | `T_COMPLICA` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `legacy` | `T_COMQUIR` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `legacy` | `T_COMSEGIM` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `legacy` | `T_DIAGASOC` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `legacy` | `T_DOCUDENG` | tabla | -1 | 17 | 0 | 0 |  |
| P2 | `legacy` | `T_DOCUSOSP` | tabla | -1 | 7 | 0 | 0 |  |
| P2 | `legacy` | `T_FDOLORTO` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `legacy` | `T_FICHAACC` | tabla | -1 | 12 | 0 | 0 |  |
| P2 | `legacy` | `T_FICHASEP` | tabla | -1 | 14 | 0 | 0 |  |
| P2 | `legacy` | `T_HECHOSVI` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `legacy` | `T_INTQUIR` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `legacy` | `T_LUGARVIS` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `legacy` | `T_MBASED` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `legacy` | `T_MCAUMORB` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `legacy` | `T_MCAUSMRE` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `legacy` | `T_MHOJAREP` | tabla | -1 | 17 | 0 | 0 |  |
| P2 | `legacy` | `T_MORTCAUS` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `legacy` | `T_MORTFETA` | tabla | -1 | 13 | 0 | 0 |  |
| P2 | `legacy` | `T_MORTMADR` | tabla | -1 | 22 | 0 | 0 |  |
| P2 | `legacy` | `T_MORTVIOL` | tabla | -1 | 9 | 0 | 0 |  |
| P2 | `legacy` | `T_MRESPA` | tabla | -1 | 11 | 0 | 0 |  |
| P2 | `legacy` | `T_NOTDSP04` | tabla | -1 | 4 | 0 | 0 |  |
| P2 | `legacy` | `T_OTROTRAT` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `legacy` | `T_PACCONDE` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `legacy` | `T_PACIEND` | tabla | -1 | 18 | 0 | 0 |  |
| P2 | `legacy` | `T_PACIENFE` | tabla | -1 | 30 | 0 | 0 |  |
| P2 | `legacy` | `T_PACIENTT` | tabla | -1 | 15 | 0 | 0 |  |
| P2 | `legacy` | `T_PACIMISI` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `legacy` | `T_PERQUIR` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `legacy` | `T_POBESTA` | tabla | -1 | 7 | 0 | 0 |  |
| P2 | `legacy` | `T_PRODIABE` | tabla | -1 | 9 | 0 | 0 |  |
| P2 | `legacy` | `T_PROGCARD` | tabla | -1 | 10 | 0 | 0 |  |
| P2 | `legacy` | `T_PROGMCHE` | tabla | -1 | 26 | 0 | 0 |  |
| P2 | `legacy` | `T_PROGTUBE` | tabla | -1 | 24 | 0 | 0 |  |
| P2 | `legacy` | `T_PROTTROM` | tabla | -1 | 30 | 0 | 0 |  |
| P2 | `legacy` | `T_PRVIHSID` | tabla | -1 | 17 | 0 | 0 |  |
| P2 | `legacy` | `T_RCASOSMI` | tabla | -1 | 14 | 0 | 0 |  |
| P2 | `legacy` | `T_RCASOSMM` | tabla | -1 | 18 | 0 | 0 |  |
| P2 | `legacy` | `T_REGCIRU` | tabla | -1 | 19 | 0 | 0 |  |
| P2 | `legacy` | `T_REGVACU` | tabla | -1 | 13 | 0 | 0 |  |
| P2 | `legacy` | `T_RENDSP04` | tabla | -1 | 4 | 0 | 0 |  |
| P2 | `legacy` | `T_RENGSIT` | tabla | -1 | 16 | 0 | 0 |  |
| P2 | `legacy` | `T_RESUMEN` | tabla | -1 | 9 | 0 | 0 |  |
| P2 | `legacy` | `T_RNACANUL` | tabla | -1 | 10 | 0 | 0 |  |
| P2 | `legacy` | `T_SEGDIABE` | tabla | -1 | 36 | 0 | 0 |  |
| P2 | `legacy` | `T_SEGEVOLP` | tabla | -1 | 16 | 0 | 0 |  |
| P2 | `legacy` | `T_SEGUCARD` | tabla | -1 | 9 | 0 | 0 |  |
| P2 | `legacy` | `T_SIGNSINT` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `legacy` | `T_SIGSINSE` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `legacy` | `T_SITUESPE` | tabla | -1 | 10 | 0 | 0 |  |
| P2 | `legacy` | `T_TRASEGIM` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `legacy` | `T_TRATAMIE` | tabla | -1 | 8 | 0 | 0 |  |
| P2 | `legacy` | `T_TRATUBER` | tabla | -1 | 30 | 0 | 0 |  |
| P2 | `legacy` | `T_TSEGCARD` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `sismai` | `CAUSA` | tabla | -1 | 3 | 0 | 0 |  |
| P2 | `sismai` | `CAUSAANULACION` | tabla | -1 | 4 | 0 | 0 |  |
| P2 | `sismai` | `DOCUMENTOCONS` | tabla | -1 | 12 | 0 | 0 |  |
| P2 | `sismai` | `EVENTOS` | tabla | -1 | 6 | 0 | 0 |  |
| P2 | `sismai` | `M_RELAPARTO` | tabla | -1 | 5 | 0 | 0 |  |
| P2 | `sismai` | `NAC_ASISTENCIA` | tabla | -1 | 3 | 0 | 0 |  |
| P2 | `sismai` | `NAC_TIPOPARTO` | tabla | -1 | 3 | 0 | 0 |  |
| P2 | `sismai` | `NAC_TIPOREG` | tabla | -1 | 3 | 0 | 0 |  |
| P2 | `sismai` | `T_DOC` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `HISTDOC` | tabla | 58.596 | 6 | 0 | 0 |  |
| P3 | `sismai` | `MONITOR_BASEDEDATOS` | tabla | 21.798 | 8 | 0 | 0 |  |
| P3 | `sismai` | `DOCUMENTO_DENGUE` | tabla | 14.702 | 17 | 0 | 0 |  |
| P3 | `sismai` | `MOR_ANULADOS` | tabla | 12.582 | 10 | 0 | 0 |  |
| P3 | `sismai` | `REG_VACUNACION` | tabla | 9.876 | 14 | 0 | 0 |  |
| P3 | `sismai` | `OCUPACION` | tabla | 8.650 | 4 | 0 | 0 |  |
| P3 | `sismai` | `RESUMEN` | tabla | 7.810 | 9 | 0 | 0 |  |
| P3 | `sismai` | `POB_ESTAB` | tabla | 6.529 | 7 | 0 | 0 |  |
| P3 | `sismai` | `CODIFICADOR_EDAD` | tabla | 5.590 | 4 | 0 | 0 |  |
| P3 | `sismai` | `PACIENTE_FICHA_EPI` | tabla | 5.326 | 30 | 0 | 0 |  |
| P3 | `sismai` | `MONITOR_RESPALDO` | tabla | 3.114 | 11 | 0 | 0 |  |
| P3 | `sismai` | `HOJAREPARO` | tabla | 3.060 | 17 | 0 | 0 |  |
| P3 | `sismai` | `CASOSMM` | tabla | 2.407 | 8 | 0 | 0 |  |
| P3 | `sismai` | `PACIENTE_COND_ESPE` | tabla | 1.639 | 5 | 0 | 0 |  |
| P3 | `sismai` | `SEMANAS` | tabla | 1.461 | 8 | 0 | 0 |  |
| P3 | `sismai` | `PROFESION` | tabla | 837 | 8 | 0 | 0 |  |
| P3 | `sismai` | `ALBERGUE` | tabla | 760 | 10 | 0 | 0 |  |
| P3 | `sismai` | `REFERENCIAEDAD` | tabla | 713 | 6 | 0 | 0 |  |
| P3 | `sismai` | `REFERENCIA` | tabla | 670 | 6 | 0 | 0 |  |
| P3 | `sismai` | `ACTIVIDAD_OSPLAN` | tabla | 666 | 4 | 0 | 0 |  |
| P3 | `sismai` | `ASIC` | tabla | 594 | 6 | 0 | 0 |  |
| P3 | `sismai` | `DONDE_REALIZO_PAI` | tabla | 511 | 3 | 0 | 0 |  |
| P3 | `sismai` | `GAPRIVILEGIES` | tabla | 444 | 6 | 0 | 0 |  |
| P3 | `sismai` | `CODIFICADOR` | tabla | 400 | 13 | 0 | 0 |  |
| P3 | `sismai` | `ACTIVIDAD_OSP` | tabla | 139 | 8 | 0 | 0 |  |
| P3 | `sismai` | `CLASIFICADOR` | tabla | 129 | 5 | 0 | 0 |  |
| P3 | `sismai` | `RELACION_PROG_TRATAM` | tabla | 97 | 3 | 0 | 0 |  |
| P3 | `sismai` | `GR_POBLACIONAL` | tabla | 82 | 5 | 0 | 0 |  |
| P3 | `sismai` | `TRATAMIENTO_PROG` | tabla | 79 | 5 | 0 | 0 |  |
| P3 | `sismai` | `TABLASIS` | tabla | 72 | 17 | 0 | 0 |  |
| P3 | `sismai` | `V_LISTA3` | tabla | 68 | 5 | 0 | 0 |  |
| P3 | `sismai` | `INTERVENCION` | tabla | 64 | 5 | 0 | 0 |  |
| P3 | `sismai` | `SITIO_ACCIDENTE` | tabla | 61 | 4 | 0 | 0 |  |
| P3 | `sismai` | `TIPOESTABLE` | tabla | 61 | 8 | 0 | 0 |  |
| P3 | `sismai` | `ANATOMIA` | tabla | 58 | 5 | 0 | 0 |  |
| P3 | `sismai` | `PAIS` | tabla | 57 | 3 | 0 | 0 |  |
| P3 | `sismai` | `ACTIVIDADCOMUN` | tabla | 53 | 6 | 0 | 0 |  |
| P3 | `sismai` | `V_MUERTEMATERNA` | tabla | 52 | 3 | 0 | 0 |  |
| P3 | `historico` | `ERRORES` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `historico` | `ERRORESB` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `historico` | `ERRORESC` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `historico` | `ERRORES_LABO` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `historico` | `ERRORES_RESI` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `historico` | `ERRORES_SINC` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `sismai` | `ACCIDENTELABORAL` | tabla | -1 | 24 | 0 | 0 |  |
| P3 | `sismai` | `ACC_TRANSITO` | tabla | -1 | 11 | 0 | 0 |  |
| P3 | `sismai` | `ANALISIS_LABORATORIO` | tabla | -1 | 9 | 0 | 0 |  |
| P3 | `sismai` | `ANALISIS_LABORATORIO_CARDIO` | tabla | -1 | 8 | 0 | 0 |  |
| P3 | `sismai` | `ANALISIS_LAB_PROG` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `ANEXOS_PERIODO` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `ANTECEDENTES_PROG` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `ANTECED_FACT_RIESGO` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `ANUARIO_01` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `ANUARIO_02` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `ANUARIO_03` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `ANUARIO_04` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `ANUARIO_05` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `ANUARIO_06` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `BACTERIOLOGIA` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `BASES_DIAG_PROG` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `BIOPSIASPACIENTE` | tabla | -1 | 57 | 0 | 0 |  |
| P3 | `sismai` | `BIOPSIASPACIENTESEG` | tabla | -1 | 2 | 0 | 0 |  |
| P3 | `sismai` | `BIOPSIAS_ERROR` | tabla | -1 | 11 | 0 | 0 |  |
| P3 | `sismai` | `BIOPSIATRA` | tabla | -1 | 56 | 0 | 0 |  |
| P3 | `sismai` | `CAMBIOSCIRUGIA` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `sismai` | `CARGO` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `CATEGORIA` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `CATEGORIA_DOC` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `CERTI_MADRE_M` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `CHEQESQUEMA` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `sismai` | `CITOLOGIASAEXAMEN` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `CITOLOGIASANORMAL` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `CLASIF_CONSULTANTE_PROG` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `COMPLICACIONAGUDA` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `COMPLICACIONCARDIOVASCULAR` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `COMPLICACIONCRONICA` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `COMPLICACIONDISCA` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `COMPLICACIONES` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `COMPLICACIONES_SEG` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `COMPLICACIONQUIRURGICA` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `COMPLICACION_PROG` | tabla | -1 | 4 | 0 | 0 |  |
| P3 | `sismai` | `CONDICION` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `CONDICIONCASO` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `CONDICIONESPECIAL` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `sismai` | `CONDICION_INGRESO_MALARIA` | tabla | -1 | 4 | 0 | 0 |  |
| P3 | `sismai` | `CONFIGURACION` | tabla | -1 | 8 | 0 | 0 |  |
| P3 | `sismai` | `CONYUGAL` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `DESTINOCUERPO` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `DIAGNOSTICO` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `DIAGNOSTICOS_ASOC` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `DOC_CONTROL` | tabla | -1 | 4 | 0 | 0 |  |
| P3 | `sismai` | `DOC_SOSPECHA` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `sismai` | `DURACIONEMBARAZO` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `EFECTUO_HECHO` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `EGRESOS` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `ERRORES` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `sismai` | `ERRORES_ANUARIO` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `ERRORES_LABO` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `sismai` | `ERRORES_RESI` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `sismai` | `ERRORES_SINC` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `sismai` | `ESPECIALIDAD` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `ESTADISTICAS` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `ETNIA` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `sismai` | `EVENTOS_LABO` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `sismai` | `EVENTOS_RESI` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `sismai` | `EVOLUCION` | tabla | -1 | 4 | 0 | 0 |  |
| P3 | `sismai` | `FALLALECTURA` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `FICHADELDOLOR` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `FICHADOLORTORACICO` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `FICHAEPI13` | tabla | -1 | 10 | 0 | 0 |  |
| P3 | `sismai` | `FICHAS_EPIDEMIOLOGICAS` | tabla | -1 | 14 | 0 | 0 |  |
| P3 | `sismai` | `FICHA_ACCIDENTE` | tabla | -1 | 12 | 0 | 0 |  |
| P3 | `sismai` | `FINAL_TRATAMIENTO` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `FORMAPARTO` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `HECHOS_VIOLENTOS` | tabla | -1 | 8 | 0 | 0 |  |
| P3 | `sismai` | `HISTORICO_IDS` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `HIST_CODIFICADOR` | tabla | -1 | 4 | 0 | 0 |  |
| P3 | `sismai` | `HOR_AMBULAT` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `INSTITUCION_FORMADORA` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `INTERVENCIONQUIRURGICA` | tabla | -1 | 8 | 0 | 0 |  |
| P3 | `sismai` | `INTERVENCION_OMITIDA` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `LABORATORIOS` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `sismai` | `LIQUIDO_CONTA` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `LOCALIZACIONPULMON` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `LUGARES_VISITADOS` | tabla | -1 | 8 | 0 | 0 |  |
| P3 | `sismai` | `LUGARSUCESO` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `MEDICOFIRMANTE` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `MISION` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `NOTAS_DSP04` | tabla | -1 | 4 | 0 | 0 |  |
| P3 | `sismai` | `NOTIFICANTES` | tabla | -1 | 8 | 0 | 0 |  |
| P3 | `sismai` | `NUMERO_BD` | tabla | -1 | 11 | 0 | 0 |  |
| P3 | `sismai` | `NUTRICION` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `OCUPASIVIGILA` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `OPCION_CERTNACIMIENTO` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `OTROSTRATAMIENTOS` | tabla | -1 | 8 | 0 | 0 |  |
| P3 | `sismai` | `PACIENTE` | tabla | -1 | 15 | 0 | 0 |  |
| P3 | `sismai` | `PACIENTESINEXAMEN` | tabla | -1 | 1 | 0 | 0 |  |
| P3 | `sismai` | `PACIENTE_D` | tabla | -1 | 18 | 0 | 0 |  |
| P3 | `sismai` | `PACIENTE_DIABETES` | tabla | -1 | 15 | 0 | 0 |  |
| P3 | `sismai` | `PACIENTE_ERROR` | tabla | -1 | 1 | 0 | 0 |  |
| P3 | `sismai` | `PACIENTE_EXAMEN` | tabla | -1 | 25 | 0 | 0 |  |
| P3 | `sismai` | `PACIENTE_MISION` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `PERSONALQUIRURGICO` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `PESONALSALUD_POSTGRADOS` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `sismai` | `POS_CONFIG` | tabla | -1 | 25 | 0 | 0 |  |
| P3 | `sismai` | `PRESENCIAEMBARAZO` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `PROGRAMAESTABLEC` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `PROG_CARDIOVASCULAR` | tabla | -1 | 10 | 0 | 0 |  |
| P3 | `sismai` | `PROG_COMUNITARIO` | tabla | -1 | 4 | 0 | 0 |  |
| P3 | `sismai` | `PROG_DIABETES` | tabla | -1 | 9 | 0 | 0 |  |
| P3 | `sismai` | `PROG_DIABE_TEMP` | tabla | -1 | 9 | 0 | 0 |  |
| P3 | `sismai` | `PROG_MAL_CHAG_ESQ` | tabla | -1 | 26 | 0 | 0 |  |
| P3 | `sismai` | `PROG_TUBERCULOSIS` | tabla | -1 | 24 | 0 | 0 |  |
| P3 | `sismai` | `PROG_VIH_SIDA` | tabla | -1 | 17 | 0 | 0 |  |
| P3 | `sismai` | `PROTOCOLOTROMBOLISIS` | tabla | -1 | 30 | 0 | 0 |  |
| P3 | `sismai` | `QUIROFANO` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `REGISTROCIRUGIA` | tabla | -1 | 19 | 0 | 0 |  |
| P3 | `sismai` | `REGISTRO_CIRUGIA` | tabla | -1 | 10 | 0 | 0 |  |
| P3 | `sismai` | `RELACION_COMPLICA` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `RELACION_PROG_ANALISIS` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `RELACION_PROG_ANTECED` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `RELACION_PROG_BASESD` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `RENGLONDSPCON` | tabla | -1 | 4 | 0 | 0 |  |
| P3 | `sismai` | `RENGLONEPI13` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `RENGLONEPICON` | tabla | -1 | 8 | 0 | 0 |  |
| P3 | `sismai` | `RENGLONTELECON` | tabla | -1 | 12 | 0 | 0 |  |
| P3 | `sismai` | `REPORTESANUARIO` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `RESULTADOS_PROG` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `RESUMEN_D` | tabla | -1 | 10 | 0 | 0 |  |
| P3 | `sismai` | `RESUMEN_NEGATIVA` | tabla | -1 | 7 | 0 | 0 |  |
| P3 | `sismai` | `ROLMEDICOINTERV` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `R_TRANSFERENCIA` | tabla | -1 | 10 | 0 | 0 |  |
| P3 | `sismai` | `SEGUIMIENTO_CARDIOVASCULAR` | tabla | -1 | 9 | 0 | 0 |  |
| P3 | `sismai` | `SEGUIMIENTO_DIABETES` | tabla | -1 | 36 | 0 | 0 |  |
| P3 | `sismai` | `SEG_EVOL_PACIENTE` | tabla | -1 | 17 | 0 | 0 |  |
| P3 | `sismai` | `SEMANAPESOTALLA` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `SIGNOS_SINTOMAS` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `SIGNOS_SINTOMAS_SEG` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `SITIOPARTO` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `SITIO_M` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `SITIO_MUERTE` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `SITIO_OCURRENCIA` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `SITUACIONACCIDENTE` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `SITUACION_ESPECIAL` | tabla | -1 | 10 | 0 | 0 |  |
| P3 | `sismai` | `TABLE_CONFIG` | tabla | -1 | 2 | 0 | 0 |  |
| P3 | `sismai` | `TEMPONOMBRE` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `TEMPORAL` | tabla | -1 | 1 | 0 | 0 |  |
| P3 | `sismai` | `TIPOCOMPLICACION` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `TIPODENGUE` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `TIPODOCUMENTO` | tabla | -1 | 10 | 0 | 0 |  |
| P3 | `sismai` | `TIPOEVENTO` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `TIPOEXAMEN` | tabla | -1 | 4 | 0 | 0 |  |
| P3 | `sismai` | `TIPOLOCAL` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `TIPOPERIODO` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `TIPOSITUACION` | tabla | -1 | 4 | 0 | 0 |  |
| P3 | `sismai` | `TIPO_ACCIDENTE` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `TIPO_EXPOSICION` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `TIPO_HECHO` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `TIPO_M` | tabla | -1 | 5 | 0 | 0 |  |
| P3 | `sismai` | `TIPO_OBJETO` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `TIPO_VEHICULO` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `TPACIENTE` | tabla | -1 | 2 | 0 | 0 |  |
| P3 | `sismai` | `TRANSMISION_SIDA` | tabla | -1 | 4 | 0 | 0 |  |
| P3 | `sismai` | `TRATAMIENTO` | tabla | -1 | 8 | 0 | 0 |  |
| P3 | `sismai` | `TRATAMIENTO_SEG` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `TRATAMIENTO_SEGCARDIO` | tabla | -1 | 6 | 0 | 0 |  |
| P3 | `sismai` | `TRATAMIENTO_TUBERCULOSIS` | tabla | -1 | 30 | 0 | 0 |  |
| P3 | `sismai` | `TRNACIDOS` | tabla | -1 | 50 | 0 | 0 |  |
| P3 | `sismai` | `UBICACION_DIAG` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `ULTIMOGRADO` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `V_NACIMIENTO` | tabla | -1 | 4 | 0 | 0 |  |
| P3 | `sismai` | `X_CANT_HAB` | tabla | -1 | 3 | 0 | 0 |  |
| P3 | `sismai` | `X_CAUSAS_MUERTES` | tabla | -1 | 3 | 0 | 0 |  |

## Tablas P1 (dominio) con conteo exacto

| Esquema | Tabla | Filas exactas |
|---|---|---|
| `historico` | `EVENTOS` | 15.281
| `inbdlar1` | `T_ESTABLE` | 0
| `inbdlar1` | `T_ORGGEOG` | 0
| `inbdlar1` | `T_USUARIOS` | 670
| `legacy` | `T_ESTABLE` | 0
| `legacy` | `T_ORGGEOG` | 0
| `legacy` | `T_PERSMEDI` | 0
| `legacy` | `T_USUARIOS` | 0
| `sismai` | `CAMBIOS` | 10
| `sismai` | `CASOS_MMI` | 10.742
| `sismai` | `CATEGORIA_CIE10` | 4
| `sismai` | `CIE10` | 16.627
| `sismai` | `CODIF_CIE10` | 498
| `sismai` | `DEPENDENCIA_ADM` | 104
| `sismai` | `EDADES` | 162
| `sismai` | `ESTABLECIMIENTO` | 21.148
| `sismai` | `ESTABLECIMIENTO_MAESTRA` | 0
| `sismai` | `INFORME_EPI` | 298
| `sismai` | `LOCALIDADESTAB` | 23
| `sismai` | `M_VIOLENTA` | 12.409
| `sismai` | `NIVEL` | 7
| `sismai` | `ORG_GEOGRAFICA` | 58.939
| `sismai` | `PERSONALMEDICO` | 8.607
| `sismai` | `PERSONALSALUD` | 106.979
| `sismai` | `RENGLONTELE` | 2.663.432
| `sismai` | `RENGLON_CASOSMI` | 9.993
| `sismai` | `RENGLON_DSP04` | 323.004
| `sismai` | `RENGLON_EPI15` | 632.665
| `sismai` | `SEXO` | 4
| `sismai` | `USUARIOS` | 844
| `sismai` | `USUARIO_ESTAB` | 0
| `sismai` | `VALIDARCIE10` | 14.304