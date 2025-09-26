from sentence_transformers import SentenceTransformer
import joblib


model = SentenceTransformer('all-MiniLM-L6-v2')
clf = joblib.load('models/log_classifier.joblib')

def bert_classification(log_message):
    embedding = model.encode([log_message])
    probs = clf.predict_proba(embedding)

    if max(probs[0]) <= 0.5:
        return "Unknown"
    
    label = clf.predict(embedding)[0]
    return label

if __name__ == "__main__":
    # write test logs from log_message in logs.csv that does not overlap with regex patterns
    test_logs = [
        "Multiple incorrect login attempts were made by user 7918",
        "Data replication task for shard 14 did not complete",
        "Security alert: suspicious activity on server 1",
        "nova.osapi_compute.wsgi.server [req-f0bffbc3-5ab0-4916-91c1-0a61dd7d4ec2 113d3a99c3da401fbd62cc2caa5b96d2 54fadb412c4e40cdbaed9335e4c35a9e - - -] 10.11.10.1 ""GET /v2/54fadb412c4e40cdbaed9335e4c35a9e/servers/detail HTTP/1.1"" Return code: 200 len: 1874 time: 0.2131531",
        "ThirdPartyAPI,Boot process terminated unexpectedly due to kernel issue",
        "Hi, the weather is nice today"
    ]
    for log in test_logs:
        print(f"Log: {log}\nClassified as: {bert_classification(log)}\n")