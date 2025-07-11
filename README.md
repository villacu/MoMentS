# M<small>O</small>M<small>ENT</small>S: A Comprehensive Multimodal Benchmark for Theory of Mind

[![Paper](https://img.shields.io/badge/Paper-arXiv-red)](https://arxiv.org/abs/2507.04415)
[![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-blue)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

MOMENTS (Multimodal Mental States) is a benchmark designed to evaluate Theory of Mind (ToM) capabilities of multimodal large language models through realistic, narrative-rich scenarios presented in short films.

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

To evaluate your model's performance:
1. Generate predictions for all questions in the required JSON format
2. Submit your predictions to [emilio.villa@mbzuai.ac.ae](mailto:emilio.villa@mbzuai.ac.ae)
3. You will receive an accuracy report with global and per ToM ability scores within 1-3 working days

*Note: An automated evaluation platform is currently under development.*

## Updating unavailable URLs

Video URLs may occasionally change due to re-uploads. We will regularly update them in the question json. However, we also provide a script so you can update them in case the last version has unavailable URLs:

```bash
python scripts/update_urls.py --yt_key [YOUR_YOUTUBE_API_KEY] --annotations moments_questions.json --output moments_questions_updated.json --report_output url_update_report.json
```

This script will:
- Check for broken or updated video URLs
- Automatically update the `video_url` field in your annotations file
- Ensure you have access to the latest video links
- Generate a report on the replaced URLs.

## Video Processing

- Videos can be downloaded using [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- You can use [ffmpeg](https://ffmpeg.org/) to to trim each video to the respective context window.

## Dataset Statistics

- **Total Questions**: 2,344
- **Number of Videos**: 168  
- **Average Video Length**: 14.56 ± 4.65 minutes
- **Question Length**: 12.64 ± 4.2 words
- **Answer Length**: 14.62 ± 7.8 words
- **Languages**: Primarily English (144 videos) with 11 videos in other languages

## Citation

If you use MOMENTS in your research, please cite:

```bibtex
@misc{villacueva2025momentscomprehensivemultimodalbenchmark,
      title={MOMENTS: A Comprehensive Multimodal Benchmark for Theory of Mind}, 
      author={Emilio Villa-Cueva and S M Masrur Ahmed and Rendi Chevi and Jan Christian Blaise Cruz and Kareem Elzeky and Fermin Cristobal and Alham Fikri Aji and Skyler Wang and Rada Mihalcea and Thamar Solorio},
      year={2025},
      eprint={2507.04415},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2507.04415}, 
}
```

## License

This dataset is released under CC BY-NC-SA 4.0 license for academic research purposes only.