# 💡 Adaptive Document Analysis Model

This project aims to develop an Adaptive Document Analysis Model capable of processing 10-K financial documents, extracting relevant information, and generating answers to predefined queries using advanced machine learning techniques.


![Project Cover Image](front-app/public/bookLogo.png)

<!-- table of content -->
## Table of Contents
- [The Team](#the-team)
- [Project Description](#project-description)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installing](#installing)
- [Deployment](#deployment)
- [Built With](#built-with)
- [Acknowledgments](#acknowledgments)


## 👥 The Team
**Team Members**
- [Avital Harel](avital.harel@mail.huji.ac.il)
- [Amir Rosengarten](amir.rosengarten@mail.huji.ac.il)

**Supervisor**
- Dr. Gabriel Stanovsky(https://gabrielstanovsky.github.io/group/)
- [Gili Lior](gili.lior@mail.huji.ac.il)


## 📚 Project Description
The Adaptive Document Analysis Model processes 10-K financial documents to extract relevant items and generate answers to predefined queries. The model uses advanced natural language processing techniques to improve efficiency, accuracy, and relevance of retrieved answers.

### Features
- Comprehensive document processing including segmentation into individual items based on Table of Contents (TOC).
- Improved embedding generation using "sentence-transformers/all-mpnet-base-v2".
- Enhanced query handling for diverse financial insights.
- Real-time querying capabilities with efficient retrieval using FAISS indexes.

### Technologies Used
- Python
- PyTorch
- Sentence-Transformers
- FAISS
- LLMs (Mistral-7B)

## ⚡ Getting Started
These instructions will help you get a copy of the project up and running on your local machine for development purposes.

### 🧱 Prerequisites
- Python 3.8+
- PyTorch
- Sentence-Transformers
- FAISS
- pdfplumber
- Transformers (HuggingFace)

### 🏗️ Installing
1. Clone the repository:
```bash
 git clone https://github.com/amirrosen1/10K-Financial-Analyzer.git
```
2. Navigate to the project directory:
```bash
 cd 10K-Financial-Analyzer
```
3. Install dependencies:
```bash
 pip install -r requirements.txt
```

## 🚀 Deployment
For deploying on a live system, set up the backend server using Flask or FastAPI and connect the model to a user-facing interface.

## ⚙️ Built With
- [PyTorch](https://pytorch.org/)
- [Sentence-Transformers](https://www.sbert.net/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [HuggingFace Transformers](https://huggingface.co/transformers/)

## 🙏 Acknowledgments
- Dr. Gabriel Stanovsky, Gili Lior for supervision and guidance.
