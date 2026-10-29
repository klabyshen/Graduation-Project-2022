# Turkish Text Classification Using Machine Learning

## Overview

This project focuses on classifying Turkish text into predefined categories using machine learning algorithms. It was developed in Python and uses text preprocessing, TF-IDF feature extraction, and multiple classification models to analyze Turkish texts.

The system classifies texts into four main categories: **Astrology, Economy, Politics, and Sports**.

## How It Works

1. **Text Preprocessing:** Turkish texts are preprocessed using the Zemberek NLP library, written in Java, and cleaned by removing stop words.
2. **Feature Extraction:** The processed texts are converted into numerical feature vectors using TF-IDF (Term Frequency-Inverse Document Frequency). The vocabulary can also be manually updated to support new texts.
3. **Data Formatting:** The resulting feature vectors are exported in ARFF format for use with Weka.
4. **Model Training and Evaluation:** Ten different machine learning algorithms are used to train and evaluate classification models on the prepared datasets.
5. **Text Classification:** The trained models predict which predefined category or combination of categories best matches a given text.

## Results

Based on the experiments conducted with the available datasets, **Random Forest, Bayes Net, and Naive Bayes Multinomial** provided the most consistent, effective, and fast results among the evaluated algorithms.

## Potential Applications

The modular structure of the project allows it to be adapted to other text classification tasks by changing the training datasets and target categories.

## Technologies Used

- **Python:** Main implementation and text processing workflow
- **Zemberek NLP:** Turkish text preprocessing and stop-word removal
- **TF-IDF:** Text feature extraction
- **Weka:** Machine learning model training and evaluation
- **ARFF:** Dataset representation and exchange format

## Workflow

```text
Turkish Text Input
        |
        v
Zemberek Preprocessing
(text cleaning and stop-word removal)
        |
        v
TF-IDF Feature Extraction
        |
        v
ARFF Data Format
        |
        v
Weka Classification Models
        |
        v
Predicted Text Categories
```

## Possible Future Improvements

- Add quantitative evaluation metrics such as accuracy, precision, recall, and F1-score.
- Automate vocabulary updates for newly encountered texts.
- Expand the dataset and add new classification categories.
- Compare the evaluated models on a consistent test set.



![alt text](https://github.com/klabyshen/Graduation-Project-2022/blob/main/custom-text-test.jpg?raw=true)
