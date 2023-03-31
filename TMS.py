import string
import os
from jpype import *  # JClass, getDefaultJVMPath, shutdownJVM, startJVM, JString, ...
from unicode_tr import unicode_tr
import subprocess
from tkinter import *
import tkinter as tkn
from tkinter.messagebox import showinfo
from tkinter import scrolledtext
# ======================================================================================================================

# DEFINE_PATHS - for zemberek.jar and word lists
zemberek_path = r"proje_1/jar/zemberek-full.jar"
data_path = "proje_1/data"
# END_OF_DEFINE_PATHS

# --- START JVM ---
startJVM(getDefaultJVMPath(), "-ea", "-Djava.class.path=" + zemberek_path)

# Define of Java classes and objects
turkish_tokenizer: JClass = JClass("zemberek.tokenization.TurkishTokenizer")
turkish_morphology: JClass = JClass("zemberek.morphology.TurkishMorphology")
turkish_sentence_normalizer: JClass = JClass("zemberek.normalization.TurkishSentenceNormalizer")
paths: JClass = JClass("java.nio.file.Paths")
morphology = turkish_morphology.createWithDefaults()
tokenizer = turkish_tokenizer.DEFAULT
normalizer = turkish_sentence_normalizer(
    turkish_morphology.createWithDefaults(),
    paths.get(str(os.path.join(data_path, "normalization"))),
    paths.get(str(os.path.join(data_path, "lm", "lm.2gram.slm"))),
)


def open_popup(the_result):
    the_result = the_result + "\n\n\n\n\n"
    top = Toplevel(frame)
    top.geometry("480x400")
    top.title("Sonuçlar")
    text_area = scrolledtext.ScrolledText(top,
                                          width=55,
                                          font=("Times New Roman", 12))
    text_area.grid(column=0, row=0, pady=15, padx=15)
    text_area.insert(tkn.INSERT, the_result)


# For all operation functions
def send_arff_file_to_weka(the_weka_file_path: str, the_model_path: str, the_classifier: str):
    result_path = "proje_1\\ARCHIVES2\\custom_folder\\model_result.txt"
    path = os.path.dirname(__file__)        # current folder
    path_test = "C:\\Program Files\\Weka-3-8-6"
    os.chdir(path_test)
    output = subprocess.run("java -cp weka.jar " +
                            the_classifier + " -l " +
                            the_model_path + " -T " +
                            the_weka_file_path +
                            " -p 0 ", capture_output=True)

    result_file = open(result_path, 'wb')
    result_file.write(output.stdout)
    result_file.close()
    result_file = open(result_path, 'r', encoding="UTF-8")
    results = result_file.read()
    result_file.close()
    open_popup(results)
    os.chdir(path)


def send_arff_file_to_weka2(the_weka_file_path: str, the_model_path: str, the_classifier: str):
    result_path = "proje_1\\ARCHIVES2\\custom_folder\\model_result.txt"
    path = os.path.dirname(__file__)        # current folder
    path_test = "C:\\Program Files\\Weka-3-8-6"
    os.chdir(path_test)
    subprocess.call("java -cp weka.jar " +
                    the_classifier + " -l " +
                    the_model_path + " -T " +
                    the_weka_file_path +
                    " -p 0 ")
    result_file = open(result_path, 'r', encoding="UTF-8")
    results = result_file.read()
    result_file.close()
    showinfo(
        title='SONUÇLAR',
        message=results)
    os.chdir(path)


