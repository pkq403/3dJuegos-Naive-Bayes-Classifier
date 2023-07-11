# -*- coding: utf-8 -*-

"""
Web Scraping 
ejemplo
"""
import re
import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import codecs
import json
import pprint

if __name__=='__main__':
    url = "https://www.3djuegos.com/juegos/pokemon-escarlata-purpura/noticias/tres-pokemon-dificiles-atrapar-toda-saga-nos-obligaron-a-aprender-braille-lastima-que-algo-asi-nunca-vaya-a-pasar-nuevo"
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    tag = 'script'
    
    tag_array = soup.find_all(tag)
    path_file = "C:/Users/pedro/OneDrive/Escritorio/Pedro/Python/extractcomments/files/file1.txt"
    if os.path.exists(path_file):
        os.remove(path_file)
    regex_comentario1nivel = r'"tree_level":"0"' 
    regex = r'"content":"([^"]*)"'
    regex_llaves = r"(\{[^{}]*\})" # regex para encontrar todas las cadenas entre llaves
    with open(path_file, "w", encoding="utf-8") as file:
        for i in tag_array:
            content_tag = i.get_text()
            start_end_json = (170,-288) # TODO: es muy cutre parsear los JSON asi, tengo que arreglarlo
            if "AML.Comments" in content_tag:
                parsed = content_tag[start_end_json[0]:start_end_json[1]]
                json_items = re.findall(regex_llaves, parsed)
                json_objects = []
                for j in json_items:
                    json_objects.append(json.loads(j))
                for o in json_objects:
                    pprint.pprint(o)
                comments = json_items[0]
                resultados = re.findall(regex_comentario1nivel, content_tag)
                comentarios = []
                for res in resultados:
                    #print(res)
                    comentarios.append(re.findall(regex, res))
                for i, text in enumerate(comentarios):
                    raw = r"" + text
                    try:
                        file.write(str(i) + ": " + raw.encode().decode('unicode-escape') + "\n")
                    except:
                        file.write("\nerror: COMENTARIO NO PARSEABLE ->\n")
                        file.write(str(i) + ": " + text + "\n")
                        
                    
    #with open(path_file, "r", encoding="utf-8") as file:
        #print(file.read())
        