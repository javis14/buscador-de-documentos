"""BUSCADOR DE DOCUMENTOS - Churquina Javier Pablo"""
import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox as MessageBox
import tkinter as tk
from tkPDFViewer import tkPDFViewer as pdf
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer


def preproceso(NUEVO_TEXTO):
    """ funcion para realizar la limpieza y preprocesamiento del texto """
    # creamos una lista con los caracteres que no seran tomados en cuenta
    signos_esp = ['(', ')', ';', ':', '[', ']', '.', ',', '-', '_',
                  '`', '´', '¨', '=', '{', '}', '$', '%', '”', '“', '?',
                  '¿', '/', '//', '..', '...']

    # obtenemos una lista con las stopwords del idioma español.
    palabras_vacias = stopwords.words('spanish')

    # hacemos la tokenizacion del documento .pdf
    tokens = word_tokenize(NUEVO_TEXTO)

    # obtenemos una lista con las palabras claves del texto
    # sin signos de puntuacion ni palabras vacias.
    keywords = [
        word for word in tokens if not word in palabras_vacias and not word in signos_esp]

    # aplicamos el stemming con el algoritmo SNOWBALL, que admite español
    keywords_stem = []
    snowball_stemmer = SnowballStemmer("spanish")
    for w in keywords:
        keywords_stem.append(snowball_stemmer.stem(w))

    # reconstruimos el texto sin stop-words
    NUEVO_TEXTO = ""
    for i in keywords_stem:
        NUEVO_TEXTO += i+" "

    return NUEVO_TEXTO


def find_similar(tfidf_matrix, tfidf_consulta, top_n=6):
    """ funcion para buscar los n=6 documentos mas similares a la consulta ingresada """
    cosine_similarities = linear_kernel(tfidf_consulta, tfidf_matrix).flatten()
    related_docs_indices = [i for i in cosine_similarities.argsort()[::-1]]
    return [(index, cosine_similarities[index]) for index in related_docs_indices][0:top_n]


def buscar_documento(direccion, tipo_consulta, consulta_archivo):
    """ funcion para cargar los documentos con los que se va a trabajar,
        crear la representacion TFIDF y mostrar los resultados de la consulta """
    global tfidf_matrix
    iLista = 0
    # armamos una lista con todos los documentos .pdf en los que se va a buscar
    MY_PATH = direccion
    contenido = os.listdir(MY_PATH)
    nombre_doc = []
    for fichero in contenido:
        if os.path.isfile(os.path.join(MY_PATH, fichero)) and fichero.endswith('.pdf'):
            nombre_doc.append(fichero)

    # se hace la lectura de todos los documentos .pdf en los que se va a buscar
    # y guardamos los textos en una lista para poder trabajarlos.
    LISTA_DOCUMENTOS = []
    CANTIDAD_DOCUMENTOS = len(nombre_doc)
    for doc in range(CANTIDAD_DOCUMENTOS):
        lector = PdfReader(direccion+'/'+nombre_doc[doc])
        paginas = len(lector.pages)
        TEXTO = ""
        for pag in range(paginas):
            pag = lector.pages[pag]
            TEXTO += pag.extract_text()

        # guardamos el texto de cada documento.
        LISTA_DOCUMENTOS.append((nombre_doc[doc], preproceso(TEXTO)))

    # creamos la representacion TFIDF para todos los documentos pdf
    # en los que se quiere buscar
    vectorizer = TfidfVectorizer(ngram_range=(1, 3))
    tfidf_matrix = vectorizer.fit_transform(
        [content for file, content in LISTA_DOCUMENTOS])

    # cargamos la consulta ingresada (consulta simple o documento)
    # para ser preprocesada
    if tipo_consulta == 1:
        CONSULTA = consulta_archivo
    else:
        lector = PdfReader(consulta_archivo)
        paginas = len(lector.pages)
        CONSULTA = ""
        for pag in range(paginas):
            pag = lector.pages[pag]
            CONSULTA += pag.extract_text()

    # creamos la representacion TFIDF de la consulta ingresada
    consulta_preprocesada = preproceso(CONSULTA)
    tfidf_consulta = vectorizer.transform([consulta_preprocesada])

    # se muestran los documentos recuperados para la consulta ingresada
    cabecera()
    for index, score in find_similar(tfidf_matrix, tfidf_consulta):
        iLista += 1
        resultado(str(score), LISTA_DOCUMENTOS[index][0], direccion, iLista)