def convert_to_vector(the_target_file_path: str, the_weka_file_path: str, the_vector_list: list,
                      the_category_type: str):

    data_file = open(the_target_file_path, 'r', encoding="UTF-8")
    example_data = data_file.read()  # read whole file to a string
    data_file.close()

    # ============================================ ZEMBEREK JAVA FUNCTIONS =============================================

    # ---- NORMALIZATION ----
    normalized_text = str(normalizer.normalize(JString(example_data)))

    # ---- REMOVE PUNCTUATION ----
    punctuation_free = "".join([i for i in normalized_text if i not in string.punctuation])

    # ---- REMOVE NUMBERS ----
    digit_free = ''.join([i for i in punctuation_free if not i.isdigit()])

    # ---- TOKENIZATION ----
    tokens = []
    for i, token in enumerate(tokenizer.tokenizeToStrings(JString(digit_free))):
        tokens.append(str(token))

    # ---- WORD ANALYSIS ----
    analysis_list = [morphology.analyzeAndDisambiguate(JString(word)).bestAnalysis()[0] for word in tokens]

    # ---- LEMMATIZATION ----
    norm_lemm_text = [str(analysis.getDictionaryItem().normalizedLemma()) for analysis in analysis_list]

    # ---- LOWER ----
    lower_lemm_list = []
    for x in norm_lemm_text:
        text_true = unicode_tr(x).lower()
        x = text_true.replace("â", "a").replace("î", "i")
        lower_lemm_list.append(str(x))

    # ---- REMOVE STOPWORDS ----

    with open(str(os.path.join(data_path, "tr_stopwords.txt"))) as file:
        stopwords_zemberek = [line.rstrip() for line in file]
    len(stopwords_zemberek)

    no_stopwords = [i for i in lower_lemm_list if i not in stopwords_zemberek]

    # ========================================= ZEMBEREK JAVA FUNCTIONS OVER ===========================================

    # ---- PREPARE ARFF FILE FOR WEKA ----
    weka_file = open(the_weka_file_path, 'a', encoding="UTF-8")
    for i in the_vector_list:
        weka_file.write(str(no_stopwords.count(i)) + ",")
    weka_file.write(the_category_type + "\n")
    weka_file.close()


def find_files(the_target_file_path: str, the_weka_file_path: str, the_vector_list: list) -> int:

    counter = 0
    the_category_type = "?"
    target_list = os.listdir(the_target_file_path)
    for x in target_list:
        if x.endswith('.txt'):
            counter += 1
            current_file_path = the_target_file_path + "\\" + x
            convert_to_vector(current_file_path, the_weka_file_path, the_vector_list, the_category_type)
    if counter == 0:
        return -1


# Run once at startup for each weka arff file
def prepare_arff_file(the_weka_file_path: str, the_vector_list: list, the_category_list: list):
    # weka_output_path = file_path + "/OUT/your_weka_test_file.arff"
    weka_file = open(the_weka_file_path, 'w')
    weka_file.write("@RELATION tms\n\n")
    turkish_chars = ['ı', 'ğ', 'ç', 'ş', 'ö', 'ü', 'â', 'î']
    english_chars = ['i', 'g', 'c', 's', 'o', 'u', 'a', 'i']
    temporary_counter = 0
    temporary_string = "{"
    my_vector_list = the_vector_list.copy()

    # attributes must be english characters in weka
    for the_word in my_vector_list:
        i = 0
        while i < len(turkish_chars):
            the_word = the_word.replace(turkish_chars[i], english_chars[i])
            i += 1

        weka_file.write("@ATTRIBUTE " + the_word + "\tREAL" + "\n")
    for category in the_category_list:
        if temporary_counter == 0:
            temporary_string = temporary_string + category
            temporary_counter = -1
        else:
            temporary_string = temporary_string + "," + category
    temporary_string = temporary_string + "}"
    weka_file.write("@ATTRIBUTE class\t" + temporary_string + "\n\n@DATA\n")
    weka_file.close()


# To send user's input to weka
def operation_2(important_data_2: dict, the_vector_list: list, the_category_list: list):
    prepare_arff_file(important_data_2["the_weka_file_path"],
                      the_vector_list,
                      the_category_list)
    convert_to_vector(important_data_2["the_target_file_path"],
                      important_data_2["the_weka_file_path"],
                      the_vector_list,
                      important_data_2["the_category_type"])
    send_arff_file_to_weka(important_data_2["the_weka_file_path"],
                           important_data_2["the_model_path"],
                           important_data_2["the_classifier"])


