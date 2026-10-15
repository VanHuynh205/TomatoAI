---
license: cc-by-4.0
task_categories:
- visual-question-answering
language:
- en
pretty_name: PlantExpertVQA
tags:
- plant-disease
- plant-pathology
- agriculture
- multimodal
- vision-language
- fine-grained-recognition
size_categories:
- 100K<n<1M
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train.parquet
  - split: validation
    path: data/val.parquet
  - split: test
    path: data/test.parquet
---

# PlantExpertVQA

A large-scale Visual Question Answering (VQA) dataset for plant disease diagnosis, built from 45 open-source image repositories. Questions span 9 categories across 3 cognitive complexity levels and are grounded in a structured Disease Knowledge Base of 203 expert-curated cards. Every QA pair underwent two-phase domain expert review by practising botanists.

---

## Dataset at a Glance

| Property | Value |
|---|---|
| Total QA pairs | 765,186 |
| Total images | 150,841 |
| Crop species | 38 |
| Disease conditions | 89 |
| KB cards | 203 |
| Question categories | 9 (3 cognitive levels) |
| Splits | 70 / 10 / 20 (train / val / test) |
| Image sources | 45 open-source datasets |
| License | CC BY 4.0 |

---

## Splits

| Split | QA Pairs | Images |
|---|---|---|
| Train | 535,881 | 105,586 |
| Validation | 76,384 | 15,080 |
| Test | 152,921 | 30,175 |

Splits are **image-level stratified** — no image appears in more than one split. Stratification is balanced across question category, crop species, disease condition, and source dataset.

---

## Question Categories

Questions are organised into **3 cognitive levels** following a Bloom-style hierarchy:

| Level | Category | Description |
|---|---|---|
| **L1 Foundational** | Existence & Sanity Check | Confirms the image contains plant material |
| **L1 Foundational** | Plant Species Identification | Identifies the host crop |
| **L1 Foundational** | General Health Assessment | Healthy vs. diseased binary judgment |
| **L2 Analysis** | Visual Attribute Grounding | Detects specific visible symptoms |
| **L2 Analysis** | Detailed Verification | Verifies a named crop–disease combination |
| **L3 Reasoning** | Specific Disease Identification | Open-ended diagnosis without candidate |
| **L3 Reasoning** | Comprehensive Description | Full holistic description with severity |
| **L3 Reasoning** | Causal Reasoning | Identifies causal agent and risk factors |
| **L3 Reasoning** | Counterfactual Reasoning | Reasons about hypothetical healthy state |

---

## Data Schema

Each row in `train.csv` / `val.csv` / `test.csv`:

| Column | Description |
|---|---|
| `qa_id` | Unique QA pair UUID |
| `image_id` | Filename of the image |
| `image_path` | Relative path to image (`images/<filename>`) |
| `crop` | Crop species (e.g., `tomato`, `apple`) |
| `disease` | Disease or condition label |
| `category` | Broad category: `disease`, `healthy`, or `senescence` |
| `severity` | `MILD` / `MODERATE` / `SEVERE` / `HEALTHY` / `UNKNOWN` |
| `question_text` | The question |
| `answer` | Ground-truth answer |
| `answer_type` | `open`, `closed`, or `free_form` |
| `question_category` | One of the 9 categories above |
| `cognitive_level` | `Level 1 (Foundational)` / `Level 2 (Analysis)` / `Level 3 (Reasoning)` |
| `dataset_source` | `PlantVQA` (KB-generated) or `PlantVillageVQA` |

---

## Disease Knowledge Base

`disease_kb/` contains **203 JSON cards** covering 38 crop species × 89 disease conditions. Each card encodes:

- Pathogen taxonomy and transmission pathways
- Organ-specific visual symptoms (leaves, stems, fruit, roots)
- Severity rubric (MILD / MODERATE / SEVERE with quantitative thresholds)
- Lookalike conditions with key differentiating features
- Cultural, biological, and chemical management strategies

Cards are organised as `disease_kb/<crop>/<disease>.json` and aggregated in `disease_kb/all_cards.jsonl`.

---

## Zero-Shot Benchmark Results

Evaluated on 250 images (1,178 QA pairs) from the test split. Primary metric: **ROUGE-L**.

