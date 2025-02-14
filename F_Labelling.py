import csv
import google.generativeai as genai

# Set up Google Gemini API
API_KEY = "AIzaSyC_UYJdaED_LSlHJqzSbk_z6mciNv-LSvM"  # Replace with your actual API key
genai.configure(api_key=API_KEY)

# Define categories
CATEGORIES = [
    "Deep Learning",
    "Natural Language Processing",
    "Computer Vision",
    "Reinforcement Learning",
    "Optimization & Theory"
]

# Ask Gemini to classify the paper
def classify_paper(abstract):
    """Ask Gemini to classify the paper"""
    prompt = f"""
    Given the following research paper abstract:
    Abstract: {abstract}
    
    Classify this paper into one of these categories: {', '.join(CATEGORIES)}.
    Just return the category name.
    """
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        category = response.text.strip()
        return category if category in CATEGORIES else "Uncategorized"
    except Exception as e:
        print(f"Error classifying paper: {e}")
        return "Error"

# Annotate dataset
def annotate_papers(file_path, output_file):
    updated_rows = []
    final_data = []
    
    # Read CSV file
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)
        
        if "Category" not in headers:
            headers.append("Category")  # Add Category column
        
        updated_rows.append(headers)
        
        for row in reader:
            abstract = row[1]  # Column 2 (Abstract)
            pdf_link = row[2]  # Column 3 (PDF Link)
            
            if not abstract:
                category = "Missing Data"
            else:
                category = classify_paper(abstract)
                
            row.append(category)
            updated_rows.append(row)
            final_data.append([abstract, pdf_link, category])
            print(f"Annotated: {pdf_link} -> {category}")
    
    # Write back to original CSV
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)
    
    # Write new CSV with selected columns
    with open(output_file, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Abstract", "PDF Link", "Category"])  # Header
        writer.writerows(final_data)
    
    print("✅ Annotation complete! Files updated.")

# Run annotation
CSV_FILE = "NeurIPS_Papers.csv"  # Replace with your actual file
OUTPUT_FILE = "NeurIPS_Papers_Categorized.csv"  # New CSV file with selected columns
annotate_papers(CSV_FILE, OUTPUT_FILE)