# To send all executable files in the input folder path to weka
def operation_3(important_data_3: dict, the_vector_list: list, the_category_list: list):

    prepare_arff_file(important_data_3["the_weka_file_path"],
                      the_vector_list,
                      the_category_list)
    check = find_files(important_data_3["the_target_file_path"],
                       important_data_3["the_weka_file_path"],
                       the_vector_list)
    if check == -1:
        showinfo(
            title='Dosya Kontrol',
            message="Klasör yolunda işlenecek dosya bulunamadı!")
        return
    send_arff_file_to_weka(important_data_3["the_weka_file_path"],
                           important_data_3["the_model_path"],
                           important_data_3["the_classifier"])


frame = tkn.Tk()
frame.geometry('900x700')
frame.resizable(False, False)
frame.title('TMS PROJE')

algorithmtype = tkn.IntVar()
operationtype = tkn.IntVar()
categorynumber = tkn.IntVar()
categorychoice4 = tkn.StringVar()
categorychoice2 = tkn.StringVar()
categorychoice3 = tkn.StringVar()
your_text = tkn.StringVar()
categorytype = tkn.StringVar()


def create_vector_list(categorical_path: str, combination: str) -> list:
    vec_path = categorical_path + "\\vectorlist\\" + combination
    vector_file_list = os.listdir(vec_path)
    vector_list = []
    for file in vector_file_list:
        vector_file = open(vec_path + "\\" + file, 'r', encoding="UTF-8")
        vectors = vector_file.read()
        vectors = vectors.split()
        for word in vectors:
            temp_counter = 0
            for vec_word in vector_list:
                if word == vec_word:
                    temp_counter += 1
            if temp_counter == 0:
                vector_list.append(str(word))
    return vector_list


def send_parameter():

    true_archive_path = "proje_1\\ARCHIVES2\\"
    categorical_path = true_archive_path + "cat" + str(categorynumber.get())
    weka_file_path = true_archive_path + "custom_folder\\your_weka_file.arff"

    # ----------------------------------------------------------------------------
    combination = ""
    if categorynumber.get() == 4:
        combination = categorychoice4.get()
    if categorynumber.get() == 3:
        combination = categorychoice3.get()
    if categorynumber.get() == 2:
        combination = categorychoice2.get()
    if operationtype.get() == 3:
        your_text.get()
    # ----------------------------------------------------------------------------
    category_list = os.listdir(categorical_path + "\\data\\" + combination)
    test_file_path = categorical_path \
        + "\\testvector\\tms_" \
        + str(categorynumber.get()) \
        + "_test_" + combination \
        + ".arff"

    # ----------------------------------------------------------------------------
    model_path = categorical_path + "\\model\\tms_" + str(categorynumber.get())
    classifier = ""
    if algorithmtype.get() == 1:
        classifier = "weka.classifiers.bayes.NaiveBayesMultinomial"
        model_path = model_path + "_naivebayesmultinomial_"
    if algorithmtype.get() == 2:
        classifier = "weka.classifiers.bayes.BayesNet"
        model_path = model_path + "_bayesnet_"
    if algorithmtype.get() == 3:
        classifier = "weka.classifiers.trees.RandomForest"
        model_path = model_path + "_randomforest_"
    model_path = model_path + combination + ".model"
    # ------------------------------------------------------------------------------------------------------------------
    if operationtype.get() == 1:
        send_arff_file_to_weka(test_file_path, model_path, classifier)  # ope 1

    if operationtype.get() == 2:
        target_file_path = "proje_1\\ARCHIVES2\\custom_folder\\your_data_file.txt"
        your_file = open(target_file_path, 'w', encoding="UTF-8")
        your_file.write(your_text.get())
        your_file.close()
        vector_list = create_vector_list(categorical_path, combination)
        important_data_2 = {
            "the_model_path": model_path,
            "the_weka_file_path": weka_file_path,
            "the_target_file_path": target_file_path,
            "the_classifier": classifier,
            "the_category_type": categorytype.get()
        }
        operation_2(important_data_2, vector_list, category_list)  # ope 2
    if operationtype.get() == 3:
        if os.path.isdir(your_text.get()):  # folder is exist
            target_file_path = your_text.get()
        else:  # folder is not exist
            showinfo(
                title='Adres Kontrol',
                message="Böyle bir klasör yolu bulunamadı!")
            return
        vector_list = create_vector_list(categorical_path, combination)
        important_data_3 = {
            "the_model_path": model_path,
            "the_weka_file_path": weka_file_path,
            "the_target_file_path": target_file_path,
            "the_classifier": classifier
        }
        operation_3(important_data_3, vector_list, category_list)  # ope 3
    # ------------------------------------------------------------------------------------------------------------------