def Habilitar():
    """ funcion para habilitar el ingreso de una consulta simple o la carga de un
        documento pdf segun la eleccion del usuario """
    if varOpcion.get() == 1:
        entrada_documento.delete(0, tk.END)
        entrada_documento.config(state=DISABLED)
        entrada_consulta.config(state=NORMAL)
    else:
        entrada_documento.delete(0, tk.END)
        entrada_consulta.delete(0, tk.END)
        entrada_consulta.config(state=DISABLED)
        entrada_documento.config(state=NORMAL)


def ruta_carpeta():
    """ funcion para elegir la carpeta o directorio que contiene todos los
        documentos .pdf a los que se les va a realizar la representacion TFIDF """
    directorio = filedialog.askdirectory()
    if directorio != "":
        os.chdir(directorio)
        direccion = os.getcwd()
        entrada_direccion.insert(0, direccion)


def ruta_documento():
    """ funcion para elegir el documento que se quiere comparar, solo .pdf """
    Habilitar()
    documento = filedialog.askopenfilename(filetypes=(
        ("archivos pdf", "*.pdf"), ("archivos PDF", "*.PDF")))
    entrada_documento.insert(0, documento)


def buscar():
    """ funcion para saber el tipo de busqueda """
    if entrada_direccion.get() == "":
        MessageBox.showinfo("Error!", "Faltan completar casillas")
    else:
        direccion = entrada_direccion.get()
        tipo = varOpcion.get()
        if tipo == 1:
            consulta_archivo = entrada_consulta.get()
            cabecera_resultados()
            buscar_documento(direccion, tipo, consulta_archivo)
        elif tipo == 2:
            cabecera_resultados()
            consulta_archivo = entrada_documento.get()
            buscar_documento(direccion, tipo, consulta_archivo)
        else:
            MessageBox.showinfo("Error!", "Faltan completar casillas")


# INTEFAZ GRAFICA *******************************************************************************
root = Tk()
root.title('Mi buscador')
root.geometry('900x600')
root.state('zoomed')

screenWidth = root.winfo_screenwidth()
varOpcion = IntVar()
vision_pdf = False


cuadro_entrada = tk.Frame(root, padx=10)
cuadro_cabecera_resultado = tk.Frame(cuadro_entrada)

cuadro_bienvenida = tk.Frame(cuadro_entrada)
rotulo_bienvenida = tk.Label(cuadro_bienvenida,
                             text="Búsqueda de documentos .pdf",
                             padx=10, pady=15, font="verdana 14")
rotulo_bienvenida.grid(row=0, column=0)
cuadro_bienvenida.grid(row=0, column=0, columnspan=3)

cuadro_direccion = tk.Frame(cuadro_entrada)
rotulo_direccion = tk.Label(cuadro_direccion,
                            text="Documentos a análizar:",
                            padx=10, pady=10, font="verdana 11")
rotulo_direccion.grid(row=0, column=0)
entrada_direccion = tk.Entry(cuadro_direccion, width=40)
entrada_direccion.grid(row=0, column=1)
boton_cargar = tk.Button(cuadro_direccion, text="Cargar",
                         width=10, command=ruta_carpeta, font='verdana 11')
boton_cargar.grid(row=0, column=2, padx=10)
cuadro_direccion.grid(row=1, column=0, columnspan=3)

cuadro_seleccion = tk.Frame(cuadro_entrada)
rotulo_seleccion = tk.Label(cuadro_seleccion,
                            text="Selecciona un tipo de búsqueda:",
                            padx=10, pady=10, font="verdana 11")
rotulo_seleccion.grid(row=0, column=0)
cuadro_seleccion.grid(row=2, column=0, columnspan=3, sticky=W)

cuadro_consulta_simple = tk.Frame(cuadro_entrada)
opcion1 = tk.Radiobutton(cuadro_consulta_simple,
                         text='Consulta simple',
                         variable=varOpcion,
                         value=1,
                         command=Habilitar,
                         width=22, anchor=W, font="verdana 11")
