# -*- coding: utf-8 -*-

import requests
import re
import csv
from time import sleep
from bs4 import BeautifulSoup


header = {
        'Host': 'www.societe.com',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
}


APE = "5520Z"
ZIP = "97"
BASE_URL = "https://www.societe.com/cgi-bin/liste?nom={}&dirig=&pre=&ape={}&dep={}"
letters = 'abcdefghijklmnopqrstuvwxyz'


def run():
    link_list = []
    company_details_list = []
    
    # Get all company links
    for letter in letters:
        links = get_links_from_page(BASE_URL.format(letter, APE, ZIP))
        for link in links:
            link_list.append("https://www.societe.com" + link)
        print('')
        sleep(0.1)

    print('Getting {} organisations.'.format(len(link_list)))
    
    # Scrape all companys
    company_details_list = scrape_company_details(link_list)
    print(len(company_details_list))
    
    # Save all company datas
    save_data_to_csv(company_details_list)


def get_links_from_page(url):
    response = requests.get(url, headers=header)

    if response.status_code == 200:
        print("Page {}...".format(response.url))
        links = scrape_links(response.text)
    else:
        print("Error load page: {}".format(response.status_code))

    return links


def scrape_links(src):
    soup = BeautifulSoup(src, 'html.parser')

    links = []
    for a in soup.find_all('a', href=True, class_='txt-no-underline'):
        links.append(a['href'])
    print("Links in page = {}".format(len(links)))

    return(links)


def scrape_company_details(links):
    details = []
    
    for link in links:
        print("-----========= Get company detail from {}".format(link))
        response = requests.get(link, headers=header)

        if response.status_code == 200:
            print("Get company detail from {}".format(link))
            company_details = parse_details(response.text, link)
            print(company_details)
            details.append(company_details)
        else:
            print("Error load company details form {}. Status code: {}".format(link, response.status_code))


    return details


def parse_details(html, link):
    dt = {}
    soup = BeautifulSoup(html, 'html.parser')

    for table in soup.find_all("table", class_="Table identity mt-16"):
        print(len(table.find_all('tr')))

        for rec in table.find_all('tr'):
            key = rec.find_all('td')[0].text
            value = re.sub("^\s+|\n|\r|\s+$", '',rec.find_all('td')[1].text)
            r = {key: value}
            dt.update(r)

    tm = "N/a"
    for h5 in soup.find_all("h5", class_="Table__leader__title"):
        try:
            tm = h5.find_all("b", class_="fw-normal")[0].text
        except IndexError:
            tm = "N/a"
    type_mandataire = {"TYPE MANDATAIRE": tm}
    dt.update(type_mandataire)

    dm = "N/a"
    gm = "N/a"
    nm = "N/a"
    for leader_table in soup.find_all("table", id="dir0"):
        try:
            dm = leader_table.find_all("td")[0].text.split()[-1]
        except IndexError:
            dm = "N/a"

        try:
            gm = leader_table.find_all("a")[0].text.split()[0]
        except IndexError:
            gm = "N/a"

        try:
            nm = leader_table.find_all("a")[0].text.split()[1:]
        except IndexError:
            nm = "N/a"

    date_mandataire = {"DATE MANDATAIRE": dm}
    dt.update(date_mandataire)

    genre_mandataire = {"GENRE MANDATAIRE": gm + '.'}
    dt.update(genre_mandataire)
    
    nom_mandataire = {"NOM MANDATAIRE": ' '.join(nm)}
    dt.update(nom_mandataire)
    
    url = {"URL": link}
    dt.update(url)

    return dt