def check_category_type():
    category_type_1.grid_forget()
    category_type_2.grid_forget()
    category_type_3.grid_forget()
    category_type_4.grid_forget()
    category_type_5.grid_forget()
    if operationtype.get() == 2:
        if categorynumber.get() == 4:
            category_type_1.grid(column=3, row=6, sticky="W", ipadx=4, ipady=4)
            category_type_2.grid(column=3, row=7, sticky="W", ipadx=4, ipady=4)
            category_type_3.grid(column=3, row=8, sticky="W", ipadx=4, ipady=4)
            category_type_4.grid(column=3, row=9, sticky="W", ipadx=4, ipady=4)
            category_type_5.grid(column=3, row=10, sticky="W", ipadx=4, ipady=4)
            categorytype.set("?")

        if categorynumber.get() == 3:

            if categorychoice3.get() == "AstrolojiEkonomiSiyaset":
                category_type_1.grid(column=3, row=6, sticky="W", ipadx=4, ipady=4)
                category_type_2.grid(column=3, row=7, sticky="W", ipadx=4, ipady=4)
                category_type_3.grid(column=3, row=8, sticky="W", ipadx=4, ipady=4)
                category_type_5.grid(column=3, row=9, sticky="W", ipadx=4, ipady=4)
                categorytype.set("?")
            if categorychoice3.get() == "AstrolojiEkonomiSpor":
                category_type_1.grid(column=3, row=6, sticky="W", ipadx=4, ipady=4)
                category_type_2.grid(column=3, row=7, sticky="W", ipadx=4, ipady=4)
                category_type_4.grid(column=3, row=8, sticky="W", ipadx=4, ipady=4)
                category_type_5.grid(column=3, row=9, sticky="W", ipadx=4, ipady=4)
                categorytype.set("?")
            if categorychoice3.get() == "AstrolojiSiyasetSpor":
                category_type_1.grid(column=3, row=6, sticky="W", ipadx=4, ipady=4)
                category_type_3.grid(column=3, row=7, sticky="W", ipadx=4, ipady=4)
                category_type_4.grid(column=3, row=8, sticky="W", ipadx=4, ipady=4)
                category_type_5.grid(column=3, row=9, sticky="W", ipadx=4, ipady=4)
                categorytype.set("?")
            if categorychoice3.get() == "EkonomiSiyasetSpor":
                category_type_2.grid(column=3, row=6, sticky="W", ipadx=4, ipady=4)
                category_type_3.grid(column=3, row=7, sticky="W", ipadx=4, ipady=4)
                category_type_4.grid(column=3, row=8, sticky="W", ipadx=4, ipady=4)
                category_type_5.grid(column=3, row=9, sticky="W", ipadx=4, ipady=4)
                categorytype.set("?")

        if categorynumber.get() == 2:
            if categorychoice2.get() == "AstrolojiEkonomi":
                category_type_1.grid(column=3, row=6, sticky="W", ipadx=4, ipady=4)
                category_type_2.grid(column=3, row=7, sticky="W", ipadx=4, ipady=4)
                category_type_5.grid(column=3, row=8, sticky="W", ipadx=4, ipady=4)
                categorytype.set("?")
            if categorychoice2.get() == "AstrolojiSiyaset":
                category_type_1.grid(column=3, row=6, sticky="W", ipadx=4, ipady=4)
                category_type_3.grid(column=3, row=7, sticky="W", ipadx=4, ipady=4)
                category_type_5.grid(column=3, row=8, sticky="W", ipadx=4, ipady=4)
                categorytype.set("?")
            if categorychoice2.get() == "AstrolojiSpor":
                category_type_1.grid(column=3, row=6, sticky="W", ipadx=4, ipady=4)
                category_type_4.grid(column=3, row=7, sticky="W", ipadx=4, ipady=4)
                category_type_5.grid(column=3, row=8, sticky="W", ipadx=4, ipady=4)
                categorytype.set("?")
            if categorychoice2.get() == "EkonomiSiyaset":
                category_type_2.grid(column=3, row=6, sticky="W", ipadx=4, ipady=4)
                category_type_3.grid(column=3, row=7, sticky="W", ipadx=4, ipady=4)
                category_type_5.grid(column=3, row=8, sticky="W", ipadx=4, ipady=4)
                categorytype.set("?")
            if categorychoice2.get() == "EkonomiSpor":
                category_type_2.grid(column=3, row=6, sticky="W", ipadx=4, ipady=4)
                category_type_4.grid(column=3, row=7, sticky="W", ipadx=4, ipady=4)
                category_type_5.grid(column=3, row=8, sticky="W", ipadx=4, ipady=4)
                categorytype.set("?")
            if categorychoice2.get() == "SiyasetSpor":
                category_type_3.grid(column=3, row=6, sticky="W", ipadx=4, ipady=4)
                category_type_4.grid(column=3, row=7, sticky="W", ipadx=4, ipady=4)
                category_type_5.grid(column=3, row=8, sticky="W", ipadx=4, ipady=4)
                categorytype.set("?")


