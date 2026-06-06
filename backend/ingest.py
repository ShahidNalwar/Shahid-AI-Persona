import os
import fitz  # PyMuPDF
import json
import base64
import re
from github import Github
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

# Load env files
load_dotenv(dotenv_path=".env.local")
load_dotenv(dotenv_path=".env")
load_dotenv(dotenv_path="../.env.local")
load_dotenv(dotenv_path="../.env")

# Safe print to prevent Windows terminal character crashes (UnicodeEncodeError)
def safe_print(*args, **kwargs):
    import sys
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    file = kwargs.get('file', sys.stdout)
    
    msg = sep.join(str(arg) for arg in args)
    try:
        file.write(msg + end)
    except UnicodeEncodeError:
        safe_msg = msg.encode(file.encoding or 'ascii', errors='replace').decode(file.encoding or 'ascii')
        file.write(safe_msg + end)
    file.flush()

# Redefine standard print statement to use our safe printer
print = safe_print

# Configure repositories — now includes the AI Persona repo itself
REPOS = [
    "ShahidNalwar/Focus_Gaurdian",
    "ShahidNalwar/Malaria-Detection-Using-CNN-and-GAN",
    "ShahidNalwar/Laptolyze-AI",
    "ShahidNalwar/Crop-Disease-Detection",
    "ShahidNalwar/Shahid-AI-Persona"   # ← ADDED
]

# File types we care about
ALLOWED_EXTENSIONS = {
    ".py", ".dart", ".ipynb", ".js", ".ts", ".tsx", ".jsx", ".md", ".txt", ".json", ".css", ".html"
}

# Files to ignore
IGNORED_FILENAMES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "pubspec.lock",
    "gradlew", "gradlew.bat", "eslint.config.mjs", "next.config.mjs",
    "postcss.config.mjs", "tailwind.config.js"
}

# Directories to ignore
IGNORED_DIR_PREFIXES = (
    ".git", "node_modules", ".next", "build", "dist", "ios", "android",
    "gradle", "pub", "assets", "chroma_db"   # ← ADDED chroma_db to avoid ingesting the database itself
)

def chunk_text_by_lines(text, max_chars=1000, overlap_chars=200):
    """
    Split text into chunks of roughly max_chars, keeping line breaks intact
    and maintaining overlap_chars of context between chunks.
    """
    lines = text.splitlines()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for line in lines:
        if current_length + len(line) + 1 > max_chars:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
            # Keep overlap: take the last few lines that sum up to less than overlap_chars
            overlap_chunk = []
            overlap_len = 0
            for l in reversed(current_chunk):
                if overlap_len + len(l) + 1 < overlap_chars:
                    overlap_chunk.insert(0, l)
                    overlap_len += len(l) + 1
                else:
                    break
            current_chunk = overlap_chunk
            current_length = overlap_len
            
        current_chunk.append(line)
        current_length += len(line) + 1
        
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    return chunks

def parse_ipynb(content):
    """
    Parse a Jupyter notebook (.ipynb) and format cells into a readable text format.
    """
    try:
        notebook = json.loads(content)
        parsed_cells = []
        for i, cell in enumerate(notebook.get("cells", [])):
            cell_type = cell.get("cell_type")
            source = "".join(cell.get("source", []))
            if cell_type == "markdown" and source.strip():
                parsed_cells.append(f"[Jupyter Markdown Cell {i}]\n{source}")
            elif cell_type == "code" and source.strip():
                parsed_cells.append(f"[Jupyter Code Cell {i}]\n{source}")
        return "\n\n".join(parsed_cells)
    except Exception as e:
        print(f"Error parsing .ipynb file: {e}")
        return content  # fallback to raw content

def parse_md_sections(text):
    """
    Parse markdown file and split it by headers.
    This provides better chunks than a raw text splitter for READMEs.
    """
    sections = []
    pattern = r'(^#+\s+.*$)'
    parts = re.split(pattern, text, flags=re.MULTILINE)
    
    if len(parts) <= 1:
        return chunk_text_by_lines(text)
        
    current_header = "Intro"
    current_content = parts[0]
    
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        content = parts[i+1] if i+1 < len(parts) else ""
        sections.append(f"{header}\n{content}")
        
    # Re-chunk any sections that are too long
    final_chunks = []
    for section in sections:
        if len(section) > 1200:
            final_chunks.extend(chunk_text_by_lines(section, max_chars=1000, overlap_chars=200))
        else:
            final_chunks.append(section)
    return final_chunks