def save_data_to_csv(list):
    fields = ["ID",
            "DÉNOMINATION",
            "ADRESSE",
            "SIREN",
            "SIRET (SIEGE)",
            "ACTIVITÉ (CODE NAF OU APE)",
            "FORME JURIDIQUE RCS",
            "DATE IMMATRICULATION RCS",
            "DATE DE DERNIÈRE MISE À JOUR",
            "TRANCHE DEFFECTIF",
            "CAPITAL SOCIAL",
            "RCS",
            "CODE GREFFE",
            "N° DOSSIER",
            "NOM (ADRESSAGE)",
            "COMPLÉMENT NOM (ADRESSAGE)",
            "ADRESSE",
            "CODE POSTAL",
            "VILLE",
            "PAYS",
            "CATÉGORIE",
            "FORME JURIDIQUE INSEE",
            "CODE APE (NAF) DE LENTREPRISE",
            "ACTIVITÉ (CODE NAF OU APE)",
            "CODE APE (NAF) DU SIÈGE",
            "ACTIVITÉ (CODE NAF OU APE) DU SIÈGE",
            "DATE IMMATRICULATION RCS",
            "DATE CRÉATION ENTREPRISE",
            "DATE CRÉATION SIÈGE ACTUEL",
            "TYPE MANDATAIRE",
            "DATE MANDATAIRE",
            "GENRE MANDATAIRE",
            "NOM MANDATAIRE",
            "URL"]
    id = 1
    with open("out.csv", "w") as out_file:
        writer = csv.DictWriter(out_file, fieldnames=fields)
        writer.writeheader()
        for line in list:
            writer.writerow(
                {
                "ID": str(id),
                "DÉNOMINATION": is_not_empty(line, 'Dénomination'),
                "ADRESSE": is_not_empty(line, 'Adresse'),
                "SIREN": is_not_empty(line, 'SIREN'),
                "SIRET (SIEGE)": is_not_empty(line, 'SIRET (siege)'),
                "ACTIVITÉ (CODE NAF OU APE)": is_not_empty(line, 'Activité (Code NAF ou APE)'),
                "FORME JURIDIQUE RCS": is_not_empty(line, 'Forme juridique'),
                "DATE IMMATRICULATION RCS": is_not_empty(line, 'Date immatriculation RCS'),
                "DATE DE DERNIÈRE MISE À JOUR": is_not_empty(line, 'Date de dernière mise à jour'),
                "TRANCHE DEFFECTIF": is_not_empty(line, "Tranche d'effectif"),
                "CAPITAL SOCIAL": is_not_empty(line, "Capital social"),
                "RCS": is_not_empty(line, "RCS"),
                "CODE GREFFE": is_not_empty(line, "Code greffe"),
                "N° DOSSIER": is_not_empty(line, "N° dossier"),
                "NOM (ADRESSAGE)": is_not_empty(line, "Adresse (RCS)"),
                "COMPLÉMENT NOM (ADRESSAGE)": is_not_empty(line, "Nom (adressage INSEE)"),
                "ADRESSE": is_not_empty(line, "Adresse (INSEE)"),
                "CODE POSTAL": is_not_empty(line, "Code postal (INSEE)"),
                "VILLE": is_not_empty(line, "Ville (INSEE)"),
                "PAYS": is_not_empty(line, "Pays (INSEE)"),
                "CATÉGORIE": is_not_empty(line, "Catégorie"),
                "FORME JURIDIQUE INSEE": is_not_empty(line, "Forme juridique INSEE"),
                "CODE APE (NAF) DE LENTREPRISE": is_not_empty(line, "Code APE (NAF) de l'entreprise"),
                "ACTIVITÉ (CODE NAF OU APE)": is_not_empty(line, "Activité (Code NAF ou APE)"),
                "CODE APE (NAF) DU SIÈGE": is_not_empty(line, "Code APE (NAF) du siège"),
                "ACTIVITÉ (CODE NAF OU APE) DU SIÈGE": is_not_empty(line, "Activité (Code NAF ou APE) du siège"),
                "DATE IMMATRICULATION RCS": is_not_empty(line, "Date immatriculation RCS"),
                "DATE CRÉATION ENTREPRISE": is_not_empty(line, "Date création entreprise"),
                "DATE CRÉATION SIÈGE ACTUEL": is_not_empty(line, "Date création siège actuel"),
                "TYPE MANDATAIRE": is_not_empty(line, "TYPE MANDATAIRE"),
                "DATE MANDATAIRE": is_not_empty(line, "DATE MANDATAIRE"),
                "GENRE MANDATAIRE": is_not_empty(line, "GENRE MANDATAIRE"),
                "NOM MANDATAIRE": is_not_empty(line, "NOM MANDATAIRE"),
                "URL": is_not_empty(line, "URL")
                }
            )
            id += 1

def is_not_empty(st, key):
    try:
        return st[key]
    except:
        return "N/a"

if __name__ == "__main__":
    run()