def check_category_number(number: int):
    numb = number
    categorynumber.set(numb)
    check_category_type()
    category_choice_1.grid_forget()
    category_choice_2.grid_forget()
    category_choice_3.grid_forget()
    category_choice_4.grid_forget()
    category_choice_5.grid_forget()
    category_choice_6.grid_forget()
    category_choice_7.grid_forget()
    category_choice_8.grid_forget()
    category_choice_9.grid_forget()
    category_choice_10.grid_forget()
    label4.grid_forget()
    label4x.grid_forget()

    if number == 4:
        label4x.grid(padx=5, pady=5, column=0, row=15, sticky="W")

    if number == 3:
        checkchoice = categorychoice3.get()
        label4.grid(padx=5, pady=5, column=0, row=15, sticky="W", ipadx=4, ipady=4)
        category_choice_1.grid(column=0, row=16, sticky="W", ipadx=4, ipady=4)
        category_choice_2.grid(column=0, row=17, sticky="W", ipadx=4, ipady=4)
        category_choice_3.grid(column=0, row=18, sticky="W", ipadx=4, ipady=4)
        category_choice_4.grid(column=0, row=19, sticky="W", ipadx=4, ipady=4)

        categorychoice3.set(checkchoice)

    if number == 2:
        checkchoice = categorychoice2.get()
        label4.grid(padx=5, pady=5, column=0, row=15, sticky="W")
        category_choice_5.grid(column=0, row=16, sticky="W", ipadx=4, ipady=4)
        category_choice_6.grid(column=0, row=17, sticky="W", ipadx=4, ipady=4)
        category_choice_7.grid(column=0, row=18, sticky="W", ipadx=4, ipady=4)
        category_choice_8.grid(column=0, row=19, sticky="W", ipadx=4, ipady=4)
        category_choice_9.grid(column=0, row=20, sticky="W", ipadx=4, ipady=4)
        category_choice_10.grid(column=0, row=21, sticky="W", ipadx=4, ipady=4)

        categorychoice2.set(checkchoice)


def check_operation(ot: int):
    check_category_type()
    if ot == 2:
        label6.grid_forget()
        label5.grid(padx=5, pady=5, column=3, row=4, sticky="W")
        your_entry.grid(padx=5, pady=5, column=3, row=5, sticky="W", ipadx=4, ipady=4)

    if ot == 3:
        label5.grid_forget()
        label6.grid(padx=5, pady=5, column=3, row=4, sticky="W")
        your_entry.grid(padx=5, pady=5, column=3, row=5, sticky="W", ipadx=4, ipady=4)
    if ot == 1:
        label5.grid_forget()
        label6.grid_forget()
        your_entry.grid_forget()


