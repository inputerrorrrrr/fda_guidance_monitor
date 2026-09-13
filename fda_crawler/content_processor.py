import re
from collections import Counter
import requests
from bs4 import BeautifulSoup
from bs4 import Tag, NavigableString
import time
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


api_key = os.getenv("API_KEY")

api_url = "https://api.siliconflow.cn/v1/chat/completions"

def get_section_text(start_tag:str, element_name: list[str]) -> str:
    if not start_tag:
        return ""
    
    texts = []

    for element in start_tag.next_elements:

        if isinstance(element, Tag) and element.name in element_name:
            break

        if isinstance(element, NavigableString):
            text = element.strip()
            if text:
                texts.append(text)

    title = start_tag.get_text(" ", strip=True)
    content = "\n".join(texts)

    return f"{title}:\n{content}\n"

def write_to_file(name: str, content: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.txt"

    if not content.strip():
        print("The content to write is empty or whitespace.")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

    with open ("latest.txt", 'w', encoding='utf-8') as f:
        f.write(filename)

    return filename

def parse_h_types(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw = f.read()
        soup = BeautifulSoup(raw, 'html.parser')

        article = soup.find('article', id='main-content')
        main_content = article.find('div', attrs={"role": "main"})

        h_tags = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

        policy = None
        background = None
        footnote = None

        for tag in h_tags:
            text = tag.get_text(" ", strip=True).rstrip(":").lower()
            if text == "policy":
                policy = tag
            elif text == "background":
                background = tag
            elif text == "footnote":
                footnote = tag

        if background:
            start_tag = background
        elif policy:
            start_tag = policy
        else:
            start_tag = None

        texts = []

        for sibling in start_tag.next_siblings:
            if sibling is footnote:
                break
            if isinstance(sibling, Tag):
                text = sibling.get_text(" ", strip=True)

                if text:
                    texts.append(text)

        return "\n".join(texts)     
        
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return ""
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return ""

def parse_strong_types(file_path: str) -> str: #compatible with older versions of FDA guidance documents
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw = f.read()
        soup = BeautifulSoup(raw, 'html.parser')
    
        article = soup.find('article', id='main-content')
        main_content = article.find('div', attrs={"role": "main"})
    
        strong_tags = main_content.find_all('strong')

        purpose = None
        scope = None
        background = None
        appendix = None
    
        for tag in strong_tags:
            text = tag.get_text(strip=True).lower()
            if "purpose" in text:
                purpose = tag
            elif "scope" in text:
                scope = tag
            elif "background" in text:
                background = tag
            elif text in ["appendix", "appendices"]:
                appendix = tag
    
        if background:
            start = background
        elif scope:
            start = scope
        elif purpose:
            start = purpose
        else:
            start = None

        general_info = []
        
        general_info.append(get_section_text(purpose, ['strong']))
        general_info.append(get_section_text(scope, ['strong']))
        general_info.append(get_section_text(background, ['strong']))
        
        write_to_file("general_information", "\n".join(general_info))
        
    
        strong_between = []
    
        if start:
            for tag in main_content.find_all('strong'):
    
                if tag == start:
                    started = True
                    continue
    
                if appendix and tag is appendix:
                    break
    
                if started:
                    strong_between.append(tag)
    
        else:
            strong_between = main_content.find_all('strong')
    
        texts = []
    
        for tag in strong_between:
            text = get_section_text(tag)
            texts.append(text)
    
        if texts:
            print(f"Extracted {len(texts)} sections between the identified headings.")
    
        full_text = '\n\n'.join(texts)

        return full_text      
        
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return ""
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return ""

def extract_with_context(full_text: str, top_n: int = 10, window: int = 1) -> str:

    sentences = re.split(r'(?<=[.!?])\s+', full_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

    if len(sentences) < top_n *2:
        return full_text

    stop_words = {
    "this", "that", "these", "those",
    "some", "such", "each", "both",
    "other", "same",

    "with", "from", "into", "about",
    "above", "below", "between",
    "through", "during", "before", "after",
    "against", "under", "over",
    "until", "while", "because",

    "were", "been", "being",
    "have", "having",
    "does", "doing",

    "could", "would", "should",
    "might", "must",
    "will",

    "your", "yours", "yourself", "yourselves",
    "their", "theirs", "them", "themselves",
    "they",
    "ours", "ourselves",
    "hers", "herself",
    "himself",
    "itself",
    "what", "which", "whom",
    "whose",

    "when", "where", "while",
    "what", "which",

    "very", "just", "also",
    "more", "most",
    "only", "even",
    "still", "really",
    "quite", "rather",
    "already",
    "again",
    "almost",
    "perhaps", "maybe",

    "thing", "things",
    "something", "anything", "nothing",
    "someone", "somebody",
    "anyone", "anybody",
    "people",
    "person",
    "times",

    "make", "makes", "made", "making",
    "have", "having",
    "does", "doing",
    "said", "says", "saying",
    "think", "thinks", "thought",
    "know", "knows", "knew", "known",
    "want", "wants", "wanted",
    "come", "comes", "came", "coming",
    "goes", "going", "gone",
    "uses", "used", "using"
}

    words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', full_text.lower()) if w not in stop_words]

    word_counts = Counter(words)

    scored_sentences = []
    for i, sentence in enumerate(sentences):
        clean_words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', sentence)]

        score = sum(word_counts[word] for word in clean_words if word in word_counts)
        # Words appearing more frequently in the full text are considered more important.
        # The sentence's score is the sum of the frequencies of its core words.
        # Higher score = more likely to be a key summary sentence.
        scored_sentences.append((score, i, sentence))

        top_sentences = sorted(scored_sentences, key=lambda x: x[0], reverse=True)[:top_n]

        final_indices = set()
        for _, idx, _ in top_sentences:
            start = max(0, idx - window)
            end = min(len(sentences), idx + window + 1)
            final_indices.update(range(start, end))

        result_sentences = [sentences[i] for i in sorted(final_indices)]
        return ' '.join(result_sentences)


def summarize_with_ai(core_text: str, url: str) -> str:

    prompt = f"""
You are an extremely rigorous FDA compliance reviewer and a professional news editor.

Please read the provided text and generate a concise compliance briefing strictly following the [OUTPUT FORMAT] and [RULES] below.

[OUTPUT FORMAT]

1. First line: the generated headline itself
   - It should be a news-style headline.
   - Do NOT output any label such as "News-style Headline", "Headline", or "Title".
   - The first line must contain only the generated headline.
   - ALWAYS generate a concise and informative headline based on the provided content.
   - The headline should summarize the main product or product category, regulatory topic, and the most important regulatory action, requirement, or policy.
   - Do NOT write "Not mentioned" for the headline.
   - Do NOT simply copy the original document title.
   - Use neutral verbs such as "Addresses", "Describes", "Sets Out", "Clarifies", or "Provides Guidance on" unless the provided text explicitly supports a new issuance, announcement, approval, warning, recall, or other current regulatory action.
   - Do NOT use wording such as "FDA Issues", "FDA Announces", or "FDA Launches" merely because the document is an FDA guidance document.

2. Leave one blank line after the headline, then provide the following Markdown list:

   - 🎯 Product/Substance: [Specific product, device, drug, substance, or product category]
   - ⚠️ Regulatory Action: [Most specific regulatory action, requirement, policy, or regulatory document type supported by the text]

   For "Product/Substance":
   - Be as specific as the provided text allows.
   - Prefer the actual affected product or product category over a broad term such as "pharmaceuticals" or "medical devices" when a more specific description is supported.

   For "Regulatory Action":
   - Identify the substantive regulatory action or mechanism whenever possible, not merely the document format.
   - Examples include:
     Enforcement Discretion,
     Premarket Notification / 510(k) Requirement,
     Approval,
     Clearance,
     Warning,
     Recall,
     Restriction,
     Ban,
     Labeling Requirement,
     Safety Communication,
     Rule,
     Compliance Policy,
     or Guidance.
   - If the document is a guidance document but it describes a more specific regulatory mechanism, prefer the more informative description.
   - When useful and explicitly supported, a combined description is acceptable, for example:
     "Compliance Policy Guidance / Enforcement Discretion".

3. Below the list, add:

   🔍 Background Context:
   Write 1-2 concise sentences in plain, easy-to-understand English.

   The Background Context should prioritize:
   - why FDA issued or maintains the policy or guidance,
   - what FDA intends, requires, permits, restricts, or declines to enforce,
   - and what practical impact this has on the affected product, company, or industry.

   Do not merely restate that FDA received questions or inquiries if the provided text also explains the resulting policy, requirement, or regulatory consequence.

   If the text explicitly states that a policy has expired, been withdrawn, superseded, or otherwise has a limited status, mention that fact when it is important to understanding the document.


[RULES]

- Be factual, concise, and conservative.
- Use only information supported by the provided text.
- Do not hallucinate or infer unsupported facts.

- For Product/Substance, Regulatory Action, and Effective Date:
  if the information is genuinely absent from the provided text, write "Not mentioned".

- The headline is a GENERATED field and must always be created from the available information.
  It must never be "Not mentioned".

- Background Context is also a GENERATED summary, but every statement must be supported by the provided text.

- Do not treat an "issued date", "publication date", "revision date", "content current as of" date, or expiration date as an "Effective Date" unless the text explicitly identifies it as the effective date.

- If an expiration date, withdrawal date, or revision date is explicitly stated and materially affects interpretation of the document, it may be mentioned in Background Context, but do not relabel it as the Effective Date.

- Do not write "Text is incomplete" merely because the provided text is an excerpt or contains only selected sections.
  Use "Text is incomplete" only when the supplied text is visibly truncated, such as ending mid-sentence or clearly missing content necessary to interpret the passage.

- Distinguish between the type of document and the substantive regulatory action described by the document.
  For example, if an FDA guidance describes enforcement discretion, the Regulatory Action should preferably identify "Enforcement Discretion" or "Compliance Policy Guidance / Enforcement Discretion" rather than only "Guidance".

- Do not imply that an old or previously issued document is newly released unless the provided text explicitly supports that conclusion.

Text to analyze:

{core_text}
"""
    payload = {
         "model": "Qwen/Qwen2.5-7B-Instruct",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 500
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        ai_summary = data['choices'][0]['message']['content'].strip()

        return ai_summary

    except requests.exceptions.Timeout:
        print("Timeout")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")  
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
     output_file = Path("latest.txt")
     output_file.write_text("", encoding="utf-8")

     raw_content = parse_h_types("test_content.html")
     if raw_content:
         print("Successfully read content.")
     else:
         print("Failed to read content.")
     core_text = extract_with_context(raw_content)

     with open("latest.txt", "r", encoding="utf-8") as f:
         file_name = f.read().strip()
         print(f"Latest file name: {file_name}")

     if file_name:
        with open(file_name, "r", encoding="utf-8") as f:
            general_info = f.read()
            if general_info:
                print("Successfully read general information.")
     else:
         print("Failed to read general information.")
         general_info = ""

     text_for_ai = f"{general_info}\n\n{core_text}"

     result = summarize_with_ai(text_for_ai, url="https://www.fda.gov/regulatory-information/search-fda-guidance-documents/cpg-sec-550400-grenadine")
     print(result)