| Model | EM | Token-F1 | BLEU-1 | BLEU-2 | ROUGE-L | BERTScore |
|---|---|---|---|---|---|---|
| Gemma-3-4B-IT | 2.04 | 17.72 | 31.19 | 4.77 | **15.26** | **11.20** |
| Qwen3-VL-2B-Instruct | 3.29 | **17.88** | **37.18** | **6.63** | 14.54 | 8.53 |
| Qwen2-VL-2B-Instruct | **8.91** | 13.76 | 36.57 | 3.23 | 13.16 | 7.95 |
| LLaVA-1.6 Mistral-7B | 0.90 | 14.07 | 24.42 | 4.36 | 10.26 | 7.26 |
| LLaVA-1.5-7B | 7.39 | 10.21 | 26.87 | 0.58 | 9.87 | 3.15 |
| InstructBLIP Vicuna-7B | 6.54 | 9.70 | 28.53 | 2.18 | 9.40 | −0.92 |
| BLIP-2 FlanT5-XL | 3.57 | 9.92 | 28.20 | 2.13 | 8.98 | −2.74 |
| CLIP ViT-L/14 | 3.31 | 7.44 | 15.30 | 2.27 | 6.95 | 3.48 |
| BLIP VQA Large | 5.43 | 6.65 | 21.41 | 0.04 | 6.64 | −1.59 |

### Fine-Tuning (Qwen3-VL-2B, LoRA, 500-image subset)

| Setting | EM | Token-F1 | BLEU-1 | BLEU-2 | ROUGE-L | BERTScore |
|---|---|---|---|---|---|---|
| Zero-shot best | 2.04 | 17.72 | 31.19 | 4.77 | 15.26 | 11.20 |
| **Fine-tuned** | **18.85** | **64.65** | **66.18** | **41.74** | **61.70** | **63.27** |

Parameter-efficient LoRA fine-tuning on just 500 images (2,337 QA pairs) yields a **4× improvement** in ROUGE-L over the best zero-shot model.

---

## Usage

```python
import pandas as pd

train = pd.read_csv("data/train.csv")
val   = pd.read_csv("data/val.csv")
test  = pd.read_csv("data/test.csv")

print(train.head())
print(train['question_category'].value_counts())
```

Using the `datasets` library:

```python
from datasets import load_dataset

ds = load_dataset("SyedNazmusSakib/PlantExpertVQA")
print(ds['train'][0])
```

---

## Repository Structure

```
PlantExpertVQA/
├── images_part1.zip  # 37,711 images (4.1 GB) — unzips to images/
├── images_part2.zip  # 37,711 images (4.1 GB) — unzips to images/
├── images_part3.zip  # 37,711 images (2.9 GB) — unzips to images/
├── images_part4.zip  # 37,708 images (0.6 GB) — unzips to images/
├── disease_kb/       # 203 JSON knowledge base cards
│   ├── all_cards.jsonl
│   └── <crop>/<disease>.json
└── data/
    ├── train.csv / train.jsonl   (535,881 QA pairs)
    ├── val.csv   / val.jsonl     ( 76,384 QA pairs)
    ├── test.csv  / test.jsonl    (152,921 QA pairs)
    └── split_statistics.json
```

## Setup — Extracting Images

Download all four zip files and extract into the same directory:

```bash
unzip images_part1.zip
unzip images_part2.zip
unzip images_part3.zip
unzip images_part4.zip
```

All four zips unpack into the same `images/` folder. The `image_path` column in the CSV files (`images/<filename>`) will then resolve correctly.

---

## Citation

```bibtex
@article{sakib2025plantvillagevqa,
  title={PlantVillageVQA: A Visual Question Answering Dataset for Benchmarking Vision-Language Models in Plant Science},
  author={Sakib, Syed Nazmus and Haque, Nafiul and Hossain, Mohammad Zabed and Arman, Shifat E},
  journal={arXiv preprint arXiv:2508.17117},
  year={2025}
}
```

---

## License

This dataset is released under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) licence.  
All constituent source datasets were released under permissive open licences (CC0, CC BY 4.0, or CC BY-NC 3.0). Full provenance for every image is preserved in the dataset metadata.