# label 1 -> algorithm choice
label1 = tkn.Label(text="Sınıflandırma işlemi için bir algoritma seçiniz.", font='Helvetica 10 underline')
label1.grid(padx=5, pady=5, column=0, row=0, sticky="W")

algorithm_type_1 = tkn.Radiobutton(frame, text="Naive Bayes Multinomial", variable=algorithmtype, value=1)
algorithm_type_2 = tkn.Radiobutton(frame, text="Bayes Net", variable=algorithmtype, value=2)
algorithm_type_3 = tkn.Radiobutton(frame, text="Random Forest", variable=algorithmtype, value=3)
algorithmtype.set(1)

algorithm_type_1.grid(column=0, row=1, sticky="W", ipadx=4, ipady=4)
algorithm_type_2.grid(column=0, row=2, sticky="W", ipadx=4, ipady=4)
algorithm_type_3.grid(column=0, row=3, sticky="W", ipadx=4, ipady=4)

# ----------------------------------------------------------------------------------------------------------------------
# label 2 -> opration choice
label2 = tkn.Label(text="Yapacağınız işlemi seçiniz                    ", font='Helvetica 10 underline')
label2.grid(padx=5, pady=5, column=3, row=0, sticky="W", ipadx=4, ipady=4)

operation_type_1 = tkn.Radiobutton(
    frame,
    text="Test dosyasını gönder",
    variable=operationtype,
    value=1,
    command=lambda: check_operation(1))
operation_type_2 = tkn.Radiobutton(
    frame,
    text="Kendi metnini gir",
    variable=operationtype,
    value=2,
    command=lambda: check_operation(2))
operation_type_3 = tkn.Radiobutton(
    frame,
    text="Klasör adresi gir",
    variable=operationtype,
    value=3,
    command=lambda: check_operation(3))
operationtype.set(1)

operation_type_1.grid(column=3, row=1, sticky="W", ipadx=4, ipady=4)
operation_type_2.grid(column=3, row=2, sticky="W", ipadx=4, ipady=4)
operation_type_3.grid(column=3, row=3, sticky="W", ipadx=4, ipady=4)

# ----------------------------------------------------------------------------------------------------------------------
# label 3 -> category number
labelx = tkn.Label(text="     ")
labelx.grid(padx=5, pady=5, column=1, row=0, sticky="W", ipadx=4, ipady=4)

label3 = tkn.Label(text="Sınıf sayısını giriniz.", font='Helvetica 10 underline')
label3.grid(padx=5, pady=5, column=0, row=7, sticky="W", ipadx=4, ipady=4)

labelx1 = tkn.Label(text="     ")
labelx1.grid(padx=5, pady=5, column=0, row=4, sticky="W", ipadx=4, ipady=4)
labelx2 = tkn.Label(text="     ")
labelx2.grid(padx=5, pady=5, column=0, row=5, sticky="W", ipadx=4, ipady=4)
labelx3 = tkn.Label(text="     ")
labelx3.grid(padx=5, pady=5, column=0, row=6, sticky="W", ipadx=4, ipady=4)

button4 = tkn.Button(
    frame,
    text="4 Sınıf",
    command=lambda: check_category_number(4),
)
button4.grid(padx=5, pady=2, column=0, row=8, ipadx=4, ipady=4, sticky="W")

button3 = tkn.Button(
    frame,
    text="3 Sınıf",
    command=lambda: check_category_number(3)
)
button3.grid(padx=5, pady=2, column=0, row=9, ipadx=4, ipady=4, sticky="W")

button2 = tkn.Button(
    frame,
    text="2 Sınıf",
    command=lambda: check_category_number(2)
)
button2.grid(padx=5, pady=2, column=0, row=10, ipadx=4, ipady=4, sticky="W")
categorynumber.set(4)

# ----------------------------------------------------------------------------------------------------------------------
# label 4 -> category choice
label4 = tkn.Label(text="Sınıflandırılması yapılacak sınıfları seçiniz.")
# label4.grid(padx=5, pady=5, column=4, row=0, sticky="W")

