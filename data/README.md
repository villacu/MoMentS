# Dataset and Data Splits

In response to community requests, we have separated **325 questions** (from 13 short films) into a validation set, located at:

```
MoMentS/data/validation/moments_validation_questions.json
```

The corresponding answer keys are available at:

```
MoMentS/data/validation/moments_validation_keys.json
```

The **test set** remains closed. The test questions can be found at:

```
MoMentS/data/test/moments_test_questions.json
```

Please refer to the main README for instructions on requesting test labels or submitting predictions.

The file

```
MoMentS/data/moments_questions.json
```

contains the **original full release** of the dataset.

> Most video URLs were updated as of **October 2025**. For some of the videos in the dataset, we have provided alternative sources in case the main URL becomes unavailable. This will be updated for all the other videos in the dataset.

## Video Processing

* Download videos using [yt-dlp](https://github.com/yt-dlp/yt-dlp).
* Use [ffmpeg](https://ffmpeg.org/) to trim each video to its corresponding context window.

---

Would you like me to make it slightly more *formal and academic* (e.g., for publication supplement style), or keep this *repository-readme tone* (friendly but precise)?
