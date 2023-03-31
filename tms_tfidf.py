import string
import os
import math
from unicode_tr import unicode_tr
from jpype import *  # JClass, getDefaultJVMPath, shutdownJVM, startJVM, JString, ...

my_archive_path = r"proje_1\ARCHIVES\cat4\vevec"

category_list = os.listdir(my_archive_path)
print(category_list)
y = 0
categories = dict.fromkeys(category_list, y)


# print(categories)


def create_categories(category_list: list) -> dict:
    my_dict = dict()  # create dictionary
    for name in category_list:
        my_dict[name] = 0
    return my_dict


template_word_frequency = create_categories(category_list)


def generate_categories() -> dict:
    return template_word_frequency.copy()


def add_word(all_word: dict, word: str, group: str):
    if word not in all_word:
        all_word[word] = generate_categories()
    all_word[word][group] += 1
    categories[group] += 1


# DEFINE_PATHS - zemberek.jar and word lists
ZEMBEREK_PATH = r"proje_1/jar/zemberek-full.jar"
DATA_PATH = "proje_1/data"
# END_OF_DEFINE_PATHS

# --- START JVM ---
startJVM(getDefaultJVMPath(), "-ea", "-Djava.class.path=" + ZEMBEREK_PATH)

# Define of Java classes and objects
TurkishTokenizer: JClass = JClass("zemberek.tokenization.TurkishTokenizer")
TurkishMorphology: JClass = JClass("zemberek.morphology.TurkishMorphology")
TurkishSentenceNormalizer: JClass = JClass("zemberek.normalization.TurkishSentenceNormalizer")
Paths: JClass = JClass("java.nio.file.Paths")
morphology = TurkishMorphology.createWithDefaults()
tokenizer = TurkishTokenizer.DEFAULT
normalizer = TurkishSentenceNormalizer(
    TurkishMorphology.createWithDefaults(),
    Paths.get(str(os.path.join(DATA_PATH, "normalization"))),
    Paths.get(str(os.path.join(DATA_PATH, "lm", "lm.2gram.slm"))),
)


# Text preprocessing with Zemberek Java (Normalization, Remove Punctuation, ...)


def prepare_data(the_file, the_folder, word_list):
    data_file = open(the_file, 'r', encoding="ANSI")
    example_data = data_file.read()  # read whole file to a string
    data_file.close()

    # _________________ ZEMBEREK JAVA __________________________________________________________________________________

    # NORMALIZATION
    normalized_text = str(normalizer.normalize(JString(example_data)))

    # REMOVE PUNCTUATION
    punctuation_free = "".join([i for i in normalized_text if i not in string.punctuation])

    # REMOVE NUMBERS
    digit_free = ''.join([i for i in punctuation_free if not i.isdigit()])

    # TOKENIZATION
    tokens = []
    for i, token in enumerate(tokenizer.tokenizeToStrings(JString(digit_free))):
        tokens.append(str(token))

    # WORD ANALYSIS
    analysis_list = [morphology.analyzeAndDisambiguate(JString(word)).bestAnalysis()[0] for word in tokens]

    # LEMMATIZATION
    norm_lemm_text = [str(analysis.getDictionaryItem().normalizedLemma()) for analysis in analysis_list]

    # lower_norm_lemm_text = [item.replace("â", "a").replace("î", "ı").lower() for item in norm_lemm_text]
    lower_norm_lemm_text = []
    for x in norm_lemm_text:
        text_true = unicode_tr(x)
        x = text_true.replace("â", "a").replace("î", "i").lower()
        lower_norm_lemm_text.append(str(x))

    # REMOVE STOPWORDS
    with open(str(os.path.join(DATA_PATH, "tr_stopwords.txt"))) as file:
        stopwords_zemberek = [line.rstrip() for line in file]
    len(stopwords_zemberek)

    no_stopwords = [i for i in lower_norm_lemm_text if i not in stopwords_zemberek]

    analysis_list2 = [morphology.analyzeAndDisambiguate(JString(ns)).bestAnalysis()[0] for ns in no_stopwords]
    word_pass_pos = []
    for ns in no_stopwords:
        analysis_list2 = [morphology.analyzeAndDisambiguate(JString(ns)).bestAnalysis()[0]]
        for analysis in analysis_list:
            analysis  = [str(analysis.getDictionaryItem().primaryPos.shortForm)]
            if analysis == "Noun":
                word_pass_pos.append(str(ns))
    print(word_pass_pos)
    for word in no_stopwords:
        add_word(word_list, word, the_folder)

    # _________________ ZEMBEREK JAVA OVER _____________________________________________________________________________


def findfiles(thepath, current_folder, word_list):
    all_folders_list = os.listdir(thepath)
    if len(all_folders_list) > 0:
        for current_path in all_folders_list:
            current_path2 = thepath + "\\" + current_path
            if os.path.isdir(current_path2):
                current_folder = current_path
                findfiles(current_path2, current_folder, word_list)
            elif current_path.endswith('.txt'):
                prepare_data(current_path2, current_folder, word_list)
            else:
                print("Böyle bir dosya yolu tanımlı değil")


word_list = {}
findfiles(my_archive_path, "Genre Datasets", word_list)

# print(word_list)

# --- VECTOR -----------------------------------------------------------------------------------------------------------

temporary_counter = 0
temp_counter = 0
for category in category_list:

    if os.path.exists(r"proje_1\vectors\vector_" + category + ".txt"):
        os.remove(r"proje_1\vectors\vector_" + category + ".txt")
        print("Dosya kaldırıldı.")
for my_word in word_list:
    n = 0
    for category in category_list:
        temporary_counter += 1
        if word_list[my_word][category] != 0:
            n += 1
    IDF = math.log(temporary_counter / n)

    if IDF == 0:
        IDF = 0.000000001

    for category in category_list:
        TF = word_list[my_word][category] / categories[category]
        # print(str(word_list[my_word][category]) + " ehe " + str(categories[category]))
        word_list[my_word][category] = TF * IDF
        # print(word_list[my_word][category])
        temp_counter += 1
        # print(my_word + "  için " + category + " sınıfındaki TF-IDF değeri:  " + str(word_list[my_word][category]))

        # vector_file.write(str(my_word.encode("utf-8", "replace")) + "\n")

print("\n" + str(temp_counter))

for category in category_list:
    temp_counter = 0
    vector_file = open(r"proje_1\vectors\vector_" + category + ".txt", 'a'
                       , encoding="utf-8")
    sorted_keys = sorted(word_list, key=lambda x: -(word_list[x][category]))
    # print(type(sorted_keys))
    for item in sorted_keys:
        # print(type(item))
        if temp_counter < 150:
            # vector_file.write(str(item) + "\n")
            string_data = str(item) + "\n"
            vector_file.write((item + "\n").encode("utf-8").decode())
        temp_counter += 1
    vector_file.close()
# print result

# --- VECTOR -----------------------------------------------------------------------------------------------------------

shutdownJVM()

word_list.clear()



