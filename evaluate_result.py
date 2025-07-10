import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder


RESULTS_DIR = "result"
SOLUTIONS_FILE = "groupe38_stage2.csv"


def parse_verdict_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r"^\s*\*\*VERDICT:\*\*\s*\[?([^\]\n]+)\]?", content, re.IGNORECASE | re.MULTILINE)
        if match:
            verdict = match.group(1).strip().lower()
            return verdict



def map_verdicts_to_binary(verdicts):
    mapped_verdicts = []
    for v in verdicts:
        if v is None:
            mapped_verdicts.append(None)
            continue
        if 'factual' in v or 'credible' in v:
            mapped_verdicts.append('True')
        else:
            mapped_verdicts.append('Fake')
    return mapped_verdicts


def main():
    solutions_df = pd.read_csv(SOLUTIONS_FILE)
    solutions_df.columns = ['ID', 'Solution']
    solutions_df['Solution'] = solutions_df['Solution'].astype(str)

    predictions = []

    for filename in sorted(os.listdir(RESULTS_DIR)):
        if filename.startswith("analyse_article_") and filename.endswith(".txt"):
            match = re.search(r'analyse_article_(\d+)\.txt', filename)
            if match:
                article_id = int(match.group(1))
                filepath = os.path.join(RESULTS_DIR, filename)
                verdict = parse_verdict_from_file(filepath)
                if verdict:
                    predictions.append({'ID': article_id, 'Prediction_Raw': verdict})

    predictions_df = pd.DataFrame(predictions)


    predictions_df['Prediction'] = map_verdicts_to_binary(predictions_df['Prediction_Raw'])

    comparison_df = pd.merge(solutions_df, predictions_df, on='ID')
    comparison_df.dropna(subset=['Prediction'], inplace=True)

    y_true = comparison_df['Solution']
    y_pred = comparison_df['Prediction']

    le = LabelEncoder()
    all_labels = pd.concat([y_true, y_pred]).unique()
    le.fit(all_labels)
    labels = le.classes_

    accuracy = accuracy_score(y_true, y_pred)

    cm = confusion_matrix(y_true, y_pred, labels=labels)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels)
    plt.title('Confusion Matrix')
    plt.ylabel('real solution ')
    plt.xlabel('llm predicted')
    plt.tight_layout()

    plot_filename = 'confusion_matrix.png'
    plt.savefig(plot_filename)
    plt.show()


if __name__ == "__main__":
    main()