def scrape_github(token=None):
    """
    Scrape all GitHub repos, fetch files recursively, chunk them, and return.
    """
    g = Github(token) if token else Github()
    all_chunks = []
    
    for repo_name in REPOS:
        print(f"Scraping repository: {repo_name}...")
        try:
            repo = g.get_repo(repo_name)
            default_branch = repo.default_branch
            print(f"Default branch for {repo_name} is '{default_branch}'. Fetching git tree...")
            
            # Fetch git tree recursively
            tree = repo.get_git_tree(default_branch, recursive=True)
            
            for element in tree.tree:
                if element.type != "blob":
                    continue
                    
                path = element.path
                filename = os.path.basename(path)
                
                # Check ignored directories
                if any(path.startswith(prefix) or f"/{prefix}" in path for prefix in IGNORED_DIR_PREFIXES):
                    continue
                    
                # Check ignored filenames
                if filename in IGNORED_FILENAMES:
                    continue
                    
                # Check allowed extensions
                _, ext = os.path.splitext(filename)
                if ext.lower() not in ALLOWED_EXTENSIONS:
                    continue
                    
                print(f"  Fetching: {path}...")
                try:
                    blob = repo.get_git_blob(element.sha)
                    if blob.encoding == "base64":
                        content = base64.b64decode(blob.content).decode("utf-8", errors="ignore")
                    else:
                        content = blob.content
                        
                    # Parse and Chunk
                    if ext.lower() == ".ipynb":
                        formatted_text = parse_ipynb(content)
                        chunks = chunk_text_by_lines(formatted_text)
                    elif ext.lower() == ".md":
                        chunks = parse_md_sections(content)
                    else:
                        chunks = chunk_text_by_lines(content)
                        
                    for i, chunk in enumerate(chunks):
                        all_chunks.append({
                            "text": chunk,
                            "metadata": {
                                "source": "github",
                                "repo_name": repo_name,
                                "file_path": path,
                                "file_type": "notebook" if ext.lower() == ".ipynb" else ("markdown" if ext.lower() == ".md" else "code"),
                                "chunk_index": i
                            }
                        })
                except Exception as file_error:
                    print(f"    Failed to fetch/parse file {path}: {file_error}")
                    
        except Exception as repo_error:
            print(f"Error accessing repository {repo_name}: {repo_error}")
            
    return all_chunks

def fetch_commit_history(token=None):
    """
    Fetch commit messages from all repos.
    Covers the rubric requirement: answers exist only in commit history.
    """
    g = Github(token) if token else Github()
    all_chunks = []

    for repo_name in REPOS:
        print(f"Fetching commit history for: {repo_name}...")
        try:
            repo = g.get_repo(repo_name)
            commits = repo.get_commits()
            commit_lines = []
            for commit in commits[:50]:  # last 50 commits per repo
                msg = commit.commit.message.strip()
                date = commit.commit.author.date.strftime("%Y-%m-%d")
                commit_lines.append(f"[{date}] {msg}")

            if commit_lines:
                text = f"Commit history for {repo_name}:\n" + "\n".join(commit_lines)
                all_chunks.append({
                    "text": text,
                    "metadata": {
                        "source": "github_commits",
                        "repo_name": repo_name,
                        "file_path": "commit_history",
                        "file_type": "commits",
                        "chunk_index": 0
                    }
                })
                print(f"  Fetched {len(commit_lines)} commits from {repo_name}.")
        except Exception as e:
            print(f"  Failed to fetch commits for {repo_name}: {e}")

    return all_chunks