label4x = tkn.Label(frame, text="Astroloji, Ekonomi, Siyaset, Spor")
label4x.grid(padx=5, pady=5, column=0, row=15, sticky="W")

category_choice_0 = tkn.Radiobutton(
    frame,
    text="Astroloji, Ekonomi, Siyaset, Spor",
    variable=categorychoice4,
    value='AstrolojiEkonomiSiyasetSpor', command=check_category_type)
categorychoice4.set('AstrolojiEkonomiSiyasetSpor')

category_choice_1 = tkn.Radiobutton(
    frame,
    text="Astroloji, Ekonomi, Siyaset",
    variable=categorychoice3,
    value='AstrolojiEkonomiSiyaset', command=check_category_type)
category_choice_2 = tkn.Radiobutton(
    frame,
    text="Astroloji, Siyaset, Spor",
    variable=categorychoice3,
    value='AstrolojiSiyasetSpor', command=check_category_type)
category_choice_3 = tkn.Radiobutton(
    frame,
    text="Astroloji, Ekonomi, Spor",
    variable=categorychoice3,
    value='AstrolojiEkonomiSpor', command=check_category_type)
category_choice_4 = tkn.Radiobutton(
    frame,
    text="Ekonomi, Siyaset, Spor",
    variable=categorychoice3,
    value='EkonomiSiyasetSpor', command=check_category_type)
categorychoice3.set('AstrolojiEkonomiSiyaset')

category_choice_5 = tkn.Radiobutton(
    frame,
    text="Astroloji, Ekonomi",
    variable=categorychoice2,
    value='AstrolojiEkonomi', command=check_category_type)
category_choice_6 = tkn.Radiobutton(
    frame,
    text="Astroloji, Siyaset",
    variable=categorychoice2,
    value='AstrolojiSiyaset', command=check_category_type)
category_choice_7 = tkn.Radiobutton(
    frame,
    text="Astroloji, Spor",
    variable=categorychoice2,
    value='AstrolojiSpor', command=check_category_type)
category_choice_8 = tkn.Radiobutton(
    frame,
    text="Ekonomi, Siyaset",
    variable=categorychoice2,
    value='EkonomiSiyaset', command=check_category_type)
category_choice_9 = tkn.Radiobutton(
    frame,
    text="Ekonomi, Spor",
    variable=categorychoice2,
    value='EkonomiSpor', command=check_category_type)
category_choice_10 = tkn.Radiobutton(
    frame,
    text="Siyaset, Spor",
    variable=categorychoice2,
    value='SiyasetSpor', command=check_category_type)
categorychoice2.set('AstrolojiEkonomi')

# ----------------------------------------------------------------------------------------------------------------------
label5 = tkn.Label(frame, text="Sınıflandırılacak metini giriniz.", font='Helvetica 10 underline')
label6 = tkn.Label(frame, text="Klasör yolunu giriniz.", font='Helvetica 10 underline')

your_entry = Entry(frame, width=38, xscrollcommand="scrollbar", textvariable=your_text)
your_entry.focus_set()
category_type_1 = tkn.Radiobutton(frame, text="Astroloji", variable=categorytype, value="Astroloji")
category_type_2 = tkn.Radiobutton(frame, text="Ekonomi", variable=categorytype, value="Ekonomi")
category_type_3 = tkn.Radiobutton(frame, text="Siyaset", variable=categorytype, value="Siyaset")
category_type_4 = tkn.Radiobutton(frame, text="Spor", variable=categorytype, value="Spor")
category_type_5 = tkn.Radiobutton(frame, text="?", variable=categorytype, value="?")

# ----------------------------------------------------------------------------------------------------------------------

# parameter button
send_parameter_button = tkn.Button(
    frame,
    text="Parametreyi Al",
    command=send_parameter)

label_y = tkn.Label(frame, text="     ")
label_y.grid(padx=5, pady=5, column=1, row=0, sticky="W", ipadx=4, ipady=4)
send_parameter_button.grid(padx=5, pady=5, column=5, row=0, ipadx=4, ipady=4, sticky="W")


frame.mainloop()

# ---- CLOSE JVM ----
shutdownJVM()
