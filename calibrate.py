import os
import glob
from read_resume import extract_text_from_pdf
from svm_model import ATSMatcher

def main():
    print("--- ATS Nexus: Semantic Scoring Calibration ---")
    resume_paths = glob.glob("test_data/resumes/*.pdf")

    if not resume_paths:
        print("[ERROR] Please drop at least 1 Resume (.pdf) in test_data/resumes/")
        return

    matcher = ATSMatcher()
    
    true_match_scores = []
    
    print("\n[PHASE 1] Scoring Resumes against their corresponding Job Descriptions...")
    for rp in resume_paths:
        basename = os.path.basename(rp)
        name_no_ext = os.path.splitext(basename)[0]
        jd_path = os.path.join("test_data", "jds", f"{name_no_ext}_JD.txt")
        
        if not os.path.exists(jd_path):
            continue
            
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_text = f.read()
            
        matcher.fit(jd_text)
        
        with open(rp, "rb") as f:
            pdf_bytes = f.read()
        text = extract_text_from_pdf(pdf_bytes)
        if not text.strip():
            continue
            
        res = matcher.predict_match(text)
        raw_estimated = (res.semantic_score / 100.0) * (0.75 - 0.25) + 0.25
        true_match_scores.append(raw_estimated)
        print(f" - {basename}: Raw Score = {raw_estimated:.3f} | Current Final Output = {res.semantic_score}%")

    if true_match_scores:
        print("\n=== CALIBRATION RECOMMENDATION ===")
        print(f"Average True Match Score: {sum(true_match_scores)/len(true_match_scores):.3f}")
        print(f"Highest True Match:       {max(true_match_scores):.3f}")
        print(f"Lowest True Match:        {min(true_match_scores):.3f}")
        print("\nUpdate the MIN_SIM and MAX_SIM variables in `svm_model.py` based on these raw values ")
        print("so that your worst resumes score near 0% and your best score near 100%.")

if __name__ == "__main__":
    main()
