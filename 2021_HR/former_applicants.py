# -*- coding: utf-8 -*-
import pandas
import re
from pybliometrics.scopus import ScopusSearch

def regulariser_date_publication(_str):
    token_date = _str.split(' ')
    if(re.match('[0-9]', _str[0])):
        jour, mois, annee = token_date[0], token_date[1][:3].upper(), token_date[2]
        s = ' '.join([jour, mois, annee])
    else:
        mois, annee = token_date[0][:3].upper(), token_date[1]
        s = ' '.join([mois, annee])
    return (annee, s)

def obtenir_index_de_titre(_nom_publication, _dataframe):
    list_title = _dataframe['TITLE'].values.tolist()
    for i in range(len(list_title)):
        if(regulariser(_nom_publication) == regulariser(list_title[i])):
            return i
    return -1

def regulariser(_str):
    return re.sub('[^A-Za-z0-9]+', '', re.sub('&', 'and', _str)).lower()

pandas.set_option('mode.chained_assignment', None)
pandas.set_option('display.max_columns', None)
DF_JCR_SCIE = []
DEBUT_ANNEE, ANNEE_REMARQUE, FIN_ANNEE = 2016, 2019, 2020

for i in range(DEBUT_ANNEE, FIN_ANNEE + 1):
    print(str(i) + "년도 시트를 로딩중입니다.")
    DF_JCR_SCIE.append(pandas.read_excel('JCR_SCIE_' + str(i) + '.xlsx'))

DF_APPLICANTS = pandas.read_excel('applicants.xlsx', header = 1)
DF_APPLICANTS = DF_APPLICANTS.drop(["지원번호\nApplication No.", "CNCI", "Reprint Author", "REPRINT AUTHOR\n(Y/N)"], axis = 1)
list_nom_anglais = DF_APPLICANTS['이름 (영문)\nName'].values.tolist()
list_doi = DF_APPLICANTS['DOIs (Final)'].values.tolist()

for i in range(len(list_doi)):
    doi = list_doi[i]
    info_scopus = ScopusSearch("DOI (" + doi + ")", download=True).results[0]
    
    k2 = ANNEE_REMARQUE - DEBUT_ANNEE
    index_remarque = obtenir_index_de_titre(info_scopus.publicationName, DF_JCR_SCIE[k2])
    
    scie_ouinon = 'N'
    if 0 < index_remarque:
        scie_ouinon = 'Y'
    else:
        print("SCIE 논문이 아닙니다.")
        continue
    DF_APPLICANTS['SCIE (Y/N)'][i] = scie_ouinon

    annee, date = regulariser_date_publication(info_scopus.coverDisplayDate)
    DF_APPLICANTS["Publication Year"][i] = annee
    DF_APPLICANTS["Publication Date"][i] = date
    DF_APPLICANTS["#citation"][i] = str(info_scopus.citedby_count)
    
    if int(annee) <= 2020:
        k1 = int(annee) - DEBUT_ANNEE
        index_n = obtenir_index_de_titre(info_scopus.publicationName, DF_JCR_SCIE[k1])
        jif_n = str(DF_JCR_SCIE[k1]['IMPACT_FACTOR'][index_n])
    else:
        jif_n = ''

    DF_APPLICANTS["Publication Year journal impact factor"][i] = jif_n
    DF_APPLICANTS["2019\njournal\nimpact\nfactor"][i] = str(DF_JCR_SCIE[k2]['IMPACT_FACTOR'][index_remarque])
    DF_APPLICANTS["2019 journal impact factor percentile"][i] = str(DF_JCR_SCIE[k2]['JIF_PERCENTILE'][index_remarque])

    author_cru = info_scopus.author_names.split(';')[0]
    if regulariser(author_cru) == regulariser(list_nom_anglais[i]):
        premier_author = list_nom_anglais[i]
        premier_author_ouinon = 'Y'
    else:
        premier_author = author_cru
        premier_author_ouinon = 'N'

    DF_APPLICANTS["1st Author"][i] = premier_author
    DF_APPLICANTS["1ST AUTHOR\n(Y/N)"][i] = premier_author_ouinon

    DF_APPLICANTS["Source\n(Journal)"][i] = info_scopus.aggregationType
    DF_APPLICANTS["volume"][i] = info_scopus.volume

    if info_scopus.issueIdentifier != None:
        issue = info_scopus.issueIdentifier
    else:
        issue = ''
    DF_APPLICANTS["issue"][i] = issue

print(DF_APPLICANTS)




