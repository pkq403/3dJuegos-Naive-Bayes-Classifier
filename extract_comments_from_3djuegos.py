# -*- coding: utf-8 -*-

"""
3Djuegos NAIVE-BAYES
"""
import re
import os
import copy
import requests
from bs4 import BeautifulSoup
import json
import pprint
import tkinter as tk

# *** Global variables ***
is3djuegos = r"^https?://(www\.)?3djuegos\.com/"
pattern_lines = "xxlf" # pattern to distinguish lines

# Pathing files
current_script_path = os.path.dirname(os.path.abspath(__file__))
path_file = os.path.join(current_script_path, "files", "comments.txt")

actual_coment = "PREDEF"
comentarios = []

total_p = 0 # total positive comments
total_n = 0 # total de negatives comments
total_neu = 0 # total de neutral comments
total_cometarios = 0 # total number of comments

#*** Vocabs ***
p_vocab = {}
neu_vocab = {}
n_vocab = {}

res = [0,0,0] # positives, neutrals, negatives in the test link

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

def normaliza(com):
    # Basic text normalization
    clean_text = re.sub(r'[^\w\s]','',com) # Remove puntuation signs
    return clean_text.lower().split(" ") # Change the text to lower case and divides by  " "

def naivebayes(comentario):
    global p_vocab, n_vocab, neu_vocab
    global total_p, total_n, total_neu, total_comentarios
    local_pv = copy.deepcopy(p_vocab)
    local_nv = copy.deepcopy(n_vocab)
    local_neuv = copy.deepcopy(neu_vocab)
    # kind of fix in order to make NAIVE BAYES work when a non explored word is found in a query (Because we dont use a fixed vocabulary) 
    # if there is a word non explored in any vocab (neutral, positive or negative)
    # adds 1 to all the words and 1 to the new non explored word (it is a kind of add-1)
    clean_com = normaliza(comentario)
    for p in clean_com:
        if not p in local_pv.keys():
            local_pv[p] = 0
            local_pv = {k: v + 1 for k, v in local_pv.items()}
    
        if not p in local_nv.keys():
            local_nv[p] = 0
            local_nv = {k: v + 1 for k, v in local_nv.items()}
            
        if not p in local_neuv.keys():
            local_neuv[p] = 0
            local_neuv = {k: v + 1 for k, v in local_neuv.items()}
            
    
    start_probs = [total_p / total_comentarios, total_neu / total_comentarios, total_n / total_comentarios]
    total_ocurs = [sum(local_pv.values()), sum(local_neuv.values()), sum(local_nv.values())]
    end_probs = []
    
    for i, sp in enumerate(start_probs):
        prob = sp
        for word in clean_com:
            prob *= (local_pv[word]/total_ocurs[i])
        end_probs.append(prob)
    
    max_p = max(end_probs)
    if max_p == 0: # Comments with no words trained are classified as NEUTRALS
        return "NEU"
    
    maxim_prob = end_probs.index(max_p)
    
    if maxim_prob == 0:
        return "POS"
    elif maxim_prob == 1:
        return "NEU"
    elif maxim_prob == 2:
        return "NEG"
    return "ERROR"

