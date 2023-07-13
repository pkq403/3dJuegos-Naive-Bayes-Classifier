# -*- coding: utf-8 -*-

"""
3Djuegos NAIVE-BAYES
"""
import re
import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
import pprint
import tkinter as tk
from PIL import Image, ImageTk

# *** Global variables ***
is3djuegos = r"^https?://(www\.)?3djuegos\.com/"
pattern_lines = "xxlf" # patron para distinguir comentarios

# Pathing files
current_script_path = os.path.dirname(os.path.abspath(__file__))
path_file = os.path.join(current_script_path, "files", "comments.txt")

actual_coment = "PREDEF"
comentarios = []

total_p = 0 # total de repeticiones palabras positivas
total_n = 0 # total de repeticiones palabras negativas
total_neu = 0 # total de repeticiones de palabras neutras
total = 0 # numero total de resenhas

#*** Vocabs ***
p_vocab = {}
neu_vocab = {}
n_vocab = {}


def loadComments(p_url):
    url = p_url
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    tag = 'script'
    
    tag_array = soup.find_all(tag)
    if os.path.exists(path_file):
        os.remove(path_file)
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
                comentarios = []
                for o in json_objects:
                    if o["tree_level"] == "0":
                        comentarios.append(o["content"])
                    #pprint.pprint(o) printea los obbjetos json con formato
                for i, text in enumerate(comentarios):
                       file.write(pattern_lines + text + "\n")
    # Comments written in comments.txt

def readComments():
    coments = []
    with open(path_file, "r", encoding="utf-8") as file:
        coment = "NO MORE COMMENTS\n"
        for line in file:
            if re.search(pattern_lines, line):
                coments.append(re.sub(pattern_lines, "", coment))
                coment = ""
            coment += line
        coments.append(re.sub(pattern_lines, "", coment))
    return coments

def naivebayes(comentario):
    pass
    
if __name__=='__main__':
    
    def write_comment():
        global comentarios
        actual_coment = comentarios.pop() if len(comentarios) > 1 else comentarios[0]
        
        text_block.configure(state=tk.NORMAL)
        text_block.delete("1.0", tk.END)
        text_block.insert(tk.END, actual_coment)
        text_block.configure(state="disabled")
        
    def on_positive():
        global total_p
        if actual_coment in p_vocab.keys():
            p_vocab[actual_coment] += 1
        else:
            p_vocab[actual_coment] = 1 # use add-1 to do not bad calcs
        total_p += 1
        write_comment()
        
    def on_neutral():
        global total_neu
        if actual_coment in p_vocab.keys():
            neu_vocab[actual_coment] += 1
        else:
            neu_vocab[actual_coment] = 1 # use add-1 to do not bad calcs
        total_neu += 1
        write_comment()
    
    def on_negative():
        global total_n
        if actual_coment in n_vocab.keys():
            n_vocab[actual_coment] += 1
        else:
            n_vocab[actual_coment] = 1 # use add-1 to do not bad calcs
        total_n += 1
        write_comment()
         
    def loadintrotrain():
        endtrain_frame.pack_forget()
        url_text.delete("1.0", tk.END)
        introtrain_frame.pack()
    
    def gotrain():
        global comentarios # accedemos a la variable global comentarios
        input_url = url_text.get("1.0", "end-1c").strip()
        if re.match(is3djuegos, input_url):
            loadComments(input_url)
            comentarios = readComments()
            introtrain_frame.pack_forget()
            train_frame.pack()
            write_comment()
        else:
            url_text.delete("1.0", tk.END)
            url_text.insert(tk.END, "No es un link a una noticia de 3djuegos")
            
    def end_train(): # Aqui se decide si hacer otro entrenamiento con otra noticia o si pasar a la fase de test
        train_frame.pack_forget()
        endtrain_frame.pack()
        
    def gotest():
        endtrain_frame.pack_forget()
        test_frame.pack()

    def test():
        global comentarios
        urltest = urltest_text.get("1.0", "end-1c").strip()
        if re.match(is3djuegos, urltest):
            loadComments(urltest)
            comentarios = readComments()
            
            for c in comentarios:
                if naivebayes(c) == "POS":
                    res[0] += 1
                elif naivebayes(c) == "NEU":
                    res[1] += 1
                elif naivebayes(c) == "NEG":
                    res[2] += 1
                
        else:
            url_text.delete("1.0", tk.END)
            url_text.insert(tk.END, "No es un link a una noticia de 3djuegos")
        
    
    #GUI
    root = tk.Tk()
    root.title("3djuegos -> Review Comments")
    root.iconbitmap(os.path.join(current_script_path, "icons", "3djuegos.ico"))
    
    # intro train frame
    introtrain_frame = tk.Frame(root)
    introtrain_frame.pack()
    introtrain_label = tk.Label(introtrain_frame, text = "Insert 3dJuegos news link")
    introtrain_label.config(font =("Courier", 14))
    introtrain_label.pack()
    url_text = tk.Text(introtrain_frame, width=60, height=5)
    url_text.pack()
    buttonto_train = tk.Button(introtrain_frame, text="Train", bg="#53F484", command=gotrain)
    buttonto_train.pack(padx=5, side=tk.RIGHT)
    
    # train frame
    train_frame = tk.Frame(root)
    
    train_label = tk.Label(train_frame, text = "Review Comments")
    train_label.config(font =("Courier", 14))
    train_label.pack()
    
    text_block = tk.Text(train_frame)
    text_block.pack(fill=tk.BOTH, expand=True)
    
    #Botones
    button_frame = tk.Frame(train_frame)
    button_frame.pack(pady=10)
    
    positive_button = tk.Button(button_frame, text="Positive", bg="green", command=on_positive)
    positive_button.pack(side=tk.LEFT, padx=5)
    
    neutral_button = tk.Button(button_frame, text="Neutral", bg="gray", command=on_neutral)
    neutral_button.pack(side=tk.LEFT, padx=5)
    
    negative_button = tk.Button(button_frame, text="Negative", bg="red", command=on_negative)
    negative_button.pack(side=tk.LEFT, padx=5)
    
    end_button = tk.Button(button_frame, text="End train phase", bg="#ADD8E6", command=end_train)
    end_button.pack(pady=10, anchor=tk.CENTER, padx=5)
    
    # Endtrain frame
    endtrain_frame = tk.Frame(root)
    button_train = tk.Button(endtrain_frame, text="Train with other news", bg="red", command=loadintrotrain, width=20, height=5)
    button_train.grid(row=0, column=0, padx=10, pady=5)
    button_train2 = tk.Button(endtrain_frame, text="Test phase", bg="blue", command=gotest, width=20, height=5)
    button_train2.grid(row=0, column=1, padx=10, pady=5)

    # Test frame 
    res = [0,0,0] # positivos, neutrales, negativos
    test_frame = tk.Frame(root)
    test_label = tk.Label(test_frame, text = "Insert 3dJuegos link to test")
    test_label.config(font =("Courier", 14))
    test_label.pack()
    urltest_text = tk.Text(test_frame, width=60, height=5)
    urltest_text.pack()
    button_test = tk.Button(test_frame, text="Test!", bg="#53F484", command=test)
    button_test.pack(padx=5, side=tk.RIGHT)
    
    root.mainloop()
        