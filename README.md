# M<small>O</small>M<small>ENT</small>S: A Comprehensive Multimodal Benchmark for Theory of Mind

[![Paper](https://img.shields.io/badge/Paper-arXiv-red)](https://arxiv.org/abs/2507.04415)
[![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-blue)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

MOMENTS (Multimodal Mental States) is a benchmark designed to evaluate Theory of Mind (ToM) capabilities of multimodal large language models through realistic, narrative-rich scenarios presented in short films.


### 🔄 Update (October 2025)

* Several **video URLs** that were previously invalid have been **updated**.
* We now provide an **open validation set** for model development and hyperparameter tuning.
* Please refer to the [`MoMentS/data`](./MoMentS/data) folder for detailed usage instructions.
* For **test set evaluation**, you may now either:

  1. **Submit** your model predictions to [emilio.villa@mbzuai.ac.ae](mailto:emilio.villa@mbzuai.ac.ae), **or**
  2. **Request access** to the **test set ground-truth labels** by completing and submitting the release form found at:
     `MoMentS/data/test/moments_test_release_form.pdf`
     *(PI signature required)*


## Overview

MOMENTS includes over 2,344 multiple-choice questions spanning seven distinct ToM categories based on the ATOMS taxonomy:

- **Knowledge**: Understanding what a person knows or doesn't know
- **Emotions**: Identifying and reasoning about emotional responses  
- **Desires**: Situations involving preferences and desires
- **Beliefs**: Comprehending true and false beliefs and their influence on actions
- **Intentions**: Understanding goals, motivations, and reasons for actions
- **Percepts**: Reasoning about what characters can perceive through their sensory input
- **Non-literal Communication (NLC)**: Interpreting any non-literal communication such as humor, sarcasm, deception, among others.

## Dataset Structure

### Question Format

Each question in `moments_questions.json` contains:

```json
{
    "question_id": "unique_identifier",
    "question": "Question text",
    "assigned_categories": ["ToM_category1", "ToM_category2"],
    "options": {
        "A": "Option A text",
        "B": "Option B text", 
        "C": "Option C text",
        "D": "Option D text"
    },
    "movie_title": "SHORT FILM TITLE",
    "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "t_0": 0.0,                    // Full context start time
    "t_i": 102.66,                 // Focused context start time  
    "t_j": 144.27,                 // Context end time
    "multimodal_cues": ["Body Language", "Face Expression & Gaze"],
    "video_length": 537.66
}
```

### Context Windows

- **Full Context Window [t₀, tⱼ]**: Provides complete narrative context from the beginning of the video
- **Focused Context Window [tᵢ, tⱼ]**: Contains only the immediate context required to understand the question

### Multimodal Cues

Questions may be tagged with multimodal cues when visual/auditory signals are deemed necessary by annotators:
- `"Face Expression & Gaze"`
- `"Body Language"`  
- `"Speech-related"`

## Evaluation

### Answer Format

Submit your predictions in the following JSON format:

```json
[
    {
        "question_id": "zT2dD",
        "answer_key": "A"
    },
    {
        "question_id": "5YIGn", 
        "answer_key": "B"
    }
]
```

### Handling Unavailable Videos

If a video is unavailable during evaluation:
1. First try updating URLs using the provided script (see below)
2. If the video remains inaccessible, submit `"NA"` as the answer_key for the entries related to that video.
3. Invalid entries will be excluded from accuracy computation

### Submission

To evaluate your model's performance, generate predictions for all questions in the required JSON format and either:
   * Submit predictions to [emilio.villa@mbzuai.ac.ae](mailto:emilio.villa@mbzuai.ac.ae). You will receive an accuracy report with both global and per-category ToM ability scores within **1–3 working days**, **or**
   * Request the test labels by completing `MoMentS/data/test/moments_test_release_form.pdf`.
3

*Note: An automated evaluation platform is currently under development.*

## Unavailable URLs

Video URLs may change (or be unavailable) due to re-uploads. We will regularly update them in the question json. 
If you cannot access URLs to download the videos, we may be able to provide them upon request, please reach out to [emilio.villa@mbzuai.ac.ae](mailto:emilio.villa@mbzuai.ac.ae).

## Video Processing

- Videos can be downloaded using [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- You can use [ffmpeg](https://ffmpeg.org/) to to trim each video to the respective context window.

## License

This dataset is released under CC BY-NC-SA 4.0 license for academic research purposes only.