import pandas as pd

from pipeline.regex_processor import regex_classification
from pipeline.bert_processor import bert_classification
from pipeline.llm_processor import llm_classification

def classify(logs):
    labels = []
    for source, log_msg in logs:
        label = classify_log(source, log_msg)
        labels.append(label)
    return labels

def classify_log(source, log_msg):
    if source == "LegacyCRM":
        label = llm_classification(log_msg)
    else:
        label = regex_classification(log_msg)
        if not label:
            label = bert_classification(log_msg)
    return label
    
def classify_csv(file_path):
    df = pd.read_csv(file_path)
    df['target_label'] = classify(zip(df['source'], df['log_message']))

    df.to_csv('resources/output.csv', index=False)
    
if __name__ == "__main__":
    classify_csv('resources/test.csv')
    # logs = [
    #     ("ModernCRM", "IP 192.168.133.114 blocked due to potential attack"),
    #     ("BillingSystem", "User User12345 logged in."),
    #     ("AnalyticsEngine", "File data_6957.csv uploaded successfully by user User265."),
    #     ("AnalyticsEngine", "Backup completed successfully."),
    #     ("ModernHR", "GET /v2/54fadb412c4e40cdbaed9335e4c35a9e/servers/detail HTTP/1.1 RCODE  200 len: 1583 time: 0.1878400"),
    #     ("ModernHR", "Admin access escalation detected for user 9429"),
    #     ("LegacyCRM", "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active."),
    #     ("LegacyCRM", "Invoice generation process aborted for order ID 8910 due to invalid tax calculation module."),
    #     ("LegacyCRM", "The 'BulkEmailSender' feature is no longer supported. Use 'EmailCampaignManager' for improved functionality."),
    #     ("LegacyCRM", " The 'ReportGenerator' module will be retired in version 4.0. Please migrate to the 'AdvancedAnalyticsSuite' by Dec 2025")
    # ]
    # for source, log in logs:
    #     print(f"Source: {source}\nLog: {log}\nClassified as: {classify_log(source, log)}\n")