def parse_resume(pdf_path):
    """
    Parse the resume PDF file page-by-page.
    """
    if not os.path.exists(pdf_path):
        print(f"Resume PDF not found at {pdf_path}. Skipping resume parsing...")
        return []
        
    print(f"Parsing resume PDF: {pdf_path}...")
    chunks = []
    
    # Method 1: Try with PyMuPDF (fitz)
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                page_chunks = chunk_text_by_lines(text, max_chars=1200, overlap_chars=200)
                for i, chunk in enumerate(page_chunks):
                    chunks.append({
                        "text": chunk,
                        "metadata": {
                            "source": "resume",
                            "page": page_num + 1,
                            "filename": os.path.basename(pdf_path),
                            "chunk_index": i
                        }
                    })
        print(f"Successfully parsed resume using PyMuPDF. Extracted {len(chunks)} chunks.")
        return chunks
    except Exception as mupdf_err:
        print(f"PyMuPDF failed to parse: {mupdf_err}. Trying fallback pypdf parser...")
        
    # Method 2 Fallback: Try with pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                page_chunks = chunk_text_by_lines(text, max_chars=1200, overlap_chars=200)
                for i, chunk in enumerate(page_chunks):
                    chunks.append({
                        "text": chunk,
                        "metadata": {
                            "source": "resume",
                            "page": page_num + 1,
                            "filename": os.path.basename(pdf_path),
                            "chunk_index": i
                        }
                    })
        print(f"Successfully parsed resume using pypdf fallback. Extracted {len(chunks)} chunks.")
        return chunks
    except Exception as pypdf_err:
        import traceback
        print(f"Fallback parser pypdf failed: {pypdf_err}")
        traceback.print_exc()
        
    return chunks

def run_ingestion():
    """
    Main runner to scrape GitHub, fetch commits, parse resume,
    embed everything, and store in ChromaDB.
    """
    github_token = os.getenv("GITHUB_TOKEN")

    # 1. Scrape GitHub file contents
    github_chunks = scrape_github(github_token)
    print(f"Scraped {len(github_chunks)} total chunks from GitHub files.")

    # 2. Fetch commit history — covers rubric: "answers only in commit history"
    commit_chunks = fetch_commit_history(github_token)
    print(f"Fetched {len(commit_chunks)} commit history chunks.")

    # 3. Parse Resume
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(backend_dir, "data")
    resume_path = os.path.join(data_dir, "Shahid Nalwar-resume.pdf")
    
    # Fallback: find any PDF file in the backend/data directory
    if not os.path.exists(resume_path):
        if os.path.exists(data_dir) and os.path.isdir(data_dir):
            pdf_files = [f for f in os.listdir(data_dir) if f.lower().endswith(".pdf")]
            if pdf_files:
                resume_path = os.path.join(data_dir, pdf_files[0])
                
    resume_chunks = parse_resume(resume_path)
    print(f"Parsed {len(resume_chunks)} resume chunks.")

    # 4. Combine all chunks
    all_chunks = github_chunks + commit_chunks + resume_chunks
    if not all_chunks:
        print("No chunks found to ingest. Exiting...")
        return
        
    print(f"\nTotal chunks to ingest: {len(all_chunks)}")
    print(f"  - GitHub files:    {len(github_chunks)}")
    print(f"  - Commit history:  {len(commit_chunks)}")
    print(f"  - Resume:          {len(resume_chunks)}")

    # 5. Load embedding model
    print(f"\nInitializing embedding model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # 6. Connect to ChromaDB
    print(f"Connecting to ChromaDB...")
    db_path = os.path.join(os.path.dirname(__file__), "chroma_db")
    chroma_client = chromadb.PersistentClient(path=db_path)
    
    # Create or replace collection
    collection_name = "shahid_knowledge_base"
    try:
        chroma_client.delete_collection(name=collection_name)
        print(f"Deleted existing collection '{collection_name}' for clean overwrite.")
    except Exception:
        pass
        
    collection = chroma_client.create_collection(name=collection_name)
    
    # 7. Ingest in batches
    batch_size = 100
    total_chunks = len(all_chunks)
    print(f"\nIngesting {total_chunks} chunks into ChromaDB...")
    
    for i in range(0, total_chunks, batch_size):
        batch = all_chunks[i:i+batch_size]
        ids = [f"doc_{i+j}" for j in range(len(batch))]
        documents = [item["text"] for item in batch]
        metadatas = [item["metadata"] for item in batch]
        
        embeddings = model.encode(documents, show_progress_bar=False).tolist()
        
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        print(f"  Ingested batch {i // batch_size + 1}/{(total_chunks + batch_size - 1) // batch_size} ({len(batch)} items)")
        
    print("\nIngestion complete! ChromaDB database successfully created and persisted.")
    print(f"Final document count: {collection.count()}")

if __name__ == "__main__":
    run_ingestion()