def addwords(comentario, vocab):
    clean_text = normaliza(comentario)
    
    for word in clean_text:
        vocab[word] = 1 if not word in vocab.keys() else vocab[word] + 1
    
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
        addwords(actual_coment, p_vocab)
        total_p += 1 # 1 more positive comment ++
        write_comment()
        
    def on_neutral():
        global total_neu
        addwords(actual_coment, neu_vocab)
        total_neu += 1
        write_comment()
    
    def on_negative():
        global total_n
        addwords(actual_coment, n_vocab)
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
        global total_comentarios
        endtrain_frame.pack_forget()
        test_frame.pack()
        total_comentarios = total_p + total_n + total_neu

    def test():
        global comentarios, res
        urltest = urltest_text.get("1.0", "end-1c").strip()
        if re.match(is3djuegos, urltest):
            loadComments(urltest)
            comentarios = readComments()
            
            for c in comentarios[1:]:
                if naivebayes(c) == "POS":
                    res[0] += 1
                elif naivebayes(c) == "NEU":
                    res[1] += 1
                elif naivebayes(c) == "NEG":
                    res[2] += 1
                    
            test_frame.pack_forget()
            
            list_labels = ["Nº Positives comments predicted = ", "Nº Neutral comments predicted = ", "Nº Negatives comments predicted = "]
            for i,label in enumerate(list_labels):
                l_label = tk.Label(results_frame, text = label + str(res[i]), bg="#F5C043")
                l_label.place(x = 20)
                l_label.pack()
            conc_text ="The prediction has been: "
            conclusion_label = tk.Label(results_frame, text = "", font = ("Courier", 14), bg="#F5C043") 
            final_predic = res.index(max(res))
            if final_predic == 0:
                conclusion_label.config(text = conc_text +  "POSITIVE")
            elif final_predic == 1:
                conclusion_label.config(text = conc_text + "NEUTRAL")
            elif final_predic == 2:
                conclusion_label.config(text = conc_text +  "NEGATIVE")
            conclusion_label.pack()
            
            results_frame.pack()
        else:
            url_text.delete("1.0", tk.END)
            url_text.insert(tk.END, "Not a link of a 3djuegos's news")
        
    
    #GUI
    root = tk.Tk()
    root.title("3djuegos -> Review Comments")
    root.iconbitmap(os.path.join(current_script_path, "icons", "3djuegos.ico"))
    
    # intro train frame
    introtrain_frame = tk.Frame(root)
    introtrain_frame.configure(bg="#F5C043")
    introtrain_frame.pack()
    introtrain_label = tk.Label(introtrain_frame, text = "Insert 3dJuegos news link", font =("Courier", 14), bg="#F5C043")
    introtrain_label.pack()
    url_text = tk.Text(introtrain_frame, width=60, height=5, bg = "#EAEB28")
    url_text.pack()
    buttonto_train = tk.Button(introtrain_frame, text="Train", bg="#53F484", command=gotrain)
    buttonto_train.pack(padx=5, side=tk.RIGHT)
    
    # train frame
    train_frame = tk.Frame(root)
    train_frame.configure(bg="#F5C043")
    train_label = tk.Label(train_frame, text = "Review Comments", font =("Courier", 14), bg="#F5C043")
    train_label.pack()
    
    text_block = tk.Text(train_frame, bg = "#EAEB28")
    text_block.pack(fill=tk.BOTH, expand=True)
    
    #Botones
    button_frame = tk.Frame(train_frame)
    button_frame.configure(bg="#F5C043")
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
    endtrain_frame.configure(bg="#F5C043")
    button_train = tk.Button(endtrain_frame, text="Train with other news", bg="#1B6FDE", command=loadintrotrain, width=20, height=5)
    button_train.grid(row=0, column=0, padx=10, pady=5)
    button_train2 = tk.Button(endtrain_frame, text="Test phase", bg="#57DE47", command=gotest, width=20, height=5)
    button_train2.grid(row=0, column=1, padx=10, pady=5)

    # Test frame 
    
    test_frame = tk.Frame(root)
    test_frame.configure(bg="#F5C043")
    test_label = tk.Label(test_frame, text = "Insert 3dJuegos link to test", font =("Courier", 14), bg="#F5C043")
    test_label.pack()
    urltest_text = tk.Text(test_frame, width=60, height=5, bg = "#EAEB28")
    urltest_text.pack()
    button_test = tk.Button(test_frame, text="Test!", bg="#53F484", command=test)
    button_test.pack(padx=5, side=tk.RIGHT)
    
    # Results frame
    results_frame = tk.Frame(root)
    results_frame.configure(bg="#F5C043")
    results_title = tk.Label(results_frame, text = "Final Results", font = ("Courier", 12), bg="#F5C043")
    results_title.pack()

    root.mainloop()
        