opcion1.grid(row=0, column=0)
entrada_consulta = tk.Entry(cuadro_consulta_simple, state=DISABLED, width=50)
entrada_consulta.grid(row=0, column=1)
cuadro_consulta_simple.grid(row=3, column=0, columnspan=3, sticky=W)

cuadro_consulta_documento = tk.Frame(cuadro_entrada)
opcion2 = tk.Radiobutton(cuadro_consulta_documento,
                         text='Consulta con documento',
                         variable=varOpcion,
                         value=2,
                         command=ruta_documento,
                         width=22, anchor=W, font="verdana 11")
opcion2.grid(row=0, column=0)
entrada_documento = tk.Entry(cuadro_consulta_documento,
                             state="readonly", width=50)
entrada_documento.grid(row=0, column=1)
cuadro_consulta_documento.grid(row=4, column=0, columnspan=3, sticky=W)

cuadro_buscar = tk.Frame(cuadro_entrada)
boton_buscar = tk.Button(cuadro_buscar, text="Buscar",
                         width=10, font='verdana 12 bold', command=buscar)
boton_buscar.grid(row=0, column=0, pady=10)
cuadro_buscar.grid(row=5, column=0, columnspan=3)


def cabecera_resultados():
    global cuadro_cabecera_resultado
    cuadro_cabecera_resultado.destroy()
    cuadro_cabecera_resultado = tk.Frame(cuadro_entrada)
    cuadro_cabecera_resultado.grid(row=6, column=0, columnspan=3)


def cabecera():
    """ titulo de los resultados """
    cuadro_cabecera = tk.Frame(cuadro_cabecera_resultado)
    rotulo_score = tk.Label(cuadro_cabecera,
                            text="Score",
                            width=10, anchor=W, font="verdana 11")
    rotulo_score.grid(row=0, column=0)
    rotulo_documento = tk.Label(cuadro_cabecera,
                                text="Documentos encontrados",
                                width=50, anchor=W, font="verdana 11")
    rotulo_documento.grid(row=0, column=1)
    cuadro_cabecera.grid(row=0, column=0)


def resultado(tfidf, documento, direccion, i):
    """ funcion para mostrar los documentos recuperados para la consulta ingresada
        cada uno con su correspondiente valor TFIDF y el nombre del documento
        y la opcion para poder ver el contenido del documento """
    cuadro_resultado = tk.Frame(cuadro_cabecera_resultado)
    tf_idf1 = tk.Label(cuadro_resultado,
                       text=tfidf, width=10,
                       bg='white', anchor=W)
    tf_idf1.grid(row=0, column=0, padx=5)
    resultado = tk.Label(cuadro_resultado,
                         text=documento, width=50,
                         bg='white', anchor=W)
    resultado.grid(row=0, column=1, padx=5)
    boton_ver1 = tk.Button(cuadro_resultado, text="Ver", width=10,
                           command=lambda: mostrarPDF(direccion+'/'+documento),
                           font='verdana 11')
    boton_ver1.grid(row=0, column=2, padx=5, pady=2)
    cuadro_resultado.grid(row=i, column=0)


cuadro_entrada.pack(side=tk.LEFT, anchor=N, padx=10)

# seccion de previsualizacion del documento pdf *************************************************
cuadro_salida = Frame(root, padx=10)


def mostrarPDF(ubicacion):
    """ funcion para mostrar un documento obtenido de la consulta """
    global cuadro_pdf
    global vision_pdf
    vision_pdf = True
    destruir_vistaPDF()
    cuadro_pdf = Frame(cuadro_salida)
    ver_pdf = pdf.ShowPdf()
    vista_pdf = ver_pdf.pdf_view(cuadro_pdf,
                                 pdf_location=ubicacion,
                                 width=80, height=100)
    vista_pdf.pack(side=tk.LEFT, padx=10, pady=10)
    cuadro_pdf.pack()


if vision_pdf is False:
    cuadro_pdf = Frame(cuadro_salida)
    ver_pdf = pdf.ShowPdf()
    vista_pdf = ver_pdf.pdf_view(cuadro_pdf, pdf_location=r"",
                                 width=80, height=100)
    vista_pdf.pack(side=tk.LEFT, padx=10, pady=10)
    cuadro_pdf.pack()


def destruir_vistaPDF():
    global cuadro_pdf
    cuadro_pdf.destroy()


cuadro_salida.pack(anchor=N)

root.mainloop()
